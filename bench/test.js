import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import { join } from "node:path";
import test from "node:test";
import { analyse } from "./reference.js";
import { quantile, readResults } from "./results.js";
import { serverPhases } from "./testbed.js";

test("quantile computes exact inclusive quartiles and handles empty input", () => {
  assert.equal(quantile([], 0.5), null);
  assert.equal(quantile([42], 0.5), 42);
  assert.equal(quantile([10, 20, 30, 40], 0.5), 25);
  assert.equal(quantile([10, 20, 30, 40], 0.25), 17.5);
  assert.equal(quantile([10, 20, 30, 40], 0.75), 32.5);
});

test("readResults filters pre-noise, post-noise, high CPU steal, and collapsed clean-link iperf3 blocks", () => {
  const tmp = mkdtempSync(join(os.tmpdir(), "sb-unit-"));
  try {
    mkdirSync(join(tmp, "runs"));
    const blocks = [
      // Healthy clean block
      { scenario: "accuracy-1000", rep: 1, noise: { hashMs: 100, stealTicks: 0 }, noiseAfter: { hashMs: 102, stealTicks: 10 }, startedAt: 1_000, endedAt: 31_000 },
      // Post-block CPU contention (> 1.25x median hashMs)
      { scenario: "accuracy-1000", rep: 2, noise: { hashMs: 100, stealTicks: 10 }, noiseAfter: { hashMs: 165, stealTicks: 20 }, startedAt: 32_000, endedAt: 62_000 },
      // High hypervisor steal (> 5% of 4 CPUs * 30s * 100 ticks = 600 ticks)
      { scenario: "accuracy-100", rep: 1, noise: { hashMs: 100, stealTicks: 20 }, noiseAfter: { hashMs: 101, stealTicks: 1_500 }, startedAt: 63_000, endedAt: 93_000 },
      // Clean shaped link where iperf3 control collapsed (< 75% ceiling)
      { scenario: "accuracy-100", rep: 2, noise: { hashMs: 100, stealTicks: 1_500 }, noiseAfter: { hashMs: 101, stealTicks: 1_505 }, startedAt: 94_000, endedAt: 124_000 },
      // Lossy link: low iperf3 rate is expected and must NOT be excluded
      { scenario: "loss-100", rep: 1, noise: { hashMs: 100, stealTicks: 1_505 }, noiseAfter: { hashMs: 100, stealTicks: 1_510 }, startedAt: 125_000, endedAt: 155_000 },
      // Legacy manifest block without noiseAfter/startedAt/endedAt: healthy
      { scenario: "proxy-1000", rep: 1, noise: { hashMs: 101, stealTicks: 1_510 } },
    ];
    writeFileSync(join(tmp, "manifest.json"), JSON.stringify({ host: { cpus: 4 }, blocks }));
    const write = (name, obj) => writeFileSync(join(tmp, "runs", `${name}.json`), JSON.stringify(obj));

    write("1", { scenario: "accuracy-1000", rep: 1, tool: "iperf3", reported: { outcome: "complete", downloadMbit: 956, uploadMbit: 956 } });
    write("2", { scenario: "accuracy-1000", rep: 1, tool: "graphite-meter", reported: { outcome: "complete", downloadMbit: 956, uploadMbit: 955 } });
    write("3", { scenario: "accuracy-1000", rep: 2, tool: "iperf3", reported: { outcome: "complete", downloadMbit: 956, uploadMbit: 956 } });
    write("4", { scenario: "accuracy-100", rep: 1, tool: "iperf3", reported: { outcome: "complete", downloadMbit: 95.6, uploadMbit: 95.6 } });
    write("5", { scenario: "accuracy-100", rep: 2, tool: "iperf3", reported: { outcome: "complete", downloadMbit: 42, uploadMbit: 95.6 } });
    write("6", { scenario: "accuracy-100", rep: 2, tool: "graphite-meter", reported: { outcome: "complete", downloadMbit: 45, uploadMbit: 95.6 } });
    write("7", { scenario: "loss-100", rep: 1, tool: "iperf3", reported: { outcome: "complete", downloadMbit: 12.8, uploadMbit: 12.7 } });
    write("8", { scenario: "proxy-1000", rep: 1, tool: "iperf3", reported: { outcome: "complete", downloadMbit: 956, uploadMbit: 956 } });

    const { runs, noisy } = readResults([tmp]);
    assert.equal(noisy, 4);
    assert.equal(runs.length, 4);
    assert.deepEqual(
      runs.map((r) => `${r.scenario}:${r.rep}:${r.tool}`).sort(),
      [
        "accuracy-1000:1:graphite-meter",
        "accuracy-1000:1:iperf3",
        "loss-100:1:iperf3",
        "proxy-1000:1:iperf3",
      ],
    );
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
});

test("serverPhases separates sustained download, upload, and short bursts into other", () => {
  // Format: [t_ms, user_usec, sys_usec, rx_bytes, tx_bytes]
  const samples = [];
  let t = 0;
  let u = 0;
  let s = 0;
  let rx = 0;
  let tx = 0;
  samples.push([t, u, s, rx, tx]);
  // 2 intervals short burst (200 ms -> < 500 ms threshold -> "other"), followed by 1 idle interval
  for (let i = 0; i < 2; i++) {
    t += 100; u += 10_000; tx += 1_000_000;
    samples.push([t, u, s, rx, tx]);
  }
  t += 100;
  samples.push([t, u, s, rx, tx]);
  // 6 intervals sustained download (server tx dominant, 10 MB / 100ms)
  for (let i = 0; i < 6; i++) {
    t += 100; u += 20_000; s += 10_000; tx += 10_000_000; rx += 100_000;
    samples.push([t, u, s, rx, tx]);
  }
  // 6 intervals sustained upload (server rx dominant, 10 MB / 100ms)
  for (let i = 0; i < 6; i++) {
    t += 100; u += 50_000; s += 50_000; rx += 10_000_000; tx += 100_000;
    samples.push([t, u, s, rx, tx]);
  }
  const split = serverPhases(samples);
  assert.ok(Math.abs(split.other.cpuSeconds - 0.02) < 1e-6);
  assert.ok(Math.abs(split.down.cpuSeconds - 0.18) < 1e-6);
  assert.equal(split.down.directionBytes, 60_000_000);
  assert.equal(split.down.milliseconds, 600);
  assert.ok(Math.abs(split.up.cpuSeconds - 0.60) < 1e-6);
  assert.equal(split.up.directionBytes, 60_000_000);
  assert.equal(split.up.milliseconds, 600);
});

test("reference.analyse computes FIFO queue delay and skips unshaped scenarios", () => {
  assert.equal(analyse([], { downMbit: null, upMbit: null }), null);
  // 30 Mbit/s upload => 3.75 MB/s; 750,000 bytes backlog = 200 ms queue delay
  const mkSample = (t, bytes, backlog) => ({
    t,
    qdiscs: [
      { dev: "cl", kind: "tbf", bytes: 0, backlog: 0 },
      { dev: "sv", kind: "tbf", bytes, backlog },
    ],
    competitor: {},
  });
  const res = analyse(
    [mkSample(0, 0, 0), mkSample(0.1, 375_000, 750_000), mkSample(0.2, 750_000, 750_000)],
    { downMbit: 300, upMbit: 30, queue: "fifo" },
  );
  assert.equal(res.kind, "fifo");
  assert.equal(res.up.loadedSamples, 2);
  assert.ok(Math.abs(res.up.medianQueueMs - 200) < 1e-6);
  assert.ok(Math.abs(res.up.medianOwnLinkMbit - 30) < 1e-6);
});
