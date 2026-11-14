from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median, quantiles
import json
import math
import os
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

plt.rcParams.update({
    "figure.facecolor": "#f3f6fa",
    "axes.facecolor": "#ffffff",
    "font.family": "DejaVu Sans",
    "text.color": "#15253a",
    "axes.labelcolor": "#40536b",
    "xtick.color": "#40536b",
    "ytick.color": "#15253a",
})

run, artifact_path = sys.argv[1:]
if not run.isascii() or not run.isdecimal():
    raise SystemExit("Expected a numeric GitHub Actions run ID")

jobs = sorted(Path(artifact_path).glob("job-*"))
readme = Path("README.md")
original = readme.read_text()
latest = original.split("## Latest GitHub runner results", 1)[1].split("## What runs", 1)[0]
previous = re.search(r"results/(\d{4}-\d{2}-\d{2})-ci-run-(\d+)", latest)
if previous and int(previous[2]) >= int(run):
    print("The README already shows this run or a newer one.")
    sys.exit(0)

scenarios = {entry["id"] for entry in json.loads(Path("scenarios.json").read_text())}
if len(jobs) != 15:
    raise SystemExit("Expected artifacts for all 15 benchmark jobs")
manifests = [json.loads((job / "manifest.json").read_text()) for job in jobs]
for job, manifest in zip(jobs, manifests, strict=True):
    planned = set(manifest["scenarios"])
    blocks = manifest["blocks"]
    expected = {(scenario, rep) for scenario in planned for rep in (1, 2)}
    completed = {(b["scenario"], b["rep"]) for b in blocks}
    covered = planned | set(manifest["skipped"])
    if manifest["reps"] != 2 or covered != scenarios or completed != expected:
        print("The run did not cover the full two-pass benchmark. Skipping publication.")
        sys.exit(0)
    count = sum(len(block["order"]) for block in blocks)
    if sum(1 for _ in (job / "runs").glob("*.json")) != count:
        raise SystemExit(f"Missing measurements in {job.name}")
    if manifest["pins"] != manifests[0]["pins"] or manifest["bench"] != manifests[0]["bench"]:
        raise SystemExit("Benchmark jobs used different pins or source revisions")

date = min(datetime.fromisoformat(manifest["startedAt"]) for manifest in manifests).date().isoformat()
report = Path(f"results/{date}-ci-run-{run}")
report.mkdir(exist_ok=True)
with TemporaryDirectory() as temporary:
    data = Path(temporary) / "measurements.json"
    summary = subprocess.check_output(
        ["node", "bench/summarize.js", *jobs], text=True, env={**os.environ, "SB_REPORT_DATA": str(data)}
    )
    measurements = json.loads(data.read_text())
phases = subprocess.check_output(["node", "bench/phases.js", *jobs], text=True)
run_url = f"https://github.com/zR-JB/selfhosted-speedtest-bench/actions/runs/{run}"
(report / "README.md").write_text(
    f"# GitHub runner benchmark, {date}\n\n[Workflow run {run}]({run_url}) (raw measurements and screenshots under Artifacts) · "
    "[Bench overview](../../README.md) · [Server CPU by phase](server-cpu.md)"
    + (f" · [Previous report](../{Path(previous[0]).name})" if previous else "")
    + "\n\n" + summary
)

def tables(markdown, heading):
    groups = {}
    for line in markdown.splitlines():
        if line.startswith(heading):
            groups[line[len(heading):]] = group = {}
        elif line.startswith("| ") and groups:
            label, *cells = [part.strip() for part in line.strip("|").split("|")]
            if re.fullmatch(r"\d+(?:/\d+)?", cells[0]):
                group[label] = cells
    return groups


browser_tools = {
    "Graphite Meter": ("Graphite Meter Browser", "#1264ac"),
    "LibreSpeed": ("LibreSpeed", "#187765"),
    "LibreSpeed Go backend": ("LibreSpeed Go", "#a1482b"),
    "LibreSpeed Rust backend": ("LibreSpeed Rust", "#744399"),
    "OpenSpeedTest": ("OpenSpeedTest", "#886008"),
}
terminal_tool = "Graphite Meter terminal client"
terminal_tools = {
    terminal_tool: ("Graphite Meter Terminal", "#34455f"),
    "LibreSpeed CLI": ("LibreSpeed CLI", "#276d58"),
}
headline_tools = {**browser_tools, **terminal_tools}
reference_tool = "iperf3 (reference)"
reference_series = ("iperf3 reference", "#5b6570")
shaped_tools = {**headline_tools, reference_tool: reference_series}
groups = tables(summary, "## ")


def display(label):
    if label in terminal_tools:
        return terminal_tools[label][0]
    return browser_tools["Graphite Meter"][0] if label == "Graphite Meter" else label


def chrome_key(label):
    return f"{label}, chrome" if label in browser_tools else label


def style_axis(ax, title, unit, *, labels=True, tools=headline_tools):
    ax.set_title(title, loc="left", fontsize=10, weight="bold", pad=8)
    ax.set_xlabel(unit, fontsize=8)
    ax.set_yticks(range(len(tools)), [name for name, _ in tools.values()] if labels else [])
    ax.set_ylim(len(tools) - .35, -.65)
    ax.tick_params(axis="y", labelsize=8.5, length=0)
    ax.tick_params(axis="x", labelsize=8, length=3, labelbottom=True)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6, min_n_ticks=4))
    ax.grid(axis="x", color="#e1e8f0", linewidth=.75)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)


def save_chart(fig, name, title, subtitle):
    fig.suptitle(title, x=.02, y=.98, ha="left", fontsize=17, weight="bold")
    fig.text(.02, .872 if fig.get_figheight() < 5 else .905, subtitle, fontsize=8.5, color="#40536b")
    fig.savefig(report / name, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def quartiles(values):
    center = median(values)
    if len(values) == 1:
        return center, center, center
    low, _, high = quantiles(values, n=4, method="inclusive")
    return center, low, high


def spread_bar(ax, y, center, low, high, color, value_label):
    ax.barh(y, center, color=color, height=.55, zorder=3)
    ax.errorbar(center, y, xerr=[[center - low], [high - center]], color="#15253a",
                fmt="o", ms=3, capsize=3, linewidth=1, zorder=4)
    ax.annotate(value_label, (high, y), xytext=(5, 0), textcoords="offset points",
                va="center", fontsize=8, color="#15253a")


shaped_title = "1/1 Gbit/s, 20 ms RTT, fq_codel"
plain = groups[shaped_title]
fast = groups["10/10 Gbit/s, 2 ms RTT, fq_codel, offloads on"]
loss = groups["100/100 Mbit/s, 40 ms RTT, 1 % loss each way, fq_codel"]
pins = manifests[0]["pins"]


def value_at(row, col):
    value = row[col].split()[0]
    return float(value) if value != "n/a" else math.nan


baseline = {
    (row["job"], row["rep"]): row["reported"] for row in measurements
    if row["scenario"] == "accuracy-1000" and row["tool"] == "iperf3"
}
paired_rates = defaultdict(list)
for row in measurements:
    tool = row["tool"]
    ref = baseline.get((row["job"], row["rep"]))
    if row["scenario"] != "accuracy-1000" or tool == "iperf3" or ref is None:
        continue
    label = (pins["tools"].get(tool) or pins["clients"][tool])["name"]
    for field in ("downloadMbit", "uploadMbit"):
        value = row["reported"].get(field)
        if value is not None and ref.get(field) and ref[field] > 0:
            paired_rates[label, row["browser"], field].append(100 * (value / ref[field] - 1))

fig, axes = plt.subplots(2, 2, figsize=(11.2, 6.85), sharex=True)
fig.subplots_adjust(left=.208, right=.98, top=.83, bottom=.10, hspace=.64, wspace=.12)
for row, browser in enumerate(("chrome", "firefox")):
    for col, (direction, field) in enumerate((("Download", "downloadMbit"), ("Upload", "uploadMbit"))):
        ax = axes[row, col]
        ax.axvline(0, color="#41546a", linewidth=1.2)
        for pos, (label, (_, color)) in enumerate(headline_tools.items()):
            values = paired_rates[label, None if label in terminal_tools else browser, field]
            if not values:
                continue
            center, low, high = quartiles(values)
            ax.scatter(values, [pos] * len(values), color=color, alpha=.24, s=13)
            ax.hlines(pos, low, high, color=color, linewidth=3, zorder=3)
            ax.scatter(center, pos, color=color, edgecolor="white", linewidth=.8, s=56,
                       marker="D" if label in terminal_tools else "o", zorder=4)
        style_axis(ax, f"{browser.capitalize()}  /  {direction}", "Difference from same-pass iperf3", labels=col == 0)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: "0%" if value == 0 else f"{value:+g}%"))
save_chart(fig, "throughput.png", "Reporting accuracy on a 1 Gbit/s link",
           "Dot: median   /   Line: middle 50%   /   Diamonds: terminal medians   /   0%: matches iperf3")

buf = groups["300/30 Mbit/s, 20 ms RTT, 200 ms FIFO"]
total = int(re.search(r"Runs: (\d+)", summary)[1])
included = sum(int(v[0].split("/")[1]) for rows in groups.values() for v in rows.values())
complete = sum(int(v[0].split("/")[0]) for rows in groups.values() for v in rows.values())
path = str(report)
def speed(row, column, divisor=1):
    value = value_at(row, column)
    precision = 2 if divisor != 1 else 1
    return f"{value/divisor:,.{precision}f}" if math.isfinite(value) else "—"


def pair(rows, label, d=2, u=4, divisor=1):
    return " / ".join(speed(rows[label], column, divisor) for column in (d, u)) if label in rows else "—"


def paired_median(label, browser, field):
    values = paired_rates[label, None if label in terminal_tools else browser, field]
    if not values:
        return "—"
    rounded = round(median(values), 1)
    return f"{rounded:+.1f}%" if rounded else "0.0%"


report_date = datetime.fromisoformat(date).strftime("%-d %B %Y")
version_line = summary.splitlines()[1]
historical = ""
if previous:
    previous_date = datetime.fromisoformat(previous[1]).strftime("%-d %B %Y")
    historical = f" ·\n[Previous report, {previous_date}]({previous[0]})"
intro = f"""## Latest GitHub runner results

**{report_date}** · **{complete:,}/{included:,}** scored runs completed · **{len(jobs)}** independent runner jobs · **{total - included:,}** runs excluded by the busy-host rule

{version_line}

### Compare the tradeoffs

The upload columns show how closely each tool agrees with iperf3 on an ordinary 1 Gbit/s link, how fast it reports
on a 10 Gbit/s link, and what it reports on a 100 Mbit/s link with 1% packet loss. Server CPU and memory are from the
1 Gbit/s test. Throughput and resource figures use default Chrome or the native terminal clients.

| Tool or client | 1 Gbit/s upload vs iperf3 (Chrome / Firefox) | 10 Gbit/s upload | Upload with 1% loss | Server upload CPU | Peak server memory |
| --- | ---: | ---: | ---: | ---: | ---: |
"""
cpu = tables(phases, "### ")
shaped_cpu = cpu[shaped_title]
uncapped_title = "Unshaped, offloads on: as fast as the host allows"
unshaped = groups[uncapped_title]
memory = defaultdict(list)
openspeed = []
paired = {tool: [0, 0] for tool in ("graphite-meter-client", "iperf3")}
for result in measurements:
    tool = result["tool"]
    if result["scenario"] == "accuracy-1000":
        if tool == "openspeedtest":
            openspeed.append(result)
        if (result["browser"] == "chrome" or tool in ("graphite-meter-client", "librespeed-cli")) and result.get("serverMemoryPeakBytes") is not None:
            name = (pins["tools"].get(tool) or pins["clients"][tool])["name"]
            memory[name].append(result["serverMemoryPeakBytes"] / 1e6)
    elif result["scenario"] == "unshaped" and tool in paired:
        measurement = result["reported"]
        paired[tool][0] += measurement["uploadMbit"] > measurement["downloadMbit"]
        paired[tool][1] += 1

for label in headline_tools:
    key = chrome_key(label)
    chrome = paired_median(label, "chrome", "uploadMbit")
    firefox = paired_median(label, "firefox", "uploadMbit")
    agreement = f"{chrome} (native)" if label in terminal_tools else f"{chrome} / {firefox}"
    fast_upload = speed(fast[key], 4, 1000)
    loss_upload = speed(loss[key], 4)
    cpu_upload = shaped_cpu.get(key, ["", "n/a", "n/a"])[2].split()[0]
    peak = f"{median(memory[label]):.0f} MB" if memory[label] else "—"
    intro += f"| {display(label)} | {agreement} | {fast_upload} Gbit/s | {loss_upload} Mbit/s | {cpu_upload} s/GB | {peak} |\n"

intro += """
### Shaped throughput

Download / upload medians for default Chrome and native terminal tests. Graphite Meter Browser uses streaming
HTTP/1.1. Connection counts can differ between tools.

| Tool or client | 1 Gbit/s link, Mbit/s | 10 Gbit/s link, Gbit/s | 100 Mbit/s with 1% loss, Mbit/s |
| --- | ---: | ---: | ---: |
"""
for label in shaped_tools:
    key = chrome_key(label)
    intro += f"| {display(label)} | {pair(plain, key)} | {pair(fast, key, divisor=1000)} | {pair(loss, key)} |\n"
intro += f"""
#### Accuracy on the shaped 1 Gbit/s link

![Differences from same-VM iperf3 on the 1 Gbit/s link, by browser and direction]({path}/throughput.png)

Each faint dot is one tool run paired with iperf3 on the same VM, scenario, and pass. The large dot is the median
paired difference. The line spans the 25th to 75th percentile. Zero matches iperf3. Positive values mean the tool
displayed a higher rate. Each VM contributes two passes. Both browser rows show the same native terminal runs for comparison.

### Latency and alternate transports

- **Latency under load.** On the 200 ms FIFO, Graphite Meter in Chrome measured **{buf['Graphite Meter, chrome'][7]} ms**
  during download and **{buf['Graphite Meter, chrome'][8]} ms** during upload, with the queue-based reference in
  parentheses. See the full tables for which tools reported loaded latency.
- **HTTP/3 and WebTransport.** Use the transport-specific rows if you plan to deploy them. On the 1 Gbit/s link,
  Graphite Meter in Chrome reported **{speed(plain['Graphite Meter, HTTP/3, chrome'], 4)} Mbit/s upload over HTTP/3**
  and **{speed(plain['Graphite Meter, WebTransport, chrome'], 4)} Mbit/s over WebTransport**.

[Full tables and run details]({path}) ·
[Hosted run, raw measurements and screenshots]({run_url}){historical}

"""
fig, axes = plt.subplots(1, 3, figsize=(12, 4.4))
fig.subplots_adjust(left=.192, right=.98, top=.78, bottom=.16, wspace=.21)
for ax, (title, field, unit) in zip(axes, (
    ("Server CPU / download", 1, "CPU seconds per GB"),
    ("Server CPU / upload", 2, "CPU seconds per GB"),
    ("Peak server memory", None, "MB"),
), strict=True):
    maximum = 0
    for pos, (label, (_, color)) in enumerate(headline_tools.items()):
        key = chrome_key(label)
        if field is None:
            values = memory.get(label, [])
            if not values:
                continue
            center, low, high = quartiles(values)
        else:
            raw = shaped_cpu.get(key, ["", "n/a", "n/a"])[field]
            if raw == "n/a":
                continue
            center, low, high = map(float, re.findall(r"[\d.]+", raw))
        maximum = max(maximum, high)
        spread_bar(ax, pos, center, low, high, color, f"{center:.0f}" if field is None else f"{center:.3f}")
    style_axis(ax, title, unit, labels=field == 1)
    ax.set_xlim(0, maximum * 1.28 if maximum else 1)
save_chart(fig, "server-load.png", "Server resources at 1 Gbit/s",
           "Default Chrome and native terminal   /   Lower uses fewer resources   /   Median and middle 50%")

def first(part):
    return part.split()[0]


def gbit(part):
    return f'{float(first(part))/1000:.2f}' if first(part) != 'n/a' else '—'


load = f'''### Server load at 1 Gbit/s

The browser and terminal tests use the same shaped link. CPU seconds per GB measure server container work per GB counted
on its interface during each phase. Memory is the median of each run’s peak container memory.

![Server download CPU, upload CPU, and peak memory on the same 1 Gbit/s path]({report}/server-load.png)

Bars show medians. Whiskers show the middle half of observed runs. Each metric uses its own scale.

| Tool or client | Download / upload, Mbit/s | Server download CPU, s/GB | Server upload CPU, s/GB | Peak server memory, MB |
| --- | ---: | ---: | ---: | ---: |
'''
for label in headline_tools:
    key = chrome_key(label)
    down, up = (first(plain[key][i]) for i in (2, 4))
    cpu_down, cpu_up = (first(value) for value in shaped_cpu.get(key, ["", "n/a", "n/a"])[1:3])
    peak = f'{median(memory[label]):.0f}' if label in memory else '—'
    load += f'| {display(label)} | {down} / {up} | {cpu_down} | {cpu_up} | {peak} |\n'

chart = f'![Uncapped download and upload for browser tools, terminal clients, and the iperf3 reference]({report}/uncapped.png)'
load += f'''
### Uncapped throughput

The unshaped scenario removes the rate limit and artificial delay and keeps offloads enabled. These are median
single-test rates over the runner’s virtual network. The server has one vCPU and the browser has two. The browser,
server, and runner can each cap the result. A capacity test for a production server would also need separate client
machines and concurrent tests. **Graphite Meter Terminal** runs `graphite-meter-client --url http://10.71.2.10:7246
--report`. The default path uses streaming HTTP/1.1 with six lanes in each direction, 10-second download and upload
windows, and loaded latency enabled. The full tables include the separately measured transport variants.

{chart}

Bars show the median. Whiskers span the 25th to 75th percentile of repeated runs for the same setup.
The browser rows use default Chrome settings. The terminal rows use native clients. iperf3 is the reference. The full tables also show
client-side browser CPU. Native client CPU is unmeasured.

| Browser tool | Chrome down / up, Gbit/s | Firefox down / up, Gbit/s | Chrome server CPU, s/GB | Chrome server peak, MB |
| --- | ---: | ---: | ---: | ---: |
'''
for label in browser_tools:
    chrome = unshaped[chrome_key(label)]
    firefox = unshaped[f"{label}, firefox"]
    load += f'| {display(label)} | {gbit(chrome[1])} / {gbit(chrome[2])} | {gbit(firefox[1])} / {gbit(firefox[2])} | {chrome[3]} | {chrome[4]} |\n'
load += '''
| Native client | Down / up, Gbit/s | Server CPU, s/GB | Server peak, MB |
| --- | ---: | ---: | ---: |
'''
for label in (*terminal_tools, reference_tool):
    cells = unshaped[label]
    load += f'| {display(label)} | {gbit(cells[1])} / {gbit(cells[2])} | {cells[3]} | {cells[4]} |\n'
uncapped_cpu = cpu.get(uncapped_title, {}).get('Graphite Meter terminal client', ['', 'n/a', 'n/a'])
terminal_up, terminal_runs = paired['graphite-meter-client']
iperf_up, iperf_runs = paired['iperf3']
if terminal_runs and iperf_runs:
    load += f'''
Graphite Meter Terminal uploaded faster than it downloaded in **{terminal_up} of {terminal_runs}** uncapped tests.
iperf3 did so in **{iperf_up} of {iperf_runs}**. The server used a median **{first(uncapped_cpu[1])} CPU s/GB** while
sending and **{first(uncapped_cpu[2])} CPU s/GB** while receiving for Graphite Meter Terminal. The terminal counts
download bytes and time at the client and upload bytes and time at the server.
'''
load += f'\n[Download and upload CPU breakdown for all scenarios and transports]({report}/server-cpu.md)\n\n'
(report / 'server-cpu.md').write_text(f'# Server CPU by phase, {date}\n\n[Full benchmark report](README.md)\n\n' + phases.split('\n\n', 1)[1])
fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.65))
fig.subplots_adjust(left=.208, right=.98, top=.77, bottom=.16, wspace=.17)
for ax, (direction, field) in zip(axes, (("Download", 1), ("Upload", 2)), strict=True):
    maximum = 0
    for pos, (label, (_, color)) in enumerate(shaped_tools.items()):
        raw = unshaped[chrome_key(label)][field]
        if raw == "n/a":
            continue
        center, low, high = (float(value) / 1000 for value in re.findall(r"[\d.]+", raw))
        maximum = max(maximum, high)
        spread_bar(ax, pos, center, low, high, color, f"{center:.2f}")
    style_axis(ax, direction, "Gbit/s", labels=field == 1, tools=shaped_tools)
    ax.set_xlim(0, maximum * 1.22 if maximum else 1)
save_chart(fig, "uncapped.png", "Single-test throughput without shaping",
           "Default Chrome and native terminal   /   Median and middle 50%   /   Separate scales for each direction")

check = """### Independent upload check

The 1 Gbit/s OpenSpeedTest results below use the tool’s displayed payload rate and independent network counters.
The shaper measures a median over busy intervals and includes protocol overhead. The server-interface rate, when
available, averages bytes received during sustained upload intervals. Neither uses the app’s timing window, so their
difference from the displayed rate is a diagnostic rather than an exact payload error.

| Browser | Displayed upload, Mbit/s | Shaper busy median, Mbit/s | Server interface, Mbit/s | Above paired iperf3 |
| --- | ---: | ---: | ---: | ---: |
"""
for browser in ("chrome", "firefox"):
    label = f"OpenSpeedTest, {browser}"
    records = [result for result in openspeed if result["browser"] == browser]
    link = [value for result in records
            if (value := (result.get("queues") or {}).get("up", {}).get("medianOwnLinkMbit")) is not None]
    received = shaped_cpu.get(label, [])[6:7]
    display_mbit = first(plain[label][4])
    differences = paired_rates["OpenSpeedTest", browser, "uploadMbit"]
    above = sum(value > 0 for value in differences)
    shaper_median = f"{median(link):.1f}" if link else "—"
    receiver_median = first(received[0]) if received else "—"
    comparison = f"{above}/{len(differences)}" if differences else "—"
    check += f"| {browser.capitalize()} | {display_mbit} | {shaper_median} | {receiver_median} | {comparison} |\n"
check += "\n"

start = original.index("## Latest GitHub runner results")
end = original.index("## What runs", start)
readme.write_text(original[:start] + intro.replace("### Latency and alternate transports", load + check + "### Latency and alternate transports") + original[end:])
if output := os.environ.get("GITHUB_OUTPUT"):
    with Path(output).open("a") as stream:
        print(f"report={report}", file=stream)
