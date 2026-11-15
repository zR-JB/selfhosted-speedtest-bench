# GitHub runner benchmark, 2026-11-14

**4,530/4,530** retained runs completed across **15 runner jobs** (0 runs excluded by the busy-host rule).
The 25 and 40 Gbit/s shaped scenarios are skipped on these 4-vCPU runners. They require 8+ CPUs.

[Benchmark source at 6f9063202cdedffd4c7957dedd57758cef9b9a44](https://github.com/zR-JB/selfhosted-speedtest-bench/tree/6f9063202cdedffd4c7957dedd57758cef9b9a44) · [Workflow run and raw artifacts](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/43601751633)
[Provenance and exact pins](provenance.json) · [Retained scalar measurements](measurements.json.gz) · [Server CPU by phase](server-cpu.md) · [Bench overview](../../README.md) · [Previous report](../2026-11-01-ci-run-41295946781)

The workflow stores the detailed artifacts and screenshots for its retention window. The scalar archive
keeps the inputs used by the overview charts and tables. Read it with `gzip -dc measurements.json.gz`.
Provenance records the job order, CPU allocation, pinned releases and workload definitions.

To regenerate the overview tables and charts from the committed archive, run
`python3 bench/report.py 43601751633 --from-archive --rerender` from the repository root.
The renderer uses Python 3 with Matplotlib. When this is the latest run, the command also updates
the root README. Regenerating the detailed pass tables requires all 15 job artifacts, Node.js 22 or later,
and the benchmark source revision in local Git history. Use
`python3 bench/report.py 43601751633 /path/to/artifacts --rerender` while they remain available.

| Tested release | Version |
| --- | ---: |
| Graphite Meter Browser | 0.14.3 |
| LibreSpeed | 6.3.1 |
| LibreSpeed Go backend | 1.1.6 |
| LibreSpeed Rust backend | 1.4.0 |
| OpenSpeedTest | 2.5.4 |
| Graphite Meter Terminal | 0.14.3 |
| LibreSpeed CLI | 1.0.14 |
| Chrome | 157.0.8103.78 |
| Firefox | 160.0 |

## Overview data

We take each VM’s median over its retained passes, then summarize across VMs. A VM contributes once,
with up to two passes. Large marks show medians across VMs. Lines span the middle 50%, and small
marks show VM values where plotted. The spreads describe these runners. Sample sizes and exact
values are in the linked tables.

### Shaped throughput

Download / upload medians. Browser rows use Chrome. The loss test uses a 100 Mbit/s link, 1% loss in each direction and 40 ms RTT.

| Tool or client | 1 Gbit/s (Mbit/s) | 10 Gbit/s (Gbit/s) | 1% loss (Mbit/s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser | 956.1 / 954.4 | 9.56 / 4.19 | 13.4 / 13.9 |
| LibreSpeed | 956.0 / 943.5 | 9.14 / 3.23 | 16.6 / 9.5 |
| LibreSpeed Go backend | 954.5 / 946.5 | 9.20 / 3.22 | 16.9 / 9.5 |
| LibreSpeed Rust backend | 954.0 / 947.0 | 9.39 / 3.17 | 16.9 / 9.6 |
| OpenSpeedTest | 953.2 / 954.5 | 9.27 / 3.31 | 18.7 / 21.5 |
| Graphite Meter Terminal | 956.4 / 956.5 | 9.56 / 9.56 | 20.0 / 20.0 |
| LibreSpeed CLI | 943.8 / 871.5 | 9.36 / 7.88 | 11.2 / 11.8 |
| iperf3 (reference) | 956.4 / 956.4 | 9.56 / 9.56 | 13.0 / 12.8 |

### 10 Gbit/s upload spread

Each cell shows the median [25th, 75th percentile] and number of VMs. The last column uses matched same-VM, same-pass iperf3 rates. A lower achieved rate can come from any part of the test setup.

Graphite Meter Browser’s same-pass upload difference from OpenSpeedTest in Chrome was **+0.69 Gbit/s** (middle 50% +0.38 to +0.80). Graphite Meter Browser reported more on **15/15 matched VMs**.

| Tool or client | Upload (Gbit/s) | Paired difference from iperf3 (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 4.19 [2.68, 5.74] (n=15) | -56.1 [-72.0, -40.0] (n=15) |
| LibreSpeed · Chrome | 3.23 [2.18, 4.66] (n=15) | -66.2 [-77.2, -51.3] (n=15) |
| LibreSpeed Go backend · Chrome | 3.22 [2.17, 4.74] (n=15) | -66.3 [-77.4, -50.4] (n=15) |
| LibreSpeed Rust backend · Chrome | 3.17 [2.17, 4.65] (n=15) | -66.8 [-77.3, -51.4] (n=15) |
| OpenSpeedTest · Chrome | 3.31 [2.30, 4.85] (n=15) | -65.4 [-75.9, -49.3] (n=15) |
| Graphite Meter Browser · Firefox | 5.09 [3.72, 7.70] (n=15) | -46.8 [-61.1, -19.5] (n=15) |
| LibreSpeed · Firefox | 3.10 [2.47, 4.01] (n=15) | -67.6 [-74.2, -58.1] (n=15) |
| LibreSpeed Go backend · Firefox | 3.08 [2.48, 3.84] (n=15) | -67.7 [-74.1, -59.9] (n=15) |
| LibreSpeed Rust backend · Firefox | 3.05 [2.49, 3.93] (n=15) | -68.1 [-74.0, -58.9] (n=15) |
| OpenSpeedTest · Firefox | 2.85 [2.60, 3.88] (n=15) | -70.2 [-72.8, -59.4] (n=15) |
| Graphite Meter Terminal | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | 7.88 [7.60, 8.23] (n=15) | -17.6 [-20.6, -13.9] (n=15) |
| iperf3 (reference) | 9.56 [9.56, 9.56] (n=15) | — |

### Matched 1 Gbit/s agreement

Signed percentage differences from iperf3 on the same VM and pass. Each cell shows the median [25th, 75th percentile] and number of VMs after reducing the matched pass differences within each VM. Tests ran sequentially. App and iperf3 start times were a median of 2.5 minutes apart (maximum 8.4).

| Tool or client | Download difference (%) | Upload difference (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.0 [-0.1, 0.0] (n=15) | -0.2 [-0.3, -0.1] (n=15) |
| LibreSpeed · Chrome | 0.0 [-0.2, +0.1] (n=15) | -1.3 [-1.5, -0.8] (n=15) |
| LibreSpeed Go backend · Chrome | -0.2 [-0.3, -0.1] (n=15) | -1.0 [-1.3, -0.1] (n=15) |
| LibreSpeed Rust backend · Chrome | -0.2 [-0.3, -0.1] (n=15) | -1.0 [-1.2, -0.4] (n=15) |
| OpenSpeedTest · Chrome | -0.3 [-0.6, -0.3] (n=15) | -0.2 [-0.7, 0.0] (n=15) |
| Graphite Meter Browser · Firefox | -0.1 [-0.1, 0.0] (n=15) | -0.5 [-0.7, -0.4] (n=15) |
| LibreSpeed · Firefox | -3.3 [-5.2, -1.6] (n=15) | -6.1 [-9.7, -5.0] (n=15) |
| LibreSpeed Go backend · Firefox | -3.5 [-4.4, -1.3] (n=15) | -7.3 [-8.4, -5.4] (n=15) |
| LibreSpeed Rust backend · Firefox | -2.9 [-5.2, -1.0] (n=15) | -6.2 [-7.3, -5.6] (n=15) |
| OpenSpeedTest · Firefox | -0.6 [-0.8, -0.3] (n=15) | -0.7 [-1.2, -0.5] (n=15) |
| Graphite Meter Terminal | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | -1.3 [-1.8, -1.3] (n=15) | -8.9 [-9.1, -8.8] (n=15) |

### Unshaped throughput and browser CPU

Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand.
Each maximum is the fastest retained pass in that direction. The two maxima can come from different passes. Browser CPU measures the client process tree over the full run per GB at the shaper.

| Tool or client | Median down / up (Gbit/s) | Max down / up (Gbit/s) | Browser CPU (s/GB) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 16.7 / 4.7 | 25.7 / 12.4 | 1.48 |
| LibreSpeed · Chrome | 10.2 / 4.1 | 16.7 / 11.2 | 2.11 |
| LibreSpeed Go backend · Chrome | 10.0 / 4.1 | 17.0 / 11.3 | 2.12 |
| LibreSpeed Rust backend · Chrome | 10.1 / 4.1 | 16.5 / 11.4 | 2.14 |
| OpenSpeedTest · Chrome | 9.2 / 4.3 | 17.3 / 11.9 | 2.14 |
| Graphite Meter Browser · Firefox | 3.5 / 5.8 | 6.0 / 17.1 | 2.62 |
| LibreSpeed · Firefox | 2.2 / 3.2 | 3.6 / 5.4 | 5.80 |
| LibreSpeed Go backend · Firefox | 2.2 / 3.4 | 3.5 / 5.5 | 5.74 |
| LibreSpeed Rust backend · Firefox | 2.0 / 3.3 | 3.5 / 5.6 | 5.66 |
| OpenSpeedTest · Firefox | 2.6 / 3.2 | 6.3 / 5.2 | 5.69 |
| Graphite Meter Terminal | 35.5 / 55.3 | 63.5 / 105.5 | — |
| LibreSpeed CLI | 28.3 / 18.6 | 55.3 / 28.2 | — |
| iperf3 (reference) | 31.4 / 44.5 | 63.9 / 100.6 | — |

#### Unshaped native upload by runner hardware

Upload medians in Gbit/s. “GM above iperf3” counts VMs after matching same-pass comparisons. CPU, kernel and runner conditions vary together. Groups with one VM show that VM’s median.

Graphite Meter Terminal had a higher upload rate than iperf3 on **11 of 15 VMs** after matching passes. The split was 0/4 on AWS-kernel VMs, 11/11 on Azure-kernel VMs.

| CPU and kernel | VMs | Graphite Meter Terminal | LibreSpeed CLI | iperf3 | GM above iperf3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| AMD EPYC 7763 64-Core Processor (7.0.0-1017-azure) | 7 | 55.3 | 16.1 | 42.5 | 7/7 |
| AMD EPYC 9V45 96-Core Processor (7.0.0-1017-azure) | 2 | 92.7 | 26.5 | 74.7 | 2/2 |
| AMD EPYC 9V74 80-Core Processor (7.0.0-1017-azure) | 1 | 65.6 | 18.6 | 43.1 | 1/1 |
| INTEL(R) XEON(R) PLATINUM 8573C (7.0.0-1017-azure) | 1 | 62.8 | 23.3 | 58.0 | 1/1 |
| Intel(R) Xeon(R) 6975P-C (7.0.0-1014-aws) | 4 | 48.8 | 27.7 | 95.4 | 0/4 |

### Server resources at 1 Gbit/s

Server CPU is container CPU time per decimal GB of server-interface traffic during each phase,
counting bytes in both directions. Peak memory is the container’s per-run peak in decimal MB.
The adjacent reported rates show how much of the same shaped link each setup used. Browser CPU is
measured separately on the client. Native client CPU is unavailable.

| Tool or client | Down / up (Mbit/s) | Down CPU (s/GB) | Up CPU (s/GB) | Peak RAM (MB) |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 956.1 / 954.4 | 0.368 | 3.949 | 15.1 |
| LibreSpeed · Chrome | 956.0 / 943.5 | 0.418 | 5.700 | 80.3 |
| LibreSpeed Go backend · Chrome | 954.5 / 946.5 | 0.396 | 5.034 | 48.1 |
| LibreSpeed Rust backend · Chrome | 954.0 / 947.0 | 0.322 | 3.846 | 22.5 |
| OpenSpeedTest · Chrome | 953.2 / 954.5 | 0.182 | 3.672 | 29.3 |
| Graphite Meter Terminal | 956.4 / 956.5 | 0.203 | 6.849 | 17.2 |
| LibreSpeed CLI | 943.8 / 871.5 | 0.275 | 1.997 | 68.7 |
| iperf3 (reference) | 956.4 / 956.4 | 0.239 | 5.078 | 19.3 |
| Graphite Meter Browser · Firefox | 955.6 / 950.7 | 0.303 | 4.698 | 14.9 |
| LibreSpeed · Firefox | 924.5 / 897.5 | 0.486 | 5.441 | 85.8 |
| LibreSpeed Go backend · Firefox | 923.0 / 886.5 | 0.443 | 4.934 | 52.0 |
| LibreSpeed Rust backend · Firefox | 929.0 / 897.0 | 0.404 | 3.278 | 26.4 |
| OpenSpeedTest · Firefox | 951.1 / 949.5 | 0.231 | 3.568 | 29.4 |

Absolute server CPU time for the complete 1 Gbit/s test and each transfer phase.

| Tool or client | Download (CPU s) | Upload (CPU s) | Test total (CPU s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.22 | 3.30 | 3.47 |
| LibreSpeed · Chrome | 0.36 | 5.92 | 6.31 |
| LibreSpeed Go backend · Chrome | 0.34 | 5.18 | 5.58 |
| LibreSpeed Rust backend · Chrome | 0.27 | 3.86 | 4.19 |
| OpenSpeedTest · Chrome | 0.33 | 5.64 | 6.01 |
| Graphite Meter Terminal | 0.29 | 9.89 | 10.30 |
| LibreSpeed CLI | 0.54 | 3.59 | 4.44 |
| iperf3 (reference) | 0.36 | 7.68 | 8.02 |
| Graphite Meter Browser · Firefox | 0.39 | 4.20 | 4.67 |
| LibreSpeed · Firefox | 0.40 | 5.19 | 5.70 |
| LibreSpeed Go backend · Firefox | 0.37 | 4.57 | 5.04 |
| LibreSpeed Rust backend · Firefox | 0.33 | 3.12 | 3.51 |
| OpenSpeedTest · Firefox | 0.42 | 5.41 | 5.83 |

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
| Graphite Meter Browser · Chrome | 954.4 | 972.9 | 7/30 |
| LibreSpeed · Chrome | 943.5 | 972.9 | 2/30 |
| LibreSpeed Go backend · Chrome | 946.5 | 972.7 | 8/30 |
| LibreSpeed Rust backend · Chrome | 947.0 | 972.2 | 7/30 |
| OpenSpeedTest · Chrome | 954.5 | 972.9 | 7/30 |
| Graphite Meter Browser · Firefox | 950.7 | 972.9 | 4/30 |
| LibreSpeed · Firefox | 897.5 | 961.3 | 0/30 |
| LibreSpeed Go backend · Firefox | 886.5 | 960.8 | 0/30 |
| LibreSpeed Rust backend · Firefox | 897.0 | 957.3 | 0/30 |
| OpenSpeedTest · Firefox | 949.5 | 974.3 | 3/30 |
| Graphite Meter Terminal | 956.5 | 971.5 | 18/30 |
| LibreSpeed CLI | 871.5 | 962.6 | 0/30 |
| iperf3 (reference) | 956.4 | 972.4 | — |

**30 Mbit/s upload, deep FIFO**

| Tool or client | App rate | Shaper | Above iperf3 |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 28.7 | 30.8 | 15/30 |
| LibreSpeed · Chrome | 29.6 | 30.9 | 25/30 |
| LibreSpeed Go backend · Chrome | 29.1 | 30.9 | 18/30 |
| LibreSpeed Rust backend · Chrome | 28.6 | 30.9 | 12/30 |
| OpenSpeedTest · Chrome | 31.0 | 30.8 | 30/30 |
| Graphite Meter Browser · Firefox | 28.7 | 30.6 | 15/30 |
| LibreSpeed · Firefox | 29.1 | 30.9 | 19/30 |
| LibreSpeed Go backend · Firefox | 29.4 | 30.8 | 23/30 |
| LibreSpeed Rust backend · Firefox | 28.9 | 30.9 | 19/30 |
| OpenSpeedTest · Firefox | 30.8 | 30.8 | 30/30 |
| Graphite Meter Terminal | 28.7 | 30.9 | 12/30 |
| LibreSpeed CLI | 29.0 | 30.9 | 25/30 |
| iperf3 (reference) | 28.7 | 30.9 | — |

### Idle latency against ICMP

The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference.
Each cell shows the median paired difference in ms [25th, 75th percentile] and number of VMs.

| Tool or client | 20 ms path | 40 ms path | 160 ms path |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | +0.3 [+0.2, +0.3] (n=15) | +0.3 [+0.3, +0.3] (n=15) | +0.4 [+0.4, +0.4] (n=15) |
| LibreSpeed · Chrome | +0.2 [+0.2, +0.2] (n=15) | +0.2 [+0.1, +0.2] (n=15) | -0.1 [-0.1, -0.1] (n=15) |
| LibreSpeed Go backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, +0.1] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed Rust backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| OpenSpeedTest · Chrome | +0.4 [-0.1, +0.9] (n=15) | +0.9 [+0.1, +0.9] (n=15) | +0.8 [+0.3, +0.9] (n=15) |
| Graphite Meter Browser · Firefox | +0.9 [+0.9, +0.9] (n=15) | +1.4 [+0.9, +1.4] (n=15) | +0.9 [+0.8, +0.9] (n=15) |
| LibreSpeed · Firefox | +1.8 [+1.4, +1.9] (n=15) | +1.9 [+1.3, +1.9] (n=15) | +1.8 [+1.4, +1.8] (n=15) |
| LibreSpeed Go backend · Firefox | +0.9 [+0.9, +1.4] (n=15) | +1.4 [+0.9, +1.4] (n=15) | +1.4 [+1.1, +1.8] (n=15) |
| LibreSpeed Rust backend · Firefox | +1.3 [+0.9, +1.4] (n=15) | +1.4 [+0.9, +1.4] (n=15) | +1.3 [+0.9, +1.4] (n=15) |
| OpenSpeedTest · Firefox | +0.4 [-0.1, +0.4] (n=15) | +0.9 [+0.8, +0.9] (n=15) | +0.9 [+0.8, +0.9] (n=15) |
| Graphite Meter Terminal | 0.0 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed CLI | +0.1 [+0.1, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) |

### Latency under load on a FIFO

Each cell shows the app’s reported latency followed by the queue-based estimate, in ms.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 162.2 / 154.5 | 184.9 / 181.3 |
| Graphite Meter Browser · Firefox | 170.0 / 159.5 | 184.5 / 180.6 |
| Graphite Meter Terminal | 175.0 / 169.5 | 197.5 / 193.2 |

Paired app minus queue estimate in ms, summarized within VMs, then across VMs.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | +9.5 [+7.8, +11.8] (n=15) | +3.4 [+2.1, +5.5] (n=15) |
| Graphite Meter Browser · Firefox | +7.9 [+6.3, +12.6] (n=15) | +3.9 [+2.8, +5.5] (n=15) |
| Graphite Meter Terminal | +5.4 [+4.6, +6.7] (n=15) | +4.9 [+4.4, +5.6] (n=15) |

## Pooled pass tables

The tables below pool all retained completed passes for each configuration, including alternate
transports. Their comparison columns show the difference from the modeled TCP payload ceiling
when iperf3 reaches at least 98% of the model in both directions. QUIC rows show measured rates separately.
The matched comparison above uses the measured same-pass receiver rate.
Below-ceiling rates can reflect any constraint on the end-to-end transfer.

[100 Mbit/s](#100100-mbits-20-ms-rtt-fq_codel) · [1 Gbit/s](#11-gbits-20-ms-rtt-fq_codel) · [10 Gbit/s](#1010-gbits-2-ms-rtt-fq_codel-offloads-on) · [Deep FIFO](#30030-mbits-20-ms-rtt-200-ms-fifo) · [1% loss](#100100-mbits-40-ms-rtt-1--loss-each-way-fq_codel) · [0.1% loss](#11-gbits-40-ms-rtt-01--loss-each-way-fq_codel) · [160 ms RTT](#300300-mbits-160-ms-rtt-fq_codel) · [Competing traffic](#100100-mbits-20-ms-rtt-fq_codel-one-competing-flow-each-way) · [Reverse proxy](#11-gbits-20-ms-rtt-fq_codel-behind-nginx) · [Two servers](#two-servers-200200-mbits-path-each-20-ms-rtt-fq_codel) · [Unshaped](#unshaped-offloads-on-as-fast-as-the-host-allows)

<!-- pooled-pass-tables -->
Jobs: 15. Runs: 4530, of which 0 left out from blocks on a busy host. Hosts: AMD EPYC 7763 64-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 9V74 80-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); Intel(R) Xeon(R) 6975P-C (4 CPUs, kernel 7.0.0-1014-aws, rootful); AMD EPYC 9V45 96-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); INTEL(R) XEON(R) PLATINUM 8573C (4 CPUs, kernel 7.0.0-1017-azure, rootful).
Tools: Graphite Meter 0.14.3, LibreSpeed 6.3.1, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest 2.5.4, Graphite Meter terminal client 0.14.3, LibreSpeed CLI 1.0.14. Browsers: chrome 157.0.8103.78, firefox 160.0.

## 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 95.6 [95.6, 95.7] | +0.0 % | 95.5 [95.4, 95.6] | -0.2 % | 20.4 (20.1) | 20.6 (n/a) | 20.5 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.6 [95.6, 95.7] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.4 [95.3, 95.5] | -0.2 % | 21.0 (20.1) | 23.5 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.5, 95.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.3 [95.2, 95.4] | -0.4 % | 96.0 [95.8, 96.5] | +0.4 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.8 [94.7, 94.8] | -0.9 % | 91.4 [91.4, 92.4] | -4.4 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.3 [95.1, 95.6] | -0.3 % | 95.5 [94.5, 96.3] | -0.2 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.3 [95.2, 95.3] | -0.4 % | 95.5 [95.0, 95.7] | -0.1 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.3 [95.1, 95.5] | -0.4 % | 95.3 [94.6, 96.0] | -0.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.2, 95.3] | -0.4 % | 95.6 [94.7, 96.3] | -0.0 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.3 [95.2, 95.5] | -0.4 % | 95.8 [95.1, 96.3] | +0.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.6 [95.4, 95.6] | -0.0 % | 95.5 [95.3, 96.5] | -0.1 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.5 [95.3, 95.6] | -0.2 % | 96.5 [95.8, 96.9] | +0.9 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.3 [955.8, 956.4] | -0.0 % | 954.6 [953.2, 955.8] | -0.2 % | 20.4 (20.1) | 21.2 (n/a) | 20.6 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 956.4 [956.4, 956.4] | -0.0 % | 956.4 [956.4, 956.5] | -0.0 % | 20.1 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 953.2 [953.2, 953.2] | -0.3 % | 953.2 [953.2, 953.2] | -0.3 % | 20.2 (20.1) | 20.3 (n/a) | 20.2 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 938.2 [937.9, 938.6] | n/a | 948.8 [948.7, 948.8] | n/a | 20.2 (20.1) | 20.3 (n/a) | 20.3 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 955.8 [954.8, 956.5] | -0.1 % | 952.5 [948.0, 955.1] | -0.4 % | 21.0 (20.1) | 32.0 (n/a) | 22.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 950.9 [950.3, 951.2] | -0.6 % | 946.8 [945.0, 948.6] | -1.0 % | 20.4 (20.1) | 21.6 (n/a) | 22.7 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 949.4 [946.6, 952.1] | n/a | 691.8 [636.0, 811.9] | n/a | 20.4 (20.1) | 20.6 (n/a) | 23.1 (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 948.1 [944.0, 951.2] | n/a | 640.3 [554.8, 786.7] | n/a | 20.5 (20.1) | 20.6 (n/a) | 21.9 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.3, 956.4] | -0.0 % | 956.4 [956.3, 956.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 956.5 [954.0, 958.8] | +0.0 % | 945.5 [939.0, 949.0] | -1.1 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 943.6 [939.9, 944.6] | -1.3 % | 871.2 [869.0, 872.4] | -8.9 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 927.5 [908.0, 943.8] | -3.0 % | 893.5 [877.5, 912.0] | -6.6 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 954.0 [954.0, 955.8] | -0.3 % | 951.0 [941.3, 956.5] | -0.6 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 938.0 [906.8, 944.3] | -1.9 % | 890.5 [878.0, 904.8] | -6.9 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 946.0 [945.0, 949.5] | -1.1 % | 412.0 [411.0, 414.0] | -56.9 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 954.0 [953.0, 955.0] | -0.3 % | 949.0 [943.3, 955.8] | -0.8 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 933.0 [904.3, 949.5] | -2.4 % | 897.0 [883.3, 906.5] | -6.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.7 [952.0, 954.1] | -0.4 % | 953.8 [950.8, 955.9] | -0.3 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 950.7 [948.7, 954.2] | -0.6 % | 949.0 [944.5, 952.6] | -0.8 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 949.5 [947.7, 950.9] | -0.7 % | 941.3 [933.8, 945.6] | -1.6 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 9559.3 [9554.3, 9563.6] | -0.0 % | 4194.8 [2669.2, 5891.9] | -56.1 % | 2.2 (2.1) | 3.2 (n/a) | 3.5 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.2 (n/a) | 2.2 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 9525.0 [9510.0, 9530.0] | -0.4 % | 9525.0 [9502.5, 9530.0] | -0.4 % | 2.1 (2.1) | 6.8 (n/a) | 2.5 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 6090.0 [5945.0, 7022.5] | n/a | 6290.0 [6107.5, 7810.0] | n/a | 2.1 (2.1) | 3.3 (n/a) | 2.3 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 3211.6 [2537.7, 4999.1] | -66.4 % | 5085.5 [3744.6, 7961.0] | -46.8 % | 3.0 (2.1) | 21.0 (n/a) | 64.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 4908.5 [3833.5, 6871.9] | -48.7 % | 2626.2 [1813.7, 4600.6] | -72.5 % | 2.2 (2.1) | 3.5 (n/a) | 3.4 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 2123.4 [1497.1, 2847.3] | n/a | 738.6 [682.0, 1407.3] | n/a | 2.2 (2.1) | 2.4 (n/a) | 5.7 (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 2114.5 [1492.2, 2766.1] | n/a | 696.1 [626.3, 1103.8] | n/a | 2.3 (2.1) | 2.6 (n/a) | 4.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.2 [9564.2, 9564.3] | +0.0 % | 9564.3 [9564.2, 9564.3] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 9142.5 [8141.5, 9562.8] | -4.4 % | 3231.0 [2177.5, 4863.8] | -66.2 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9355.1 [9354.8, 9355.4] | -2.2 % | 7880.4 [7599.9, 8230.5] | -17.6 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 2228.0 [1693.3, 3101.8] | -76.7 % | 3052.5 [2445.5, 4036.5] | -68.1 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 9196.0 [8013.3, 9549.5] | -3.8 % | 3221.0 [2177.3, 4984.5] | -66.3 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 2052.0 [1729.5, 3014.5] | -78.5 % | 3054.5 [2470.3, 3878.8] | -68.1 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 3927.0 [3104.0, 4327.3] | -58.9 % | 2460.0 [1693.5, 3298.0] | -74.3 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 9386.5 [8040.0, 9538.0] | -1.9 % | 3173.5 [2170.5, 4913.0] | -66.8 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 2213.0 [1682.3, 3009.3] | -76.9 % | 3054.0 [2443.5, 3935.0] | -68.1 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 9169.5 [7932.9, 9558.8] | -4.1 % | 3311.6 [2305.0, 5112.4] | -65.4 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 2723.4 [2191.3, 5045.9] | -71.5 % | 2882.1 [2573.3, 3904.8] | -69.9 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 4343.0 [3117.8, 5676.8] | -54.6 % | 2407.8 [1705.8, 4010.7] | -74.8 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.4 (20.1) | 155.8 (142.7) | 185.4 (180.8) |
| Graphite Meter Terminal | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.2 (20.1) | 175.0 (169.0) | 198.0 (193.4) |
| Graphite Meter Browser, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 21.0 (20.1) | 178.5 (174.7) | 184.3 (180.0) |
| iperf3 (reference) | 30/30 | payload | 286.9 [286.9, 287.0] | -0.0 % | 28.7 [28.6, 28.8] | -0.0 % | n/a (20.1) | n/a (181.1) | n/a (187.3) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [283.0, 287.0] | -0.3 % | 29.9 [29.1, 30.0] | +4.2 % | 20.3 (20.1) | n/a (161.6) | n/a (186.4) |
| LibreSpeed CLI | 30/30 | payload | 283.6 [282.9, 284.3] | -1.2 % | 29.0 [29.0, 29.6] | +1.2 % | 20.2 (20.1) | n/a (172.0) | n/a (173.6) |
| LibreSpeed, firefox | 30/30 | payload | 285.0 [284.0, 286.8] | -0.7 % | 29.0 [28.5, 29.4] | +1.1 % | 22.0 (20.1) | n/a (160.1) | n/a (186.4) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 286.0 [283.3, 286.8] | -0.3 % | 28.9 [28.3, 29.7] | +0.5 % | 20.1 (20.1) | n/a (162.1) | n/a (166.9) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 286.0 [283.3, 287.0] | -0.3 % | 29.3 [28.6, 29.6] | +2.1 % | 21.0 (20.1) | n/a (160.2) | n/a (186.4) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 28.3 [28.1, 29.0] | -1.4 % | 20.1 (20.1) | n/a (156.4) | n/a (172.0) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 28.9 [28.6, 29.3] | +0.5 % | 22.0 (20.1) | n/a (155.4) | n/a (188.1) |
| OpenSpeedTest, chrome | 30/30 | payload | 286.4 [286.0, 287.2] | -0.2 % | 31.3 [30.3, 31.5] | +8.9 % | 20.5 (20.1) | n/a (161.9) | n/a (195.5) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.8 [285.8, 287.8] | -0.0 % | 31.0 [30.1, 31.5] | +8.0 % | 20.0 (20.1) | n/a (163.4) | n/a (196.7) |

## 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 13.1 [12.6, 13.7] | n/a | 13.9 [13.2, 14.2] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 19.9 [19.3, 20.7] | n/a | 19.9 [19.2, 20.5] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 13.3 [12.8, 13.6] | n/a | 14.1 [13.1, 15.2] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 12.8 [12.4, 13.3] | n/a | 12.6 [12.5, 13.2] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 16.5 [16.1, 17.4] | n/a | 9.4 [8.9, 9.9] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 11.1 [10.4, 11.7] | n/a | 11.8 [11.3, 12.8] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 20.9 [20.3, 22.1] | n/a | 9.4 [9.0, 10.0] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 17.1 [16.2, 17.6] | n/a | 9.4 [9.1, 9.7] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 21.4 [19.9, 22.1] | n/a | 9.8 [9.3, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 16.6 [16.0, 17.5] | n/a | 9.7 [9.2, 10.2] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 20.9 [19.9, 22.4] | n/a | 9.6 [9.1, 10.0] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 18.8 [17.9, 19.8] | n/a | 21.6 [20.9, 23.0] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.2 [18.7, 19.8] | n/a | 21.9 [21.1, 23.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 56.0 [52.4, 62.0] | n/a | 69.7 [62.3, 75.6] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 87.6 [82.4, 93.8] | n/a | 87.5 [84.1, 92.4] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 14.4 [13.7, 17.0] | n/a | 13.4 [11.9, 15.1] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 77.9 [63.0, 116.7] | n/a | 140.7 [106.9, 174.6] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 59.3 [54.8, 62.7] | n/a | 76.1 [67.8, 81.2] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 16.8 [13.8, 19.0] | n/a | 14.1 [11.5, 17.3] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 89.7 [72.5, 120.6] | n/a | 26.4 [22.1, 31.3] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 95.2 [73.1, 114.1] | n/a | 29.0 [25.2, 32.1] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.4 (n/a) |
| iperf3 (reference) | 30/30 | payload | 50.1 [46.6, 52.1] | n/a | 49.2 [47.0, 51.3] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 94.9 [84.1, 119.0] | n/a | 36.3 [33.3, 40.5] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 58.0 [49.6, 62.9] | n/a | 49.5 [45.2, 52.1] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 132.0 [111.5, 149.5] | n/a | 38.0 [35.6, 44.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 100.3 [86.0, 113.0] | n/a | 71.0 [50.7, 84.3] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 142.0 [117.0, 156.8] | n/a | 38.0 [34.4, 41.3] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 13.1 [11.2, 14.9] | n/a | 13.1 [10.9, 15.0] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 103.0 [89.0, 112.0] | n/a | 59.5 [43.8, 101.7] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 128.5 [115.0, 145.5] | n/a | 37.5 [34.6, 43.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 78.9 [73.8, 83.0] | n/a | 95.8 [87.8, 100.4] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 77.3 [73.7, 82.3] | n/a | 94.1 [88.9, 98.4] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 11.1 [10.3, 12.4] | n/a | 15.3 [12.8, 18.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 274.9 [265.5, 279.1] | n/a | 237.7 [230.7, 241.3] | n/a | 160.5 (160.1) | 160.4 (n/a) | 160.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 282.7 [281.3, 284.6] | n/a | 279.5 [276.3, 282.8] | n/a | 160.0 (160.1) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 276.3 [265.8, 282.6] | n/a | 238.4 [234.3, 241.3] | n/a | 161.0 (160.1) | 162.3 (n/a) | 161.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 222.7 [201.8, 235.8] | n/a | 204.1 [202.8, 225.6] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 269.5 [264.0, 275.0] | n/a | 238.0 [229.0, 243.3] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 230.3 [222.7, 235.1] | n/a | 123.1 [122.6, 123.1] | n/a | 160.3 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 273.0 [268.0, 277.8] | n/a | 230.0 [224.0, 236.0] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 271.0 [266.3, 275.8] | n/a | 235.0 [224.3, 239.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 274.0 [269.3, 278.0] | n/a | 224.5 [219.0, 229.8] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 270.5 [264.5, 273.0] | n/a | 232.5 [228.3, 238.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 275.0 [274.0, 277.0] | n/a | 223.0 [216.5, 230.0] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 272.3 [269.7, 275.6] | n/a | 273.8 [272.1, 277.6] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 270.7 [267.4, 274.7] | n/a | 273.3 [271.2, 276.5] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |

## 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 75.0 [74.9, 75.1] | n/a | 75.2 [75.1, 75.3] | n/a | 20.5 (20.1) | 20.6 (n/a) | 20.5 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.8] | n/a | 20.3 (20.1) | 20.3 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 74.9 [74.9, 75.0] | n/a | 75.1 [75.0, 75.2] | n/a | 21.0 (20.1) | 22.8 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 75.0 [74.9, 75.1] | n/a | 75.1 [75.0, 75.3] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.8 [77.8, 77.8] | n/a | 70.7 [70.0, 71.3] | n/a | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.4 [69.3, 69.4] | n/a | 68.8 [68.8, 69.3] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.2 [80.1, 80.4] | n/a | 71.2 [69.9, 71.3] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.7 [77.7, 77.8] | n/a | 72.5 [72.4, 72.7] | n/a | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 80.1 [79.9, 80.5] | n/a | 71.1 [69.9, 71.3] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 72.6 [72.0, 72.7] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.2 [80.0, 80.3] | n/a | 71.3 [70.4, 71.4] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.2 [80.1, 80.2] | n/a | 80.8 [80.5, 81.3] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.2 [80.1, 80.3] | n/a | 80.8 [80.6, 81.8] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. iperf3 bypasses nginx and measures the direct shaped path as a control. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 955.9 [951.6, 956.3] | -0.1 % | 954.4 [953.1, 955.9] | -0.2 % | 20.4 (20.1) | 21.8 (n/a) | 22.7 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 954.9 [951.5, 955.8] | -0.2 % | 954.9 [953.0, 956.2] | -0.2 % | 21.0 (20.1) | 33.0 (n/a) | 25.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.3 [956.3, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 954.0 [939.5, 956.0] | -0.3 % | 903.5 [885.0, 915.0] | -5.5 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 918.0 [893.0, 943.5] | -4.0 % | 841.0 [818.3, 875.8] | -12.1 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.5 [951.5, 953.1] | -0.4 % | 922.6 [918.2, 925.3] | -3.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 952.3 [951.0, 954.3] | -0.4 % | 914.0 [902.0, 919.8] | -4.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.6 [381.2, 381.8] | -0.3 % | 20.4 (20.1) | 20.8 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | 20.1 (20.1) | 20.4 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 382.5 [382.4, 382.6] | -0.0 % | 381.3 [380.9, 381.7] | -0.3 % | 21.0 (20.1) | 23.0 (n/a) | 21.0 (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 382.6 [382.5, 382.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

## Unshaped, offloads on: as fast as the host allows

Unshaped single-test throughput on the runner’s virtual link. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | 16675.7 [12316.7, 21524.1] | 4724.0 [3180.3, 9951.0] | 0.29 | 9 | 1.48 |
| Graphite Meter Terminal | 30/30 | 35535.0 [33032.5, 59115.0] | 56305.0 [52185.0, 62815.0] | 0.16 | 11 | n/a |
| Graphite Meter Terminal, HTTP/2 | 30/30 | 14290.0 [12542.5, 16207.5] | 14895.0 [14015.0, 17990.0] | 0.50 | 5 | n/a |
| Graphite Meter Terminal, HTTP/3 | 30/30 | 7070.0 [6670.0, 8432.5] | 7575.0 [7165.0, 8637.5] | 1.04 | 13 | n/a |
| Graphite Meter Browser, firefox | 30/30 | 3493.0 [2795.2, 5364.3] | 5804.2 [4335.5, 12896.3] | 0.27 | 9 | 2.62 |
| iperf3 (reference) | 30/30 | 31445.0 [30430.8, 56265.4] | 44472.2 [42602.7, 85019.7] | 0.20 | 10 | n/a |
| LibreSpeed, chrome | 30/30 | 10228.5 [8440.0, 14438.0] | 4078.5 [2629.0, 9292.0] | 0.31 | 82 | 2.11 |
| LibreSpeed CLI | 30/30 | 28333.3 [25690.2, 48640.8] | 18602.5 [16133.7, 27246.7] | 0.32 | 71 | n/a |
| LibreSpeed, firefox | 30/30 | 2102.0 [1652.3, 3032.3] | 3204.5 [2626.5, 4501.8] | 0.33 | 86 | 5.80 |
| LibreSpeed Go backend, chrome | 30/30 | 9982.0 [8177.8, 14098.8] | 4113.5 [2618.5, 9260.0] | 0.36 | 49 | 2.12 |
| LibreSpeed Go backend, firefox | 30/30 | 2144.0 [1766.3, 3015.8] | 3350.5 [2671.8, 4622.0] | 0.33 | 52 | 5.74 |
| LibreSpeed Rust backend, chrome | 30/30 | 10041.0 [8406.0, 14469.0] | 4051.5 [2594.3, 9131.3] | 0.24 | 23 | 2.14 |
| LibreSpeed Rust backend, firefox | 30/30 | 1992.5 [1690.5, 2964.0] | 3286.0 [2615.8, 4610.8] | 0.24 | 26 | 5.66 |
| OpenSpeedTest, chrome | 30/30 | 9150.5 [7533.3, 13325.5] | 4278.0 [2765.4, 9738.4] | 0.20 | 22 | 2.14 |
| OpenSpeedTest, firefox | 30/30 | 2633.3 [2125.3, 4976.0] | 3154.2 [2645.0, 4521.9] | 0.25 | 21 | 5.69 |
