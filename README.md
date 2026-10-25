# Self-hosted speed test bench

A reproducible comparison of open-source, self-hosted speed test applications: each one deployed from its authors'
own image, driven through its own page in pinned browsers, over the same shaped network paths, and checked against a
reference that does not come from any of the tools.

**Conflict of interest:** this repository is maintained by the author of [Graphite Meter](https://github.com/zR-JB/graphite-meter),
one of the tools compared. Every config, adapter and raw result is published so anyone can check or rerun it, and
corrections to how a tool is set up or read are welcome as issues.

**Status:** results from GitHub runners and from a 16-thread desktop below.

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

Transport variants, each set up only as its project documents, in Chrome in the 1, 10, 25 and 40 Gbit/s scenarios and at
0.1 % loss, and for Graphite Meter's terminal client in those scenarios and the unshaped one:

| Variant | Setup | Protocol evidence |
| --- | --- | --- |
| Graphite Meter, HTTP/2 / HTTP/3 / WebTransport | Native TLS listeners (`GM_H1_TLS_ADDR`, `GM_H2_ADDR`, `GM_H3_ADDR`), page over HTTPS, connection path set in its settings | The browser-observed protocol in each saved result |
| LibreSpeed Go backend, HTTP/2 | `enable_tls` and `enable_http2` in its `settings.toml` | The server's negotiated protocol, checked with curl before each run |
| OpenSpeedTest, HTTP/2 | `http2` on its TLS listener plus its documented upload fix, in its nginx config | The same curl check |
| Graphite Meter terminal client, HTTP/2 / HTTP/3 | The same native listeners; `--throughput-protocol`, `--throughput-transport fetch-stream` and `--latency-transport websocket`, as the browser variants set their connection path | The client offers only that protocol in its TLS handshake, so it cannot fall back |

All TLS uses one self-signed certificate per job; Chrome trusts its key by hash and the terminal client takes it with
its documented `--insecure`. Firefox is left out of these cells: it does not accept a test certificate for QUIC, and
Graphite Meter's own tests keep its HTTP/2 cells Chrome-only for a Firefox worker bug. LibreSpeed's PHP image and Rust
backend document no HTTP/2 setting and are not in this profile.

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
| Server CPU and memory | The server container's cgroup: CPU seconds per GB moved, peak memory; each run also splits that CPU by 100 ms samples into download, upload and other phases, which `bench/phases.js` tables |
| Browser CPU | CPU seconds per GB of the browser's process tree |

Scenarios are in [`scenarios.json`](scenarios.json): 100 Mbit/s and 1 Gbit/s at 20 ms RTT; 10, 25 and 40 Gbit/s at
2 ms (25 and 40 only on hosts with at least 8 CPUs); 300/30 Mbit/s behind a 200 ms FIFO; 1 % and 0.1 % loss at 40 ms;
a 160 ms path; competing traffic; a reverse proxy; two servers; and an unshaped run. This testbed cannot show real
network card, Wi-Fi or switch behaviour, and its unshaped scenario shows where each tool runs out of CPU, not a
network's capacity.

## Results: GitHub runners, 22 October 2026

[Bench run 39772524145](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/39772524145) at commit
`459cc32`: 15 independent jobs on GitHub-hosted `ubuntu-24.04` runners (images 20261012.334.1, 20261018.339.1 and
20261021.345.10, 4 vCPUs, kernel 6.17.0-1022-azure on 9 jobs and 7.0.0-1017-azure on 6, rootful Podman). The runners
came on four CPU models: AMD EPYC 7763 (6 jobs), EPYC 9V45 (4), EPYC 9V74 (4) and Intel Xeon Platinum 8370C (1). Each
job ran 2 repetitions of every scenario, so each tool and browser has 30 runs per scenario: 4,290 runs, all complete.
Versions: Graphite Meter 0.13.4 (server and terminal client), LibreSpeed 6.3.1, LibreSpeed Go backend 1.1.6,
LibreSpeed Rust backend 1.4.0, OpenSpeedTest 2.5.4, LibreSpeed CLI 1.0.14, Chrome for Testing 156.0.8078.47, Firefox
158.0.1. The 25 and 40 Gbit/s scenarios need a larger host and do not run here.

Values are medians with the 25th and 75th percentile in brackets; error compares the median with the payload rate;
latency references are in brackets.

### What the numbers say

- **Plain links, download:** over HTTP/1.1, every browser tool reads within 0.4 % of the payload rate at 100 Mbit/s.
  At 1 Gbit/s, Graphite Meter reads within 0.2 % and OpenSpeedTest within 0.6 % in both browsers; the LibreSpeed
  backends read within 0.1 % in Chrome and 1.3 to 2.0 % low in Firefox.
- **Plain links, upload:** at 100 Mbit/s and 1 Gbit/s, Graphite Meter reads within 0.4 % in both browsers and
  OpenSpeedTest within 0.7 %. The LibreSpeed backends read within 1.3 % in Chrome, but 6.6 to 7.5 % low in Firefox at
  1 Gbit/s.
- **Behind a 200 ms FIFO (300/30 Mbit/s):** Graphite Meter's upload reads within 0.1 % and it is the only tool that
  reports latency under load, 1 to 11 ms above the queue reference. OpenSpeedTest's upload reads 8.6 to 9.4 % above
  the payload the link can carry, and LibreSpeed's up to 3.3 % above it: both count uploads where they are sent, so
  bytes still waiting in the queue are counted.
- **Terminal clients:** Graphite Meter's reads within 0.1 % of the payload rate in every scored scenario, 10 Gbit/s
  included. LibreSpeed's reads 1.0 to 2.8 % low at 100 Mbit/s, 11.5 % low on upload at 1 Gbit/s and 20 % low on
  upload at 10 Gbit/s.
- **10 Gbit/s on 4 vCPUs:** iperf3 and Graphite Meter's client fill the link, and so does Graphite Meter's Chrome
  download (9.56 Gbit/s); the LibreSpeed backends reach 9.1 to 9.2 and OpenSpeedTest 8.7. Uploads, and Firefox in both
  directions, stop where the browser runs out of CPU, so they follow the runner's CPU model: Chrome uploads reach 2.1
  to 2.7 Gbit/s on the EPYC 7763 and 4.1 to 5.5 on the EPYC 9V45. Graphite Meter's uploads are the fastest on every
  CPU model in both browsers; in Firefox it reaches 3.4 Gbit/s down and 5.4 up, the others 2.6 to 2.8 and 3.0.
- **Other transports (Chrome, 1 Gbit/s):** over HTTP/2, Graphite Meter reads 0.6 % low on download and 1.8 % on
  upload, OpenSpeedTest 0.7 and 1.9 %, and LibreSpeed Go's upload stops at 414 Mbit/s. Graphite Meter's HTTP/3 upload
  stops near 140 Mbit/s and its WebTransport upload near 670 Mbit/s. With 0.1 % loss, every HTTP/2 variant falls to 12
  to 16 Mbit/s, below the same tools over HTTP/1.1, which use several connections.
- **Behind nginx with each project's documented settings (1 Gbit/s):** Chrome uploads read 0.3 % (Graphite Meter),
  3.8 % (OpenSpeedTest) and 8.4 % (LibreSpeed) low, against 0.4, 0.4 and 1.3 % direct; Firefox uploads 0.1, 5.0 and
  13.7 % low, against 0.3, 0.7 and 6.6 %. LibreSpeed's documentation only raises `client_max_body_size`, which leaves
  nginx's default request buffering on.
- **Loss, long paths and competing traffic** have no single right answer. Tools that open more connections tend to get
  more of a lossy link or a shared one: at 0.1 % loss the LibreSpeed backends read 97 to 133 Mbit/s down where iperf3
  gets 50; under a competing flow OpenSpeedTest and Graphite Meter's client get about 80 Mbit/s, and Graphite Meter's
  browser about 75, like iperf3. Both runner kernels give similar loss results (iperf3 at 1 % loss: 13.1 and 12.9
  Mbit/s down).
- **Two servers:** Graphite Meter measures both paths together within 0.3 % in both browsers and directions; its
  client is exact.
- **CPU and memory (unshaped):** server CPU per GB is 0.21 to 0.26 s for OpenSpeedTest and the Rust backend, 0.27 to
  0.30 s for Graphite Meter and 0.32 to 0.34 s for LibreSpeed's PHP and Go backends. Peak server memory is 8 MB for
  Graphite Meter, 18 to 25 MB for OpenSpeedTest and the Rust backend, 50 to 54 MB for Go and 82 to 87 MB for the PHP
  image. Browser CPU per GB in Chrome is 2.0 s with Graphite Meter and 2.2 with the others; in Firefox, 2.9 s with
  Graphite Meter and 5.5 to 5.8 with the others.
- **Idle latency:** every tool reads within 2 ms of the base RTT. Firefox reports whole milliseconds.
- **Since the 18 October run (Graphite Meter 0.13.1):** Graphite Meter's download no longer reads above the payload
  rate (+0.4 % then at 100 Mbit/s), and its upload gap closed: at 1 Gbit/s it read 11.1 % (Firefox) and 1.8 % (Chrome)
  low then, 9.7 % behind nginx in Firefox and 7.2 % over HTTP/2. Its peak server memory fell from 21 to 23 MB to 8 MB and
  its Firefox CPU per GB from 5.0 to 2.9 s, where the other tools' fell 5 to 15 %. The other tools' medians moved by
  0.1 % (median, 90 % of cells within 1.0 %) on links without loss and by 1.8 % (90 % within 7.7 %) with loss or the
  160 ms path. At 10 Gbit/s and unshaped they moved by 13 % (median, up to 49 %, mostly up): those cells follow the
  runner CPUs, and this run had more of the faster EPYC 9V45 and 9V74, so compare them only within a run.
- **Reproducibility:** the 18 October run and a second complete run four hours later on a different mix of runner
  CPUs ([run 39181262815](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/39181262815), Graphite
  Meter 0.13.2, everything else identical, raw data in
  [`results/2026-10-19-ci-run-39181262815`](results/2026-10-19-ci-run-39181262815)) matched the other tools' medians
  within 0.1 % (median difference, at most 3.0 %) on links without loss, within 0.8 % (at most 3.6 %) at 10 Gbit/s
  and unshaped, and within 1.2 % (at most 25 %) with loss or the 160 ms path.

### 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.5 [95.4, 95.5] | -0.2 % | 20.4 (20.1) | 20.5 (n/a) | 20.4 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 95.7 [95.6, 95.8] | +0.0 % | 95.7 [95.6, 95.7] | +0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.3 [95.2, 95.5] | -0.3 % | 21.0 (20.1) | 23.0 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.7 [95.6, 95.7] | +0.0 % | 95.6 [95.5, 95.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.3 [95.2, 95.3] | -0.4 % | 96.5 [95.9, 97.4] | +0.9 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.7 [94.6, 94.8] | -1.0 % | 92.9 [91.9, 93.5] | -2.8 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.7 [95.6, 95.9] | +0.1 % | 95.3 [94.7, 95.9] | -0.4 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.3 [95.2, 95.3] | -0.4 % | 95.3 [94.6, 95.8] | -0.3 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.6 [95.5, 95.7] | -0.0 % | 95.2 [94.7, 95.7] | -0.5 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.3, 95.5] | -0.4 % | 95.3 [94.5, 96.0] | -0.4 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.5 [95.4, 95.6] | -0.1 % | 95.3 [94.6, 95.9] | -0.4 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 96.0 [95.1, 96.5] | +0.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.7 [95.4, 95.9] | +0.1 % | 96.3 [96.0, 96.9] | +0.7 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 956.0 [955.3, 956.2] | -0.0 % | 952.5 [950.6, 953.7] | -0.4 % | 20.4 (20.1) | 21.2 (n/a) | 20.7 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 956.5 [956.4, 956.9] | +0.0 % | 956.4 [955.7, 956.7] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 954.9 [952.5, 956.7] | -0.2 % | 953.5 [947.3, 954.9] | -0.3 % | 21.0 (20.1) | 35.3 (n/a) | 21.0 (n/a) |
| Graphite Meter, HTTP/2, chrome | 30/30 | payload | 950.7 [950.4, 950.9] | -0.6 % | 939.5 [933.0, 942.3] | -1.8 % | 20.4 (20.1) | 21.4 (n/a) | 23.3 (n/a) |
| Graphite Meter, HTTP/3, chrome | 30/30 | payload | 942.5 [939.9, 953.1] | -1.5 % | 138.9 [135.2, 140.9] | -85.5 % | 20.4 (20.1) | 20.6 (n/a) | 20.4 (n/a) |
| Graphite Meter, WebTransport, chrome | 30/30 | payload | 947.8 [938.1, 954.5] | -0.9 % | 668.5 [564.7, 780.6] | -30.1 % | 20.5 (20.1) | 20.6 (n/a) | 22.4 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.3 [956.0, 956.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 956.0 [954.0, 958.8] | -0.0 % | 944.0 [936.5, 947.8] | -1.3 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 934.7 [931.1, 943.4] | -2.3 % | 846.0 [843.7, 867.1] | -11.5 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 938.0 [926.5, 951.8] | -1.9 % | 893.0 [878.3, 906.3] | -6.6 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 955.0 [954.0, 956.0] | -0.1 % | 949.0 [938.3, 954.0] | -0.8 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 943.5 [933.3, 952.8] | -1.3 % | 885.0 [878.3, 908.8] | -7.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 945.0 [940.8, 947.0] | -1.2 % | 414.0 [411.0, 416.8] | -56.7 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 956.0 [953.0, 958.0] | -0.0 % | 949.0 [939.8, 952.0] | -0.8 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 937.0 [930.5, 950.0] | -2.0 % | 890.5 [873.0, 899.0] | -6.9 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 951.3 [950.0, 952.0] | -0.5 % | 952.8 [947.5, 955.0] | -0.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 950.7 [948.4, 953.0] | -0.6 % | 949.4 [945.6, 952.7] | -0.7 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 950.0 [949.0, 952.3] | -0.7 % | 938.5 [925.8, 943.2] | -1.9 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. On 4-vCPU runners the browser (two vCPUs) is usually the limit here, so a low reading shows how much of the link a tool can drive on that hardware, not a counting error. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 9560.6 [9548.6, 9562.9] | -0.0 % | 3826.7 [2746.2, 5001.5] | -60.0 % | 2.2 (2.1) | 2.9 (n/a) | 3.8 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.2 (n/a) | 2.1 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 3404.4 [2789.8, 4178.2] | -64.4 % | 5388.6 [3882.9, 6334.4] | -43.7 % | 3.0 (2.1) | 22.5 (n/a) | 63.3 (n/a) |
| Graphite Meter, HTTP/2, chrome | 30/30 | payload | 4377.7 [3898.1, 6329.0] | -54.2 % | 2639.9 [1811.4, 3722.0] | -72.4 % | 2.2 (2.1) | 2.9 (n/a) | 3.3 (n/a) |
| Graphite Meter, HTTP/3, chrome | 30/30 | payload | 1814.4 [1384.4, 2488.8] | -81.0 % | 767.4 [679.5, 877.7] | -92.0 % | 2.2 (2.1) | 2.5 (n/a) | 5.7 (n/a) |
| Graphite Meter, WebTransport, chrome | 30/30 | payload | 1862.8 [1397.6, 2572.5] | -80.5 % | 728.3 [651.6, 833.4] | -92.4 % | 2.3 (2.1) | 2.7 (n/a) | 4.6 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.2 [9564.1, 9564.3] | +0.0 % | 9564.3 [9564.2, 9564.4] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 9166.0 [8182.0, 9479.5] | -4.2 % | 3174.0 [2145.8, 3784.5] | -66.8 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9355.9 [9354.8, 9357.0] | -2.2 % | 7651.2 [7510.9, 8133.6] | -20.0 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 2613.0 [1980.8, 3224.0] | -72.7 % | 3004.0 [2415.5, 3322.8] | -68.6 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 9223.0 [8237.0, 9467.8] | -3.6 % | 3184.5 [2132.0, 3881.3] | -66.7 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 2605.5 [1915.5, 3279.0] | -72.8 % | 3032.0 [2430.8, 3549.5] | -68.3 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 3928.5 [3494.3, 4263.0] | -58.9 % | 2460.5 [1685.0, 3061.0] | -74.3 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 9079.0 [8108.5, 9453.0] | -5.1 % | 3163.5 [2147.8, 3653.3] | -66.9 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 2620.0 [1909.5, 3283.0] | -72.6 % | 2988.0 [2438.3, 3484.0] | -68.8 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 8694.6 [7590.7, 9555.4] | -9.1 % | 3284.8 [2267.8, 3811.9] | -65.7 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 2834.0 [2230.6, 3875.5] | -70.4 % | 2956.3 [2668.7, 3400.0] | -69.1 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 4264.9 [3348.2, 5866.7] | -55.4 % | 2446.3 [1685.3, 3441.3] | -74.4 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |

### 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Error is against the quantity each tool says it reports. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.4 (20.1) | 186.2 (179.6) | 184.1 (183.0) |
| Graphite Meter terminal client | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.2 (20.1) | 179.5 (173.6) | 199.0 (192.5) |
| Graphite Meter, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 21.0 (20.1) | 190.5 (179.7) | 185.0 (180.5) |
| iperf3 (reference) | 30/30 | payload | 286.9 [286.9, 287.0] | -0.0 % | 28.6 [28.6, 28.7] | -0.3 % | n/a (20.1) | n/a (175.4) | n/a (191.9) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [285.0, 287.0] | -0.3 % | 29.6 [29.2, 30.0] | +3.3 % | 20.3 (20.1) | n/a (156.7) | n/a (185.8) |
| LibreSpeed CLI | 30/30 | payload | 282.4 [280.5, 283.3] | -1.6 % | 29.0 [29.0, 29.0] | +1.2 % | 20.2 (20.1) | n/a (174.8) | n/a (175.4) |
| LibreSpeed, firefox | 30/30 | payload | 286.0 [284.0, 287.0] | -0.3 % | 29.1 [28.7, 29.3] | +1.4 % | 22.0 (20.1) | n/a (158.6) | n/a (185.8) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 286.0 [285.3, 287.0] | -0.3 % | 28.9 [28.3, 29.7] | +0.5 % | 20.1 (20.1) | n/a (157.2) | n/a (169.8) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 286.0 [283.3, 287.0] | -0.3 % | 29.3 [28.7, 29.6] | +1.9 % | 21.0 (20.1) | n/a (159.2) | n/a (186.1) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 28.6 [28.2, 29.2] | -0.3 % | 20.1 (20.1) | n/a (151.6) | n/a (171.1) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 286.0 [285.0, 287.0] | -0.3 % | 29.1 [28.6, 29.4] | +1.6 % | 21.0 (20.1) | n/a (152.8) | n/a (186.7) |
| OpenSpeedTest, chrome | 30/30 | payload | 286.3 [285.6, 287.2] | -0.2 % | 31.4 [30.2, 31.8] | +9.4 % | 21.0 (20.1) | n/a (158.4) | n/a (197.5) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.5 [285.7, 287.1] | -0.1 % | 31.1 [30.1, 31.6] | +8.6 % | 21.0 (20.1) | n/a (162.4) | n/a (196.6) |

### 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 13.0 [12.5, 13.5] | n/a | 13.2 [12.8, 13.7] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 19.9 [19.4, 20.3] | n/a | 19.8 [19.1, 20.4] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 13.0 [12.7, 13.8] | n/a | 13.9 [13.5, 15.1] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 13.0 [12.6, 13.3] | n/a | 12.8 [12.4, 13.1] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 16.8 [16.1, 17.3] | n/a | 9.7 [9.1, 9.9] | n/a | 40.4 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 11.6 [10.9, 11.9] | n/a | 12.1 [11.3, 12.8] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 21.1 [20.1, 22.1] | n/a | 9.3 [9.0, 10.0] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 16.7 [16.0, 17.1] | n/a | 9.5 [9.1, 10.0] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 21.4 [20.5, 22.1] | n/a | 9.2 [8.9, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 16.6 [15.9, 17.0] | n/a | 9.6 [9.1, 9.8] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 20.5 [19.6, 21.8] | n/a | 9.6 [9.1, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 19.0 [18.7, 20.2] | n/a | 22.0 [20.9, 23.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.4 [18.7, 19.9] | n/a | 21.9 [21.2, 22.8] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

### 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 59.2 [54.9, 63.5] | n/a | 67.9 [62.9, 72.8] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 89.5 [84.2, 94.7] | n/a | 88.7 [82.6, 93.4] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 60.5 [54.1, 66.6] | n/a | 70.7 [62.8, 76.2] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter, HTTP/2, chrome | 30/30 | payload | 15.6 [11.7, 18.9] | n/a | 14.2 [11.9, 17.7] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter, HTTP/3, chrome | 30/30 | payload | 92.7 [80.6, 113.3] | n/a | 19.0 [17.5, 28.1] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter, WebTransport, chrome | 30/30 | payload | 78.0 [67.7, 116.7] | n/a | 30.0 [27.9, 35.2] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.4 (n/a) |
| iperf3 (reference) | 30/30 | payload | 49.5 [48.4, 51.7] | n/a | 51.4 [49.3, 54.1] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 100.0 [92.0, 105.5] | n/a | 37.0 [32.8, 41.2] | n/a | 40.4 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 51.7 [45.8, 61.1] | n/a | 47.3 [43.5, 50.5] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 125.5 [112.5, 149.5] | n/a | 36.9 [34.5, 41.6] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 105.0 [90.1, 115.3] | n/a | 62.8 [47.5, 84.5] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 133.0 [118.8, 161.3] | n/a | 36.6 [33.4, 39.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 13.3 [10.8, 14.7] | n/a | 12.0 [10.7, 13.9] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 96.9 [87.8, 127.0] | n/a | 54.8 [47.2, 59.3] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 132.0 [121.3, 149.5] | n/a | 36.1 [32.7, 42.0] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 76.1 [73.5, 84.5] | n/a | 91.0 [85.3, 99.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 76.5 [72.3, 81.3] | n/a | 89.8 [84.1, 95.9] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 11.6 [10.4, 12.8] | n/a | 14.1 [11.2, 17.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

### 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 266.4 [259.5, 277.6] | n/a | 232.5 [224.6, 237.9] | n/a | 160.5 (160.2) | 160.5 (n/a) | 160.4 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 279.2 [273.3, 282.4] | n/a | 282.5 [277.4, 285.5] | n/a | 160.0 (160.2) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 273.8 [265.1, 282.4] | n/a | 226.5 [221.6, 236.6] | n/a | 161.0 (160.2) | 163.0 (n/a) | 161.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 235.0 [217.5, 260.6] | n/a | 255.3 [220.1, 269.0] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 253.5 [246.3, 271.8] | n/a | 236.0 [229.0, 240.0] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 216.6 [205.9, 221.5] | n/a | 117.2 [114.9, 123.0] | n/a | 160.2 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 251.5 [243.0, 272.8] | n/a | 227.0 [219.0, 231.0] | n/a | 162.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 247.5 [243.3, 271.8] | n/a | 230.0 [219.0, 240.8] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 249.5 [240.5, 273.3] | n/a | 225.5 [223.3, 231.5] | n/a | 162.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 247.5 [242.0, 269.0] | n/a | 236.5 [224.5, 239.5] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 251.5 [244.0, 270.5] | n/a | 225.0 [215.8, 237.8] | n/a | 162.0 (160.2) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 273.6 [267.7, 277.0] | n/a | 271.7 [266.6, 276.7] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 271.8 [269.6, 276.0] | n/a | 271.6 [269.6, 274.2] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |

### 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 74.9 [74.9, 75.0] | n/a | 75.4 [75.3, 75.4] | n/a | 20.5 (20.1) | 20.5 (n/a) | 20.4 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 80.3 [80.3, 80.4] | n/a | 80.8 [80.8, 80.8] | n/a | 20.2 (20.1) | 20.3 (n/a) | 20.2 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 74.9 [74.8, 75.0] | n/a | 75.2 [75.2, 75.3] | n/a | 21.0 (20.1) | 22.5 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 75.0 [74.8, 75.1] | n/a | 75.2 [75.1, 75.3] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.8 [77.7, 78.0] | n/a | 70.5 [69.8, 71.4] | n/a | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.3 [69.3, 69.4] | n/a | 68.8 [68.8, 69.2] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.3 [80.2, 80.4] | n/a | 70.1 [69.7, 70.6] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.8 [77.8, 77.8] | n/a | 72.5 [71.7, 73.1] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 80.3 [80.2, 80.4] | n/a | 70.3 [69.8, 70.9] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.8 [77.7, 77.9] | n/a | 71.9 [71.3, 72.7] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.3 [80.1, 80.5] | n/a | 70.8 [70.0, 71.3] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.2 [80.1, 80.2] | n/a | 80.6 [80.2, 81.6] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.2 [80.1, 80.4] | n/a | 80.7 [80.2, 81.8] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 956.0 [955.5, 956.3] | -0.0 % | 953.9 [951.8, 954.8] | -0.3 % | 20.4 (20.1) | 21.4 (n/a) | 23.4 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 955.1 [953.4, 955.8] | -0.1 % | 955.3 [953.1, 956.2] | -0.1 % | 21.0 (20.1) | 34.0 (n/a) | 24.5 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.3, 956.5] | +0.0 % | 956.3 [956.0, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 953.0 [942.5, 955.0] | -0.4 % | 876.5 [843.8, 891.0] | -8.4 % | 20.6 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 927.5 [896.3, 947.8] | -3.0 % | 825.5 [800.5, 847.0] | -13.7 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 951.3 [949.2, 951.9] | -0.5 % | 920.5 [910.3, 923.8] | -3.8 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 951.1 [947.4, 953.2] | -0.5 % | 908.5 [900.0, 915.0] | -5.0 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

### Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | payload | 382.5 [382.5, 382.5] | -0.0 % | 381.5 [381.0, 381.7] | -0.3 % | 20.4 (20.1) | 20.8 (n/a) | 20.4 (n/a) |
| Graphite Meter terminal client | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.7 [382.5, 382.9] | +0.0 % | 20.2 (20.1) | 20.4 (n/a) | 20.2 (n/a) |
| Graphite Meter, firefox | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.4 [381.0, 381.7] | -0.3 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.6 [382.5, 382.6] | +0.0 % | 382.6 [382.5, 382.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

### Unshaped, offloads on: as fast as the host allows

No shaping: the host's CPU is the limit, so rates show how far each tool gets on it, not a network's capacity. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 30/30 | 13122.2 [11652.0, 19368.0] | 4956.5 [3348.2, 6260.1] | 0.30 | 8 | 2.01 |
| Graphite Meter terminal client | 30/30 | 25660.0 [21652.5, 49200.0] | 64230.0 [59625.0, 69050.0] | 0.19 | 13 | n/a |
| Graphite Meter, firefox | 30/30 | 3649.4 [2975.9, 4584.6] | 6169.5 [4556.0, 7655.8] | 0.27 | 8 | 2.88 |
| iperf3 (reference) | 30/30 | 30675.4 [28369.9, 42079.6] | 44335.2 [43887.6, 71142.3] | 0.20 | 10 | n/a |
| LibreSpeed, chrome | 30/30 | 10046.5 [8524.8, 11853.3] | 4199.0 [2713.5, 5033.3] | 0.32 | 82 | 2.16 |
| LibreSpeed CLI | 30/30 | 33611.1 [27700.1, 43209.1] | 16829.4 [15696.6, 21788.1] | 0.28 | 76 | n/a |
| LibreSpeed, firefox | 30/30 | 2581.0 [1878.3, 3340.0] | 3257.0 [2596.3, 3766.0] | 0.33 | 87 | 5.61 |
| LibreSpeed Go backend, chrome | 30/30 | 9953.0 [8306.5, 12469.3] | 4194.5 [2691.0, 5020.5] | 0.34 | 50 | 2.15 |
| LibreSpeed Go backend, firefox | 30/30 | 2625.5 [1958.5, 3337.0] | 3251.0 [2600.0, 3940.0] | 0.32 | 54 | 5.72 |
| LibreSpeed Rust backend, chrome | 30/30 | 9827.5 [8510.5, 11664.5] | 4096.5 [2662.3, 4870.3] | 0.25 | 21 | 2.22 |
| LibreSpeed Rust backend, firefox | 30/30 | 2628.0 [1960.0, 3293.0] | 3282.0 [2532.8, 3587.3] | 0.25 | 25 | 5.75 |
| OpenSpeedTest, chrome | 30/30 | 8997.0 [7695.2, 10436.3] | 4313.8 [2820.5, 5009.3] | 0.21 | 21 | 2.25 |
| OpenSpeedTest, firefox | 30/30 | 2685.3 [2180.1, 3575.4] | 3219.4 [2609.2, 3720.6] | 0.26 | 18 | 5.52 |

Raw data: [`results/2026-10-22-ci-run-39772524145`](results/2026-10-22-ci-run-39772524145), one JSON per run and each
job's manifest (pins, host, CPU sets, block order, noise checks). Screenshots of every run's final screen are in the
run's artifacts. Earlier runs are kept in `results/` with their manifests, among them the 18 October run with Graphite
Meter 0.13.1 ([`results/2026-10-18-ci-run-39163069945`](results/2026-10-18-ci-run-39163069945)).

## Results: desktop, night of 18 to 19 October 2026

A second dataset from an AMD Ryzen 7 7800X3D desktop (8 cores, 16 threads, kernel 7.2.10-1-cachyos, rootless Podman),
with the browser on three cores instead of the runners' two vCPUs, the same tools and versions as the 18 October
runner run (Graphite Meter 0.13.1, Chrome 155, Firefox 158.0), and the 25 and 40 Gbit/s scenarios: 6 runs per tool,
browser and scenario, 1,074 runs, all complete. Full tables and setup:
[`results/2026-10-18-desktop-7800x3d`](results/2026-10-18-desktop-7800x3d). With 6 runs per cell, differences of
about 2 % or less are within its noise.

This kernel's TCP recovers from random loss far better than the runners' (iperf3 reaches 94 Mbit/s at 1 % loss here
and 13 there, with the same netem loss and CUBIC on both), so its loss, long-path and deep-buffer numbers compare only
within that dataset.

- **10 Gbit/s with three browser cores:** over HTTP/1.1, Chrome reaches the link in both directions with every tool
  (9.55 to 9.60 Gbit/s). In Firefox, Graphite Meter downloads at 9.60 Gbit/s and uploads at 7.8; the LibreSpeed
  backends reach 8.4 to 9.2 down and 8.2 to 8.5 up; OpenSpeedTest 7.1 down and 9.5 up.
- **25 Gbit/s:** Graphite Meter's client fills the link (23.91 Gbit/s both ways; iperf3 23.90 and 23.45). Chrome
  downloads reach it with every tool; Chrome uploads stop at 12.9 Gbit/s with Graphite Meter and 11.1 to 11.4 with the
  others. In Firefox, Graphite Meter reaches 17.7 Gbit/s down and the others 8.3 to 10.4.
- **40 Gbit/s:** only Graphite Meter's client fills the link (38.26 Gbit/s both ways; iperf3 37.8 and 37.5). In
  Chrome, Graphite Meter downloads at 33.6 Gbit/s and the others at 24.2 to 24.7; uploads stop at 12.7 and 11.1 to
  11.3.
- **Unshaped:** Chrome downloads reach 39.0 Gbit/s with Graphite Meter and 24.1 to 24.5 with the others, uploads 15.1
  and 13.9 to 14.1. Graphite Meter's client moves 185 Gbit/s down and 242 up, iperf3 172 and 207. Server CPU per GB:
  0.11 to 0.14 s for Graphite Meter, OpenSpeedTest and the Rust backend, 0.15 to 0.18 s for LibreSpeed's Go and PHP
  backends.
- **Upload on plain links:** Graphite Meter 0.13.1's Firefox upload at 1 Gbit/s reads 3.2 % low here against 11.1 % on
  the 18 October runners, so that gap depended strongly on the host. OpenSpeedTest's upload reads above the payload
  rate here: 1.7 to 4.5 % at 100 Mbit/s and 2.0 to 2.6 % at 1 Gbit/s.
- **Behind a 200 ms FIFO:** Graphite Meter's upload again reads within 0.3 %, and its loaded latency lands within 6 ms
  of the queue reference. OpenSpeedTest's upload reads 7.0 % (Chrome) and 27 % (Firefox) above the payload rate.
- **Behind nginx:** OpenSpeedTest's upload reads 10.0 % (Chrome) and 11.6 % (Firefox) low, LibreSpeed's 3.6 % and 10.6
  %, Graphite Meter's 2.2 % and 1.6 %.

## Run it

Needs Linux with cgroup v2, Podman, Node 22 or later, `nsenter`, `ethtool`, `curl`, `unzip` and `xz`. Rootless Podman
works; set `SB_ROOTFUL=1` to use `sudo podman` instead. Several instances can share a machine: `SB_PREFIX` names their
containers and `SB_CPUSETS` (for example `{"shaper":"6","server":"14","client":"7,15"}`) gives each its own cores.
`SB_PIN_OVERRIDES` swaps pins for a local experiment, such as a locally built image (`localhost/...`) of a fix branch;
the run's manifest records what ran.

```sh
node bench/run.js --scenarios accuracy-100 --reps 1
node bench/summarize.js results/local-*
node bench/phases.js results/local-*
```

Published numbers come from the [Bench workflow](.github/workflows/bench.yml) on GitHub-hosted runners, where every
log is public, and from full campaigns on a named local machine, whose raw data and manifests are committed the same
way. Shorter local runs are for development.
