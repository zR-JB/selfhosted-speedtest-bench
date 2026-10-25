// Tables each run's server-side CPU by phase (testbed.js serverPhases): node bench/phases.js results/a [results/b ...]
import { readdirSync, readFileSync } from "node:fs";

// The same busy-host rule as bench/summarize.js, so both tables count the same runs.
const NOISY = 1.25;

const dirs = process.argv.slice(2);
if (!dirs.length) throw new Error("usage: node bench/phases.js <results dir>...");

const scenarios = JSON.parse(readFileSync(new URL("../scenarios.json", import.meta.url), "utf8"));
const quantile = (values, q) => {
  const sorted = [...values].sort((a, b) => a - b);
  const at = (sorted.length - 1) * q;
  const low = Math.floor(at);
  return sorted[low] + (sorted[Math.min(low + 1, sorted.length - 1)] - sorted[low]) * (at - low);
};
const spread = (values, digits) => {
  const v = values.filter(Number.isFinite);
  const f = (x) => x.toFixed(digits);
  return v.length ? `${f(quantile(v, 0.5))} [${f(quantile(v, 0.25))}, ${f(quantile(v, 0.75))}]` : "n/a";
};

const runs = [];
let pins;
for (const dir of dirs) {
  const manifest = JSON.parse(readFileSync(`${dir}/manifest.json`, "utf8"));
  pins ??= manifest.pins;
  const typical = quantile(manifest.blocks.map((b) => b.noise.hashMs), 0.5);
  const busy = new Set(
    manifest.blocks.filter((b) => b.noise.hashMs > typical * NOISY).map((b) => `${b.scenario}|${b.rep}`),
  );
  for (const file of readdirSync(`${dir}/runs`)) {
    const run = JSON.parse(readFileSync(`${dir}/runs/${file}`, "utf8"));
    if (!busy.has(`${run.scenario}|${run.rep}`) && run.serverPhases && run.reported.outcome === "complete") runs.push(run);
  }
}
const entry = (tool) => pins.tools[tool] ?? pins.clients?.[tool];
const label = (run) =>
  `${run.tool === "iperf3" ? "iperf3 (reference)" : entry(run.tool).name}${run.browser ? `, ${run.browser}` : ""}`;

console.log("## Server CPU by phase");
console.log();
console.log(
  "Each run's server-side CPU split by its 100 ms samples: half a second or more of one direction carrying four times the other's bytes, at 1 Mbit/s or more, is a download or an upload phase; idle probing, page loads and bidirectional stages are other. Competing-traffic runs are left out, since the competitor shares the server's link. Median [25th, 75th percentile].",
);
for (const scenario of scenarios) {
  const mine = runs.filter((run) => run.scenario === scenario.id);
  if (!mine.length) continue;
  console.log();
  console.log(`### ${scenario.title}`);
  console.log();
  console.log("| Tool | Runs | Download s/GB | Upload s/GB | Other s | Other share |");
  console.log("| --- | --- | --- | --- | --- | --- |");
  for (const group of Map.groupBy(mine, (run) => `${run.tool}|${run.browser}`).values()) {
    const phases = group.map((run) => run.serverPhases);
    const perGb = (phase) => phases.map((p) => (p[phase].bytes ? p[phase].cpuSeconds / (p[phase].bytes / 1e9) : NaN));
    const total = (p) => p.down.cpuSeconds + p.up.cpuSeconds + p.other.cpuSeconds;
    const others = phases.map((p) => p.other.cpuSeconds);
    const shares = phases.map((p) => p.other.cpuSeconds / total(p));
    console.log(
      `| ${label(group[0])} | ${group.length} | ${spread(perGb("down"), 3)} | ${spread(perGb("up"), 3)} | ${spread(others, 3)} | ${spread(shares, 2)} |`,
    );
  }
}
