import { readdirSync, readFileSync } from "node:fs";

const PAYLOAD_SHARE = 1448 / 1514;
// Clean fillable shaped scenarios where a healthy host's iperf3 control reliably exceeds 75% of the payload ceiling.
const CLEAN_SHAPED_FLOORS = new Map([
  ["accuracy-100", [100 * PAYLOAD_SHARE * 0.75, 100 * PAYLOAD_SHARE * 0.75]],
  ["accuracy-1000", [1000 * PAYLOAD_SHARE * 0.75, 1000 * PAYLOAD_SHARE * 0.75]],
  ["accuracy-10000", [10000 * PAYLOAD_SHARE * 0.75, 10000 * PAYLOAD_SHARE * 0.75]],
  ["bufferbloat-300-30", [300 * PAYLOAD_SHARE * 0.75, 30 * PAYLOAD_SHARE * 0.75]],
  ["proxy-1000", [1000 * PAYLOAD_SHARE * 0.75, 1000 * PAYLOAD_SHARE * 0.75]],
]);
const STEAL_SHARE_LIMIT = 0.05;

export function quantile(values, q) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const at = (sorted.length - 1) * q;
  const low = Math.floor(at);
  return sorted[low] + (sorted[Math.min(low + 1, sorted.length - 1)] - sorted[low]) * (at - low);
}

export function readResults(dirs, { withJob = false } = {}) {
  const manifests = [];
  const runs = [];
  let noisy = 0;
  for (const dir of dirs) {
    const manifest = JSON.parse(readFileSync(`${dir}/manifest.json`, "utf8"));
    manifests.push(manifest);
    const hashes = manifest.blocks.flatMap((block) => [
      block.noise?.hashMs,
      block.noiseAfter?.hashMs,
    ].filter((v) => typeof v === "number" && Number.isFinite(v)));
    const cutoff = 1.25 * quantile(hashes, 0.5);
    const cpus = manifest.host?.cpus ?? 1;
    const busy = new Set();
    for (const block of manifest.blocks) {
      const key = `${block.scenario}|${block.rep}`;
      if (block.noise?.hashMs > cutoff || (block.noiseAfter?.hashMs != null && block.noiseAfter.hashMs > cutoff)) {
        busy.add(key);
        continue;
      }
      if (block.noiseAfter?.stealTicks != null && block.noise?.stealTicks != null && block.startedAt && block.endedAt) {
        const elapsedSec = (block.endedAt - block.startedAt) / 1000;
        const stealDelta = block.noiseAfter.stealTicks - block.noise.stealTicks;
        if (elapsedSec >= 5 && stealDelta > 0 && stealDelta / (100 * elapsedSec * cpus) > STEAL_SHARE_LIMIT) {
          busy.add(key);
        }
      }
    }
    const dirRuns = readdirSync(`${dir}/runs`).map((file) => JSON.parse(readFileSync(`${dir}/runs/${file}`, "utf8")));
    // Also exclude a clean shaped block if its own iperf3 control collapsed (e.g., transient host/shaper stall).
    for (const run of dirRuns) {
      if (run.tool !== "iperf3") continue;
      const floor = CLEAN_SHAPED_FLOORS.get(run.scenario);
      if (!floor) continue;
      const key = `${run.scenario}|${run.rep}`;
      const ok = run.reported?.outcome === "complete"
        && run.reported.downloadMbit >= floor[0]
        && run.reported.uploadMbit >= floor[1];
      if (!ok) busy.add(key);
    }
    for (const run of dirRuns) {
      if (busy.has(`${run.scenario}|${run.rep}`)) noisy++;
      else runs.push(withJob ? { ...run, job: dir } : run);
    }
  }
  return { manifests, runs, noisy };
}
