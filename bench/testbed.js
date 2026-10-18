// One host, three roles in their own network namespaces: client <-> shaper <-> server, joined by direct veth pairs.
// Podman's bridges are not used: they hand the shaper 64 KB GSO packets, which tbf drops and netem loses whole.
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import os from "node:os";
import { promisify } from "node:util";

const exec = promisify(execFile);

// GitHub runners lack a systemd user session for rootless cgroups, so CI runs rootful (SB_ROOTFUL=1).
const ROOTFUL = process.env.SB_ROOTFUL === "1";
const PODMAN = ROOTFUL ? ["sudo", "podman"] : ["podman"];
const PRIVILEGED = ROOTFUL ? ["sudo"] : ["podman", "unshare"];

export const NET = {
  client: "10.71.1.10",
  server: "10.71.2.10",
  clientGateway: "10.71.1.1",
  serverGateway: "10.71.2.1",
  server2: "10.71.3.10",
  server2Gateway: "10.71.3.1",
};
export const TOOLS_IMAGE = "localhost/sb-tools:latest";
const CPUS = { shaper: "0", server: "1", client: "2-3" };
const COMPETITOR_PORT = 5202;

async function sh([cmd, ...args], { timeoutMs = 120_000 } = {}) {
  const { stdout } = await exec(cmd, args, { maxBuffer: 256 << 20, timeout: timeoutMs });
  return stdout.trim();
}

export const podman = (...args) => sh([...PODMAN, ...args], { timeoutMs: 600_000 });
const privileged = (script) => sh([...PRIVILEGED, "sh", "-ec", script]);
const pid = (name) => podman("inspect", "-f", "{{.State.Pid}}", name);

let cpusets = true;
const cpuArgs = (role) => (cpusets ? ["--cpuset-cpus", CPUS[role]] : []);

// Offloads off on both ends, so every hop carries real 1,500 byte frames.
const flat = (p, dev) => `nsenter -t ${p} -n ethtool -K ${dev} tso off gso off gro off`;

async function link(shaperPid, peerPid, dev, address, gateway) {
  // A replaced server's namespace can outlive its container for a moment, and its link with it.
  await privileged(`
    nsenter -t ${shaperPid} -n ip link del ${dev} 2>/dev/null || true
    nsenter -t ${shaperPid} -n ip link add ${dev} type veth peer name eth0 netns ${peerPid}
    nsenter -t ${shaperPid} -n ip addr add ${gateway}/24 dev ${dev}
    nsenter -t ${shaperPid} -n ip link set ${dev} up
    nsenter -t ${peerPid} -n ip link set lo up
    nsenter -t ${peerPid} -n ip addr add ${address}/24 dev eth0
    nsenter -t ${peerPid} -n ip link set eth0 up
    nsenter -t ${peerPid} -n ip route add default via ${gateway}
    ${flat(shaperPid, dev)}
    ${flat(peerPid, "eth0")}`);
}

async function start(name, role, image, args = [], command = []) {
  await remove([name], 0);
  await podman("run", "-d", "--rm", "--name", name, "--network", "none", ...cpuArgs(role), ...args, image, ...command);
}

export async function prepare(pins, root) {
  await podman("build", "-q", "-t", TOOLS_IMAGE, `${root}/images/tools`);
  for (const image of [pins.client, pins.proxy.image, ...Object.values(pins.tools).flatMap((tool) => tool.image ?? [])])
    await podman("pull", "-q", image);
  // Pinning needs one CPU each for shaper and server and two for the browser; smaller hosts run unpinned.
  cpusets =
    os.availableParallelism() >= 4 &&
    (await podman("run", "--rm", "--network", "none", "--cpuset-cpus", "0", TOOLS_IMAGE, "true").then(
      () => true,
      () => false,
    ));
  return { cpusets: cpusets ? CPUS : null, rootful: ROOTFUL };
}

export async function up(pins, { browsers, driver, results }) {
  await start("sb-shaper", "shaper", TOOLS_IMAGE, ["--cap-add", "NET_ADMIN", "--sysctl", "net.ipv4.ip_forward=1"], [
    "sleep",
    "infinity",
  ]);
  await start(
    "sb-client",
    "client",
    pins.client,
    [
      // An init that reaps: browser helpers orphaned at quit would otherwise stay as zombies and exhaust the pid limit.
      "--init",
      "--shm-size",
      "2g",
      "-e",
      "DISPLAY=:99",
      "-v",
      `${browsers}:/browsers:ro`,
      "-v",
      `${driver}:/driver:ro`,
      "-v",
      `${results}:/results`,
    ],
    ["sleep", "infinity"],
  );
  await link(await pid("sb-shaper"), await pid("sb-client"), "cl", NET.client, NET.clientGateway);
  // Counts the competing flow where it crosses the shaper, so each run's own share of a shared link is known.
  await podman("exec", "sb-shaper", "sh", "-ec", `nft -f - <<'EOF'
table inet sb {
  counter compdown {}
  counter compup {}
  chain passing {
    type filter hook forward priority 0;
    tcp sport ${COMPETITOR_PORT} counter name "compdown"
    tcp dport ${COMPETITOR_PORT} counter name "compup"
  }
}
EOF`);
  await podman("exec", "-d", "sb-client", "Xvfb", ":99", "-screen", "0", "1280x900x24", "-nolisten", "tcp");
}

export async function down() {
  await remove(["sb-compete-cl", "sb-compete-srv", "sb-proxy", "sb-server", "sb-server2", "sb-client", "sb-shaper"], 0);
}

// The server is replaced for every run, so no tool carries state or memory from an earlier one.
export async function serve(image, env = {}, command = [], args = []) {
  // Sidecars share the old server's namespace; they must go before the server can be replaced.
  await unserve();
  const vars = Object.entries(env).flatMap(([key, value]) => ["-e", `${key}=${value}`]);
  await start("sb-server", "server", image, [...vars, ...args], command);
  await link(await pid("sb-shaper"), await pid("sb-server"), "sv", NET.server, NET.serverGateway);
}

// A driver that died cannot take its browser down; kill whatever runs from the pinned browser directory.
export async function sweepClient() {
  await podman("exec", "sb-client", "sh", "-c", "pkill -9 -f '^/browsers/' || true");
  await new Promise((resolve) => setTimeout(resolve, 500));
}

// Removes containers one by one and waits until each is gone: older Podman returns before a --rm container's own
// cleanup ends, and fails a whole removal over one missing name.
async function remove(names, graceSeconds) {
  for (const name of names) await podman("rm", "-f", "-t", String(graceSeconds), name).catch(() => {});
  const until = Date.now() + 30_000;
  for (;;) {
    const left = (await podman("ps", "-a", "--format", "{{.Names}}")).split("\n").filter((n) => names.includes(n));
    if (!left.length) return;
    if (Date.now() > until) throw new Error(`containers did not go away: ${left.join(", ")}`);
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
}

export const unserve = () => remove(["sb-compete-cl", "sb-compete-srv", "sb-proxy", "sb-server", "sb-server2"], 2);

// The second server of a multi-server scenario, on its own link and subnet.
export async function serveSecond(image, env = {}, command = [], args = []) {
  const vars = Object.entries(env).flatMap(([key, value]) => ["-e", `${key}=${value}`]);
  await start("sb-server2", "server", image, [...vars, ...args], command);
  await link(await pid("sb-shaper"), await pid("sb-server2"), "sv2", NET.server2, NET.server2Gateway);
}

// The proxy shares the server's namespace and CPU set, like a proxy on the same host, and forwards over loopback.
export async function startProxy(image, port, configFile) {
  await podman("run", "-d", "--rm", "--name", "sb-proxy", "--network", "container:sb-server", ...cpuArgs("server"),
    "-v", `${configFile}:/etc/nginx/conf.d/default.conf:ro`, image);
  await waitForPort(port);
}

export async function waitForPort(port, host = NET.server, timeoutMs = 60_000) {
  const until = Date.now() + timeoutMs;
  for (;;) {
    const open = await clientTool("nc", "-z", "-w", "1", host, String(port)).then(
      () => true,
      () => false,
    );
    if (open) return;
    if (Date.now() > until) throw new Error(`server port ${port} did not open within ${timeoutMs} ms`);
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
}

// One bulk TCP flow each way between sidecars in the client's and server's namespaces, on the shaper's CPU so the
// tool and browser CPUs stay untouched.
export async function startCompetitor() {
  await podman("run", "-d", "--rm", "--name", "sb-compete-srv", "--network", "container:sb-server", ...cpuArgs("shaper"),
    TOOLS_IMAGE, "iperf3", "-s", "-p", String(COMPETITOR_PORT));
  await waitForPort(COMPETITOR_PORT);
  await podman("run", "-d", "--rm", "--name", "sb-compete-cl", "--network", "container:sb-client", ...cpuArgs("shaper"),
    TOOLS_IMAGE, "iperf3", "-c", NET.server, "-p", String(COMPETITOR_PORT), "--bidir", "-t", "86400");
  // Long enough for both flows to leave slow start before the tool begins.
  await new Promise((resolve) => setTimeout(resolve, 3000));
}

export const stopCompetitor = () => remove(["sb-compete-cl", "sb-compete-srv"], 0);

// What a finished run must not leave behind; anything listed here would distort or break the runs after it.
export async function residue() {
  const problems = [];
  const containers = (await podman("ps", "--format", "{{.Names}}")).split("\n").filter((n) => n.startsWith("sb-"));
  const extra = containers.filter((name) => !["sb-shaper", "sb-client"].includes(name));
  if (extra.length) problems.push(`containers left: ${extra.join(", ")}`);
  const processes = (await podman("exec", "sb-client", "ps", "-eo", "comm", "--no-headers"))
    .split("\n")
    .map((line) => line.trim())
    .filter((name) => name && !["podman-init", "catatonit", "sleep", "Xvfb", "ps"].includes(name));
  if (processes.length) problems.push(`client processes left: ${processes.join(", ")}`);
  const loops = Number(await podman("exec", "sb-shaper", "sh", "-c", "pgrep -f 'while \\[ ! -f /tmp/stop' | wc -l"));
  if (loops) problems.push(`${loops} queue sampler(s) still running`);
  return problems;
}

// Tools that run on the client side (iperf3, ping) share the client's namespace and CPU set.
export const clientTool = (...command) => clientRun([], command);

export const clientRun = (args, command) =>
  podman("run", "--rm", "--network", "container:sb-client", ...cpuArgs("client"), ...args, TOOLS_IMAGE, ...command);

const queue = (s, rateMbit) => {
  const bytesPerMs = (rateMbit * 1e6) / 8 / 1000;
  const burst = Math.max(Math.round(bytesPerMs * 4), 16_000);
  if (s.queue === "fifo") return `tbf rate ${rateMbit}mbit burst ${burst} limit ${Math.round(bytesPerMs * s.queueMs)}`;
  return `tbf rate ${rateMbit}mbit burst ${burst} limit ${Math.round(bytesPerMs * 1000)}`;
};

// Each direction is shaped on the shaper's egress toward the receiver: cl carries downloads, sv carries uploads.
// With two servers each has its own path: its downloads are shaped where they leave the server, its uploads on the
// shaper's link toward it, and the client link carries only the delay.
export async function shape(s) {
  const script = [];
  const two = s.servers === 2;
  const links = two
    ? [
        ["cl", null],
        ["sv", s.upMbit],
        ["sv2", s.upMbit],
      ]
    : [
        ["cl", s.downMbit],
        ["sv", s.upMbit],
      ];
  for (const [dev, rate] of links) {
    script.push(`tc qdisc del dev ${dev} root 2>/dev/null || true`);
    if (rate == null && !s.rttMs && !s.lossPct) continue;
    const loss = s.lossPct ? ` loss ${s.lossPct}%` : "";
    script.push(`tc qdisc add dev ${dev} root handle 1: netem delay ${s.rttMs / 2}ms${loss} limit 1000000`);
    if (rate == null) continue;
    script.push(`tc qdisc add dev ${dev} parent 1:1 handle 10: ${queue(s, rate)}`);
    if (s.queue === "fq_codel") script.push(`tc qdisc add dev ${dev} parent 10:1 handle 20: fq_codel`);
  }
  await podman("exec", "sb-shaper", "sh", "-ec", script.join("\n"));
  // Offloads stay off where shaping and loss must act on real frames; multi-gigabit and unshaped runs use them, as
  // real network cards do, so the shaper's per-packet cost does not become the limit.
  const state = s.offloads ? "on" : "off";
  const running = (await podman("ps", "--format", "{{.Names}}")).split("\n");
  const shaper = await pid("sb-shaper");
  const ends = [[shaper, "cl"], [await pid("sb-client"), "eth0"]];
  if (running.includes("sb-server")) ends.push([shaper, "sv"], [await pid("sb-server"), "eth0"]);
  if (running.includes("sb-server2")) ends.push([shaper, "sv2"], [await pid("sb-server2"), "eth0"]);
  await privileged(ends.map(([p, dev]) => `nsenter -t ${p} -n ethtool -K ${dev} tso ${state} gso ${state} gro ${state}`).join("\n"));
  if (!two) return;
  for (const name of ["sb-server", "sb-server2"]) {
    const p = await pid(name);
    await privileged(`
      nsenter -t ${p} -n tc qdisc replace dev eth0 root handle 10: ${queue(s, s.downMbit)}
      nsenter -t ${p} -n tc qdisc add dev eth0 parent 10:1 handle 20: fq_codel`);
  }
}

export async function linkBytes() {
  const links = JSON.parse(await podman("exec", "sb-shaper", "ip", "-s", "-j", "link", "show"));
  const bytes = (dev) => links.find((l) => l.ifname === dev)?.stats64;
  return {
    down: bytes("cl")?.tx.bytes ?? 0,
    up: (bytes("sv")?.tx.bytes ?? 0) + (bytes("sv2")?.tx.bytes ?? 0),
  };
}

// Samples the bottleneck queues every 100 ms on the shaper itself, so the reference adds no traffic to the path.
export async function startSampler() {
  await podman(
    "exec",
    "-d",
    "sb-shaper",
    "sh",
    "-c",
    'rm -f /tmp/samples /tmp/stop; while [ ! -f /tmp/stop ]; do printf "%s\\t%s\\t%s\\n" "$(cut -d" " -f1 /proc/uptime)" "$(tc -s -j qdisc show)" "$(nft -j list counters table inet sb)" >> /tmp/samples; usleep 100000; done',
  );
}

export async function stopSampler() {
  await podman("exec", "sb-shaper", "touch", "/tmp/stop");
  await new Promise((resolve) => setTimeout(resolve, 300));
  const text = await podman("exec", "sb-shaper", "cat", "/tmp/samples").catch(() => "");
  // A line cut short by the stop, or a tool call that printed nothing, is skipped rather than guessed at.
  return text.split("\n").flatMap((line) => {
    try {
      const [t, qdiscs, counters] = line.split("\t");
      const competitor = Object.fromEntries(
        JSON.parse(counters)
          .nftables.filter((entry) => entry.counter)
          .map(({ counter }) => [counter.name, counter]),
      );
      return [{ t: Number(t), qdiscs: JSON.parse(qdiscs), competitor }];
    } catch {
      return [];
    }
  });
}

export async function serverCgroup(name = "sb-server") {
  const path = await podman("inspect", "-f", "{{.State.CgroupPath}}", name);
  const read = (file) => readFile(`/sys/fs/cgroup${path}/${file}`, "utf8").catch(() => null);
  const stat = await read("cpu.stat");
  const peak = await read("memory.peak");
  return {
    cpuUsec: stat ? Number(/usage_usec (\d+)/.exec(stat)[1]) : null,
    memoryPeakBytes: peak ? Number(peak) : null,
  };
}

export const driver = (args) =>
  sh([...PODMAN, "exec", "sb-client", "node", "/driver/main.js", JSON.stringify(args)], { timeoutMs: 300_000 });
