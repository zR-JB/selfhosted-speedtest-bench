"""Publication-grade charts and auto-extending historic trends for selfhosted-speedtest-bench."""

import gzip
import json
import math
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median, quantiles

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.ticker import FuncFormatter, MaxNLocator

# Palette: crisp editorial light theme (high contrast on GitHub light & dark modes)
BG = "#ffffff"
CARD_BG = "#f8fafc"
STRIPE = "#f6f8fb"
INK = "#0f172a"
TEXT = "#1e293b"
MUTED = "#64748b"
FAINT = "#94a3b8"
GRID = "#e2e8f0"
DIVIDER = "#cbd5e1"
GOOD_BAND = "#ecfdf5"
GOOD_EDGE = "#10b981"

COLORS = {
    "graphite-meter": "#1d4ed8",
    "graphite-meter-no-loaded-latency": "#6482c8",
    "librespeed": "#0f766e",
    "librespeed-go": "#c2410c",
    "librespeed-rust": "#7c3aed",
    "openspeedtest": "#be185d",
    "graphite-meter-client": "#1d4ed8",
    "graphite-meter-client-no-loaded-latency": "#6482c8",
    "librespeed-cli": "#0f766e",
    "iperf3": "#475569",
}

TRANSPORT_COLORS = {
    "HTTP/1.1": "#1d4ed8",
    "HTTP/2": "#0f766e",
    "HTTP/3": "#d97706",
    "WebTransport": "#7c3aed",
}

NO_LOADED_LATENCY = "graphite-meter-no-loaded-latency"
TERMINAL_NO_LOADED_LATENCY = "graphite-meter-client-no-loaded-latency"
REFERENCE = ("iperf3", None)
PLAIN = "accuracy-1000"
FAST = "accuracy-10000"
LOSS = "loss-100"
LONG = "long-300"
PROXY = "proxy-1000"
FIFO = "bufferbloat-300-30"
UNCAPPED = "unshaped"
DOWNLOAD = "downloadMbit"
UPLOAD = "uploadMbit"


def configure_matplotlib():
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "savefig.edgecolor": GRID,
        "font.family": "DejaVu Sans",
        "text.color": INK,
        "axes.labelcolor": TEXT,
        "xtick.color": MUTED,
        "ytick.color": TEXT,
        "axes.titleweight": "bold",
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
    })


def spread(values):
    if len(values) == 1:
        return (values[0],) * 3
    low, center, high = quantiles(values, n=4, method="inclusive")
    return center, low, high


def fmt_num(value, digits=1, signed=False):
    if value is None or not math.isfinite(value):
        return "—"
    value = round(value, digits) or 0.0
    return f"{value:{'+' if signed and value else ''},.{digits}f}"


def leaders(values, digits, preference):
    if not values:
        return set()
    if preference == "closest":
        scores = {client: abs(round(value, digits)) for client, value in values.items()}
    else:
        direction = -1 if preference == "highest" else 1
        scores = {client: direction * round(value, digits) for client, value in values.items()}
    best = min(scores.values(), default=None)
    return {client for client, value in scores.items() if value == best}


def _header(fig, height_in, kicker, title, subtitle):
    fig.text(0.022, 1 - 0.14 / height_in, kicker, color=MUTED, fontsize=8.0, weight="bold", va="top")
    fig.text(0.022, 1 - 0.34 / height_in, title, color=INK, fontsize=15.5, weight="bold", va="top")
    fig.text(0.022, 1 - 0.66 / height_in, subtitle, color=MUTED, fontsize=8.3, va="top")
    line_y = 1 - 0.90 / height_in
    fig.add_artist(plt.Line2D([0.022, 0.978], [line_y, line_y], transform=fig.transFigure, color=GRID, linewidth=0.9))


def _style_axis(ax, grid_axis="x"):
    ax.set_facecolor(BG)
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.7, linestyle="-")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(GRID)
        ax.spines[side].set_linewidth(0.8)


def _deconflict_labels(items, y_min, y_max, min_gap):
    """Push vertically close end-of-line labels apart so they never overlap."""
    if not items:
        return []
    ordered = sorted(items, key=lambda x: x[0])
    ys = [x[0] for x in ordered]
    # Forward pass: enforce minimum gap upward
    for i in range(1, len(ys)):
        if ys[i] - ys[i - 1] < min_gap:
            ys[i] = ys[i - 1] + min_gap
    # If pushed past top, shift backward
    if ys[-1] > y_max:
        overflow = ys[-1] - y_max
        ys[-1] -= overflow
        for i in range(len(ys) - 2, -1, -1):
            if ys[i + 1] - ys[i] < min_gap:
                ys[i] = ys[i + 1] - min_gap
    ys = [max(y_min, min(y_max, y)) for y in ys]
    return [(orig_y, adj_y, text, color) for (orig_y, text, color), adj_y in zip(ordered, ys, strict=True)]


def render_dot_strip_chart(
    out_path,
    title,
    groups,
    compute,
    *,
    report_date,
    vm_count,
    show_version,
    native_clients,
    unit,
    digits=1,
    preference="highest",
    subtitle_extra="",
    context_fn=None,
    show_max=False,
):
    """Upgraded per-VM dot strip + IQR bar + median + IQR readout chart."""
    difference = preference == "closest"
    has_third = bool(context_fn or show_max)
    rows, sections = [], []
    for heading, clients in groups:
        series = {client: compute(client) for client in clients}
        if not any(series.values()):
            continue
        sections.append((len(rows), heading))
        rows.append(None)
        best = leaders(
            {c: median(v) for c, v in series.items() if c != REFERENCE and v},
            digits,
            preference,
        )
        rows.extend((client, series[client], client in best) for client in clients)

    row_h = 0.325
    top_pad = 1.32
    bot_pad = 0.62
    height = top_pad + bot_pad + row_h * len(rows)
    fig_w = 11.2 if has_third else 10.2
    fig, ax = plt.subplots(figsize=(fig_w, height))
    left_edge = 0.285 if has_third else 0.310
    right_edge = 0.665 if has_third else 0.725
    fig.subplots_adjust(left=left_edge, right=right_edge, top=1 - top_pad / height, bottom=bot_pad / height)

    extent = [val for row in rows if row for val in row[1]]
    left = min([-1.5, *extent]) if difference else 0.0
    right = max([1.5 if difference else 1.0, *extent])
    span = max(right - left, 1e-6)
    pad = span * 0.08
    ax.set_xlim(left - pad if difference else -span * 0.025, right + pad)
    ax.set_ylim(len(rows) - 0.38, -0.78)

    ax.set_xlabel(unit, fontsize=9.0, labelpad=6, color=TEXT)
    ax.set_axisbelow(True)
    ax.set_yticks([])
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
    if difference:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+g}%" if v else "0%"))
        ax.axvspan(-1.0, 1.0, color=GOOD_BAND, alpha=0.85, zorder=0)
        ax.axvline(0.0, color=GOOD_EDGE, linewidth=1.15, linestyle="-", zorder=2)
    ax.tick_params(axis="x", length=3, color=DIVIDER, labelsize=8.6, pad=4)
    ax.grid(axis="x", color=GRID, linewidth=0.75, zorder=1)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Use figure-level blended transform for left labels & right stat columns so column alignment is exact in figure X!
    blended = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax.transData)
    x_sec = 0.024
    x_dot = 0.032
    x_lbl = 0.044
    if has_third:
        col_med = 0.742
        col_iqr = 0.875
        col_ext = 0.976
    else:
        col_med = 0.820
        col_iqr = 0.974
        col_ext = 0.974

    # Column headers
    ax.text(col_med, -0.82, "MEDIAN", transform=blended, ha="right", va="bottom",
            fontsize=7.6, color=MUTED, weight="bold")
    ax.text(col_iqr, -0.82, "IQR [p25, p75]", transform=blended, ha="right", va="bottom",
            fontsize=7.6, color=MUTED, weight="bold")
    if show_max:
        ax.text(col_ext, -0.82, "MAX", transform=blended, ha="right", va="bottom",
                fontsize=7.6, color=MUTED, weight="bold")
    elif context_fn:
        ax.text(col_ext, -0.82, "RATE", transform=blended, ha="right", va="bottom",
                fontsize=7.6, color=MUTED, weight="bold")

    # Full-width row bands in figure X coordinates [0.022, 0.980]
    for y, heading in sections:
        rect = mpatches.Rectangle(
            (0.022, y - 0.44), 0.958, 0.88,
            transform=blended, facecolor="#f1f5f9", edgecolor="none", clip_on=False, zorder=0,
        )
        ax.add_patch(rect)
        ax.text(x_sec, y, heading, transform=blended, ha="left", va="center",
                fontsize=9.3, color=INK, weight="bold")

    stripe_idx = 0
    for y, row in enumerate(rows):
        if row is None:
            stripe_idx = 0
            continue
        client, series, highlighted = row
        color = COLORS.get(client[0], MUTED)
        if stripe_idx % 2 == 1:
            rect = mpatches.Rectangle(
                (0.022, y - 0.48), 0.958, 0.96,
                transform=blended, facecolor=STRIPE, edgecolor="none", clip_on=False, zorder=0,
            )
            ax.add_patch(rect)
        stripe_idx += 1

        lbl = show_version(client)
        t = ax.text(x_lbl, y, lbl, transform=blended, ha="left", va="center",
                    fontsize=8.6, color=INK if highlighted else TEXT,
                    weight="bold" if highlighted else "normal")
        if "\n" in lbl:
            t.set_linespacing(0.88)
        ax.scatter(x_dot, y, transform=blended, color=color, s=24, clip_on=False, zorder=5)
        ax.plot([0.022, 0.980], [y + 0.5, y + 0.5], transform=blended, color="#edf2f7",
                linewidth=0.55, clip_on=False, zorder=1)

        med_text, iqr_text, extra_text = "—", "—", "—"
        if series:
            center, low, high = spread(series)
            offsets = [y + ((i % 5) - 2) * 0.068 for i in range(len(series))]
            ax.scatter(series, offsets, color=color, s=16, alpha=0.42, linewidth=0, zorder=3)
            ax.plot([low, high], [y, y], color=color, linewidth=3.4, solid_capstyle="round", alpha=0.88, zorder=4)
            marker = (
                "D" if client in native_clients
                else "s" if client == REFERENCE
                else "^" if client[0] in (NO_LOADED_LATENCY, TERMINAL_NO_LOADED_LATENCY)
                else "v" if client[1] == "firefox"
                else "o"
            )
            if highlighted:
                ax.scatter(center, y, s=128, facecolor="none", edgecolor=color, linewidth=1.4, marker=marker, zorder=5)
            ax.scatter(center, y, color=color, s=46, edgecolor="#ffffff", linewidth=0.9, marker=marker, zorder=6)

            suffix = "%" if difference else ""
            med_text = fmt_num(center, digits, signed=difference) + suffix
            iqr_text = f"[{fmt_num(low, digits, signed=difference)}, {fmt_num(high, digits, signed=difference)}]"
            if show_max:
                extra_text = fmt_num(max(series), digits)
            elif context_fn:
                extra_text = context_fn(client)

        ax.text(col_med, y, med_text, transform=blended, ha="right", va="center",
                fontsize=9.0, color=INK if highlighted else TEXT, weight="bold" if highlighted else "normal")
        ax.text(col_iqr, y, iqr_text, transform=blended, ha="right", va="center",
                fontsize=8.0, color=MUTED)
        if has_third:
            ax.text(col_ext, y, extra_text, transform=blended, ha="right", va="center",
                    fontsize=8.0, color=MUTED)

    highlight_desc = {"closest": "closest to 0%", "highest": "highest median", "lowest": "lowest median"}[preference]
    sub = f"Dots: {vm_count} runner VMs  ·  Bar: middle 50% (IQR)  ·  Ring & bold: {highlight_desc} per group"
    if difference:
        sub += "  ·  Shaded band: ±1%"
    if subtitle_extra:
        sub += f"  ·  {subtitle_extra}"
    _header(fig, height, f"GITHUB RUNNER BENCHMARK  ·  {report_date}  ·  {vm_count} VMs", title, sub)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)


def render_shaped_paths_dashboard(out_path, *, report_date, vm_count, measure, rate, chrome, firefox, native):
    """2x2 rich shaped-paths dashboard: 10G upload, 1% loss, 160ms high-BDP, behind nginx."""
    fig, axes = plt.subplots(2, 2, figsize=(12.6, 8.9))
    fig.subplots_adjust(left=0.155, right=0.975, top=0.835, bottom=0.065, wspace=0.40, hspace=0.38)

    # Panel A (top-left): 10 Gbit/s Upload across Chrome, Firefox, Native, iperf3
    ax = axes[0, 0]
    _style_axis(ax, "x")
    c_10g = [
        ("GM Browser · Chrome", ("graphite-meter", "chrome")),
        ("OpenSpeedTest · Chrome", ("openspeedtest", "chrome")),
        ("LibreSpeed Go · Chrome", ("librespeed-go", "chrome")),
        ("LibreSpeed PHP · Chrome", ("librespeed", "chrome")),
        ("LibreSpeed Rust · Chrome", ("librespeed-rust", "chrome")),
        ("GM Browser · Firefox", ("graphite-meter", "firefox")),
        ("LibreSpeed Go · Firefox", ("librespeed-go", "firefox")),
        ("OpenSpeedTest · Firefox", ("openspeedtest", "firefox")),
        ("GM Terminal", ("graphite-meter-client", None)),
        ("LibreSpeed CLI", ("librespeed-cli", None)),
        ("iperf3 (reference)", REFERENCE),
    ]
    rows_a = [(lbl, cl, measure(FAST, cl, rate(UPLOAD, 1000))) for lbl, cl in c_10g]
    rows_a = [(lbl, cl, vals) for lbl, cl, vals in rows_a if vals]
    ys = np.arange(len(rows_a))
    for i, (lbl, cl, vals) in enumerate(rows_a):
        c = COLORS.get(cl[0], MUTED)
        med, lo, hi = spread(vals)
        ax.barh(i, med, height=0.58, color=c, alpha=0.20, edgecolor=c, linewidth=0.9, zorder=2)
        ax.plot([lo, hi], [i, i], color=c, linewidth=2.6, solid_capstyle="round", zorder=4)
        ax.scatter(med, i, color=c, s=30, edgecolor="#fff", linewidth=0.7, zorder=5)
        ax.text(max(hi, med) + 0.18, i, f"{med:.2f}", va="center", ha="left", fontsize=8.0, color=INK, weight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows_a], fontsize=8.0)
    ax.invert_yaxis()
    ax.set_xlim(0, 11.4)
    ax.axvline(9.56, color=FAINT, linestyle="--", linewidth=0.9, zorder=1)
    ax.text(9.66, 0.25, "TCP\nceiling", fontsize=7.0, color=MUTED, va="top")
    ax.set_xlabel("Upload (Gbit/s) · bar=median, line=IQR", fontsize=8.2)
    ax.set_title("10 Gbit/s Upload (2 ms RTT, offloads on)", fontsize=10.4, loc="left", pad=10)

    def paired_panel(ax_p, scenario_id, title_p, unit_p, ceiling_x=None, subset=None):
        _style_axis(ax_p, "x")
        items = subset or [
            ("GM Browser · Chrome", ("graphite-meter", "chrome")),
            ("OpenSpeedTest · Chrome", ("openspeedtest", "chrome")),
            ("LibreSpeed Rust · Chrome", ("librespeed-rust", "chrome")),
            ("LibreSpeed PHP · Chrome", ("librespeed", "chrome")),
            ("GM Browser · Firefox", ("graphite-meter", "firefox")),
            ("OpenSpeedTest · Firefox", ("openspeedtest", "firefox")),
            ("GM Terminal", ("graphite-meter-client", None)),
            ("LibreSpeed CLI", ("librespeed-cli", None)),
            ("iperf3 (reference)", REFERENCE),
        ]
        data = []
        for lbl, cl in items:
            d = measure(scenario_id, cl, rate(DOWNLOAD))
            u = measure(scenario_id, cl, rate(UPLOAD))
            if d or u:
                data.append((lbl, cl, median(d) if d else 0.0, median(u) if u else 0.0))
        y = np.arange(len(data))
        h = 0.34
        dl_vals = [x[2] for x in data]
        ul_vals = [x[3] for x in data]
        max_v = max([*dl_vals, *ul_vals, ceiling_x or 1.0])
        ax_p.barh(y - h / 2, dl_vals, height=h, color="#2563eb", alpha=0.86, label="Download", zorder=3)
        ax_p.barh(y + h / 2, ul_vals, height=h, color="#ea580c", alpha=0.82, label="Upload", zorder=3)
        for i, (_, _, dv, uv) in enumerate(data):
            ax_p.text(dv + max_v * 0.015, i - h / 2, f"{dv:.1f}", va="center", ha="left", fontsize=7.4, color="#1e40af")
            ax_p.text(uv + max_v * 0.015, i + h / 2, f"{uv:.1f}", va="center", ha="left", fontsize=7.4, color="#9a3412")
        if ceiling_x:
            ax_p.axvline(ceiling_x, color=FAINT, linestyle="--", linewidth=0.9, zorder=1)
        ax_p.set_yticks(y)
        ax_p.set_yticklabels([x[0] for x in data], fontsize=8.0)
        ax_p.invert_yaxis()
        ax_p.set_xlim(0, max_v * 1.18)
        ax_p.set_xlabel(unit_p, fontsize=8.2)
        ax_p.set_title(title_p, fontsize=10.4, loc="left", pad=10)

    paired_panel(axes[0, 1], LOSS, "100 Mbit/s · 1% Loss Each Way (40 ms RTT)", "Throughput (Mbit/s)")
    paired_panel(axes[1, 0], LONG, "300 Mbit/s · 160 ms RTT (High-BDP Path)", "Throughput (Mbit/s)", ceiling_x=286.9)
    proxy_subset = [
        ("GM Browser · Chrome", ("graphite-meter", "chrome")),
        ("LibreSpeed PHP · Chrome", ("librespeed", "chrome")),
        ("OpenSpeedTest · Chrome", ("openspeedtest", "chrome")),
        ("GM Browser · Firefox", ("graphite-meter", "firefox")),
        ("LibreSpeed PHP · Firefox", ("librespeed", "firefox")),
        ("OpenSpeedTest · Firefox", ("openspeedtest", "firefox")),
        ("iperf3 (direct control)", REFERENCE),
    ]
    paired_panel(axes[1, 1], PROXY, "1 Gbit/s Behind nginx Reverse Proxy (20 ms RTT)", "Throughput (Mbit/s)",
                 ceiling_x=956.4, subset=proxy_subset)

    fig.legend(
        handles=[
            mpatches.Patch(color="#2563eb", alpha=0.86, label="Download (paired panels)"),
            mpatches.Patch(color="#ea580c", alpha=0.82, label="Upload (paired panels)"),
        ],
        loc="upper right", bbox_to_anchor=(0.975, 0.905), ncol=2, frameon=False, fontsize=8.2, handlelength=1.3,
    )

    _header(
        fig, 8.9,
        f"SHAPED & CHALLENGING PATHS  ·  {report_date}  ·  {vm_count} VMs",
        "Throughput across high-speed, lossy, high-RTT & proxied paths",
        "Per-VM medians summarized across runner VMs  ·  Dashed vertical lines: modeled TCP payload ceiling",
    )
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)


def render_transports_chart(out_path, *, report_date, vm_count, measure, rate):
    """Side-by-side HTTP/1.1 vs HTTP/2 vs HTTP/3 vs WebTransport comparison at 10 Gbit/s & Unshaped."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 5.4))
    fig.subplots_adjust(left=0.175, right=0.975, top=0.74, bottom=0.12, wspace=0.38)

    chrome_items = [
        ("Graphite Meter · HTTP/1.1", ("graphite-meter", "chrome"), "HTTP/1.1"),
        ("Graphite Meter · HTTP/2", ("graphite-meter-h2", "chrome"), "HTTP/2"),
        ("Graphite Meter · HTTP/3", ("graphite-meter-h3", "chrome"), "HTTP/3"),
        ("Graphite Meter · WebTransport", ("graphite-meter-wt", "chrome"), "WebTransport"),
        ("LibreSpeed Go · HTTP/1.1", ("librespeed-go", "chrome"), "HTTP/1.1"),
        ("LibreSpeed Go · HTTP/2", ("librespeed-go-h2", "chrome"), "HTTP/2"),
        ("OpenSpeedTest · HTTP/1.1", ("openspeedtest", "chrome"), "HTTP/1.1"),
        ("OpenSpeedTest · HTTP/2", ("openspeedtest-h2", "chrome"), "HTTP/2"),
        ("iperf3 (4 TCP streams)", REFERENCE, None),
    ]
    _style_axis(ax1, "x")
    rows1 = []
    for lbl, cl, proto in chrome_items:
        d = measure(FAST, cl, rate(DOWNLOAD, 1000))
        u = measure(FAST, cl, rate(UPLOAD, 1000))
        if d or u:
            rows1.append((lbl, proto, median(d) if d else 0.0, median(u) if u else 0.0))
    y1 = np.arange(len(rows1))
    h = 0.35
    for i, (lbl, proto, dv, uv) in enumerate(rows1):
        c = TRANSPORT_COLORS.get(proto, COLORS["iperf3"])
        ax1.barh(i - h / 2, dv, height=h, color=c, alpha=0.88, zorder=3)
        ax1.barh(i + h / 2, uv, height=h, color=c, alpha=0.36, edgecolor=c, linewidth=0.9, zorder=3)
        ax1.text(dv + 0.14, i - h / 2, f"{dv:.2f}", va="center", ha="left", fontsize=7.6, color=INK)
        ax1.text(uv + 0.14, i + h / 2, f"{uv:.2f}", va="center", ha="left", fontsize=7.6, color=MUTED)
    ax1.axvline(9.56, color=FAINT, linestyle="--", linewidth=0.9, zorder=1)
    ax1.set_yticks(y1)
    ax1.set_yticklabels([r[0] for r in rows1], fontsize=8.2)
    ax1.invert_yaxis()
    ax1.set_xlim(0, 11.2)
    ax1.set_xlabel("Throughput (Gbit/s)  ·  Solid = Download, Light = Upload", fontsize=8.2)
    ax1.set_title("Chrome on 10 Gbit/s Shaped Path (2 ms RTT)", fontsize=10.3, loc="left", pad=10)

    native_items = [
        ("GM Terminal · HTTP/1.1 (10G)", FAST, ("graphite-meter-client", None), "HTTP/1.1"),
        ("GM Terminal · HTTP/2 (10G)", FAST, ("graphite-meter-client-h2", None), "HTTP/2"),
        ("GM Terminal · HTTP/3 (10G)", FAST, ("graphite-meter-client-h3", None), "HTTP/3"),
        ("LibreSpeed CLI · H1 (10G)", FAST, ("librespeed-cli", None), "HTTP/1.1"),
        ("iperf3 TCP (10G)", FAST, REFERENCE, None),
        ("GM Terminal · HTTP/1.1 (Unsh.)", UNCAPPED, ("graphite-meter-client", None), "HTTP/1.1"),
        ("GM Terminal · HTTP/2 (Unsh.)", UNCAPPED, ("graphite-meter-client-h2", None), "HTTP/2"),
        ("GM Terminal · HTTP/3 (Unsh.)", UNCAPPED, ("graphite-meter-client-h3", None), "HTTP/3"),
        ("iperf3 TCP (Unshaped)", UNCAPPED, REFERENCE, None),
    ]
    _style_axis(ax2, "x")
    rows2 = []
    for lbl, sc, cl, proto in native_items:
        d = measure(sc, cl, rate(DOWNLOAD, 1000))
        u = measure(sc, cl, rate(UPLOAD, 1000))
        if d or u:
            rows2.append((lbl, proto, median(d) if d else 0.0, median(u) if u else 0.0))
    y2 = np.arange(len(rows2))
    max2 = max([r[2] for r in rows2] + [r[3] for r in rows2] + [10.0])
    for i, (lbl, proto, dv, uv) in enumerate(rows2):
        c = TRANSPORT_COLORS.get(proto, COLORS["iperf3"])
        ax2.barh(i - h / 2, dv, height=h, color=c, alpha=0.88, zorder=3)
        ax2.barh(i + h / 2, uv, height=h, color=c, alpha=0.36, edgecolor=c, linewidth=0.9, zorder=3)
        ax2.text(dv + max2 * 0.015, i - h / 2, f"{dv:.1f}", va="center", ha="left", fontsize=7.6, color=INK)
        ax2.text(uv + max2 * 0.015, i + h / 2, f"{uv:.1f}", va="center", ha="left", fontsize=7.6, color=MUTED)
    if len(rows2) > 5:
        ax2.axhline(4.5, color=DIVIDER, linestyle=":", linewidth=1.0)
    ax2.set_yticks(y2)
    ax2.set_yticklabels([r[0] for r in rows2], fontsize=8.2)
    ax2.invert_yaxis()
    ax2.set_xlim(0, max2 * 1.18)
    ax2.set_xlabel("Throughput (Gbit/s)  ·  Solid = Download, Light = Upload", fontsize=8.2)
    ax2.set_title("Native Terminal Clients (10 Gbit/s & Unshaped)", fontsize=10.3, loc="left", pad=10)

    handles = [
        mpatches.Patch(color=TRANSPORT_COLORS[p], label=p)
        for p in ("HTTP/1.1", "HTTP/2", "HTTP/3", "WebTransport")
    ] + [mpatches.Patch(color=COLORS["iperf3"], label="iperf3 TCP")]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.975, 0.845), ncol=5,
               frameon=False, fontsize=8.0, handlelength=1.2)

    _header(
        fig, 5.4,
        f"PROTOCOL & TRANSPORT COMPARISON  ·  {report_date}  ·  {vm_count} VMs",
        "HTTP/1.1 vs HTTP/2 vs HTTP/3 vs WebTransport throughput",
        "All TLS variants use one self-signed certificate per job  ·  Solid bars: Download  ·  Lighter bars: Upload",
    )
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)


def render_resource_overview(out_path, *, report_date, vm_count, measure, phase_cpu, peak_memory, client_cpu):
    """3-panel comprehensive resource efficiency chart: 1G Server CPU, Peak RAM, Client CPU."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14.4, 5.8))
    fig.subplots_adjust(left=0.125, right=0.985, top=0.73, bottom=0.12, wspace=0.56)

    items1 = [
        ("GM Browser · Chrome", ("graphite-meter", "chrome")),
        ("LibreSpeed PHP · Chrome", ("librespeed", "chrome")),
        ("LibreSpeed Go · Chrome", ("librespeed-go", "chrome")),
        ("LibreSpeed Rust · Chrome", ("librespeed-rust", "chrome")),
        ("OpenSpeedTest · Chrome", ("openspeedtest", "chrome")),
        ("GM Terminal", ("graphite-meter-client", None)),
        ("LibreSpeed CLI", ("librespeed-cli", None)),
        ("iperf3 (reference)", REFERENCE),
    ]

    # Panel 1: 1 Gbit/s Server CPU (Download vs Upload s/GB)
    _style_axis(ax1, "x")
    r1 = []
    for lbl, cl in items1:
        dc = measure(PLAIN, cl, phase_cpu("down"))
        uc = measure(PLAIN, cl, phase_cpu("up"))
        if dc or uc:
            r1.append((lbl, cl, median(dc) if dc else 0.0, median(uc) if uc else 0.0))
    y1 = np.arange(len(r1))
    h = 0.35
    m1 = max([x[2] for x in r1] + [x[3] for x in r1] + [1.0])
    ax1.barh(y1 - h / 2, [x[2] for x in r1], height=h, color="#0284c7", alpha=0.90, label="Download", zorder=3)
    ax1.barh(y1 + h / 2, [x[3] for x in r1], height=h, color="#e11d48", alpha=0.82, label="Upload", zorder=3)
    for i, (_, _, dv, uv) in enumerate(r1):
        ax1.text(dv + m1 * 0.02, i - h / 2, f"{dv:.3f}", va="center", ha="left", fontsize=7.4, color="#0369a1")
        ax1.text(uv + m1 * 0.02, i + h / 2, f"{uv:.3f}", va="center", ha="left", fontsize=7.4, color="#9f1239", weight="bold")
    ax1.axhline(4.5, color=DIVIDER, linestyle=":", linewidth=0.9)
    ax1.set_yticks(y1)
    ax1.set_yticklabels([x[0] for x in r1], fontsize=8.0)
    ax1.invert_yaxis()
    ax1.set_xlim(0, m1 * 1.24)
    ax1.set_xlabel("Server CPU (s/GB, lower is better)", fontsize=8.2)
    ax1.set_title("1 Gbit/s Server CPU by Phase", fontsize=10.2, loc="left", pad=22)
    ax1.legend(loc="upper left", bbox_to_anchor=(0.0, 1.07), ncol=2, frameon=False, fontsize=7.7, handlelength=1.1)

    # Panel 2: Peak Server Memory (1 Gbit/s vs Unshaped)
    _style_axis(ax2, "x")
    r2 = []
    for lbl, cl in items1:
        m_1g = measure(PLAIN, cl, peak_memory)
        m_un = measure(UNCAPPED, cl, peak_memory)
        if m_1g or m_un:
            r2.append((lbl, cl, median(m_1g) if m_1g else 0.0, median(m_un) if m_un else 0.0))
    y2 = np.arange(len(r2))
    m2 = max([x[2] for x in r2] + [x[3] for x in r2] + [10.0])
    ax2.barh(y2 - h / 2, [x[2] for x in r2], height=h, color="#4f46e5", alpha=0.86, label="1 Gbit/s", zorder=3)
    ax2.barh(y2 + h / 2, [x[3] for x in r2], height=h, color="#94a3b8", alpha=0.72, label="Unshaped", zorder=3)
    for i, (_, _, v1, v2) in enumerate(r2):
        ax2.text(v1 + m2 * 0.02, i - h / 2, f"{v1:.1f}", va="center", ha="left", fontsize=7.4, color="#3730a3", weight="bold")
        ax2.text(v2 + m2 * 0.02, i + h / 2, f"{v2:.1f}", va="center", ha="left", fontsize=7.4, color=MUTED)
    ax2.axhline(4.5, color=DIVIDER, linestyle=":", linewidth=0.9)
    ax2.set_yticks(y2)
    ax2.set_yticklabels([x[0] for x in r2], fontsize=8.0)
    ax2.invert_yaxis()
    ax2.set_xlim(0, m2 * 1.24)
    ax2.set_xlabel("Peak container memory (MB, lower is better)", fontsize=8.2)
    ax2.set_title("Peak Server Memory", fontsize=10.2, loc="left", pad=22)
    ax2.legend(loc="upper left", bbox_to_anchor=(0.0, 1.07), ncol=2, frameon=False, fontsize=7.7, handlelength=1.1)

    # Panel 3: Client CPU on Unshaped (Chrome, Firefox, and Native when available)
    _style_axis(ax3, "x")
    items3 = [
        ("GM Browser · Chrome", ("graphite-meter", "chrome")),
        ("LibreSpeed Rust · Chrome", ("librespeed-rust", "chrome")),
        ("LibreSpeed Go · Chrome", ("librespeed-go", "chrome")),
        ("OpenSpeedTest · Chrome", ("openspeedtest", "chrome")),
        ("LibreSpeed PHP · Chrome", ("librespeed", "chrome")),
        ("GM Browser · Firefox", ("graphite-meter", "firefox")),
        ("OpenSpeedTest · Firefox", ("openspeedtest", "firefox")),
        ("LibreSpeed Go · Firefox", ("librespeed-go", "firefox")),
        ("LibreSpeed PHP · Firefox", ("librespeed", "firefox")),
        ("GM Terminal", ("graphite-meter-client", None)),
        ("LibreSpeed CLI", ("librespeed-cli", None)),
        ("iperf3 (reference)", REFERENCE),
    ]
    r3 = []
    for lbl, cl in items3:
        vals = measure(UNCAPPED, cl, client_cpu)
        if vals:
            r3.append((lbl, cl, spread(vals)))
    y3 = np.arange(len(r3))
    m3 = max([x[2][2] for x in r3] + [1.0])
    for i, (lbl, cl, (med, lo, hi)) in enumerate(r3):
        c = COLORS.get(cl[0], MUTED)
        ax3.barh(i, med, height=0.58, color=c, alpha=0.20, edgecolor=c, linewidth=0.9, zorder=2)
        ax3.plot([lo, hi], [i, i], color=c, linewidth=2.5, solid_capstyle="round", zorder=4)
        ax3.scatter(med, i, color=c, s=26, edgecolor="#fff", linewidth=0.7, zorder=5)
        ax3.text(max(hi, med) + m3 * 0.025, i, f"{med:.2f}", va="center", ha="left", fontsize=7.6, color=INK, weight="bold")
    ax3.set_yticks(y3)
    ax3.set_yticklabels([x[0] for x in r3], fontsize=8.0)
    ax3.invert_yaxis()
    ax3.set_xlim(0, m3 * 1.24)
    ax3.set_xlabel("Client CPU (s/GB, bar=median, line=IQR)", fontsize=8.2)
    ax3.set_title("Client CPU Efficiency (Unshaped)", fontsize=10.2, loc="left", pad=22)

    _header(
        fig, 5.8,
        f"RESOURCE EFFICIENCY OVERVIEW  ·  {report_date}  ·  {vm_count} VMs",
        "Server CPU per GB, peak memory & client-side CPU",
        "Server metrics from cgroup v2 per run  ·  Client CPU includes browser process tree (and native cgroup CPU where recorded)",
    )
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)


def render_latency_chart(out_path, *, report_date, vm_count, measure, idle_delta, rate, fifo_latency):
    """Side-by-side Idle Latency Overhead vs ICMP and Loaded Latency on 300/30 FIFO."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 5.4))
    fig.subplots_adjust(left=0.165, right=0.975, top=0.73, bottom=0.12, wspace=0.40)

    # Left: Idle latency overhead over ICMP across 20ms, 40ms, 160ms
    _style_axis(ax1, "x")
    idle_items = [
        ("GM Browser · Chrome", ("graphite-meter", "chrome")),
        ("LibreSpeed Rust · Chrome", ("librespeed-rust", "chrome")),
        ("LibreSpeed Go · Chrome", ("librespeed-go", "chrome")),
        ("LibreSpeed PHP · Chrome", ("librespeed", "chrome")),
        ("OpenSpeedTest · Chrome", ("openspeedtest", "chrome")),
        ("GM Browser · Firefox", ("graphite-meter", "firefox")),
        ("OpenSpeedTest · Firefox", ("openspeedtest", "firefox")),
        ("GM Terminal", ("graphite-meter-client", None)),
        ("LibreSpeed CLI", ("librespeed-cli", None)),
    ]
    rows1 = []
    for lbl, cl in idle_items:
        v20 = measure(PLAIN, cl, idle_delta)
        v40 = measure(LOSS, cl, idle_delta)
        v160 = measure(LONG, cl, idle_delta)
        if v20 or v40 or v160:
            rows1.append((
                lbl,
                median(v20) if v20 else None,
                median(v40) if v40 else None,
                median(v160) if v160 else None,
            ))
    y1 = np.arange(len(rows1))
    h = 0.24
    all_v = [v for r in rows1 for v in r[1:] if v is not None]
    min1 = min([0.0, *all_v])
    max1 = max([1.5, *all_v])
    specs = [(-h, "#2563eb", "20 ms"), (0.0, "#d97706", "40 ms (1% loss)"), (h, "#7c3aed", "160 ms")]
    for idx, (dy, col, sname) in enumerate(specs, start=1):
        xs = [r[idx] if r[idx] is not None else 0.0 for r in rows1]
        ax1.barh(y1 + dy, xs, height=h, color=col, alpha=0.84, label=sname, zorder=3)
    ax1.axvline(0.0, color=MUTED, linewidth=0.9, zorder=2)
    ax1.set_yticks(y1)
    ax1.set_yticklabels([r[0] for r in rows1], fontsize=8.1)
    ax1.invert_yaxis()
    ax1.set_xlim(min1 - 0.35, max1 * 1.25)
    ax1.set_xlabel("App idle latency minus ICMP min (ms, closer to 0 is tighter)", fontsize=8.1)
    ax1.set_title("Idle Latency Overhead vs ICMP", fontsize=10.3, loc="left", pad=22)
    ax1.legend(loc="upper left", bbox_to_anchor=(0.0, 1.08), ncol=3, frameon=False, fontsize=7.6, handlelength=1.1)

    # Right: Loaded latency on 300/30 Mbit/s 200 ms FIFO (App vs Queue estimate)
    _style_axis(ax2, "x")
    fifo_items = [
        ("GM Chrome · Download", ("graphite-meter", "chrome"), "loadedLatencyDownMs", "down"),
        ("GM Chrome · Upload", ("graphite-meter", "chrome"), "loadedLatencyUpMs", "up"),
        ("GM Firefox · Download", ("graphite-meter", "firefox"), "loadedLatencyDownMs", "down"),
        ("GM Firefox · Upload", ("graphite-meter", "firefox"), "loadedLatencyUpMs", "up"),
        ("GM Terminal · Download", ("graphite-meter-client", None), "loadedLatencyDownMs", "down"),
        ("GM Terminal · Upload", ("graphite-meter-client", None), "loadedLatencyUpMs", "up"),
    ]
    rows2 = []
    for lbl, cl, fld, ddir in fifo_items:
        app = measure(FIFO, cl, rate(fld))
        est = measure(FIFO, cl, fifo_latency(ddir))
        if app and est:
            rows2.append((lbl, median(app), median(est)))
    y2 = np.arange(len(rows2))
    h2 = 0.34
    m2 = max([max(r[1], r[2]) for r in rows2] + [200.0])
    ax2.barh(y2 - h2 / 2, [r[1] for r in rows2], height=h2, color="#1d4ed8", alpha=0.88, label="App reported", zorder=3)
    ax2.barh(y2 + h2 / 2, [r[2] for r in rows2], height=h2, color="#94a3b8", alpha=0.82, label="Queue-based estimate", zorder=3)
    for i, (_, av, ev) in enumerate(rows2):
        delta = av - ev
        ax2.text(av + 3.5, i - h2 / 2, f"{av:.1f} ms ({delta:+.1f})", va="center", ha="left", fontsize=7.7, color=INK, weight="bold")
        ax2.text(ev + 3.5, i + h2 / 2, f"{ev:.1f} ms", va="center", ha="left", fontsize=7.5, color=MUTED)
    ax2.set_yticks(y2)
    ax2.set_yticklabels([r[0] for r in rows2], fontsize=8.2)
    ax2.invert_yaxis()
    ax2.set_xlim(0, m2 * 1.38)
    ax2.set_xlabel("Loaded latency (ms)", fontsize=8.2)
    ax2.set_title("Loaded Latency on 300/30 Mbit/s · 200 ms FIFO", fontsize=10.3, loc="left", pad=22)
    ax2.legend(loc="upper left", bbox_to_anchor=(0.0, 1.08), ncol=2, frameon=False, fontsize=7.8, handlelength=1.1)

    _header(
        fig, 5.4,
        f"LATENCY & BUFFERBLOAT ACCURACY  ·  {report_date}  ·  {vm_count} VMs",
        "Idle latency overhead vs ICMP & FIFO bufferbloat tracking",
        "Idle reference: min of 10 ICMP pings  ·  FIFO reference: idle ICMP + shaper median queue delay (100 ms samples)",
    )
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Auto-extending Historic Trends across ALL published results/*-ci-run-*
# ---------------------------------------------------------------------------

def _load_ci_run_directory(run_dir):
    """Load one published CI run dir (either modern measurements.json.gz or legacy job-* raw dir)."""
    name = run_dir.name
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-ci-run-(\d+)$", name)
    if not m:
        return None
    date_str, run_id = m.group(1), int(m.group(2))
    prov_path = run_dir / "provenance.json"
    meas_path = run_dir / "measurements.json.gz"
    if prov_path.exists() and meas_path.exists():
        prov = json.loads(prov_path.read_text())
        meas = json.loads(gzip.decompress(meas_path.read_bytes()))
        return {
            "date": date_str,
            "run_id": run_id,
            "pins": prov["pins"],
            "runs": meas["runs"],
            "jobs": len(prov.get("jobs", [])),
        }
    jobs = sorted(run_dir.glob("job-*"))
    if jobs and (jobs[0] / "manifest.json").exists():
        m0 = json.loads((jobs[0] / "manifest.json").read_text())
        runs = []
        for j in jobs:
            manifest = json.loads((j / "manifest.json").read_text())
            hashes = [b["noise"]["hashMs"] for b in manifest.get("blocks", []) if b.get("noise", {}).get("hashMs") is not None]
            cutoff = 1.25 * median(hashes) if hashes else float("inf")
            busy = {(b["scenario"], b["rep"]) for b in manifest.get("blocks", []) if b.get("noise", {}).get("hashMs", 0) > cutoff}
            for f in (j / "runs").glob("*.json"):
                row = json.loads(f.read_text())
                if (row.get("scenario"), row.get("rep")) in busy:
                    continue
                row["job"] = j.name
                runs.append(row)
        return {
            "date": date_str,
            "run_id": run_id,
            "pins": m0["pins"],
            "runs": runs,
            "jobs": len(jobs),
        }
    return None


def _vm_summary(runs, scenario, tool, browser, extractor):
    per_job = defaultdict(list)
    for r in runs:
        if r.get("scenario") != scenario or r.get("tool") != tool or r.get("browser") != browser:
            continue
        if r.get("reported", {}).get("outcome") != "complete":
            continue
        val = extractor(r)
        if val is not None and math.isfinite(val):
            per_job[r.get("job", "0")].append(val)
    if not per_job:
        return None
    vms = [median(vs) for vs in per_job.values()]
    return spread(vms)


def render_historic_trends(results_root, out_path):
    """Scan all published CI runs in results/*-ci-run-* and plot multi-metric historic trends."""
    entries = []
    for d in sorted(Path(results_root).glob("*-ci-run-*")):
        if not d.is_dir():
            continue
        loaded = _load_ci_run_directory(d)
        if loaded and loaded["runs"]:
            entries.append(loaded)
    entries.sort(key=lambda e: (e["date"], e["run_id"]))
    if not entries:
        return []

    date_counts = defaultdict(int)
    for e in entries:
        date_counts[e["date"]] += 1
    date_seen = defaultdict(int)
    x_labels = []
    version_markers = []
    prev_gm = None
    for idx, e in enumerate(entries):
        dt = datetime.fromisoformat(e["date"])
        d_txt = dt.strftime("%d %b")
        suffix_line = ""
        if date_counts[e["date"]] > 1:
            date_seen[e["date"]] += 1
            suffix_line = f"run {date_seen[e['date']]}"
        gm_ver = e["pins"].get("tools", {}).get("graphite-meter", {}).get("version", "")
        if gm_ver and gm_ver != prev_gm:
            version_markers.append((idx, f"GM {gm_ver}"))
            sub_lbl = f"{gm_ver}" if not suffix_line else f"{gm_ver} #{date_seen[e['date']]}"
            x_labels.append(f"{d_txt}\n{sub_lbl}")
            prev_gm = gm_ver
        else:
            x_labels.append(f"{d_txt}\n{suffix_line}" if suffix_line else d_txt)

    def dl_gbps(r):
        v = r.get("reported", {}).get(DOWNLOAD)
        return v / 1000.0 if v is not None else None

    def ul_gbps(r):
        v = r.get("reported", {}).get(UPLOAD)
        return v / 1000.0 if v is not None else None

    def srv_cpu(direction):
        def fn(r):
            ph = (r.get("serverPhases") or {}).get(direction) or {}
            b = ph.get("bytes")
            return ph["cpuSeconds"] * 1e9 / b if b and ph.get("cpuSeconds") is not None else None
        return fn

    def mem_mb(r):
        v = r.get("serverMemoryPeakBytes")
        return v / 1e6 if v is not None else None

    panels = [
        (
            "Unshaped Download · Chrome",
            "Gbit/s (higher is faster)",
            UNCAPPED,
            dl_gbps,
            [
                ("Graphite Meter", "graphite-meter", "chrome", COLORS["graphite-meter"], "o", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", COLORS["librespeed-rust"], "s", "-"),
                ("LibreSpeed PHP", "librespeed", "chrome", COLORS["librespeed"], "^", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", COLORS["openspeedtest"], "D", "-"),
            ],
            False,
        ),
        (
            "Unshaped Upload · Chrome",
            "Gbit/s (higher is faster)",
            UNCAPPED,
            ul_gbps,
            [
                ("Graphite Meter", "graphite-meter", "chrome", COLORS["graphite-meter"], "o", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", COLORS["openspeedtest"], "D", "-"),
                ("LibreSpeed Go", "librespeed-go", "chrome", COLORS["librespeed-go"], "^", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", COLORS["librespeed-rust"], "s", "-"),
            ],
            False,
        ),
        (
            "Unshaped Upload · Native Clients",
            "Gbit/s (higher is faster)",
            UNCAPPED,
            ul_gbps,
            [
                ("GM Terminal", "graphite-meter-client", None, COLORS["graphite-meter-client"], "o", "-"),
                ("iperf3 (ref)", "iperf3", None, COLORS["iperf3"], "s", "--"),
                ("LibreSpeed CLI", "librespeed-cli", None, COLORS["librespeed-cli"], "^", "-"),
            ],
            False,
        ),
        (
            "10 Gbit/s Upload · Chrome",
            "Gbit/s (higher is faster)",
            FAST,
            ul_gbps,
            [
                ("Graphite Meter", "graphite-meter", "chrome", COLORS["graphite-meter"], "o", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", COLORS["openspeedtest"], "D", "-"),
                ("LibreSpeed Go", "librespeed-go", "chrome", COLORS["librespeed-go"], "^", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", COLORS["librespeed-rust"], "s", "-"),
            ],
            False,
        ),
        (
            "Server Upload CPU · 1 Gbit/s",
            "CPU s/GB (lower is better)",
            PLAIN,
            srv_cpu("up"),
            [
                ("GM Terminal", "graphite-meter-client", None, COLORS["graphite-meter-client"], "D", "--"),
                ("GM Browser (Chrome)", "graphite-meter", "chrome", COLORS["graphite-meter"], "o", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", COLORS["openspeedtest"], "v", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", COLORS["librespeed-rust"], "s", "-"),
                ("LibreSpeed CLI", "librespeed-cli", None, COLORS["librespeed-cli"], "^", "--"),
                ("iperf3 (ref)", "iperf3", None, COLORS["iperf3"], "P", ":"),
            ],
            True,
        ),
        (
            "Peak Server Memory · 1 Gbit/s",
            "MB (lower is better)",
            PLAIN,
            mem_mb,
            [
                ("GM Browser (Chrome)", "graphite-meter", "chrome", COLORS["graphite-meter"], "o", "-"),
                ("GM Terminal", "graphite-meter-client", None, "#60a5fa", "D", "--"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", COLORS["librespeed-rust"], "s", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", COLORS["openspeedtest"], "v", "-"),
                ("LibreSpeed Go", "librespeed-go", "chrome", COLORS["librespeed-go"], "^", "-"),
                ("LibreSpeed PHP", "librespeed", "chrome", COLORS["librespeed"], "X", "-"),
                ("iperf3 (ref)", "iperf3", None, COLORS["iperf3"], "P", ":"),
            ],
            False,
        ),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(14.0, 8.9))
    fig.subplots_adjust(left=0.055, right=0.985, top=0.845, bottom=0.095, wspace=0.22, hspace=0.42)

    max_ticks = 8
    if len(entries) <= max_ticks:
        tick_idxs = list(range(len(entries)))
    else:
        step = max(1, math.ceil(len(entries) / max_ticks))
        tick_idxs = sorted(set(list(range(0, len(entries), step)) + [len(entries) - 1]))

    for ax, (ptitle, ylabel, scen, fn, series_spec, phase_note) in zip(axes.flat, panels, strict=True):
        _style_axis(ax, "y")
        ax.grid(axis="x", color="#f1f5f9", linewidth=0.6, zorder=0)
        for v_idx, _ in version_markers:
            if v_idx > 0:
                ax.axvline(v_idx, color=DIVIDER, linestyle=":", linewidth=0.9, zorder=1)
        all_y = []
        first_valid = None
        end_labels = []
        last_x = len(entries) - 1
        for slbl, tool, br, col, mk, ls in series_spec:
            px, py, plo, phi = [], [], [], []
            for i, e in enumerate(entries):
                sp = _vm_summary(e["runs"], scen, tool, br, fn)
                if sp is not None:
                    px.append(i)
                    py.append(sp[0])
                    plo.append(sp[1])
                    phi.append(sp[2])
                    all_y.extend([sp[1], sp[2]])
                    if first_valid is None or i < first_valid:
                        first_valid = i
            if not px:
                continue
            ax.fill_between(px, plo, phi, color=col, alpha=0.08, zorder=2)
            ax.plot(px, py, color=col, linestyle=ls, linewidth=1.9, marker=mk, markersize=4.8,
                    markeredgecolor="#ffffff", markeredgewidth=0.6, label=slbl, zorder=4)
            txt = f"{py[-1]:.2f}" if ylabel.startswith("CPU") else f"{py[-1]:.1f}"
            end_labels.append((py[-1], txt, col))

        y_top = max(all_y) * 1.22 if all_y else 10.0
        ax.set_ylim(0, y_top)
        # De-conflict right-side end labels so closely spaced lines remain crisp and readable
        placed = _deconflict_labels(end_labels, y_top * 0.03, y_top * 0.96, y_top * 0.068)
        for orig_y, adj_y, txt, col in placed:
            if abs(adj_y - orig_y) > y_top * 0.012:
                ax.plot([last_x + 0.08, last_x + 0.24], [orig_y, adj_y], color=col, alpha=0.45, linewidth=0.75, zorder=3)
            ax.text(last_x + 0.26, adj_y, txt, va="center", ha="left", fontsize=7.2, color=col, weight="bold")

        if phase_note and first_valid and first_valid > 0:
            ax.axvspan(-0.35, first_valid - 0.35, color="#f8fafc", alpha=0.92, zorder=1)
            ax.text((first_valid - 0.7) / 2, 0.45, "Phase CPU\ntracking\nadded\nNov 2026",
                    transform=ax.get_xaxis_transform(), ha="center", va="center",
                    fontsize=7.2, color=FAINT, style="italic")

        ax.set_xticks(tick_idxs)
        ax.set_xticklabels([x_labels[i] for i in tick_idxs], fontsize=7.2)
        ax.set_xlim(-0.35, len(entries) - 1 + max(1.05, 0.17 * len(entries)))
        ax.set_ylabel(ylabel, fontsize=8.0, color=TEXT)
        ax.set_title(ptitle, fontsize=10.2, loc="left", pad=8)
        ax.legend(loc="upper left", frameon=True, facecolor="#ffffff", framealpha=0.92,
                  edgecolor=GRID, fontsize=6.8, ncol=2 if len(series_spec) > 4 else 1,
                  handlelength=1.4, borderpad=0.35, labelspacing=0.24)

    first_d = datetime.fromisoformat(entries[0]["date"]).strftime("%d.%m.%Y")
    last_d = datetime.fromisoformat(entries[-1]["date"]).strftime("%d.%m.%Y")
    _header(
        fig, 8.9,
        f"HISTORIC BENCHMARK TRENDS  ·  {len(entries)} PUBLISHED CI RUNS ({first_d} – {last_d})",
        "Performance & server resource trends across all runner campaigns",
        "Points: median across runner VMs  ·  Shaded bands: VM middle 50% (IQR)  ·  Dotted lines: Graphite Meter release changes  ·  Auto-updated each run",
    )
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)
    return entries
