// Turns one or more result directories into Markdown tables: node bench/summarize.js results/a [results/b ...]
import { readdirSync, readFileSync } from "node:fs";

// tbf counts Ethernet frames: 1,514 bytes carry 1,448 bytes of TCP payload (IPv4, timestamps, 1,500 byte MTU).
const PAYLOAD_SHARE = 1448 / 1514;
// A link counts as fillable when iperf3's median reaches this share of the payload rate in both directions.
const FILLABLE = 0.98;
// A block whose fixed CPU benchmark ran this much slower than its job's median ran on a busy host.
const NOISY = 1.25;

const dirs = process.argv.slice(2);
if (!dirs.length) throw new Error("usage: node bench/summarize.js <results dir>...");

const scenarios = JSON.parse(readFileSync(new URL("../scenarios.json", import.meta.url), "utf8"));
const quantile = (values, q) => {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const at = (sorted.length - 1) * q;
  const low = Math.floor(at);
  return sorted[low] + (sorted[Math.min(low + 1, sorted.length - 1)] - sorted[low]) * (at - low);
};
const median = (values) => quantile(values, 0.5);

const manifests = [];
const runs = [];
let noisy = 0;
for (const dir of dirs) {
  const manifest = JSON.parse(readFileSync(`${dir}/manifest.json`, "utf8"));
  manifests.push(manifest);
  const typical = median(manifest.blocks.map((b) => b.noise.hashMs));
  const busy = new Set(
    manifest.blocks.filter((b) => b.noise.hashMs > typical * NOISY).map((b) => `${b.scenario}|${b.rep}`),
  );
  for (const file of readdirSync(`${dir}/runs`)) {
    const run = JSON.parse(readFileSync(`${dir}/runs/${file}`, "utf8"));
    if (busy.has(`${run.scenario}|${run.rep}`)) noisy++;
    else runs.push(run);
  }
}
const pins = manifests[0].pins;

const fmt = (value, digits = 1) => (value == null || Number.isNaN(value) ? "n/a" : value.toFixed(digits));
const pct = (value) => (value == null ? "n/a" : `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)} %`);
const entry = (tool) => pins.tools[tool] ?? pins.clients?.[tool];
const quantity = (tool) => (tool === "iperf3" ? "payload" : entry(tool).reports.quantity);
const label = (run) =>
  `${run.tool === "iperf3" ? "iperf3 (reference)" : entry(run.tool).name}${run.browser ? `, ${run.browser}` : ""}`;

const lines = [];
const out = (line = "") => lines.push(line);

const hosts = new Set(
  manifests.map((m) => `${m.host.cpu} (${m.host.cpus} CPUs, kernel ${m.host.kernel}, ${m.host.rootful ? "rootful" : "rootless"})`),
);
out(`Jobs: ${manifests.length}. Runs: ${runs.length + noisy}, of which ${noisy} left out from blocks on a busy host. Hosts: ${[...hosts].join("; ")}.`);
out(
  `Tools: ${Object.values({ ...pins.tools, ...pins.clients }).filter((t) => !t.variantOf).map((t) => `${t.name} ${t.version}`).join(", ")}. Browsers: ${Object.entries(pins.browsers).map(([name, b]) => `${name} ${b.version}`).join(", ")}.`,
);

for (const scenario of scenarios) {
  const mine = runs.filter((run) => run.scenario === scenario.id);
  if (!mine.length) continue;
  const groups = Map.groupBy(mine, (run) => `${run.tool}|${run.browser}`);
  out();
  out(`## ${scenario.title}`);
  out();
  const shaped = scenario.downMbit != null;
  const completed = (group) => group.filter((run) => run.reported.outcome === "complete");
  const values = (group, fn) => completed(group).map(fn).filter((v) => v != null && !Number.isNaN(v));
  const pick = (group, fn) => median(values(group, fn));
  const spread = (group, fn) => {
    const v = values(group, fn);
    return v.length ? `${fmt(median(v))} [${fmt(quantile(v, 0.25))}, ${fmt(quantile(v, 0.75))}]` : "n/a";
  };
  if (!shaped) {
    out("No shaping: rates measure the host, not a network, so only CPU cost is compared.");
    out();
    out("| Tool | Runs ok | Server CPU s/GB | Server peak MB | Browser CPU s/GB |");
    out("| --- | --- | --- | --- | --- |");
    const gb = (run) => (run.linkBytes.down + run.linkBytes.up) / 1e9;
    for (const group of groups.values())
      out(
        `| ${label(group[0])} | ${completed(group).length}/${group.length} | ${fmt(pick(group, (r) => r.serverCpuSeconds / gb(r)), 2)} | ${fmt(pick(group, (r) => r.serverMemoryPeakBytes / 1e6), 0)} | ${fmt(pick(group, (r) => (r.reported.browserCpuSeconds ?? NaN) / gb(r)), 2)} |`,
      );
    continue;
  }
  const reference = [...groups.values()].find((group) => group[0].tool === "iperf3") ?? [];
  const fillable =
    pick(reference, (r) => r.reported.downloadMbit) >= scenario.downMbit * PAYLOAD_SHARE * FILLABLE &&
    pick(reference, (r) => r.reported.uploadMbit) >= scenario.upMbit * PAYLOAD_SHARE * FILLABLE;
  const fifo = scenario.queue === "fifo";
  out(
    [
      `Link rate ${scenario.downMbit} / ${scenario.upMbit} Mbit/s; payload rate ${fmt(scenario.downMbit * PAYLOAD_SHARE)} / ${fmt(scenario.upMbit * PAYLOAD_SHARE)} Mbit/s.`,
      scenario.competing
        ? "One bulk TCP flow each way shares the link, so each run is scored against its own share of it, measured on the shaper as link bytes minus the competing flow's."
        : fillable
          ? "Error is against the quantity each tool says it reports."
          : "iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams).",
      fifo ? "" : "Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference.",
      "Rates show median [25th, 75th percentile].",
    ]
      .filter(Boolean)
      .join(" "),
  );
  out();
  out("| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |");
  out("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |");
  for (const group of groups.values()) {
    const share = quantity(group[0].tool) === "payload" ? PAYLOAD_SHARE : 1;
    const error = (fn, rate, dir) => {
      if (scenario.competing)
        return pct(pick(group, (r) => fn(r) / ((r.queues?.[dir].medianOwnLinkMbit ?? NaN) * share) - 1));
      const value = pick(group, fn);
      return fillable && value != null ? pct(value / (rate * share) - 1) : "n/a";
    };
    const ref = (dir) => (fifo ? fmt(pick(group, (r) => r.baseRttMs + (r.queues?.[dir].medianQueueMs ?? NaN))) : "n/a");
    const loaded = (key, dir) => `${fmt(pick(group, (r) => r.reported[key]))} (${ref(dir)})`;
    const down = (r) => r.reported.downloadMbit;
    const up = (r) => r.reported.uploadMbit;
    out(
      `| ${label(group[0])} | ${completed(group).length}/${group.length} | ${quantity(group[0].tool)} | ${spread(group, down)} | ${error(down, scenario.downMbit, "down")} | ${spread(group, up)} | ${error(up, scenario.upMbit, "up")} | ${fmt(pick(group, (r) => r.reported.idleLatencyMs))} (${fmt(pick(group, (r) => r.baseRttMs))}) | ${loaded("loadedLatencyDownMs", "down")} | ${loaded("loadedLatencyUpMs", "up")} |`,
    );
  }
  for (const run of mine.filter((r) => r.reported.outcome !== "complete"))
    out(`\n- ${label(run)}, rep ${run.rep}: ${run.reported.outcome}${run.reported.error ? `: ${run.reported.error.split("\n")[0]}` : ""}`);
}

console.log(lines.join("\n"));
