import { readdirSync, readFileSync } from "node:fs";

export function quantile(values, q) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const at = (sorted.length - 1) * q;
  const low = Math.floor(at);
  return sorted[low] + (sorted[Math.min(low + 1, sorted.length - 1)] - sorted[low]) * (at - low);
}

export function readResults(dirs) {
  const manifests = [];
  const runs = [];
  let noisy = 0;
  for (const dir of dirs) {
    const manifest = JSON.parse(readFileSync(`${dir}/manifest.json`, "utf8"));
    manifests.push(manifest);
    const cutoff = 1.25 * quantile(manifest.blocks.map((block) => block.noise.hashMs), 0.5);
    const busy = new Set(manifest.blocks.filter((b) => b.noise.hashMs > cutoff).map((b) => `${b.scenario}|${b.rep}`));
    for (const file of readdirSync(`${dir}/runs`)) {
      const run = JSON.parse(readFileSync(`${dir}/runs/${file}`, "utf8"));
      if (busy.has(`${run.scenario}|${run.rep}`)) noisy++;
      else runs.push(run);
    }
  }
  return { manifests, runs, noisy };
}
