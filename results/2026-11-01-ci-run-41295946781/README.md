# GitHub runner benchmark, 2026-11-01

**4,530/4,530** retained runs completed across **15 runner jobs** (0 runs excluded by the busy-host rule).
The 25 and 40 Gbit/s shaped scenarios are skipped on these 4-vCPU runners. They require 8+ CPUs.

[Benchmark source at a74c21332d1eede5090432b4fd6bf8518338c47f](https://github.com/zR-JB/selfhosted-speedtest-bench/tree/a74c21332d1eede5090432b4fd6bf8518338c47f) · [Workflow run and raw artifacts](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/41295946781)
[Provenance and exact pins](provenance.json) · [Retained scalar measurements](measurements.json.gz) · [Server CPU by phase](server-cpu.md) · [Bench overview](../../README.md) · [Previous report](../2026-10-22-ci-run-39772524145)

The workflow stores the detailed artifacts and screenshots for its retention window. The scalar archive
keeps the inputs used by the overview charts and tables. Read it with `gzip -dc measurements.json.gz`.
Provenance records the job order, CPU allocation, pinned releases and workload definitions.

To regenerate the overview tables and charts from the committed archive, run
`python3 bench/report.py 41295946781 --from-archive --rerender` from the repository root.
The renderer uses Python 3 with Matplotlib. When this is the latest run, the command also updates
the root README. Regenerating the detailed pass tables requires all 15 job artifacts, Node.js 22 or later,
and the benchmark source revision in local Git history. Use
`python3 bench/report.py 41295946781 /path/to/artifacts --rerender` while they remain available.

| Tested release | Version |
| --- | ---: |
| Graphite Meter Browser | 0.13.4 |
| LibreSpeed | 6.3.1 |
| LibreSpeed Go backend | 1.1.6 |
| LibreSpeed Rust backend | 1.4.0 |
| OpenSpeedTest | 2.5.4 |
| Graphite Meter Terminal | 0.13.4 |
| LibreSpeed CLI | 1.0.14 |
| Chrome | 156.0.8078.47 |
| Firefox | 158.0.1 |

## Overview data

We take each VM’s median over its retained passes, then summarize across VMs. A VM contributes once,
with up to two passes. Large marks show medians across VMs. Lines span the middle 50%, and small
marks show VM values where plotted. The spreads describe these runners. Sample sizes and exact
values are in the linked tables.

### Shaped throughput

Download / upload medians. Browser rows use Chrome. The loss test uses a 100 Mbit/s link, 1% loss in each direction and 40 ms RTT.

| Tool or client | 1 Gbit/s (Mbit/s) | 10 Gbit/s (Gbit/s) | 1% loss (Mbit/s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser | 956.0 / 953.1 | 9.56 / 4.25 | 13.2 / 14.3 |
| LibreSpeed | 957.0 / 945.0 | 9.27 / 3.25 | 16.8 / 9.6 |
| LibreSpeed Go backend | 955.0 / 950.0 | 9.34 / 3.23 | 16.8 / 9.6 |
| LibreSpeed Rust backend | 955.5 / 948.5 | 9.23 / 3.19 | 16.6 / 9.5 |
| OpenSpeedTest | 951.8 / 953.0 | 9.32 / 3.38 | 19.2 / 22.6 |
| Graphite Meter Terminal | 956.4 / 956.3 | 9.56 / 9.56 | 19.6 / 19.4 |
| LibreSpeed CLI | 943.7 / 869.9 | 9.36 / 8.10 | 11.5 / 11.8 |
| iperf3 (reference) | 956.4 / 956.1 | 9.56 / 9.56 | 12.9 / 12.9 |

### 10 Gbit/s upload spread

Each cell shows the median [25th, 75th percentile] and number of VMs. The last column uses matched same-VM, same-pass iperf3 rates. A lower achieved rate can come from any part of the test setup.

Graphite Meter Browser’s same-pass upload difference from OpenSpeedTest in Chrome was **+0.84 Gbit/s** (middle 50% +0.39 to +1.14). Graphite Meter Browser reported more on **15/15 matched VMs**.

| Tool or client | Upload (Gbit/s) | Paired difference from iperf3 (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 4.25 [2.74, 5.45] (n=15) | -55.6 [-71.3, -43.1] (n=15) |
| LibreSpeed · Chrome | 3.25 [2.25, 4.14] (n=15) | -66.0 [-76.5, -56.7] (n=15) |
| LibreSpeed Go backend · Chrome | 3.23 [2.25, 4.13] (n=15) | -66.2 [-76.5, -56.8] (n=15) |
| LibreSpeed Rust backend · Chrome | 3.19 [2.23, 4.03] (n=15) | -66.6 [-76.7, -57.8] (n=15) |
| OpenSpeedTest · Chrome | 3.38 [2.35, 4.19] (n=15) | -64.6 [-75.4, -56.2] (n=15) |
| Graphite Meter Browser · Firefox | 5.51 [4.00, 6.96] (n=15) | -42.3 [-58.2, -27.2] (n=15) |
| LibreSpeed · Firefox | 3.11 [2.49, 3.85] (n=15) | -67.5 [-74.0, -59.8] (n=15) |
| LibreSpeed Go backend · Firefox | 3.14 [2.49, 3.83] (n=15) | -67.1 [-74.0, -59.9] (n=15) |
| LibreSpeed Rust backend · Firefox | 3.08 [2.48, 3.78] (n=15) | -67.8 [-74.1, -60.5] (n=15) |
| OpenSpeedTest · Firefox | 3.01 [2.56, 3.76] (n=15) | -68.5 [-73.3, -60.7] (n=15) |
| Graphite Meter Terminal | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | 8.10 [7.63, 8.58] (n=15) | -15.3 [-20.2, -10.3] (n=15) |
| iperf3 (reference) | 9.56 [9.56, 9.56] (n=15) | — |

### Matched 1 Gbit/s agreement

Signed percentage differences from iperf3 on the same VM and pass. Each cell shows the median [25th, 75th percentile] and number of VMs after reducing the matched pass differences within each VM. Tests ran sequentially. App and iperf3 start times were a median of 2.7 minutes apart (maximum 8.9).

| Tool or client | Download difference (%) | Upload difference (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.0 [-0.1, 0.0] (n=15) | -0.3 [-0.7, -0.1] (n=15) |
| LibreSpeed · Chrome | 0.0 [-0.2, +0.1] (n=15) | -1.1 [-1.3, -0.9] (n=15) |
| LibreSpeed Go backend · Chrome | -0.1 [-0.2, 0.0] (n=15) | -0.7 [-0.9, -0.2] (n=15) |
| LibreSpeed Rust backend · Chrome | -0.1 [-0.3, 0.0] (n=15) | -0.8 [-1.2, -0.3] (n=15) |
| OpenSpeedTest · Chrome | -0.5 [-0.6, -0.4] (n=15) | -0.2 [-0.5, -0.1] (n=15) |
| Graphite Meter Browser · Firefox | 0.0 [-0.1, 0.0] (n=15) | -0.5 [-0.7, -0.2] (n=15) |
| LibreSpeed · Firefox | -3.4 [-5.6, -1.8] (n=15) | -7.6 [-8.6, -5.5] (n=15) |
| LibreSpeed Go backend · Firefox | -2.6 [-5.7, -1.8] (n=15) | -7.2 [-8.8, -5.2] (n=15) |
| LibreSpeed Rust backend · Firefox | -3.9 [-4.7, -2.4] (n=15) | -6.2 [-7.6, -5.5] (n=15) |
| OpenSpeedTest · Firefox | -0.6 [-0.7, -0.3] (n=15) | -0.7 [-0.9, -0.5] (n=15) |
| Graphite Meter Terminal | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | -1.3 [-1.4, -1.3] (n=15) | -9.0 [-9.1, -8.9] (n=15) |

### Unshaped throughput and browser CPU

Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand.
Each maximum is the fastest retained pass in that direction. The two maxima can come from different passes. Browser CPU measures the client process tree over the full run per GB at the shaper.

| Tool or client | Median down / up (Gbit/s) | Max down / up (Gbit/s) | Browser CPU (s/GB) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 18.0 / 5.1 | 23.5 / 11.8 | 1.59 |
| LibreSpeed · Chrome | 10.4 / 4.2 | 16.2 / 10.9 | 2.07 |
| LibreSpeed Go backend · Chrome | 10.3 / 4.2 | 16.6 / 11.0 | 2.06 |
| LibreSpeed Rust backend · Chrome | 10.4 / 4.0 | 16.1 / 11.3 | 2.13 |
| OpenSpeedTest · Chrome | 9.6 / 4.2 | 14.9 / 11.5 | 2.15 |
| Graphite Meter Browser · Firefox | 3.9 / 6.2 | 6.0 / 16.8 | 2.84 |
| LibreSpeed · Firefox | 2.3 / 3.3 | 3.4 / 5.2 | 5.69 |
| LibreSpeed Go backend · Firefox | 2.2 / 3.3 | 3.5 / 4.9 | 5.79 |
| LibreSpeed Rust backend · Firefox | 2.1 / 3.3 | 3.4 / 5.0 | 5.74 |
| OpenSpeedTest · Firefox | 2.7 / 3.2 | 5.8 / 5.0 | 5.62 |
| Graphite Meter Terminal | 26.3 / 64.2 | 61.8 / 108.4 | — |
| LibreSpeed CLI | 28.0 / 18.5 | 54.1 / 28.9 | — |
| iperf3 (reference) | 31.0 / 44.0 | 62.5 / 98.2 | — |

#### Unshaped native upload by runner hardware

Upload medians in Gbit/s. “GM above iperf3” counts VMs after matching same-pass comparisons. CPU, kernel and runner conditions vary together. Groups with one VM show that VM’s median.

Graphite Meter Terminal had a higher upload rate than iperf3 on **14 of 15 VMs** after matching passes. The split was 0/1 on AWS-kernel VMs, 14/14 on Azure-kernel VMs.

| CPU and kernel | VMs | Graphite Meter Terminal | LibreSpeed CLI | iperf3 | GM above iperf3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| AMD EPYC 7763 64-Core Processor (7.0.0-1017-azure) | 5 | 57.2 | 16.0 | 42.1 | 5/5 |
| AMD EPYC 9V45 96-Core Processor (7.0.0-1017-azure) | 5 | 104.0 | 26.9 | 76.4 | 5/5 |
| AMD EPYC 9V74 80-Core Processor (7.0.0-1017-azure) | 3 | 64.2 | 17.9 | 42.7 | 3/3 |
| INTEL(R) XEON(R) PLATINUM 8573C (7.0.0-1017-azure) | 1 | 73.6 | 24.9 | 59.7 | 1/1 |
| Intel(R) Xeon(R) 6975P-C (7.0.0-1014-aws) | 1 | 48.9 | 27.5 | 96.0 | 0/1 |

### Server resources at 1 Gbit/s

Server CPU is container CPU time per decimal GB of server-interface traffic during each phase,
counting bytes in both directions. Peak memory is the container’s per-run peak in decimal MB.
The adjacent reported rates show how much of the same shaped link each setup used. Browser CPU is
measured separately on the client. Native client CPU is unavailable.

| Tool or client | Down / up (Mbit/s) | Down CPU (s/GB) | Up CPU (s/GB) | Peak RAM (MB) |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 956.0 / 953.1 | 0.300 | 3.932 | 15.2 |
| LibreSpeed · Chrome | 957.0 / 945.0 | 0.361 | 5.878 | 80.2 |
| LibreSpeed Go backend · Chrome | 955.0 / 950.0 | 0.378 | 5.961 | 48.1 |
| LibreSpeed Rust backend · Chrome | 955.5 / 948.5 | 0.314 | 4.025 | 22.7 |
| OpenSpeedTest · Chrome | 951.8 / 953.0 | 0.189 | 3.704 | 29.1 |
| Graphite Meter Terminal | 956.4 / 956.3 | 0.207 | 7.104 | 17.1 |
| LibreSpeed CLI | 943.7 / 869.9 | 0.264 | 2.675 | 68.4 |
| iperf3 (reference) | 956.4 / 956.1 | 0.234 | 7.122 | 19.2 |
| Graphite Meter Browser · Firefox | 956.2 / 950.4 | 0.343 | 5.233 | 15.0 |
| LibreSpeed · Firefox | 924.0 / 884.0 | 0.470 | 5.189 | 85.5 |
| LibreSpeed Go backend · Firefox | 931.5 / 887.0 | 0.422 | 5.301 | 52.0 |
| LibreSpeed Rust backend · Firefox | 919.0 / 896.5 | 0.376 | 3.730 | 26.3 |
| OpenSpeedTest · Firefox | 950.8 / 949.0 | 0.223 | 3.957 | 29.2 |

Absolute server CPU time for the complete 1 Gbit/s test and each transfer phase.

| Tool or client | Download (CPU s) | Upload (CPU s) | Test total (CPU s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.28 | 3.52 | 3.79 |
| LibreSpeed · Chrome | 0.31 | 6.03 | 6.36 |
| LibreSpeed Go backend · Chrome | 0.32 | 6.16 | 6.47 |
| LibreSpeed Rust backend · Chrome | 0.27 | 4.07 | 4.48 |
| OpenSpeedTest · Chrome | 0.34 | 5.73 | 6.08 |
| Graphite Meter Terminal | 0.29 | 10.28 | 10.62 |
| LibreSpeed CLI | 0.52 | 4.81 | 5.31 |
| iperf3 (reference) | 0.36 | 10.72 | 11.02 |
| Graphite Meter Browser · Firefox | 0.37 | 4.79 | 5.19 |
| LibreSpeed · Firefox | 0.38 | 5.00 | 5.40 |
| LibreSpeed Go backend · Firefox | 0.35 | 5.08 | 5.52 |
| LibreSpeed Rust backend · Firefox | 0.31 | 3.55 | 3.89 |
| OpenSpeedTest · Firefox | 0.41 | 5.87 | 6.41 |

### Upload counter checks

All rates are in Mbit/s. The shaper reports the median over busy intervals, includes protocol
overhead and can show rates above the configured limit even for iperf3. “Above iperf3” counts passes
where the tool reported a higher rate than the same-VM, same-pass iperf3 receiver. Each VM runs
its two passes sequentially. The separate receiver smoke used the 1 Gbit/s path only.
This run predates passive server-interface timing. A payload accounting check would require
receiver payload bytes over the app’s reporting window.

**1 Gbit/s path**

| Tool or client | App rate | Shaper | Above iperf3 |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 953.1 | 969.1 | 4/30 |
| LibreSpeed · Chrome | 945.0 | 968.6 | 0/30 |
| LibreSpeed Go backend · Chrome | 950.0 | 964.6 | 8/30 |
| LibreSpeed Rust backend · Chrome | 948.5 | 965.7 | 5/30 |
| OpenSpeedTest · Chrome | 953.0 | 970.9 | 9/30 |
| Graphite Meter Browser · Firefox | 950.4 | 965.7 | 2/30 |
| LibreSpeed · Firefox | 884.0 | 958.6 | 0/30 |
| LibreSpeed Go backend · Firefox | 887.0 | 957.8 | 0/30 |
| LibreSpeed Rust backend · Firefox | 896.5 | 957.8 | 0/30 |
| OpenSpeedTest · Firefox | 949.0 | 965.8 | 2/30 |
| Graphite Meter Terminal | 956.3 | 973.5 | 19/30 |
| LibreSpeed CLI | 869.9 | 960.6 | 0/30 |
| iperf3 (reference) | 956.1 | 970.7 | — |

**30 Mbit/s upload, deep FIFO**

| Tool or client | App rate | Shaper | Above iperf3 |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 28.7 | 31.1 | 17/30 |
| LibreSpeed · Chrome | 29.4 | 31.0 | 24/30 |
| LibreSpeed Go backend · Chrome | 28.9 | 31.1 | 22/30 |
| LibreSpeed Rust backend · Chrome | 28.9 | 31.1 | 15/30 |
| OpenSpeedTest · Chrome | 31.1 | 31.0 | 29/30 |
| Graphite Meter Browser · Firefox | 28.7 | 31.1 | 18/30 |
| LibreSpeed · Firefox | 29.2 | 31.0 | 24/30 |
| LibreSpeed Go backend · Firefox | 29.3 | 31.0 | 26/30 |
| LibreSpeed Rust backend · Firefox | 29.2 | 31.0 | 24/30 |
| OpenSpeedTest · Firefox | 30.8 | 31.1 | 29/30 |
| Graphite Meter Terminal | 28.6 | 31.0 | 9/30 |
| LibreSpeed CLI | 29.3 | 31.0 | 28/30 |
| iperf3 (reference) | 28.7 | 31.0 | — |

### Idle latency against ICMP

The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference.
Each cell shows the median paired difference in ms [25th, 75th percentile] and number of VMs.

| Tool or client | 20 ms path | 40 ms path | 160 ms path |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | +0.2 [+0.2, +0.3] (n=15) | +0.3 [+0.2, +0.3] (n=15) | +0.3 [+0.3, +0.4] (n=15) |
| LibreSpeed · Chrome | +0.2 [+0.2, +0.2] (n=15) | +0.2 [+0.2, +0.2] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed Go backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed Rust backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| OpenSpeedTest · Chrome | +0.4 [+0.4, +0.9] (n=15) | +0.4 [+0.4, +0.8] (n=15) | +0.4 [+0.3, +0.8] (n=15) |
| Graphite Meter Browser · Firefox | +0.9 [+0.9, +0.9] (n=15) | +0.9 [+0.9, +1.0] (n=15) | +0.9 [+0.8, +0.9] (n=15) |
| LibreSpeed · Firefox | +1.4 [+0.9, +1.9] (n=15) | +1.4 [+1.1, +1.6] (n=15) | +1.4 [+1.3, +1.8] (n=15) |
| LibreSpeed Go backend · Firefox | +1.4 [+0.9, +1.4] (n=15) | +0.9 [+0.9, +1.4] (n=15) | +1.3 [+0.9, +1.4] (n=15) |
| LibreSpeed Rust backend · Firefox | +1.4 [+0.9, +1.4] (n=15) | +0.9 [+0.9, +1.3] (n=15) | +1.3 [+0.9, +1.4] (n=15) |
| OpenSpeedTest · Firefox | +0.4 [-0.1, +0.4] (n=15) | +0.4 [+0.3, +0.8] (n=15) | +0.8 [+0.4, +0.9] (n=15) |
| Graphite Meter Terminal | 0.0 [0.0, +0.1] (n=15) | 0.0 [0.0, +0.1] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed CLI | +0.1 [0.0, +0.1] (n=15) | +0.1 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) |

### Latency under load on a FIFO

Each cell shows the app’s reported latency followed by the queue-based estimate, in ms.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 179.6 / 174.3 | 183.0 / 181.0 |
| Graphite Meter Browser · Firefox | 186.0 / 175.2 | 181.2 / 178.8 |
| Graphite Meter Terminal | 176.0 / 169.2 | 199.5 / 193.8 |

Paired app minus queue estimate in ms, summarized within VMs, then across VMs.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | +6.3 [+4.7, +6.8] (n=15) | +3.2 [+2.8, +5.5] (n=15) |
| Graphite Meter Browser · Firefox | +8.2 [+6.4, +10.6] (n=15) | +2.4 [+2.0, +4.6] (n=15) |
| Graphite Meter Terminal | +6.7 [+5.3, +7.8] (n=15) | +5.7 [+4.9, +6.2] (n=15) |

## Pooled pass tables

The tables below pool all retained completed passes for each configuration, including alternate
transports. Their comparison columns show the difference from the modeled TCP payload ceiling
when iperf3 reaches at least 98% of the model in both directions. QUIC rows show measured rates separately.
The matched comparison above uses the measured same-pass receiver rate.
Below-ceiling rates can reflect any constraint on the end-to-end transfer.

[100 Mbit/s](#100100-mbits-20-ms-rtt-fq_codel) · [1 Gbit/s](#11-gbits-20-ms-rtt-fq_codel) · [10 Gbit/s](#1010-gbits-2-ms-rtt-fq_codel-offloads-on) · [Deep FIFO](#30030-mbits-20-ms-rtt-200-ms-fifo) · [1% loss](#100100-mbits-40-ms-rtt-1--loss-each-way-fq_codel) · [0.1% loss](#11-gbits-40-ms-rtt-01--loss-each-way-fq_codel) · [160 ms RTT](#300300-mbits-160-ms-rtt-fq_codel) · [Competing traffic](#100100-mbits-20-ms-rtt-fq_codel-one-competing-flow-each-way) · [Reverse proxy](#11-gbits-20-ms-rtt-fq_codel-behind-nginx) · [Two servers](#two-servers-200200-mbits-path-each-20-ms-rtt-fq_codel) · [Unshaped](#unshaped-offloads-on-as-fast-as-the-host-allows)

<!-- pooled-pass-tables -->
Jobs: 15. Runs: 4530, of which 0 left out from blocks on a busy host. Hosts: AMD EPYC 9V45 96-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 7763 64-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 9V74 80-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); Intel(R) Xeon(R) 6975P-C (4 CPUs, kernel 7.0.0-1014-aws, rootful); INTEL(R) XEON(R) PLATINUM 8573C (4 CPUs, kernel 7.0.0-1017-azure, rootful).
Tools: Graphite Meter 0.13.4, LibreSpeed 6.3.1, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest 2.5.4, Graphite Meter terminal client 0.13.4, LibreSpeed CLI 1.0.14. Browsers: chrome 156.0.8078.47, firefox 158.0.1.

## 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.5 [95.5, 95.6] | -0.1 % | 20.3 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.6 [95.6, 95.6] | -0.0 % | 20.1 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.4 [95.3, 95.5] | -0.3 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.7 [95.6, 95.7] | +0.0 % | 95.6 [95.5, 95.6] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.3 [95.2, 95.4] | -0.4 % | 97.2 [95.9, 97.6] | +1.6 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.8 [94.8, 94.8] | -0.9 % | 92.4 [91.4, 93.0] | -3.4 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.6 [95.5, 95.7] | -0.0 % | 95.5 [95.1, 95.6] | -0.1 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.3 [95.2, 95.7] | -0.4 % | 95.3 [94.3, 95.5] | -0.4 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.6 [95.5, 95.8] | -0.0 % | 95.3 [94.8, 95.7] | -0.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.3, 95.7] | -0.4 % | 95.3 [95.0, 95.9] | -0.4 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.6 [95.4, 95.9] | -0.0 % | 95.2 [94.8, 95.6] | -0.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.6 [95.5, 95.6] | -0.0 % | 95.6 [95.3, 96.5] | -0.0 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.6 [95.5, 95.8] | -0.0 % | 96.3 [95.7, 96.8] | +0.7 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.1 [955.4, 956.3] | -0.0 % | 952.7 [949.1, 955.4] | -0.4 % | 20.3 (20.1) | 21.1 (n/a) | 20.5 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 956.4 [956.4, 956.5] | -0.0 % | 956.4 [955.4, 956.4] | -0.0 % | 20.1 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 953.2 [953.0, 953.2] | -0.3 % | 953.2 [953.0, 953.2] | -0.3 % | 20.1 (20.1) | 20.3 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 938.1 [937.9, 938.7] | n/a | 949.4 [949.3, 949.4] | n/a | 20.1 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 955.7 [954.5, 956.9] | -0.1 % | 951.5 [946.8, 954.6] | -0.5 % | 21.0 (20.1) | 31.8 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 950.8 [948.8, 951.0] | -0.6 % | 944.4 [941.2, 946.2] | -1.3 % | 20.3 (20.1) | 21.4 (n/a) | 22.9 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 942.5 [940.4, 951.3] | n/a | 139.9 [133.5, 141.2] | n/a | 20.3 (20.1) | 20.5 (n/a) | 20.4 (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 954.0 [946.2, 954.9] | n/a | 668.5 [567.9, 822.3] | n/a | 20.4 (20.1) | 20.5 (n/a) | 22.2 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.3 [955.7, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 956.5 [954.0, 959.0] | +0.0 % | 944.5 [941.5, 948.0] | -1.2 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 943.8 [943.2, 944.2] | -1.3 % | 869.9 [868.4, 870.8] | -9.0 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 929.0 [898.3, 945.0] | -2.9 % | 890.0 [868.0, 903.8] | -6.9 % | 21.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 955.0 [954.0, 957.0] | -0.1 % | 950.5 [944.0, 956.5] | -0.6 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 930.0 [902.8, 945.0] | -2.8 % | 889.0 [872.5, 906.0] | -7.0 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 945.0 [942.3, 946.8] | -1.2 % | 414.0 [411.0, 415.8] | -56.7 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 955.0 [953.3, 957.0] | -0.1 % | 948.5 [940.3, 953.0] | -0.8 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 923.5 [908.3, 941.3] | -3.4 % | 894.5 [878.3, 906.5] | -6.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.0 [951.0, 953.0] | -0.5 % | 953.8 [951.0, 956.7] | -0.3 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 951.9 [948.1, 953.6] | -0.5 % | 950.0 [945.0, 951.6] | -0.7 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 948.8 [946.9, 951.2] | -0.8 % | 940.3 [934.6, 944.2] | -1.7 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 9561.9 [9552.5, 9563.4] | -0.0 % | 4256.3 [2709.2, 5411.8] | -55.5 % | 2.2 (2.1) | 2.8 (n/a) | 3.6 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.2 (n/a) | 2.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 9510.0 [9440.0, 9530.0] | -0.6 % | 9520.0 [9480.0, 9530.0] | -0.5 % | 2.1 (2.1) | 7.3 (n/a) | 2.2 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 6560.0 [5907.5, 9087.5] | n/a | 7095.0 [5955.0, 9230.0] | n/a | 2.1 (2.1) | 3.2 (n/a) | 2.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 3517.7 [2723.6, 4450.0] | -63.2 % | 5532.9 [4024.5, 6988.1] | -42.1 % | 3.0 (2.1) | 22.5 (n/a) | 53.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 5357.3 [3869.6, 6956.5] | -44.0 % | 2674.8 [1881.2, 4287.5] | -72.0 % | 2.2 (2.1) | 3.3 (n/a) | 3.2 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 2044.7 [1416.1, 2781.4] | n/a | 762.6 [677.0, 909.5] | n/a | 2.2 (2.1) | 2.5 (n/a) | 5.3 (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 2068.3 [1447.6, 2771.3] | n/a | 735.3 [653.2, 840.1] | n/a | 2.2 (2.1) | 2.5 (n/a) | 4.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.2 [9564.2, 9564.3] | +0.0 % | 9564.3 [9564.2, 9564.3] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 9265.0 [8149.0, 9531.0] | -3.1 % | 3275.0 [2212.5, 4098.8] | -65.8 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9355.3 [9354.9, 9355.8] | -2.2 % | 8100.5 [7625.6, 8565.2] | -15.3 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 2288.5 [1696.5, 2830.0] | -76.1 % | 3179.0 [2503.3, 3888.8] | -66.8 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 9329.5 [8165.0, 9498.0] | -2.5 % | 3242.5 [2216.5, 4153.0] | -66.1 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 2105.5 [1805.5, 2808.5] | -78.0 % | 3178.0 [2472.3, 3830.5] | -66.8 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 4016.5 [3079.8, 4223.0] | -58.0 % | 2541.5 [1735.8, 3333.8] | -73.4 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 9280.0 [7998.3, 9527.5] | -3.0 % | 3242.0 [2205.5, 4033.0] | -66.1 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 2186.0 [1780.5, 2902.8] | -77.1 % | 3146.0 [2457.3, 3759.3] | -67.1 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 9457.7 [8411.7, 9561.6] | -1.1 % | 3383.3 [2319.6, 4173.2] | -64.6 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 2837.7 [2218.4, 4127.2] | -70.3 % | 3131.8 [2530.8, 3676.1] | -67.3 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 4457.6 [3264.5, 5991.5] | -53.4 % | 2483.5 [1730.9, 3792.4] | -74.0 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 286.9 [286.9, 286.9] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.3 (20.1) | 180.3 (171.2) | 182.9 (180.0) |
| Graphite Meter Terminal | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.5, 28.7] | -0.1 % | 20.1 (20.1) | 176.0 (168.8) | 199.0 (194.0) |
| Graphite Meter Browser, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 21.0 (20.1) | 187.5 (176.9) | 181.8 (179.4) |
| iperf3 (reference) | 30/30 | payload | 286.9 [286.9, 287.0] | -0.0 % | 28.7 [28.6, 28.7] | -0.1 % | n/a (20.1) | n/a (184.2) | n/a (187.3) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [285.3, 287.0] | -0.3 % | 29.8 [28.8, 30.0] | +3.7 % | 20.3 (20.1) | n/a (163.1) | n/a (186.0) |
| LibreSpeed CLI | 30/30 | payload | 283.5 [283.2, 284.4] | -1.2 % | 29.6 [29.0, 29.6] | +3.1 % | 20.2 (20.1) | n/a (167.5) | n/a (171.7) |
| LibreSpeed, firefox | 30/30 | payload | 286.0 [284.3, 287.0] | -0.3 % | 29.3 [28.9, 29.4] | +2.1 % | 21.0 (20.1) | n/a (163.9) | n/a (186.3) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 286.0 [285.0, 287.0] | -0.3 % | 29.0 [28.7, 29.7] | +1.1 % | 20.1 (20.1) | n/a (162.7) | n/a (167.5) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 287.0 [285.3, 287.0] | +0.0 % | 29.3 [28.9, 29.4] | +2.1 % | 21.0 (20.1) | n/a (160.2) | n/a (186.0) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 287.0 [286.3, 287.0] | +0.0 % | 28.7 [28.1, 29.6] | +0.0 % | 20.1 (20.1) | n/a (157.5) | n/a (168.9) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 287.0 [286.0, 288.0] | +0.0 % | 29.1 [28.8, 29.7] | +1.4 % | 21.0 (20.1) | n/a (155.6) | n/a (187.2) |
| OpenSpeedTest, chrome | 30/30 | payload | 286.5 [286.1, 286.9] | -0.1 % | 31.4 [30.2, 31.8] | +9.3 % | 20.0 (20.1) | n/a (159.9) | n/a (197.3) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.4 [285.7, 287.9] | -0.2 % | 30.4 [29.9, 31.6] | +5.8 % | 20.0 (20.1) | n/a (158.7) | n/a (196.5) |

## 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 13.2 [12.9, 13.7] | n/a | 14.1 [13.7, 14.8] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 19.7 [19.1, 20.2] | n/a | 19.6 [19.0, 20.1] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 13.2 [12.8, 13.6] | n/a | 14.2 [13.5, 14.6] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 12.9 [12.7, 13.3] | n/a | 13.1 [12.3, 13.3] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 16.8 [16.4, 17.4] | n/a | 9.7 [9.4, 10.3] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 11.3 [10.8, 12.4] | n/a | 11.8 [11.3, 12.4] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 21.0 [20.2, 21.8] | n/a | 9.3 [9.1, 10.1] | n/a | 41.5 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 16.6 [15.9, 17.3] | n/a | 9.6 [9.1, 10.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 21.1 [19.9, 22.7] | n/a | 9.7 [8.8, 10.4] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 16.6 [16.0, 17.3] | n/a | 9.4 [8.9, 10.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 20.9 [20.3, 22.1] | n/a | 9.9 [9.3, 10.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 19.3 [18.5, 20.0] | n/a | 22.4 [21.9, 23.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.4 [19.0, 19.9] | n/a | 22.1 [20.8, 22.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 61.4 [54.6, 68.7] | n/a | 72.7 [65.5, 79.5] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 86.8 [81.5, 94.0] | n/a | 86.8 [83.1, 92.3] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 14.7 [12.3, 19.4] | n/a | 14.2 [12.1, 15.6] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 72.9 [59.9, 108.3] | n/a | 97.6 [39.5, 161.4] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 60.4 [55.0, 63.0] | n/a | 80.8 [68.1, 86.5] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 15.0 [13.7, 17.1] | n/a | 14.7 [13.5, 17.9] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 82.1 [68.8, 102.0] | n/a | 21.3 [19.0, 34.2] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 83.5 [63.7, 98.1] | n/a | 29.3 [24.0, 31.1] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 50.6 [47.7, 55.3] | n/a | 50.7 [47.9, 54.1] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 104.5 [92.8, 123.5] | n/a | 38.0 [36.3, 41.0] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 56.9 [52.9, 62.7] | n/a | 50.0 [44.4, 54.6] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 138.5 [127.0, 150.8] | n/a | 36.5 [33.4, 39.4] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 98.5 [84.9, 119.0] | n/a | 65.3 [50.0, 81.8] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 145.0 [111.8, 164.8] | n/a | 39.1 [34.4, 42.6] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 12.8 [11.4, 15.7] | n/a | 12.7 [11.2, 16.3] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 103.5 [92.0, 116.8] | n/a | 62.5 [51.6, 72.6] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 135.5 [117.0, 156.5] | n/a | 37.9 [33.3, 41.0] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 75.7 [71.4, 81.2] | n/a | 92.3 [86.4, 104.6] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 77.5 [75.3, 78.9] | n/a | 94.8 [88.0, 99.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 11.3 [9.9, 12.1] | n/a | 15.8 [12.5, 19.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 277.7 [272.6, 283.1] | n/a | 235.8 [225.9, 241.3] | n/a | 160.5 (160.1) | 160.4 (n/a) | 160.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 283.1 [280.6, 284.4] | n/a | 281.7 [277.6, 283.5] | n/a | 160.0 (160.1) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 272.7 [269.3, 279.3] | n/a | 239.2 [231.8, 244.6] | n/a | 161.0 (160.1) | 162.0 (n/a) | 161.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 227.0 [220.1, 234.0] | n/a | 204.2 [201.2, 226.4] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 269.5 [264.8, 273.8] | n/a | 236.5 [229.0, 241.8] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 230.9 [225.5, 237.4] | n/a | 123.1 [122.6, 123.1] | n/a | 160.2 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 275.0 [270.0, 277.0] | n/a | 231.0 [222.5, 235.8] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 269.0 [264.5, 273.0] | n/a | 227.0 [220.3, 237.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 273.5 [269.3, 276.0] | n/a | 226.0 [221.3, 230.0] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 268.0 [262.5, 272.0] | n/a | 230.5 [222.3, 238.5] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 277.0 [271.0, 279.0] | n/a | 224.0 [215.3, 232.8] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 273.6 [268.3, 277.6] | n/a | 274.4 [271.6, 278.3] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 269.4 [264.9, 273.2] | n/a | 275.8 [272.2, 279.6] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |

## 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 75.0 [74.9, 75.0] | n/a | 75.4 [75.3, 75.4] | n/a | 20.4 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.8] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 74.9 [74.8, 75.0] | n/a | 75.2 [75.1, 75.3] | n/a | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 75.0 [74.9, 75.1] | n/a | 75.1 [75.0, 75.2] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 71.3 [70.2, 71.4] | n/a | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.4 [69.3, 69.4] | n/a | 69.3 [68.8, 69.4] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.3 [80.2, 80.4] | n/a | 70.3 [69.7, 70.6] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.7 [77.7, 77.8] | n/a | 72.5 [72.4, 72.7] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 80.3 [80.2, 80.5] | n/a | 70.3 [69.5, 70.8] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 72.5 [71.2, 72.6] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.3 [80.2, 80.4] | n/a | 70.3 [69.6, 71.3] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.2 [80.1, 80.2] | n/a | 81.1 [80.3, 81.5] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.2 [80.1, 80.3] | n/a | 80.8 [80.7, 81.8] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. iperf3 bypasses nginx and measures the direct shaped path as a control. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.0 [955.5, 956.3] | -0.0 % | 954.5 [952.4, 955.5] | -0.2 % | 20.4 (20.1) | 21.3 (n/a) | 23.4 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 955.3 [951.8, 956.2] | -0.1 % | 954.0 [951.4, 955.8] | -0.3 % | 21.0 (20.1) | 33.0 (n/a) | 25.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.3 [956.0, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 953.5 [949.3, 956.0] | -0.3 % | 899.5 [888.0, 915.5] | -6.0 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 928.0 [888.5, 946.8] | -3.0 % | 853.0 [826.3, 869.5] | -10.8 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 950.9 [949.0, 953.0] | -0.6 % | 922.0 [918.3, 925.9] | -3.6 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 949.5 [947.6, 952.9] | -0.7 % | 911.1 [905.0, 915.0] | -4.7 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.5 [381.2, 381.7] | -0.3 % | 20.3 (20.1) | 20.8 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | 20.1 (20.1) | 20.3 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.3 [380.9, 381.6] | -0.3 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 382.6 [382.5, 382.6] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

## Unshaped, offloads on: as fast as the host allows

Unshaped single-test throughput on the runner’s virtual link. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | 18142.8 [12184.1, 21724.8] | 5125.7 [3321.3, 6976.6] | 0.27 | 8 | 1.56 |
| Graphite Meter Terminal | 30/30 | 26475.0 [21377.5, 51297.5] | 62165.0 [53702.5, 96430.0] | 0.19 | 9 | n/a |
| Graphite Meter Terminal, HTTP/2 | 30/30 | 13395.0 [11977.5, 18442.5] | 17170.0 [14115.0, 22845.0] | 0.55 | 5 | n/a |
| Graphite Meter Terminal, HTTP/3 | 30/30 | 7835.0 [6622.5, 10955.0] | 8330.0 [6922.5, 11565.0] | 1.01 | 12 | n/a |
| Graphite Meter Browser, firefox | 30/30 | 3860.3 [2968.4, 4775.7] | 6248.6 [4520.3, 8612.8] | 0.23 | 8 | 2.81 |
| iperf3 (reference) | 30/30 | 31010.5 [29310.6, 41975.4] | 44095.4 [42300.2, 76080.0] | 0.20 | 12 | n/a |
| LibreSpeed, chrome | 30/30 | 10384.5 [8410.0, 13889.3] | 4227.0 [2650.3, 5590.5] | 0.30 | 81 | 2.07 |
| LibreSpeed CLI | 30/30 | 28262.4 [25531.7, 50236.0] | 18539.9 [16161.6, 26582.7] | 0.33 | 71 | n/a |
| LibreSpeed, firefox | 30/30 | 2284.0 [1750.3, 2633.3] | 3365.5 [2676.8, 4345.3] | 0.32 | 86 | 5.69 |
| LibreSpeed Go backend, chrome | 30/30 | 10338.5 [8351.8, 13744.0] | 4185.0 [2666.5, 5670.5] | 0.32 | 49 | 2.06 |
| LibreSpeed Go backend, firefox | 30/30 | 2290.5 [1702.0, 2679.3] | 3300.0 [2718.3, 4297.3] | 0.33 | 52 | 5.74 |
| LibreSpeed Rust backend, chrome | 30/30 | 10415.0 [8442.8, 13574.8] | 4028.5 [2635.0, 5541.0] | 0.24 | 22 | 2.13 |
| LibreSpeed Rust backend, firefox | 30/30 | 2222.5 [1699.0, 2696.0] | 3395.5 [2658.0, 4207.3] | 0.23 | 26 | 5.66 |
| OpenSpeedTest, chrome | 30/30 | 9357.6 [7561.1, 12445.6] | 4178.4 [2762.7, 5728.8] | 0.19 | 21 | 2.15 |
| OpenSpeedTest, firefox | 30/30 | 2672.3 [2149.5, 3964.9] | 3247.4 [2672.3, 4384.4] | 0.24 | 20 | 5.62 |
