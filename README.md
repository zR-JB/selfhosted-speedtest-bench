# Self-hosted speed test bench

A reproducible comparison of open-source, self-hosted speed test applications: each one deployed from its authors'
own image, driven through its own page in pinned browsers, over the same shaped network paths, and checked against a
reference that does not come from any of the tools.

**Conflict of interest:** this repository is maintained by the author of [Graphite Meter](https://github.com/zR-JB/graphite-meter),
one of the tools compared. Every config, adapter and raw result is published so anyone can check or rerun it, and
corrections to how a tool is set up or read are welcome as issues.

**Status:** results from GitHub runners below. A second dataset from a 16-thread desktop, including 25 and 40 Gbit/s, is being collected.

## What runs

| Tool | Deployment |
| --- | --- |
| Graphite Meter | `ghcr.io/zr-jb/graphite-meter`, defaults |
| LibreSpeed | `ghcr.io/librespeed/speedtest` (`latest` image), defaults (classic page), overhead factor 1 |
| LibreSpeed Go backend | Release binary with its bundled `settings.toml` (no public image), serving its embedded page, overhead factor 1 |
| LibreSpeed Rust backend | `ghcr.io/librespeed/speedtest-rust`, defaults, overhead factor 1 |
| OpenSpeedTest | `openspeedtest/latest`, defaults (nginx, HTTP/1.1), `?clean` |
| Graphite Meter terminal client | Release binary, `--report`, against the Graphite Meter server |
| LibreSpeed CLI | Release binary, `--json`, against the LibreSpeed (PHP) server |

Every tool is scored against the payload rate. Current versions, image digests, browser builds and checksums are in
[`pins.json`](pins.json); each results section names the versions it ran, and each run's manifest records them exactly.

Transport variants, each set up only as its project documents, Chrome only, in the 1, 10, 25 and 40 Gbit/s scenarios
and at 0.1 % loss:

| Variant | Setup | Protocol evidence |
| --- | --- | --- |
| Graphite Meter, HTTP/2 / HTTP/3 / WebTransport | Native TLS listeners (`GM_H1_TLS_ADDR`, `GM_H2_ADDR`, `GM_H3_ADDR`), page over HTTPS, connection path set in its settings | The browser-observed protocol in each saved result |
| LibreSpeed Go backend, HTTP/2 | `enable_tls` and `enable_http2` in its `settings.toml` | The server's negotiated protocol, checked with curl before each run |
| OpenSpeedTest, HTTP/2 | `http2` on its TLS listener plus its documented upload fix, in its nginx config | The same curl check |

All TLS uses one self-signed certificate per job; Chrome trusts its key by hash. Firefox is left out of these
cells: it does not accept a test certificate for QUIC, and Graphite Meter's own tests keep its HTTP/2 cells
Chrome-only for a Firefox worker bug. LibreSpeed's PHP image and Rust backend document no HTTP/2 setting and are not
in this profile.

By default LibreSpeed shows its measured rate × 1.06 and OpenSpeedTest × 1.04, as an estimate of transport overhead.
In both, the factor only multiplies the displayed rate: test duration, stop rules and stream counts use the
unadjusted rate (`speedtest_worker.js` lines 404 to 411 and 562 to 569; `app-2.5.4.js` `upAdjust`, whose only consumer
is the displayed and averaged rate). So the bench turns it off with each project's documented setting
(`setParameter("overheadCompensationFactor", 1)` and the `?clean` URL parameter) and scores every tool against the
same payload rate. A default page shows exactly these numbers × 1.06 or × 1.04.

Browsers: Chrome for Testing and Firefox release builds, fresh profile per run, headed under Xvfb.

## How it works

```
 client container            shaper container                server container
 (browser, iperf3)  <-veth->  tc: netem + tbf  <-veth->  (one tool, fresh each run)
   10.71.1.10        cl: shapes downloads | sv: shapes uploads      10.71.2.10
```

- One Linux host; each role has its own network namespace, joined by direct veth pairs with a 1,500 byte MTU.
  Containers start with `--network none` and the harness wires them; no container bridge, port publishing or NAT is in
  the path. This is the one difference from the
  authors' quick starts, and it applies to every tool alike.
- The shaper applies half the RTT on each side (`netem`), the rate (`tbf`), and the queue: a FIFO of fixed depth, or
  `fq_codel`. Segmentation offloads are off up to 1 Gbit/s and wherever loss applies, so shaping and loss act on real
  frames; the 10, 25 and 40 Gbit/s and unshaped scenarios turn them on, as real network cards do.
- CPU sets and memory caps are fixed per role (shaper, server, client) and the same for every tool.
- Every repetition runs every tool in every browser plus an iperf3 reference, in a seeded random order followed by its
  reverse, so a slow stretch on a shared machine hits every tool alike.
- Each tool is pressed through its own start button; results are read from what the page shows or saves. Adapters are
  in [`bench/driver/adapters`](bench/driver/adapters), one small file per tool. Terminal clients run in the client's
  namespace and their own report is parsed.
- The proxy scenario puts the same nginx in front of every tool whose project documents a proxy setup, with only the
  directives that project's documentation asks for (recorded in `pins.json`).
- The competing-traffic scenario adds one bulk TCP flow each way through the same bottleneck for the whole run.
- The two-server scenario gives each server its own 200 Mbit/s path. Only tools that measure several servers at once
  run in it (Graphite Meter, through its documented server catalogue); the others test one server at a time.
- After every run the harness checks that nothing was left behind (browser processes, helper containers, sampler
  loops) and stops the job otherwise; three harness errors in a row also stop it. A full bench only starts after a
  [smoke](.github/workflows/smoke.yml) of every tool and every scenario passes with no harness error.
- A weekly [watcher](.github/workflows/watch.yml) moves the pins to new releases in a pull request; merging it reruns
  the bench.

## What is compared

| Measure | Reference |
| --- | --- |
| Download and upload | Payload rate: 1,448 of every 1,514 bytes on the wire, where iperf3 shows the link can be filled |
| Download and upload with loss, a long path or competing traffic | None: TCP cannot fill these links, and a tool's share of a shared link grows over its run. The tools are compared with each other and with iperf3; each run's median share under competition, measured on the shaper, is in the raw data |
| Idle latency | Base RTT measured with ping before each block |
| Latency under load | Base RTT plus the bottleneck FIFO's queue delay, sampled on the shaper every 100 ms (FIFO scenarios only; under `fq_codel` a probe flow skips the bulk queue) |
| Server CPU and memory | The server container's cgroup: CPU seconds per GB moved, peak memory |
| Browser CPU | CPU seconds per GB of the browser's process tree |

Scenarios are in [`scenarios.json`](scenarios.json): 100 Mbit/s and 1 Gbit/s at 20 ms RTT; 10, 25 and 40 Gbit/s at
2 ms (25 and 40 only on hosts with at least 8 CPUs); 300/30 Mbit/s behind a 200 ms FIFO; 1 % and 0.1 % loss at 40 ms;
a 160 ms path; competing traffic; a reverse proxy; two servers; and an unshaped run. This testbed cannot show real
network card, Wi-Fi or switch behaviour, and its unshaped scenario shows where each tool runs out of CPU, not a
network's capacity.

## Results: GitHub runners, 18 October 2026

[Bench run 39163069945](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/39163069945) at commit
`0986d68`: 15 independent jobs on GitHub-hosted `ubuntu-24.04` runners (image 20261012.334.1, 4 vCPUs, kernel
6.17.0-1022-azure, rootful Podman). The runners came on five CPU models: AMD EPYC 7763 (10 jobs), EPYC 9V45 (2), EPYC
9V74, Intel Xeon 6973P-C and Xeon Platinum 8573C (1 each). Each job ran 2 repetitions of every scenario, so each tool
and browser has 30 runs per scenario: 4,290 runs, no harness errors, one run that its tool reported incomplete. Versions:
Graphite Meter 0.13.1, LibreSpeed 6.3.0, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest
2.5.4, LibreSpeed CLI 1.0.14, Chrome for Testing 155.0.8059.84, Firefox 158.0. The 25 and 40 Gbit/s scenarios need a
larger host and do not run here.

Values are medians with the 25th and 75th percentile in brackets; error compares the median with the payload rate;
latency references are in brackets.

### What the numbers say

- **Reproducibility:** a second complete run four hours later, on a different mix of runner CPUs
  ([run 39181262815](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/39181262815), Graphite Meter
  0.13.2, everything else identical, raw data in [`results/2026-10-19-ci-run-39181262815`](results/2026-10-19-ci-run-39181262815)),
  reproduced the other tools' medians within 0.1 % (median difference, at most 3.0 %) on links without loss, within
  0.8 % (at most 3.6 %) at 10 Gbit/s and unshaped, and within 1.2 % (at most 25 %) with loss or the 160 ms path, where
  single runs vary most. Graphite Meter 0.13.2 reads like 0.13.1 within the same margins in every HTTP/1.1 cell.
- **Plain links, download:** over HTTP/1.1, every browser tool reads within 0.6 % of the payload rate at 100 Mbit/s and
  1 Gbit/s. Graphite Meter reads 0.3 to 0.4 % above it in Chrome, and in Firefox at 100 Mbit/s: slightly more than the
  link can carry.
- **Plain links, upload:** OpenSpeedTest is the closest in both browsers (within 0.8 % at 100 Mbit/s and 1 Gbit/s).
  The LibreSpeed backends read within 1.2 % in Chrome, but 7.5 to 7.8 % low in Firefox at 1 Gbit/s. Graphite Meter reads
  1.6 % (Chrome) and 2.8 % (Firefox) low at 100 Mbit/s, and 1.8 % and 11.1 % low at 1 Gbit/s.
- **Behind a 200 ms FIFO (300/30 Mbit/s):** Graphite Meter's upload reads within 0.2 % and is the only tool that reports
  latency under load, 4 to 11 ms above the queue reference. OpenSpeedTest's upload reads 7.9 to 8.9 % above the payload
  the link can carry, and LibreSpeed's up to 2.1 % above it: both count uploads where they are sent, so bytes still
  waiting in the queue are counted.
- **Terminal clients:** Graphite Meter's matches iperf3 within 0.1 % in every scored scenario, 10 Gbit/s included.
  LibreSpeed's reads 1.1 to 2.8 % low at 100 Mbit/s, 11.8 % low on upload at 1 Gbit/s and 24 % low on upload at
  10 Gbit/s.
- **10 Gbit/s on 4 vCPUs:** iperf3 and Graphite Meter's client fill the link. In Chrome, downloads reach 9.55 Gbit/s
  with Graphite Meter, 8.6 to 8.7 with the LibreSpeed backends and 7.7 with OpenSpeedTest. Uploads, and Firefox in
  both directions, stop at similar rates for every tool, which points at the browser's CPU; that rate follows the
  runner's CPU model. Chrome uploads, for example, reach 2.2 to 2.5 Gbit/s on the EPYC 7763 and 3.8 to 5.0 Gbit/s on
  the EPYC 9V45 and the two Xeons, with Graphite Meter above OpenSpeedTest on each model.
- **Other transports (Chrome, 1 Gbit/s):** over HTTP/2, OpenSpeedTest stays within 1.9 %, while Graphite Meter's upload
  reads 7.2 % low and LibreSpeed Go's stops at 413 Mbit/s. Graphite Meter's HTTP/3 upload stops near 100 Mbit/s and
  its WebTransport upload near 490 Mbit/s. With 0.1 % loss, every HTTP/2 variant falls to 11 to 16 Mbit/s, below the
  same tools over HTTP/1.1, which use several connections.
- **Behind nginx with each project's documented settings (1 Gbit/s):** Chrome uploads read 2.4 % (Graphite Meter),
  3.7 % (OpenSpeedTest) and 14 % (LibreSpeed) low, against 1.8, 0.5 and 1.2 % direct; in Firefox, LibreSpeed reads 19 %
  low. LibreSpeed's documentation only raises `client_max_body_size`, which leaves nginx's default request buffering on.
- **Loss, long paths and competing traffic** have no single right answer. Tools that open more connections tend to get
  more of a lossy link or a shared one: at 0.1 % loss LibreSpeed reads 93 to 147 Mbit/s down where iperf3 gets 49; under a
  competing flow OpenSpeedTest and Graphite Meter's client get about 80 Mbit/s and Graphite Meter's browser 69 to 75.
- **Two servers:** Graphite Meter measures both paths together within 0.4 % on download, and 1.9 % (Chrome) and 4.9 %
  (Firefox) low on upload; its client is exact.
- **CPU and memory (unshaped):** server CPU per GB is 0.25 to 0.31 s for OpenSpeedTest and the Rust backend, 0.28 to
  0.35 s for Graphite Meter and 0.37 to 0.41 s for LibreSpeed's PHP and Go backends. Peak server memory is 17 to 25 MB
  for OpenSpeedTest, Graphite Meter and the Rust backend, 52 to 56 MB for Go and 81 to 87 MB for the PHP image. Chrome
  uses about 2.7 s of CPU per GB with every tool; in Firefox, Graphite Meter uses 5.0 s, LibreSpeed 6.0 to 6.1 and
  OpenSpeedTest 6.5.
- **Idle latency:** every tool reads within 2 ms of the base RTT. Firefox reports whole milliseconds.

### 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 96.0 [96.0, 96.1] | +0.4 % | 94.1 [93.6, 94.5] | -1.6 % | 20.4 (20.1) | 20.7 (n/a) | 20.5 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 95.7 [95.7, 95.8] | +0.1 % | 95.7 [95.6, 95.7] | +0.0 % | 20.2 (20.1) | 20.3 (n/a) | 20.2 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 96.0 [95.9, 96.4] | +0.4 % | 92.9 [92.5, 93.5] | -2.8 % | 21.0 (20.1) | 27.0 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.7 [95.5, 95.7] | +0.0 % | 95.6 [95.6, 95.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.3 [95.2, 95.5] | -0.4 % | 96.3 [95.5, 96.7] | +0.7 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.6 [94.6, 94.7] | -1.1 % | 93.0 [91.9, 94.1] | -2.8 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.6 [95.5, 95.6] | -0.0 % | 95.1 [94.5, 95.5] | -0.6 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.3 [95.2, 95.3] | -0.4 % | 95.3 [94.3, 95.6] | -0.4 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.6 [95.5, 95.6] | -0.0 % | 94.8 [94.2, 95.8] | -0.9 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.2, 95.3] | -0.4 % | 95.0 [94.5, 95.3] | -0.7 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.5 [95.4, 95.6] | -0.1 % | 95.2 [94.5, 95.7] | -0.5 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.9 [95.2, 96.2] | +0.3 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.7 [95.5, 95.9] | +0.1 % | 96.1 [95.4, 96.8] | +0.4 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |

### 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 959.3 [958.7, 961.3] | +0.3 % | 939.0 [932.5, 942.5] | -1.8 % | 20.4 (20.1) | 22.8 (n/a) | 22.2 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 957.0 [956.4, 957.2] | +0.1 % | 956.5 [956.4, 957.0] | +0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 955.8 [952.8, 958.5] | -0.1 % | 850.2 [828.8, 865.2] | -11.1 % | 21.0 (20.1) | 38.5 (n/a) | 23.8 (n/a) |
| Graphite Meter, HTTP/2, chrome | 30/30 | payload | 951.6 [951.0, 952.1] | -0.5 % | 887.6 [877.8, 907.3] | -7.2 % | 20.4 (20.1) | 22.0 (n/a) | 23.4 (n/a) |
| Graphite Meter, HTTP/3, chrome | 30/30 | payload | 877.2 [855.3, 947.1] | -8.3 % | 101.3 [97.4, 104.0] | -89.4 % | 20.4 (20.1) | 20.8 (n/a) | 20.5 (n/a) |
| Graphite Meter, WebTransport, chrome | 30/30 | payload | 892.9 [850.3, 941.1] | -6.6 % | 490.8 [462.8, 644.4] | -48.7 % | 20.5 (20.1) | 21.2 (n/a) | 22.9 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.4 [956.3, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 956.0 [954.0, 958.0] | -0.0 % | 945.0 [939.3, 948.0] | -1.2 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 935.4 [932.7, 936.3] | -2.2 % | 844.0 [841.9, 845.1] | -11.8 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 951.0 [946.5, 955.0] | -0.6 % | 884.5 [877.0, 894.3] | -7.5 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 956.0 [955.0, 957.0] | -0.0 % | 946.0 [940.5, 954.5] | -1.1 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 953.0 [946.0, 956.0] | -0.4 % | 881.5 [870.3, 903.3] | -7.8 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 946.5 [944.0, 948.0] | -1.0 % | 412.5 [411.0, 414.0] | -56.9 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 956.0 [954.3, 957.8] | -0.0 % | 945.0 [935.3, 953.0] | -1.2 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 952.5 [947.0, 954.0] | -0.4 % | 883.5 [858.5, 899.8] | -7.6 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 953.3 [951.9, 954.1] | -0.3 % | 951.5 [948.3, 953.4] | -0.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 953.6 [952.5, 955.0] | -0.3 % | 948.8 [945.7, 950.7] | -0.8 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 948.4 [945.8, 950.4] | -0.8 % | 938.7 [932.6, 942.1] | -1.9 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. On 4-vCPU runners the browser (two vCPUs) is usually the limit here, so a low reading shows how much of the link a tool can drive on that hardware, not a counting error. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 9551.8 [9497.7, 9593.4] | -0.1 % | 2442.4 [2398.6, 3818.2] | -74.5 % | 2.3 (2.1) | 3.8 (n/a) | 3.9 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.2 (n/a) | 2.2 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 2729.8 [2657.6, 3581.6] | -71.5 % | 2290.3 [2231.8, 2955.3] | -76.1 % | 3.0 (2.1) | 18.8 (n/a) | 31.0 (n/a) |
| Graphite Meter, HTTP/2, chrome | 30/30 | payload | 3725.3 [3599.7, 5083.3] | -61.0 % | 1590.0 [1543.8, 2843.0] | -83.4 % | 2.3 (2.1) | 3.0 (n/a) | 3.9 (n/a) |
| Graphite Meter, HTTP/3, chrome | 30/30 | payload | 879.5 [862.6, 1591.3] | -90.8 % | 496.2 [476.6, 670.2] | -94.8 % | 2.3 (2.1) | 2.7 (n/a) | 6.4 (n/a) |
| Graphite Meter, WebTransport, chrome | 30/30 | payload | 903.8 [875.3, 1650.4] | -90.5 % | 486.8 [470.8, 611.9] | -94.9 % | 2.3 (2.1) | 3.1 (n/a) | 5.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.3 [9564.2, 9564.3] | +0.0 % | 9564.2 [9564.2, 9564.3] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 8700.0 [8478.5, 9306.8] | -9.0 % | 2160.5 [2144.0, 3413.8] | -77.4 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9356.5 [9354.7, 9357.0] | -2.2 % | 7241.4 [7208.9, 7555.2] | -24.3 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 2607.0 [2576.3, 3307.3] | -72.7 % | 2470.0 [2413.8, 3202.5] | -74.2 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 8594.5 [8487.5, 9318.5] | -10.1 % | 2156.0 [2128.0, 3524.5] | -77.5 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 2590.5 [2545.8, 3055.8] | -72.9 % | 2508.5 [2407.0, 3198.8] | -73.8 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 3756.0 [3641.3, 3941.5] | -60.7 % | 1703.5 [1677.3, 2767.5] | -82.2 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 8631.5 [8445.0, 9267.0] | -9.8 % | 2161.5 [2128.3, 3416.0] | -77.4 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 2615.0 [2567.3, 3177.5] | -72.7 % | 2446.5 [2404.0, 3219.3] | -74.4 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 7689.4 [7563.7, 9139.6] | -19.6 % | 2288.6 [2252.9, 3485.7] | -76.1 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 2383.1 [2339.8, 3578.9] | -75.1 % | 2758.4 [2661.7, 3179.8] | -71.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 3799.2 [3711.0, 4791.1] | -60.3 % | 1697.8 [1667.5, 2930.2] | -82.2 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |

### 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Error is against the quantity each tool says it reports. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.6 [28.6, 28.6] | -0.2 % | 20.4 (20.1) | 186.6 (179.6) | 156.4 (152.1) |
| Graphite Meter terminal client | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.2 (20.1) | 186.0 (179.2) | 200.0 (193.9) |
| Graphite Meter, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.6 [28.6, 28.7] | -0.2 % | 21.0 (20.1) | 189.5 (178.3) | 154.0 (145.8) |
| iperf3 (reference) | 30/30 | payload | 286.9 [286.9, 287.0] | -0.0 % | 28.6 [28.6, 28.6] | -0.3 % | n/a (20.1) | n/a (174.8) | n/a (191.2) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 29.1 [28.7, 29.6] | +1.2 % | 20.3 (20.1) | n/a (155.1) | n/a (185.2) |
| LibreSpeed CLI | 30/30 | payload | 282.4 [281.3, 282.9] | -1.6 % | 29.0 [29.0, 29.0] | +1.2 % | 20.2 (20.1) | n/a (175.0) | n/a (177.2) |
| LibreSpeed, firefox | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 29.3 [28.6, 29.7] | +2.1 % | 22.0 (20.1) | n/a (157.6) | n/a (185.3) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 286.0 [285.3, 287.0] | -0.3 % | 28.6 [28.2, 29.2] | -0.5 % | 20.1 (20.1) | n/a (155.1) | n/a (171.4) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 286.0 [285.0, 287.0] | -0.3 % | 29.3 [28.8, 29.6] | +1.9 % | 21.0 (20.1) | n/a (156.6) | n/a (185.6) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 28.5 [27.9, 29.3] | -0.7 % | 20.1 (20.1) | n/a (141.9) | n/a (174.1) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 286.0 [285.3, 287.0] | -0.3 % | 29.0 [28.5, 29.3] | +1.1 % | 22.0 (20.1) | n/a (144.8) | n/a (186.4) |
| OpenSpeedTest, chrome | 30/30 | payload | 286.2 [285.7, 286.8] | -0.3 % | 31.3 [29.9, 31.7] | +8.9 % | 21.0 (20.1) | n/a (160.6) | n/a (196.6) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.8 [286.0, 287.3] | -0.1 % | 31.0 [29.8, 31.6] | +7.9 % | 20.0 (20.1) | n/a (162.0) | n/a (195.0) |

### 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 13.2 [12.8, 13.9] | n/a | 9.8 [9.5, 10.3] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter terminal client | 29/30 | payload | 19.6 [19.0, 20.4] | n/a | 19.8 [19.2, 20.2] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 13.0 [12.8, 13.3] | n/a | 10.2 [9.8, 10.8] | n/a | 41.0 (40.1) | 41.8 (n/a) | 41.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 13.1 [12.7, 13.5] | n/a | 12.8 [12.5, 13.1] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 16.6 [16.3, 17.1] | n/a | 9.6 [9.2, 10.3] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 11.0 [10.5, 11.2] | n/a | 11.8 [11.3, 12.4] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 21.3 [20.6, 22.6] | n/a | 9.4 [9.0, 9.9] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 16.7 [16.0, 17.4] | n/a | 9.6 [9.0, 10.1] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 20.4 [19.7, 21.4] | n/a | 9.3 [8.7, 10.1] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 16.9 [16.4, 17.5] | n/a | 9.6 [9.1, 10.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 21.1 [20.3, 22.2] | n/a | 9.7 [9.3, 10.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 19.4 [19.0, 20.0] | n/a | 21.0 [20.3, 21.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.4 [18.9, 20.1] | n/a | 21.4 [20.8, 22.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

- Graphite Meter terminal client, rep 2: incomplete

### 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 60.0 [56.0, 67.6] | n/a | 47.0 [43.3, 52.0] | n/a | 40.4 (40.1) | 40.5 (n/a) | 40.4 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 88.6 [83.2, 94.3] | n/a | 88.0 [83.3, 92.9] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 58.6 [53.7, 62.8] | n/a | 51.9 [42.4, 59.7] | n/a | 41.0 (40.1) | 42.0 (n/a) | 41.0 (n/a) |
| Graphite Meter, HTTP/2, chrome | 30/30 | payload | 15.9 [12.2, 19.2] | n/a | 14.9 [11.7, 16.1] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter, HTTP/3, chrome | 30/30 | payload | 77.0 [58.3, 103.1] | n/a | 20.1 [15.7, 27.3] | n/a | 40.5 (40.1) | 40.5 (n/a) | 40.4 (n/a) |
| Graphite Meter, WebTransport, chrome | 30/30 | payload | 86.6 [69.6, 107.6] | n/a | 30.4 [26.5, 33.6] | n/a | 40.5 (40.1) | 40.5 (n/a) | 40.4 (n/a) |
| iperf3 (reference) | 30/30 | payload | 49.3 [46.1, 51.9] | n/a | 49.9 [47.5, 52.6] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 101.0 [92.4, 107.8] | n/a | 38.4 [34.1, 42.7] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 49.3 [42.7, 55.1] | n/a | 45.2 [41.5, 48.1] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 134.0 [121.8, 167.5] | n/a | 39.8 [35.3, 44.1] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 93.3 [87.7, 102.8] | n/a | 55.4 [42.3, 75.7] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 147.0 [121.0, 160.8] | n/a | 36.1 [33.3, 41.3] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 13.0 [11.8, 14.3] | n/a | 11.9 [11.0, 14.1] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 109.0 [91.0, 126.8] | n/a | 65.3 [54.6, 71.7] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 132.0 [110.8, 172.0] | n/a | 39.1 [35.4, 42.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 78.5 [74.8, 82.7] | n/a | 87.1 [81.9, 96.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 76.7 [74.4, 79.9] | n/a | 87.5 [84.2, 92.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 11.2 [9.9, 13.0] | n/a | 15.8 [11.8, 17.8] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

### 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 271.7 [261.0, 277.9] | n/a | 219.6 [213.0, 224.3] | n/a | 160.5 (160.1) | 160.8 (n/a) | 160.5 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 276.5 [265.1, 279.5] | n/a | 281.3 [276.2, 286.2] | n/a | 160.0 (160.1) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 266.3 [258.0, 270.8] | n/a | 191.6 [189.3, 196.4] | n/a | 161.0 (160.1) | 164.5 (n/a) | 161.5 (n/a) |
| iperf3 (reference) | 30/30 | payload | 246.7 [232.6, 264.2] | n/a | 247.7 [237.0, 263.8] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 247.5 [242.8, 251.0] | n/a | 233.0 [229.0, 238.3] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 210.6 [204.5, 217.7] | n/a | 116.7 [116.1, 117.2] | n/a | 160.3 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 249.0 [244.5, 253.5] | n/a | 228.0 [221.0, 235.0] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 247.0 [240.3, 250.0] | n/a | 234.5 [227.3, 238.8] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 246.0 [242.0, 250.0] | n/a | 225.0 [220.0, 233.0] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 244.5 [240.5, 249.0] | n/a | 236.5 [233.0, 242.8] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 251.0 [244.3, 252.0] | n/a | 225.0 [216.5, 230.0] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 277.7 [271.9, 282.4] | n/a | 269.4 [264.6, 274.2] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 273.5 [270.9, 275.8] | n/a | 266.8 [263.7, 273.7] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |

### 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 75.3 [75.2, 75.4] | n/a | 69.4 [69.3, 69.5] | n/a | 20.5 (20.1) | 20.7 (n/a) | 20.5 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 80.4 [80.3, 80.4] | n/a | 80.8 [80.8, 80.8] | n/a | 20.3 (20.1) | 20.3 (n/a) | 20.3 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 75.2 [75.1, 75.4] | n/a | 68.7 [68.4, 69.0] | n/a | 21.0 (20.1) | 25.5 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 75.0 [74.9, 75.1] | n/a | 75.2 [75.1, 75.3] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.9 [77.7, 78.0] | n/a | 70.3 [69.0, 71.7] | n/a | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.4 [69.3, 69.4] | n/a | 68.5 [68.3, 68.8] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.3 [80.3, 80.4] | n/a | 70.3 [69.6, 70.8] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.8 [77.7, 77.9] | n/a | 71.7 [71.6, 72.0] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 80.3 [80.2, 80.5] | n/a | 70.3 [69.7, 70.8] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 71.7 [71.6, 73.0] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.3 [80.2, 80.4] | n/a | 70.8 [69.8, 71.1] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.2 [80.2, 80.3] | n/a | 80.4 [80.1, 80.9] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.4 [80.3, 80.5] | n/a | 80.5 [79.8, 80.8] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 959.1 [957.6, 959.8] | +0.3 % | 933.0 [924.0, 940.0] | -2.4 % | 20.4 (20.1) | 22.9 (n/a) | 25.2 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 956.2 [953.4, 959.2] | -0.0 % | 863.7 [836.8, 876.4] | -9.7 % | 21.0 (20.1) | 37.5 (n/a) | 26.5 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | -0.0 % | 956.3 [956.2, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 954.5 [944.0, 957.0] | -0.2 % | 822.5 [796.3, 861.3] | -14.0 % | 20.6 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 940.5 [918.5, 952.0] | -1.7 % | 775.5 [737.8, 814.0] | -18.9 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 953.2 [952.8, 954.1] | -0.3 % | 921.4 [915.1, 925.7] | -3.7 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 952.1 [951.1, 955.0] | -0.4 % | 903.7 [897.8, 905.7] | -5.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 383.9 [383.8, 384.0] | +0.3 % | 375.2 [374.4, 376.1] | -1.9 % | 20.4 (20.1) | 21.0 (n/a) | 20.6 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.8 [382.7, 382.9] | +0.0 % | 20.2 (20.1) | 20.4 (n/a) | 20.2 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 384.0 [383.8, 384.5] | +0.4 % | 363.8 [360.9, 366.4] | -4.9 % | 21.0 (20.1) | 25.0 (n/a) | 22.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.6 [382.5, 382.6] | +0.0 % | 382.6 [382.5, 382.6] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

### Unshaped, offloads on: as fast as the host allows

No shaping: the host's CPU is the limit, so rates show how far each tool gets on it, not a network's capacity. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | 10281.8 [10073.6, 15657.3] | 2936.4 [2820.3, 5084.0] | 0.35 | 23 | 2.72 |
| Graphite Meter terminal client | 30/30 | 29135.0 [27727.5, 42095.0] | 63080.0 [61920.0, 63947.5] | 0.19 | 17 | n/a |
| Graphite Meter, firefox | 30/30 | 2984.7 [2872.6, 3806.5] | 2437.7 [2376.5, 3189.6] | 0.28 | 21 | 4.97 |
| iperf3 (reference) | 30/30 | 32280.3 [31756.6, 37401.3] | 44212.7 [43603.0, 51826.6] | 0.20 | 11 | n/a |
| LibreSpeed, chrome | 30/30 | 9030.5 [8738.8, 10810.3] | 2814.5 [2765.3, 4729.3] | 0.37 | 81 | 2.68 |
| LibreSpeed CLI | 30/30 | 33377.0 [32475.3, 38675.3] | 14279.3 [14062.3, 19633.6] | 0.28 | 74 | n/a |
| LibreSpeed, firefox | 30/30 | 2699.5 [2648.3, 3176.5] | 2645.0 [2591.3, 3587.5] | 0.40 | 87 | 6.04 |
| LibreSpeed Go backend, chrome | 30/30 | 8630.0 [8450.0, 10909.3] | 2820.5 [2760.0, 5033.5] | 0.41 | 52 | 2.71 |
| LibreSpeed Go backend, firefox | 30/30 | 2685.0 [2638.0, 3141.5] | 2683.0 [2601.5, 3538.8] | 0.38 | 56 | 6.04 |
| LibreSpeed Rust backend, chrome | 30/30 | 8881.5 [8756.0, 10143.0] | 2784.0 [2714.0, 4651.0] | 0.30 | 21 | 2.74 |
| LibreSpeed Rust backend, firefox | 30/30 | 2679.5 [2630.3, 3264.8] | 2600.0 [2581.3, 3525.5] | 0.31 | 25 | 6.11 |
| OpenSpeedTest, chrome | 30/30 | 7790.9 [7607.4, 9929.9] | 2934.1 [2892.9, 5113.2] | 0.25 | 20 | 2.76 |
| OpenSpeedTest, firefox | 30/30 | 2415.9 [2392.7, 3667.7] | 2785.8 [2671.8, 3576.5] | 0.31 | 17 | 6.49 |

Raw data: [`results/2026-10-18-ci-run-39163069945`](results/2026-10-18-ci-run-39163069945), one JSON per run and each
job's manifest (pins, host, CPU sets, block order, noise checks). Screenshots of every run's final screen are in the
run's artifacts. Earlier runs with other settings, superseded by this one, are kept in `results/` with their manifests.

## Run it

Needs Linux with cgroup v2, Podman, Node 22 or later, `nsenter`, `ethtool`, `curl`, `unzip` and `xz`. Rootless Podman
works; set `SB_ROOTFUL=1` to use `sudo podman` instead. Several instances can share a machine: `SB_PREFIX` names their
containers and `SB_CPUSETS` (for example `{"shaper":"6","server":"14","client":"7,15"}`) gives each its own cores.
`SB_PIN_OVERRIDES` swaps pins for a local experiment, such as a locally built image (`localhost/...`) of a fix branch;
the run's manifest records what ran.

```sh
node bench/run.js --scenarios accuracy-100 --reps 1
node bench/summarize.js results/local-*
```

Published numbers come from the [Bench workflow](.github/workflows/bench.yml) on GitHub-hosted runners, where every
log is public, and from full campaigns on a named local machine, whose raw data and manifests are committed the same
way. Shorter local runs are for development.
