# Self-hosted speed test bench

A reproducible comparison of open-source, self-hosted speed test applications: each one deployed from its authors'
own image, driven through its own page in pinned browsers, over the same shaped network paths, and checked against a
reference that does not come from any of the tools.

**Conflict of interest:** this repository is maintained by the author of [Graphite Meter](https://github.com/zR-JB/graphite-meter),
one of the tools compared. Every config, adapter and raw result is published so anyone can check or rerun it, and
corrections to how a tool is set up or read are welcome as issues.

**Status:** under construction. No results are published yet.

## What runs

| Tool | Version | Deployment | Reports |
| --- | --- | --- | --- |
| Graphite Meter | 0.13.1 | `ghcr.io/zr-jb/graphite-meter`, defaults | Payload rate |
| LibreSpeed | 6.3.0 (`latest` image) | `ghcr.io/librespeed/speedtest`, defaults (classic page) | Payload × 1.06, its default estimate of transport overhead |

Exact image digests, browser builds and checksums are in [`pins.json`](pins.json) and in every run's manifest.
Browsers: Chrome for Testing and Firefox release builds, fresh profile per run, headed under Xvfb.

## How it works

```
 client container            shaper container                server container
 (browser, iperf3)  <-veth->  tc: netem + tbf  <-veth->  (one tool, fresh each run)
   10.71.1.10        cl: shapes downloads | sv: shapes uploads      10.71.2.10
```

- One Linux host; each role has its own network namespace, joined by direct veth pairs with a 1,500 byte MTU and
  segmentation offloads off, so the shaper sees real frames. Containers start with `--network none` and the harness
  wires them; no container bridge, port publishing or NAT is in the path. This is the one difference from the
  authors' quick starts, and it applies to every tool alike.
- The shaper applies half the RTT on each side (`netem`), the rate (`tbf`), and the queue: a FIFO of fixed depth, or
  `fq_codel`.
- CPU sets are fixed per role (shaper, server, client) and the same for every tool.
- Every repetition runs every tool in every browser plus an iperf3 reference, in a seeded random order followed by its
  reverse, so a slow stretch on a shared machine hits every tool alike.
- Each tool is pressed through its own start button; results are read from what the page shows or saves. Adapters are
  in [`bench/driver/adapters`](bench/driver/adapters), one small file per tool.

## What is compared

| Measure | Reference |
| --- | --- |
| Download and upload | Shaped link rate, and payload rate (1,448 of every 1,514 bytes on the wire). Each tool is scored against the quantity it says it reports. |
| Idle latency | Base RTT measured with ping before each block |
| Latency under load | Base RTT plus the bottleneck FIFO's queue delay, sampled on the shaper every 100 ms (FIFO scenarios only; under `fq_codel` a probe flow skips the bulk queue) |
| Server CPU and memory | The server container's cgroup: CPU seconds per GB moved, peak memory |
| Browser CPU | CPU seconds per GB of the browser's process tree |

Scenarios are in [`scenarios.json`](scenarios.json). This testbed cannot show real network card, Wi-Fi or switch
behaviour, and its unshaped scenario measures CPU cost, not network capacity.

## Run it

Needs Linux with cgroup v2, Podman, Node 22 or later, `nsenter`, `ethtool`, `curl`, `unzip` and `xz`. Rootless Podman
works; set `SB_ROOTFUL=1` to use `sudo podman` instead.

```sh
node bench/run.js --scenarios accuracy-100 --reps 1
node bench/summarize.js results/local-*
```

Published numbers come from the [Bench workflow](.github/workflows/bench.yml) on GitHub-hosted runners, where every
log is public; local runs are for development.
