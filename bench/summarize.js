// Turns one or more result directories into Markdown tables: node bench/summarize.js results/a [results/b ...]
import { readFileSync, writeFileSync } from "node:fs";
import { basename } from "node:path";
import { quantile, readResults } from "./results.js";

// tbf counts Ethernet frames: 1,514 bytes carry 1,448 bytes of TCP payload (IPv4, timestamps, 1,500 byte MTU).
const PAYLOAD_SHARE = 1448 / 1514;
// A link counts as fillable when iperf3's median reaches this share of the payload rate in both directions.
const FILLABLE = 0.98;

const dirs = process.argv.slice(2);
if (!dirs.length) throw new Error("usage: node bench/summarize.js <results dir>...");

const published = Boolean(process.env.SB_REPORT_DATA);
const scenarios = JSON.parse(readFileSync(process.env.SB_SCENARIOS ?? new URL("../scenarios.json", import.meta.url), "utf8"));
const median = (values) => quantile(values, 0.5);
const { manifests, runs, noisy } = readResults(dirs, { withJob: published });
if (published) {
  const fields = (record, keys) => Object.fromEntries(keys.filter((key) => record?.[key] != null).map((key) => [key, record[key]]));
  const directions = (record, keys) => Object.fromEntries(
    ["down", "up"].map((direction) => [direction, fields(record?.[direction], keys)]),
  );
  const measurements = runs.map((run) => ({
    ...fields(run, ["tool", "browser", "scenario", "rep", "position", "baseRttMs", "serverCpuSeconds", "serverMemoryPeakBytes"]),
    job: basename(run.job),
    reported: fields(run.reported, [
      "outcome", "startedAt", "endedAt", "downloadMbit", "uploadMbit", "idleLatencyMs", "loadedLatencyDownMs",
      "loadedLatencyUpMs", "browserCpuSeconds", "clientCpuSeconds", "clientMemoryPeakBytes",
    ]),
    linkBytes: fields(run.linkBytes, ["down", "up"]),
    serverPhases: directions(run.serverPhases, ["bytes", "cpuSeconds", "directionBytes", "milliseconds"]),
    queues: directions(run.queues, ["loadedSamples", "medianQueueMs", "medianOwnLinkMbit"]),
  }));
  writeFileSync(process.env.SB_REPORT_DATA, JSON.stringify({ runs: measurements, noisy }));
}
const pins = manifests[0].pins;

const fmt = (value, digits = 1) => (value == null || Number.isNaN(value) ? "n/a" : value.toFixed(digits));
const pct = (value) => (value == null ? "n/a" : `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)} %`);
const entry = (tool) => pins.tools[tool] ?? pins.clients?.[tool];
const quantity = (tool) => (tool === "iperf3" ? "payload" : entry(tool).reports.quantity);
const name = (run) => {
  const tool = entry(run.tool);
  if (process.env.SB_SCENARIOS && run.tool.startsWith("graphite-meter")) {
    return tool.name.replace(/^(Graphite Meter terminal client|Graphite Meter)/,
      run.browser ? "Graphite Meter Browser" : "Graphite Meter Terminal");
  }
  return tool.name;
};
const label = (run) =>
  `${run.tool === "iperf3" ? "iperf3 (reference)" : name(run)}${run.browser ? `, ${run.browser}` : ""}`;

const lines = [];
const out = (line = "") => lines.push(line);

const hosts = new Set(
  manifests.map((m) => `${m.host.cpu} (${m.host.cpus} CPUs, kernel ${m.host.kernel}, ${m.host.rootful ? "rootful" : "rootless"})`),
);
out(`Jobs: ${manifests.length}. Runs: ${runs.length + noisy}, of which ${noisy} left out from blocks on a busy host. Hosts: ${[...hosts].join("; ")}.`);
out(
  `Tools: ${Object.values({ ...pins.tools, ...pins.clients }).filter((t) => !t.variantOf).map((t) => `${t.name} ${t.version}`).join(", ")}. Browsers: ${Object.entries(pins.browsers).map(([name, b]) => `${name} ${b.version}`).join(", ")}.`,
);

for (let scenario of scenarios) {
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
    out(published
      ? "Unshaped single-test throughput on the runner’s virtual link. Rates show median [25th, 75th percentile]."
      : "No shaping: the host's CPU is the limit, so rates show how far each tool gets on it, not a network's capacity. Rates show median [25th, 75th percentile].");
    out();
    out("| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Client CPU s/GB |");
    out("| --- | --- | --- | --- | --- | --- | --- |");
    const gb = (run) => (run.linkBytes.down + run.linkBytes.up) / 1e9;
    for (const group of groups.values())
      out(
        `| ${label(group[0])} | ${completed(group).length}/${group.length} | ${spread(group, (r) => r.reported.downloadMbit)} | ${spread(group, (r) => r.reported.uploadMbit)} | ${fmt(pick(group, (r) => r.serverCpuSeconds / gb(r)), 2)} | ${fmt(pick(group, (r) => r.serverMemoryPeakBytes / 1e6), 0)} | ${fmt(pick(group, (r) => (r.reported.browserCpuSeconds ?? r.reported.clientCpuSeconds ?? NaN) / gb(r)), 2)} |`,
      );
    continue;
  }
  const reference = [...groups.values()].find((group) => group[0].tool === "iperf3") ?? [];
  // Rates and references are for the whole run: with two servers, both paths together.
  const paths = scenario.servers ?? 1;
  scenario = { ...scenario, downMbit: scenario.downMbit * paths, upMbit: scenario.upMbit * paths };
  const fillable =
    pick(reference, (r) => r.reported.downloadMbit) >= scenario.downMbit * PAYLOAD_SHARE * FILLABLE &&
    pick(reference, (r) => r.reported.uploadMbit) >= scenario.upMbit * PAYLOAD_SHARE * FILLABLE;
  const fifo = scenario.queue === "fifo";
  out(
    [
      `Link rate ${scenario.downMbit} / ${scenario.upMbit} Mbit/s; payload rate ${fmt(scenario.downMbit * PAYLOAD_SHARE)} / ${fmt(scenario.upMbit * PAYLOAD_SHARE)} Mbit/s.`,
      scenario.competing
        ? "One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data."
        : fillable
          ? (published ? "Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage." : "Error is against the quantity each tool says it reports.")
          : "iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams).",
      fifo ? "" : "Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference.",
      published && scenario.proxy ? "iperf3 bypasses nginx and measures the direct shaped path as a control." : "",
      published ? "" : scenario.note ?? "",
      "Rates show median [25th, 75th percentile].",
    ]
      .filter(Boolean)
      .join(" "),
  );
  out();
  const difference = published ? "vs TCP model" : "Error";
  out(`| Tool | Runs ok | Reports | Download Mbit/s | ${difference} | Upload Mbit/s | ${difference} | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |`);
  out("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |");
  for (const group of groups.values()) {
    const tool = group[0].tool;
    const share = quantity(tool) === "payload" ? PAYLOAD_SHARE : 1;
    const options = pins.tools[tool]?.options?.config?.transports;
    const target = options?.throughputTarget;
    const args = pins.clients?.[tool]?.args ?? [];
    const quic = target === "protocol:http3" || target === "transport:webtransport" ||
      (args.includes("--throughput-protocol") && args[args.indexOf("--throughput-protocol") + 1] === "http3");
    const error = (fn, rate) => {
      const value = pick(group, fn);
      return fillable && !scenario.competing && !(published && quic) && value != null ? pct(value / (rate * share) - 1) : "n/a";
    };
    const ref = (dir) => (fifo ? fmt(pick(group, (r) => r.baseRttMs + (r.queues?.[dir].medianQueueMs ?? NaN))) : "n/a");
    const loaded = (key, dir) => `${fmt(pick(group, (r) => r.reported[key]))} (${ref(dir)})`;
    const down = (r) => r.reported.downloadMbit;
    const up = (r) => r.reported.uploadMbit;
    out(
      `| ${label(group[0])} | ${completed(group).length}/${group.length} | ${quantity(group[0].tool)} | ${spread(group, down)} | ${error(down, scenario.downMbit)} | ${spread(group, up)} | ${error(up, scenario.upMbit)} | ${fmt(pick(group, (r) => r.reported.idleLatencyMs))} (${fmt(pick(group, (r) => r.baseRttMs))}) | ${loaded("loadedLatencyDownMs", "down")} | ${loaded("loadedLatencyUpMs", "up")} |`,
    );
  }
  for (const run of mine.filter((r) => r.reported.outcome !== "complete"))
    out(`\n- ${label(run)}, rep ${run.rep}: ${run.reported.outcome}${run.reported.error ? `: ${run.reported.error.split("\n")[0]}` : ""}`);
}

console.log(lines.join("\n"));
