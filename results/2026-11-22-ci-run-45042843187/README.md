# GitHub runner benchmark, 22.11.2026

**5,490/5,490** retained runs completed across **15 runner jobs** (0 runs excluded by the busy-host rule).
The 25 and 40 Gbit/s shaped scenarios are skipped on these 4-vCPU runners. They require 8+ CPUs.

[Benchmark source at 52375b4273a7dec70c1254927f51d8e3d79a0999](https://github.com/zR-JB/selfhosted-speedtest-bench/tree/52375b4273a7dec70c1254927f51d8e3d79a0999) · [Workflow run and raw artifacts](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/45042843187)
[Provenance and exact pins](provenance.json) · [Retained scalar measurements](measurements.json.gz) · [Server CPU by phase](server-cpu.md) · [Bench overview](../../README.md) · [Previous report](../2026-11-22-ci-run-44971677456)

The workflow stores the detailed artifacts and screenshots for its retention window. The scalar archive
keeps the inputs used by the overview charts and tables. Read it with `gzip -dc measurements.json.gz`.
Provenance records the job order, CPU allocation, pinned releases and workload definitions.

To regenerate the overview tables and charts from the committed archive, run
`python3 bench/report.py 45042843187 --from-archive --rerender` from the repository root.
The renderer uses Python 3 with Matplotlib. When this is the latest run, the command also updates
the root README. Regenerating the detailed pass tables requires all 15 job artifacts, Node.js 22 or later,
and the benchmark source revision in local Git history. Use
`python3 bench/report.py 45042843187 /path/to/artifacts --rerender` while they remain available.

## Tested versions

| Tested release | Version |
| --- | ---: |
| Graphite Meter Browser | 0.14.5 |
| Graphite Meter without loaded latency | 0.14.5 |
| LibreSpeed | 6.3.1 |
| LibreSpeed Go backend | 1.1.6 |
| LibreSpeed Rust backend | 1.4.0 |
| OpenSpeedTest | 2.5.4 |
| Graphite Meter Terminal | 0.14.5 |
| Graphite Meter Terminal without loaded latency | 0.14.5 |
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
| Graphite Meter Browser · Chrome | 956.3 / **954.4** | **9.56** / **5.57** | **20.0** / 19.9 |
| Graphite Meter without loaded latency · Chrome | 955.5 / 953.7 | **9.56** / **5.57** | 19.7 / 19.9 |
| LibreSpeed · Chrome | **956.5** / 949.0 | 9.54 / 5.07 | 17.1 / 9.6 |
| LibreSpeed Go backend · Chrome | 955.0 / 953.5 | 9.54 / 5.11 | 16.6 / 9.5 |
| LibreSpeed Rust backend · Chrome | 953.0 / 952.0 | 9.55 / 5.15 | 17.2 / 9.7 |
| OpenSpeedTest · Chrome | 954.1 / 953.4 | 9.55 / 5.39 | 19.3 / **21.9** |
| Graphite Meter Terminal | **956.5** / **956.4** | **9.56** / **9.56** | **19.7** / 19.8 |
| Graphite Meter Terminal without loaded latency | **956.5** / **956.4** | **9.56** / **9.56** | 19.5 / **20.0** |
| LibreSpeed CLI | 941.2 / 871.0 | 9.36 / 8.22 | 11.3 / 11.6 |
| iperf3 (reference) | 956.4 / 956.4 | 9.56 / 9.56 | 13.0 / 12.7 |

### 10 Gbit/s upload spread

Each cell shows the median [25th, 75th percentile] and number of VMs. The last column uses matched same-VM, same-pass iperf3 rates. A lower achieved rate can come from any part of the test setup.

Graphite Meter Browser’s same-pass upload difference from OpenSpeedTest in Chrome was **+0.26 Gbit/s** (middle 50% +0.22 to +0.36). Graphite Meter Browser reported more on **15/15 matched VMs**.

| Tool or client | Upload (Gbit/s) | Paired difference from iperf3 (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 5.57 [3.75, 5.69] (n=15) | -41.8 [-60.8, -40.6] (n=15) |
| Graphite Meter without loaded latency · Chrome | 5.57 [3.85, 5.72] (n=15) | -41.7 [-59.7, -40.2] (n=15) |
| LibreSpeed · Chrome | 5.07 [3.29, 5.19] (n=15) | -47.0 [-65.6, -45.7] (n=15) |
| LibreSpeed Go backend · Chrome | 5.11 [3.29, 5.23] (n=15) | -46.5 [-65.6, -45.4] (n=15) |
| LibreSpeed Rust backend · Chrome | 5.15 [3.24, 5.21] (n=15) | -46.2 [-66.2, -45.5] (n=15) |
| OpenSpeedTest · Chrome | 5.39 [3.33, 5.48] (n=15) | -43.7 [-65.2, -42.7] (n=15) |
| Graphite Meter Browser · Firefox | 8.86 [5.16, 9.04] (n=15) | -7.4 [-46.1, -5.5] (n=15) |
| Graphite Meter without loaded latency · Firefox | 8.94 [5.49, 9.29] (n=15) | -6.5 [-42.6, -2.9] (n=15) |
| LibreSpeed · Firefox | 4.14 [3.20, 4.20] (n=15) | -56.7 [-66.6, -56.1] (n=15) |
| LibreSpeed Go backend · Firefox | 3.99 [3.23, 4.08] (n=15) | -58.3 [-66.2, -57.3] (n=15) |
| LibreSpeed Rust backend · Firefox | 3.93 [3.18, 4.11] (n=15) | -58.9 [-66.8, -57.0] (n=15) |
| OpenSpeedTest · Firefox | 3.95 [3.15, 4.21] (n=15) | -58.7 [-67.0, -56.0] (n=15) |
| Graphite Meter Terminal | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| Graphite Meter Terminal without loaded latency | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | 8.22 [8.16, 8.26] (n=15) | -14.0 [-14.6, -13.6] (n=15) |
| iperf3 (reference) | 9.56 [9.56, 9.56] (n=15) | — |

### Matched 1 Gbit/s agreement

Signed percentage differences from iperf3 on the same VM and pass. Each cell shows the median [25th, 75th percentile] and number of VMs after reducing the matched pass differences within each VM. Tests ran sequentially. App and iperf3 start times were a median of 3.1 minutes apart (maximum 9.4).

| Tool or client | Download difference (%) | Upload difference (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | **0.0** [-0.1, 0.0] (n=15) | **-0.2** [-2.4, -0.1] (n=15) |
| Graphite Meter without loaded latency · Chrome | -0.1 [-0.1, 0.0] (n=15) | -0.3 [-1.5, 0.0] (n=15) |
| LibreSpeed · Chrome | **0.0** [-0.1, +0.1] (n=15) | -0.8 [-1.3, -0.6] (n=15) |
| LibreSpeed Go backend · Chrome | -0.1 [-0.2, 0.0] (n=15) | -0.3 [-0.5, -0.3] (n=15) |
| LibreSpeed Rust backend · Chrome | -0.3 [-0.4, -0.1] (n=15) | -0.4 [-0.9, -0.3] (n=15) |
| OpenSpeedTest · Chrome | -0.2 [-0.4, -0.2] (n=15) | -0.3 [-0.8, 0.0] (n=15) |
| Graphite Meter Browser · Firefox | **-0.1** [-0.2, 0.0] (n=15) | **-0.1** [-0.7, 0.0] (n=15) |
| Graphite Meter without loaded latency · Firefox | -0.3 [-0.4, -0.1] (n=15) | **-0.1** [-0.5, 0.0] (n=15) |
| LibreSpeed · Firefox | -1.2 [-3.7, -0.4] (n=15) | -6.6 [-7.4, -5.5] (n=15) |
| LibreSpeed Go backend · Firefox | -0.7 [-3.2, -0.2] (n=15) | -5.5 [-6.3, -5.1] (n=15) |
| LibreSpeed Rust backend · Firefox | -1.7 [-2.5, -0.3] (n=15) | -5.5 [-6.1, -5.1] (n=15) |
| OpenSpeedTest · Firefox | -0.3 [-0.6, -0.1] (n=15) | -0.8 [-0.9, -0.4] (n=15) |
| Graphite Meter Terminal | **0.0** [0.0, 0.0] (n=15) | **0.0** [0.0, 0.0] (n=15) |
| Graphite Meter Terminal without loaded latency | **0.0** [0.0, 0.0] (n=15) | **0.0** [0.0, 0.0] (n=15) |
| LibreSpeed CLI | -1.6 [-1.9, -1.3] (n=15) | -8.9 [-9.0, -8.8] (n=15) |

### Unshaped throughput and client CPU

Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand.
Each maximum is the fastest retained pass in that direction. The two maxima can come from different passes. Client CPU divides browser process-tree CPU (browser rows) or container cgroup CPU (native rows, where recorded) by total shaper GB.

| Tool or client | Median down / up (Gbit/s) | Max down / up (Gbit/s) | Client CPU (s/GB) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 24.3 / 12.2 | 27.0 / 13.0 | 0.86 |
| Graphite Meter without loaded latency · Chrome | **24.6** / **12.5** | 27.5 / 13.4 | 0.81 |
| LibreSpeed · Chrome | 14.8 / 10.6 | 17.2 / 11.3 | 1.18 |
| LibreSpeed Go backend · Chrome | 15.3 / 10.6 | 16.8 / 11.2 | 1.15 |
| LibreSpeed Rust backend · Chrome | 14.8 / 10.6 | 16.4 / 11.3 | 1.19 |
| OpenSpeedTest · Chrome | 13.7 / 11.2 | 16.6 / 11.8 | 1.15 |
| Graphite Meter Browser · Firefox | 7.2 / 15.9 | 7.7 / 18.6 | 1.26 |
| Graphite Meter without loaded latency · Firefox | **7.8** / **16.8** | 8.7 / 18.9 | 1.13 |
| LibreSpeed · Firefox | 3.2 / 4.7 | 3.5 / 5.4 | 3.56 |
| LibreSpeed Go backend · Firefox | 3.1 / 4.7 | 3.5 / 5.6 | 3.57 |
| LibreSpeed Rust backend · Firefox | 3.0 / 4.7 | 3.3 / 5.3 | 3.55 |
| OpenSpeedTest · Firefox | 5.5 / 4.8 | 6.2 / 5.4 | 2.97 |
| Graphite Meter Terminal | 80.2 / 169.7 | 83.0 / 175.6 | 0.09 |
| Graphite Meter Terminal without loaded latency | **80.9** / **170.7** | 83.9 / 175.5 | 0.09 |
| LibreSpeed CLI | 48.6 / 26.7 | 51.4 / 28.2 | 0.25 |
| iperf3 (reference) | 61.9 / 92.2 | 64.1 / 98.0 | 0.12 |

#### Unshaped native upload by runner hardware

Upload medians in Gbit/s. “GM above iperf3” counts VMs after matching same-pass comparisons. CPU, kernel and runner conditions vary together. Groups with one VM show that VM’s median.

Graphite Meter Terminal had a higher upload rate than iperf3 on **15 of 15 VMs** after matching passes. The split was 8/8 on AWS-kernel VMs, 7/7 on Azure-kernel VMs.

| CPU and kernel | VMs | Graphite Meter Terminal | Graphite Meter Terminal without loaded latency | LibreSpeed CLI | iperf3 | GM above iperf3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AMD EPYC 7763 64-Core Processor (7.0.0-1017-azure) | 2 | 55.4 | 55.6 | 16.1 | 44.5 | 2/2 |
| AMD EPYC 9V45 96-Core Processor (7.0.0-1017-azure) | 2 | 96.8 | 94.1 | 26.9 | 77.5 | 2/2 |
| AMD EPYC 9V74 80-Core Processor (7.0.0-1017-azure) | 3 | 76.6 | 76.3 | 18.9 | 43.2 | 3/3 |
| Intel(R) Xeon(R) 6975P-C (7.0.0-1014-aws) | 8 | 171.9 | 172.3 | 27.2 | 94.0 | 8/8 |

### Server resources at 1 Gbit/s

Server CPU is container CPU time per decimal GB of server-interface traffic during each phase (counting both directions), or total container CPU per shaper GB on unshaped. Peak memory is per-run container memory.peak in decimal MB. Client CPU divides browser process-tree CPU (browser rows) or container cgroup CPU (native rows) by shaper GB.

| Tool or client | Down / up (Mbit/s) | Down CPU (s/GB) | Up CPU (s/GB) | Peak RAM (MB) |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 956.3 / 954.4 | 0.332 | 0.921 | 20.1 |
| Graphite Meter without loaded latency · Chrome | 955.5 / 953.7 | 0.280 | **0.820** | **19.7** |
| LibreSpeed · Chrome | 956.5 / 949.0 | 0.476 | 6.368 | 80.2 |
| LibreSpeed Go backend · Chrome | 955.0 / 953.5 | 0.412 | 5.840 | 48.2 |
| LibreSpeed Rust backend · Chrome | 953.0 / 952.0 | 0.340 | 4.320 | 22.5 |
| OpenSpeedTest · Chrome | 954.1 / 953.4 | **0.177** | 3.673 | 29.3 |
| Graphite Meter Terminal | 956.5 / 956.4 | 0.130 | 0.721 | 18.5 |
| Graphite Meter Terminal without loaded latency | 956.5 / 956.4 | **0.123** | **0.702** | **18.3** |
| LibreSpeed CLI | 941.2 / 871.0 | 0.280 | 2.449 | 68.8 |
| iperf3 (reference) | 956.4 / 956.4 | 0.208 | 5.538 | 19.3 |
| Graphite Meter Browser · Firefox | 955.5 / 955.4 | 0.290 | 1.154 | 20.7 |
| Graphite Meter without loaded latency · Firefox | 953.9 / 955.3 | 0.313 | **1.045** | **19.8** |
| LibreSpeed · Firefox | 943.5 / 893.0 | 0.547 | 5.826 | 85.7 |
| LibreSpeed Go backend · Firefox | 949.5 / 903.5 | 0.492 | 5.366 | 51.9 |
| LibreSpeed Rust backend · Firefox | 940.0 / 903.5 | 0.443 | 3.910 | 26.2 |
| OpenSpeedTest · Firefox | 953.5 / 948.5 | **0.208** | 4.788 | 29.5 |

Absolute server CPU time for the complete 1 Gbit/s test and each transfer phase.

| Tool or client | Download (CPU s) | Upload (CPU s) | Test total (CPU s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.21 | 0.59 | 0.81 |
| Graphite Meter without loaded latency · Chrome | 0.18 | 0.55 | 0.76 |
| LibreSpeed · Chrome | 0.40 | 6.45 | 6.88 |
| LibreSpeed Go backend · Chrome | 0.35 | 6.04 | 6.44 |
| LibreSpeed Rust backend · Chrome | 0.29 | 4.45 | 4.81 |
| OpenSpeedTest · Chrome | 0.32 | 5.60 | 5.94 |
| Graphite Meter Terminal | 0.18 | 1.04 | 1.23 |
| Graphite Meter Terminal without loaded latency | 0.17 | 1.02 | 1.19 |
| LibreSpeed CLI | 0.55 | 4.41 | 5.11 |
| iperf3 (reference) | 0.32 | 8.40 | 8.72 |
| Graphite Meter Browser · Firefox | 0.32 | 0.83 | 1.16 |
| Graphite Meter without loaded latency · Firefox | 0.26 | 0.64 | 0.89 |
| LibreSpeed · Firefox | 0.45 | 5.42 | 5.88 |
| LibreSpeed Go backend · Firefox | 0.40 | 5.02 | 5.43 |
| LibreSpeed Rust backend · Firefox | 0.37 | 3.61 | 4.04 |
| OpenSpeedTest · Firefox | 0.38 | 7.30 | 7.71 |

### Graphite Meter without loaded latency

Within each client, both profiles use the same server build, automatic connection settings, and transfer durations. The variant skips the app’s idle-latency stage and loaded probes. Each cell is **without loaded latency minus default** on the same VM and pass, summarized across VMs as median [middle 50%]. Total server CPU includes the skipped idle stage.

| Path | Client | Download (Mbit/s) | Upload (Mbit/s) | Download server CPU (s/GB) | Upload server CPU (s/GB) | Total server CPU (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 Gbit/s | Chrome | -0.5 [-0.9, -0.4] (n=15) | +1.2 [+0.4, +7.3] (n=15) | -0.059 [-0.100, +0.039] (n=15) | -0.003 [-0.040, +0.033] (n=15) | -0.08 [-0.19, 0.00] (n=15) |
| 1 Gbit/s | Firefox | -0.6 [-2.4, +0.1] (n=15) | -0.1 [-1.0, +1.5] (n=15) | -0.017 [-0.054, +0.048] (n=15) | -0.035 [-0.111, 0.000] (n=15) | -0.17 [-0.30, +0.01] (n=15) |
| 1 Gbit/s | Terminal | +0.1 [0.0, +0.2] (n=15) | 0.0 [-0.1, +0.1] (n=15) | -0.011 [-0.017, -0.007] (n=15) | -0.024 [-0.034, +0.021] (n=15) | -0.06 [-0.09, 0.00] (n=15) |
| 10 Gbit/s | Terminal | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | 0.000 [-0.001, +0.001] (n=15) | -0.001 [-0.005, +0.001] (n=15) | -0.05 [-0.11, -0.03] (n=15) |
| Unshaped | Terminal | +770.0 [+400.0, +942.5] (n=15) | +170.0 [-502.5, +985.0] (n=15) | -0.001 [-0.002, -0.001] (n=15) | 0.000 [-0.001, 0.000] (n=15) | -0.08 [-0.09, -0.07] (n=15) |

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
| Graphite Meter Browser · Chrome | 954.4 | 1,026.5 | 939.0 [929.2, 946.3] (n=15) | 4/30 |
| Graphite Meter without loaded latency · Chrome | 953.7 | 1,016.3 | 938.5 [934.2, 942.2] (n=15) | 7/30 |
| LibreSpeed · Chrome | 949.0 | 1,012.0 | 953.2 [935.0, 957.2] (n=15) | 3/30 |
| LibreSpeed Go backend · Chrome | 953.5 | 1,019.6 | 954.6 [946.1, 961.2] (n=15) | 9/30 |
| LibreSpeed Rust backend · Chrome | 952.0 | 1,001.1 | 949.8 [945.5, 955.3] (n=15) | 7/30 |
| OpenSpeedTest · Chrome | 953.4 | 1,027.8 | 972.1 [967.1, 978.5] (n=15) | 8/30 |
| Graphite Meter Browser · Firefox | 955.4 | 1,024.5 | 940.1 [931.9, 942.0] (n=15) | 9/30 |
| Graphite Meter without loaded latency · Firefox | 955.3 | 1,028.4 | 941.5 [933.8, 947.3] (n=15) | 9/30 |
| LibreSpeed · Firefox | 893.0 | 959.9 | 902.9 [892.8, 911.3] (n=15) | 0/30 |
| LibreSpeed Go backend · Firefox | 903.5 | 960.7 | 909.3 [895.5, 912.0] (n=15) | 0/30 |
| LibreSpeed Rust backend · Firefox | 903.5 | 957.7 | 906.7 [897.0, 910.3] (n=15) | 0/30 |
| OpenSpeedTest · Firefox | 948.5 | 1,027.9 | 957.7 [951.9, 962.9] (n=15) | 3/30 |
| Graphite Meter Terminal | 956.4 | 1,026.1 | 978.4 [977.5, 979.6] (n=15) | 14/30 |
| Graphite Meter Terminal without loaded latency | 956.4 | 1,027.1 | 983.2 [981.4, 984.3] (n=15) | 14/30 |
| LibreSpeed CLI | 871.0 | 1,014.9 | 935.5 [925.5, 940.7] (n=15) | 0/30 |
| iperf3 (reference) | 956.4 | 1,025.9 | 980.9 [979.7, 981.4] (n=15) | — |

**30 Mbit/s upload, deep FIFO**

| Tool or client | App rate | Shaper | Server RX | Above iperf3 |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 28.7 | 30.9 | 29.4 [29.4, 29.5] (n=15) | 12/30 |
| Graphite Meter without loaded latency · Chrome | 28.7 | 30.9 | 29.4 [29.4, 29.5] (n=15) | 15/30 |
| LibreSpeed · Chrome | 29.6 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 24/30 |
| LibreSpeed Go backend · Chrome | 28.8 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 16/30 |
| LibreSpeed Rust backend · Chrome | 28.6 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 12/30 |
| OpenSpeedTest · Chrome | 30.7 | 30.9 | 29.7 [29.7, 29.7] (n=15) | 30/30 |
| Graphite Meter Browser · Firefox | 28.7 | 30.9 | 29.4 [29.4, 29.5] (n=15) | 15/30 |
| Graphite Meter without loaded latency · Firefox | 28.7 | 30.9 | 29.5 [29.4, 29.5] (n=15) | 14/30 |
| LibreSpeed · Firefox | 29.0 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 22/30 |
| LibreSpeed Go backend · Firefox | 29.1 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 22/30 |
| LibreSpeed Rust backend · Firefox | 29.0 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 19/30 |
| OpenSpeedTest · Firefox | 30.5 | 30.9 | 29.7 [29.7, 29.8] (n=15) | 28/30 |
| Graphite Meter Terminal | 28.7 | 30.9 | 29.5 [29.4, 29.6] (n=15) | 11/30 |
| Graphite Meter Terminal without loaded latency | 28.7 | 30.9 | 29.6 [29.6, 29.6] (n=15) | 14/30 |
| LibreSpeed CLI | 29.3 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 28/30 |
| iperf3 (reference) | 28.7 | 30.9 | 29.7 [29.7, 29.8] (n=15) | — |

### Idle latency against ICMP

The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference.
Each cell shows the median paired difference in ms [25th, 75th percentile] and number of VMs.

| Tool or client | 20 ms path | 40 ms path | 160 ms path |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | +0.3 [+0.2, +0.3] (n=15) | +0.3 [+0.2, +0.4] (n=15) | +0.4 [+0.3, +0.5] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — | — |
| LibreSpeed · Chrome | +0.2 [+0.1, +0.2] (n=15) | +0.2 [+0.2, +0.2] (n=15) | -0.1 [-0.1, +0.3] (n=15) |
| LibreSpeed Go backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, +0.1] (n=15) | -0.2 [-0.2, -0.1] (n=15) |
| LibreSpeed Rust backend · Chrome | 0.0 [-0.1, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.2 [-0.2, -0.1] (n=15) |
| OpenSpeedTest · Chrome | +0.3 [-0.1, +0.4] (n=15) | -0.1 [-0.1, +0.4] (n=15) | +0.4 [+0.3, +0.8] (n=15) |
| Graphite Meter Browser · Firefox | +0.9 [+0.9, +0.9] (n=15) | +1.0 [+0.9, +1.4] (n=15) | +0.8 [+0.8, +0.9] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — | — |
| LibreSpeed · Firefox | +1.4 [+1.1, +1.6] (n=15) | +0.9 [+0.9, +1.4] (n=15) | +1.4 [+1.3, +1.8] (n=15) |
| LibreSpeed Go backend · Firefox | +0.9 [+0.9, +0.9] (n=15) | +0.9 [+0.9, +1.4] (n=15) | +1.4 [+1.1, +1.8] (n=15) |
| LibreSpeed Rust backend · Firefox | +0.9 [+0.8, +1.1] (n=15) | +0.9 [+0.9, +1.1] (n=15) | +1.3 [+0.9, +1.3] (n=15) |
| OpenSpeedTest · Firefox | +0.3 [-0.1, +0.4] (n=15) | +0.9 [+0.6, +0.9] (n=15) | +0.8 [+0.6, +0.9] (n=15) |
| Graphite Meter Terminal | 0.0 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | -0.2 [-0.2, -0.1] (n=15) |
| Graphite Meter Terminal without loaded latency | — | — | — |
| LibreSpeed CLI | +0.1 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) |

### Latency under load on a FIFO

Each cell shows the app’s reported latency followed by the queue-based estimate, in ms.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 179.5 / 173.9 | 193.2 / 187.8 |
| Graphite Meter without loaded latency · Chrome | — / 161.1 | — / 183.7 |
| Graphite Meter Browser · Firefox | 183.0 / 175.2 | 193.5 / 187.4 |
| Graphite Meter without loaded latency · Firefox | — / 173.5 | — / 185.7 |
| Graphite Meter Terminal | 177.5 / 171.2 | 197.0 / 193.2 |
| Graphite Meter Terminal without loaded latency | — / 175.7 | — / 193.8 |

Paired app minus queue estimate in ms, summarized within VMs, then across VMs.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | +5.5 [+3.9, +7.7] (n=15) | +4.6 [+2.8, +5.9] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — |
| Graphite Meter Browser · Firefox | +7.0 [+5.7, +8.7] (n=15) | +5.4 [+3.4, +6.8] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — |
| Graphite Meter Terminal | +6.5 [+5.0, +7.7] (n=15) | +4.3 [+3.3, +4.8] (n=15) |
| Graphite Meter Terminal without loaded latency | — | — |

## Pooled pass tables

The tables below pool all retained completed passes for each configuration, including alternate
transports. Their comparison columns show the difference from the modeled TCP payload ceiling
when iperf3 reaches at least 98% of the model in both directions. QUIC rows show measured rates separately.
The matched comparison above uses the measured same-pass receiver rate.
Below-ceiling rates can reflect any constraint on the end-to-end transfer.

[100 Mbit/s](#100100-mbits-20-ms-rtt-fq_codel) · [1 Gbit/s](#11-gbits-20-ms-rtt-fq_codel) · [10 Gbit/s](#1010-gbits-2-ms-rtt-fq_codel-offloads-on) · [Deep FIFO](#30030-mbits-20-ms-rtt-200-ms-fifo) · [1% loss](#100100-mbits-40-ms-rtt-1--loss-each-way-fq_codel) · [0.1% loss](#11-gbits-40-ms-rtt-01--loss-each-way-fq_codel) · [160 ms RTT](#300300-mbits-160-ms-rtt-fq_codel) · [Competing traffic](#100100-mbits-20-ms-rtt-fq_codel-one-competing-flow-each-way) · [Reverse proxy](#11-gbits-20-ms-rtt-fq_codel-behind-nginx) · [Two servers](#two-servers-200200-mbits-path-each-20-ms-rtt-fq_codel) · [Unshaped](#unshaped-offloads-on-as-fast-as-the-host-allows)

<!-- pooled-pass-tables -->
Jobs: 15. Runs: 5490, of which 0 left out from blocks on a busy host. Hosts: AMD EPYC 9V45 96-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 9V74 80-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); Intel(R) Xeon(R) 6975P-C (4 CPUs, kernel 7.0.0-1014-aws, rootful); AMD EPYC 7763 64-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful).
Tools: Graphite Meter 0.14.5, LibreSpeed 6.3.1, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest 2.5.4, Graphite Meter terminal client 0.14.5, LibreSpeed CLI 1.0.15. Browsers: chrome 158.0.8127.36, firefox 160.0.1.

## 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.6 [95.5, 95.6] | -0.1 % | 20.4 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 95.7 [95.6, 95.7] | +0.0 % | 95.6 [95.6, 95.6] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.6, 95.6] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.6, 95.6] | -0.0 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 95.6 [95.6, 95.7] | -0.0 % | 95.6 [95.5, 95.6] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | +0.0 % | 95.6 [95.6, 95.7] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.7 [95.6, 95.7] | +0.1 % | 95.6 [95.6, 95.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.2 [95.2, 95.2] | -0.5 % | 96.2 [95.9, 96.6] | +0.6 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.8 [94.7, 94.8] | -0.9 % | 91.4 [90.9, 93.4] | -4.4 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.4 [95.2, 95.6] | -0.3 % | 95.6 [94.8, 96.1] | -0.0 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.3 [95.2, 95.7] | -0.4 % | 95.3 [94.6, 95.7] | -0.3 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.2 [95.1, 95.5] | -0.5 % | 95.3 [94.8, 96.0] | -0.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.2, 95.5] | -0.4 % | 95.3 [94.6, 96.0] | -0.4 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.3 [95.2, 95.5] | -0.4 % | 95.3 [94.9, 95.9] | -0.4 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.5 [95.4, 95.6] | -0.1 % | 96.0 [95.4, 96.6] | +0.4 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.6 [95.5, 95.7] | -0.0 % | 95.9 [95.4, 96.4] | +0.3 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.3 [955.8, 956.4] | -0.0 % | 954.3 [929.8, 955.8] | -0.2 % | 20.4 (20.1) | 21.1 (n/a) | 21.1 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 956.4 [956.4, 956.6] | -0.0 % | 956.4 [956.3, 956.5] | -0.0 % | 20.2 (20.1) | 20.3 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 953.2 [953.2, 953.2] | -0.3 % | 953.2 [953.1, 953.2] | -0.3 % | 20.2 (20.1) | 20.4 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 937.9 [937.7, 938.1] | n/a | 948.7 [948.7, 948.8] | n/a | 20.2 (20.1) | 20.3 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 956.5 [956.4, 956.7] | +0.0 % | 956.4 [956.4, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 955.6 [954.6, 956.4] | -0.1 % | 955.2 [952.9, 956.5] | -0.1 % | 21.0 (20.1) | 30.0 (n/a) | 22.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 950.8 [950.5, 951.2] | -0.6 % | 945.6 [940.0, 948.4] | -1.1 % | 20.4 (20.1) | 22.4 (n/a) | 23.1 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 948.1 [947.1, 949.8] | n/a | 806.3 [736.6, 825.6] | n/a | 20.4 (20.1) | 20.4 (n/a) | 22.7 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 955.6 [954.6, 956.3] | -0.1 % | 955.2 [941.4, 956.3] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 954.5 [952.4, 956.1] | -0.2 % | 955.3 [953.7, 956.4] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 947.0 [944.6, 953.3] | n/a | 752.0 [678.5, 816.6] | n/a | 20.5 (20.1) | 20.5 (n/a) | 21.1 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.4 [956.3, 956.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 956.0 [954.3, 958.8] | -0.0 % | 947.0 [942.5, 949.8] | -1.0 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 942.6 [936.7, 944.2] | -1.4 % | 871.2 [869.9, 872.4] | -8.9 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 942.5 [926.8, 953.0] | -1.5 % | 897.5 [879.5, 908.5] | -6.2 % | 21.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 955.0 [954.0, 956.8] | -0.1 % | 952.0 [949.3, 956.8] | -0.5 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 943.0 [927.3, 955.8] | -1.4 % | 904.0 [894.3, 908.5] | -5.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 945.0 [943.3, 947.0] | -1.2 % | 413.5 [411.0, 414.8] | -56.8 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 953.5 [952.0, 955.0] | -0.3 % | 951.5 [944.3, 955.8] | -0.5 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 942.5 [933.8, 953.8] | -1.5 % | 903.5 [896.3, 912.8] | -5.5 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 954.3 [952.0, 954.9] | -0.2 % | 953.2 [948.1, 956.7] | -0.3 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 954.1 [951.8, 955.3] | -0.2 % | 950.5 [944.0, 953.0] | -0.6 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 950.8 [948.9, 951.6] | -0.6 % | 935.6 [933.3, 940.1] | -2.2 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 9563.8 [9562.2, 9564.7] | -0.0 % | 5450.5 [3747.6, 5693.9] | -43.0 % | 2.2 (2.1) | 2.8 (n/a) | 3.9 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.1 (n/a) | 2.2 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 9530.0 [9530.0, 9530.0] | -0.4 % | 9530.0 [9530.0, 9530.0] | -0.4 % | 2.1 (2.1) | 7.0 (n/a) | 2.4 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 6800.0 [6500.0, 7045.0] | n/a | 7710.0 [6280.0, 7797.5] | n/a | 2.1 (2.1) | 3.2 (n/a) | 2.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 6198.8 [4431.6, 6518.2] | -35.2 % | 8517.3 [5180.9, 9156.9] | -10.9 % | 3.0 (2.1) | 21.0 (n/a) | 52.5 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 6867.5 [5539.4, 7001.0] | -28.2 % | 4638.4 [2667.8, 4738.6] | -51.5 % | 2.2 (2.1) | 3.4 (n/a) | 2.9 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 2504.6 [1919.2, 2581.8] | n/a | 1526.3 [772.5, 1553.1] | n/a | 2.2 (2.1) | 2.4 (n/a) | 4.6 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 9562.2 [9560.9, 9563.4] | -0.0 % | 5569.9 [3840.4, 5711.1] | -41.8 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 6778.0 [4760.9, 7016.3] | -29.1 % | 8938.3 [5493.2, 9293.4] | -6.5 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 2485.8 [1940.5, 2542.4] | n/a | 1158.0 [705.0, 1193.9] | n/a | 2.2 (2.1) | 2.5 (n/a) | 3.2 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.3 [9564.2, 9564.3] | +0.0 % | 9564.3 [9564.2, 9564.3] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 9518.5 [9360.0, 9551.3] | -0.5 % | 5049.0 [3278.3, 5226.8] | -47.2 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9355.6 [9355.1, 9356.2] | -2.2 % | 8217.2 [8168.0, 8274.3] | -14.1 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 3275.5 [2209.5, 3438.8] | -65.8 % | 4009.5 [3204.3, 4213.3] | -58.1 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 9532.5 [9302.5, 9559.3] | -0.3 % | 5098.5 [3286.0, 5227.0] | -46.7 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 3142.5 [2329.8, 3362.3] | -67.1 % | 3912.0 [3209.5, 4112.3] | -59.1 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 4398.0 [4137.8, 4442.5] | -54.0 % | 3298.5 [2553.0, 3330.8] | -65.5 % | 2.2 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 9539.5 [9435.3, 9559.8] | -0.3 % | 5130.0 [3223.5, 5258.8] | -46.4 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 3160.5 [2204.3, 3448.0] | -67.0 % | 3881.5 [3159.8, 4122.8] | -59.4 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 9551.6 [9407.5, 9562.2] | -0.1 % | 5357.6 [3336.8, 5447.6] | -44.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 5262.5 [2786.3, 5598.6] | -45.0 % | 3986.1 [3173.5, 4187.5] | -58.3 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 5479.6 [4483.2, 5826.2] | -42.7 % | 4002.1 [2446.3, 4142.2] | -58.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.4 (20.1) | 180.9 (176.4) | 193.2 (188.5) |
| Graphite Meter Terminal | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.6, 28.7] | -0.1 % | 20.2 (20.1) | 178.0 (171.1) | 198.0 (193.3) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.0 % | n/a (20.1) | n/a (172.4) | n/a (193.7) |
| Graphite Meter Browser, firefox | 30/30 | payload | 286.9 [286.9, 286.9] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 21.0 (20.1) | 182.5 (175.8) | 192.5 (188.2) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (175.7) | n/a (184.9) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (174.6) | n/a (184.5) |
| iperf3 (reference) | 30/30 | payload | 286.9 [286.9, 287.0] | -0.0 % | 28.7 [28.6, 28.7] | -0.1 % | n/a (20.1) | n/a (176.7) | n/a (186.8) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [284.0, 287.0] | -0.3 % | 29.6 [29.1, 30.0] | +3.0 % | 20.3 (20.1) | n/a (163.3) | n/a (185.5) |
| LibreSpeed CLI | 30/30 | payload | 283.0 [281.4, 284.2] | -1.4 % | 29.0 [29.0, 29.6] | +1.2 % | 20.2 (20.1) | n/a (173.4) | n/a (174.3) |
| LibreSpeed, firefox | 30/30 | payload | 286.0 [283.3, 286.0] | -0.3 % | 29.1 [28.7, 29.4] | +1.2 % | 21.0 (20.1) | n/a (164.0) | n/a (186.1) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 285.0 [283.3, 287.0] | -0.7 % | 28.7 [28.2, 29.4] | +0.0 % | 20.1 (20.1) | n/a (160.8) | n/a (167.0) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 285.0 [282.5, 287.0] | -0.7 % | 29.0 [28.7, 29.4] | +1.2 % | 21.0 (20.1) | n/a (160.8) | n/a (186.0) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 28.4 [28.0, 29.3] | -1.0 % | 20.1 (20.1) | n/a (161.0) | n/a (169.3) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 287.0 [286.0, 287.0] | +0.0 % | 29.0 [28.5, 29.5] | +1.1 % | 21.0 (20.1) | n/a (153.4) | n/a (187.3) |
| OpenSpeedTest, chrome | 30/30 | payload | 286.9 [286.2, 287.2] | -0.0 % | 31.1 [29.8, 31.6] | +8.4 % | 20.0 (20.1) | n/a (160.1) | n/a (196.8) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.5 [285.9, 287.0] | -0.1 % | 30.0 [29.8, 30.6] | +4.6 % | 20.0 (20.1) | n/a (160.5) | n/a (197.5) |

## 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 20.0 [19.6, 20.8] | n/a | 20.2 [19.2, 20.9] | n/a | 40.5 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 19.8 [19.3, 20.4] | n/a | 19.5 [19.0, 20.4] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 19.5 [19.0, 20.5] | n/a | 19.8 [18.9, 20.7] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 19.6 [19.0, 20.3] | n/a | 19.3 [18.6, 20.7] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 19.5 [19.1, 20.1] | n/a | 20.2 [18.6, 20.8] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 19.9 [19.5, 20.6] | n/a | 20.0 [19.5, 20.9] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 12.9 [12.4, 13.3] | n/a | 12.8 [12.3, 13.1] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 16.9 [16.2, 17.5] | n/a | 9.5 [9.1, 10.2] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 11.3 [10.7, 12.2] | n/a | 11.8 [11.3, 12.4] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 21.1 [20.1, 22.6] | n/a | 9.2 [8.8, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 16.6 [16.1, 17.1] | n/a | 9.5 [9.1, 10.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 20.9 [20.1, 21.6] | n/a | 9.6 [9.1, 10.3] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 17.1 [16.4, 17.6] | n/a | 9.6 [9.0, 10.2] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 20.9 [20.1, 21.9] | n/a | 9.5 [9.3, 10.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 19.3 [18.8, 20.1] | n/a | 21.3 [20.8, 22.7] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.3 [18.6, 19.8] | n/a | 21.6 [20.3, 22.4] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 94.6 [85.5, 101.7] | n/a | 100.0 [92.7, 107.5] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 89.4 [84.5, 95.5] | n/a | 87.7 [83.3, 91.3] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 13.8 [12.7, 15.5] | n/a | 14.2 [12.3, 16.9] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.2 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 91.0 [64.2, 118.2] | n/a | 147.8 [102.4, 179.0] | n/a | 40.3 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 86.3 [83.1, 91.0] | n/a | 87.1 [80.8, 90.9] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 91.3 [86.9, 97.3] | n/a | 101.6 [90.9, 107.8] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 14.6 [12.3, 17.0] | n/a | 15.6 [13.9, 18.6] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 108.6 [73.4, 136.5] | n/a | 26.2 [23.7, 31.6] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 91.1 [84.1, 95.3] | n/a | 94.1 [86.9, 101.0] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 92.8 [84.1, 98.8] | n/a | 101.1 [90.0, 114.7] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 88.1 [67.4, 127.6] | n/a | 27.8 [24.8, 32.5] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 48.9 [47.5, 52.5] | n/a | 49.9 [47.7, 55.9] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 98.0 [90.2, 111.0] | n/a | 38.5 [34.4, 40.5] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 57.5 [53.2, 62.2] | n/a | 48.9 [44.1, 54.0] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 138.0 [120.0, 151.5] | n/a | 37.8 [35.0, 42.3] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 89.8 [82.2, 108.8] | n/a | 56.0 [43.6, 80.4] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 150.0 [130.5, 167.0] | n/a | 38.2 [34.8, 41.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 13.2 [10.8, 15.8] | n/a | 11.8 [11.1, 13.0] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 101.0 [86.2, 116.5] | n/a | 61.7 [51.5, 75.7] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 134.0 [124.0, 150.5] | n/a | 38.2 [34.0, 42.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 75.8 [73.8, 79.0] | n/a | 94.5 [85.8, 103.2] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 77.8 [74.4, 82.5] | n/a | 96.4 [86.6, 99.0] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 12.0 [10.4, 13.6] | n/a | 14.1 [11.4, 16.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 281.1 [262.0, 284.8] | n/a | 263.5 [259.5, 266.2] | n/a | 160.5 (160.2) | 160.3 (n/a) | 160.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 283.1 [279.7, 284.8] | n/a | 281.5 [278.7, 283.4] | n/a | 160.0 (160.2) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 274.6 [267.0, 277.0] | n/a | 281.5 [279.7, 283.4] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 282.5 [276.9, 285.5] | n/a | 265.1 [257.0, 269.7] | n/a | 161.0 (160.2) | 161.0 (n/a) | 161.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 272.2 [263.5, 280.0] | n/a | 253.4 [247.6, 255.6] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 271.9 [265.9, 276.4] | n/a | 254.8 [251.3, 256.9] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 205.5 [200.9, 231.6] | n/a | 225.6 [203.9, 243.5] | n/a | n/a (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 269.5 [262.0, 275.0] | n/a | 239.5 [230.3, 244.0] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 221.0 [219.1, 227.4] | n/a | 123.1 [122.0, 123.5] | n/a | 160.2 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 271.0 [268.3, 275.0] | n/a | 227.5 [221.3, 234.8] | n/a | 162.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 270.0 [263.5, 273.8] | n/a | 230.0 [225.3, 234.0] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 274.0 [268.0, 277.0] | n/a | 225.5 [220.0, 233.8] | n/a | 162.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 271.5 [266.3, 277.0] | n/a | 232.0 [226.5, 238.0] | n/a | 160.0 (160.2) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 274.5 [270.0, 278.0] | n/a | 224.5 [217.3, 233.5] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 271.5 [267.9, 274.8] | n/a | 274.1 [270.1, 278.1] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 270.1 [267.2, 273.8] | n/a | 274.3 [270.7, 277.5] | n/a | 161.0 (160.2) | n/a (n/a) | n/a (n/a) |

## 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 78.6 [78.5, 78.7] | n/a | 20.5 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.8] | n/a | 20.2 (20.1) | 20.3 (n/a) | 20.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.9] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 80.3 [80.2, 80.3] | n/a | 78.6 [78.5, 78.7] | n/a | 21.0 (20.1) | 21.8 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 78.6 [78.5, 78.7] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 78.6 [78.5, 78.7] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 74.9 [74.9, 75.0] | n/a | 75.2 [75.0, 75.3] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.8 [77.7, 77.8] | n/a | 71.1 [70.1, 71.4] | n/a | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.4 [69.3, 69.4] | n/a | 68.8 [68.8, 69.4] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.1 [80.0, 80.2] | n/a | 70.0 [69.9, 71.3] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.8 [77.6, 77.8] | n/a | 72.5 [72.0, 72.6] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 80.0 [79.8, 80.1] | n/a | 70.2 [69.8, 71.2] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.7 [77.7, 77.8] | n/a | 72.5 [71.2, 72.7] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.1 [80.0, 80.3] | n/a | 69.9 [69.8, 71.0] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.1 [80.1, 80.2] | n/a | 81.1 [80.9, 81.4] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.2 [80.1, 80.3] | n/a | 80.7 [80.6, 81.7] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. iperf3 bypasses nginx and measures the direct shaped path as a control. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.3 [955.3, 956.5] | -0.0 % | 955.1 [952.2, 956.0] | -0.1 % | 20.5 (20.1) | 21.5 (n/a) | 22.6 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 954.3 [946.4, 956.1] | -0.2 % | 956.0 [955.5, 956.7] | -0.0 % | 21.0 (20.1) | 37.0 (n/a) | 25.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 955.5 [953.1, 956.1] | -0.1 % | 955.1 [951.8, 956.0] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 949.3 [942.8, 955.6] | -0.7 % | 956.2 [955.7, 956.9] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.3, 956.5] | -0.0 % | 956.4 [956.3, 956.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 955.5 [953.0, 957.0] | -0.1 % | 912.5 [902.5, 922.8] | -4.6 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 941.0 [922.3, 952.8] | -1.6 % | 867.5 [847.5, 879.5] | -9.3 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.0 [949.2, 953.5] | -0.5 % | 923.1 [919.3, 928.8] | -3.5 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 952.0 [949.5, 953.7] | -0.5 % | 916.4 [910.1, 920.0] | -4.2 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 382.5 [382.5, 382.5] | -0.0 % | 382.5 [382.3, 382.6] | -0.0 % | 20.4 (20.1) | 20.6 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | 20.2 (20.1) | 20.3 (n/a) | 20.2 (n/a) |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 382.5 [382.2, 382.6] | -0.0 % | 382.6 [382.5, 382.7] | -0.0 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 382.5 [382.5, 382.5] | -0.0 % | 382.5 [382.4, 382.7] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 382.6 [382.5, 382.6] | -0.0 % | 382.5 [382.4, 382.6] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.5 [382.5, 382.5] | -0.0 % | 382.6 [382.5, 382.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

## Unshaped, offloads on: as fast as the host allows

Unshaped single-test throughput on the runner’s virtual link. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Client CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | 24267.6 [14177.7, 24972.2] | 11971.8 [4945.7, 12371.9] | 0.10 | 11 | 0.86 |
| Graphite Meter Terminal | 30/30 | 80140.0 [43740.0, 81675.0] | 168800.0 [76605.0, 172050.0] | 0.06 | 9 | 0.09 |
| Graphite Meter Terminal, HTTP/2 | 30/30 | 15380.0 [14037.5, 18442.5] | 18090.0 [16802.5, 18397.5] | 0.43 | 6 | 0.40 |
| Graphite Meter Terminal, HTTP/3 | 30/30 | 8155.0 [7877.5, 9065.0] | 8740.0 [7640.0, 9850.0] | 0.88 | 8 | 0.86 |
| Graphite Meter Terminal Terminal without loaded latency | 30/30 | 80930.0 [44552.5, 82417.5] | 169650.0 [76587.5, 172650.0] | 0.06 | 9 | 0.09 |
| Graphite Meter Browser, firefox | 30/30 | 7108.6 [5035.9, 7388.3] | 15393.2 [6632.9, 17113.2] | 0.15 | 11 | 1.30 |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | 24408.2 [14591.1, 25082.3] | 12373.1 [5309.8, 12826.9] | 0.10 | 11 | 0.82 |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | 7744.5 [5255.4, 8106.3] | 16571.8 [7024.4, 17586.1] | 0.15 | 11 | 1.14 |
| iperf3 (reference) | 30/30 | 61646.0 [29914.9, 62957.6] | 91569.6 [44242.4, 94137.4] | 0.10 | 48 | 0.12 |
| LibreSpeed, chrome | 30/30 | 14507.0 [10509.0, 15916.0] | 10519.0 [4259.0, 10960.3] | 0.28 | 82 | 1.18 |
| LibreSpeed CLI | 30/30 | 48482.6 [28664.8, 49440.5] | 26796.3 [18965.9, 27569.6] | 0.20 | 73 | 0.25 |
| LibreSpeed, firefox | 30/30 | 3105.0 [2167.3, 3266.8] | 4629.5 [3390.3, 4879.0] | 0.26 | 87 | 3.62 |
| LibreSpeed Go backend, chrome | 30/30 | 15140.0 [10599.3, 15733.3] | 10470.0 [4275.8, 10889.5] | 0.30 | 49 | 1.17 |
| LibreSpeed Go backend, firefox | 30/30 | 3062.0 [2129.5, 3285.0] | 4683.0 [3379.8, 4853.0] | 0.26 | 53 | 3.57 |
| LibreSpeed Rust backend, chrome | 30/30 | 14496.0 [10570.5, 15485.3] | 10470.0 [4171.0, 10929.0] | 0.23 | 23 | 1.22 |
| LibreSpeed Rust backend, firefox | 30/30 | 2911.0 [2157.5, 3172.3] | 4689.5 [3375.8, 4852.5] | 0.21 | 26 | 3.64 |
| OpenSpeedTest, chrome | 30/30 | 13600.7 [10082.4, 14745.5] | 11109.8 [4364.4, 11404.1] | 0.16 | 24 | 1.16 |
| OpenSpeedTest, firefox | 30/30 | 5366.9 [2711.9, 5695.8] | 4754.3 [3346.4, 4931.4] | 0.16 | 22 | 3.02 |
