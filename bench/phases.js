// Splits the server side's CPU by phase from each run's 100 ms samples: node bench/phases.js results/a [results/b ...]
import { readdirSync, readFileSync } from "node:fs";

// An interval belongs to a direction when that direction carries this many times the other's bytes and at least
// 1 Mbit/s; everything else, such as idle probing, page loads and bidirectional stages, is "other".
const DOMINANT = 4;
const MIN_BITS_PER_SECOND = 1e6;
// The same busy-host rule as bench/summarize.js, so both tables count the same runs.
const NOISY = 1.25;

const dirs = process.argv.slice(2);
if (!dirs.length) throw new Error("usage: node bench/phases.js <results dir>...");

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

/** CPU seconds and bytes per phase; down is what the server sent, up what it received. */
function phases(samples) {
  const split = { down: { cpu: 0, bytes: 0 }, up: { cpu: 0, bytes: 0 }, other: { cpu: 0, bytes: 0 } };
  for (let i = 1; i < samples.length; i++) {
    const [t0, user0, sys0, rx0, tx0] = samples[i - 1];
    const [t1, user1, sys1, rx1, tx1] = samples[i];
    if ([user0, sys0, rx0, tx0, user1, sys1, rx1, tx1].includes(null) || t1 <= t0) continue;
    const [rx, tx] = [rx1 - rx0, tx1 - tx0];
    const floor = (MIN_BITS_PER_SECOND / 8) * ((t1 - t0) / 1000);
    const phase =
      tx > DOMINANT * rx && tx >= floor ? "down" : rx > DOMINANT * tx && rx >= floor ? "up" : "other";
    split[phase].cpu += (user1 - user0 + sys1 - sys0) / 1e6;
    split[phase].bytes += rx + tx;
  }
  return split;
}

const groups = new Map();
for (const dir of dirs) {
  const manifest = JSON.parse(readFileSync(`${dir}/manifest.json`, "utf8"));
  const typical = quantile(manifest.blocks.map((b) => b.noise.hashMs), 0.5);
  const busy = new Set(
    manifest.blocks.filter((b) => b.noise.hashMs > typical * NOISY).map((b) => `${b.scenario}|${b.rep}`),
  );
  for (const file of readdirSync(`${dir}/runs`)) {
    const run = JSON.parse(readFileSync(`${dir}/runs/${file}`, "utf8"));
    if (busy.has(`${run.scenario}|${run.rep}`) || !run.serverSamples || run.reported?.outcome !== "complete") continue;
    const key = `${run.scenario}|${run.tool}|${run.browser ?? "-"}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(phases(run.serverSamples));
  }
}

console.log("## Server CPU by phase");
console.log();
console.log(
  `Each run's server-side CPU split by its 100 ms samples: an interval is a download or an upload when one direction carries ${DOMINANT} times the other's bytes and at least 1 Mbit/s, otherwise other (idle probing, page loads, bidirectional stages). Median [25th, 75th percentile].`,
);
console.log();
console.log("| Scenario | Tool | Browser | Runs | Download s/GB | Upload s/GB | Other s | Other share |");
console.log("| --- | --- | --- | --- | --- | --- | --- | --- |");
for (const [key, runs] of [...groups].sort(([a], [b]) => a.localeCompare(b))) {
  const [scenario, tool, browser] = key.split("|");
  const perGb = (phase) => runs.map((r) => (r[phase].bytes ? r[phase].cpu / (r[phase].bytes / 1e9) : NaN));
  const total = (r) => r.down.cpu + r.up.cpu + r.other.cpu;
  console.log(
    `| ${scenario} | ${tool} | ${browser} | ${runs.length} | ${spread(perGb("down"), 3)} | ${spread(perGb("up"), 3)} | ${spread(
      runs.map((r) => r.other.cpu),
      2,
    )} | ${spread(
      runs.map((r) => r.other.cpu / total(r)),
      2,
    )} |`,
  );
}
