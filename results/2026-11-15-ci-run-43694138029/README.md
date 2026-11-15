# GitHub runner benchmark, 15.11.2026

**5,190/5,190** retained runs completed across **15 runner jobs** (0 runs excluded by the busy-host rule).
The 25 and 40 Gbit/s shaped scenarios are skipped on these 4-vCPU runners. They require 8+ CPUs.

[Benchmark source at 17493717f18e880a5988dec32fe69fc834aeb161](https://github.com/zR-JB/selfhosted-speedtest-bench/tree/17493717f18e880a5988dec32fe69fc834aeb161) · [Workflow run and raw artifacts](https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/43694138029)
[Provenance and exact pins](provenance.json) · [Retained scalar measurements](measurements.json.gz) · [Server CPU by phase](server-cpu.md) · [Bench overview](../../README.md) · [Previous report](../2026-11-14-ci-run-43601751633)

The workflow stores the detailed artifacts and screenshots for its retention window. The scalar archive
keeps the inputs used by the overview charts and tables. Read it with `gzip -dc measurements.json.gz`.
Provenance records the job order, CPU allocation, pinned releases and workload definitions.

To regenerate the overview tables and charts from the committed archive, run
`python3 bench/report.py 43694138029 --from-archive --rerender` from the repository root.
The renderer uses Python 3 with Matplotlib. When this is the latest run, the command also updates
the root README. Regenerating the detailed pass tables requires all 15 job artifacts, Node.js 22 or later,
and the benchmark source revision in local Git history. Use
`python3 bench/report.py 43694138029 /path/to/artifacts --rerender` while they remain available.

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
| Graphite Meter Browser | **956.2** / 954.4 | **9.56** / 4.46 | 13.1 / 13.5 |
| Graphite Meter without loaded latency | 955.5 / **954.7** | **9.56** / **4.56** | 13.2 / 13.3 |
| LibreSpeed | 956.0 / 942.0 | 9.48 / 3.65 | 17.0 / 9.6 |
| LibreSpeed Go backend | 954.5 / 950.5 | 9.47 / 3.74 | 16.9 / 9.9 |
| LibreSpeed Rust backend | 954.0 / 948.5 | 9.43 / 3.69 | 16.8 / 9.8 |
| OpenSpeedTest | 952.8 / 954.5 | 9.52 / 3.80 | **19.3** / **22.1** |
| Graphite Meter Terminal | **956.4** / **956.4** | **9.56** / **9.56** | **19.5** / **20.3** |
| LibreSpeed CLI | 944.0 / 870.4 | 9.36 / 8.18 | 10.8 / 12.1 |
| iperf3 (reference) | 956.4 / 956.4 | 9.56 / 9.56 | 13.0 / 13.0 |

### 10 Gbit/s upload spread

Each cell shows the median [25th, 75th percentile] and number of VMs. The last column uses matched same-VM, same-pass iperf3 rates. A lower achieved rate can come from any part of the test setup.

Graphite Meter Browser’s same-pass upload difference from OpenSpeedTest in Chrome was **+0.79 Gbit/s** (middle 50% +0.65 to +0.90). Graphite Meter Browser reported more on **15/15 matched VMs**.

| Tool or client | Upload (Gbit/s) | Paired difference from iperf3 (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 4.46 [4.24, 5.81] (n=15) | -53.4 [-55.7, -39.3] (n=15) |
| Graphite Meter without loaded latency · Chrome | 4.56 [4.36, 5.93] (n=15) | -52.3 [-54.5, -38.0] (n=15) |
| LibreSpeed · Chrome | 3.65 [3.29, 4.82] (n=15) | -61.8 [-65.6, -49.6] (n=15) |
| LibreSpeed Go backend · Chrome | 3.74 [3.28, 4.87] (n=15) | -60.9 [-65.7, -49.0] (n=15) |
| LibreSpeed Rust backend · Chrome | 3.69 [3.24, 4.82] (n=15) | -61.4 [-66.1, -49.7] (n=15) |
| OpenSpeedTest · Chrome | 3.80 [3.39, 4.88] (n=15) | -60.3 [-64.5, -49.0] (n=15) |
| Graphite Meter Browser · Firefox | 5.77 [5.22, 8.17] (n=15) | -39.7 [-45.5, -14.6] (n=15) |
| Graphite Meter without loaded latency · Firefox | 6.21 [5.72, 8.33] (n=15) | -35.0 [-40.2, -12.9] (n=15) |
| LibreSpeed · Firefox | 3.26 [3.06, 3.95] (n=15) | -65.9 [-68.0, -58.7] (n=15) |
| LibreSpeed Go backend · Firefox | 3.19 [3.10, 3.97] (n=15) | -66.7 [-67.6, -58.5] (n=15) |
| LibreSpeed Rust backend · Firefox | 3.22 [3.06, 4.09] (n=15) | -66.3 [-68.0, -57.2] (n=15) |
| OpenSpeedTest · Firefox | 3.16 [2.89, 3.99] (n=15) | -67.0 [-69.8, -58.2] (n=15) |
| Graphite Meter Terminal | 9.56 [9.56, 9.56] (n=15) | 0.0 [0.0, 0.0] (n=15) |
| LibreSpeed CLI | 8.18 [7.98, 8.21] (n=15) | -14.5 [-16.5, -14.2] (n=15) |
| iperf3 (reference) | 9.56 [9.56, 9.56] (n=15) | — |

### Matched 1 Gbit/s agreement

Signed percentage differences from iperf3 on the same VM and pass. Each cell shows the median [25th, 75th percentile] and number of VMs after reducing the matched pass differences within each VM. Tests ran sequentially. App and iperf3 start times were a median of 2.9 minutes apart (maximum 10.0).

| Tool or client | Download difference (%) | Upload difference (%) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | **0.0** [-0.1, 0.0] (n=15) | **-0.2** [-0.5, -0.1] (n=15) |
| Graphite Meter without loaded latency · Chrome | -0.1 [-0.1, -0.1] (n=15) | **-0.2** [-0.3, 0.0] (n=15) |
| LibreSpeed · Chrome | **0.0** [-0.3, 0.0] (n=15) | -1.5 [-2.1, -1.2] (n=15) |
| LibreSpeed Go backend · Chrome | -0.2 [-0.4, -0.1] (n=15) | -0.6 [-0.8, -0.4] (n=15) |
| LibreSpeed Rust backend · Chrome | -0.3 [-0.3, 0.0] (n=15) | -0.8 [-1.1, -0.1] (n=15) |
| OpenSpeedTest · Chrome | -0.4 [-0.6, -0.2] (n=15) | **-0.2** [-0.7, 0.0] (n=15) |
| Graphite Meter Browser · Firefox | **-0.1** [-0.2, -0.1] (n=15) | **-0.4** [-0.6, -0.2] (n=15) |
| Graphite Meter without loaded latency · Firefox | **-0.1** [-0.2, 0.0] (n=15) | **-0.4** [-0.5, -0.1] (n=15) |
| LibreSpeed · Firefox | -2.2 [-3.1, -0.9] (n=15) | -6.3 [-7.2, -5.4] (n=15) |
| LibreSpeed Go backend · Firefox | -2.0 [-3.7, -0.8] (n=15) | -6.4 [-7.0, -5.3] (n=15) |
| LibreSpeed Rust backend · Firefox | -2.6 [-4.2, -1.3] (n=15) | -5.7 [-6.7, -4.8] (n=15) |
| OpenSpeedTest · Firefox | -0.4 [-0.5, -0.3] (n=15) | -0.8 [-1.0, -0.4] (n=15) |
| Graphite Meter Terminal | **0.0** [0.0, 0.0] (n=15) | **0.0** [0.0, 0.0] (n=15) |
| LibreSpeed CLI | -1.3 [-1.6, -1.3] (n=15) | -9.0 [-9.1, -8.8] (n=15) |

### Unshaped throughput and browser CPU

Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand.
Each maximum is the fastest retained pass in that direction. The two maxima can come from different passes. Browser CPU measures the client process tree over the full run per GB at the shaper.

| Tool or client | Median down / up (Gbit/s) | Max down / up (Gbit/s) | Browser CPU (s/GB) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 18.4 / 5.6 | 23.9 / 11.8 | 1.33 |
| Graphite Meter without loaded latency · Chrome | **19.0** / **5.8** | 25.1 / 12.1 | 1.25 |
| LibreSpeed · Chrome | 10.5 / 5.0 | 16.3 / 11.1 | 1.94 |
| LibreSpeed Go backend · Chrome | 10.7 / 5.0 | 16.2 / 11.1 | 1.93 |
| LibreSpeed Rust backend · Chrome | 10.7 / 5.0 | 15.8 / 11.1 | 1.96 |
| OpenSpeedTest · Chrome | 10.1 / 5.2 | 16.3 / 11.7 | 2.01 |
| Graphite Meter Browser · Firefox | 3.6 / 7.4 | 6.2 / 16.8 | 2.40 |
| Graphite Meter without loaded latency · Firefox | **4.1** / **7.8** | 6.7 / 17.2 | 2.06 |
| LibreSpeed · Firefox | 2.4 / 3.7 | 3.5 / 5.8 | 5.00 |
| LibreSpeed Go backend · Firefox | 2.4 / 3.7 | 3.4 / 5.8 | 5.01 |
| LibreSpeed Rust backend · Firefox | 2.4 / 3.7 | 3.4 / 5.7 | 5.09 |
| OpenSpeedTest · Firefox | 3.3 / 3.5 | 5.8 / 5.1 | 4.84 |
| Graphite Meter Terminal | **44.7** / **62.6** | 61.8 / 105.8 | — |
| LibreSpeed CLI | 38.3 / 23.8 | 54.0 / 31.9 | — |
| iperf3 (reference) | 41.4 / 57.3 | 63.9 / 96.3 | — |

#### Unshaped native upload by runner hardware

Upload medians in Gbit/s. “GM above iperf3” counts VMs after matching same-pass comparisons. CPU, kernel and runner conditions vary together. Groups with one VM show that VM’s median.

Graphite Meter Terminal had a higher upload rate than iperf3 on **11 of 15 VMs** after matching passes. The split was 0/4 on AWS-kernel VMs, 11/11 on Azure-kernel VMs.

| CPU and kernel | VMs | Graphite Meter Terminal | LibreSpeed CLI | iperf3 | GM above iperf3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| AMD EPYC 7763 64-Core Processor (7.0.0-1017-azure) | 3 | 61.8 | 16.1 | 44.0 | 3/3 |
| AMD EPYC 9V45 96-Core Processor (7.0.0-1017-azure) | 1 | 101.7 | 25.1 | 75.4 | 1/1 |
| AMD EPYC 9V74 80-Core Processor (7.0.0-1017-azure) | 2 | 63.0 | 18.7 | 43.4 | 2/2 |
| INTEL(R) XEON(R) PLATINUM 8573C (7.0.0-1017-azure) | 3 | 69.2 | 23.2 | 56.8 | 3/3 |
| Intel(R) Xeon(R) 6973P-C (7.0.0-1017-azure) | 2 | 95.5 | 30.6 | 78.5 | 2/2 |
| Intel(R) Xeon(R) 6975P-C (7.0.0-1014-aws) | 4 | 46.9 | 27.0 | 93.2 | 0/4 |

### Server resources at 1 Gbit/s

Server CPU is container CPU time per decimal GB of server-interface traffic during each phase,
counting bytes in both directions. Peak memory is the container’s per-run peak in decimal MB.
The adjacent reported rates show how much of the same shaped link each setup used. Browser CPU is
measured separately on the client. Native client CPU is unavailable.

| Tool or client | Down / up (Mbit/s) | Down CPU (s/GB) | Up CPU (s/GB) | Peak RAM (MB) |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 956.2 / 954.4 | 0.386 | 4.647 | **15.0** |
| Graphite Meter without loaded latency · Chrome | 955.5 / 954.7 | 0.334 | 4.981 | 15.2 |
| LibreSpeed · Chrome | 956.0 / 942.0 | 0.440 | 6.077 | 80.3 |
| LibreSpeed Go backend · Chrome | 954.5 / 950.5 | 0.384 | 5.119 | 48.2 |
| LibreSpeed Rust backend · Chrome | 954.0 / 948.5 | 0.336 | 3.748 | 22.5 |
| OpenSpeedTest · Chrome | 952.8 / 954.5 | **0.171** | **3.660** | 29.4 |
| Graphite Meter Terminal | 956.4 / 956.4 | **0.247** | 6.987 | **17.2** |
| LibreSpeed CLI | 944.0 / 870.4 | 0.305 | **2.091** | 68.7 |
| iperf3 (reference) | 956.4 / 956.4 | 0.215 | 5.238 | 19.2 |
| Graphite Meter Browser · Firefox | 955.2 / 952.9 | 0.374 | 5.141 | 15.2 |
| Graphite Meter without loaded latency · Firefox | 955.7 / 952.4 | 0.331 | 5.656 | **15.1** |
| LibreSpeed · Firefox | 935.5 / 896.0 | 0.519 | 5.190 | 86.1 |
| LibreSpeed Go backend · Firefox | 937.5 / 895.5 | 0.482 | 4.937 | 51.9 |
| LibreSpeed Rust backend · Firefox | 932.0 / 901.5 | 0.408 | **3.625** | 26.3 |
| OpenSpeedTest · Firefox | 952.7 / 948.6 | **0.224** | 3.905 | 29.5 |

Absolute server CPU time for the complete 1 Gbit/s test and each transfer phase.

| Tool or client | Download (CPU s) | Upload (CPU s) | Test total (CPU s) |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 0.23 | 3.67 | 3.82 |
| Graphite Meter without loaded latency · Chrome | 0.26 | 3.28 | 3.58 |
| LibreSpeed · Chrome | 0.38 | 6.31 | 6.72 |
| LibreSpeed Go backend · Chrome | 0.33 | 5.28 | 5.63 |
| LibreSpeed Rust backend · Chrome | 0.29 | 3.91 | 4.23 |
| OpenSpeedTest · Chrome | 0.31 | 5.61 | 5.92 |
| Graphite Meter Terminal | 0.35 | 10.09 | 10.47 |
| LibreSpeed CLI | 0.60 | 3.77 | 4.56 |
| iperf3 (reference) | 0.33 | 7.95 | 8.33 |
| Graphite Meter Browser · Firefox | 0.43 | 4.52 | 4.90 |
| Graphite Meter without loaded latency · Firefox | 0.38 | 4.33 | 4.64 |
| LibreSpeed · Firefox | 0.42 | 4.90 | 5.32 |
| LibreSpeed Go backend · Firefox | 0.39 | 4.68 | 5.15 |
| LibreSpeed Rust backend · Firefox | 0.34 | 3.33 | 3.80 |
| OpenSpeedTest · Firefox | 0.41 | 5.90 | 6.32 |

### Graphite Meter without loaded latency

Within each client, both profiles use the same server build, automatic connection settings, and transfer durations. The variant skips the app’s idle-latency stage and loaded probes. Each cell is **without loaded latency minus default** on the same VM and pass, summarized across VMs as median [middle 50%]. Total server CPU includes the skipped idle stage.

| Path | Client | Download (Mbit/s) | Upload (Mbit/s) | Download server CPU (s/GB) | Upload server CPU (s/GB) | Total server CPU (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 Gbit/s | Chrome | -0.4 [-1.2, +0.3] (n=15) | +0.8 [-0.3, +1.9] (n=15) | -0.024 [-0.061, +0.018] (n=15) | +0.106 [+0.001, +0.219] (n=15) | +0.10 [-0.89, +0.66] (n=15) |
| 1 Gbit/s | Firefox | +0.1 [-0.3, +0.8] (n=15) | +0.8 [-1.7, +2.9] (n=15) | -0.029 [-0.057, +0.016] (n=15) | +0.058 [+0.009, +0.254] (n=15) | -0.16 [-1.20, +0.62] (n=15) |

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
| Graphite Meter Browser · Chrome | 954.4 | 972.9 | 939.6 [928.9, 947.8] (n=15) | 0/30 |
| Graphite Meter without loaded latency · Chrome | 954.7 | 972.6 | 933.0 [925.6, 944.6] (n=15) | 8/30 |
| LibreSpeed · Chrome | 942.0 | 973.1 | 956.5 [952.8, 958.7] (n=15) | 0/30 |
| LibreSpeed Go backend · Chrome | 950.5 | 973.8 | 957.5 [949.0, 961.1] (n=15) | 6/30 |
| LibreSpeed Rust backend · Chrome | 948.5 | 973.5 | 955.6 [951.5, 960.1] (n=15) | 10/30 |
| OpenSpeedTest · Chrome | 954.5 | 972.9 | 973.9 [970.0, 976.9] (n=15) | 7/30 |
| Graphite Meter Browser · Firefox | 952.9 | 973.2 | 941.4 [938.8, 955.9] (n=15) | 5/30 |
| Graphite Meter without loaded latency · Firefox | 952.4 | 973.3 | 944.1 [933.0, 950.7] (n=15) | 1/30 |
| LibreSpeed · Firefox | 896.0 | 959.0 | 900.3 [893.1, 907.5] (n=15) | 0/30 |
| LibreSpeed Go backend · Firefox | 895.5 | 957.1 | 906.1 [898.1, 916.1] (n=15) | 0/30 |
| LibreSpeed Rust backend · Firefox | 901.5 | 957.0 | 905.2 [903.8, 910.1] (n=15) | 0/30 |
| OpenSpeedTest · Firefox | 948.6 | 973.3 | 957.3 [947.9, 962.8] (n=15) | 6/30 |
| Graphite Meter Terminal | 956.4 | 973.3 | 981.6 [980.5, 981.9] (n=15) | 20/30 |
| LibreSpeed CLI | 870.4 | 963.9 | 937.9 [930.0, 939.6] (n=15) | 0/30 |
| iperf3 (reference) | 956.4 | 972.0 | 984.0 [981.4, 986.5] (n=15) | — |

**30 Mbit/s upload, deep FIFO**

| Tool or client | App rate | Shaper | Server RX | Above iperf3 |
| --- | ---: | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | 28.7 | 30.9 | 29.4 [29.4, 29.4] (n=15) | 15/30 |
| Graphite Meter without loaded latency · Chrome | 28.7 | 30.9 | 29.4 [29.4, 29.5] (n=15) | 15/30 |
| LibreSpeed · Chrome | 29.8 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 28/30 |
| LibreSpeed Go backend · Chrome | 29.1 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 18/30 |
| LibreSpeed Rust backend · Chrome | 28.7 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 14/30 |
| OpenSpeedTest · Chrome | 30.9 | 30.9 | 29.7 [29.6, 29.8] (n=15) | 29/30 |
| Graphite Meter Browser · Firefox | 28.7 | 30.9 | 29.4 [29.3, 29.4] (n=15) | 16/30 |
| Graphite Meter without loaded latency · Firefox | 28.7 | 30.9 | 29.4 [29.4, 29.4] (n=15) | 16/30 |
| LibreSpeed · Firefox | 29.3 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 25/30 |
| LibreSpeed Go backend · Firefox | 28.9 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 20/30 |
| LibreSpeed Rust backend · Firefox | 29.1 | 30.9 | 29.8 [29.8, 29.9] (n=15) | 21/30 |
| OpenSpeedTest · Firefox | 30.8 | 30.9 | 29.8 [29.8, 29.8] (n=15) | 30/30 |
| Graphite Meter Terminal | 28.7 | 30.9 | 29.5 [29.5, 29.5] (n=15) | 14/30 |
| LibreSpeed CLI | 29.3 | 30.9 | 29.8 [29.7, 29.8] (n=15) | 27/30 |
| iperf3 (reference) | 28.7 | 31.0 | 29.8 [29.8, 29.8] (n=15) | — |

### Idle latency against ICMP

The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference.
Each cell shows the median paired difference in ms [25th, 75th percentile] and number of VMs.

| Tool or client | 20 ms path | 40 ms path | 160 ms path |
| --- | ---: | ---: | ---: |
| Graphite Meter Browser · Chrome | +0.2 [+0.2, +0.3] (n=15) | +0.3 [+0.3, +0.4] (n=15) | +0.4 [+0.3, +0.4] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — | — |
| LibreSpeed · Chrome | +0.1 [+0.1, +0.2] (n=15) | +0.2 [+0.2, +0.3] (n=15) | -0.1 [-0.1, +0.4] (n=15) |
| LibreSpeed Go backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, +0.1] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed Rust backend · Chrome | 0.0 [0.0, 0.0] (n=15) | 0.0 [0.0, 0.0] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| OpenSpeedTest · Chrome | +0.4 [-0.1, +0.6] (n=15) | +0.4 [-0.1, +0.8] (n=15) | +0.8 [+0.4, +0.9] (n=15) |
| Graphite Meter Browser · Firefox | +0.9 [+0.9, +0.9] (n=15) | +1.0 [+0.9, +1.8] (n=15) | +0.9 [+0.8, +0.9] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — | — |
| LibreSpeed · Firefox | +1.4 [+0.9, +1.9] (n=15) | +1.4 [+0.9, +1.4] (n=15) | +1.8 [+1.4, +1.9] (n=15) |
| LibreSpeed Go backend · Firefox | +0.9 [+0.6, +1.4] (n=15) | +1.3 [+0.9, +1.4] (n=15) | +1.4 [+0.9, +1.8] (n=15) |
| LibreSpeed Rust backend · Firefox | +1.4 [+0.9, +1.4] (n=15) | +1.0 [+0.9, +1.3] (n=15) | +1.3 [+0.9, +1.8] (n=15) |
| OpenSpeedTest · Firefox | +0.4 [-0.1, +0.4] (n=15) | +0.4 [+0.4, +0.9] (n=15) | +0.8 [+0.4, +0.9] (n=15) |
| Graphite Meter Terminal | +0.1 [0.0, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | -0.1 [-0.2, -0.1] (n=15) |
| LibreSpeed CLI | +0.1 [+0.1, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) | +0.1 [+0.1, +0.1] (n=15) |

### Latency under load on a FIFO

Each cell shows the app’s reported latency followed by the queue-based estimate, in ms.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | 169.7 / 160.6 | 186.8 / 183.8 |
| Graphite Meter without loaded latency · Chrome | — / 165.5 | — / 184.4 |
| Graphite Meter Browser · Firefox | 167.2 / 159.4 | 182.5 / 179.9 |
| Graphite Meter without loaded latency · Firefox | — / 137.0 | — / 179.1 |
| Graphite Meter Terminal | 176.0 / 169.2 | 197.5 / 192.2 |

Paired app minus queue estimate in ms, summarized within VMs, then across VMs.

| Tool or client | During download (ms) | During upload (ms) |
| --- | ---: | ---: |
| Graphite Meter Browser · Chrome | +9.4 [+6.4, +10.5] (n=15) | +3.8 [+2.5, +6.0] (n=15) |
| Graphite Meter without loaded latency · Chrome | — | — |
| Graphite Meter Browser · Firefox | +9.6 [+8.7, +13.1] (n=15) | +3.6 [+2.9, +4.8] (n=15) |
| Graphite Meter without loaded latency · Firefox | — | — |
| Graphite Meter Terminal | +6.3 [+4.9, +7.6] (n=15) | +5.1 [+4.1, +6.4] (n=15) |

## Pooled pass tables

The tables below pool all retained completed passes for each configuration, including alternate
transports. Their comparison columns show the difference from the modeled TCP payload ceiling
when iperf3 reaches at least 98% of the model in both directions. QUIC rows show measured rates separately.
The matched comparison above uses the measured same-pass receiver rate.
Below-ceiling rates can reflect any constraint on the end-to-end transfer.

[100 Mbit/s](#100100-mbits-20-ms-rtt-fq_codel) · [1 Gbit/s](#11-gbits-20-ms-rtt-fq_codel) · [10 Gbit/s](#1010-gbits-2-ms-rtt-fq_codel-offloads-on) · [Deep FIFO](#30030-mbits-20-ms-rtt-200-ms-fifo) · [1% loss](#100100-mbits-40-ms-rtt-1--loss-each-way-fq_codel) · [0.1% loss](#11-gbits-40-ms-rtt-01--loss-each-way-fq_codel) · [160 ms RTT](#300300-mbits-160-ms-rtt-fq_codel) · [Competing traffic](#100100-mbits-20-ms-rtt-fq_codel-one-competing-flow-each-way) · [Reverse proxy](#11-gbits-20-ms-rtt-fq_codel-behind-nginx) · [Two servers](#two-servers-200200-mbits-path-each-20-ms-rtt-fq_codel) · [Unshaped](#unshaped-offloads-on-as-fast-as-the-host-allows)

<!-- pooled-pass-tables -->
Jobs: 15. Runs: 5190, of which 0 left out from blocks on a busy host. Hosts: AMD EPYC 9V45 96-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); Intel(R) Xeon(R) 6975P-C (4 CPUs, kernel 7.0.0-1014-aws, rootful); Intel(R) Xeon(R) 6973P-C (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 7763 64-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful); INTEL(R) XEON(R) PLATINUM 8573C (4 CPUs, kernel 7.0.0-1017-azure, rootful); AMD EPYC 9V74 80-Core Processor (4 CPUs, kernel 7.0.0-1017-azure, rootful).
Tools: Graphite Meter 0.14.3, LibreSpeed 6.3.1, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest 2.5.4, Graphite Meter terminal client 0.14.3, LibreSpeed CLI 1.0.14. Browsers: chrome 157.0.8103.78, firefox 160.0.

## 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.5 [95.4, 95.6] | -0.2 % | 20.3 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.6 [95.6, 95.7] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.4 [95.3, 95.5] | -0.2 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 95.6 [95.6, 95.6] | -0.0 % | 95.5 [95.4, 95.5] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 95.6 [95.6, 95.7] | +0.0 % | 95.4 [95.3, 95.6] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 95.6 [95.5, 95.7] | -0.0 % | 95.6 [95.6, 95.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.2 [95.2, 95.3] | -0.5 % | 96.0 [95.7, 96.6] | +0.4 % | 20.3 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 94.8 [94.7, 94.8] | -0.9 % | 91.5 [91.4, 93.0] | -4.3 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 95.3 [95.2, 95.5] | -0.4 % | 95.5 [94.6, 96.4] | -0.2 % | 21.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.3 [95.2, 95.7] | -0.4 % | 95.5 [94.3, 95.9] | -0.1 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 95.3 [95.0, 95.6] | -0.4 % | 95.5 [95.0, 96.1] | -0.1 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 95.3 [95.2, 95.6] | -0.4 % | 95.7 [94.8, 96.0] | +0.0 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 95.3 [95.1, 95.3] | -0.4 % | 95.3 [95.0, 95.9] | -0.3 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 95.5 [95.5, 95.6] | -0.1 % | 95.8 [95.1, 96.2] | +0.1 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 95.6 [95.5, 95.8] | -0.0 % | 96.4 [95.7, 97.0] | +0.8 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.2 [955.7, 956.5] | -0.0 % | 954.7 [952.2, 955.9] | -0.2 % | 20.4 (20.1) | 21.0 (n/a) | 20.6 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 956.4 [956.4, 956.5] | -0.0 % | 956.4 [956.3, 956.4] | -0.0 % | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 953.2 [953.2, 953.2] | -0.3 % | 953.2 [953.2, 953.2] | -0.3 % | 20.2 (20.1) | 20.3 (n/a) | 20.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 937.9 [937.8, 938.1] | n/a | 948.7 [948.7, 948.8] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.3 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 955.1 [953.9, 956.0] | -0.1 % | 953.8 [950.1, 955.4] | -0.3 % | 21.0 (20.1) | 30.8 (n/a) | 21.5 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 950.8 [950.8, 951.0] | -0.6 % | 945.9 [941.4, 947.7] | -1.1 % | 20.4 (20.1) | 21.4 (n/a) | 22.9 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 949.2 [946.2, 952.1] | n/a | 795.3 [658.2, 854.3] | n/a | 20.4 (20.1) | 20.5 (n/a) | 21.9 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 955.6 [954.7, 956.1] | -0.1 % | 955.1 [953.9, 956.3] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 955.4 [954.0, 956.4] | -0.1 % | 954.2 [951.4, 955.4] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 945.3 [944.1, 950.7] | n/a | 777.7 [678.1, 813.7] | n/a | 20.5 (20.1) | 20.5 (n/a) | 21.5 (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.4 [956.3, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 955.0 [954.0, 957.0] | -0.1 % | 942.0 [937.3, 945.0] | -1.5 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 943.9 [941.5, 944.4] | -1.3 % | 870.4 [869.3, 871.5] | -9.0 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 939.5 [925.0, 949.0] | -1.8 % | 897.0 [888.5, 904.0] | -6.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 954.0 [952.0, 955.8] | -0.3 % | 950.5 [946.3, 956.0] | -0.6 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 937.5 [924.0, 948.8] | -2.0 % | 896.5 [887.3, 909.0] | -6.3 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 946.0 [944.3, 948.0] | -1.1 % | 414.0 [412.3, 415.0] | -56.7 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 954.5 [952.3, 956.0] | -0.2 % | 950.5 [945.0, 957.0] | -0.6 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 933.0 [915.5, 944.8] | -2.4 % | 900.5 [888.8, 913.0] | -5.8 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 952.7 [950.9, 954.5] | -0.4 % | 954.3 [951.0, 955.9] | -0.2 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 952.7 [950.6, 954.7] | -0.4 % | 949.1 [946.1, 955.0] | -0.8 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 948.1 [946.5, 951.0] | -0.9 % | 935.4 [932.0, 939.5] | -2.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 9562.1 [9557.7, 9563.6] | -0.0 % | 4491.0 [4217.8, 5968.5] | -53.0 % | 2.2 (2.1) | 3.2 (n/a) | 3.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.1 (2.1) | 2.2 (n/a) | 2.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 9530.0 [9520.0, 9530.0] | -0.4 % | 9530.0 [9530.0, 9530.0] | -0.4 % | 2.1 (2.1) | 6.2 (n/a) | 2.2 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 6545.0 [6087.5, 7225.0] | n/a | 6635.0 [6290.0, 7860.0] | n/a | 2.1 (2.1) | 3.2 (n/a) | 2.3 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 3382.4 [3225.0, 4943.7] | -64.6 % | 5814.6 [5256.1, 8308.2] | -39.2 % | 3.0 (2.1) | 20.8 (n/a) | 54.8 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 5447.7 [5207.9, 6889.6] | -43.0 % | 3413.2 [2659.0, 4606.1] | -64.3 % | 2.2 (2.1) | 3.3 (n/a) | 3.0 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 2278.1 [2146.5, 2870.3] | n/a | 1021.7 [764.2, 1525.6] | n/a | 2.2 (2.1) | 2.4 (n/a) | 4.7 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 9562.6 [9552.1, 9564.4] | -0.0 % | 4600.6 [4328.1, 6084.1] | -51.9 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 3787.1 [3453.3, 5595.2] | -60.4 % | 6269.0 [5703.1, 8539.0] | -34.5 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 2286.1 [2097.1, 2935.3] | n/a | 929.2 [702.0, 1200.6] | n/a | 2.2 (2.1) | 2.5 (n/a) | 3.7 (n/a) |
| iperf3 (reference) | 30/30 | payload | 9564.3 [9564.2, 9564.3] | +0.0 % | 9564.3 [9564.2, 9564.3] | +0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 9504.0 [9237.0, 9542.5] | -0.6 % | 3669.0 [3273.3, 4936.0] | -61.6 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 9355.2 [9354.7, 9355.9] | -2.2 % | 8154.6 [7979.1, 8211.2] | -14.7 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 2443.5 [2219.0, 3143.5] | -74.5 % | 3275.5 [3060.5, 3983.3] | -65.8 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 9505.5 [9192.0, 9549.8] | -0.6 % | 3765.0 [3248.0, 4951.8] | -60.6 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 2462.0 [2014.8, 3257.0] | -74.3 % | 3220.5 [3076.3, 3972.3] | -66.3 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 4250.0 [4110.5, 4432.0] | -55.6 % | 2923.5 [2500.3, 3338.8] | -69.4 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 9468.5 [9260.5, 9547.3] | -1.0 % | 3694.5 [3265.0, 4937.3] | -61.4 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 2578.0 [2257.8, 3143.0] | -73.0 % | 3253.0 [3045.5, 4036.3] | -66.0 % | 3.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 9524.8 [8705.9, 9560.7] | -0.4 % | 3809.4 [3347.3, 5081.1] | -60.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 3319.4 [2709.4, 5093.0] | -65.3 % | 3158.0 [2865.4, 4042.8] | -67.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 4578.9 [4398.5, 5726.0] | -52.1 % | 3172.8 [2457.6, 4049.7] | -66.8 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.4 (20.1) | 171.4 (160.8) | 186.5 (182.1) |
| Graphite Meter Terminal | 30/30 | payload | 286.9 [286.9, 286.9] | -0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 20.2 (20.1) | 176.0 (169.2) | 197.5 (193.0) |
| Graphite Meter Browser, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | 21.0 (20.1) | 165.3 (145.7) | 183.5 (179.4) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (174.5) | n/a (182.8) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 286.9 [286.9, 287.0] | +0.0 % | 28.7 [28.7, 28.7] | -0.1 % | n/a (20.1) | n/a (132.6) | n/a (179.2) |
| iperf3 (reference) | 30/30 | payload | 287.0 [286.9, 287.0] | +0.0 % | 28.7 [28.6, 28.7] | -0.1 % | n/a (20.1) | n/a (176.4) | n/a (187.9) |
| LibreSpeed, chrome | 30/30 | payload | 286.0 [284.0, 287.0] | -0.3 % | 30.0 [29.3, 30.1] | +4.6 % | 20.3 (20.1) | n/a (160.2) | n/a (185.6) |
| LibreSpeed CLI | 30/30 | payload | 283.3 [282.9, 284.3] | -1.3 % | 29.0 [29.0, 29.6] | +1.2 % | 20.2 (20.1) | n/a (172.1) | n/a (173.2) |
| LibreSpeed, firefox | 30/30 | payload | 286.0 [283.0, 287.0] | -0.3 % | 29.3 [29.0, 29.7] | +2.1 % | 21.5 (20.1) | n/a (162.2) | n/a (185.8) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 287.0 [285.3, 287.0] | +0.0 % | 28.9 [28.3, 29.8] | +0.7 % | 20.1 (20.1) | n/a (162.6) | n/a (168.1) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 286.0 [285.0, 287.0] | -0.3 % | 29.1 [28.4, 29.4] | +1.2 % | 21.0 (20.1) | n/a (161.6) | n/a (186.3) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 286.0 [286.0, 287.0] | -0.3 % | 28.6 [28.1, 29.4] | -0.3 % | 20.1 (20.1) | n/a (156.8) | n/a (171.4) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 286.0 [285.0, 287.0] | -0.3 % | 29.1 [28.6, 29.6] | +1.2 % | 21.0 (20.1) | n/a (151.3) | n/a (186.6) |
| OpenSpeedTest, chrome | 30/30 | payload | 286.5 [286.1, 287.2] | -0.1 % | 31.4 [30.1, 31.7] | +9.6 % | 20.0 (20.1) | n/a (161.0) | n/a (196.2) |
| OpenSpeedTest, firefox | 30/30 | payload | 286.4 [285.9, 287.3] | -0.2 % | 30.6 [30.0, 31.6] | +6.6 % | 20.0 (20.1) | n/a (161.3) | n/a (197.3) |

## 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 13.1 [12.7, 13.7] | n/a | 13.3 [13.1, 14.5] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 19.6 [18.8, 20.1] | n/a | 20.0 [19.4, 20.6] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 13.1 [12.8, 13.5] | n/a | 14.9 [13.9, 15.5] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 13.2 [12.7, 13.7] | n/a | 13.6 [12.8, 13.9] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 13.2 [12.4, 13.6] | n/a | 14.2 [13.5, 15.3] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 12.8 [12.6, 13.3] | n/a | 12.9 [12.5, 13.4] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 17.2 [16.3, 17.7] | n/a | 9.4 [9.0, 10.2] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 10.8 [10.2, 11.5] | n/a | 11.8 [11.3, 12.4] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 21.2 [20.6, 22.6] | n/a | 9.7 [9.0, 10.2] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 16.8 [16.0, 17.1] | n/a | 9.8 [9.2, 10.2] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 21.3 [20.1, 22.4] | n/a | 9.5 [9.2, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 16.5 [16.0, 17.1] | n/a | 9.4 [9.0, 10.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 20.8 [19.6, 22.5] | n/a | 9.7 [9.2, 10.1] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 19.2 [18.4, 20.0] | n/a | 22.0 [21.0, 23.1] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 19.9 [19.3, 20.3] | n/a | 21.9 [21.1, 23.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 61.7 [58.7, 64.6] | n/a | 69.2 [62.0, 74.7] | n/a | 40.4 (40.1) | 40.3 (n/a) | 40.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 90.9 [83.9, 94.1] | n/a | 89.4 [84.7, 95.0] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/2 | 30/30 | payload | 14.6 [12.0, 17.1] | n/a | 13.4 [12.3, 15.2] | n/a | 40.2 (40.1) | 40.2 (n/a) | 40.1 (n/a) |
| Graphite Meter Terminal, HTTP/3 | 30/30 | payload | 87.0 [72.3, 112.8] | n/a | 138.4 [98.5, 199.6] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 63.9 [57.7, 71.7] | n/a | 70.4 [64.7, 79.6] | n/a | 41.0 (40.1) | 41.0 (n/a) | 41.0 (n/a) |
| Graphite Meter Browser, HTTP/2, chrome | 30/30 | payload | 13.7 [12.5, 16.0] | n/a | 16.5 [13.8, 18.0] | n/a | 40.4 (40.1) | 40.4 (n/a) | 40.4 (n/a) |
| Graphite Meter Browser, HTTP/3, chrome | 30/30 | payload | 97.6 [72.7, 125.9] | n/a | 27.0 [23.0, 31.8] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 58.0 [54.4, 62.9] | n/a | 71.0 [63.3, 78.0] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 58.4 [56.5, 62.4] | n/a | 71.7 [69.9, 78.6] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser, WebTransport, chrome | 30/30 | payload | 85.4 [58.3, 113.7] | n/a | 29.1 [26.4, 33.0] | n/a | 40.5 (40.1) | 40.3 (n/a) | 40.3 (n/a) |
| iperf3 (reference) | 30/30 | payload | 49.6 [46.3, 51.9] | n/a | 51.1 [48.7, 53.5] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 95.8 [86.7, 108.5] | n/a | 38.9 [34.2, 41.9] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 55.2 [51.2, 63.1] | n/a | 47.3 [45.3, 52.0] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 138.0 [116.0, 152.5] | n/a | 37.8 [35.2, 41.3] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 95.8 [83.5, 106.8] | n/a | 50.5 [44.5, 60.0] | n/a | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 128.5 [116.0, 152.5] | n/a | 36.3 [33.0, 42.5] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 30/30 | payload | 13.1 [10.2, 15.8] | n/a | 12.4 [10.9, 14.7] | n/a | 40.3 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 94.2 [81.5, 118.8] | n/a | 58.9 [45.9, 77.1] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 143.5 [124.0, 160.8] | n/a | 37.2 [32.8, 40.8] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 76.4 [72.9, 82.5] | n/a | 92.7 [88.3, 99.3] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 78.8 [73.5, 83.4] | n/a | 96.1 [88.4, 99.6] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 30/30 | payload | 11.8 [10.3, 13.7] | n/a | 13.9 [12.0, 15.7] | n/a | 41.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 275.6 [262.8, 280.0] | n/a | 238.9 [231.1, 244.5] | n/a | 160.5 (160.1) | 160.4 (n/a) | 160.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 282.2 [277.6, 283.9] | n/a | 280.1 [273.2, 281.9] | n/a | 160.0 (160.1) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 276.0 [262.8, 280.0] | n/a | 238.2 [235.1, 241.1] | n/a | 161.0 (160.1) | 162.0 (n/a) | 161.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 266.8 [260.3, 271.0] | n/a | 233.9 [227.8, 238.6] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 262.7 [255.8, 270.9] | n/a | 232.0 [223.8, 235.2] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 222.4 [202.1, 247.3] | n/a | 218.0 [201.0, 239.6] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 270.5 [267.3, 274.0] | n/a | 234.0 [227.3, 243.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 225.0 [217.9, 232.6] | n/a | 122.6 [121.5, 123.1] | n/a | 160.2 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 274.0 [270.5, 276.0] | n/a | 226.5 [218.8, 232.8] | n/a | 162.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 268.5 [262.3, 272.0] | n/a | 231.0 [219.0, 235.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 271.5 [267.0, 277.0] | n/a | 229.0 [221.3, 238.8] | n/a | 161.5 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 271.5 [265.3, 275.8] | n/a | 231.5 [228.3, 241.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 276.0 [270.5, 278.0] | n/a | 224.0 [215.0, 231.8] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 273.5 [268.2, 275.6] | n/a | 274.4 [270.9, 279.1] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 271.3 [265.6, 275.7] | n/a | 273.4 [269.0, 277.6] | n/a | 161.0 (160.1) | n/a (n/a) | n/a (n/a) |

## 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 75.0 [74.9, 75.0] | n/a | 75.2 [75.1, 75.4] | n/a | 20.5 (20.1) | 20.4 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 80.3 [80.3, 80.3] | n/a | 80.8 [80.8, 80.8] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 74.9 [74.9, 75.0] | n/a | 75.1 [75.0, 75.1] | n/a | 21.0 (20.1) | 22.3 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 75.0 [74.9, 75.1] | n/a | 75.1 [75.1, 75.3] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 74.9 [74.8, 75.0] | n/a | 75.1 [75.0, 75.2] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 74.9 [74.9, 75.0] | n/a | 75.1 [75.1, 75.3] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 77.7 [77.7, 77.8] | n/a | 71.0 [70.2, 71.3] | n/a | 20.4 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 30/30 | payload | 69.4 [69.3, 69.4] | n/a | 68.8 [68.8, 69.3] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 80.2 [80.0, 80.3] | n/a | 70.7 [69.8, 71.3] | n/a | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 30/30 | payload | 77.7 [77.7, 77.8] | n/a | 72.5 [72.4, 72.7] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 30/30 | payload | 80.0 [79.9, 80.2] | n/a | 70.0 [69.8, 71.1] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 30/30 | payload | 77.7 [77.7, 77.8] | n/a | 72.5 [72.0, 72.6] | n/a | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 30/30 | payload | 80.1 [80.0, 80.2] | n/a | 70.8 [69.9, 71.3] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 80.1 [80.1, 80.2] | n/a | 81.0 [80.5, 81.5] | n/a | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 80.3 [80.2, 80.3] | n/a | 80.8 [80.5, 81.6] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. iperf3 bypasses nginx and measures the direct shaped path as a control. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 956.1 [955.0, 956.4] | -0.0 % | 954.7 [952.8, 955.6] | -0.2 % | 20.4 (20.1) | 21.3 (n/a) | 22.8 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 954.6 [951.2, 956.0] | -0.2 % | 954.0 [951.1, 955.9] | -0.2 % | 21.0 (20.1) | 32.8 (n/a) | 25.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 955.3 [954.7, 955.9] | -0.1 % | 954.7 [953.0, 955.7] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 955.1 [952.3, 955.9] | -0.1 % | 955.2 [953.8, 956.1] | -0.1 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 956.4 [956.4, 956.5] | +0.0 % | 956.4 [956.3, 956.4] | -0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 30/30 | payload | 953.0 [946.3, 955.8] | -0.4 % | 907.0 [896.8, 925.8] | -5.2 % | 20.5 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 30/30 | payload | 935.0 [920.5, 949.0] | -2.2 % | 873.0 [855.3, 881.8] | -8.7 % | 22.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 30/30 | payload | 953.4 [950.1, 954.5] | -0.3 % | 928.0 [922.9, 932.4] | -3.0 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 30/30 | payload | 951.3 [950.4, 953.7] | -0.5 % | 916.5 [907.0, 924.2] | -4.2 % | 21.0 (20.1) | n/a (n/a) | n/a (n/a) |

## Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Differences use the modeled TCP payload rate. QUIC rows retain their reported rates without a TCP percentage. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | vs TCP model | Upload Mbit/s | vs TCP model | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | payload | 382.5 [382.5, 382.5] | -0.0 % | 381.7 [381.4, 381.9] | -0.2 % | 20.4 (20.1) | 20.8 (n/a) | 20.4 (n/a) |
| Graphite Meter Terminal | 30/30 | payload | 382.6 [382.6, 382.6] | +0.0 % | 382.5 [382.5, 382.5] | -0.0 % | 20.1 (20.1) | 20.3 (n/a) | 20.1 (n/a) |
| Graphite Meter Browser, firefox | 30/30 | payload | 382.5 [382.4, 382.6] | -0.0 % | 381.4 [381.0, 381.8] | -0.3 % | 21.0 (20.1) | 22.0 (n/a) | 21.0 (n/a) |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | payload | 382.5 [382.5, 382.6] | -0.0 % | 381.8 [381.3, 382.0] | -0.2 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | payload | 382.5 [382.4, 382.6] | -0.0 % | 381.3 [381.0, 381.8] | -0.3 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| iperf3 (reference) | 30/30 | payload | 382.5 [382.5, 382.5] | -0.0 % | 382.6 [382.6, 382.7] | +0.0 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

## Unshaped, offloads on: as fast as the host allows

Unshaped single-test throughput on the runner’s virtual link. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter Browser, chrome | 30/30 | 18437.8 [16812.5, 21254.1] | 5570.7 [4969.6, 9856.3] | 0.27 | 9 | 1.33 |
| Graphite Meter Terminal | 30/30 | 44925.0 [35392.5, 59765.0] | 62920.0 [52625.0, 69560.0] | 0.15 | 11 | n/a |
| Graphite Meter Terminal, HTTP/2 | 30/30 | 15115.0 [14127.5, 17627.5] | 16745.0 [14692.5, 18597.5] | 0.48 | 5 | n/a |
| Graphite Meter Terminal, HTTP/3 | 30/30 | 8125.0 [7052.5, 9227.5] | 8595.0 [7600.0, 9912.5] | 0.87 | 14 | n/a |
| Graphite Meter Browser, firefox | 30/30 | 3685.7 [3445.0, 5345.3] | 7451.4 [5711.4, 13500.2] | 0.23 | 10 | 2.39 |
| Graphite Meter Browser without loaded latency, chrome | 30/30 | 18931.3 [16975.3, 21836.5] | 5768.8 [5229.3, 10333.7] | 0.27 | 9 | 1.25 |
| Graphite Meter Browser without loaded latency, firefox | 30/30 | 4085.0 [3889.8, 5781.8] | 7842.6 [6485.4, 13786.6] | 0.23 | 10 | 2.05 |
| iperf3 (reference) | 30/30 | 41026.7 [31032.4, 57657.6] | 57580.8 [44427.1, 82680.0] | 0.16 | 12 | n/a |
| LibreSpeed, chrome | 30/30 | 10609.0 [9800.0, 14548.5] | 4969.0 [4259.3, 9580.0] | 0.29 | 82 | 1.94 |
| LibreSpeed CLI | 30/30 | 38723.4 [28848.0, 48476.8] | 23488.4 [18694.9, 27149.9] | 0.25 | 71 | n/a |
| LibreSpeed, firefox | 30/30 | 2416.0 [2177.0, 2985.0] | 3714.0 [3432.8, 4894.8] | 0.29 | 87 | 4.96 |
| LibreSpeed Go backend, chrome | 30/30 | 10671.5 [9734.0, 13962.3] | 4985.5 [4259.0, 9195.3] | 0.32 | 49 | 1.93 |
| LibreSpeed Go backend, firefox | 30/30 | 2434.5 [2119.3, 3060.3] | 3767.5 [3381.5, 4804.5] | 0.28 | 52 | 4.97 |
| LibreSpeed Rust backend, chrome | 30/30 | 10844.5 [9697.0, 14603.8] | 5032.5 [4208.8, 9524.3] | 0.24 | 23 | 1.96 |
| LibreSpeed Rust backend, firefox | 30/30 | 2464.5 [2137.8, 2936.5] | 3675.0 [3361.3, 4846.8] | 0.23 | 26 | 5.06 |
| OpenSpeedTest, chrome | 30/30 | 10143.1 [8599.7, 13702.0] | 5130.7 [4346.1, 9831.5] | 0.17 | 22 | 1.99 |
| OpenSpeedTest, firefox | 30/30 | 3276.5 [2696.3, 4998.6] | 3532.8 [3246.8, 4823.6] | 0.18 | 20 | 4.84 |
