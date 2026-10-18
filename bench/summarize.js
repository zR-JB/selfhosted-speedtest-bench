// Turns one or more result directories into Markdown tables: node bench/summarize.js results/a [results/b ...]
import { readdirSync, readFileSync } from "node:fs";
import { median } from "./reference.js";

// tbf counts Ethernet frames: 1,514 bytes carry 1,448 bytes of TCP payload (IPv4, timestamps, 1,500 byte MTU).
const PAYLOAD_SHARE = 1448 / 1514;

const dirs = process.argv.slice(2);
if (!dirs.length) throw new Error("usage: node bench/summarize.js <results dir>...");

const manifests = dirs.map((dir) => JSON.parse(readFileSync(`${dir}/manifest.json`, "utf8")));
const scenarios = JSON.parse(readFileSync(new URL("../scenarios.json", import.meta.url), "utf8"));
const runs = dirs.flatMap((dir) =>
  readdirSync(`${dir}/runs`).map((file) => JSON.parse(readFileSync(`${dir}/runs/${file}`, "utf8"))),
);
const pins = manifests[0].pins;

const fmt = (value, digits = 1) => (value == null || Number.isNaN(value) ? "n/a" : value.toFixed(digits));
const pct = (value) => (value == null ? "n/a" : `${value >= 0 ? "+" : ""}${(value * 100).toFixed(1)} %`);
const quantity = (tool) => (tool === "iperf3" ? "payload" : pins.tools[tool].reports.quantity);
const label = (run) => `${run.tool === "iperf3" ? "iperf3 (reference)" : pins.tools[run.tool].name}${run.browser ? `, ${run.browser}` : ""}`;

const lines = [];
const out = (line = "") => lines.push(line);

out(`Jobs: ${manifests.length}. Runs: ${runs.length}. Hosts: ${[...new Set(manifests.map((m) => `${m.host.cpu} (${m.host.cpus} CPUs, kernel ${m.host.kernel}, ${m.host.rootful ? "rootful" : "rootless"})`))].join("; ")}.`);
out(`Tools: ${Object.values(pins.tools).map((t) => `${t.name} ${t.version}`).join(", ")}. Browsers: ${Object.entries(pins.browsers).map(([name, b]) => `${name} ${b.version}`).join(", ")}.`);

for (const scenario of scenarios) {
  const mine = runs.filter((run) => run.scenario === scenario.id);
  if (!mine.length) continue;
  const groups = Map.groupBy(mine, (run) => `${run.tool}|${run.browser}`);
  out();
  out(`## ${scenario.title}`);
  out();
  const shaped = scenario.downMbit != null;
  if (shaped) {
    out(`Payload reference ${fmt(scenario.downMbit * PAYLOAD_SHARE)} / ${fmt(scenario.upMbit * PAYLOAD_SHARE)} Mbit/s; link rate ${scenario.downMbit} / ${scenario.upMbit} Mbit/s. Error is against the quantity each tool says it reports.${scenario.queue === "fifo" ? "" : " Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference."}`);
    out();
    out("| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |");
    out("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |");
  } else {
    out("No shaping: rates measure the host, not a network, so only CPU cost is compared.");
    out();
    out("| Tool | Runs ok | Server CPU s/GB | Server peak MB | Browser CPU s/GB |");
    out("| --- | --- | --- | --- | --- |");
  }
  for (const group of groups.values()) {
    const ok = group.filter((run) => run.reported.outcome === "complete");
    const pick = (fn) => median(ok.map(fn).filter((v) => v != null && !Number.isNaN(v)));
    const gb = (run) => (run.linkBytes.down + run.linkBytes.up) / 1e9;
    const name = label(group[0]);
    const okText = `${ok.length}/${group.length}`;
    if (!shaped) {
      out(`| ${name} | ${okText} | ${fmt(pick((r) => r.serverCpuSeconds / gb(r)), 2)} | ${fmt(pick((r) => r.serverMemoryPeakBytes / 1e6), 0)} | ${fmt(pick((r) => (r.reported.browserCpuSeconds ?? NaN) / gb(r)), 2)} |`);
      continue;
    }
    const share = quantity(group[0].tool) === "payload" ? PAYLOAD_SHARE : 1;
    const down = pick((r) => r.reported.downloadMbit);
    const up = pick((r) => r.reported.uploadMbit);
    const fifo = scenario.queue === "fifo";
    const ref = (dir) => (fifo ? pick((r) => r.baseRttMs + (r.queues?.[dir].medianQueueMs ?? NaN)) : null);
    const loaded = (key, dir) => `${fmt(pick((r) => r.reported[key]))} (${fifo ? fmt(ref(dir)) : "n/a"})`;
    out(
      `| ${name} | ${okText} | ${quantity(group[0].tool)} | ${fmt(down)} | ${pct(down == null ? null : down / (scenario.downMbit * share) - 1)} | ${fmt(up)} | ${pct(up == null ? null : up / (scenario.upMbit * share) - 1)} | ${fmt(pick((r) => r.reported.idleLatencyMs))} (${fmt(pick((r) => r.baseRttMs))}) | ${loaded("loadedLatencyDownMs", "down")} | ${loaded("loadedLatencyUpMs", "up")} |`,
    );
  }
  const failed = mine.filter((run) => run.reported.outcome !== "complete");
  for (const run of failed) out(`\n- ${label(run)}, rep ${run.rep}: ${run.reported.outcome}${run.reported.error ? `: ${run.reported.error.split("\n")[0]}` : ""}`);
}

console.log(lines.join("\n"));
