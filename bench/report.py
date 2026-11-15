import gzip
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median, quantiles
from tempfile import TemporaryDirectory

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

TOOLS = {
    "graphite-meter": "Graphite Meter Browser",
    "librespeed": "LibreSpeed",
    "librespeed-go": "LibreSpeed Go backend",
    "librespeed-rust": "LibreSpeed Rust backend",
    "openspeedtest": "OpenSpeedTest",
    "graphite-meter-client": "Graphite Meter Terminal",
    "librespeed-cli": "LibreSpeed CLI",
    "iperf3": "iperf3 (reference)",
}
TERMINAL = ("graphite-meter-client", "librespeed-cli")
BROWSER = tuple(tool for tool in TOOLS if tool not in (*TERMINAL, "iperf3"))
CHROME = [(tool, "chrome") for tool in BROWSER]
FIREFOX = [(tool, "firefox") for tool in BROWSER]
NATIVE = [(tool, None) for tool in TERMINAL]
REFERENCE = ("iperf3", None)
CLIENTS = [*CHROME, *NATIVE, REFERENCE]
PLAIN = "accuracy-1000"
FAST = "accuracy-10000"
LOSS = "loss-100"
FIFO = "bufferbloat-300-30"
UNCAPPED = "unshaped"
DOWNLOAD = "downloadMbit"
UPLOAD = "uploadMbit"
INK, MUTED, LINE = "#192b3d", "#455b6e", "#dbe4eb"
BROWSER_COLOR, NATIVE_COLOR, REF_COLOR = "#1c6f89", "#71448c", "#465563"
BAND = {BROWSER_COLOR: "#f5f9fb", NATIVE_COLOR: "#f7f3fa", REF_COLOR: "#f1f4f7"}

plt.rcParams.update({
    "figure.facecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "axes.titleweight": "bold",
})

parser = ArgumentParser()
parser.add_argument("run")
parser.add_argument("artifacts", type=Path, nargs="?")
parser.add_argument("--rerender", action="store_true", help="Render again when this run already headlines the README")
parser.add_argument("--from-archive", action="store_true", help="Read the published provenance and scalar measurements")
args = parser.parse_args()
run = args.run
if not run.isascii() or not run.isdecimal():
    parser.error("Expected a numeric GitHub Actions run ID")
if args.from_archive == bool(args.artifacts):
    parser.error("Pass either a job artifacts directory or --from-archive")

readme = Path("README.md")
original = readme.read_text()
start = original.index("## Latest GitHub runner results")
end = original.index("## What runs", start)
links = re.findall(r"results/(\d{4}-\d{2}-\d{2})-ci-run-(\d+)", original[start:end])
latest = int(links[0][1]) if links else 0
historical = int(run) < latest
if int(run) <= latest and not args.rerender:
    print("The README already shows this run or a newer one.")
    sys.exit(0)
previous = next((f"results/{day}-ci-run-{number}" for day, number in links if int(number) < int(run)), "")
if args.from_archive or historical:
    archives = list(Path("results").glob(f"*-ci-run-{run}"))
    if len(archives) != 1:
        sys.exit(f"Expected one published report for run {run}")
    report = archives[0]
    document = (report / "README.md").read_text()
    prior = re.search(r"\[Previous report\]\(\.\./(\d{4}-\d{2}-\d{2}-ci-run-\d+)\)", document)
    previous = f"results/{prior[1]}" if prior else ""
if args.from_archive:
    provenance = json.loads((report / "provenance.json").read_text())
    if provenance["runId"] != run:
        sys.exit(f"Archive run ID differs from {run}")
    summary = document.split("<!-- pooled-pass-tables -->\n", 1)[1]
    archive = gzip.decompress((report / "measurements.json.gz").read_bytes())
    if hashlib.sha256(archive).hexdigest() != provenance["measurementsSha256"]:
        sys.exit("Measurements archive does not match provenance")
else:
    jobs = sorted(args.artifacts.glob("job-*"))
    if len(jobs) != 15:
        sys.exit("Expected artifacts for all 15 benchmark jobs")
    manifests = [json.loads((job / "manifest.json").read_text()) for job in jobs]
    revision, pins = (manifests[0][key] for key in ("bench", "pins"))
    if not re.fullmatch(r"[a-f0-9]{7,40}", revision):
        sys.exit("Missing benchmark source revision")
    source = subprocess.check_output(["git", "rev-parse", "--verify", f"{revision}^{{commit}}"], text=True).strip()
    source_scenarios = subprocess.check_output(["git", "show", f"{source}:scenarios.json"], text=True)
    scenario_defs = json.loads(source_scenarios)
    scenario_ids = {s["id"] for s in scenario_defs}
    for job, manifest in zip(jobs, manifests, strict=True):
        planned = set(manifest["scenarios"])
        blocks = manifest["blocks"]
        expected = {(scenario, rep) for scenario in planned for rep in (1, 2)}
        if (manifest["reps"] != 2 or planned | set(manifest["skipped"]) != scenario_ids
                or len(blocks) != len(expected) or {(b["scenario"], b["rep"]) for b in blocks} != expected):
            print("The run did not cover the full two-pass benchmark. Skipping publication.")
            sys.exit(0)
        expected_files = {f"{block['scenario']}-{block['rep']}-{tool}-{browser if browser != 'null' else 'cli'}.json"
                          for block in blocks for tool, browser in map(lambda item: item.split("/"), block["order"])}
        if {file.name for file in (job / "runs").glob("*.json")} != expected_files:
            sys.exit(f"Missing measurements in {job.name}")
        if manifest["pins"] != pins or manifest["bench"] != revision:
            sys.exit("Benchmark jobs used different pins or source revisions")
    provenance = {
        "runId": run,
        "benchmarkRevision": source,
        "pins": pins,
        "scenarios": scenario_defs,
        "jobs": [{"job": job.name,
                  **{key: manifest[key] for key in ("host", "seed", "startedAt", "endedAt", "reps", "skipped")},
                  "blocks": [{key: block[key] for key in ("scenario", "rep", "order", "noise", "baseRttMs")}
                             for block in manifest["blocks"]]}
                 for job, manifest in zip(jobs, manifests, strict=True)],
    }
    with TemporaryDirectory() as temporary:
        data = Path(temporary) / "measurements.json"
        scenario_file = Path(temporary) / "scenarios.json"
        scenario_file.write_text(source_scenarios)
        env = {**os.environ, "SB_SCENARIOS": str(scenario_file)}
        summary = subprocess.check_output(
            ["node", "bench/summarize.js", *jobs], text=True, env={**env, "SB_REPORT_DATA": str(data)}
        )
        phases = subprocess.check_output(["node", "bench/phases.js", *jobs], text=True, env=env)
        archive = data.read_bytes()
    provenance["measurementsSha256"] = hashlib.sha256(archive).hexdigest()

source, pins, jobs = (provenance[key] for key in ("benchmarkRevision", "pins", "jobs"))
scenarios = {s["id"]: s for s in provenance["scenarios"]}
date = min(datetime.fromisoformat(job["startedAt"]) for job in jobs).date().isoformat()
report_date = datetime.fromisoformat(date).strftime("%-d %B %Y")
report = Path(f"results/{date}-ci-run-{run}")
repo = "https://github.com/zR-JB/selfhosted-speedtest-bench"
run_url = f"{repo}/actions/runs/{run}"
report.mkdir(exist_ok=True)
measurements = json.loads(archive)
runs, noisy = measurements["runs"], measurements["noisy"]
completed = [row for row in runs if row["reported"]["outcome"] == "complete"]
groups = defaultdict(list)
for row in completed:
    groups[row["scenario"], (row["tool"], row.get("browser"))].append(row)
baseline = {(row["scenario"], row["job"], row["rep"]): row for row in completed if row["tool"] == "iperf3"}
measured = [row for row in completed if row["scenario"] in (PLAIN, FAST, LOSS, FIFO, UNCAPPED)]
if not measured:
    sys.exit("No completed measurements for the overview comparisons")


def same_pass(row):
    return row["job"], row["rep"]


def paired(row, field):
    ref = baseline.get((row["scenario"], *same_pass(row)))
    value = row["reported"].get(field)
    base = ref["reported"].get(field) if ref else None
    return 100 * (value / base - 1) if value is not None and base is not None and base > 0 else None


def by_vm(scenario, client, metric):
    per_job = defaultdict(list)
    for row in groups[scenario, client]:
        value = metric(row)
        if value is not None and math.isfinite(value):
            per_job[row["job"]].append(value)
    return {job: median(values) for job, values in per_job.items()}


def measure(scenario, client, metric):
    return list(by_vm(scenario, client, metric).values())


def spread(values):
    if len(values) == 1:
        return (values[0],) * 3
    low, center, high = quantiles(values, n=4, method="inclusive")
    return center, low, high


def point(values):
    return median(values) if values else None


def number(value, digits=1, signed=False):
    if value is None:
        return "—"
    value = round(value, digits) or 0
    return f"{value:{'+' if signed and value else ''},.{digits}f}"


def rate(field, divisor=1):
    return lambda row: row["reported"][field] / divisor if field in row["reported"] else None


def phase_cpu(direction):
    def per_gb(row):
        phase = row["serverPhases"][direction]
        return phase["cpuSeconds"] * 1e9 / phase["bytes"] if phase.get("bytes") else None
    return per_gb


def peak_memory(row):
    peak = row.get("serverMemoryPeakBytes")
    return peak / 1e6 if peak is not None else None


def total_server_cpu(row):
    return row.get("serverCpuSeconds")


def browser_cpu(row):
    cpu = row["reported"].get("browserCpuSeconds")
    link = sum(row["linkBytes"].values())
    return cpu * 1e9 / link if cpu is not None and link else None


def server_rx(row):
    phase = row["serverPhases"]["up"]
    byte_count, ms = phase.get("directionBytes"), phase.get("milliseconds")
    return byte_count * 0.008 / ms if byte_count is not None and ms else None


def idle_delta(row):
    reported = row["reported"].get("idleLatencyMs")
    return reported - row["baseRttMs"] if reported is not None and "baseRttMs" in row else None


def fifo_latency(direction):
    def expected(row):
        queue = row["queues"][direction].get("medianQueueMs")
        return row["baseRttMs"] + queue if queue is not None and "baseRttMs" in row else None
    return expected


def table(headers, rows):
    heading = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---", *(["---:"] * (len(headers) - 1))]) + " |"]
    return "\n".join([*heading, *("| " + " | ".join(row) + " |" for row in rows)])


def client_name(client):
    tool, browser = client
    return TOOLS[tool] + (f" · {browser.capitalize()}" if browser else "")


def latest_value(scenario, client, metric, digits=1, signed=False):
    return number(point(measure(scenario, client, metric)), digits, signed)


def rate_pair(scenario, client, divisor, digits):
    return " / ".join(latest_value(scenario, client, rate(field, divisor), digits) for field in (DOWNLOAD, UPLOAD))


def figure(filename, description):
    asset = f"{report}/{filename}"
    return f"[![{description}]({asset})]({asset})"


def case_link(scenario):
    heading = re.sub(r"[^\w -]", "", scenarios[scenario]["title"].lower()).replace(" ", "-")
    return f"#{heading}"


def difference_in_minutes(row):
    ref = baseline.get((row["scenario"], row["job"], row["rep"]))
    started = row["reported"].get("startedAt")
    reference_start = ref["reported"].get("startedAt") if ref else None
    return abs(started - reference_start) / 60000 if started and reference_start else None


def paired_vms(scenario, client, other, metric):
    baseline = {same_pass(row): metric(row) for row in groups[scenario, other]}
    deltas = defaultdict(list)
    for row in groups[scenario, client]:
        value, reference = metric(row), baseline.get(same_pass(row))
        if value is not None and reference is not None:
            deltas[row["job"]].append(value - reference)
    return {job: median(values) for job, values in deltas.items()}


def results_range(scenario, clients, metric, digits=1, signed=False):
    values = [point(measure(scenario, client, metric)) for client in clients]
    if any(value is None for value in values):
        return "—"
    low, high = (number(value, digits, signed) for value in (min(values), max(values)))
    if signed:
        return f"{low}% to {high}%" if low != high else f"{low}%"
    return low if low == high else f"{low}–{high}"


def render_chart(filename, title, subtitle, groups, panels, *, differences=False, show_vms=False, labels=False):
    rows = []
    bands = []
    y = 0
    for heading, clients, color in groups:
        bands.append((y, y + len(clients) + .51, heading, color))
        y += .92
        for client in clients:
            rows.append((y, client, color))
            y += 1
        y += .75
    height = 1.65 + .29 * y
    fig, axes = plt.subplots(1, len(panels), figsize=(8.8, height))
    fig.subplots_adjust(left=.290, right=.970, top=1 - 1.19 / height, bottom=.50 / height,
                        wspace=.2 if len(panels) == 2 else .27)
    values = [[compute(client) for _, client, _ in rows] for _, _, compute in panels]
    if differences:
        extent = [value for panel in values for series in panel for value in series]
        left, right = min([-1, *extent]), max([1, *extent])
        padding = (right - left) * .08
        limits = [(left - padding, right + padding)] * len(panels)
    elif len({unit for _, unit, _ in panels}) == 1:
        right = max((max(series) if show_vms else spread(series)[2]
                     for panel in values for series in panel if series), default=1)
        limits = [(0, right * (1.25 if labels else 1.08))] * len(panels)
    else:
        limits = [(0, max((spread(series)[2] for series in panel if series), default=1) * 1.24) for panel in values]
    for panel_index, (ax, (heading, unit, _), panel, limit) in enumerate(zip(axes, panels, values, limits, strict=True)):
        ax.set_xlim(limit)
        ax.set_ylim(rows[-1][0] + .60, -.50)
        ax.set_title(heading, loc="left", fontsize=13, pad=13)
        ax.set_xlabel(unit, fontsize=10, labelpad=6)
        ax.set_axisbelow(True)
        ax.set_yticks([])
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5 if len(axes) == 2 else 4))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:+g}%" if value else "0%") if differences
                                     else FuncFormatter(lambda value, _: f"{value:g}"))
        ax.tick_params(axis="x", length=3, color=LINE, labelsize=10, pad=4)
        ax.grid(axis="x", color=LINE, linewidth=.75)
        if labels:
            ax.text(.99, 1.01, "Median", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color=MUTED)
        ax.axvline(0, color=MUTED, linewidth=1.1, zorder=2)
        for spine in ax.spines.values():
            spine.set_visible(False)
        for top, bottom, label, color in bands:
            ax.axhspan(top - .42, bottom, color=BAND[color], linewidth=0, zorder=0)
            if panel_index == 0:
                ax.text(-.045, top, label, transform=ax.get_yaxis_transform(), ha="right", va="center",
                        fontsize=11, color=color, weight="bold")
        for (row_y, client, color), series in zip(rows, panel, strict=True):
            if panel_index == 0:
                ax.text(-.045, row_y, TOOLS[client[0]], transform=ax.get_yaxis_transform(),
                        ha="right", va="center", fontsize=10.75)
            if not series:
                ax.text(.035, row_y, "—", transform=ax.get_yaxis_transform(), color=MUTED, va="center")
                continue
            center, low, high = spread(series)
            if differences or show_vms:
                offsets = [row_y + ((index % 5) - 2) * .103 for index in range(len(series))]
                ax.scatter(series, offsets, color=color, s=15, alpha=.70, linewidth=0, zorder=3)
            ax.hlines(row_y, low, high, color=color, linewidth=3.2, zorder=4)
            ax.scatter(center, row_y, color=color, s=47, edgecolor="white", linewidth=.8, zorder=5,
                       marker="D" if client in NATIVE else "s" if client == REFERENCE else "o")
            if labels:
                ax.text(.99, row_y, number(center, 1), transform=ax.get_yaxis_transform(), ha="right",
                        va="center", fontsize=10, color=INK)
    fig.text(.02, 1 - .24 / height, title, fontsize=18, weight="bold", va="top")
    fig.text(.02, 1 - .59 / height, subtitle, fontsize=10.5, color=MUTED, va="top")
    fig.savefig(report / filename, dpi=170)
    plt.close(fig)


browser_terminal_groups = [("Chrome", CHROME, BROWSER_COLOR), ("Firefox", FIREFOX, BROWSER_COLOR),
                           ("Native terminal", NATIVE, NATIVE_COLOR)]
reference_group = [("TCP reference", [REFERENCE], REF_COLOR)]
render_chart(
    "throughput.png", "Agreement with iperf3 at 1 Gbit/s", "Matched within the same VM and pass. Zero matches the reference.",
    browser_terminal_groups,
    [(heading, "Difference from iperf3", lambda client, field=field: measure(PLAIN, client, lambda row: paired(row, field)))
     for heading, field in (("Download", DOWNLOAD), ("Upload", UPLOAD))], differences=True,
)
render_chart(
    "uncapped.png", "Observed throughput without shaping", "Gbit/s on the runner’s virtual network, one test at a time",
    browser_terminal_groups + reference_group,
    [(heading, "Gbit/s", lambda client, field=field: measure(UNCAPPED, client, rate(field, 1000)))
     for heading, field in (("Download", DOWNLOAD), ("Upload", UPLOAD))], show_vms=True, labels=True,
)
resource_metrics = [
    ("Download CPU", "CPU s/GB", phase_cpu("down"), 3),
    ("Upload CPU", "CPU s/GB", phase_cpu("up"), 3),
    ("Peak memory", "MB", peak_memory, 1),
]
render_chart(
    "server-load.png", "Server resources at 1 Gbit/s", "Chrome and native clients on the same shaped link. Each panel has its own scale.",
    [browser_terminal_groups[0], browser_terminal_groups[2], *reference_group],
    [(heading, unit, lambda client, metric=metric: measure(PLAIN, client, metric))
     for heading, unit, metric, _ in resource_metrics],
)

version_rows = [[TOOLS[tool], (pins["tools"] | pins["clients"])[tool]["version"]] for tool in TOOLS if tool != "iperf3"]
version_rows += [[browser.capitalize(), pin["version"]] for browser, pin in pins["browsers"].items()]
bench_links = (f"[Full report and tested versions]({report}) · [Benchmark source]({repo}/tree/{source}) · "
               f"[Workflow run and raw artifacts]({run_url})")
if previous:
    bench_links += f" · [Previous report]({previous})"
tool_versions = table(["Tested release", "Version"], version_rows)
shape_rows = [
    [TOOLS[client[0]], *(rate_pair(scenario, client, divisor, digits)
                         for scenario, divisor, digits in ((PLAIN, 1, 1), (FAST, 1000, 2), (LOSS, 1, 1)))]
    for client in CLIENTS
]
shape_table = table(["Tool or client", "1 Gbit/s (Mbit/s)", "10 Gbit/s (Gbit/s)", "1% loss (Mbit/s)"], shape_rows)
uncapped_table = table(
    ["Tool or client", "Median down / up (Gbit/s)", "Max down / up (Gbit/s)", "Browser CPU (s/GB)"],
    [[client_name(client), rate_pair(UNCAPPED, client, 1000, 1),
      " / ".join(number(max((row["reported"][field] / 1000 for row in groups[UNCAPPED, client]
                             if field in row["reported"]), default=None)) for field in (DOWNLOAD, UPLOAD)),
      latest_value(UNCAPPED, client, browser_cpu, 2)]
     for client in [*CHROME, *FIREFOX, *NATIVE, REFERENCE]],
)
resource_headers = ["Tool or client", "Down / up (Mbit/s)", "Down CPU (s/GB)", "Up CPU (s/GB)", "Peak RAM (MB)"]
resource_rows = [[client_name(client), rate_pair(PLAIN, client, 1, 1),
                  *(latest_value(PLAIN, client, metric, digits) for _, _, metric, digits in resource_metrics)]
                 for client in [*CHROME, *NATIVE, REFERENCE, *FIREFOX]]
resource_table = table(resource_headers, resource_rows)

absolute_cpu = table(
    ["Tool or client", "Download (CPU s)", "Upload (CPU s)", "Test total (CPU s)"],
    [[client_name(client), *(latest_value(PLAIN, client, lambda row: row["serverPhases"][direction].get("cpuSeconds"), 2)
                             for direction in ("down", "up")),
      latest_value(PLAIN, client, total_server_cpu, 2)]
     for client in [*CLIENTS, *FIREFOX]],
)

def interval_label(values, digits=1, signed=False):
    if not values:
        return "—"
    center, low, high = spread(values)
    return f"{number(center, digits, signed)} [{number(low, digits, signed)}, {number(high, digits, signed)}] (n={len(values)})"


start_gaps = [gap for client in [*CHROME, *FIREFOX, *NATIVE] for row in groups[PLAIN, client]
              if (gap := difference_in_minutes(row)) is not None]
match_timing = ""
if start_gaps:
    match_timing = (f"Tests ran sequentially. App and iperf3 start times were a median of "
                    f"{number(median(start_gaps))} minutes apart (maximum {number(max(start_gaps))}).")
agreement_table = table(
    ["Tool or client", "Download difference (%)", "Upload difference (%)"],
    [[client_name(client), *(interval_label(measure(PLAIN, client, lambda row: paired(row, field)), signed=True)
                             for field in (DOWNLOAD, UPLOAD))]
     for client in [*CHROME, *FIREFOX, *NATIVE]],
)
fast_upload_table = table(
    ["Tool or client", "Upload (Gbit/s)", "Paired difference from iperf3 (%)"],
    [[client_name(client), interval_label(measure(FAST, client, rate(UPLOAD, 1000)), 2),
      interval_label(measure(FAST, client, lambda row: paired(row, UPLOAD)), signed=True)
      if client != REFERENCE else "—"]
     for client in [*CHROME, *FIREFOX, *NATIVE, REFERENCE]],
)
idle_table = table(
    ["Tool or client", "20 ms path", "40 ms path", "160 ms path"],
    [[client_name(client), *(interval_label(measure(scenario, client, idle_delta), signed=True)
                             for scenario in (PLAIN, LOSS, "long-300"))]
     for client in [*CHROME, *FIREFOX, *NATIVE]],
)
loaded_fields = (("loadedLatencyDownMs", "down"), ("loadedLatencyUpMs", "up"))
loaded_clients = [("graphite-meter", "chrome"), ("graphite-meter", "firefox"), ("graphite-meter-client", None)]
fifo_table = table(
    ["Tool or client", "During download (ms)", "During upload (ms)"],
    [[client_name(client), *(
        f"{latest_value(FIFO, client, rate(field))} / {latest_value(FIFO, client, fifo_latency(direction))}"
        for field, direction in loaded_fields
    )] for client in loaded_clients],
)


def loaded_delta(field, direction):
    expected = fifo_latency(direction)
    def difference(row):
        value = row["reported"].get(field)
        estimate = expected(row)
        return value - estimate if value is not None and estimate is not None else None
    return difference


fifo_deltas = table(
    ["Tool or client", "During download (ms)", "During upload (ms)"],
    [[client_name(client), *(interval_label(measure(FIFO, client, loaded_delta(field, direction)), signed=True)
                             for field, direction in loaded_fields)]
     for client in loaded_clients],
)



def shaper_upload(row):
    return row["queues"]["up"].get("medianOwnLinkMbit")


def above_reference(scenario, client):
    values = [delta for row in groups[scenario, client] if (delta := paired(row, UPLOAD)) is not None]
    return (sum(value > 0 for value in values), len(values)) if values and client != REFERENCE else None


def upload_row(scenario, client):
    cells = [client_name(client), latest_value(scenario, client, rate(UPLOAD)), latest_value(scenario, client, shaper_upload)]
    if receiver_available[scenario]:
        cells.append(interval_label(measure(scenario, client, server_rx)))
    passes = above_reference(scenario, client)
    return [*cells, f"{passes[0]}/{passes[1]}" if passes else "—"]


def upload_check(scenario, clients):
    headers = ["Tool or client", "App rate", "Shaper"]
    if receiver_available[scenario]:
        headers.append("Server RX")
    return table([*headers, "Above iperf3"], [upload_row(scenario, client) for client in clients])


ost = [("openspeedtest", browser) for browser in ("chrome", "firefox")]
receiver_cases = [(PLAIN, "1 Gbit/s path"), (FIFO, "30 Mbit/s upload, deep FIFO")]
receiver_available = {scenario: any(server_rx(row) is not None for row in completed if row["scenario"] == scenario)
                      for scenario, _ in receiver_cases}
receiver_check = "\n\n".join([
    f"**{title}**\n\n{upload_check(scenario, [*ost, REFERENCE])}" for scenario, title in receiver_cases
])
receiver_method = """All rates are in Mbit/s. The shaper reports the median over busy intervals, includes protocol
overhead and can show rates above the configured limit even for iperf3. “Above iperf3” counts passes
where the tool reported a higher rate than the same-VM, same-pass iperf3 receiver. Each VM runs
its two passes sequentially. The separate receiver smoke used the 1 Gbit/s path only."""
if any(receiver_available.values()):
    receiver_method += """
Server RX averages traffic during sustained upload intervals and shows the median, middle 50% and
number of VMs when available. Like the shaper, it includes protocol overhead and uses a separate
timing window. A payload accounting check would require matching bytes and timing to the app."""
else:
    receiver_method += """
This run predates passive server-interface timing. A payload accounting check would require
receiver payload bytes over the app’s reporting window."""
bench_count = (f"**{len(completed):,}/{len(runs):,}** retained runs completed across **{len(jobs)} runner jobs** "
               f"({noisy:,} runs excluded by the busy-host rule).")
skipped_by_all = set.intersection(*(set(job["skipped"]) for job in jobs))
cpu_skips = [s for s in scenarios.values()
             if s["id"] in skipped_by_all and s.get("minHostCpus") and s["downMbit"] is not None]
runner_scope = ""
if cpu_skips:
    speeds = " and ".join(f"{s['downMbit'] / 1000:g}" for s in cpu_skips)
    ceilings = ", ".join(str(count) for count in sorted({s["minHostCpus"] for s in cpu_skips}))
    hosts = ", ".join(str(count) for count in sorted({job["host"]["cpus"] for job in jobs}))
    runner_scope = (f"The {speeds} Gbit/s shaped scenarios are skipped on these {hosts}-vCPU runners. "
                    f"They require {ceilings}+ CPUs.")
vm_method = """We take each VM’s median over its retained passes, then summarize across VMs. A VM contributes once,
with up to two passes. Large marks show medians across VMs. Lines span the middle 50%, and small
marks show VM values where plotted. The spreads describe these runners. Sample sizes and exact
values are in the linked tables."""
scope = """Tools keep their own test durations, connection counts and probes. Graphite Meter keeps loaded probes
enabled in both clients. The other adapters record idle latency. The benchmark disables LibreSpeed
and OpenSpeedTest’s throughput compensation. [Deployment settings](#what-runs)"""
latency_method = """The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference."""
uncapped_method = """Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand."""
resource_method = """Server CPU is container CPU time per decimal GB of server-interface traffic during each phase,
counting bytes in both directions. Peak memory is the container’s per-run peak in decimal MB.
The adjacent reported rates show how much of the same shaped link each setup used. Browser CPU is
measured separately on the client. Native client CPU is unavailable."""
gm_browser = ("graphite-meter", "chrome")
gm_terminal = ("graphite-meter-client", None)
ls_terminal = ("librespeed-cli", None)
firefox_librespeed = [client for client in FIREFOX if client[0].startswith("librespeed")]
firefox_upload = results_range(PLAIN, firefox_librespeed, lambda row: paired(row, UPLOAD), signed=True)
chrome_upload = results_range(PLAIN, CHROME, lambda row: paired(row, UPLOAD), signed=True)
browser_fast = results_range(FAST, CHROME, rate(UPLOAD, 1000), 2)
firefox_fast = results_range(FAST, FIREFOX, rate(UPLOAD, 1000), 2)
browser_fast_deltas = list(paired_vms(FAST, gm_browser, ost[0], rate(UPLOAD, 1000)).values())
browser_fast_comparison = ""
if browser_fast_deltas:
    center, low, high = spread(browser_fast_deltas)
    above = sum(value > 0 for value in browser_fast_deltas)
    browser_fast_comparison = (
        f"Graphite Meter Browser’s same-pass upload difference from OpenSpeedTest in Chrome was "
        f"**{number(center, 2, True)} Gbit/s** (middle 50% {number(low, 2, True)} to {number(high, 2, True)}). "
        f"Graphite Meter Browser reported more on **{above}/{len(browser_fast_deltas)} matched VMs**."
    )
transport_upload = [latest_value(FAST, (tool, "chrome"), rate(UPLOAD, 1000), 2)
                    for tool in ("graphite-meter", "graphite-meter-h2", "graphite-meter-h3", "graphite-meter-wt")]
terminal_fast = [latest_value(FAST, client, rate(UPLOAD, 1000), 2) for client in NATIVE]
terminal_rates = [rate_pair(UNCAPPED, client, 1000, 1) for client in [*NATIVE, REFERENCE]]
native_difference = paired_vms(UNCAPPED, gm_terminal, REFERENCE, rate(UPLOAD))
native_comparison = ""
if native_difference:
    above = sum(value > 0 for value in native_difference.values())
    native_comparison = (f"Graphite Meter Terminal had a higher upload rate than iperf3 on "
                         f"**{above} of {len(native_difference)} VMs** after matching passes.")
by_host = defaultdict(list)
provider_differences = defaultdict(list)
for job in jobs:
    host = job["host"]
    by_host[host["cpu"], host["kernel"]].append(job["job"])
    provider = "Azure-kernel" if host["kernel"].endswith("-azure") else "AWS-kernel" if host["kernel"].endswith("-aws") else "other"
    if job["job"] in native_difference:
        provider_differences[provider].append(native_difference[job["job"]])
if len(provider_differences) > 1:
    split = ", ".join(f"{sum(value > 0 for value in values)}/{len(values)} on {provider} VMs"
                      for provider, values in sorted(provider_differences.items()))
    native_comparison += f" The split was {split}."
hardware_rows = []
for (cpu, kernel), labels in sorted(by_host.items()):
    upload = []
    for client in [*NATIVE, REFERENCE]:
        values = by_vm(UNCAPPED, client, rate(UPLOAD, 1000))
        upload.append(number(point([values[job] for job in labels if job in values])))
    differences = [native_difference[job] for job in labels if job in native_difference]
    hardware_rows.append([f"{cpu} ({kernel})", str(len(labels)), *upload,
                          f"{sum(value > 0 for value in differences)}/{len(differences)}" if differences else "—"])
hardware_table = table(
    ["CPU and kernel", "VMs", "Graphite Meter Terminal", "LibreSpeed CLI", "iperf3", "GM above iperf3"],
    hardware_rows,
)
resource_notes = (
    f"With Chrome, Graphite Meter Browser’s median peak memory was **{latest_value(PLAIN, gm_browser, peak_memory, 1)} MB**. "
    f"The LibreSpeed deployments ranged from {results_range(PLAIN, CHROME[1:4], peak_memory)} MB. "
    f"OpenSpeedTest used **{latest_value(PLAIN, ost[0], phase_cpu('down'), 3)} CPU s/GB** on download and "
    f"**{latest_value(PLAIN, ost[0], phase_cpu('up'), 3)} CPU s/GB** on upload."
)
total_cpu_notes = (
    f"Over the full Chrome test the median total server CPU time was "
    f"**{latest_value(PLAIN, ost[0], total_server_cpu, 2)} s** for OpenSpeedTest and "
    f"**{latest_value(PLAIN, gm_browser, total_server_cpu, 2)} s** for Graphite Meter Browser. "
    f"Total time reflects both the amount of data moved and the work per byte."
)
terminal_resource_notes = (
    f"Graphite Meter Terminal used **{latest_value(PLAIN, gm_terminal, phase_cpu('up'), 3)} CPU s/GB** on upload "
    f"at **{latest_value(PLAIN, gm_terminal, rate(UPLOAD))} Mbit/s**. "
    f"LibreSpeed CLI used **{latest_value(PLAIN, ls_terminal, phase_cpu('up'), 3)} CPU s/GB** "
    f"at **{latest_value(PLAIN, ls_terminal, rate(UPLOAD))} Mbit/s**."
)
fifo_checks = [above_reference(FIFO, client) for client in ost]
fifo_notes = ""
if all(fifo_checks):
    fifo_notes = (f"On the FIFO path, OpenSpeedTest’s reported rate exceeded the matched iperf3 receiver rate in "
                  f"**{fifo_checks[0][0]}/{fifo_checks[0][1]} Chrome** and "
                  f"**{fifo_checks[1][0]}/{fifo_checks[1][1]} Firefox** passes.")

summary_heading = "\n\n".join([
    "### Shaped throughput",
    "Download / upload medians. Browser rows use Chrome. The loss test uses a 100 Mbit/s link, "
    "1% loss in each direction and 40 ms RTT.",
    shape_table,
    "### 10 Gbit/s upload spread",
    "Each cell shows the median [25th, 75th percentile] and number of VMs. The last column uses matched "
    "same-VM, same-pass iperf3 rates. A lower achieved rate can come from any part of the test setup.",
    browser_fast_comparison,
    fast_upload_table,
    "### Matched 1 Gbit/s agreement",
    "Signed percentage differences from iperf3 on the same VM and pass. Each cell shows the median "
    "[25th, 75th percentile] and number of VMs after reducing the matched pass differences within each VM. " + match_timing,
    agreement_table,
    "### Unshaped throughput and browser CPU",
    uncapped_method + "\n" + "Each maximum is the fastest retained pass in that direction. "
    "The two maxima can come from different passes. Browser CPU measures the client process tree "
    "over the full run per GB at the shaper.",
    uncapped_table,
    "#### Unshaped native upload by runner hardware",
    "Upload medians in Gbit/s. “GM above iperf3” counts VMs after matching same-pass comparisons. "
    "CPU, kernel and runner conditions vary together. Groups with one VM show that VM’s median.",
    native_comparison,
    hardware_table,
    "### Server resources at 1 Gbit/s",
    resource_method,
    resource_table,
    "Absolute server CPU time for the complete 1 Gbit/s test and each transfer phase.",
    absolute_cpu,
    "### Upload counter checks",
    receiver_method,
    *(f"**{title}**\n\n{upload_check(scenario, [*CHROME, *FIREFOX, *NATIVE, REFERENCE])}"
      for scenario, title in receiver_cases),
    "### Idle latency against ICMP",
    latency_method + "\n" + "Each cell shows the median paired difference in ms [25th, 75th percentile] and number of VMs.",
    idle_table,
    "### Latency under load on a FIFO",
    "Each cell shows the app’s reported latency followed by the queue-based estimate, in ms.",
    fifo_table,
    "Paired app minus queue estimate in ms, summarized within VMs, then across VMs.",
    fifo_deltas,
])

overview = f"""## Latest GitHub runner results

**{report_date}.** {bench_count}
{runner_scope}

{bench_links}

### Shaped throughput

On the 10 Gbit/s path, reported median uploads ranged from **{browser_fast} Gbit/s in Chrome** and
**{firefox_fast} Gbit/s in Firefox**. Graphite Meter Terminal
reported **{terminal_fast[0]} Gbit/s** and LibreSpeed CLI **{terminal_fast[1]} Gbit/s**.
{browser_fast_comparison} [Upload spread across VMs]({report}/#10-gbits-upload-spread)

Each throughput cell shows **download / upload**. Browser rows use default Chrome. The two terminal
clients use their native defaults. The 1 Gbit/s link uses a 20 ms RTT and has a payload ceiling of
about 956 Mbit/s. The 10 Gbit/s test uses a 2 ms RTT and offloads. iperf3 uses four TCP streams.

{shape_table}

The loss test uses a 100 Mbit/s link, 1% loss in each direction and 40 ms RTT. Chrome reported
**{latest_value(LOSS, ost[0], rate(UPLOAD))} Mbit/s** upload with OpenSpeedTest and
**{latest_value(LOSS, gm_browser, rate(UPLOAD))} Mbit/s** with Graphite Meter Browser.
Connection counts and test windows can change rates on lossy paths.

{vm_method}

{scope}

### Agreement at 1 Gbit/s

Chrome’s median upload differences from iperf3 spanned **{chrome_upload}**. In Firefox, the three
LibreSpeed deployments spanned **{firefox_upload}**.

[Full-size agreement chart]({report}/throughput.png) · [Agreement values for every tool]({report}/#matched-1-gbits-agreement)

{figure("throughput.png", "Download and upload differences from same-VM, same-pass iperf3 for all browser and terminal tools.")}

Zero matches the iperf3 receiver payload rate. Positive values mean the app reported a higher rate.
The comparison reflects both the traffic each setup drove and its reporting method.
{match_timing}

### Unshaped throughput

Median download / upload was **{terminal_rates[0]} Gbit/s** for Graphite Meter Terminal,
**{terminal_rates[1]} Gbit/s** for LibreSpeed CLI and **{terminal_rates[2]} Gbit/s** for iperf3.
{native_comparison}

[Full-size unshaped chart]({report}/uncapped.png) · [Unshaped medians, maxima and browser CPU]({report}/#unshaped-throughput-and-browser-cpu)

{figure("uncapped.png", "Observed download and upload rates for Chrome, Firefox, the terminal clients and iperf3 on the same scale.")}

{uncapped_method}

Graphite Meter Terminal times downloads at the client and uploads at the server. iperf3 reports
the receiver in both directions. [Native upload by runner hardware]({report}/#unshaped-native-upload-by-runner-hardware)

### Server resources at 1 Gbit/s

{resource_notes}

{terminal_resource_notes}

[Full-size resource chart]({report}/server-load.png) · [Server resource values for Chrome, Firefox and terminals]({report}/#server-resources-at-1-gbits)

{figure("server-load.png", "Server download and upload CPU per GB and peak server memory for Chrome tools, the terminal clients and iperf3.")}

{resource_method}

{total_cpu_notes}

{table(resource_headers, resource_rows[:len(CLIENTS)])}

[All server CPU phases]({report}/server-cpu.md)

### OpenSpeedTest upload check

{fifo_notes}

{receiver_check}

{receiver_method}
[Counter data for all tools]({report}/#upload-counter-checks) ·
[Instrumented receiver check](#receiver-counter-validation)

### Idle and loaded latency

{latency_method} [Idle comparisons at 20, 40 and 160 ms]({report}/#idle-latency-against-icmp)

Graphite Meter reports loaded latency during download and upload in this run. On the 300/30 Mbit/s path
with a 200 ms FIFO, each cell shows the app’s median followed by the queue-based estimate.

{fifo_table}

On the 10 Gbit/s path, Graphite Meter Browser in Chrome reported median upload of
**{transport_upload[0]} Gbit/s over HTTP/1.1**, **{transport_upload[1]} over HTTP/2**,
**{transport_upload[2]} over HTTP/3**, and **{transport_upload[3]} over WebTransport**.
[1 Gbit/s transport comparison]({report}/{case_link(PLAIN)}) ·
[Reverse-proxy results]({report}/{case_link("proxy-1000")}) ·
[Additional paths]({report}/#pooled-pass-tables)

"""
if not args.from_archive:
    (report / "provenance.json").write_text(json.dumps(provenance, separators=(",", ":"), ensure_ascii=False) + "\n")
    (report / "measurements.json.gz").write_bytes(gzip.compress(archive, compresslevel=9, mtime=0))
    (report / "server-cpu.md").write_text(
        f"# Server CPU by phase, {date}\n\n[Full benchmark report](README.md)\n\n"
        "These tables pool retained passes. The overview gives each VM equal weight.\n\n" + phases.split("\n\n", 1)[1]
    )
scenario_labels = {
    "accuracy-100": "100 Mbit/s", PLAIN: "1 Gbit/s", FAST: "10 Gbit/s",
    "accuracy-25000": "25 Gbit/s", "accuracy-40000": "40 Gbit/s", FIFO: "Deep FIFO",
    LOSS: "1% loss", "loss-1000": "0.1% loss", "long-300": "160 ms RTT",
    "compete-100": "Competing traffic", "proxy-1000": "Reverse proxy", "multi-200": "Two servers",
    UNCAPPED: "Unshaped",
}
retained_cases = {row["scenario"] for row in runs}
scenario_index = " · ".join(
    f"[{scenario_labels.get(scenario, scenarios[scenario]['title'])}]({case_link(scenario)})"
    for scenario in scenarios if scenario in retained_cases
)
archive_links = "\n".join([
    f"[Benchmark source at {source}]({repo}/tree/{source}) · [Workflow run and raw artifacts]({run_url})",
    "[Provenance and exact pins](provenance.json) · [Retained scalar measurements](measurements.json.gz) · "
    "[Server CPU by phase](server-cpu.md) · [Bench overview](../../README.md)",
])
if previous:
    archive_links += f" · [Previous report](../{Path(previous).name})"
(report / "README.md").write_text(f"""# GitHub runner benchmark, {date}

{bench_count}
{runner_scope}

{archive_links}

The workflow stores the detailed artifacts and screenshots for its retention window. The scalar archive
keeps the inputs used by the overview charts and tables. Read it with `gzip -dc measurements.json.gz`.
Provenance records the job order, CPU allocation, pinned releases and workload definitions.

To regenerate the overview tables and charts from the committed archive, run
`python3 bench/report.py {run} --from-archive --rerender` from the repository root.
The renderer uses Python 3 with Matplotlib. When this is the latest run, the command also updates
the root README. Regenerating the detailed pass tables requires all 15 job artifacts, Node.js 22 or later,
and the benchmark source revision in local Git history. Use
`python3 bench/report.py {run} /path/to/artifacts --rerender` while they remain available.

{tool_versions}

## Overview data

{vm_method}

{summary_heading}

## Pooled pass tables

The tables below pool all retained completed passes for each configuration, including alternate
transports. Their comparison columns show the difference from the modeled TCP payload ceiling
when iperf3 reaches at least 98% of the model in both directions. QUIC rows show measured rates separately.
The matched comparison above uses the measured same-pass receiver rate.
Below-ceiling rates can reflect any constraint on the end-to-end transfer.

{scenario_index}

<!-- pooled-pass-tables -->
{summary}""")
if not historical:
    readme.write_text(original[:start] + overview + original[end:])
if (output := os.environ.get("GITHUB_OUTPUT")) and not args.from_archive and not historical:
    with Path(output).open("a") as stream:
        print(f"report={report}", file=stream)
