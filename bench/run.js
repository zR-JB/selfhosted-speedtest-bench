// Runs every tool in every browser through each scenario, interleaved, and writes one JSON file per run.
// node bench/run.js [--scenarios a,b] [--tools a,b] [--browsers chrome,firefox] [--reps 3] [--out dir] [--seed n]
import { execFileSync } from "node:child_process";
import { createHash, X509Certificate } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import { parseArgs } from "node:util";
import { analyse } from "./reference.js";
import * as bed from "./testbed.js";

const root = new URL("..", import.meta.url).pathname.replace(/\/$/, "");
const pins = JSON.parse(readFileSync(`${root}/pins.json`, "utf8"));
const allScenarios = JSON.parse(readFileSync(`${root}/scenarios.json`, "utf8"));

const { values: opts } = parseArgs({
  options: {
    scenarios: { type: "string", default: allScenarios.map((s) => s.id).join(",") },
    tools: { type: "string", default: [...Object.keys(pins.tools), ...Object.keys(pins.clients)].join(",") },
    browsers: { type: "string", default: Object.keys(pins.browsers).join(",") },
    reps: { type: "string", default: "3" },
    out: { type: "string", default: `${root}/results/local-${new Date().toISOString().replace(/[:.]/g, "-")}` },
    seed: { type: "string", default: String(Date.now() % 1e9) },
    "timeout-ms": { type: "string", default: "180000" },
    // Any harness error fails the job: for the preflight that gates a full bench.
    strict: { type: "boolean", default: false },
  },
});
// A variant is its base tool with a documented option set; it inherits everything it does not override.
for (const tool of Object.values(pins.tools))
  if (tool.variantOf) Object.assign(tool, { ...pins.tools[tool.variantOf], ...tool });
const scenarios = opts.scenarios.split(",").map((id) => allScenarios.find((s) => s.id === id) ?? fail(`no scenario ${id}`));
const tools = opts.tools.split(",");
const browsers = opts.browsers.split(",");
const reps = Number(opts.reps);
const out = opts.out;

function fail(message) {
  throw new Error(message);
}

// Mulberry32: a seeded order makes a job's schedule reproducible from its manifest.
let seed = Number(opts.seed) >>> 0;
function random() {
  seed = (seed + 0x6d2b79f5) >>> 0;
  let t = seed;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}
const shuffle = (items) => {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
};

const browserDir = `${root}/.cache/browsers`;
const releaseDir = `${root}/.cache/releases`;

// Downloads, checks and unpacks every pinned archive once: browsers, and tools that ship as release binaries.
function fetchArchives() {
  const archives = [
    ...Object.entries(pins.browsers).map(([name, pin]) => [`${browserDir}/${name}-${pin.version}`, pin]),
    ...Object.entries({ ...pins.tools, ...pins.clients })
      .filter(([, tool]) => tool.release && !tool.variantOf)
      .map(([name, tool]) => [`${releaseDir}/${name}-${tool.version}`, tool.release]),
  ];
  for (const [dir, pin] of archives) {
    if (existsSync(`${dir}/.complete`)) continue;
    mkdirSync(dir, { recursive: true });
    const archive = `${dir}.download`;
    execFileSync("curl", ["-sfL", "-o", archive, pin.url]);
    const sha = createHash("sha256").update(readFileSync(archive)).digest("hex");
    if (sha !== pin.sha256) fail(`${pin.url}: sha256 ${sha}, pinned ${pin.sha256}`);
    if (pin.url.endsWith(".zip")) execFileSync("unzip", ["-q", archive, "-d", dir]);
    else execFileSync("tar", ["-xf", archive, "-C", dir]);
    execFileSync("rm", [archive]);
    writeFileSync(`${dir}/.complete`, "");
  }
}

// One self-signed certificate for every server address, made per job. Chrome trusts its key by hash and Firefox
// accepts it through WebDriver, so no tool's TLS setup differs from what its documentation describes.
async function tlsMaterial() {
  const dir = `${out}/config/tls`;
  mkdirSync(dir, { recursive: true });
  await bed.podman("run", "--rm", "--network", "none", "-v", `${dir}:/tls`, bed.TOOLS_IMAGE, "sh", "-ec", `
    openssl req -x509 -newkey rsa:2048 -nodes -days 7 -subj /CN=${bed.NET.server} \
      -addext subjectAltName=IP:${bed.NET.server},IP:${bed.NET.server2} -keyout /tls/key.pem -out /tls/cert.pem 2>/dev/null
    cp /tls/cert.pem /tls/nginx.crt && cp /tls/key.pem /tls/nginx.key && chmod 644 /tls/*`);
  const spki = createHash("sha256")
    .update(new X509Certificate(readFileSync(`${dir}/cert.pem`)).publicKey.export({ type: "spki", format: "der" }))
    .digest("base64");
  return { dir, spki };
}

// A documented option that lives in a config file: the tool's own file with exact edits, each of which must match.
async function configFile(name) {
  const { source, target, edits } = pins.tools[name].configFile;
  const tool = pins.tools[name];
  let text = source.startsWith("release:")
    ? readFileSync(`${releaseDir}/${tool.variantOf ?? name}-${tool.version}/${source.slice(8)}`, "utf8")
    : await bed.podman("run", "--rm", "--network", "none", "--entrypoint", "cat", tool.image, source.slice(6));
  for (const [from, to] of edits) {
    if (!text.includes(from)) fail(`${name}: ${source} no longer contains ${JSON.stringify(from)}`);
    text = text.replaceAll(from, to);
  }
  const file = `${out}/config/${name}-${target.split("/").pop()}`;
  writeFileSync(file, text);
  return ["-v", `${file}:${target}:ro`];
}

// A tool ships as an image, or as a release archive run unchanged in the small tools image.
async function serveTool(name, proxied, multi) {
  const tool = pins.tools[name];
  const env = Object.fromEntries(
    Object.entries({
      ...tool.env,
      ...(proxied ? tool.proxy.env : {}),
      ...tool.tls?.env,
      ...(multi ? tool.multiServer.env : {}),
    }).map(([key, value]) => [
      key,
      value.replaceAll("{host}", bed.NET.server),
    ]),
  );
  const mounts = [
    ...(tool.tls ? ["-v", `${tls.dir}:${tool.tls.mount}:ro`] : []),
    ...(tool.configFile ? await configFile(name) : []),
  ];
  if (!tool.release) return bed.serve(tool.image, env, [], mounts);
  const dir = `${releaseDir}/${tool.variantOf ?? name}-${tool.version}`;
  return bed.serve(bed.TOOLS_IMAGE, env, tool.command ?? tool.release.command, [
    "-v",
    `${dir}:/opt/tool:ro`,
    "-w",
    "/opt/tool",
    ...mounts,
  ]);
}

// The same nginx for every tool, with only the directives that tool's own documentation asks for.
function proxyConfig(name) {
  const tool = pins.tools[name];
  const file = `${out}/config/nginx-${name}.conf`;
  mkdirSync(`${out}/config`, { recursive: true });
  writeFileSync(
    file,
    `map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}
server {
    listen ${pins.proxy.port};
    location / {
        proxy_pass http://127.0.0.1:${tool.port};
        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
${tool.proxy.location.map((line) => `        ${line}`).join("\n")}
    }
}
`,
  );
  return file;
}

// Terminal clients print a report; each parser turns one into the fields the browser adapters return.
const rate = (text, label) => {
  const m = new RegExp(`${label}\\s+([\\d.]+) (k|M|G)bit/s`).exec(text);
  return m ? Number(m[1]) * { k: 1e-3, M: 1, G: 1e3 }[m[2]] : null;
};
const ms = (text, label) => {
  const m = new RegExp(`^${label}\\s+([\\d.]+) ms`, "m").exec(text);
  return m ? Number(m[1]) : null;
};
const PARSERS = {
  "graphite-meter-report": (text) => ({
    outcome: /^Graphite Meter\s+Complete/m.test(text) ? "complete" : "incomplete",
    downloadMbit: rate(text, "Download"),
    uploadMbit: rate(text, "Upload"),
    idleLatencyMs: ms(text, "Idle"),
    loadedLatencyDownMs: ms(text, "Loaded download"),
    loadedLatencyUpMs: ms(text, "Loaded upload"),
  }),
  "librespeed-json": (text) => {
    const [result] = JSON.parse(text);
    return {
      outcome: "complete",
      downloadMbit: result.download,
      uploadMbit: result.upload,
      idleLatencyMs: result.ping,
      loadedLatencyDownMs: null,
      loadedLatencyUpMs: null,
    };
  },
};

async function runClient(name) {
  const client = pins.clients[name];
  const config = `${out}/config`;
  mkdirSync(config, { recursive: true });
  for (const [file, content] of Object.entries(client.config ?? {}))
    writeFileSync(`${config}/${file}`, JSON.stringify(content));
  const startedAt = Date.now();
  // A non-zero exit still prints a report (a partial run); the parser decides what it means.
  const text = await bed
    .clientRun(
      ["-v", `${releaseDir}/${name}-${client.version}:/opt/tool:ro`, "-v", `${config}:/config:ro`, "-w", "/opt/tool"],
      client.release.command,
    )
    .catch((error) => error.stdout ?? "");
  return { ...PARSERS[client.parse](text), report: text, startedAt, endedAt: Date.now() };
}

// A fixed amount of hashing; a block that takes much longer than the job's median ran on a busy host.
function noise() {
  const started = process.hrtime.bigint();
  const data = Buffer.alloc(1 << 20, 1);
  for (let i = 0; i < 200; i++) createHash("sha256").update(data).digest();
  const steal = readFileSync("/proc/stat", "utf8").split("\n")[0].trim().split(/\s+/)[8];
  return { hashMs: Number(process.hrtime.bigint() - started) / 1e6, stealTicks: Number(steal) };
}

async function baseRtt() {
  const text = await bed.clientTool("ping", "-c", "10", "-i", "0.2", "-q", bed.NET.server);
  // The minimum: the first probe also waits for neighbour discovery.
  const min = /= ([\d.]+)\//.exec(text);
  return min ? Number(min[1]) : null;
}

async function iperf(reverse, host = bed.NET.server) {
  const json = JSON.parse(
    await bed.clientTool("iperf3", "-c", host, "-P", "4", "-t", "10", "-O", "2", "-J", ...(reverse ? ["-R"] : [])),
  );
  return json.end.sum_received.bits_per_second / 1e6;
}

// With two servers the reference measures both paths at once, as the tools do.
const iperfAll = async (reverse, hosts) =>
  (await Promise.all(hosts.map((host) => iperf(reverse, host)))).reduce((sum, mbit) => sum + mbit, 0);

const toolUrl = (name, proxied) =>
  proxied
    ? `http://${bed.NET.server}:${pins.proxy.port}/`
    : (pins.tools[name].url ?? `http://${bed.NET.server}:${pins.tools[name].port}/`).replaceAll("{host}", bed.NET.server);

async function measure(unit, scenario, file) {
  const isReference = unit.tool === "iperf3";
  const client = pins.clients[unit.tool];
  const server = client?.server ?? unit.tool;
  const proxied = Boolean(scenario.proxy && !isReference);
  let sampling = false;
  // Whatever fails, the next run must start from a clean server side: no sampler, competitor, proxy or server left.
  try {
    const multi = scenario.servers === 2;
    const hosts = multi ? [bed.NET.server, bed.NET.server2] : [bed.NET.server];
    if (isReference) await bed.serve(bed.TOOLS_IMAGE, {}, ["iperf3", "-s"]);
    else await serveTool(server, proxied, multi);
    if (multi && isReference) await bed.serveSecond(bed.TOOLS_IMAGE, {}, ["iperf3", "-s"]);
    else if (multi) await bed.serveSecond(pins.tools[server].image, pins.tools[server].env);
    await bed.shape(scenario);
    for (const host of hosts) await bed.waitForPort(isReference ? 5201 : pins.tools[server].port, host);
    if (proxied) await bed.startProxy(pins.proxy.image, pins.proxy.port, proxyConfig(server));
    // A variant named for a protocol must really serve it; a server that falls back would be reported under a false name.
    const expected = pins.tools[server]?.expectProtocol;
    const served = expected
      ? await bed.clientTool("curl", "-sk", "--http2", "-o", "/dev/null", "-w", "%{http_version}", toolUrl(server, false))
      : null;
    if (expected && served !== expected) throw new Error(`${server} served HTTP/${served}, expected HTTP/${expected}`);
    // Everything on the server side counts: a proxy in front, or the second server.
    const cgroups = async () => {
      const parts = await Promise.all(
        ["sb-server", ...(proxied ? ["sb-proxy"] : []), ...(multi ? ["sb-server2"] : [])].map((n) => bed.serverCgroup(n)),
      );
      return {
        cpuUsec: parts.reduce((sum, p) => sum + p.cpuUsec, 0),
        memoryPeakBytes: parts.reduce((sum, p) => sum + p.memoryPeakBytes, 0),
      };
    };
    if (scenario.competing) await bed.startCompetitor();
    const before = { bytes: await bed.linkBytes(), cgroup: await cgroups() };
    await bed.startSampler();
    sampling = true;
    let reported;
    if (isReference) {
      const startedAt = Date.now();
      const downloadMbit = await iperfAll(true, hosts);
      const uploadMbit = await iperfAll(false, hosts);
      reported = { outcome: "complete", downloadMbit, uploadMbit, startedAt, endedAt: Date.now() };
    } else if (client) {
      reported = await runClient(unit.tool);
    } else {
      const pin = pins.browsers[unit.browser];
      reported = JSON.parse(
        await bed.driver({
          adapter: pins.tools[unit.tool].adapter ?? pins.tools[unit.tool].variantOf ?? unit.tool,
          browser: unit.browser,
          binary: `/browsers/${unit.browser}-${pin.version}/${pin.binary}`,
          url: `${toolUrl(unit.tool, proxied)}${pins.tools[unit.tool].urlSuffix ?? ""}`,
          options: pins.tools[unit.tool].options ?? {},
          chromeArgs: [
            `--ignore-certificate-errors-spki-list=${tls.spki}`,
            `--origin-to-force-quic-on=${pins.quicOrigins.join(",")}`,
          ],
          screenshot: `/results/screens/${file}.png`,
          timeoutMs: Number(opts["timeout-ms"]),
        }),
      );
    }
    const samples = await bed.stopSampler();
    sampling = false;
    const after = { bytes: await bed.linkBytes(), cgroup: await cgroups() };
    return {
      ...unit,
      scenario: scenario.id,
      reported,
      ...(served ? { serverProtocol: `HTTP/${served}` } : {}),
      linkBytes: { down: after.bytes.down - before.bytes.down, up: after.bytes.up - before.bytes.up },
      serverCpuSeconds: after.cgroup.cpuUsec == null ? null : (after.cgroup.cpuUsec - before.cgroup.cpuUsec) / 1e6,
      serverMemoryPeakBytes: after.cgroup.memoryPeakBytes,
      queues: analyse(samples, scenario),
    };
  } finally {
    await bed.sweepClient();
    if (sampling) await bed.stopSampler().catch(() => {});
    await bed.stopCompetitor();
    await bed.unserve();
  }
}

const units = [
  { tool: "iperf3", browser: null },
  ...tools.flatMap((tool) =>
    pins.clients[tool]
      ? [{ tool, browser: null }]
      : browsers.filter((b) => pins.tools[tool].browsers?.includes(b) ?? true).map((browser) => ({ tool, browser })),
  ),
];

mkdirSync(`${out}/runs`, { recursive: true });
mkdirSync(`${out}/screens`, { recursive: true });
fetchArchives();
const host = await bed.prepare(pins, root);
const tls = await tlsMaterial();
const manifest = {
  startedAt: new Date().toISOString(),
  seed: Number(opts.seed),
  reps,
  scenarios: scenarios.map((s) => s.id),
  units,
  pins,
  host: {
    kernel: os.release(),
    cpu: os.cpus()[0]?.model,
    cpus: os.cpus().length,
    memoryBytes: os.totalmem(),
    podman: await bed.podman("--version"),
    node: process.version,
    runner: process.env.GITHUB_ACTIONS ? `${process.env.ImageOS} ${process.env.ImageVersion}` : "local",
    ...host,
  },
  bench: (() => {
    try {
      return execFileSync("git", ["-C", root, "describe", "--always", "--dirty"], { encoding: "utf8" }).trim();
    } catch {
      return "uncommitted";
    }
  })(),
  blocks: [],
};
const writeManifest = () => writeFileSync(`${out}/manifest.json`, `${JSON.stringify(manifest, null, 2)}\n`);
writeManifest();

// Consecutive harness errors (not tool failures) that end a job early.
const FAIL_FAST = 3;
let failures = 0;
let harnessErrors = 0;
await bed.down();
try {
  await bed.up(pins, { browsers: browserDir, driver: `${root}/bench/driver`, results: out });
  for (const scenario of scenarios) {
    // Balanced order: each new random order is followed by its reverse, so slow stretches hit every unit alike.
    let order = [];
    for (let rep = 1; rep <= reps; rep++) {
      // Scenarios and variants can narrow who runs: a proxy scenario only tools whose projects document a proxy, a
      // multi-server scenario only tools that measure several servers at once, a transport variant only its scenarios.
      const eligible = units.filter((u) => {
        if (u.tool === "iperf3") return true;
        const entry = pins.tools[u.tool] ?? pins.clients[u.tool];
        if (scenario.tools && !scenario.tools.includes(u.tool)) return false;
        if (entry.onlyScenarios && !entry.onlyScenarios.includes(scenario.id)) return false;
        return !scenario.proxy || Boolean(pins.tools[u.tool]?.proxy && !entry.tls);
      });
      order = rep % 2 ? shuffle(eligible) : [...order].reverse();
      const block = { scenario: scenario.id, rep, order: order.map((u) => `${u.tool}/${u.browser}`), noise: noise() };
      // A block whose base RTT cannot be measured still runs; its runs carry no base RTT instead of ending the job.
      try {
        await bed.serve(bed.TOOLS_IMAGE, {}, ["sleep", "infinity"]);
        if (scenario.servers === 2) await bed.serveSecond(bed.TOOLS_IMAGE, {}, ["sleep", "infinity"]);
        await bed.shape(scenario);
        block.baseRttMs = await baseRtt();
      } catch (error) {
        block.baseRttMs = null;
        block.error = String(error.message ?? error).split("\n")[0];
      } finally {
        await bed.unserve();
      }
      manifest.blocks.push(block);
      writeManifest();
      for (const [position, unit] of order.entries()) {
        const file = `${scenario.id}-${rep}-${unit.tool}-${unit.browser ?? "cli"}`;
        console.error(`${file} (${position + 1}/${order.length})`);
        const result = await measure(unit, scenario, file).catch((error) => ({
          ...unit,
          scenario: scenario.id,
          reported: { outcome: "harness-error", error: String(error.stack ?? error) },
        }));
        writeFileSync(`${out}/runs/${file}.json`, `${JSON.stringify({ rep, position, baseRttMs: block.baseRttMs, ...result }, null, 2)}\n`);
        // A run that leaves anything behind poisons every run after it, so the job stops instead of measuring on.
        const problems = await bed.residue();
        if (problems.length) throw new Error(`harness left state behind after ${file}: ${problems.join("; ")}`);
        if (result.reported.outcome === "harness-error") harnessErrors++;
        failures = result.reported.outcome === "harness-error" ? failures + 1 : 0;
        if (failures >= FAIL_FAST) throw new Error(`${FAIL_FAST} harness errors in a row, last in ${file}`);
      }
    }
  }
} finally {
  manifest.endedAt = new Date().toISOString();
  writeManifest();
  await bed.down();
}
console.error(`results in ${out}`);
if (opts.strict && harnessErrors) {
  console.error(`${harnessErrors} harness error(s); see the runs marked harness-error`);
  process.exitCode = 1;
}
