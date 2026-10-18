// What the shaper saw while a direction was loaded: the bottleneck queue's delay and, with a competing flow, the run's
// own share of the link. Only a FIFO gives every flow the same queue; under fq_codel a probe flow skips the bulk
// backlog, so queue delay is not a latency reference there.
const median = (values) => {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = sorted.length >> 1;
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
};

// tbf counts Ethernet frames; nftables counts IP packets, 14 bytes shorter each. The competitor is counted as it
// enters the queue, so its share is only exact where the queue drops little: fq_codel, not a deep tail-drop FIFO.
const frameBytes = (counter) => (counter ? counter.bytes + 14 * counter.packets : 0);

function direction(samples, dev, counter, rateMbit) {
  const tbf = (sample) => sample.qdiscs.find((q) => q.dev === dev && q.kind === "tbf");
  const queueMs = [];
  const ownMbit = [];
  for (let i = 1; i < samples.length; i++) {
    const previous = tbf(samples[i - 1]);
    const current = tbf(samples[i]);
    const seconds = samples[i].t - samples[i - 1].t;
    if (!previous || !current || seconds <= 0) continue;
    const mbit = (bytes) => (bytes * 8) / seconds / 1e6;
    const linkMbit = mbit(current.bytes - previous.bytes);
    const competitorMbit = mbit(
      frameBytes(samples[i].competitor?.[counter]) - frameBytes(samples[i - 1].competitor?.[counter]),
    );
    const own = linkMbit - competitorMbit;
    // A sample counts as loaded once the run itself carries a tenth of the rate, or half of it without competition.
    if (competitorMbit > 0 ? own >= rateMbit / 10 : linkMbit >= rateMbit / 2) {
      queueMs.push((current.backlog * 8) / (rateMbit * 1e3));
      ownMbit.push(own);
    }
  }
  return { loadedSamples: queueMs.length, medianQueueMs: median(queueMs), medianOwnLinkMbit: median(ownMbit) };
}

export function analyse(samples, scenario) {
  if (scenario.downMbit == null) return null;
  return {
    kind: scenario.queue,
    down: direction(samples, "cl", "compdown", scenario.downMbit),
    up: direction(samples, "sv", "compup", scenario.upMbit),
  };
}
