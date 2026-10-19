# Desktop campaign, night of 18 to 19 October 2026

AMD Ryzen 7 7800X3D (8 cores, 16 threads), 31 GiB of RAM, kernel 7.2.10-1-cachyos, rootless Podman 6.1.4, bench commit
`0986d68`, run from 20:29 to 05:33 UTC. CPU sets: shaper on core 0, server on cores 1 and 2, browser and clients on
cores 3 to 5 (each core with its second thread); memory capped per container. 6 repetitions, every scenario in each,
so each tool and browser has 6 runs per scenario: 1,074 runs, all complete. Versions as in the GitHub runner results:
Graphite Meter 0.13.1, LibreSpeed 6.3.0, LibreSpeed Go backend 1.1.6, LibreSpeed Rust backend 1.4.0, OpenSpeedTest
2.5.4, LibreSpeed CLI 1.0.14, Chrome for Testing 155.0.8059.84, Firefox 158.0.

This kernel's TCP recovers from random loss far better than the runners' kernel 6.17 (iperf3 reaches 94 Mbit/s at
1 % loss here and 13 there, with the same netem loss and CUBIC on both), so loss, long-path and deep-buffer numbers
are comparable within this page, not with the runner results. With 6 runs per cell, differences of about 2 % or
less are within this dataset's noise.

Values are medians with the 25th and 75th percentile in brackets; error compares the median with the payload rate;
latency references are in brackets. Raw data: one JSON per run in `runs/` and the campaign's `manifest.json`.

## 100/100 Mbit/s, 20 ms RTT, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 96.0 [95.9, 96.1] | +0.4 % | 94.2 [93.8, 94.7] | -1.5 % | 20.1 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 95.8 [95.7, 95.8] | +0.2 % | 95.9 [95.8, 96.0] | +0.3 % | 20.1 (20.1) | 20.1 (n/a) | 20.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 95.9 [95.8, 96.0] | +0.3 % | 94.9 [94.9, 95.1] | -0.7 % | 20.0 (20.1) | 20.0 (n/a) | 20.0 (n/a) |
| iperf3 (reference) | 6/6 | payload | 94.5 [93.6, 95.6] | -1.2 % | 94.8 [93.8, 95.6] | -0.9 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 95.8 [95.7, 96.1] | +0.1 % | 96.1 [94.3, 96.7] | +0.4 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 94.4 [94.4, 94.5] | -1.3 % | 92.8 [92.5, 93.4] | -3.0 % | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 95.8 [95.6, 95.9] | +0.1 % | 95.3 [94.0, 96.3] | -0.4 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 96.0 [95.7, 97.3] | +0.4 % | 93.8 [92.2, 94.2] | -2.0 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 96.4 [95.7, 97.5] | +0.8 % | 94.2 [93.7, 95.0] | -1.5 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 96.5 [96.0, 97.0] | +0.9 % | 89.5 [89.0, 93.0] | -6.4 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 96.9 [95.7, 98.2] | +1.3 % | 95.7 [94.3, 96.2] | +0.0 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 95.5 [95.3, 95.5] | -0.2 % | 97.3 [96.0, 97.5] | +1.7 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 95.5 [95.4, 95.6] | -0.1 % | 100.0 [99.1, 100.8] | +4.5 % | 19.5 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 964.6 [962.8, 965.9] | +0.9 % | 937.9 [929.3, 944.7] | -1.9 % | 20.1 (20.1) | 20.1 (n/a) | 20.1 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 959.2 [956.6, 961.2] | +0.3 % | 957.6 [956.4, 959.5] | +0.1 % | 20.1 (20.1) | 20.1 (n/a) | 20.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 962.4 [959.5, 971.0] | +0.6 % | 925.9 [920.8, 949.2] | -3.2 % | 20.0 (20.1) | 20.0 (n/a) | 20.0 (n/a) |
| Graphite Meter, HTTP/2, chrome | 6/6 | payload | 893.0 [783.4, 943.5] | -6.6 % | 950.5 [804.1, 954.6] | -0.6 % | 20.1 (20.1) | 20.1 (n/a) | 20.1 (n/a) |
| Graphite Meter, HTTP/3, chrome | 6/6 | payload | 937.5 [936.6, 938.7] | -2.0 % | 118.3 [116.8, 119.4] | -87.6 % | 20.2 (20.1) | 20.2 (n/a) | 20.1 (n/a) |
| Graphite Meter, WebTransport, chrome | 6/6 | payload | 958.4 [957.1, 959.7] | +0.2 % | 941.1 [941.1, 941.1] | -1.6 % | 20.2 (20.1) | 20.1 (n/a) | 20.2 (n/a) |
| iperf3 (reference) | 6/6 | payload | 949.6 [941.5, 955.7] | -0.7 % | 942.5 [936.5, 949.4] | -1.5 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 960.5 [955.0, 977.3] | +0.4 % | 939.0 [936.0, 961.5] | -1.8 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 936.2 [935.2, 938.2] | -2.1 % | 718.6 [712.8, 834.1] | -24.9 % | 20.2 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 973.5 [969.3, 977.8] | +1.8 % | 918.0 [878.5, 936.5] | -4.0 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 968.5 [966.3, 970.8] | +1.3 % | 997.0 [979.8, 999.3] | +4.2 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 959.0 [954.3, 969.8] | +0.3 % | 937.0 [934.5, 938.8] | -2.0 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 6/6 | payload | 872.5 [776.8, 937.5] | -8.8 % | 414.0 [407.3, 417.0] | -56.7 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 972.5 [972.0, 973.0] | +1.7 % | 966.5 [890.8, 968.0] | +1.1 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 968.0 [966.3, 973.5] | +1.2 % | 903.0 [900.0, 905.3] | -5.6 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 956.2 [955.5, 956.8] | -0.0 % | 981.2 [968.1, 995.6] | +2.6 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 956.2 [955.0, 956.9] | -0.0 % | 975.9 [962.4, 991.8] | +2.0 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 6/6 | payload | 913.4 [907.2, 914.2] | -4.5 % | 905.8 [777.6, 940.3] | -5.3 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 10000 / 10000 Mbit/s; payload rate 9564.1 / 9564.1 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. On 4-vCPU runners the browser (two vCPUs) is usually the limit here, so a low reading shows how much of the link a tool can drive on that hardware, not a counting error. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 9599.5 [9592.2, 9605.7] | +0.4 % | 9564.1 [9563.4, 9564.2] | +0.0 % | 2.1 (2.1) | 2.1 (n/a) | 2.2 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 9560.0 [9560.0, 9560.0] | -0.0 % | 9560.0 [9560.0, 9560.0] | -0.0 % | 2.0 (2.1) | 2.1 (n/a) | 2.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 9604.1 [9583.6, 9606.0] | +0.4 % | 7815.2 [7603.3, 7947.1] | -18.3 % | 2.0 (2.1) | 2.0 (n/a) | 3.0 (n/a) |
| Graphite Meter, HTTP/2, chrome | 6/6 | payload | 9514.7 [9509.9, 9521.2] | -0.5 % | 7112.6 [7061.7, 7261.5] | -25.6 % | 2.1 (2.1) | 2.1 (n/a) | 2.5 (n/a) |
| Graphite Meter, HTTP/3, chrome | 6/6 | payload | 3568.4 [3557.5, 3583.0] | -62.7 % | 1583.7 [1579.3, 1588.2] | -83.4 % | 2.1 (2.1) | 2.2 (n/a) | 3.1 (n/a) |
| Graphite Meter, WebTransport, chrome | 6/6 | payload | 3667.5 [3644.9, 3686.5] | -61.7 % | 1526.7 [1525.0, 1527.7] | -84.0 % | 2.1 (2.1) | 2.2 (n/a) | 3.8 (n/a) |
| iperf3 (reference) | 6/6 | payload | 9541.8 [9412.2, 9563.9] | -0.2 % | 9562.4 [9540.9, 9564.1] | -0.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 9582.5 [9576.8, 9597.3] | +0.2 % | 9550.0 [9526.0, 9550.0] | -0.1 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 9354.6 [9351.9, 9356.5] | -2.2 % | 8864.8 [8491.7, 8886.5] | -7.3 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 8364.0 [8277.3, 8415.5] | -12.5 % | 8541.0 [8538.0, 8593.5] | -10.7 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 9575.0 [9563.8, 9581.0] | +0.1 % | 9550.0 [9550.0, 9550.0] | -0.1 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 8507.0 [8386.5, 8555.5] | -11.1 % | 8198.5 [7869.5, 8433.0] | -14.3 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 6/6 | payload | 7679.5 [7588.8, 7753.0] | -19.7 % | 3965.0 [3947.8, 3968.8] | -58.5 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 9574.0 [9572.5, 9582.3] | +0.1 % | 9550.0 [9550.0, 9550.0] | -0.1 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 9197.0 [8956.3, 9441.5] | -3.8 % | 8259.0 [8007.5, 8325.3] | -13.6 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 9560.5 [9554.2, 9566.8] | -0.0 % | 9579.5 [9568.7, 9587.7] | +0.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 7059.8 [6657.6, 7324.4] | -26.2 % | 9539.7 [9523.5, 9578.2] | -0.3 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 6/6 | payload | 9413.6 [9392.8, 9479.6] | -1.6 % | 2644.6 [2311.6, 2818.7] | -72.3 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 25/25 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 25000 / 25000 Mbit/s; payload rate 23910.2 / 23910.2 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Only on hosts with at least 8 CPUs; the browser's CPU share is usually the limit, so a low reading shows how much of the link a tool can drive there, not a counting error. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 24003.1 [23982.9, 24012.9] | +0.4 % | 12916.8 [12785.7, 12987.5] | -46.0 % | 2.1 (2.1) | 2.1 (n/a) | 2.4 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 23910.0 [23910.0, 23910.0] | -0.0 % | 23910.0 [23910.0, 23910.0] | -0.0 % | 2.0 (2.1) | 2.1 (n/a) | 2.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 17693.3 [17488.7, 18051.1] | -26.0 % | 8740.2 [8637.1, 8859.5] | -63.4 % | 2.0 (2.1) | 3.0 (n/a) | 3.5 (n/a) |
| Graphite Meter, HTTP/2, chrome | 6/6 | payload | 11620.9 [11600.0, 11645.0] | -51.4 % | 7092.1 [7034.7, 7145.3] | -70.3 % | 2.1 (2.1) | 2.1 (n/a) | 2.5 (n/a) |
| Graphite Meter, HTTP/3, chrome | 6/6 | payload | 3586.1 [3566.2, 3595.8] | -85.0 % | 1575.0 [1562.5, 1584.3] | -93.4 % | 2.1 (2.1) | 2.2 (n/a) | 3.0 (n/a) |
| Graphite Meter, WebTransport, chrome | 6/6 | payload | 3675.1 [3666.9, 3681.9] | -84.6 % | 1524.7 [1522.3, 1527.4] | -93.6 % | 2.1 (2.1) | 2.2 (n/a) | 4.2 (n/a) |
| iperf3 (reference) | 6/6 | payload | 23900.0 [23550.4, 23910.7] | -0.0 % | 23451.5 [23436.9, 23778.3] | -1.9 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 23914.0 [23886.8, 23936.0] | +0.0 % | 11228.0 [11204.0, 11252.0] | -53.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 23147.0 [23137.3, 23148.6] | -3.2 % | 8388.3 [8371.5, 8401.8] | -64.9 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 8741.0 [8526.0, 8947.0] | -63.4 % | 8216.5 [8146.8, 8302.8] | -65.6 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 23905.5 [23881.3, 23938.0] | -0.0 % | 11179.5 [11091.0, 11196.0] | -53.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 8539.0 [8416.0, 8767.0] | -64.3 % | 8085.5 [8022.8, 8110.0] | -66.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 6/6 | payload | 7570.0 [7535.3, 7735.3] | -68.3 % | 3965.0 [3962.0, 3968.0] | -83.4 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 23927.0 [23891.8, 23935.3] | +0.1 % | 11131.0 [11131.0, 11155.0] | -53.4 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 10448.5 [9557.3, 11372.8] | -56.3 % | 8160.5 [8147.8, 8273.0] | -65.9 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 23910.8 [23904.6, 23918.1] | +0.0 % | 11386.5 [11344.3, 11412.2] | -52.4 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 8326.0 [7015.5, 9797.8] | -65.2 % | 8596.0 [8418.9, 8620.2] | -64.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 6/6 | payload | 10912.8 [10876.7, 10967.0] | -54.4 % | 2760.6 [2061.7, 2832.2] | -88.5 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 40/40 Gbit/s, 2 ms RTT, fq_codel, offloads on

Link rate 40000 / 40000 Mbit/s; payload rate 38256.3 / 38256.3 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Only on hosts with at least 8 CPUs; the browser's CPU share is usually the limit, so a low reading shows how much of the link a tool can drive there, not a counting error. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 33583.5 [31645.4, 34979.4] | -12.2 % | 12729.6 [12649.9, 12852.7] | -66.7 % | 2.1 (2.1) | 2.2 (n/a) | 2.4 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 38260.0 [38260.0, 38260.0] | +0.0 % | 38260.0 [38260.0, 38260.0] | +0.0 % | 2.0 (2.1) | 2.1 (n/a) | 2.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 20023.5 [18955.2, 20309.4] | -47.7 % | 8660.2 [8565.1, 8728.1] | -77.4 % | 2.0 (2.1) | 17.3 (n/a) | 3.3 (n/a) |
| Graphite Meter, HTTP/2, chrome | 6/6 | payload | 11631.5 [11624.7, 11635.3] | -69.6 % | 7473.8 [7053.3, 7894.9] | -80.5 % | 2.1 (2.1) | 2.1 (n/a) | 2.5 (n/a) |
| Graphite Meter, HTTP/3, chrome | 6/6 | payload | 3569.3 [3561.5, 3576.2] | -90.7 % | 1580.3 [1573.3, 1582.3] | -95.9 % | 2.1 (2.1) | 2.2 (n/a) | 3.0 (n/a) |
| Graphite Meter, WebTransport, chrome | 6/6 | payload | 3651.2 [3628.7, 3670.5] | -90.5 % | 1522.1 [1519.4, 1524.8] | -96.0 % | 2.1 (2.1) | 2.2 (n/a) | 3.8 (n/a) |
| iperf3 (reference) | 6/6 | payload | 37774.5 [37499.4, 38192.7] | -1.3 % | 37499.9 [37499.6, 37500.7] | -2.0 % | n/a (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 24439.0 [24380.8, 24486.8] | -36.1 % | 11260.0 [11212.0, 11284.0] | -70.6 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 36909.2 [36888.9, 36928.0] | -3.5 % | 9900.0 [8765.6, 9902.1] | -74.1 % | 2.1 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 8995.5 [8660.0, 9259.0] | -76.5 % | 8238.5 [8188.3, 8294.8] | -78.5 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 24663.0 [24313.0, 24886.3] | -35.5 % | 11147.0 [11131.0, 11211.8] | -70.9 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 9107.0 [8898.5, 9288.5] | -76.2 % | 8102.5 [8038.0, 8158.8] | -78.8 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 6/6 | payload | 7671.5 [7563.0, 7783.8] | -79.9 % | 3952.0 [3928.5, 3966.5] | -89.7 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 24448.0 [24342.0, 24668.0] | -36.1 % | 11131.0 [11131.0, 11155.0] | -70.9 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 10759.0 [10246.5, 11366.0] | -71.9 % | 8033.0 [8011.8, 8080.5] | -79.0 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 24244.4 [24198.3, 24338.8] | -36.6 % | 11348.5 [11320.2, 11359.9] | -70.3 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 7316.3 [6959.3, 7697.3] | -80.9 % | 8732.7 [8720.9, 8939.0] | -77.2 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 6/6 | payload | 10848.0 [10833.7, 10899.1] | -71.6 % | 2111.4 [1935.8, 2442.8] | -94.5 % | 2.0 (2.1) | n/a (n/a) | n/a (n/a) |

## 300/30 Mbit/s, 20 ms RTT, 200 ms FIFO

Link rate 300 / 30 Mbit/s; payload rate 286.9 / 28.7 Mbit/s. Error is against the quantity each tool says it reports. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 287.9 [286.9, 288.9] | +0.3 % | 28.6 [28.6, 28.6] | -0.3 % | 20.1 (20.1) | 68.3 (69.9) | 48.0 (53.6) |
| Graphite Meter terminal client | 6/6 | payload | 286.5 [282.8, 286.9] | -0.1 % | 28.7 [28.6, 28.7] | -0.1 % | 20.1 (20.1) | 110.0 (109.5) | 163.0 (157.9) |
| Graphite Meter, firefox | 6/6 | payload | 286.9 [286.8, 288.7] | -0.0 % | 28.6 [28.6, 28.7] | -0.2 % | 20.0 (20.1) | 105.5 (107.4) | 105.0 (102.5) |
| iperf3 (reference) | 6/6 | payload | 286.1 [282.3, 286.8] | -0.3 % | 28.4 [28.3, 28.4] | -1.2 % | n/a (20.1) | n/a (46.8) | n/a (60.8) |
| LibreSpeed, chrome | 6/6 | payload | 287.0 [287.0, 287.8] | +0.0 % | 29.3 [28.6, 30.1] | +2.1 % | 20.0 (20.1) | n/a (169.0) | n/a (131.9) |
| LibreSpeed CLI | 6/6 | payload | 283.8 [282.8, 283.9] | -1.1 % | 29.0 [28.6, 29.0] | +1.2 % | 20.1 (20.1) | n/a (51.7) | n/a (60.9) |
| LibreSpeed, firefox | 6/6 | payload | 287.5 [287.0, 288.0] | +0.2 % | 26.1 [25.5, 27.2] | -9.0 % | 20.0 (20.1) | n/a (131.4) | n/a (112.3) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 287.0 [286.3, 287.0] | +0.0 % | 31.0 [29.4, 35.0] | +8.0 % | 20.0 (20.1) | n/a (118.9) | n/a (141.2) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 287.5 [287.0, 288.0] | +0.2 % | 29.0 [28.1, 30.0] | +1.1 % | 20.0 (20.1) | n/a (152.9) | n/a (129.5) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 287.0 [287.0, 287.0] | +0.0 % | 31.3 [29.6, 34.0] | +8.9 % | 20.0 (20.1) | n/a (157.6) | n/a (170.9) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 286.5 [285.3, 287.0] | -0.1 % | 28.7 [27.3, 29.8] | +0.0 % | 20.0 (20.1) | n/a (179.5) | n/a (122.8) |
| OpenSpeedTest, chrome | 6/6 | payload | 286.2 [286.1, 286.6] | -0.3 % | 30.7 [30.5, 36.5] | +7.0 % | 20.0 (20.1) | n/a (110.3) | n/a (198.2) |
| OpenSpeedTest, firefox | 6/6 | payload | 286.1 [286.0, 286.3] | -0.3 % | 36.5 [32.2, 38.2] | +27.0 % | 20.0 (20.1) | n/a (103.2) | n/a (201.5) |

## 100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 93.9 [93.4, 94.4] | -1.8 % | 93.4 [91.1, 94.2] | -2.4 % | 40.2 (40.1) | 40.2 (n/a) | 40.2 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 95.1 [94.1, 95.6] | -0.6 % | 95.7 [95.1, 95.8] | +0.0 % | 40.1 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 93.9 [93.3, 94.8] | -1.8 % | 93.1 [92.4, 93.8] | -2.7 % | 40.0 (40.1) | 40.0 (n/a) | 40.0 (n/a) |
| iperf3 (reference) | 6/6 | payload | 94.4 [94.1, 95.0] | -1.3 % | 94.1 [93.6, 94.6] | -1.6 % | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 98.8 [97.5, 99.8] | +3.3 % | 88.8 [86.8, 94.1] | -7.1 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 91.1 [88.2, 91.2] | -4.8 % | 91.7 [87.8, 91.9] | -4.2 % | 40.2 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 98.2 [96.5, 98.5] | +2.6 % | 98.0 [96.8, 100.6] | +2.5 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 99.7 [97.3, 100.8] | +4.2 % | 95.7 [88.3, 98.5] | +0.1 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 98.3 [97.5, 98.8] | +2.7 % | 97.9 [97.3, 98.7] | +2.4 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 97.7 [97.0, 99.0] | +2.2 % | 94.9 [92.1, 95.2] | -0.7 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 97.7 [96.7, 98.7] | +2.2 % | 95.4 [94.9, 96.6] | -0.3 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 95.5 [94.5, 97.6] | -0.1 % | 103.0 [99.8, 106.9] | +7.6 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 98.3 [97.7, 98.9] | +2.7 % | 102.5 [101.4, 103.0] | +7.2 % | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 40 ms RTT, 0.1 % loss each way, fq_codel

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 943.5 [276.8, 953.7] | n/a | 911.2 [851.4, 933.5] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 929.8 [280.0, 954.1] | n/a | 954.1 [943.7, 957.0] | n/a | 40.1 (40.1) | 40.1 (n/a) | 40.0 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 941.6 [934.5, 953.0] | n/a | 917.4 [885.4, 926.3] | n/a | 40.0 (40.1) | 40.0 (n/a) | 40.0 (n/a) |
| Graphite Meter, HTTP/2, chrome | 6/6 | payload | 18.5 [14.7, 349.5] | n/a | 939.0 [901.9, 956.3] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.2 (n/a) |
| Graphite Meter, HTTP/3, chrome | 6/6 | payload | 90.8 [66.9, 105.3] | n/a | 24.3 [19.6, 29.6] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| Graphite Meter, WebTransport, chrome | 6/6 | payload | 71.5 [62.7, 85.2] | n/a | 28.6 [25.8, 34.0] | n/a | 40.2 (40.1) | 40.1 (n/a) | 40.1 (n/a) |
| iperf3 (reference) | 6/6 | payload | 493.7 [48.8, 937.2] | n/a | 933.2 [273.8, 946.5] | n/a | n/a (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 932.0 [286.2, 986.0] | n/a | 871.0 [255.1, 895.0] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 51.3 [43.2, 645.7] | n/a | 288.2 [232.1, 289.4] | n/a | 40.1 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 861.5 [268.5, 1003.8] | n/a | 869.5 [257.5, 870.8] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 989.5 [310.4, 996.3] | n/a | 519.9 [56.0, 968.0] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 935.5 [882.0, 994.3] | n/a | 868.5 [828.8, 890.3] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, HTTP/2, chrome | 6/6 | payload | 364.3 [12.8, 742.0] | n/a | 66.8 [11.4, 141.5] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 882.0 [287.5, 958.3] | n/a | 952.0 [911.3, 968.0] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 526.5 [134.3, 915.8] | n/a | 903.0 [878.3, 929.3] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 413.2 [72.5, 762.7] | n/a | 527.4 [89.7, 969.4] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 765.3 [251.6, 843.9] | n/a | 977.8 [971.1, 992.8] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, HTTP/2, chrome | 6/6 | payload | 10.8 [10.0, 11.5] | n/a | 761.0 [199.8, 825.6] | n/a | 40.0 (40.1) | n/a (n/a) | n/a (n/a) |

## 300/300 Mbit/s, 160 ms RTT, fq_codel

Link rate 300 / 300 Mbit/s; payload rate 286.9 / 286.9 Mbit/s. iperf3 does not fill this link, so it has no accuracy reference: compare the tools with each other and with iperf3 (4 TCP streams). Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 261.9 [226.4, 290.2] | n/a | 246.5 [204.2, 269.1] | n/a | 160.2 (160.1) | 160.1 (n/a) | 160.1 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 273.8 [250.2, 297.6] | n/a | 282.8 [275.7, 293.9] | n/a | 160.0 (160.1) | 160.0 (n/a) | 160.0 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 235.6 [214.4, 280.9] | n/a | 226.4 [201.2, 252.8] | n/a | 160.0 (160.1) | 160.0 (n/a) | 160.0 (n/a) |
| iperf3 (reference) | 6/6 | payload | 216.9 [206.8, 272.0] | n/a | 215.3 [199.3, 230.6] | n/a | n/a (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 274.0 [262.0, 277.0] | n/a | 210.0 [194.0, 226.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 199.0 [166.8, 215.7] | n/a | 123.1 [122.7, 123.1] | n/a | 160.2 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 258.0 [246.8, 270.0] | n/a | 207.5 [197.3, 208.0] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 232.5 [222.3, 238.3] | n/a | 269.0 [224.8, 330.5] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 231.0 [224.0, 250.0] | n/a | 218.0 [178.0, 299.3] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 245.5 [225.0, 268.3] | n/a | 249.5 [241.0, 315.8] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 225.5 [222.0, 234.3] | n/a | 221.0 [216.3, 237.8] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 274.9 [270.9, 277.9] | n/a | 295.5 [294.7, 297.4] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 269.6 [254.3, 273.1] | n/a | 283.9 [271.0, 293.1] | n/a | 160.0 (160.1) | n/a (n/a) | n/a (n/a) |

## 100/100 Mbit/s, 20 ms RTT, fq_codel, one competing flow each way

Link rate 100 / 100 Mbit/s; payload rate 95.6 / 95.6 Mbit/s. One bulk TCP flow each way shares the link. A tool's share grows over its run as its flows take their part, and each tool averages a different window, so there is no single reference: compare the tools with each other and with iperf3 (4 TCP streams). Each run's median share, measured on the shaper, is in the raw data. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 75.3 [75.2, 75.9] | n/a | 69.6 [69.2, 69.7] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 80.7 [80.5, 80.7] | n/a | 80.7 [80.5, 80.8] | n/a | 20.2 (20.1) | 20.2 (n/a) | 20.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 75.0 [74.8, 75.1] | n/a | 68.9 [68.6, 69.3] | n/a | 20.0 (20.1) | 20.0 (n/a) | 20.0 (n/a) |
| iperf3 (reference) | 6/6 | payload | 75.0 [74.6, 75.2] | n/a | 75.2 [73.7, 75.4] | n/a | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 78.3 [78.2, 78.3] | n/a | 70.3 [70.0, 71.3] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed CLI | 6/6 | payload | 69.2 [69.1, 69.2] | n/a | 67.8 [67.3, 68.1] | n/a | 20.1 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 80.8 [80.5, 81.9] | n/a | 69.8 [69.7, 70.5] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, chrome | 6/6 | payload | 78.3 [78.3, 78.5] | n/a | 72.5 [72.4, 73.0] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Go backend, firefox | 6/6 | payload | 80.4 [80.1, 80.7] | n/a | 69.7 [69.3, 70.2] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, chrome | 6/6 | payload | 78.7 [77.7, 79.1] | n/a | 73.0 [71.3, 73.8] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed Rust backend, firefox | 6/6 | payload | 81.5 [80.9, 82.1] | n/a | 69.6 [68.6, 69.9] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 80.4 [80.2, 80.9] | n/a | 82.3 [81.9, 82.7] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 80.3 [80.3, 80.9] | n/a | 82.0 [81.6, 82.3] | n/a | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## 1/1 Gbit/s, 20 ms RTT, fq_codel, behind nginx

Link rate 1000 / 1000 Mbit/s; payload rate 956.4 / 956.4 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 960.6 [959.9, 969.2] | +0.4 % | 935.1 [933.2, 941.8] | -2.2 % | 20.2 (20.1) | 20.2 (n/a) | 20.2 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 963.0 [956.0, 970.0] | +0.7 % | 940.9 [929.8, 951.9] | -1.6 % | 20.0 (20.1) | 21.0 (n/a) | 20.0 (n/a) |
| iperf3 (reference) | 6/6 | payload | 938.7 [935.2, 951.5] | -1.9 % | 953.2 [943.0, 955.3] | -0.3 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, chrome | 6/6 | payload | 960.5 [937.3, 968.8] | +0.4 % | 921.5 [903.0, 961.0] | -3.6 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| LibreSpeed, firefox | 6/6 | payload | 960.0 [916.8, 968.8] | +0.4 % | 855.0 [821.8, 894.3] | -10.6 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, chrome | 6/6 | payload | 956.4 [954.8, 956.8] | -0.0 % | 860.5 [781.4, 897.1] | -10.0 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |
| OpenSpeedTest, firefox | 6/6 | payload | 955.3 [953.5, 956.3] | -0.1 % | 845.4 [815.1, 856.7] | -11.6 % | 20.0 (20.1) | n/a (n/a) | n/a (n/a) |

## Two servers, 200/200 Mbit/s path each, 20 ms RTT, fq_codel

Link rate 400 / 400 Mbit/s; payload rate 382.6 / 382.6 Mbit/s. Error is against the quantity each tool says it reports. Under fq_codel a latency probe skips the bulk queue, so loaded latency has no reference. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Reports | Download Mbit/s | Error | Upload Mbit/s | Error | Idle ms (base) | Loaded down ms (ref) | Loaded up ms (ref) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | payload | 383.9 [383.5, 384.2] | +0.3 % | 377.7 [376.9, 378.9] | -1.3 % | 20.1 (20.1) | 20.2 (n/a) | 20.1 (n/a) |
| Graphite Meter terminal client | 6/6 | payload | 382.6 [382.5, 382.6] | +0.0 % | 384.1 [382.8, 384.7] | +0.4 % | 20.1 (20.1) | 20.1 (n/a) | 20.1 (n/a) |
| Graphite Meter, firefox | 6/6 | payload | 382.9 [382.6, 383.5] | +0.1 % | 378.9 [377.2, 381.2] | -1.0 % | 20.0 (20.1) | 20.0 (n/a) | 20.0 (n/a) |
| iperf3 (reference) | 6/6 | payload | 375.8 [374.4, 381.1] | -1.8 % | 377.1 [375.5, 381.6] | -1.4 % | n/a (20.1) | n/a (n/a) | n/a (n/a) |

## Unshaped, offloads on: as fast as the host allows

No shaping: the host's CPU is the limit, so rates show how far each tool gets on it, not a network's capacity. Rates show median [25th, 75th percentile].

| Tool | Runs ok | Download Mbit/s | Upload Mbit/s | Server CPU s/GB | Server peak MB | Browser CPU s/GB |
| --- | --- | --- | --- | --- | --- | --- |
| Graphite Meter, chrome | 6/6 | 38949.7 [38572.2, 39944.6] | 15084.2 [14797.6, 15702.4] | 0.13 | 34 | 0.74 |
| Graphite Meter terminal client | 6/6 | 185400.0 [184750.0, 186125.0] | 242400.0 [215725.0, 310025.0] | 0.11 | 42 | n/a |
| Graphite Meter, firefox | 6/6 | 19279.2 [19251.0, 19412.6] | 9367.5 [9340.9, 9434.2] | 0.11 | 45 | 2.43 |
| iperf3 (reference) | 6/6 | 172164.8 [171926.9, 172395.3] | 206516.8 [187788.9, 215513.4] | 0.10 | 28 | n/a |
| LibreSpeed, chrome | 6/6 | 24455.5 [24198.3, 25135.8] | 13938.0 [13914.0, 13938.0] | 0.18 | 140 | 0.69 |
| LibreSpeed CLI | 6/6 | 132730.6 [127241.4, 132907.4] | 75208.7 [74561.1, 75616.0] | 0.14 | 171 | n/a |
| LibreSpeed, firefox | 6/6 | 8364.5 [8150.8, 8697.5] | 8547.5 [8471.3, 8611.0] | 0.17 | 143 | 3.67 |
| LibreSpeed Go backend, chrome | 6/6 | 24134.5 [23994.3, 24179.5] | 13970.5 [13914.0, 14051.0] | 0.17 | 185 | 0.69 |
| LibreSpeed Go backend, firefox | 6/6 | 8771.5 [8562.3, 8861.5] | 8448.0 [8421.5, 8494.0] | 0.15 | 122 | 3.64 |
| LibreSpeed Rust backend, chrome | 6/6 | 24468.0 [24463.3, 24478.0] | 13986.5 [13938.0, 14035.0] | 0.14 | 59 | 0.69 |
| LibreSpeed Rust backend, firefox | 6/6 | 10624.5 [9952.8, 10855.3] | 8441.0 [8432.8, 8495.0] | 0.13 | 72 | 3.51 |
| OpenSpeedTest, chrome | 6/6 | 24068.2 [24048.7, 24094.1] | 14117.1 [14075.6, 14152.0] | 0.12 | 94 | 0.67 |
| OpenSpeedTest, firefox | 6/6 | 6851.8 [6538.1, 7099.0] | 9236.1 [9185.3, 9268.5] | 0.14 | 76 | 3.79 |
