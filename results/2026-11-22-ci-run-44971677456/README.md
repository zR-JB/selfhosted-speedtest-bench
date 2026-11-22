# GitHub runner benchmark, 22.11.2026

**5,489/5,490** retained runs completed across **15 runner jobs** (0 runs excluded by the busy-host rule).
The 25 and 40 Gbit/s shaped scenarios are skipped on these 4-vCPU runners. They require 8+ CPUs.

[Benchmark source at 7f25fce927cb5e839d53fe3fa09dcf47acce9349](https://github.com/zR-JB/selfhosted-speedtest-bench/tree/7f25fce927cb5e839d53fe3fa09dcf47acce9349) · [Workflow run and raw artifacts](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/44971677456)
[Provenance and exact pins](provenance.json) · [Retained scalar measurements](measurements.json.gz) · [Server CPU by phase](server-cpu.md) · [Bench overview](../../README.md) · [Previous report](../2026-11-15-ci-run-43720854999)

The workflow stores the detailed artifacts and screenshots for its retention window. The scalar archive
keeps the inputs used by the overview charts and tables. Read it with `gzip -dc measurements.json.gz`.
Provenance records the job order, CPU allocation, pinned releases and workload definitions.

To regenerate the overview tables and charts from the committed archive, run
`python3 bench/report.py 44971677456 --from-archive --rerender` from the repository root.
The renderer uses Python 3 with Matplotlib. When this is the latest run, the command also updates
the root README. Regenerating the detailed pass tables requires all 15 job artifacts, Node.js 22 or later,
and the benchmark source revision in local Git history. Use
`python3 bench/report.py 44971677456 /path/to/artifacts --rerender` while they remain available.

## Tested versions

| Tested release | Version |
| --- | ---: |
| Graphite Meter Browser | 0.14.4 |
| Graphite Meter without loaded latency | 0.14.4 |
| LibreSpeed | 6.3.1 |
| LibreSpeed Go backend | 1.1.6 |
| LibreSpeed Rust backend | 1.4.0 |
| OpenSpeedTest | 2.5.4 |
| Graphite Meter Terminal | 0.14.4 |
| Graphite Meter Terminal without loaded latency | 0.14.4 |
| LibreSpeed CLI | 1.0.15 |
| Chrome | 158.0.8127.36 |
| Firefox | 160.0.1 |
| iperf3 (reference) | 3.19.1 |

## Overview data

We take each VM’s median over its retained passes, then summarize across VMs. A VM contributes once,
with up to two passes. Large marks show medians across VMs. Lines span the middle 50%, and small
marks show VM values where plotted. The spreads describe these runners. Sample sizes and exact
values are in the linked tables.

### Shaped throughput

Download / upload medians. Browser rows use Chrome. The loss test uses a 100 Mbit/s link, 1% loss in each direction and 40 ms RTT.

| Tool or client | 1 Gbit/s (Mbit/s) | 10 Gbit/s (Gbit/s) | 1% loss (Mbit/s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 956.3 / 954.4 | **9.56** / 6.27 | 16.5 / 17.1 |
| Graphite Meter without loaded latency · Chrome | 955.7 / **954.6** | **9.56** / **6.33** | 19.5 / 16.8 |
| LibreSpeed · Chrome | **956.5** / 945.0 | 9.51 / 5.11 | 16.8 / 9.4 |
| LibreSpeed Go backend · Chrome | 955.0 / 952.5 | 9.53 / 5.15 | 16.9 / 9.7 |
| LibreSpeed Rust backend · Chrome | 954.5 / 952.5 | 9.54 / 5.10 | 17.0 / 9.9 |
| OpenSpeedTest · Chrome | 953.4 / 953.2 | **9.56** / 5.42 | **19.8** / **22.7** |
| Graphite Meter Terminal | **956.6** / **956.4** | **9.56** / **9.56** | **19.9** / 19.5 |
| Graphite Meter Terminal without loaded latency | 956.5 / **956.4** | **9.56** / **9.56** | 19.8 / **19.7** |
| LibreSpeed CLI | 940.9 / 871.8 | 9.36 / 8.22 | 11.2 / 11.8 |
| iperf3 (reference) | 956.5 / 956.4 | 9.56 / 9.56 | 12.9 / 12.8 |

### 10 Gbit/s upload spread

Each cell shows the median [25th, 75th percentile] and number of VMs. The last column uses matched same-VM, same-pass iperf3 rates. A lower achieved rate can come from any part of the test setup.

Graphite Meter Browser’s same-pass upload difference from OpenSpeedTest in Chrome was **+1.16 Gbit/s** (middle 50% +0.83 to +1.23). Graphite Meter Browser reported more on **15/15 matched VMs**.

| Tool or client | Upload (Gbit/s) | Paired difference from iperf3 (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 6.27 [4.20, 6.79] (n=15) | -34.5 [-56.1, -29.0] (n=15) |
| Graphite Meter without loaded latency · Chrome | 6.33 [4.32, 6.81] (n=15) | -33.8 [-54.9, -28.8] (n=15) |
| LibreSpeed · Chrome | 5.11 [3.40, 5.32] (n=15) | -46.5 [-64.5, -44.3] (n=15) |
| LibreSpeed Go backend · Chrome | 5.15 [3.38, 5.32] (n=15) | -46.2 [-64.6, -44.4] (n=15) |
| LibreSpeed Rust backend · Chrome | 5.10 [3.35, 5.35] (n=15) | -46.7 [-65.0, -44.1] (n=15) |
| OpenSpeedTest · Chrome | 5.42 [3.50, 5.56] (n=15) | -43.4 [-63.5, -41.9] (n=15) |
| Graphite Meter Browser · Firefox | 8.74 [5.37, 9.40] (n=15) | -8.6 [-43.8, -1.8] (n=15) |
| Graphite Meter without loaded latency · Firefox | 9.30 [5.76, 9.52] (n=15) | -2.7 [-39.8, -0.5] (n=15) |
| LibreSpeed · Firefox | 4.12 [3.18, 4.34] (n=15) | -56.9 [-66.7, -54.6] (n=15) |
| LibreSpeed Go backend · Firefox | 4.05 [3.16, 4.30] (n=15) | -57.7 [-66.9, -55.0] (n=15) |
| LibreSpeed Rust backend · Firefox | 3.96 [3.07, 4.32] (n=15) | -58.6 [-67.9, -54.8] (n=15) |
| OpenSpeedTest · Firefox | 4.11 [3.10, 4.37] (n=15) | -57.0 [-67.5, -54.3] (n=15) |
| Graphite Meter Terminal | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| Graphite Meter Terminal without loaded latency | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | 8.22 [8.13, 8.27] (n=15) | -14.1 [-15.0, -13.6] (n=15) |
| iperf3 (reference) | 9.56 [9.56, 9.56] (n=15) | — |

### Matched 1 Gbit/s agreement

Signed percentage differences from iperf3 on the same VM and pass. Each cell shows the median [25th, 75th percentile] and number of VMs after reducing the matched pass differences within each VM. Tests ran sequentially. App and iperf3 start times were a median of 3.6 minutes apart (maximum 10.3).

| Tool or client | Download difference (%) | Upload difference (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | **0.0** [-0.1, 0.0] (n=15) | **-0.2** [-2.1, -0.1] (n=15) |
| Graphite Meter without loaded latency · Chrome | -0.1 [-0.1, 0.0] (n=15) | **-0.2** [-0.4, -0.1] (n=15) |
| LibreSpeed · Chrome | **0.0** [-0.1, +0.1] (n=15) | -1.2 [-1.3, -0.5] (n=15) |
| LibreSpeed Go backend · Chrome | -0.2 [-0.3, +0.1] (n=15) | -0.4 [-0.9, -0.2] (n=15) |
| LibreSpeed Rust backend · Chrome | -0.2 [-0.2, 0.0] (n=15) | -0.4 [-0.7, -0.3] (n=15) |
| OpenSpeedTest · Chrome | -0.3 [-0.5, -0.1] (n=15) | -0.3 [-0.8, -0.1] (n=15) |
| Graphite Meter Browser · Firefox | **-0.1** [-0.2, 0.0] (n=15) | -0.4 [-0.5, -0.1] (n=15) |
| Graphite Meter without loaded latency · Firefox | -0.2 [-0.4, -0.2] (n=15) | **-0.2** [-0.5, -0.1] (n=15) |
| LibreSpeed · Firefox | -1.3 [-3.1, -0.5] (n=15) | -5.6 [-6.6, -4.6] (n=15) |
| LibreSpeed Go backend · Firefox | -1.4 [-2.3, -0.7] (n=15) | -5.3 [-6.0, -4.6] (n=15) |
| LibreSpeed Rust backend · Firefox | -1.2 [-2.6, -0.5] (n=15) | -5.1 [-6.3, -4.3] (n=15) |
| OpenSpeedTest · Firefox | -0.2 [-0.6, -0.1] (n=15) | -0.7 [-0.8, -0.6] (n=15) |
| Graphite Meter Terminal | **0.0** [0.0, +0.1] (n=15) | **0.0** [0.0, 0.0] (n=15) |
| Graphite Meter Terminal without loaded latency | **0.0** [0.0, 0.0] (n=15) | **0.0** [0.0, 0.0] (n=15) |
| LibreSpeed CLI | -1.6 [-2.1, -1.3] (n=15) | -8.8 [-8.9, -8.8] (n=15) |

### Unshaped throughput and client CPU

Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand.
Each maximum is the fastest retained pass in that direction. The two maxima can come from different passes. Client CPU divides browser process-tree CPU (browser rows) or container cgroup CPU (native rows, where recorded) by total shaper GB.

| Tool or client | Median down / up (Gbit/s) | Max down / up (Gbit/s) | Client CPU (s/GB) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | **26.2** / 11.2 | 29.4 / 12.3 | 0.83 |
| Graphite Meter without loaded latency · Chrome | 25.7 / **11.5** | 29.6 / 12.7 | 0.81 |
| LibreSpeed · Chrome | 15.3 / 10.4 | 17.1 / 11.3 | 1.18 |
| LibreSpeed Go backend · Chrome | 15.2 / 10.3 | 16.9 / 11.2 | 1.18 |
| LibreSpeed Rust backend · Chrome | 15.2 / 10.7 | 16.8 / 11.2 | 1.18 |
| OpenSpeedTest · Chrome | 14.8 / 10.9 | 17.2 / 11.9 | 1.12 |
| Graphite Meter Browser · Firefox | 6.4 / 15.5 | 7.3 / 18.1 | 1.28 |
| Graphite Meter without loaded latency · Firefox | **7.9** / **16.6** | 8.7 / 18.7 | 1.13 |
| LibreSpeed · Firefox | 3.1 / 4.8 | 3.6 / 5.5 | 3.57 |
| LibreSpeed Go backend · Firefox | 3.2 / 4.7 | 3.6 / 5.6 | 3.57 |
| LibreSpeed Rust backend · Firefox | 3.1 / 4.7 | 3.5 / 5.7 | 3.55 |
| OpenSpeedTest · Firefox | 5.5 / 4.7 | 6.2 / 5.4 | 3.00 |
| Graphite Meter Terminal | 79.4 / **168.7** | 81.4 / 176.1 | 0.09 |
| Graphite Meter Terminal without loaded latency | **79.9** / 168.6 | 82.0 / 176.0 | 0.09 |
| LibreSpeed CLI | 49.4 / 26.6 | 53.6 / 28.4 | 0.25 |
| iperf3 (reference) | 61.4 / 88.1 | 63.6 / 98.7 | 0.13 |

#### Unshaped native upload by runner hardware

Upload medians in Gbit/s. “GM above iperf3” counts VMs after matching same-pass comparisons. CPU, kernel and runner conditions vary together. Groups with one VM show that VM’s median.

Graphite Meter Terminal had a higher upload rate than iperf3 on **15 of 15 VMs** after matching passes. The split was 8/8 on AWS-kernel VMs, 7/7 on Azure-kernel VMs.

| CPU and kernel | VMs | Graphite Meter Terminal | Graphite Meter Terminal without loaded latency | LibreSpeed CLI | iperf3 | GM above iperf3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AMD EPYC 7763 64-Core Processor (7.0.0-1017-azure) | 2 | 55.4 | 55.2 | 15.9 | 41.6 | 2/2 |
| AMD EPYC 9V45 96-Core Processor (7.0.0-1017-azure) | 2 | 97.7 | 97.8 | 27.0 | 77.4 | 2/2 |
| AMD EPYC 9V74 80-Core Processor (7.0.0-1017-azure) | 2 | 75.9 | 75.8 | 18.6 | 43.4 | 2/2 |
| INTEL(R) XEON(R) PLATINUM 8573C (7.0.0-1017-azure) | 1 | 76.7 | 76.5 | 22.9 | 56.3 | 1/1 |
| Intel(R) Xeon(R) 6975P-C (7.0.0-1014-aws) | 8 | 174.0 | 173.3 | 27.3 | 95.5 | 8/8 |

### Server resources at 1 Gbit/s

Server CPU is container CPU time per decimal GB of server-interface traffic during each phase (counting both directions), or total container CPU per shaper GB on unshaped. Peak memory is per-run container memory.peak in decimal MB. Client CPU divides browser process-tree CPU (browser rows) or container cgroup CPU (native rows) by shaper GB.

| Tool or client | Down / up (Mbit/s) | Down CPU (s/GB) | Up CPU (s/GB) | Peak RAM (MB) |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 956.3 / 954.4 | 0.293 | **1.794** | **17.3** |
| Graphite Meter without loaded latency · Chrome | 955.7 / 954.6 | 0.290 | 1.885 | 18.6 |
| LibreSpeed · Chrome | 956.5 / 945.0 | 0.442 | 6.277 | 79.9 |
| LibreSpeed Go backend · Chrome | 955.0 / 952.5 | 0.397 | 5.718 | 48.2 |
| LibreSpeed Rust backend · Chrome | 954.5 / 952.5 | 0.365 | 4.284 | 22.5 |
| OpenSpeedTest · Chrome | 953.4 / 953.2 | **0.167** | 3.655 | 29.3 |
| Graphite Meter Terminal | 956.6 / 956.4 | 0.132 | 1.399 | 18.1 |
| Graphite Meter Terminal without loaded latency | 956.5 / 956.4 | **0.116** | **1.346** | **17.7** |
| LibreSpeed CLI | 940.9 / 871.8 | 0.287 | 2.375 | 68.7 |
| iperf3 (reference) | 956.5 / 956.4 | 0.199 | 5.278 | 19.2 |
| Graphite Meter Browser · Firefox | 955.6 / 952.9 | 0.288 | 2.365 | **17.5** |
| Graphite Meter without loaded latency · Firefox | 954.3 / 954.3 | 0.257 | **2.248** | 19.0 |
| LibreSpeed · Firefox | 944.5 / 902.5 | 0.485 | 5.700 | 85.6 |
| LibreSpeed Go backend · Firefox | 942.5 / 906.0 | 0.478 | 5.362 | 51.9 |
| LibreSpeed Rust backend · Firefox | 945.0 / 907.0 | 0.438 | 3.745 | 26.4 |
| OpenSpeedTest · Firefox | 954.8 / 949.5 | **0.189** | 4.700 | 29.4 |

Absolute server CPU time for the complete 1 Gbit/s test and each transfer phase.

| Tool or client | Download (CPU s) | Upload (CPU s) | Test total (CPU s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.18 | 1.10 | 1.27 |
| Graphite Meter without loaded latency · Chrome | 0.20 | 1.08 | 1.27 |
| LibreSpeed · Chrome | 0.37 | 6.34 | 6.80 |
| LibreSpeed Go backend · Chrome | 0.34 | 5.89 | 6.22 |
| LibreSpeed Rust backend · Chrome | 0.31 | 4.38 | 4.74 |
| OpenSpeedTest · Chrome | 0.31 | 5.64 | 5.94 |
| Graphite Meter Terminal | 0.18 | 2.02 | 2.22 |
| Graphite Meter Terminal without loaded latency | 0.16 | 1.95 | 2.10 |
| LibreSpeed CLI | 0.56 | 4.29 | 4.94 |
| iperf3 (reference) | 0.30 | 7.99 | 8.30 |
| Graphite Meter Browser · Firefox | 0.25 | 1.75 | 2.07 |
| Graphite Meter without loaded latency · Firefox | 0.24 | 1.77 | 2.07 |
| LibreSpeed · Firefox | 0.40 | 5.38 | 5.83 |
| LibreSpeed Go backend · Firefox | 0.39 | 5.00 | 5.42 |
| LibreSpeed Rust backend · Firefox | 0.36 | 3.49 | 3.88 |
| OpenSpeedTest · Firefox | 0.34 | 7.14 | 7.46 |

### Graphite Meter without loaded latency

Within each client, both profiles use the same server build, automatic connection settings, and transfer durations. The variant skips the app’s idle-latency stage and loaded probes. Each cell is **without loaded latency minus default** on the same VM and pass, summarized across VMs as median [middle 50%]. Total server CPU includes the skipped idle stage.

| Path | Client | Download (Mbit/s) | Upload (Mbit/s) | Download server CPU (s/GB) | Upload server CPU (s/GB) | Total server CPU (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 Gbit/s | Chrome | -0.6 [-1.1, -0.1] (n=15) | +1.4 [+0.1, +6.0] (n=15) | -0.011 [-0.047, +0.020] (n=15) | +0.015 [-0.018, +0.298] (n=15) | -0.03 [-0.11, +0.11] (n=15) |
| 1 Gbit/s | Firefox | -1.3 [-2.1, +0.3] (n=15) | +1.7 [-0.4, +2.7] (n=15) | -0.029 [-0.080, +0.008] (n=15) | -0.099 [-0.181, -0.023] (n=15) | -0.10 [-0.44, +0.29] (n=15) |
| 1 Gbit/s | Terminal | -0.1 [-0.2, 0.0] (n=15) | 0.0 [-0.2, +0.2] (n=15) | -0.014 [-0.024, +0.003] (n=15) | -0.001 [-0.028, +0.024] (n=15) | -0.03 [-0.09, +0.02] (n=15) |
| 10 Gbit/s | Terminal | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | 0.000 [0.000, 0.000] (n=15) | 0.000 [-0.004, +0.001] (n=15) | -0.05 [-0.11, -0.01] (n=15) |
| Unshaped | Terminal | +90.0 [-140.0, +472.5] (n=15) | -160.0 [-700.0, +17.5] (n=15) | 0.000 [-0.001, +0.001] (n=15) | 0.000 [0.000, 0.000] (n=15) | -0.07 [-0.10, -0.06] (n=15) |

### Upload counter checks

All rates are in Mbit/s. The shaper reports the median over busy intervals, includes protocol
overhead and can show rates above the configured limit even for iperf3. “Above iperf3” counts passes
where the tool reported a higher rate than the same-VM, same-pass iperf3 receiver. Each VM runs
its two passes sequentially. The separate receiver smoke used the 1 Gbit/s path only.
Server RX averages traffic during sustained upload intervals and shows the median, middle 50% and
number of VMs when available. Like the shaper, it includes protocol overhead and uses a separate
timing window. A payload accounting check would require matching bytes and timing to the app.

**1 Gbit/s path**

| Tool or client | App rate | Shaper | Server RX | Above iperf3 |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 954.4 | 1,024.5 | 941.2 [930.9, 946.0] (n=15) | 2/30 |
| Graphite Meter without loaded latency · Chrome | 954.6 | 1,023.9 | 938.2 [932.1, 942.8] (n=15) | 3/30 |
| LibreSpeed · Chrome | 945.0 | 1,011.8 | 955.8 [945.3, 958.3] (n=15) | 3/30 |
| LibreSpeed Go backend · Chrome | 952.5 | 1,009.3 | 953.6 [947.4, 959.3] (n=15) | 5/30 |
| LibreSpeed Rust backend · Chrome | 952.5 | 1,017.2 | 953.4 [943.2, 959.4] (n=15) | 8/30 |
| OpenSpeedTest · Chrome | 953.2 | 1,024.7 | 973.2 [964.7, 975.0] (n=15) | 8/30 |
| Graphite Meter Browser · Firefox | 952.9 | 1,024.6 | 943.2 [937.1, 951.2] (n=15) | 4/30 |
| Graphite Meter without loaded latency · Firefox | 954.3 | 1,024.5 | 946.6 [942.9, 949.6] (n=15) | 1/30 |
| LibreSpeed · Firefox | 902.5 | 961.9 | 907.9 [903.6, 914.4] (n=15) | 0/30 |
| LibreSpeed Go backend · Firefox | 906.0 | 962.4 | 911.0 [897.5, 914.9] (n=15) | 0/30 |
| LibreSpeed Rust backend · Firefox | 907.0 | 958.7 | 903.0 [898.5, 916.7] (n=15) | 0/30 |
| OpenSpeedTest · Firefox | 949.5 | 1,025.6 | 961.1 [958.2, 964.5] (n=15) | 0/30 |
| Graphite Meter Terminal | 956.4 | 1,025.2 | 978.9 [978.1, 980.2] (n=15) | 15/30 |
| Graphite Meter Terminal without loaded latency | 956.4 | 1,025.2 | 985.4 [981.7, 986.6] (n=15) | 19/30 |
| LibreSpeed CLI | 871.8 | 1,016.6 | 937.3 [930.1, 940.8] (n=15) | 0/30 |
| iperf3 (reference) | 956.4 | 1,024.9 | 981.4 [979.8, 984.5] (n=15) | — |

**30 Mbit/s upload, deep FIFO**

| Tool or client | App rate | Shaper | Server RX | Above iperf3 |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 28.7 | 30.9 | 29.4 [29.4, 29.4] (n=15) | 11/30 |
| Graphite Meter without loaded latency · Chrome | 28.7 | 30.9 | 29.4 [29.4, 29.5] (n=15) | 17/30 |
| LibreSpeed · Chrome | 29.8 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 27/30 |
| LibreSpeed Go backend · Chrome | 29.2 | 30.9 | 29.8 [29.8, 29.9] (n=15) | 23/30 |
| LibreSpeed Rust backend · Chrome | 28.9 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 16/30 |
| OpenSpeedTest · Chrome | 31.6 | 30.9 | 29.7 [29.6, 29.7] (n=15) | 30/30 |
| Graphite Meter Browser · Firefox | 28.7 | 30.9 | 29.4 [29.4, 29.4] (n=15) | 18/30 |
| Graphite Meter without loaded latency · Firefox | 28.7 | 30.9 | 29.4 [29.4, 29.4] (n=15) | 17/30 |
| LibreSpeed · Firefox | 29.3 | 30.9 | 29.8 [29.8, 29.9] (n=15) | 24/30 |
| LibreSpeed Go backend · Firefox | 29.0 | 30.9 | 29.8 [29.7, 29.9] (n=15) | 19/30 |
| LibreSpeed Rust backend · Firefox | 28.9 | 30.8 | 29.8 [29.8, 29.8] (n=15) | 21/30 |
| OpenSpeedTest · Firefox | 31.0 | 30.9 | 29.7 [29.7, 29.8] (n=15) | 30/30 |
| Graphite Meter Terminal | 28.7 | 30.9 | 29.5 [29.4, 29.6] (n=15) | 16/30 |
| Graphite Meter Terminal without loaded latency | 28.7 | 30.9 | 29.6 [29.6, 29.7] (n=15) | 13/30 |
| LibreSpeed CLI | 29.3 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 29/30 |
| iperf3 (reference) | 28.7 | 30.9 | 29.8 [29.7, 29.8] (n=15) | — |

### Idle latency against ICMP

The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference.
Each cell shows the median paired difference in ms [25th, 75th percentile] and number of VMs.

| Tool or client | 20 ms path | 40 ms path | 160 ms path |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | +0.3 [+0.2, +0.3] (n=15) | +0.3 [+0.3, +0.4] (n=15) | +0.4 [+0.3, +0.5] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — | — |
| LibreSpeed · Chrome | +0.1 [+0.1, +0.2] (n=15) | +0.2 [+0.1, +0.2] (n=15) | -0.1 [-0.1, -0.1] (n=15) |
| LibreSpeed Go backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed Rust backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| OpenSpeedTest · Chrome | -0.1 [-0.1, +0.4] (n=15) | -0.1 [-0.1, +0.4] (n=15) | +0.4 [+0.1, +0.8] (n=15) |
| Graphite Meter Browser · Firefox | +0.9 [+0.9, +0.9] (n=15) | +0.9 [+0.9, +1.4] (n=15) | +0.9 [+0.8, +0.9] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — | — |
| LibreSpeed · Firefox | +1.4 [+0.9, +1.4] (n=15) | +1.3 [+0.9, +1.4] (n=15) | +1.8 [+0.9, +1.8] (n=15) |
| LibreSpeed Go backend · Firefox | +0.9 [+0.9, +0.9] (n=15) | +0.9 [+0.9, +1.3] (n=15) | +0.9 [+0.9, +1.6] (n=15) |
| LibreSpeed Rust backend · Firefox | +0.9 [+0.9, +1.2] (n=15) | +0.9 [+0.9, +1.1] (n=15) | +1.4 [+1.1, +1.6] (n=15) |
| OpenSpeedTest · Firefox | -0.1 [-0.1, -0.1] (n=15) | +0.4 [+0.4, +0.9] (n=15) | +0.4 [+0.4, +0.8] (n=15) |
| Graphite Meter Terminal | +0.1 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| Graphite Meter Terminal without loaded latency | — | — | — |
| LibreSpeed CLI | +0.1 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) |

### Latency under load on a FIFO

Each cell shows the app’s reported latency followed by the queue-based estimate, in ms.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 165.3 / 157.6 | 190.4 / 185.9 |
| Graphite Meter without loaded latency · Chrome | — / 165.5 | — / 181.8 |
| Graphite Meter Browser · Firefox | 163.5 / 156.0 | 186.0 / 180.5 |
| Graphite Meter without loaded latency · Firefox | — / 171.9 | — / 181.0 |
| Graphite Meter Terminal | 180.0 / 172.6 | 198.0 / 193.5 |
| Graphite Meter Terminal without loaded latency | — / 173.1 | — / 192.6 |

Paired app minus queue estimate in ms, summarized within VMs, then across VMs.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | +5.5 [+4.1, +9.1] (n=15) | +4.1 [+2.7, +5.1] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — |
| Graphite Meter Browser · Firefox | +7.5 [+6.1, +11.1] (n=15) | +4.2 [+3.2, +6.1] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — |
| Graphite Meter Terminal | +4.8 [+4.2, +5.6] (n=15) | +4.2 [+3.7, +6.6] (n=15) |
| Graphite Meter Terminal without loaded latency | — | — |

## Pooled pass tables

The tables below pool all retained completed passes for each configuration, including alternate
transports. Their comparison columns show the difference from the modeled TCP payload ceiling
when iperf3 reaches at least 98% of the model in both directions. QUIC rows show measured rates separately.
The matched comparison above uses the measured same-pass receiver rate.
Below-ceiling rates can reflect any constraint on the end-to-end transfer.

[100 Mbit/s](#100100-mbits-20-ms-rtt-fq_codel) · [1 Gbit/s](#11-gbits-20-ms-rtt-fq_codel) · [10 Gbit/s](#1010-gbits-2-ms-rtt-fq_codel-offloads-on) · [Deep FIFO](#30030-mbits-20-ms-rtt-200-ms-fifo) · [1% loss](#100100-mbits-40-ms-rtt-1--loss-each-way-fq_codel) · [0.1% loss](#11-gbits-40-ms-rtt-01--loss-each-way-fq_codel) · [160 ms RTT](#300300-mbits-160-ms-rtt-fq_codel) · [Competing traffic](#100100-mbits-20-ms-rtt-fq_codel-one-competing-flow-each-way) · [Reverse proxy](#11-gbits-20-ms-rtt-fq_codel-behind-nginx) · [Two servers](#two-servers-200200-mbits-path-each-20-ms-rtt-fq_codel) · [Unshaped](#unshaped-offloads-on-as-fast-as-the-host-allows)

<!-- pooled-pass-tables -->
Jobs: 15. Runs: 5490, of which 0 left out from blocks on a busy host. Hosts: AMD EPYC 9V45 96-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); Intel(R) Xeon(R) 6975P-C (4 CPUs, kernel 7.0.0-1014-aws, rootful); AMD EPYC 9V74 80-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 7763 64-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); INTEL(R) XEON(R) PLATINUM 8573C (4 CPUs, kernel 7.0.0-1017-azure, rootful).
Tools: Graphite Meter 0.14.4, LibreSpeed 6.3.1, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest 2.5.4, Graphite Meter terminal client 0.14.4, LibreSpeed CLI 1.0.15. Browsers: chrome 158.0.8127.36, firefox 160.0.1.

## 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.5, 95.6] | -0.0 % | 20.4 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.6, 95.6] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.6, 95.6] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | +0.0 % | 95.6 [95.5, 95.6] | -0.1 % | 21.0 (20.1) | 21.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 95.7 [95.6, 95.7] | +0.0 % | 95.6 [95.5, 95.6] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | +0.0 % | 95.6 [95.5, 95.6] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.5, 95.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.2 [95.2, 95.3] | -0.5 % | 96.1 [95.9, 96.6] | +0.5 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.8 [94.7, 94.8] | -0.9 % | 91.4 [91.4, 92.5] | -4.4 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.4 [95.3, 95.5] | -0.3 % | 95.5 [95.0, 96.1] | -0.1 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.7 [95.3, 95.7] | +0.1 % | 95.3 [94.7, 95.8] | -0.3 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.1 [95.0, 95.3] | -0.6 % | 95.8 [95.1, 96.5] | +0.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.3, 95.7] | -0.4 % | 95.1 [94.8, 96.1] | -0.6 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.3 [95.2, 95.4] | -0.4 % | 95.2 [94.6, 96.0] | -0.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.4 [95.4, 95.6] | -0.3 % | 95.8 [95.2, 96.5] | +0.1 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.5 [95.5, 95.7] | -0.1 % | 96.0 [95.7, 96.4] | +0.4 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.4 [955.9, 956.5] | -0.0 % | 954.1 [937.0, 955.5] | -0.2 % | 20.4 (20.1) | 20.8 (n/a) | 20.6 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 956.4 [956.4, 957.0] | -0.0 % | 956.4 [956.4, 956.4] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 953.2 [953.2, 953.2] | -0.3 % | 953.2 [953.1, 953.2] | -0.3 % | 20.2 (20.1) | 20.3 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 937.9 [937.7, 938.1] | n/a | 948.7 [948.7, 948.8] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 956.4 [956.4, 956.6] | -0.0 % | 956.4 [956.4, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 955.5 [954.5, 956.2] | -0.1 % | 954.2 [950.2, 955.9] | -0.2 % | 21.0 (20.1) | 28.0 (n/a) | 22.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 950.8 [950.7, 951.0] | -0.6 % | 945.4 [937.3, 948.5] | -1.2 % | 20.4 (20.1) | 21.6 (n/a) | 22.6 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 947.4 [945.7, 949.9] | n/a | 811.6 [727.7, 848.7] | n/a | 20.4 (20.1) | 20.4 (n/a) | 21.6 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 955.8 [955.0, 956.3] | -0.1 % | 954.6 [952.4, 956.0] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 953.9 [952.3, 955.9] | -0.3 % | 954.6 [951.0, 955.6] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 944.4 [940.3, 951.5] | n/a | 777.3 [684.8, 827.2] | n/a | 20.5 (20.1) | 20.4 (n/a) | 21.4 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.4 [956.4, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 957.0 [955.0, 958.8] | +0.1 % | 948.0 [941.3, 952.0] | -0.9 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 942.8 [937.9, 944.2] | -1.4 % | 871.8 [871.0, 872.4] | -8.8 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 944.0 [927.5, 952.0] | -1.3 % | 901.5 [897.0, 909.8] | -5.7 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 955.0 [952.3, 957.0] | -0.1 % | 952.0 [946.3, 955.0] | -0.5 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 943.5 [932.3, 952.8] | -1.3 % | 907.0 [899.5, 913.0] | -5.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 944.5 [943.0, 948.0] | -1.2 % | 414.0 [412.3, 415.8] | -56.7 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 954.0 [953.0, 956.0] | -0.3 % | 951.5 [947.3, 956.5] | -0.5 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 944.5 [931.3, 956.0] | -1.2 % | 905.5 [897.0, 914.3] | -5.3 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 953.5 [950.3, 955.8] | -0.3 % | 953.0 [949.5, 957.1] | -0.4 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 954.5 [949.4, 955.6] | -0.2 % | 950.1 [946.4, 951.9] | -0.7 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 948.8 [947.3, 952.3] | -0.8 % | 936.0 [933.5, 941.7] | -2.1 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 9563.0 [9560.7, 9563.8] | -0.0 % | 6221.9 [4194.6, 6749.3] | -34.9 % | 2.2 (2.1) | 2.5 (n/a) | 3.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.1 (n/a) | 2.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 9530.0 [9530.0, 9530.0] | -0.4 % | 9530.0 [9530.0, 9530.0] | -0.4 % | 2.1 (2.1) | 5.6 (n/a) | 2.3 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 6780.0 [6430.0, 7127.5] | n/a | 7500.0 [6185.0, 7637.5] | n/a | 2.1 (2.1) | 3.2 (n/a) | 2.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 5898.0 [3818.9, 6250.4] | -38.3 % | 8683.2 [5298.9, 9419.5] | -9.2 % | 3.0 (2.1) | 14.0 (n/a) | 42.8 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 6980.9 [5360.3, 7082.2] | -27.0 % | 4674.4 [2785.5, 4834.4] | -51.1 % | 2.2 (2.1) | 3.3 (n/a) | 2.8 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 2521.8 [1910.3, 2620.2] | n/a | 1525.2 [800.4, 1565.9] | n/a | 2.2 (2.1) | 2.4 (n/a) | 4.5 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 9562.6 [9560.5, 9563.3] | -0.0 % | 6222.2 [4314.5, 6848.7] | -34.9 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 6738.8 [4651.0, 7288.8] | -29.5 % | 9208.6 [5690.0, 9519.0] | -3.7 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 2494.3 [1932.6, 2596.7] | n/a | 1195.1 [725.4, 1231.5] | n/a | 2.2 (2.1) | 2.5 (n/a) | 3.1 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.3 [9564.2, 9564.3] | +0.0 % | 9564.3 [9564.3, 9564.4] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 9534.0 [9341.8, 9568.3] | -0.3 % | 5114.0 [3336.3, 5315.8] | -46.5 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9355.7 [9355.2, 9356.5] | -2.2 % | 8211.8 [8119.2, 8270.3] | -14.1 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 3112.5 [2321.0, 3499.8] | -67.5 % | 4117.5 [3180.3, 4307.8] | -56.9 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 9534.0 [9255.0, 9567.3] | -0.3 % | 5114.0 [3331.3, 5324.0] | -46.5 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 3343.5 [2237.8, 3438.0] | -65.0 % | 4045.5 [3147.5, 4258.8] | -57.7 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 4416.0 [4059.0, 4502.8] | -53.8 % | 3327.5 [2585.3, 3374.3] | -65.2 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 9536.0 [9362.3, 9564.8] | -0.3 % | 5098.0 [3298.5, 5355.8] | -46.7 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 3195.0 [2256.0, 3461.0] | -66.6 % | 4027.0 [3078.3, 4180.0] | -57.9 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 9558.9 [9508.5, 9568.0] | -0.1 % | 5386.5 [3433.8, 5526.5] | -43.7 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 29/30 | payload | 5496.0 [2780.8, 5727.7] | -42.5 % | 4108.7 [3081.3, 4373.0] | -57.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 5683.2 [4388.9, 5990.3] | -40.6 % | 4076.6 [2614.8, 4245.5] | -57.4 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

- OpenSpeedTest, firefox, rep 1: harness-error: Error: timed out waiting for: document.getElementById("oDoLiveStatus")?.textContent.trim() === "All done"

## 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.4 (20.1) | 159.5 (146.0) | 190.9 (185.6) |
| Graphite Meter Terminal | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.2 (20.1) | 177.5 (174.0) | 198.0 (192.5) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.0 % | n/a (20.1) | n/a (171.0) | n/a (192.2) |
| Graphite Meter Browser, firefox | 30/30 | payload | 286.9 [286.8, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 21.0 (20.1) | 183.0 (175.5) | 187.0 (181.6) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 286.9 [286.9, 287.0] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (178.7) | n/a (179.6) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (175.6) | n/a (180.9) |
| iperf3 (reference) | 30/30 | payload | 286.9 [286.9, 287.0] | -0.0 % | 28.7 [28.6, 28.7] | -0.1 % | n/a (20.1) | n/a (176.8) | n/a (187.4) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [283.3, 287.0] | -0.3 % | 30.0 [29.4, 30.0] | +4.6 % | 20.3 (20.1) | n/a (165.1) | n/a (186.1) |
| LibreSpeed CLI | 30/30 | payload | 283.0 [281.8, 283.5] | -1.4 % | 29.0 [29.0, 29.6] | +1.2 % | 20.2 (20.1) | n/a (171.3) | n/a (173.3) |
| LibreSpeed, firefox | 30/30 | payload | 286.0 [283.0, 287.0] | -0.3 % | 29.3 [28.8, 29.6] | +2.1 % | 21.0 (20.1) | n/a (163.5) | n/a (186.3) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 29.2 [28.7, 29.7] | +1.8 % | 20.1 (20.1) | n/a (164.9) | n/a (169.2) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 285.0 [283.3, 286.0] | -0.7 % | 29.3 [28.5, 29.4] | +2.1 % | 21.0 (20.1) | n/a (160.5) | n/a (185.7) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 286.0 [286.0, 286.8] | -0.3 % | 28.7 [28.3, 29.7] | +0.0 % | 20.1 (20.1) | n/a (160.0) | n/a (170.6) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 286.0 [285.3, 287.0] | -0.3 % | 28.9 [28.5, 29.3] | +0.7 % | 21.0 (20.1) | n/a (156.5) | n/a (187.5) |
| OpenSpeedTest, chrome | 30/30 | payload | 286.5 [285.7, 287.3] | -0.1 % | 31.6 [30.6, 31.8] | +10.1 % | 20.0 (20.1) | n/a (156.2) | n/a (196.1) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.6 [285.7, 287.1] | -0.1 % | 30.5 [30.0, 31.6] | +6.3 % | 20.0 (20.1) | n/a (169.8) | n/a (197.4) |

## 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 16.5 [16.0, 17.0] | n/a | 17.1 [16.4, 18.1] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 19.8 [19.5, 20.4] | n/a | 19.4 [18.9, 20.0] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 19.8 [19.3, 20.4] | n/a | 19.9 [19.1, 20.6] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 16.6 [16.2, 17.0] | n/a | 18.3 [17.6, 18.9] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 19.5 [18.9, 20.2] | n/a | 16.8 [16.5, 17.3] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 19.9 [19.0, 20.6] | n/a | 18.0 [17.4, 19.0] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 13.0 [12.5, 13.7] | n/a | 13.0 [12.4, 13.3] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 16.8 [16.2, 17.4] | n/a | 9.4 [9.1, 9.8] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 11.2 [10.7, 11.6] | n/a | 11.8 [11.1, 12.4] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 20.5 [20.1, 21.3] | n/a | 9.3 [8.9, 9.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 16.8 [16.4, 17.7] | n/a | 9.7 [9.1, 10.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 21.2 [20.1, 22.9] | n/a | 9.6 [8.8, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 17.0 [16.6, 17.6] | n/a | 9.8 [9.0, 10.6] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 20.9 [20.2, 22.1] | n/a | 9.3 [9.0, 9.6] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 19.4 [18.7, 20.1] | n/a | 22.3 [21.1, 23.3] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.6 [18.9, 20.1] | n/a | 21.9 [20.7, 22.8] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 77.1 [70.9, 79.9] | n/a | 83.4 [72.4, 95.8] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 88.4 [81.6, 92.9] | n/a | 88.0 [82.6, 91.3] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 14.1 [11.3, 16.9] | n/a | 14.0 [12.5, 15.2] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.2 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 72.2 [53.7, 108.0] | n/a | 158.9 [126.2, 189.3] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 89.6 [82.5, 96.8] | n/a | 85.5 [81.4, 92.5] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 77.9 [70.6, 80.7] | n/a | 90.4 [80.6, 102.4] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 16.3 [14.5, 18.9] | n/a | 14.5 [13.1, 16.4] | n/a | 40.4 (40.1) | 40.5 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 102.9 [86.3, 143.6] | n/a | 25.7 [22.7, 30.6] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 90.3 [84.8, 95.9] | n/a | 88.6 [80.6, 93.2] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 87.1 [82.6, 95.1] | n/a | 91.2 [81.1, 95.2] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 75.6 [47.5, 104.8] | n/a | 27.6 [24.9, 30.9] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 50.9 [47.4, 53.7] | n/a | 50.7 [49.8, 53.5] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 102.0 [91.6, 121.5] | n/a | 36.0 [33.0, 40.4] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 54.7 [50.5, 61.4] | n/a | 46.5 [44.1, 48.3] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 146.0 [135.3, 170.8] | n/a | 37.2 [34.0, 40.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 96.8 [88.0, 113.3] | n/a | 68.3 [48.1, 85.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 139.0 [131.0, 162.0] | n/a | 38.0 [33.9, 41.8] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 12.0 [10.8, 13.1] | n/a | 12.6 [11.2, 14.8] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 106.0 [88.5, 124.3] | n/a | 55.7 [43.7, 72.8] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 124.5 [108.8, 147.3] | n/a | 37.9 [34.8, 43.0] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 75.2 [72.0, 82.5] | n/a | 91.0 [87.1, 97.0] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 75.8 [71.0, 84.3] | n/a | 93.3 [88.7, 102.8] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 11.0 [9.9, 12.4] | n/a | 14.2 [11.5, 16.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 275.2 [262.4, 282.3] | n/a | 254.9 [248.4, 260.0] | n/a | 160.6 (160.1) | 160.3 (n/a) | 160.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 280.6 [277.4, 283.3] | n/a | 282.3 [279.0, 284.3] | n/a | 160.0 (160.1) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 275.7 [268.9, 278.8] | n/a | 280.9 [278.5, 283.9] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 265.7 [259.4, 279.9] | n/a | 251.6 [247.5, 255.0] | n/a | 161.0 (160.1) | 161.0 (n/a) | 161.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 269.4 [257.1, 278.3] | n/a | 247.3 [244.3, 251.4] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 274.6 [269.4, 284.1] | n/a | 235.5 [232.6, 239.4] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 215.6 [200.7, 231.0] | n/a | 215.7 [203.7, 256.4] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 272.0 [270.0, 275.8] | n/a | 236.5 [222.0, 241.8] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 224.9 [218.8, 234.6] | n/a | 123.1 [122.0, 123.1] | n/a | 160.2 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 274.0 [271.3, 276.0] | n/a | 227.0 [221.0, 239.0] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 270.0 [263.3, 274.0] | n/a | 231.5 [225.3, 237.5] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 273.5 [271.0, 277.0] | n/a | 225.0 [218.3, 233.0] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 271.0 [266.5, 274.8] | n/a | 229.5 [223.0, 237.5] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 276.0 [272.3, 279.0] | n/a | 225.5 [220.5, 231.3] | n/a | 161.5 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 270.9 [268.2, 273.6] | n/a | 275.4 [272.6, 278.8] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 273.3 [267.9, 276.4] | n/a | 273.8 [270.5, 276.7] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |

## 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 78.1 [78.1, 78.2] | n/a | 78.5 [78.4, 78.9] | n/a | 20.4 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 80.3 [80.3, 80.4] | n/a | 80.8 [80.8, 80.8] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.9] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 78.1 [78.0, 78.1] | n/a | 78.5 [78.4, 79.0] | n/a | 21.0 (20.1) | 21.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 80.3 [80.3, 80.4] | n/a | 78.6 [78.5, 79.1] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 80.3 [80.2, 80.3] | n/a | 78.5 [78.4, 79.0] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 74.9 [74.8, 75.0] | n/a | 75.2 [75.1, 75.4] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 70.2 [70.0, 71.3] | n/a | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.4 [69.3, 69.4] | n/a | 69.1 [68.8, 69.4] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.0 [80.0, 80.2] | n/a | 69.9 [69.8, 70.8] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 72.6 [72.5, 72.6] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 79.9 [79.8, 80.0] | n/a | 69.9 [69.8, 71.2] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.8 [77.6, 77.8] | n/a | 72.2 [71.2, 72.6] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.1 [80.0, 80.3] | n/a | 69.9 [69.9, 71.3] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.1 [80.1, 80.2] | n/a | 81.0 [80.7, 81.4] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.3 [80.2, 80.4] | n/a | 80.7 [80.6, 80.9] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. iperf3 bypasses nginx and measures the direct shaped path as a control. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.2 [954.3, 956.4] | -0.0 % | 955.2 [953.9, 956.2] | -0.1 % | 20.4 (20.1) | 21.3 (n/a) | 22.8 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 954.0 [948.6, 955.8] | -0.2 % | 955.3 [953.8, 956.5] | -0.1 % | 21.0 (20.1) | 34.0 (n/a) | 25.5 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 955.8 [953.5, 956.3] | -0.1 % | 955.6 [953.2, 956.2] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 955.3 [947.6, 956.1] | -0.1 % | 956.2 [955.7, 956.7] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.4 [956.2, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 954.0 [951.0, 957.0] | -0.3 % | 914.0 [904.3, 924.8] | -4.4 % | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 946.5 [918.0, 953.8] | -1.0 % | 866.5 [847.5, 878.5] | -9.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.2 [950.5, 953.6] | -0.4 % | 925.0 [921.2, 928.7] | -3.3 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 953.4 [951.3, 953.9] | -0.3 % | 910.0 [900.0, 918.1] | -4.9 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |

## Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 382.5 [382.3, 382.6] | -0.0 % | 20.4 (20.1) | 20.6 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | 20.2 (20.1) | 20.3 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.6] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 382.6 [382.5, 382.6] | -0.0 % | 382.1 [382.0, 382.4] | -0.1 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 382.3 [382.2, 382.6] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.7 [381.5, 382.0] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.5 [382.5, 382.5] | -0.0 % | 382.6 [382.5, 382.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

## Unshaped, offloads on: as fast as the host allows

Unshaped single-test throughput on the runner’s virtual link. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Client CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | 26038.9 [14935.4, 28252.3] | 11193.0 [5218.1, 12007.2] | 0.17 | 9 | 0.84 |
| Graphite Meter Terminal | 30/30 | 79330.0 [43137.5, 80852.5] | 168650.0 [76090.0, 174350.0] | 0.06 | 9 | 0.09 |
| Graphite Meter Terminal, HTTP/2 | 30/30 | 15310.0 [14392.5, 18320.0] | 17540.0 [16785.0, 18442.5] | 0.44 | 5 | 0.40 |
| Graphite Meter Terminal, HTTP/3 | 30/30 | 8370.0 [7967.5, 8800.0] | 7500.0 [7407.5, 9247.5] | 0.91 | 8 | 0.91 |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | 79445.0 [43045.0, 81187.5] | 168650.0 [76212.5, 173425.0] | 0.06 | 12 | 0.09 |
| Graphite Meter Browser, firefox | 30/30 | 6276.0 [4312.0, 7006.7] | 14446.1 [6586.8, 17320.3] | 0.16 | 9 | 1.33 |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | 25455.4 [14382.9, 27227.7] | 11474.7 [5470.0, 12199.9] | 0.17 | 10 | 0.81 |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | 7654.6 [5283.2, 8257.7] | 16575.8 [7087.4, 18174.1] | 0.16 | 11 | 1.13 |
| iperf3 (reference) | 30/30 | 61372.7 [32793.8, 63042.8] | 88110.4 [46976.9, 95200.1] | 0.11 | 32 | 0.13 |
| LibreSpeed, chrome | 30/30 | 14929.5 [10278.3, 16072.8] | 10422.0 [4379.8, 11034.0] | 0.28 | 82 | 1.18 |
| LibreSpeed CLI | 30/30 | 48607.6 [30521.6, 50156.8] | 26723.7 [19785.5, 27564.1] | 0.20 | 73 | 0.25 |
| LibreSpeed, firefox | 30/30 | 3063.5 [2084.8, 3247.3] | 4790.0 [3386.8, 5065.3] | 0.26 | 87 | 3.58 |
| LibreSpeed Go backend, chrome | 30/30 | 14830.5 [10540.5, 15965.0] | 10340.5 [4380.3, 11059.3] | 0.30 | 49 | 1.19 |
| LibreSpeed Go backend, firefox | 30/30 | 3059.5 [2192.8, 3375.0] | 4689.0 [3439.8, 5114.8] | 0.26 | 52 | 3.57 |
| LibreSpeed Rust backend, chrome | 30/30 | 14763.5 [10492.8, 15837.5] | 10663.5 [4342.3, 11091.5] | 0.23 | 23 | 1.19 |
| LibreSpeed Rust backend, firefox | 30/30 | 3113.0 [2168.8, 3344.0] | 4576.0 [3410.5, 5031.0] | 0.20 | 26 | 3.69 |
| OpenSpeedTest, chrome | 30/30 | 14252.8 [10055.2, 15861.0] | 10948.8 [4500.6, 11658.6] | 0.16 | 23 | 1.14 |
| OpenSpeedTest, firefox | 30/30 | 5192.1 [2731.1, 5824.7] | 4722.1 [3328.5, 5083.5] | 0.16 | 20 | 3.16 |
