# Self-hosted speed test bench

A reproducible comparison of open-source, self-hosted speed test applications: each one deployed from its authors'
own image, driven through its own page in pinned browsers, over the same shaped network paths, and checked against a
reference that does not come from any of the tools.

**Conflict of interest:** this repository is maintained by the author of [Graphite Meter](https://github.com/zR-JB/graphite-meter),
one of the tools compared. Every config, adapter and raw result is published so anyone can check or rerun it, and
corrections to how a tool is set up or read are welcome as issues.

**Status:** first results below (18 October 2026). Two tools so far; more will follow.

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

## Results, 18 October 2026

[Bench run 39131795262](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/39131795262): 6 independent
jobs on GitHub-hosted `ubuntu-24.04` runners (image 20261012.334.1, 4 vCPUs, kernel 6.17.0-1022-azure, rootful
Podman), three on AMD EPYC 7763 and three on AMD EPYC 9V74 hosts. 3 repetitions per scenario in each job, so 18 runs
per tool, browser and scenario; 360 runs, all complete. Graphite Meter 0.13.1, LibreSpeed 6.3.0 (`latest` image of
that day), Chrome for Testing 155.0.8059.84, Firefox 158.0. Values are medians; error compares the median with the
quantity each tool says it reports; latency references are in brackets.

### 100/100 Mbit/s, 20 ms RTT, fq_codel

Payload reference 95.6 / 95.6 Mbit/s; link rate 100 / 100 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference.

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 18/18 | payload | 96.0 | +0.4 % | 94.1 | -1.6 % | 20.4 (20.1) | 20.6 (n/a) | 20.5 (n/a) |
| Graphite Meter, firefox | 18/18 | payload | 96.1 | +0.5 % | 93.2 | -2.6 % | 21.0 (20.1) | 25.8 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 18/18 | payload | 95.6 | -0.0 % | 95.6 | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 18/18 | link | 101.0 | +1.0 % | 102.0 | +2.0 % | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 18/18 | link | 101.0 | +1.0 % | 101.0 | +1.0 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |

### 1/1 Gbit/s, 20 ms RTT, fq_codel

Payload reference 956.4 / 956.4 Mbit/s; link rate 1000 / 1000 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference.

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 18/18 | payload | 960.3 | +0.4 % | 936.6 | -2.1 % | 20.4 (20.1) | 22.6 (n/a) | 24.3 (n/a) |
| Graphite Meter, firefox | 18/18 | payload | 953.8 | -0.3 % | 841.6 | -12.0 % | 21.0 (20.1) | 39.8 (n/a) | 24.0 (n/a) |
| iperf3 (reference) | 18/18 | payload | 956.4 | +0.0 % | 956.4 | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 18/18 | link | 1013.0 | +1.3 % | 1003.5 | +0.4 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 18/18 | link | 1010.5 | +1.0 % | 943.5 | -5.6 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Payload reference 286.9 / 28.7 Mbit/s; link rate 300 / 30 Mbit/s. Error is against the quantity each tool says it reports.

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 18/18 | payload | 286.9 | +0.0 % | 28.6 | -0.2 % | 20.3 (20.1) | 183.1 (179.8) | 160.4 (153.2) |
| Graphite Meter, firefox | 18/18 | payload | 286.9 | -0.0 % | 28.6 | -0.2 % | 21.0 (20.1) | 194.0 (179.9) | 161.3 (150.7) |
| iperf3 (reference) | 18/18 | payload | 286.9 | -0.0 % | 28.6 | -0.3 % | n/a (20.1) | n/a (174.9) | n/a (186.9) |
| LibreSpeed, chrome | 18/18 | link | 303.0 | +1.0 % | 30.6 | +2.0 % | 20.4 (20.1) | n/a (156.2) | n/a (186.4) |
| LibreSpeed, firefox | 18/18 | link | 304.0 | +1.3 % | 31.0 | +3.5 % | 22.0 (20.1) | n/a (160.7) | n/a (184.5) |

### Unshaped veth, CPU cost only

No shaping: rates measure the host, not a network, so only CPU cost is compared.

| Tool | Runs ok | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 18/18 | 0.69 | 14 | 6.86 |
| Graphite Meter, firefox | 18/18 | 0.69 | 19 | 9.27 |
| iperf3 (reference) | 18/18 | 1.04 | 25 | n/a |
| LibreSpeed, chrome | 18/18 | 0.82 | 74 | 4.33 |
| LibreSpeed, firefox | 18/18 | 0.77 | 83 | 7.31 |

Raw data: [`results/2026-10-18-run-39131795262`](results/2026-10-18-run-39131795262), one JSON per run plus each
job's manifest. Screenshots of every run's final screen are in the run's artifacts.

### What the numbers say

- **Download:** both tools land within 1.3 % of the quantity they report in every shaped scenario, in both browsers.
- **Upload:** Graphite Meter reads within 0.3 % of the payload rate behind the 200 ms FIFO and 1.6 to 2.6 % low at
  100 Mbit/s. LibreSpeed's upload reads 1 to 3.5 % above the link rate itself at 100 and 30 Mbit/s, a rate the link
  cannot carry.
- **Firefox at 1 Gbit/s upload:** both tools read low in Firefox only: Graphite Meter by 12 %, LibreSpeed by 5.6 %;
  Chrome stays within 2.1 %. The cause is not yet investigated; these runners have 4 vCPUs shared by browser, shaper
  and server.
- **Latency under load:** only Graphite Meter reports it. Behind the 200 ms FIFO its loaded medians are 3 to 14 ms
  above the queue reference (for example 183.1 ms against 179.8 ms for downloads in Chrome). LibreSpeed reports idle
  latency only.
- **Idle latency:** both tools are within 2 ms of the 20.1 ms base RTT. Firefox values are whole milliseconds.
- **CPU and memory:** Graphite Meter's server used less CPU per GB (0.69 s against 0.77 to 0.82 s) and less peak memory
  (14 to 19 MB against 74 to 83 MB). LibreSpeed's page used less browser CPU per GB: 4.33 s against 6.86 s in Chrome,
  7.31 s against 9.27 s in Firefox.
- LibreSpeed shows rates to three significant digits, so its medians step in whole Mbit/s.

## Run it

Needs Linux with cgroup v2, Podman, Node 22 or later, `nsenter`, `ethtool`, `curl`, `unzip` and `xz`. Rootless Podman
works; set `SB_ROOTFUL=1` to use `sudo podman` instead.

```sh
node bench/run.js --scenarios accuracy-100 --reps 1
node bench/summarize.js results/local-*
```

Published numbers come from the [Bench workflow](.github/workflows/bench.yml) on GitHub-hosted runners, where every
log is public; local runs are for development.
