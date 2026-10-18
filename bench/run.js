// Runs every tool in every browser through each scenario, interleaved, and writes one JSON file per run.
// node bench/run.js [--scenarios a,b] [--tools a,b] [--browsers chrome,firefox] [--reps 3] [--out dir] [--seed n]
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
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

// A tool ships as an image, or as a release archive run unchanged in the small tools image.
function serveTool(name, proxied) {
  const tool = pins.tools[name];
  const env = { ...tool.env, ...(proxied ? tool.proxy.env : {}) };
  if (!tool.release) return bed.serve(tool.image, env);
  const dir = `${releaseDir}/${tool.variantOf ?? name}-${tool.version}`;
  return bed.serve(bed.TOOLS_IMAGE, env, tool.release.command, ["-v", `${dir}:/opt/tool:ro`, "-w", "/opt/tool"]);
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

async function iperf(reverse) {
  const json = JSON.parse(
    await bed.clientTool("iperf3", "-c", bed.NET.server, "-P", "4", "-t", "10", "-O", "2", "-J", ...(reverse ? ["-R"] : [])),
  );
  return json.end.sum_received.bits_per_second / 1e6;
}

async function measure(unit, scenario, file) {
  const isReference = unit.tool === "iperf3";
  const client = pins.clients[unit.tool];
  const server = client?.server ?? unit.tool;
  const proxied = Boolean(scenario.proxy && !isReference);
  if (isReference) await bed.serve(bed.TOOLS_IMAGE, {}, ["iperf3", "-s"]);
  else await serveTool(server, proxied);
  await bed.shape(scenario);
  await bed.waitForPort(isReference ? 5201 : pins.tools[server].port);
  if (proxied) await bed.startProxy(pins.proxy.image, pins.proxy.port, proxyConfig(server));
  const cgroups = async () => {
    const own = await bed.serverCgroup();
    if (!proxied) return own;
    const proxy = await bed.serverCgroup("sb-proxy");
    return { cpuUsec: own.cpuUsec + proxy.cpuUsec, memoryPeakBytes: own.memoryPeakBytes + proxy.memoryPeakBytes };
  };
  if (scenario.competing) await bed.startCompetitor();
  const before = { bytes: await bed.linkBytes(), cgroup: await cgroups() };
  await bed.startSampler();
  let reported;
  if (isReference) {
    const startedAt = Date.now();
    const downloadMbit = await iperf(true);
    const uploadMbit = await iperf(false);
    reported = { outcome: "complete", downloadMbit, uploadMbit, startedAt, endedAt: Date.now() };
  } else if (client) {
    reported = await runClient(unit.tool);
  } else {
    const pin = pins.browsers[unit.browser];
    reported = JSON.parse(
      await bed.driver({
        adapter: pins.tools[unit.tool].adapter ?? unit.tool,
        browser: unit.browser,
        binary: `/browsers/${unit.browser}-${pin.version}/${pin.binary}`,
        url: `http://${bed.NET.server}:${proxied ? pins.proxy.port : pins.tools[unit.tool].port}/${pins.tools[unit.tool].urlSuffix ?? ""}`,
        options: pins.tools[unit.tool].options ?? {},
        screenshot: `/results/screens/${file}.png`,
        timeoutMs: Number(opts["timeout-ms"]),
      }),
    );
  }
  const samples = await bed.stopSampler();
  const after = { bytes: await bed.linkBytes(), cgroup: await cgroups() };
  await bed.stopCompetitor();
  await bed.unserve();
  const bytes = { down: after.bytes.down - before.bytes.down, up: after.bytes.up - before.bytes.up };
  const serverCpuSeconds =
    after.cgroup.cpuUsec == null ? null : (after.cgroup.cpuUsec - before.cgroup.cpuUsec) / 1e6;
  return {
    ...unit,
    scenario: scenario.id,
    reported,
    linkBytes: bytes,
    serverCpuSeconds,
    serverMemoryPeakBytes: after.cgroup.memoryPeakBytes,
    queues: analyse(samples, scenario),
  };
}

const units = [
  { tool: "iperf3", browser: null },
  ...tools.flatMap((tool) => (pins.clients[tool] ? [{ tool, browser: null }] : browsers.map((browser) => ({ tool, browser })))),
];

mkdirSync(`${out}/runs`, { recursive: true });
mkdirSync(`${out}/screens`, { recursive: true });
fetchArchives();
const host = await bed.prepare(pins, root);
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

await bed.down();
try {
  await bed.up(pins, { browsers: browserDir, driver: `${root}/bench/driver`, results: out });
  for (const scenario of scenarios) {
    // Balanced order: each new random order is followed by its reverse, so slow stretches hit every unit alike.
    let order = [];
    for (let rep = 1; rep <= reps; rep++) {
      // A proxy scenario runs the reference and the tools whose projects document a proxy setup.
      const eligible = units.filter((u) => !scenario.proxy || u.tool === "iperf3" || pins.tools[u.tool]?.proxy);
      order = rep % 2 ? shuffle(eligible) : [...order].reverse();
      await bed.serve(bed.TOOLS_IMAGE, {}, ["sleep", "infinity"]);
      await bed.shape(scenario);
      const block = { scenario: scenario.id, rep, order: order.map((u) => `${u.tool}/${u.browser}`), noise: noise(), baseRttMs: await baseRtt() };
      await bed.unserve();
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
      }
    }
  }
} finally {
  manifest.endedAt = new Date().toISOString();
  writeManifest();
  await bed.down();
}
console.error(`results in ${out}`);
