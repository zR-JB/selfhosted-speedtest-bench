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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts
charts.configure_matplotlib()

NO_LOADED_LATENCY = "graphite-meter-no-loaded-latency"
TERMINAL_NO_LOADED_LATENCY = "graphite-meter-client-no-loaded-latency"
TOOLS = {
    "graphite-meter": "Graphite Meter Browser",
    NO_LOADED_LATENCY: "Graphite Meter without loaded latency",
    "librespeed": "LibreSpeed",
    "librespeed-go": "LibreSpeed Go backend",
    "librespeed-rust": "LibreSpeed Rust backend",
    "openspeedtest": "OpenSpeedTest",
    "graphite-meter-client": "Graphite Meter Terminal",
    TERMINAL_NO_LOADED_LATENCY: "Graphite Meter Terminal without loaded latency",
    "librespeed-cli": "LibreSpeed CLI",
    "iperf3": "iperf3 (reference)",
}
TERMINAL = ("graphite-meter-client", TERMINAL_NO_LOADED_LATENCY, "librespeed-cli")
PLAIN = "accuracy-1000"
FAST = "accuracy-10000"
LOSS = "loss-100"
LONG = "long-300"
PROXY = "proxy-1000"
FIFO = "bufferbloat-300-30"
UNCAPPED = "unshaped"
DOWNLOAD = "downloadMbit"
UPLOAD = "uploadMbit"

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
end = original.index("<!-- historic-trends-start -->", start) if "<!-- historic-trends-start -->" in original[start:original.index("## What runs", start)] else original.index("## What runs", start)
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
                  "blocks": [{key: block[key] for key in ("scenario", "rep", "order", "noise", "noiseAfter", "startedAt", "endedAt", "baseRttMs") if key in block}
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
report_date = datetime.fromisoformat(date).strftime("%d.%m.%Y")
releases = pins["tools"] | pins["clients"]
BROWSER = tuple(tool for tool in TOOLS if tool in pins["tools"])
CHROME = [(tool, "chrome") for tool in BROWSER]
FIREFOX = [(tool, "firefox") for tool in BROWSER]
NATIVE = [(tool, None) for tool in TERMINAL if tool in pins["clients"]]
REFERENCE = ("iperf3", None)
CLIENTS = [*CHROME, *NATIVE, REFERENCE]
reference_versions = {job["host"].get("iperf3") for job in jobs}
reference_version = "Unrecorded" if None in reference_versions else ", ".join(sorted(reference_versions))
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


def client_cpu(row):
    cpu = row["reported"].get("browserCpuSeconds")
    if cpu is None:
        cpu = row["reported"].get("clientCpuSeconds")
    link = sum(row["linkBytes"].values())
    return cpu * 1e9 / link if cpu is not None and link else None


def server_rx(row, divisor=1):
    phase = row["serverPhases"]["up"]
    byte_count, ms = phase.get("directionBytes"), phase.get("milliseconds")
    return byte_count * 0.008 / ms / divisor if byte_count is not None and ms else None


def idle_delta(row):
    reported = row["reported"].get("idleLatencyMs")
    return reported - row["baseRttMs"] if reported is not None and "baseRttMs" in row else None


def fifo_latency(direction):
    def expected(row):
        queue = row["queues"][direction].get("medianQueueMs")
        return row["baseRttMs"] + queue if queue is not None and "baseRttMs" in row else None
    return expected


def loaded_delta(field, direction):
    expected = fifo_latency(direction)
    def difference(row):
        value = row["reported"].get(field)
        estimate = expected(row)
        return value - estimate if value is not None and estimate is not None else None
    return difference


def above_reference(scenario, client):
    values = [delta for row in groups[scenario, client] if (delta := paired(row, UPLOAD)) is not None]
    return (sum(value > 0 for value in values), len(values)) if values and client != REFERENCE else None


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
    asset = f"{report}/{filename}.png"
    return f"[![{description}]({asset})]({asset})"


def picture_figure(stem, description, base=None):
    prefix = f"{base or report}/{stem}"
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{prefix}-dark.png">\n'
        f'  <img src="{prefix}-light.png" alt="{description}" width="100%">\n'
        "</picture>"
    )


def companion(filename, description, *, open_by_default=False):
    tag = "<details open>" if open_by_default else "<details>"
    return f"{tag}\n<summary>{description}</summary>\n\n{figure(filename, description)}\n\n</details>"


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


def leaders(values, digits, preference):
    if preference == "closest":
        scores = {client: abs(round(value, digits)) for client, value in values.items()}
    else:
        direction = -1 if preference == "highest" else 1
        scores = {client: direction * round(value, digits) for client, value in values.items()}
    best = min(scores.values(), default=None)
    return {client for client, value in scores.items() if value == best}


def show_version(client):
    tool, _ = client
    if client == REFERENCE:
        return "iperf3" if reference_version == "Unrecorded" else f"iperf3 {reference_version}"
    version = releases[tool]["version"]
    if tool == NO_LOADED_LATENCY:
        return f"Graphite Meter {version}\nwithout loaded latency"
    if tool == TERMINAL_NO_LOADED_LATENCY:
        return f"Graphite Meter Terminal {version}\nwithout loaded latency"
    return f"{TOOLS[tool]} {version}"


chrome_group = (f"Chrome {pins['browsers']['chrome']['version']}", CHROME)
firefox_group = (f"Firefox {pins['browsers']['firefox']['version']}", FIREFOX)
native_group = ("Native terminal", NATIVE)
reference_group = ("TCP reference", [REFERENCE])
client_groups = [chrome_group, firefox_group, native_group]
vm_count = len(jobs)

resource_metrics = [
    ("Server CPU during download at 1 Gbit/s", "download-cpu", "CPU seconds per GB (lower is better)", phase_cpu("down"), 3, DOWNLOAD),
    ("Server CPU during upload at 1 Gbit/s", "upload-cpu", "CPU seconds per GB (lower is better)", phase_cpu("up"), 3, UPLOAD),
    ("Peak server memory at 1 Gbit/s", "peak-memory", "Peak container memory (MB, lower is better)", peak_memory, 1, None),
]

charts.render_throughput_chart(
    report / "chart-throughput",
    report_date=report_date,
    vm_count=vm_count,
    measure=measure,
    rate=rate,
)
charts.render_accuracy_chart(
    report / "chart-accuracy",
    report_date=report_date,
    vm_count=vm_count,
    measure=measure,
    paired=paired,
    rate=rate,
    shaper_upload=lambda row: row["queues"]["up"].get("medianOwnLinkMbit"),
    server_rx=server_rx,
    fifo_latency=fifo_latency,
    loaded_delta=loaded_delta,
    above_reference=above_reference,
)
charts.render_resources_chart(
    report / "chart-resources",
    report_date=report_date,
    vm_count=vm_count,
    groups=groups,
    measure=measure,
    phase_cpu=phase_cpu,
    peak_memory=peak_memory,
    client_cpu=client_cpu,
    rate=rate,
)
charts.render_transports_chart(
    report / "chart-transports",
    report_date=report_date,
    vm_count=vm_count,
    measure=measure,
    rate=rate,
)
charts.render_hardware_chart(
    report / "chart-hardware",
    report_date=report_date,
    vm_count=vm_count,
    by_vm=by_vm,
    paired_vms=paired_vms,
    rate=rate,
    jobs=jobs,
)


def group_leaders(values, digits, preference):
    return set().union(*(leaders({client: values[client] for client in group if values.get(client) is not None},
                                 digits, preference) for _, group in client_groups))


def ranked_values(clients, scenario, metric, digits, preference):
    values = {client: point(measure(scenario, client, metric)) for client in clients}
    best = group_leaders(values, digits, preference)
    return {client: f"**{number(value, digits)}**" if client in best else number(value, digits)
            for client, value in values.items()}


def ranked_rates(clients, scenario, divisor, digits):
    down, up = (ranked_values(clients, scenario, rate(field, divisor), digits, "highest") for field in (DOWNLOAD, UPLOAD))
    return {client: f"{down[client]} / {up[client]}" for client in clients}


tested_versions = [[TOOLS[tool], releases[tool]["version"]] for tool in TOOLS if tool in releases]
version_rows = list(tested_versions)
browser_versions = " · ".join(f"{browser.capitalize()} {pin['version']}" for browser, pin in pins["browsers"].items())
version_rows += [[browser.capitalize(), pin["version"]] for browser, pin in pins["browsers"].items()]
version_rows.append([TOOLS[REFERENCE[0]], reference_version])
bench_links = (f"[Full report and tested versions]({report}) · [Benchmark source]({repo}/tree/{source}) · "
               f"[Workflow run and raw artifacts]({run_url})")
if previous:
    bench_links += f" · [Previous report]({previous})"
tool_versions = table(["Tested release", "Version"], version_rows)
tested_tools = " · ".join(f"{name} {version}" for name, version in tested_versions)
shape_rates = [ranked_rates(CLIENTS, scenario, divisor, digits)
               for scenario, divisor, digits in ((PLAIN, 1, 1), (FAST, 1000, 2), (LOSS, 1, 1))]
shape_rows = [[client_name(client), *(rates[client] for rates in shape_rates)] for client in CLIENTS]
shape_table = table(["Tool or client", "1 Gbit/s (Mbit/s)", "10 Gbit/s (Gbit/s)", "1% loss (Mbit/s)"], shape_rows)
all_clients = [*CHROME, *FIREFOX, *NATIVE, REFERENCE]
uncapped_rates = ranked_rates(all_clients, UNCAPPED, 1000, 1)
uncapped_table = table(
    ["Tool or client", "Median down / up (Gbit/s)", "Max down / up (Gbit/s)", "Client CPU (s/GB)"],
    [[client_name(client), uncapped_rates[client],
      " / ".join(number(max((row["reported"][field] / 1000 for row in groups[UNCAPPED, client]
                             if field in row["reported"]), default=None)) for field in (DOWNLOAD, UPLOAD)),
      latest_value(UNCAPPED, client, client_cpu, 2)]
     for client in all_clients],
)
resource_headers = ["Tool or client", "Down / up (Mbit/s)", "Down CPU (s/GB)", "Up CPU (s/GB)", "Peak RAM (MB)"]
resource_clients = [*CLIENTS, *FIREFOX]
resource_rankings = [ranked_values(resource_clients, PLAIN, metric, digits, "lowest")
                     for _, _, _, metric, digits, _ in resource_metrics]
resource_rows = [[client_name(client), rate_pair(PLAIN, client, 1, 1),
                  *(ranking[client] for ranking in resource_rankings)]
                 for client in resource_clients]
resource_table = table(resource_headers, resource_rows)

absolute_cpu = table(
    ["Tool or client", "Download (CPU s)", "Upload (CPU s)", "Test total (CPU s)"],
    [[client_name(client), *(latest_value(PLAIN, client, lambda row: row["serverPhases"][direction].get("cpuSeconds"), 2)
                             for direction in ("down", "up")),
      latest_value(PLAIN, client, total_server_cpu, 2)]
     for client in [*CLIENTS, *FIREFOX]],
)

def interval_label(values, digits=1, signed=False, bold=False):
    if not values:
        return "—"
    center, low, high = spread(values)
    center_text = number(center, digits, signed)
    if bold:
        center_text = f"**{center_text}**"
    return f"{center_text} [{number(low, digits, signed)}, {number(high, digits, signed)}] (n={len(values)})"


start_gaps = [gap for client in [*CHROME, *FIREFOX, *NATIVE] for row in groups[PLAIN, client]
              if (gap := difference_in_minutes(row)) is not None]
match_timing = ""
if start_gaps:
    match_timing = (f"Tests ran sequentially. App and iperf3 start times were a median of "
                    f"{number(median(start_gaps))} minutes apart (maximum {number(max(start_gaps))}).")
agreement_clients = [*CHROME, *FIREFOX, *NATIVE]
agreement_metrics = [lambda row, field=field: paired(row, field) for field in (DOWNLOAD, UPLOAD)]
agreement_leaders = [group_leaders({client: point(measure(PLAIN, client, metric)) for client in agreement_clients},
                                   1, "closest") for metric in agreement_metrics]
agreement_table = table(
    ["Tool or client", "Download difference (%)", "Upload difference (%)"],
    [[client_name(client), *(interval_label(measure(PLAIN, client, metric), signed=True, bold=client in best)
                             for metric, best in zip(agreement_metrics, agreement_leaders, strict=True))]
     for client in agreement_clients],
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
loaded_clients = [client for client in [*CHROME, *FIREFOX, *NATIVE] if client[0].startswith("graphite-meter")]
fifo_table = table(
    ["Tool or client", "During download (ms)", "During upload (ms)"],
    [[client_name(client), *(
        f"{latest_value(FIFO, client, rate(field))} / {latest_value(FIFO, client, fifo_latency(direction))}"
        for field, direction in loaded_fields
    )] for client in loaded_clients],
)


fifo_deltas = table(
    ["Tool or client", "During download (ms)", "During upload (ms)"],
    [[client_name(client), *(interval_label(measure(FIFO, client, loaded_delta(field, direction)), signed=True)
                             for field, direction in loaded_fields)]
     for client in loaded_clients],
)


def shaper_upload(row):
    return row["queues"]["up"].get("medianOwnLinkMbit")


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
scope = """Tools keep their own test durations and connection settings. Default Graphite Meter runs include loaded latency.
Its without-loaded-latency profiles omit the idle stage and loaded probes. The benchmark disables LibreSpeed
and OpenSpeedTest’s throughput compensation. [Deployment settings](#what-runs)"""
latency_method = """The idle baseline is the minimum of ten ICMP pings before each scenario pass. Browser and terminal
probes can include additional protocol and processing time. On the FIFO path, the loaded estimate adds the
same run’s median queue delay to that baseline. The app and queue sampler use distinct timing windows. Fair queuing can put
probe traffic in a separate queue, so fq_codel runs lack a loaded-latency reference."""
uncapped_method = """Unshaped runs remove the rate limit and artificial delay, with offloads enabled. The runner gives the
server one vCPU and the client two. The tool, client, server and VM can all affect the observed rate.
These are single-test results on a virtual link. Production capacity also depends on the network and
simultaneous demand."""
has_native_client_cpu = any(
    row["reported"].get("clientCpuSeconds") is not None
    for client in [*NATIVE, REFERENCE] for row in groups[UNCAPPED, client]
)
resource_method = (
    "Server CPU is container CPU time per decimal GB of server-interface traffic during each phase (counting both directions), "
    "or total container CPU per shaper GB on unshaped. Peak memory is per-run container memory.peak in decimal MB. "
    + (
        "Client CPU divides browser process-tree CPU (browser rows) or container cgroup CPU (native rows) by shaper GB."
        if has_native_client_cpu
        else "Client CPU measures the browser process tree per shaper GB; native client cgroup CPU was not yet collected in this run."
    )
)
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
terminal_fast = [latest_value(FAST, client, rate(UPLOAD, 1000), 2) for client in (gm_terminal, ls_terminal)]
terminal_rates = [rate_pair(UNCAPPED, client, 1000, 1) for client in (gm_terminal, ls_terminal, REFERENCE)]
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
    ["CPU and kernel", "VMs", *(client_name(client) for client in NATIVE), "iperf3", "GM above iperf3"],
    hardware_rows,
)
resource_notes = (
    f"With Chrome, Graphite Meter Browser’s median peak memory was **{latest_value(PLAIN, gm_browser, peak_memory, 1)} MB**. "
    f"The LibreSpeed deployments ranged from {results_range(PLAIN, [client for client in CHROME if client[0].startswith("librespeed")], peak_memory)} MB. "
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
terminal_uncapped_rx = latest_value(UNCAPPED, gm_terminal, lambda row: server_rx(row, 1000))
if terminal_uncapped_rx != "—":
    terminal_resource_notes += (
        f" On the unshaped path, the server interface recorded **{terminal_uncapped_rx} Gbit/s** of inbound traffic "
        f"during the Graphite Meter Terminal upload. Server CPU there was "
        f"**{latest_value(UNCAPPED, gm_terminal, phase_cpu('up'), 3)} CPU s/GB** for Graphite Meter Terminal "
        f"and **{latest_value(UNCAPPED, ls_terminal, phase_cpu('up'), 3)} CPU s/GB** for LibreSpeed CLI."
    )
fifo_checks = [above_reference(FIFO, client) for client in ost]
fifo_gaps = [gap for client in ost for row in groups[FIFO, client]
             if (gap := difference_in_minutes(row)) is not None]
fifo_timing = (
    f"Matched FIFO passes ran a median of {number(median(fifo_gaps))} minutes apart "
    f"(maximum {number(max(fifo_gaps))}, n={len(fifo_gaps)})."
    if fifo_gaps else ""
)
fifo_notes = ""
if all(fifo_checks):
    fifo_notes = (f"On the 30 Mbit/s FIFO path, OpenSpeedTest’s reported upload exceeded the matched iperf3 receiver rate in "
                  f"**{fifo_checks[0][0]}/{fifo_checks[0][1]} Chrome** and "
                  f"**{fifo_checks[1][0]}/{fifo_checks[1][1]} Firefox** passes. {fifo_timing}")

# Neutral, dynamically derived summary bullets scoped strictly to the plotted default rosters
default_chrome = [c for c in CHROME if c[0] != NO_LOADED_LATENCY]
default_firefox = [c for c in FIREFOX if c[0] != NO_LOADED_LATENCY]
default_native = [c for c in NATIVE if c[0] != TERMINAL_NO_LOADED_LATENCY]
def _best_client(scenario, roster, metric, mode="max"):
    scored = [(c, v) for c in roster if (v := point(measure(scenario, c, metric))) is not None]
    if not scored:
        return None, None
    return max(scored, key=lambda kv: kv[1]) if mode == "max" else min(scored, key=lambda kv: kv[1])

chr_10g_dl = results_range(FAST, default_chrome, rate(DOWNLOAD, 1000), 2)
chr_10g_ul = results_range(FAST, default_chrome, rate(UPLOAD, 1000), 2)
ff_10g_ul = results_range(FAST, default_firefox, rate(UPLOAD, 1000), 2)
loss_chr_dn_top, loss_chr_dn_val = _best_client(LOSS, default_chrome, rate(DOWNLOAD), "max")
loss_chr_ul_top, loss_chr_ul_val = _best_client(LOSS, default_chrome, rate(UPLOAD), "max")
long_chr_top, _ = _best_client(LONG, default_chrome, rate(UPLOAD), "max")
cpu_dn_top, cpu_dn_val = _best_client(PLAIN, default_chrome, phase_cpu("down"), "min")
cpu_up_top, cpu_up_val = _best_client(PLAIN, default_chrome, phase_cpu("up"), "min")
nat_cpu_top, nat_cpu_val = _best_client(PLAIN, default_native, phase_cpu("up"), "min")
ram_chr_top, ram_chr_val = _best_client(PLAIN, default_chrome, peak_memory, "min")
ram_chr_others = results_range(PLAIN, [c for c in default_chrome if c != ram_chr_top], peak_memory, 1)
proxy_chrome = [c for c in default_chrome if measure(PROXY, c, peak_memory)]
ram_proxy_top, ram_proxy_val = _best_client(PROXY, proxy_chrome, peak_memory, "min")
ram_proxy_others = results_range(PROXY, [c for c in proxy_chrome if c != ram_proxy_top], peak_memory, 0)

if loss_chr_dn_top and loss_chr_ul_top:
    if loss_chr_dn_top == loss_chr_ul_top:
        loss_phrase = (
            f"On 1% packet loss among plotted Chrome rows, {client_name(loss_chr_dn_top)} leads both directions "
            f"with medians of **{number(loss_chr_dn_val, 1)} / {number(loss_chr_ul_val, 1)} Mbit/s**"
        )
    else:
        loss_phrase = (
            f"On 1% packet loss among plotted Chrome rows, {client_name(loss_chr_dn_top)} leads download "
            f"(**{number(loss_chr_dn_val, 1)} Mbit/s**) and {client_name(loss_chr_ul_top)} leads upload "
            f"(**{number(loss_chr_ul_val, 1)} Mbit/s**)"
        )
else:
    loss_phrase = ""
long_phrase = (
    f"; on 160 ms RTT Chrome upload, {client_name(long_chr_top)} leads at **{latest_value(LONG, long_chr_top, rate(UPLOAD), 1)} Mbit/s**"
    if long_chr_top else ""
)
if cpu_dn_top and cpu_up_top:
    if cpu_dn_top == cpu_up_top:
        cpu_chr_phrase = (
            f"{client_name(cpu_dn_top)} uses the lowest Chrome server CPU per GB on both download "
            f"(**{number(cpu_dn_val, 3)} s/GB**) and upload (**{number(cpu_up_val, 3)} s/GB**)"
        )
    else:
        cpu_chr_phrase = (
            f"{client_name(cpu_dn_top)} uses the lowest Chrome server CPU per GB on download "
            f"(**{number(cpu_dn_val, 3)} s/GB**) and {client_name(cpu_up_top)} on upload (**{number(cpu_up_val, 3)} s/GB**)"
        )
else:
    cpu_chr_phrase = ""
cpu_nat_phrase = (
    f", and {client_name(nat_cpu_top)} uses the lowest server CPU during native upload "
    f"(**{number(nat_cpu_val, 3)} s/GB** at {latest_value(PLAIN, nat_cpu_top, rate(UPLOAD), 0)} Mbit/s)"
    if nat_cpu_top else ""
)
if ram_chr_top:
    proxy_clause = ""
    if ram_proxy_top:
        if ram_proxy_top == ram_chr_top:
            proxy_clause = (
                f"; **{number(ram_proxy_val, 1)} MB** sum of server + nginx peaks vs {ram_proxy_others} MB"
            )
        else:
            proxy_clause = (
                f"; behind nginx, {client_name(ram_proxy_top)} uses the lowest sum of server + nginx peaks "
                f"at **{number(ram_proxy_val, 1)} MB** vs {ram_proxy_others} MB"
            )
    ram_phrase = (
        f", while {client_name(ram_chr_top)} uses the lowest peak server RAM with Chrome "
        f"(**{number(ram_chr_val, 1)} MB** direct vs {ram_chr_others} MB for other Chrome servers{proxy_clause})"
    )
else:
    ram_phrase = ""

key_findings = "\n".join([
    f"- **10 Gbit/s & hard links (default plotted clients):** Chrome download medians reach **{chr_10g_dl} Gbit/s** (`9.56 Gbit/s` link), while upload medians stop at **{chr_10g_ul} Gbit/s** in Chrome and **{ff_10g_ul} Gbit/s** in Firefox with wide VM-to-VM spread. {loss_phrase}{long_phrase}.",
    f"- **Unshaped native runner split:** Pooled medians hide a runner-hardware reversal — {native_comparison}",
    f"- **Server resource trade-offs (1 Gbit/s):** {cpu_chr_phrase}{cpu_nat_phrase}{ram_phrase}.",
])

probes_comparison = ""
if NO_LOADED_LATENCY in releases or TERMINAL_NO_LOADED_LATENCY in releases:
    probe_metrics = [
        ("Download (Mbit/s)", rate(DOWNLOAD), 1),
        ("Upload (Mbit/s)", rate(UPLOAD), 1),
        ("Download server CPU (s/GB)", phase_cpu("down"), 3),
        ("Upload server CPU (s/GB)", phase_cpu("up"), 3),
        ("Total server CPU (s)", total_server_cpu, 2),
    ]
    probe_cases = [("1 Gbit/s", PLAIN, browser.capitalize(), (NO_LOADED_LATENCY, browser), ("graphite-meter", browser))
                   for browser in ("chrome", "firefox") if NO_LOADED_LATENCY in releases]
    if TERMINAL_NO_LOADED_LATENCY in releases:
        probe_cases.extend((path, scenario, "Terminal", (TERMINAL_NO_LOADED_LATENCY, None), gm_terminal)
                           for path, scenario in (("1 Gbit/s", PLAIN), ("10 Gbit/s", FAST), ("Unshaped", UNCAPPED)))
    probe_rows = [
        [path, label, *(interval_label(list(paired_vms(scenario, variant, default, metric).values()),
                                               digits, signed=True)
                                 for _, metric, digits in probe_metrics)]
        for path, scenario, label, variant, default in probe_cases
    ]
    probes_comparison = (
        "### Graphite Meter without loaded latency\n\n"
        "Within each client, both profiles use the same server build, automatic connection settings, and transfer durations. "
        "The variant skips the app’s idle-latency stage and loaded probes. Each cell is **without loaded latency minus default** on the same VM and pass, "
        "summarized across VMs as median [middle 50%]. Total server CPU includes the skipped idle stage.\n\n"
        + table(["Path", "Client", *(label for label, _, _ in probe_metrics)], probe_rows) + "\n\n"
    )

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
    "### Unshaped throughput and client CPU",
    uncapped_method + "\n" + "Each maximum is the fastest retained pass in that direction. "
    "The two maxima can come from different passes. Client CPU divides browser process-tree CPU "
    "(browser rows) or container cgroup CPU (native rows, where recorded) by total shaper GB.",
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
    *([probes_comparison.rstrip()] if probes_comparison else []),
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

**{report_date}** · {bench_count} {runner_scope} Each chart plots the median across VMs after reducing each VM’s retained passes to its own median; whiskers and bands show the middle 50% (IQR) across VMs.

{bench_links}

{key_findings}

### 1. High-speed throughput (10 Gbit/s & Unshaped)

{picture_figure("chart-throughput", "10 Gbit/s shaped and unshaped throughput with VM IQR whiskers across all default native, Chrome, and Firefox clients and iperf3.")}

10 Gbit/s shaped links use 2 ms RTT with offloads on (`9.56 Gbit/s` modeled TCP payload ceiling); unshaped runs remove rate limits on 4-vCPU runners (1 server / 2 client / 1 shaper).
[Shaped summary]({report}/#shaped-throughput) · [10 Gbit/s spread]({report}/#10-gbits-upload-spread) · [Unshaped tables]({report}/#unshaped-throughput-and-client-cpu)

### 2. Accuracy, hard links & latency

{picture_figure("chart-accuracy", "1 Gbit/s upload agreement vs same-pass iperf3, 1% loss and 160 ms high-BDP throughput, 30 Mbit/s FIFO upload counter dot plot, and paired Graphite Meter loaded RTT vs FIFO queue estimate.")}

{fifo_notes}
[1 Gbit/s agreement]({report}/#matched-1-gbits-agreement) · [Upload counter checks]({report}/#upload-counter-checks) · [Idle & FIFO latency]({report}/#idle-latency-against-icmp)

### 3. Server & client resource efficiency

{picture_figure("chart-resources", "Split 1 Gbit/s server download and upload CPU, unshaped total server CPU per GB, deployment-faceted peak server memory with achieved rates, and grouped client-side CPU efficiency.")}

{resource_method}
[Full resource tables]({report}/#server-resources-at-1-gbits) · [All server CPU phases]({report}/server-cpu.md) · [Without-loaded-latency delta]({report}/#graphite-meter-without-loaded-latency)

### 4. Protocol & transport scaling

{picture_figure("chart-transports", "HTTP/1.1 vs HTTP/2 vs HTTP/3 vs WebTransport throughput in Chrome (10 Gbit/s) and native terminal clients (separate 10 Gbit/s and unshaped scales).")}

[1 Gbit/s transports]({report}/{case_link(PLAIN)}) · [10 Gbit/s transports]({report}/{case_link(FAST)}) · [Reverse proxy]({report}/{case_link("proxy-1000")})

### 5. Runner hardware & kernel split

{picture_figure("chart-hardware", "Per-VM unshaped native upload grouped by GitHub runner CPU and cloud kernel, alongside paired per-VM Graphite Meter Terminal minus iperf3 differences.")}

{native_comparison} [Hardware breakdown]({report}/#unshaped-native-upload-by-runner-hardware) · [All pooled pass tables]({report}/#pooled-pass-tables)

"""
if not args.from_archive:
    (report / "provenance.json").write_text(json.dumps(provenance, separators=(",", ":"), ensure_ascii=False) + "\n")
    (report / "measurements.json.gz").write_bytes(gzip.compress(archive, compresslevel=9, mtime=0))
    (report / "server-cpu.md").write_text(
        f"# Server CPU by phase, {report_date}\n\n[Full benchmark report and tested versions](README.md)\n\n"
        "These tables pool retained passes. The overview gives each VM equal weight.\n\n" + phases.split("\n\n", 1)[1]
    )
# Render historic trends AFTER writing provenance.json & measurements.json.gz so new campaigns appear immediately.
history_entries = charts.render_historic_trends(Path("results"), Path("results/history-trends")) if not historical else []
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
(report / "README.md").write_text(f"""# GitHub runner benchmark, {report_date}

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

## Tested versions

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
    updated = original[:start] + overview + original[end:]
    if history_entries:
        first_d = datetime.fromisoformat(history_entries[0]["date"]).strftime("%d.%m.%Y")
        last_d = datetime.fromisoformat(history_entries[-1]["date"]).strftime("%d.%m.%Y")
        history_block = (
            "<!-- historic-trends-start -->\n"
            "## Historic trends\n\n"
            f"Automatically updated after every full 15-job GitHub runner campaign (**{len(history_entries)} campaigns** "
            f"from **{first_d}** to **{last_d}**). Each point is the campaign median of VM medians; vertical ticks show "
            "the middle 50% (IQR) of VMs; dotted vertical lines mark Graphite Meter release transitions.\n\n"
            + picture_figure("history-trends", "Throughput, accuracy and server resource trends across all published GitHub runner campaigns.", base="results")
            + "\n<!-- historic-trends-end -->"
        )
        if "<!-- historic-trends-start -->" in updated and "<!-- historic-trends-end -->" in updated:
            h_start = updated.index("<!-- historic-trends-start -->")
            h_end = updated.index("<!-- historic-trends-end -->") + len("<!-- historic-trends-end -->")
            updated = updated[:h_start] + history_block + updated[h_end:]
        else:
            updated = updated.rstrip() + "\n\n" + history_block + "\n"
    readme.write_text(updated)
if (output := os.environ.get("GITHUB_OUTPUT")) and not args.from_archive and not historical:
    with Path(output).open("a") as stream:
        print(f"report={report}", file=stream)
