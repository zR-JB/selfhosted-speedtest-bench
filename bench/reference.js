// The bottleneck queue's delay while a direction is loaded, from the shaper's own tbf statistics.
// Only a FIFO gives every flow the same queue; under fq_codel a probe flow skips the bulk backlog, so it is not a
// reference there and is reported as the bulk flows' queue only.
const median = (values) => {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = sorted.length >> 1;
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};

function direction(samples, dev, rateMbit) {
  const tbf = (sample) => sample.qdiscs.find((q) => q.dev === dev && q.kind === "tbf");
  const queueMs = [];
  for (let i = 1; i < samples.length; i++) {
    const previous = tbf(samples[i - 1]);
    const current = tbf(samples[i]);
    const seconds = samples[i].t - samples[i - 1].t;
    if (!previous || !current || seconds <= 0) continue;
    const mbit = ((current.bytes - previous.bytes) * 8) / seconds / 1e6;
    // A sample counts as loaded once the link carries at least half its rate.
    if (mbit >= rateMbit / 2) queueMs.push((current.backlog * 8) / (rateMbit * 1e3));
  }
  return { loadedSamples: queueMs.length, medianQueueMs: median(queueMs) };
}

export function analyse(samples, scenario) {
  if (scenario.downMbit == null) return null;
  return {
    kind: scenario.queue,
    down: direction(samples, "cl", scenario.downMbit),
    up: direction(samples, "sv", scenario.upMbit),
  };
}
