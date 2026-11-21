# GitHub runner benchmark, 15.11.2026

**5,490/5,490** retained runs completed across **15 runner jobs** (0 runs excluded by the busy-host rule).
The 25 and 40 Gbit/s shaped scenarios are skipped on these 4-vCPU runners. They require 8+ CPUs.

[Benchmark source at dfc3d934b77f3ee96839225c1060fa53b1e71183](https://github.com/zR-JB/selfhosted-speedtest-bench/tree/dfc3d934b77f3ee96839225c1060fa53b1e71183) · [Workflow run and raw artifacts](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/43720854999)
[Provenance and exact pins](provenance.json) · [Retained scalar measurements](measurements.json.gz) · [Server CPU by phase](server-cpu.md) · [Bench overview](../../README.md) · [Previous report](../2026-11-15-ci-run-43694138029)

The workflow stores the detailed artifacts and screenshots for its retention window. The scalar archive
keeps the inputs used by the overview charts and tables. Read it with `gzip -dc measurements.json.gz`.
Provenance records the job order, CPU allocation, pinned releases and workload definitions.

To regenerate the overview tables and charts from the committed archive, run
`python3 bench/report.py 43720854999 --from-archive --rerender` from the repository root.
The renderer uses Python 3 with Matplotlib. When this is the latest run, the command also updates
the root README. Regenerating the detailed pass tables requires all 15 job artifacts, Node.js 22 or later,
and the benchmark source revision in local Git history. Use
`python3 bench/report.py 43720854999 /path/to/artifacts --rerender` while they remain available.

## Tested versions

| Tested release | Version |
| --- | ---: |
| Graphite Meter Browser | 0.14.3 |
| Graphite Meter without loaded latency | 0.14.3 |
| LibreSpeed | 6.3.1 |
| LibreSpeed Go backend | 1.1.6 |
| LibreSpeed Rust backend | 1.4.0 |
| OpenSpeedTest | 2.5.4 |
| Graphite Meter Terminal | 0.14.3 |
| Graphite Meter Terminal without loaded latency | 0.14.3 |
| LibreSpeed CLI | 1.0.14 |
| Chrome | 157.0.8103.78 |
| Firefox | 160.0 |
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
| Graphite Meter Browser | **956.2** / 954.1 | **9.56** / 4.29 | 13.2 / 13.8 |
| Graphite Meter without loaded latency | 955.4 / 954.2 | **9.56** / **4.42** | 12.9 / 13.9 |
| LibreSpeed | 956.0 / 946.0 | 9.37 / 3.31 | 17.0 / 9.4 |
| LibreSpeed Go backend | 954.5 / 952.0 | 9.35 / 3.34 | 17.0 / 9.4 |
| LibreSpeed Rust backend | 955.5 / 950.5 | 9.50 / 3.21 | 17.1 / 9.6 |
| OpenSpeedTest | 951.3 / **954.7** | 9.41 / 3.39 | **19.3** / **21.4** |
| Graphite Meter Terminal | **956.4** / **956.4** | **9.56** / **9.56** | 19.5 / 19.8 |
| Graphite Meter Terminal without loaded latency | **956.4** / **956.4** | **9.56** / **9.56** | **19.6** / **19.9** |
| LibreSpeed CLI | 943.2 / 871.0 | 9.36 / 8.16 | 11.2 / 11.3 |
| iperf3 (reference) | 956.4 / 956.4 | 9.56 / 9.56 | 12.9 / 12.8 |

### 10 Gbit/s upload spread

Each cell shows the median [25th, 75th percentile] and number of VMs. The last column uses matched same-VM, same-pass iperf3 rates. A lower achieved rate can come from any part of the test setup.

Graphite Meter Browser’s same-pass upload difference from OpenSpeedTest in Chrome was **+0.87 Gbit/s** (middle 50% +0.75 to +0.94). Graphite Meter Browser reported more on **15/15 matched VMs**.

| Tool or client | Upload (Gbit/s) | Paired difference from iperf3 (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 4.29 [4.23, 6.20] (n=15) | -55.1 [-55.8, -35.2] (n=15) |
| Graphite Meter without loaded latency · Chrome | 4.42 [4.36, 6.33] (n=15) | -53.7 [-54.4, -33.8] (n=15) |
| LibreSpeed · Chrome | 3.31 [3.25, 5.20] (n=15) | -65.4 [-66.1, -45.7] (n=15) |
| LibreSpeed Go backend · Chrome | 3.34 [3.26, 5.24] (n=15) | -65.1 [-65.9, -45.3] (n=15) |
| LibreSpeed Rust backend · Chrome | 3.21 [3.18, 5.20] (n=15) | -66.4 [-66.7, -45.6] (n=15) |
| OpenSpeedTest · Chrome | 3.39 [3.29, 5.37] (n=15) | -64.6 [-65.6, -43.8] (n=15) |
| Graphite Meter Browser · Firefox | 5.32 [5.14, 8.72] (n=15) | -44.4 [-46.3, -8.8] (n=15) |
| Graphite Meter without loaded latency · Firefox | 5.71 [5.60, 8.84] (n=15) | -40.3 [-41.5, -7.5] (n=15) |
| LibreSpeed · Firefox | 3.24 [3.08, 4.13] (n=15) | -66.1 [-67.8, -56.8] (n=15) |
| LibreSpeed Go backend · Firefox | 3.19 [3.04, 4.02] (n=15) | -66.6 [-68.2, -57.9] (n=15) |
| LibreSpeed Rust backend · Firefox | 3.11 [3.08, 4.01] (n=15) | -67.5 [-67.8, -58.1] (n=15) |
| OpenSpeedTest · Firefox | 3.11 [2.98, 4.05] (n=15) | -67.5 [-68.8, -57.7] (n=15) |
| Graphite Meter Terminal | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| Graphite Meter Terminal without loaded latency | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | 8.16 [8.10, 8.24] (n=15) | -14.7 [-15.4, -13.9] (n=15) |
| iperf3 (reference) | 9.56 [9.56, 9.56] (n=15) | — |

### Matched 1 Gbit/s agreement

Signed percentage differences from iperf3 on the same VM and pass. Each cell shows the median [25th, 75th percentile] and number of VMs after reducing the matched pass differences within each VM. Tests ran sequentially. App and iperf3 start times were a median of 3.4 minutes apart (maximum 9.4).

| Tool or client | Download difference (%) | Upload difference (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | **0.0** [-0.1, 0.0] (n=15) | **-0.2** [-1.0, -0.1] (n=15) |
| Graphite Meter without loaded latency · Chrome | -0.1 [-0.2, -0.1] (n=15) | -0.3 [-0.5, -0.2] (n=15) |
| LibreSpeed · Chrome | **0.0** [-0.2, 0.0] (n=15) | -1.1 [-1.4, -0.7] (n=15) |
| LibreSpeed Go backend · Chrome | -0.2 [-0.4, +0.1] (n=15) | -0.5 [-1.2, -0.2] (n=15) |
| LibreSpeed Rust backend · Chrome | -0.1 [-0.2, 0.0] (n=15) | -0.6 [-0.9, -0.2] (n=15) |
| OpenSpeedTest · Chrome | -0.5 [-0.8, -0.2] (n=15) | **-0.2** [-0.6, -0.1] (n=15) |
| Graphite Meter Browser · Firefox | **-0.1** [-0.4, 0.0] (n=15) | -0.5 [-0.7, -0.4] (n=15) |
| Graphite Meter without loaded latency · Firefox | **-0.1** [-0.2, 0.0] (n=15) | **-0.3** [-0.5, -0.1] (n=15) |
| LibreSpeed · Firefox | -2.1 [-3.9, -1.1] (n=15) | -6.1 [-6.7, -4.7] (n=15) |
| LibreSpeed Go backend · Firefox | -1.7 [-4.3, -0.7] (n=15) | -5.0 [-6.6, -4.7] (n=15) |
| LibreSpeed Rust backend · Firefox | -3.0 [-3.6, -1.0] (n=15) | -5.5 [-7.4, -5.1] (n=15) |
| OpenSpeedTest · Firefox | -0.5 [-0.8, -0.1] (n=15) | -0.4 [-0.8, 0.0] (n=15) |
| Graphite Meter Terminal | **0.0** [0.0, 0.0] (n=15) | **0.0** [0.0, 0.0] (n=15) |
| Graphite Meter Terminal without loaded latency | **0.0** [0.0, 0.0] (n=15) | **0.0** [0.0, 0.0] (n=15) |
| LibreSpeed CLI | -1.4 [-1.9, -1.3] (n=15) | -8.9 [-9.0, -8.8] (n=15) |

### Unshaped throughput and browser CPU

Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand.
Each maximum is the fastest retained pass in that direction. The two maxima can come from different passes. Browser CPU measures the client process tree over the full run per GB at the shaper.

| Tool or client | Median down / up (Gbit/s) | Max down / up (Gbit/s) | Client CPU (s/GB) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 17.7 / 5.0 | 25.3 / 12.3 | 1.40 |
| Graphite Meter without loaded latency · Chrome | **18.4** / **5.3** | 23.5 / 12.5 | 1.29 |
| LibreSpeed · Chrome | 10.5 / 4.3 | 17.4 / 11.2 | 2.04 |
| LibreSpeed Go backend · Chrome | 10.9 / 4.3 | 17.0 / 11.2 | 1.98 |
| LibreSpeed Rust backend · Chrome | 10.6 / 4.2 | 16.8 / 11.2 | 2.04 |
| OpenSpeedTest · Chrome | 9.9 / 4.4 | 17.0 / 11.9 | 2.03 |
| Graphite Meter Browser · Firefox | 3.7 / 5.9 | 6.4 / 17.2 | 2.55 |
| Graphite Meter without loaded latency · Firefox | **4.3** / **6.5** | 7.3 / 17.6 | 2.19 |
| LibreSpeed · Firefox | 2.2 / 3.5 | 3.4 / 5.7 | 5.60 |
| LibreSpeed Go backend · Firefox | 2.3 / 3.5 | 3.6 / 5.6 | 5.60 |
| LibreSpeed Rust backend · Firefox | 2.4 / 3.4 | 3.6 / 5.6 | 5.62 |
| OpenSpeedTest · Firefox | 2.7 / 3.3 | 6.0 / 5.2 | 5.46 |
| Graphite Meter Terminal | **35.9** / **54.9** | 63.4 / 108.8 | — |
| Graphite Meter Terminal without loaded latency | 35.5 / 54.3 | 63.0 / 108.6 | — |
| LibreSpeed CLI | 31.0 / 18.9 | 52.8 / 28.8 | — |
| iperf3 (reference) | 30.6 / 44.2 | 63.9 / 99.0 | — |

#### Unshaped native upload by runner hardware

Upload medians in Gbit/s. “GM above iperf3” counts VMs after matching same-pass comparisons. CPU, kernel and runner conditions vary together. Groups with one VM show that VM’s median.

Graphite Meter Terminal had a higher upload rate than iperf3 on **9 of 15 VMs** after matching passes. The split was 0/6 on AWS-kernel VMs, 9/9 on Azure-kernel VMs.

| CPU and kernel | VMs | Graphite Meter Terminal | Graphite Meter Terminal without loaded latency | LibreSpeed CLI | iperf3 | GM above iperf3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AMD EPYC 7763 64-Core Processor (7.0.0-1017-azure) | 2 | 57.5 | 58.3 | 16.1 | 43.0 | 2/2 |
| AMD EPYC 9V45 96-Core Processor (7.0.0-1017-azure) | 1 | 108.2 | 105.6 | 27.9 | 76.6 | 1/1 |
| AMD EPYC 9V74 80-Core Processor (7.0.0-1017-azure) | 6 | 67.8 | 66.6 | 18.7 | 43.5 | 6/6 |
| Intel(R) Xeon(R) 6975P-C (7.0.0-1014-aws) | 6 | 46.2 | 46.1 | 27.6 | 91.0 | 0/6 |

### Server resources at 1 Gbit/s

Server CPU is container CPU time per decimal GB of server-interface traffic during each phase, counting bytes in both directions. Peak memory is the container’s per-run peak in decimal MB. The adjacent reported rates show how much of the same shaped link each setup used. Browser CPU is measured separately on the client. Native client CPU was not yet collected in this run.

| Tool or client | Down / up (Mbit/s) | Down CPU (s/GB) | Up CPU (s/GB) | Peak RAM (MB) |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 956.2 / 954.1 | 0.445 | 5.484 | **14.9** |
| Graphite Meter without loaded latency · Chrome | 955.4 / 954.2 | 0.383 | 5.556 | 15.3 |
| LibreSpeed · Chrome | 956.0 / 946.0 | 0.419 | 6.353 | 80.1 |
| LibreSpeed Go backend · Chrome | 954.5 / 952.0 | 0.403 | 5.704 | 48.1 |
| LibreSpeed Rust backend · Chrome | 955.5 / 950.5 | 0.345 | 4.415 | 22.5 |
| OpenSpeedTest · Chrome | 951.3 / 954.7 | **0.183** | **3.721** | 29.4 |
| Graphite Meter Terminal | 956.4 / 956.4 | **0.232** | 7.098 | **17.3** |
| Graphite Meter Terminal without loaded latency | 956.4 / 956.4 | 0.239 | 7.076 | 17.6 |
| LibreSpeed CLI | 943.2 / 871.0 | 0.276 | **2.488** | 68.7 |
| iperf3 (reference) | 956.4 / 956.4 | 0.198 | 5.652 | 19.2 |
| Graphite Meter Browser · Firefox | 955.7 / 951.1 | 0.398 | 5.777 | 15.7 |
| Graphite Meter without loaded latency · Firefox | 955.8 / 953.1 | 0.344 | 5.843 | **15.1** |
| LibreSpeed · Firefox | 936.0 / 898.0 | 0.497 | 5.648 | 85.8 |
| LibreSpeed Go backend · Firefox | 940.0 / 909.0 | 0.512 | 5.289 | 52.0 |
| LibreSpeed Rust backend · Firefox | 928.0 / 903.5 | 0.428 | **3.854** | 26.1 |
| OpenSpeedTest · Firefox | 951.7 / 952.3 | **0.236** | 4.843 | 29.6 |

Absolute server CPU time for the complete 1 Gbit/s test and each transfer phase.

| Tool or client | Download (CPU s) | Upload (CPU s) | Test total (CPU s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.27 | 3.47 | 3.74 |
| Graphite Meter without loaded latency · Chrome | 0.31 | 3.21 | 3.55 |
| LibreSpeed · Chrome | 0.36 | 6.53 | 6.96 |
| LibreSpeed Go backend · Chrome | 0.34 | 5.90 | 6.26 |
| LibreSpeed Rust backend · Chrome | 0.29 | 4.50 | 4.86 |
| OpenSpeedTest · Chrome | 0.33 | 5.71 | 6.03 |
| Graphite Meter Terminal | 0.33 | 10.26 | 10.74 |
| Graphite Meter Terminal without loaded latency | 0.34 | 10.22 | 10.58 |
| LibreSpeed CLI | 0.54 | 4.48 | 5.23 |
| iperf3 (reference) | 0.30 | 8.57 | 8.93 |
| Graphite Meter Browser · Firefox | 0.51 | 5.53 | 6.08 |
| Graphite Meter without loaded latency · Firefox | 0.42 | 4.80 | 5.23 |
| LibreSpeed · Firefox | 0.40 | 5.30 | 5.73 |
| LibreSpeed Go backend · Firefox | 0.42 | 4.96 | 5.44 |
| LibreSpeed Rust backend · Firefox | 0.36 | 3.62 | 4.01 |
| OpenSpeedTest · Firefox | 0.43 | 7.38 | 7.77 |

### Graphite Meter without loaded latency

Within each client, both profiles use the same server build, automatic connection settings, and transfer durations. The variant skips the app’s idle-latency stage and loaded probes. Each cell is **without loaded latency minus default** on the same VM and pass, summarized across VMs as median [middle 50%]. Total server CPU includes the skipped idle stage.

| Path | Client | Download (Mbit/s) | Upload (Mbit/s) | Download server CPU (s/GB) | Upload server CPU (s/GB) | Total server CPU (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 Gbit/s | Chrome | -0.9 [-1.1, -0.3] (n=15) | -0.2 [-0.8, +3.5] (n=15) | -0.010 [-0.082, +0.050] (n=15) | 0.000 [-0.164, +0.357] (n=15) | -0.07 [-0.51, +0.31] (n=15) |
| 1 Gbit/s | Firefox | +0.5 [-0.6, +1.9] (n=15) | +2.9 [-0.1, +4.4] (n=15) | -0.049 [-0.075, -0.023] (n=15) | -0.042 [-0.138, +0.241] (n=15) | -0.12 [-1.47, +0.92] (n=15) |
| 1 Gbit/s | Terminal | 0.0 [-0.1, +0.3] (n=15) | 0.0 [0.0, +0.3] (n=15) | -0.006 [-0.021, +0.024] (n=15) | -0.030 [-0.040, +0.015] (n=15) | -0.06 [-0.13, +0.05] (n=15) |
| 10 Gbit/s | Terminal | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | +0.002 [0.000, +0.003] (n=15) | -0.001 [-0.004, +0.002] (n=15) | -0.05 [-0.10, +0.06] (n=15) |
| Unshaped | Terminal | -150.0 [-327.5, +212.5] (n=15) | -90.0 [-1,252.5, +705.0] (n=15) | +0.002 [0.000, +0.002] (n=15) | 0.000 [-0.002, +0.003] (n=15) | -0.06 [-0.07, -0.03] (n=15) |

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
| Graphite Meter Browser · Chrome | 954.1 | 973.6 | 932.9 [926.7, 941.0] (n=15) | 0/30 |
| Graphite Meter without loaded latency · Chrome | 954.2 | 973.9 | 936.3 [929.0, 946.2] (n=15) | 2/30 |
| LibreSpeed · Chrome | 946.0 | 972.1 | 958.1 [953.5, 961.5] (n=15) | 2/30 |
| LibreSpeed Go backend · Chrome | 952.0 | 972.3 | 955.1 [946.1, 956.9] (n=15) | 9/30 |
| LibreSpeed Rust backend · Chrome | 950.5 | 972.3 | 950.7 [937.6, 956.1] (n=15) | 6/30 |
| OpenSpeedTest · Chrome | 954.7 | 973.7 | 974.8 [966.5, 976.7] (n=15) | 6/30 |
| Graphite Meter Browser · Firefox | 951.1 | 972.5 | 945.7 [926.9, 954.7] (n=15) | 3/30 |
| Graphite Meter without loaded latency · Firefox | 953.1 | 972.4 | 941.4 [932.7, 957.0] (n=15) | 5/30 |
| LibreSpeed · Firefox | 898.0 | 961.6 | 903.4 [893.9, 911.7] (n=15) | 0/30 |
| LibreSpeed Go backend · Firefox | 909.0 | 955.8 | 904.7 [897.3, 916.4] (n=15) | 0/30 |
| LibreSpeed Rust backend · Firefox | 903.5 | 962.1 | 908.5 [895.6, 914.1] (n=15) | 0/30 |
| OpenSpeedTest · Firefox | 952.3 | 972.7 | 955.5 [952.6, 969.6] (n=15) | 10/30 |
| Graphite Meter Terminal | 956.4 | 974.8 | 981.1 [979.0, 981.6] (n=15) | 14/30 |
| Graphite Meter Terminal without loaded latency | 956.4 | 974.9 | 982.4 [981.5, 984.4] (n=15) | 12/30 |
| LibreSpeed CLI | 871.0 | 965.4 | 934.6 [926.6, 940.5] (n=15) | 0/30 |
| iperf3 (reference) | 956.4 | 974.8 | 981.1 [979.9, 983.9] (n=15) | — |

**30 Mbit/s upload, deep FIFO**

| Tool or client | App rate | Shaper | Server RX | Above iperf3 |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 28.7 | 30.9 | 29.4 [29.4, 29.4] (n=15) | 14/30 |
| Graphite Meter without loaded latency · Chrome | 28.7 | 30.9 | 29.5 [29.4, 29.5] (n=15) | 16/30 |
| LibreSpeed · Chrome | 29.5 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 27/30 |
| LibreSpeed Go backend · Chrome | 29.3 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 22/30 |
| LibreSpeed Rust backend · Chrome | 29.0 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 16/30 |
| OpenSpeedTest · Chrome | 30.9 | 30.9 | 29.7 [29.7, 29.7] (n=15) | 30/30 |
| Graphite Meter Browser · Firefox | 28.7 | 30.9 | 29.4 [29.3, 29.4] (n=15) | 16/30 |
| Graphite Meter without loaded latency · Firefox | 28.7 | 30.9 | 29.4 [29.4, 29.4] (n=15) | 15/30 |
| LibreSpeed · Firefox | 29.1 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 20/30 |
| LibreSpeed Go backend · Firefox | 28.9 | 30.9 | 29.8 [29.8, 29.9] (n=15) | 21/30 |
| LibreSpeed Rust backend · Firefox | 28.8 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 17/30 |
| OpenSpeedTest · Firefox | 30.8 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 30/30 |
| Graphite Meter Terminal | 28.7 | 30.9 | 29.5 [29.5, 29.5] (n=15) | 12/30 |
| Graphite Meter Terminal without loaded latency | 28.7 | 30.9 | 29.6 [29.6, 29.7] (n=15) | 15/30 |
| LibreSpeed CLI | 29.3 | 30.9 | 29.7 [29.7, 29.8] (n=15) | 29/30 |
| iperf3 (reference) | 28.7 | 30.9 | 29.8 [29.8, 29.8] (n=15) | — |

### Idle latency against ICMP

The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference.
Each cell shows the median paired difference in ms [25th, 75th percentile] and number of VMs.

| Tool or client | 20 ms path | 40 ms path | 160 ms path |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | +0.3 [+0.2, +0.4] (n=15) | +0.3 [+0.3, +0.4] (n=15) | +0.3 [+0.3, +0.5] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — | — |
| LibreSpeed · Chrome | +0.2 [+0.2, +0.2] (n=15) | +0.2 [+0.1, +0.2] (n=15) | -0.1 [-0.2, +0.1] (n=15) |
| LibreSpeed Go backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, +0.1] (n=15) | -0.2 [-0.2, -0.1] (n=15) |
| LibreSpeed Rust backend · Chrome | 0.0 [-0.1, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.2 [-0.2, -0.1] (n=15) |
| OpenSpeedTest · Chrome | +0.4 [-0.1, +0.4] (n=15) | +0.4 [+0.3, +0.9] (n=15) | +0.8 [+0.3, +0.8] (n=15) |
| Graphite Meter Browser · Firefox | +0.9 [+0.8, +0.9] (n=15) | +0.9 [+0.9, +1.4] (n=15) | +0.8 [+0.8, +0.9] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — | — |
| LibreSpeed · Firefox | +1.4 [+1.3, +1.9] (n=15) | +1.4 [+1.3, +1.6] (n=15) | +1.8 [+1.4, +1.8] (n=15) |
| LibreSpeed Go backend · Firefox | +0.9 [+0.9, +1.3] (n=15) | +0.9 [+0.8, +1.4] (n=15) | +1.3 [+0.9, +1.6] (n=15) |
| LibreSpeed Rust backend · Firefox | +0.9 [+0.9, +0.9] (n=15) | +0.9 [+0.8, +1.4] (n=15) | +0.9 [+0.9, +1.4] (n=15) |
| OpenSpeedTest · Firefox | +0.4 [+0.1, +0.4] (n=15) | +0.8 [+0.4, +0.9] (n=15) | +0.8 [+0.4, +0.8] (n=15) |
| Graphite Meter Terminal | 0.0 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | -0.2 [-0.2, -0.1] (n=15) |
| Graphite Meter Terminal without loaded latency | — | — | — |
| LibreSpeed CLI | +0.1 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) |

### Latency under load on a FIFO

Each cell shows the app’s reported latency followed by the queue-based estimate, in ms.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 162.1 / 148.7 | 184.1 / 179.4 |
| Graphite Meter without loaded latency · Chrome | — / 161.3 | — / 181.5 |
| Graphite Meter Browser · Firefox | 166.0 / 154.4 | 184.8 / 179.7 |
| Graphite Meter without loaded latency · Firefox | — / 141.9 | — / 180.4 |
| Graphite Meter Terminal | 176.0 / 169.5 | 198.0 / 192.7 |
| Graphite Meter Terminal without loaded latency | — / 169.2 | — / 192.7 |

Paired app minus queue estimate in ms, summarized within VMs, then across VMs.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | +8.5 [+7.2, +11.5] (n=15) | +3.4 [+2.5, +5.8] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — |
| Graphite Meter Browser · Firefox | +12.1 [+10.4, +13.9] (n=15) | +4.3 [+2.2, +5.7] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — |
| Graphite Meter Terminal | +6.7 [+6.2, +7.2] (n=15) | +4.9 [+4.6, +6.2] (n=15) |
| Graphite Meter Terminal without loaded latency | — | — |

## Pooled pass tables

The tables below pool all retained completed passes for each configuration, including alternate
transports. Their comparison columns show the difference from the modeled TCP payload ceiling
when iperf3 reaches at least 98% of the model in both directions. QUIC rows show measured rates separately.
The matched comparison above uses the measured same-pass receiver rate.
Below-ceiling rates can reflect any constraint on the end-to-end transfer.

[100 Mbit/s](#100100-mbits-20-ms-rtt-fq_codel) · [1 Gbit/s](#11-gbits-20-ms-rtt-fq_codel) · [10 Gbit/s](#1010-gbits-2-ms-rtt-fq_codel-offloads-on) · [Deep FIFO](#30030-mbits-20-ms-rtt-200-ms-fifo) · [1% loss](#100100-mbits-40-ms-rtt-1--loss-each-way-fq_codel) · [0.1% loss](#11-gbits-40-ms-rtt-01--loss-each-way-fq_codel) · [160 ms RTT](#300300-mbits-160-ms-rtt-fq_codel) · [Competing traffic](#100100-mbits-20-ms-rtt-fq_codel-one-competing-flow-each-way) · [Reverse proxy](#11-gbits-20-ms-rtt-fq_codel-behind-nginx) · [Two servers](#two-servers-200200-mbits-path-each-20-ms-rtt-fq_codel) · [Unshaped](#unshaped-offloads-on-as-fast-as-the-host-allows)

<!-- pooled-pass-tables -->
Jobs: 15. Runs: 5490, of which 0 left out from blocks on a busy host. Hosts: Intel(R) Xeon(R) 6975P-C (4 CPUs, kernel 7.0.0-1014-aws, rootful); AMD EPYC 7763 64-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 9V45 96-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 9V74 80-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful).
Tools: Graphite Meter 0.14.3, LibreSpeed 6.3.1, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest 2.5.4, Graphite Meter terminal client 0.14.3, LibreSpeed CLI 1.0.14. Browsers: chrome 157.0.8103.78, firefox 160.0.

## 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.6 [95.4, 95.6] | -0.1 % | 20.4 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.6 [95.6, 95.6] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.6 [95.6, 95.7] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.3 [95.3, 95.5] | -0.3 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.5 [95.4, 95.5] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.4 [95.3, 95.5] | -0.3 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.7 [95.6, 95.7] | +0.1 % | 95.6 [95.5, 95.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.2 [95.2, 95.3] | -0.5 % | 96.0 [95.9, 97.0] | +0.4 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.8 [94.7, 94.8] | -0.9 % | 92.4 [91.4, 93.0] | -3.3 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.4 [95.1, 95.6] | -0.3 % | 95.5 [95.0, 96.4] | -0.1 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.3 [95.2, 95.7] | -0.4 % | 95.5 [94.7, 95.7] | -0.2 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.3 [95.1, 95.4] | -0.4 % | 95.8 [94.6, 96.2] | +0.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.2, 95.6] | -0.4 % | 95.0 [94.9, 95.7] | -0.7 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.3 [95.1, 95.4] | -0.4 % | 95.8 [95.1, 96.4] | +0.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.6 [95.4, 95.6] | -0.0 % | 95.8 [94.9, 96.5] | +0.1 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.6 [95.5, 95.7] | -0.0 % | 96.2 [95.7, 97.2] | +0.6 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.2 [955.8, 956.4] | -0.0 % | 954.3 [950.4, 955.4] | -0.2 % | 20.4 (20.1) | 21.3 (n/a) | 20.6 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 956.4 [956.4, 956.5] | -0.0 % | 956.4 [956.4, 956.4] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 953.2 [953.1, 953.2] | -0.3 % | 953.2 [953.2, 953.2] | -0.3 % | 20.2 (20.1) | 20.4 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 937.9 [937.7, 938.2] | n/a | 948.7 [948.7, 948.7] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 956.4 [956.4, 956.5] | -0.0 % | 956.4 [956.3, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 955.8 [953.2, 956.4] | -0.1 % | 951.0 [946.9, 955.0] | -0.6 % | 21.0 (20.1) | 31.5 (n/a) | 22.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 951.0 [950.7, 951.2] | -0.6 % | 944.2 [938.6, 947.0] | -1.3 % | 20.4 (20.1) | 22.1 (n/a) | 23.1 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 948.1 [945.3, 949.9] | n/a | 730.9 [710.1, 817.8] | n/a | 20.4 (20.1) | 20.4 (n/a) | 23.2 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 955.3 [954.8, 955.8] | -0.1 % | 954.1 [953.0, 955.1] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 955.9 [954.2, 956.4] | -0.1 % | 953.9 [950.2, 955.8] | -0.3 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 946.5 [943.7, 954.3] | n/a | 686.8 [667.2, 826.8] | n/a | 20.5 (20.1) | 20.5 (n/a) | 21.8 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.3, 956.5] | -0.0 % | 956.4 [956.2, 956.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 956.0 [954.0, 957.8] | -0.0 % | 944.0 [941.0, 949.8] | -1.3 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 943.1 [936.6, 944.0] | -1.4 % | 871.0 [869.4, 872.5] | -8.9 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 937.0 [917.0, 950.5] | -2.0 % | 903.0 [883.3, 915.5] | -5.6 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 954.0 [952.3, 957.0] | -0.3 % | 949.0 [944.0, 957.0] | -0.8 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 940.5 [911.5, 952.0] | -1.7 % | 905.0 [892.8, 914.5] | -5.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 944.0 [941.3, 946.0] | -1.3 % | 414.0 [411.3, 414.0] | -56.7 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 955.5 [954.0, 957.0] | -0.1 % | 952.0 [946.0, 954.0] | -0.5 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 935.0 [913.3, 950.5] | -2.2 % | 901.0 [880.5, 912.8] | -5.8 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.5 [948.8, 954.2] | -0.4 % | 953.1 [949.1, 955.8] | -0.3 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 952.5 [947.2, 955.5] | -0.4 % | 953.5 [947.0, 958.8] | -0.3 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 950.3 [948.0, 951.4] | -0.6 % | 935.5 [927.8, 939.9] | -2.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 9562.8 [9558.5, 9564.2] | -0.0 % | 4326.7 [4230.1, 6216.9] | -54.8 % | 2.2 (2.1) | 3.0 (n/a) | 3.5 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.1 (n/a) | 2.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 9530.0 [9512.5, 9530.0] | -0.4 % | 9530.0 [9522.5, 9530.0] | -0.4 % | 2.1 (2.1) | 7.2 (n/a) | 2.3 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 6835.0 [6385.0, 7127.5] | n/a | 7560.0 [6280.0, 7830.0] | n/a | 2.1 (2.1) | 3.2 (n/a) | 2.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 3424.6 [3210.7, 5378.3] | -64.2 % | 5345.5 [5158.7, 8673.7] | -44.1 % | 3.0 (2.1) | 19.3 (n/a) | 55.3 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 5500.7 [5127.0, 6893.0] | -42.5 % | 2632.9 [2575.8, 4753.1] | -72.5 % | 2.2 (2.1) | 3.4 (n/a) | 3.2 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 2153.0 [2100.0, 2789.7] | n/a | 769.6 [750.9, 1540.5] | n/a | 2.2 (2.1) | 2.4 (n/a) | 5.3 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 9562.3 [9555.1, 9563.9] | -0.0 % | 4482.6 [4344.0, 6302.4] | -53.1 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 3671.1 [3484.8, 6031.0] | -61.6 % | 5766.1 [5594.1, 8907.4] | -39.7 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 2193.0 [2135.1, 2778.1] | n/a | 709.0 [692.1, 1189.4] | n/a | 2.2 (2.1) | 2.5 (n/a) | 4.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.2 [9564.2, 9564.3] | +0.0 % | 9564.3 [9564.2, 9564.3] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 9446.5 [9153.0, 9570.0] | -1.2 % | 3321.0 [3205.8, 5178.5] | -65.3 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9355.6 [9355.2, 9356.2] | -2.2 % | 8156.1 [8100.8, 8237.9] | -14.7 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 2334.0 [2037.8, 3342.3] | -75.6 % | 3242.5 [3053.3, 4151.3] | -66.1 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 9452.0 [9114.8, 9533.3] | -1.2 % | 3344.5 [3253.5, 5227.0] | -65.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 2380.5 [2094.3, 3349.5] | -75.1 % | 3233.0 [2985.0, 4042.3] | -66.2 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 4318.5 [4073.0, 4408.8] | -54.8 % | 2541.0 [2471.3, 3335.5] | -73.4 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 9495.0 [9240.5, 9550.3] | -0.7 % | 3241.5 [3160.8, 5227.0] | -66.1 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 2315.0 [2054.3, 3441.8] | -75.8 % | 3158.5 [3035.8, 4015.8] | -67.0 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 9466.6 [9185.6, 9558.3] | -1.0 % | 3401.7 [3308.5, 5375.7] | -64.4 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 2768.6 [2656.5, 5448.5] | -71.1 % | 3151.8 [2959.6, 4026.0] | -67.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 4544.6 [4365.2, 5666.9] | -52.5 % | 2470.4 [2371.1, 4139.9] | -74.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.4 (20.1) | 155.2 (142.8) | 185.1 (180.5) |
| Graphite Meter Terminal | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.2 (20.1) | 176.0 (169.4) | 198.0 (193.7) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.0 % | n/a (20.1) | n/a (168.9) | n/a (192.5) |
| Graphite Meter Browser, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 21.0 (20.1) | 164.8 (148.3) | 186.5 (181.7) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 287.0 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (148.2) | n/a (181.6) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (131.7) | n/a (181.1) |
| iperf3 (reference) | 30/30 | payload | 287.0 [286.9, 287.0] | +0.0 % | 28.7 [28.6, 28.7] | -0.1 % | n/a (20.1) | n/a (176.4) | n/a (187.0) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [284.0, 287.0] | -0.3 % | 29.8 [29.0, 30.0] | +3.9 % | 20.3 (20.1) | n/a (159.9) | n/a (186.5) |
| LibreSpeed CLI | 30/30 | payload | 283.1 [282.5, 284.2] | -1.3 % | 29.0 [29.0, 29.6] | +1.2 % | 20.2 (20.1) | n/a (168.9) | n/a (171.6) |
| LibreSpeed, firefox | 30/30 | payload | 286.0 [284.0, 286.8] | -0.3 % | 29.3 [28.5, 29.5] | +2.1 % | 21.0 (20.1) | n/a (161.6) | n/a (186.1) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 286.0 [283.0, 287.0] | -0.3 % | 29.1 [28.7, 29.8] | +1.2 % | 20.1 (20.1) | n/a (163.7) | n/a (167.0) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 285.0 [281.0, 287.0] | -0.7 % | 29.3 [28.7, 29.4] | +2.1 % | 21.0 (20.1) | n/a (162.8) | n/a (186.4) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 28.7 [28.1, 29.7] | +0.0 % | 20.1 (20.1) | n/a (158.2) | n/a (169.5) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 286.5 [286.0, 287.0] | -0.1 % | 28.9 [28.5, 29.4] | +0.5 % | 21.0 (20.1) | n/a (156.0) | n/a (187.3) |
| OpenSpeedTest, chrome | 30/30 | payload | 287.1 [286.5, 287.2] | +0.0 % | 31.3 [30.1, 31.6] | +9.1 % | 20.0 (20.1) | n/a (162.4) | n/a (196.6) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.8 [285.8, 287.5] | -0.1 % | 30.3 [30.1, 31.6] | +5.6 % | 20.0 (20.1) | n/a (164.7) | n/a (197.2) |

## 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 13.3 [12.9, 13.6] | n/a | 13.9 [13.1, 14.6] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 19.5 [19.0, 20.1] | n/a | 19.9 [19.4, 20.2] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 19.6 [19.1, 20.0] | n/a | 19.7 [19.3, 20.7] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 12.8 [12.3, 13.3] | n/a | 14.4 [13.7, 15.2] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 12.8 [12.6, 13.2] | n/a | 13.9 [12.9, 14.6] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 13.3 [12.9, 13.7] | n/a | 13.7 [13.2, 14.4] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 12.8 [12.5, 13.4] | n/a | 12.7 [12.3, 13.2] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 17.1 [16.4, 17.7] | n/a | 9.5 [9.1, 9.9] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 11.2 [10.8, 11.7] | n/a | 11.3 [10.8, 11.8] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 20.5 [19.8, 21.1] | n/a | 9.2 [8.8, 10.2] | n/a | 42.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 16.8 [16.4, 17.6] | n/a | 9.4 [8.8, 9.7] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 21.8 [20.3, 23.0] | n/a | 9.6 [9.1, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 16.9 [16.4, 17.9] | n/a | 9.6 [9.3, 10.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 20.9 [20.3, 21.5] | n/a | 9.3 [9.1, 9.9] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 19.5 [18.8, 20.0] | n/a | 21.4 [20.6, 22.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.4 [18.6, 20.0] | n/a | 21.9 [21.2, 23.4] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 59.6 [54.7, 64.3] | n/a | 66.8 [59.5, 73.0] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 87.8 [83.7, 95.5] | n/a | 88.0 [82.9, 93.2] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 14.8 [12.8, 16.8] | n/a | 12.8 [11.4, 16.1] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 87.2 [62.6, 116.4] | n/a | 128.1 [102.3, 188.0] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 88.5 [82.9, 92.8] | n/a | 89.8 [83.2, 93.0] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 60.1 [54.8, 65.0] | n/a | 71.8 [63.7, 78.3] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 13.9 [12.3, 18.5] | n/a | 15.0 [12.7, 17.6] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 85.9 [71.3, 132.2] | n/a | 27.4 [22.1, 31.8] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 64.1 [59.6, 65.4] | n/a | 67.5 [60.9, 73.6] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 60.2 [55.0, 69.5] | n/a | 75.1 [66.5, 83.7] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 92.6 [63.7, 108.4] | n/a | 26.0 [23.2, 30.2] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 49.9 [47.6, 54.5] | n/a | 51.0 [47.7, 53.2] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 106.0 [91.9, 118.5] | n/a | 37.0 [34.4, 40.0] | n/a | 40.4 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 55.7 [49.4, 64.9] | n/a | 47.8 [43.8, 51.7] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 150.0 [124.3, 164.8] | n/a | 39.0 [36.5, 43.8] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 98.4 [89.5, 110.3] | n/a | 66.2 [45.7, 90.3] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 136.0 [116.3, 172.8] | n/a | 35.0 [32.0, 39.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 12.6 [11.9, 13.4] | n/a | 13.1 [11.8, 14.8] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 92.7 [84.0, 103.6] | n/a | 56.7 [47.4, 69.2] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 134.5 [120.0, 155.5] | n/a | 39.3 [36.1, 43.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 77.4 [72.3, 80.9] | n/a | 90.0 [86.7, 98.2] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 78.8 [75.2, 85.3] | n/a | 93.0 [88.8, 100.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 12.4 [10.6, 14.3] | n/a | 16.1 [14.7, 17.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 279.2 [273.6, 283.4] | n/a | 239.5 [233.5, 242.9] | n/a | 160.5 (160.2) | 160.4 (n/a) | 160.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 281.4 [278.6, 284.3] | n/a | 280.1 [274.6, 282.9] | n/a | 160.0 (160.2) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 277.3 [276.2, 280.1] | n/a | 278.1 [272.1, 280.9] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 272.1 [265.4, 278.6] | n/a | 238.6 [233.8, 243.7] | n/a | 161.0 (160.2) | 161.8 (n/a) | 161.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 269.4 [262.5, 275.1] | n/a | 231.4 [226.0, 235.4] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 265.9 [258.7, 271.2] | n/a | 232.6 [227.8, 236.7] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 206.8 [199.7, 233.5] | n/a | 225.9 [204.4, 232.7] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 271.5 [267.0, 275.0] | n/a | 235.0 [231.3, 241.0] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 222.8 [217.3, 227.6] | n/a | 123.1 [122.6, 123.1] | n/a | 160.3 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 273.0 [269.3, 276.8] | n/a | 228.0 [221.8, 239.5] | n/a | 162.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 271.5 [265.0, 275.0] | n/a | 232.5 [223.5, 237.0] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 274.5 [270.3, 278.0] | n/a | 226.0 [216.8, 236.0] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 269.0 [264.5, 273.0] | n/a | 229.5 [223.8, 238.3] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 272.0 [270.0, 277.0] | n/a | 222.0 [215.0, 227.0] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 269.7 [264.8, 273.6] | n/a | 274.4 [272.0, 276.4] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 272.6 [268.1, 276.9] | n/a | 274.1 [272.1, 276.2] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |

## 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 75.0 [74.9, 75.0] | n/a | 75.2 [75.1, 75.3] | n/a | 20.5 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.8] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.8] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 74.9 [74.9, 75.0] | n/a | 75.1 [75.0, 75.3] | n/a | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 75.0 [74.9, 75.1] | n/a | 75.2 [75.2, 75.3] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 74.9 [74.9, 75.0] | n/a | 75.1 [75.0, 75.2] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 74.9 [74.8, 75.0] | n/a | 75.2 [75.0, 75.4] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 70.9 [70.0, 71.4] | n/a | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.4 [69.3, 69.4] | n/a | 68.8 [68.4, 69.3] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.2 [80.0, 80.3] | n/a | 69.9 [69.8, 70.5] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 72.6 [72.5, 72.7] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 80.0 [79.9, 80.2] | n/a | 70.3 [69.8, 71.1] | n/a | 21.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.7 [77.7, 77.8] | n/a | 72.6 [71.3, 72.7] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.1 [80.0, 80.3] | n/a | 70.0 [69.8, 71.4] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.1 [80.1, 80.2] | n/a | 80.9 [80.6, 81.3] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.2 [80.1, 80.3] | n/a | 80.7 [80.4, 81.3] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. iperf3 bypasses nginx and measures the direct shaped path as a control. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 955.0 [951.6, 956.2] | -0.1 % | 954.8 [953.0, 955.8] | -0.2 % | 20.4 (20.1) | 22.4 (n/a) | 23.6 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 951.8 [949.5, 955.8] | -0.5 % | 954.8 [953.4, 956.3] | -0.2 % | 21.0 (20.1) | 34.0 (n/a) | 28.8 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 953.8 [950.6, 955.2] | -0.3 % | 954.1 [952.0, 955.7] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 952.6 [949.0, 955.2] | -0.4 % | 954.7 [952.5, 955.8] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.3, 956.4] | -0.0 % | 956.3 [956.3, 956.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 955.5 [951.3, 957.0] | -0.1 % | 917.5 [894.8, 925.3] | -4.1 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 933.0 [910.3, 953.0] | -2.4 % | 868.0 [851.8, 878.5] | -9.2 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.3 [950.2, 954.0] | -0.4 % | 920.0 [916.6, 928.1] | -3.8 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 950.5 [947.5, 953.7] | -0.6 % | 914.3 [909.4, 919.6] | -4.4 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.7 [381.3, 382.0] | -0.2 % | 20.4 (20.1) | 20.7 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | 20.2 (20.1) | 20.3 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 382.5 [382.4, 382.5] | -0.0 % | 381.3 [381.0, 381.6] | -0.3 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.7 [381.2, 381.9] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.6 [381.1, 381.8] | -0.3 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 382.6 [382.5, 382.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

## Unshaped, offloads on: as fast as the host allows

Unshaped single-test throughput on the runner’s virtual link. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | 18539.7 [15998.3, 21236.4] | 5016.6 [4789.4, 11362.5] | 0.27 | 10 | 1.35 |
| Graphite Meter Terminal | 30/30 | 35885.0 [29155.0, 60880.0] | 55055.0 [46750.0, 67735.0] | 0.16 | 11 | n/a |
| Graphite Meter Terminal, HTTP/2 | 30/30 | 14575.0 [13890.0, 16175.0] | 17560.0 [16362.5, 17885.0] | 0.48 | 5 | n/a |
| Graphite Meter Terminal, HTTP/3 | 30/30 | 8130.0 [7977.5, 8490.0] | 8860.0 [7617.5, 9035.0] | 0.87 | 13 | n/a |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | 35515.0 [28715.0, 61360.0] | 54615.0 [46545.0, 66895.0] | 0.16 | 11 | n/a |
| Graphite Meter Browser, firefox | 30/30 | 3705.8 [3527.0, 5615.1] | 5994.1 [5748.6, 15326.9] | 0.23 | 9 | 2.54 |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | 18367.0 [16297.6, 21355.5] | 5302.0 [5160.7, 11704.0] | 0.27 | 10 | 1.29 |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | 4278.9 [4032.0, 6551.9] | 6528.8 [6390.2, 16313.3] | 0.23 | 10 | 2.19 |
| iperf3 (reference) | 30/30 | 30648.4 [27410.1, 62032.2] | 44232.7 [43376.0, 90369.1] | 0.20 | 17 | n/a |
| LibreSpeed, chrome | 30/30 | 10622.5 [9860.8, 15056.5] | 4293.5 [4097.3, 10574.8] | 0.29 | 82 | 2.03 |
| LibreSpeed CLI | 30/30 | 31948.5 [27603.3, 48443.7] | 18925.6 [18485.2, 27607.2] | 0.29 | 72 | n/a |
| LibreSpeed, firefox | 30/30 | 2328.5 [1989.8, 3204.3] | 3458.5 [3259.0, 4818.8] | 0.31 | 87 | 5.57 |
| LibreSpeed Go backend, chrome | 30/30 | 10892.0 [9788.0, 15184.8] | 4356.0 [4194.0, 10760.0] | 0.32 | 49 | 1.98 |
| LibreSpeed Go backend, firefox | 30/30 | 2340.0 [2109.0, 3283.5] | 3481.5 [3212.3, 4802.5] | 0.33 | 52 | 5.56 |
| LibreSpeed Rust backend, chrome | 30/30 | 10841.5 [10197.8, 14937.0] | 4270.5 [4103.5, 10542.0] | 0.23 | 23 | 2.00 |
| LibreSpeed Rust backend, firefox | 30/30 | 2412.5 [2045.5, 3223.0] | 3389.5 [3214.8, 4749.0] | 0.23 | 26 | 5.61 |
| OpenSpeedTest, chrome | 30/30 | 10133.4 [9432.6, 14178.5] | 4399.1 [4267.9, 11162.9] | 0.19 | 23 | 2.01 |
| OpenSpeedTest, firefox | 30/30 | 2698.9 [2609.1, 5445.1] | 3430.2 [3210.4, 4833.8] | 0.25 | 21 | 5.38 |
