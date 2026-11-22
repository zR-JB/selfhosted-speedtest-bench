"""Unified Dark/Light Bento dashboards and auto-extending historic trends for selfhosted-speedtest-bench.

Sized at 9.8 inches wide (matching GitHub's ~850 px README column) with >= 8.5 pt typography,
explicit color-swatch legends inside every card, clear metric-direction cues, and zero legacy styles.
"""

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
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, MaxNLocator

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

FIG_W = 9.8

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "card": "#151b23",
        "card_alt": "#1b2330",
        "border": "#2b3442",
        "ink": "#f0f6fc",
        "text": "#c9d1d9",
        "muted": "#8b949e",
        "faint": "#6e7681",
        "grid": "#242c38",
        "divider": "#30363d",
        "good_band": "#0f2e1e",
        "good": "#3fb950",
        "warn": "#d29922",
        "bad": "#f85149",
        "dl": "#58a6ff",
        "ul": "#f0883e",
        "shaper": "#8b949e",
        "rx": "#3fb950",
        "family": {
            "gm1": "#58a6ff",   # Graphite Meter HTTP/1.1
            "gm2": "#39c5cf",   # Graphite Meter H2/H3/WT
            "ip": "#94a3b8",    # iperf3 reference
            "ls": "#3fb950",    # LibreSpeed PHP / CLI
            "lsg": "#f0883e",   # LibreSpeed Go
            "lsr": "#bc8cff",   # LibreSpeed Rust
            "ost": "#f778ba",   # OpenSpeedTest
        },
        "proto": {
            "HTTP/1.1": "#58a6ff",
            "HTTP/2": "#3fb950",
            "HTTP/3": "#d29922",
            "WebTransport": "#bc8cff",
            "iperf3": "#94a3b8",
        },
    },
    "light": {
        "bg": "#f6f8fa",
        "card": "#ffffff",
        "card_alt": "#f3f6fa",
        "border": "#d0d7de",
        "ink": "#1f2328",
        "text": "#334155",
        "muted": "#59636e",
        "faint": "#818b98",
        "grid": "#e5e9f0",
        "divider": "#d0d7de",
        "good_band": "#dafbe1",
        "good": "#1a7f37",
        "warn": "#9a6700",
        "bad": "#cf222e",
        "dl": "#1d4ed8",
        "ul": "#ea580c",
        "shaper": "#64748b",
        "rx": "#0f766e",
        "family": {
            "gm1": "#1d4ed8",
            "gm2": "#0891b2",
            "ip": "#475569",
            "ls": "#0f766e",
            "lsg": "#c2410c",
            "lsr": "#7c3aed",
            "ost": "#be185d",
        },
        "proto": {
            "HTTP/1.1": "#1d4ed8",
            "HTTP/2": "#0f766e",
            "HTTP/3": "#b45309",
            "WebTransport": "#7c3aed",
            "iperf3": "#475569",
        },
    },
}


def configure_matplotlib():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titleweight": "bold",
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


def _family_of(tool):
    if tool in ("graphite-meter", "graphite-meter-client", NO_LOADED_LATENCY, TERMINAL_NO_LOADED_LATENCY):
        return "gm1"
    if tool.startswith("graphite-meter"):
        return "gm2"
    if tool == "iperf3":
        return "ip"
    if tool.startswith("librespeed-rust"):
        return "lsr"
    if tool.startswith("librespeed-go"):
        return "lsg"
    if tool.startswith("librespeed"):
        return "ls"
    return "ost"


def _short_label(tool, browser):
    base = {
        "graphite-meter": "Graphite Meter",
        "graphite-meter-no-loaded-latency": "GM (no lat.)",
        "graphite-meter-h2": "GM HTTP/2",
        "graphite-meter-h3": "GM HTTP/3",
        "graphite-meter-wt": "GM WebTransport",
        "graphite-meter-client": "GM Terminal",
        "graphite-meter-client-no-loaded-latency": "GM Term. (no lat.)",
        "graphite-meter-client-h2": "GM Term. H2",
        "graphite-meter-client-h3": "GM Term. H3",
        "librespeed": "LibreSpeed PHP",
        "librespeed-go": "LibreSpeed Go",
        "librespeed-go-h2": "LibreSpeed Go H2",
        "librespeed-rust": "LibreSpeed Rust",
        "librespeed-cli": "LibreSpeed CLI",
        "openspeedtest": "OpenSpeedTest",
        "openspeedtest-h2": "OpenSpeedTest H2",
        "iperf3": "iperf3 (ref)",
    }.get(tool, tool)
    if browser == "chrome":
        return f"{base} · Chr"
    if browser == "firefox":
        return f"{base} · FF"
    return base


def _new_fig(h, theme):
    t = THEMES[theme]
    return plt.figure(figsize=(FIG_W, h), facecolor=t["bg"]), t


def _draw_banner(fig, kicker, title, t):
    fh = fig.get_figheight()
    fig.text(0.020, 1.0 - 0.14 / fh, kicker, color=t["muted"], fontsize=8.5,
             family="DejaVu Sans Mono", weight="bold", va="top", ha="left", zorder=5)
    fig.text(0.020, 1.0 - 0.36 / fh, title, color=t["ink"], fontsize=15.0,
             weight="bold", va="top", ha="left", zorder=5)


def _draw_kpi_strip(fig, y_bottom_in, h_in, tiles, t):
    fh = fig.get_figheight()
    y = y_bottom_in / fh
    h = h_in / fh
    n = len(tiles)
    margin = 0.020
    gap = 0.014
    tile_w = (1.0 - 2 * margin - gap * (n - 1)) / n
    for i, (val, label, note, accent) in enumerate(tiles):
        x = margin + i * (tile_w + gap)
        fig.patches.append(mpatches.FancyBboxPatch(
            (x, y), tile_w, h,
            boxstyle="round,pad=0,rounding_size=0.012",
            transform=fig.transFigure, facecolor=t["card"], edgecolor=t["border"],
            linewidth=1.0, zorder=0.1,
        ))
        fig.patches.append(mpatches.FancyBboxPatch(
            (x + 0.004, y + h * 0.15), 0.0045, h * 0.70,
            boxstyle="round,pad=0,rounding_size=0.002",
            transform=fig.transFigure, facecolor=accent, edgecolor="none", zorder=3,
        ))
        fig.text(x + 0.018, y + h - 0.12 / fh, val, color=accent, fontsize=14.2,
                 family="DejaVu Sans Mono", weight="bold", va="top", ha="left", zorder=5)
        fig.text(x + 0.018, y + h - 0.42 / fh, label, color=t["ink"], fontsize=8.8,
                 weight="bold", va="top", ha="left", zorder=5)
        fig.text(x + 0.018, y + 0.11 / fh, note, color=t["muted"], fontsize=7.8,
                 family="DejaVu Sans Mono", va="bottom", ha="left", zorder=5)


def _draw_card(fig, x_frac, y_in, w_frac, h_in, t, *, title, direction=None, legend=None, footer=None):
    """Draw a Bento card using inch-accurate vertical spacing so every card has crisp, identical breathing room."""
    fh = fig.get_figheight()
    y = y_in / fh
    h = h_in / fh
    fig.patches.append(mpatches.FancyBboxPatch(
        (x_frac, y), w_frac, h,
        boxstyle="round,pad=0,rounding_size=0.012",
        transform=fig.transFigure, facecolor=t["card"], edgecolor=t["border"],
        linewidth=1.0, zorder=0.1,
    ))
    fig.text(x_frac + 0.016, y + h - 0.14 / fh, title, color=t["ink"], fontsize=11.0,
             weight="bold", va="top", ha="left", zorder=5)
    if direction:
        fig.text(x_frac + w_frac - 0.016, y + h - 0.16 / fh, direction, color=t["muted"], fontsize=8.2,
                 family="DejaVu Sans Mono", weight="bold", va="top", ha="right", zorder=5)
    if legend:
        # Draw explicit color-swatch legend pills cleanly on their own row right beneath the card title
        lx = x_frac + 0.016
        ly = y + h - 0.44 / fh
        sw_w = 0.011
        sw_h = 0.095 / fh
        for lbl, col in legend:
            fig.patches.append(mpatches.FancyBboxPatch(
                (lx, ly - sw_h * 0.5), sw_w, sw_h,
                boxstyle="round,pad=0,rounding_size=0.002",
                transform=fig.transFigure, facecolor=col, edgecolor="none", zorder=5,
            ))
            fig.text(lx + sw_w + 0.006, ly, lbl, color=t["text"], fontsize=8.3,
                     va="center", ha="left", zorder=5)
            # Advance proportionally to label character count
            lx += sw_w + 0.022 + len(lbl) * 0.0074
    if footer:
        fy = y + 0.28 / fh
        fig.add_artist(plt.Line2D([x_frac + 0.015, x_frac + w_frac - 0.015], [fy + 0.09 / fh, fy + 0.09 / fh],
                                  transform=fig.transFigure, color=t["border"], linewidth=0.8, zorder=4))
        fig.text(x_frac + 0.016, fy + 0.01 / fh, footer, color=t["muted"], fontsize=8.0,
                 va="top", ha="left", zorder=5)


def _add_ax(fig, x_frac, y_in, w_frac, h_in, t, grid_axis="x"):
    fh = fig.get_figheight()
    ax = fig.add_axes([x_frac, y_in / fh, w_frac, h_in / fh])
    ax.set_zorder(2)
    ax.set_facecolor(t["card"])
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=t["grid"], linewidth=0.75, linestyle=(0, (2, 2)))
    ax.tick_params(colors=t["muted"], labelsize=8.4, length=0, pad=5)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    return ax


def _deconflict_labels(items, y_min, y_max, min_gap):
    if not items:
        return []
    ordered = sorted(items, key=lambda x: x[0])
    ys = [x[0] for x in ordered]
    for i in range(1, len(ys)):
        if ys[i] - ys[i - 1] < min_gap:
            ys[i] = ys[i - 1] + min_gap
    if ys[-1] > y_max:
        overflow = ys[-1] - y_max
        ys[-1] -= overflow
        for i in range(len(ys) - 2, -1, -1):
            if ys[i + 1] - ys[i] < min_gap:
                ys[i] = ys[i + 1] - min_gap
    ys = [max(y_min, min(y_max, y)) for y in ys]
    return [(orig_y, adj_y, text, color) for (orig_y, text, color), adj_y in zip(ordered, ys, strict=True)]


# ---------------------------------------------------------------------------
# 1. Throughput Dashboard (KPI Strip + 10 Gbit/s Shaped + Unshaped Virtual Link)
# ---------------------------------------------------------------------------

def render_throughput_chart(out_stem, *, report_date, vm_count, measure, rate, paired, total_server_cpu, peak_memory):
    gm_chr_ul = measure(PLAIN, ("graphite-meter", "chrome"), lambda r: paired(r, UPLOAD))
    gm_trm_ul = measure(PLAIN, ("graphite-meter-client", None), lambda r: paired(r, UPLOAD))
    gm_ff_10g = measure(FAST, ("graphite-meter", "firefox"), rate(UPLOAD, 1000))
    gm_ch_10g = measure(FAST, ("graphite-meter", "chrome"), rate(UPLOAD, 1000))
    ost_ch_10g = measure(FAST, ("openspeedtest", "chrome"), rate(UPLOAD, 1000))
    gm_un_dl = measure(UNCAPPED, ("graphite-meter-client", None), rate(DOWNLOAD, 1000))
    gm_un_ul = measure(UNCAPPED, ("graphite-meter-client", None), rate(UPLOAD, 1000))
    ip_un_dl = measure(UNCAPPED, REFERENCE, rate(DOWNLOAD, 1000))
    ip_un_ul = measure(UNCAPPED, REFERENCE, rate(UPLOAD, 1000))
    gm_ram = measure(PLAIN, ("graphite-meter", "chrome"), peak_memory)
    ls_ram = measure(PLAIN, ("librespeed", "chrome"), peak_memory)
    lsr_ram = measure(PLAIN, ("librespeed-rust", "chrome"), peak_memory)

    spec_10g = [
        ("GM Terminal", ("graphite-meter-client", None)),
        ("iperf3 (4 TCP)", REFERENCE),
        ("LibreSpeed CLI", ("librespeed-cli", None)),
        ("GM Browser · Chr", ("graphite-meter", "chrome")),
        ("GM Browser · FF", ("graphite-meter", "firefox")),
        ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
        ("LibreSpeed Go · Chr", ("librespeed-go", "chrome")),
        ("LibreSpeed PHP · Chr", ("librespeed", "chrome")),
        ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
        ("OpenSpeedTest · FF", ("openspeedtest", "firefox")),
        ("LibreSpeed Go · FF", ("librespeed-go", "firefox")),
    ]
    spec_un = [
        ("GM Terminal", ("graphite-meter-client", None)),
        ("iperf3 (4 TCP)", REFERENCE),
        ("LibreSpeed CLI", ("librespeed-cli", None)),
        ("GM Browser · Chr", ("graphite-meter", "chrome")),
        ("LibreSpeed Go · Chr", ("librespeed-go", "chrome")),
        ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
        ("LibreSpeed PHP · Chr", ("librespeed", "chrome")),
        ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
        ("GM Browser · FF", ("graphite-meter", "firefox")),
        ("OpenSpeedTest · FF", ("openspeedtest", "firefox")),
        ("LibreSpeed Rust · FF", ("librespeed-rust", "firefox")),
    ]

    for theme in ("dark", "light"):
        fh = 11.9
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"THROUGHPUT BENCHMARK  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "High-Speed Shaped (10 Gbit/s) & Unshaped Throughput", t)

        tiles = [
            (f"{fmt_num(median(gm_trm_ul) if gm_trm_ul else None, 1, True)}% / {fmt_num(median(gm_chr_ul) if gm_chr_ul else None, 1, True)}%",
             "1G Upload vs iperf3", "GM Term / GM Chr", t["good"]),
            (f"{fmt_num(median(gm_ff_10g) if gm_ff_10g else None, 2)} / {fmt_num(median(gm_ch_10g) if gm_ch_10g else None, 2)}",
             "10G Browser UL (Gbps)", f"GM FF/Chr · OST {fmt_num(median(ost_ch_10g) if ost_ch_10g else None, 2)}", t["dl"]),
            (f"{fmt_num(median(gm_un_dl) if gm_un_dl else None, 1)} / {fmt_num(median(gm_un_ul) if gm_un_ul else None, 1)}",
             "Unshaped Native (Gbps)", f"iperf3 {fmt_num(median(ip_un_dl) if ip_un_dl else None, 1)}/{fmt_num(median(ip_un_ul) if ip_un_ul else None, 1)}", t["dl"]),
            (f"{fmt_num(median(gm_ram) if gm_ram else None, 1)} MB",
             "Lowest 1G Peak RAM", f"LS {fmt_num(median(lsr_ram) if lsr_ram else None, 0)}–{fmt_num(median(ls_ram) if ls_ram else None, 0)} MB", t["good"]),
        ]
        _draw_kpi_strip(fig, fh - 1.72, 0.94, tiles, t)

        # Card 1: 10 Gbit/s Shaped
        c1_y, c1_h = fh - 6.70, 4.80
        _draw_card(
            fig, 0.020, c1_y, 0.960, c1_h, t,
            title="1. 10 Gbit/s Shaped Link (2 ms RTT, offloads on)",
            direction="Higher is faster →",
            legend=[("Download (Gbit/s)", t["dl"]), ("Upload (Gbit/s)", t["ul"]),
                    ("Dashed = 9.56 Gbit/s TCP payload ceiling", t["faint"])],
            footer="Right column shows median Download / Upload Gbit/s and server resource cost (Total CPU · Peak RAM) for that run.",
        )
        ax1 = _add_ax(fig, 0.215, c1_y + 0.84, 0.510, c1_h - 1.56, t, "x")
        rows1 = []
        for lbl, cl in spec_10g:
            d = measure(FAST, cl, rate(DOWNLOAD, 1000))
            u = measure(FAST, cl, rate(UPLOAD, 1000))
            cpu = measure(FAST, cl, total_server_cpu)
            ram = measure(FAST, cl, peak_memory)
            if d or u:
                rows1.append((lbl, median(d) if d else 0.0, median(u) if u else 0.0,
                              median(cpu) if cpu else None, median(ram) if ram else None))
        y1 = np.arange(len(rows1))
        h = 0.36
        ax1.barh(y1 - h / 2, [r[1] for r in rows1], height=h, color=t["dl"], alpha=0.92, zorder=3)
        ax1.barh(y1 + h / 2, [r[2] for r in rows1], height=h, color=t["ul"], alpha=0.88, zorder=3)
        ax1.axvline(9.56, color=t["faint"], linestyle="--", linewidth=1.1, zorder=4)
        bl1 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax1.transData)
        ax1.text(0.848, -0.78, "DL / UL", transform=bl1, ha="right", va="bottom",
                 fontsize=7.8, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        ax1.text(0.962, -0.78, "SRV CPU · RAM", transform=bl1, ha="right", va="bottom",
                 fontsize=7.8, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        for i, (_, dv, uv, cv, rv) in enumerate(rows1):
            ax1.text(0.848, i, f"{dv:4.2f} / {uv:4.2f}", transform=bl1, ha="right", va="center",
                     fontsize=8.3, family="DejaVu Sans Mono", color=t["ink"], weight="bold" if i < 2 else "normal")
            if cv is not None and rv is not None:
                ax1.text(0.962, i, f"{cv:4.1f}s · {rv:3.0f}M", transform=bl1, ha="right", va="center",
                         fontsize=8.0, family="DejaVu Sans Mono", color=t["muted"])
        ax1.set_yticks(y1)
        ax1.set_yticklabels([r[0] for r in rows1], fontsize=8.8, color=t["text"])
        ax1.set_ylim(len(rows1) - 0.35, -0.65)
        ax1.set_xlim(0, 10.3)
        ax1.set_xlabel("Throughput (Gbit/s)", fontsize=8.5, color=t["muted"], labelpad=3)

        # Card 2: Unshaped Virtual Link
        c2_y, c2_h = 0.22, 4.80
        _draw_card(
            fig, 0.020, c2_y, 0.960, c2_h, t,
            title="2. Unshaped Virtual Link (No Rate Limit, 1 Server vCPU / 2 Client vCPUs)",
            direction="Higher is faster →",
            legend=[("Download (Gbit/s)", t["dl"]), ("Upload (Gbit/s)", t["ul"])],
            footer="Single-test host-local virtual link capacity (median across VMs). Native upload > download reflects zero-copy receive vs transmit.",
        )
        ax2 = _add_ax(fig, 0.215, c2_y + 0.84, 0.510, c2_h - 1.56, t, "x")
        rows2 = []
        for lbl, cl in spec_un:
            d = measure(UNCAPPED, cl, rate(DOWNLOAD, 1000))
            u = measure(UNCAPPED, cl, rate(UPLOAD, 1000))
            cpu = measure(UNCAPPED, cl, total_server_cpu)
            ram = measure(UNCAPPED, cl, peak_memory)
            if d or u:
                rows2.append((lbl, median(d) if d else 0.0, median(u) if u else 0.0,
                              median(cpu) if cpu else None, median(ram) if ram else None))
        y2 = np.arange(len(rows2))
        mx2 = max([max(r[1], r[2]) for r in rows2] + [55.0])
        ax2.barh(y2 - h / 2, [r[1] for r in rows2], height=h, color=t["dl"], alpha=0.92, zorder=3)
        ax2.barh(y2 + h / 2, [r[2] for r in rows2], height=h, color=t["ul"], alpha=0.88, zorder=3)
        bl2 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax2.transData)
        ax2.text(0.848, -0.78, "DL / UL", transform=bl2, ha="right", va="bottom",
                 fontsize=7.8, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        ax2.text(0.962, -0.78, "SRV CPU · RAM", transform=bl2, ha="right", va="bottom",
                 fontsize=7.8, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        for i, (_, dv, uv, cv, rv) in enumerate(rows2):
            ax2.text(0.848, i, f"{dv:4.1f} / {uv:4.1f}", transform=bl2, ha="right", va="center",
                     fontsize=8.3, family="DejaVu Sans Mono", color=t["ink"], weight="bold" if i < 2 else "normal")
            if cv is not None and rv is not None:
                ax2.text(0.962, i, f"{cv:4.1f}s · {rv:3.0f}M", transform=bl2, ha="right", va="center",
                         fontsize=8.0, family="DejaVu Sans Mono", color=t["muted"])
        ax2.set_yticks(y2)
        ax2.set_yticklabels([r[0] for r in rows2], fontsize=8.8, color=t["text"])
        ax2.set_ylim(len(rows2) - 0.35, -0.65)
        ax2.set_xlim(0, mx2 * 1.06)
        ax2.set_xlabel("Throughput (Gbit/s)", fontsize=8.5, color=t["muted"], labelpad=3)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Accuracy, Hard Links, Upload Integrity & Bufferbloat Latency
# ---------------------------------------------------------------------------

def render_accuracy_chart(out_stem, *, report_date, vm_count, measure, paired, rate, shaper_upload, server_rx, fifo_latency):
    for theme in ("dark", "light"):
        fh = 12.85
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"ACCURACY, HARD LINKS & LATENCY  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "1 Gbit/s Agreement, Lossy/High-RTT Links, Upload Integrity & FIFO Latency", t)

        # Card 1 (Full-width top): 1 Gbit/s Upload Agreement vs same-pass iperf3 (Chrome, Firefox, Native)
        c1_y, c1_h = fh - 5.40, 4.65
        _draw_card(
            fig, 0.020, c1_y, 0.960, c1_h, t,
            title="1. 1 Gbit/s Upload Agreement vs Same-Pass iperf3",
            direction="← Closer to 0% is tighter →",
            legend=[("Shaded = ±1% band", t["good"]), ("Dots = individual VMs · Bar = middle 50% (IQR)", t["dl"])],
            footer="0% matches same-pass iperf3 receiver payload rate on the same VM. Negative = app reported slower than iperf3.",
        )
        ax1 = _add_ax(fig, 0.255, c1_y + 0.84, 0.485, c1_h - 1.56, t, "x")
        agree_rows = []
        for sec, items in [
            ("Chrome", [
                ("Graphite Meter", ("graphite-meter", "chrome")),
                ("OpenSpeedTest", ("openspeedtest", "chrome")),
                ("LibreSpeed Go", ("librespeed-go", "chrome")),
                ("LibreSpeed Rust", ("librespeed-rust", "chrome")),
                ("LibreSpeed PHP", ("librespeed", "chrome")),
            ]),
            ("Firefox", [
                ("Graphite Meter", ("graphite-meter", "firefox")),
                ("OpenSpeedTest", ("openspeedtest", "firefox")),
                ("LibreSpeed Go", ("librespeed-go", "firefox")),
                ("LibreSpeed Rust", ("librespeed-rust", "firefox")),
                ("LibreSpeed PHP", ("librespeed", "firefox")),
            ]),
            ("Native Terminal", [
                ("GM Terminal", ("graphite-meter-client", None)),
                ("LibreSpeed CLI", ("librespeed-cli", None)),
            ]),
        ]:
            agree_rows.append(("sec", sec, None, None))
            for lbl, cl in items:
                agree_rows.append(("row", lbl, cl, measure(PLAIN, cl, lambda r: paired(r, UPLOAD))))

        all_a = [v for k, _, _, vs in agree_rows if k == "row" and vs for v in vs]
        ax1.axvspan(-1.0, 1.0, color=t["good_band"], alpha=0.80, zorder=0)
        ax1.axvline(0.0, color=t["good"], linewidth=1.2, zorder=2)
        bl1 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax1.transData)
        ax1.text(0.832, -0.72, "MEDIAN", transform=bl1, ha="right", va="bottom",
                 fontsize=7.8, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        ax1.text(0.962, -0.72, "IQR [p25, p75]", transform=bl1, ha="right", va="bottom",
                 fontsize=7.8, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        for i, (kind, lbl, cl, vs) in enumerate(agree_rows):
            if kind == "sec":
                ax1.text(0.036, i, lbl, transform=bl1, va="center", ha="left",
                         fontsize=9.0, weight="bold", color=t["ink"])
                continue
            col = t["family"][_family_of(cl[0])]
            ax1.scatter(0.042, i, transform=bl1, color=col, s=22, clip_on=False, zorder=5)
            ax1.text(0.056, i, lbl, transform=bl1, va="center", ha="left", fontsize=8.6, color=t["text"])
            if vs:
                med, lo, hi = spread(vs)
                offs = [i + ((k % 5) - 2) * 0.065 for k in range(len(vs))]
                ax1.scatter(vs, offs, color=col, s=14, alpha=0.45, linewidth=0, zorder=3)
                ax1.plot([lo, hi], [i, i], color=col, linewidth=3.2, solid_capstyle="round", zorder=4)
                ax1.scatter(med, i, color=col, s=42, edgecolor=t["card"], linewidth=0.9, zorder=5)
                in_band = abs(med) <= 1.0
                ax1.text(0.832, i, f"{fmt_num(med, 1, True)}%", transform=bl1, ha="right", va="center",
                         fontsize=8.5, family="DejaVu Sans Mono",
                         color=t["good"] if in_band else t["ink"], weight="bold" if in_band else "normal")
                ax1.text(0.962, i, f"[{fmt_num(lo, 1)}, {fmt_num(hi, 1)}]", transform=bl1, ha="right", va="center",
                         fontsize=8.0, family="DejaVu Sans Mono", color=t["muted"])
        ax1.set_yticks([])
        ax1.set_ylim(len(agree_rows) - 0.3, -0.75)
        ax1.set_xlim(min([-2.0, *(all_a or [-2.0])]) - 0.8, max([2.0, *(all_a or [2.0])]) + 0.8)
        ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+g}%" if v else "0%"))
        ax1.set_xlabel("Difference from same-pass iperf3 (%)", fontsize=8.4, color=t["muted"], labelpad=3)

        # Card 2 (Middle, 2 side-by-side cards): 1% Packet Loss & 160 ms High-BDP
        c2_y, c2_h = fh - 9.15, 3.55
        hard_items = [
            ("GM Browser · Chr", ("graphite-meter", "chrome")),
            ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
            ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
            ("GM Browser · FF", ("graphite-meter", "firefox")),
            ("GM Terminal", ("graphite-meter-client", None)),
            ("LibreSpeed CLI", ("librespeed-cli", None)),
            ("iperf3 (ref)", REFERENCE),
        ]
        for x_c, sc_id, ctitle, ceil_x in [
            (0.020, LOSS, "2. 100 Mbit/s · 1% Loss (40 ms RTT)", None),
            (0.510, LONG, "3. 300 Mbit/s · 160 ms RTT (High-BDP)", 286.9),
        ]:
            _draw_card(
                fig, x_c, c2_y, 0.470, c2_h, t,
                title=ctitle,
                direction="Higher →",
                legend=[("Download", t["dl"]), ("Upload", t["ul"])],
            )
            axc = _add_ax(fig, x_c + 0.165, c2_y + 0.50, 0.282, c2_h - 1.18, t, "x")
            data = []
            for lbl, cl in hard_items:
                d = measure(sc_id, cl, rate(DOWNLOAD))
                u = measure(sc_id, cl, rate(UPLOAD))
                if d or u:
                    data.append((lbl, median(d) if d else 0.0, median(u) if u else 0.0))
            yc = np.arange(len(data))
            mx = max([*(x[1] for x in data), *(x[2] for x in data), ceil_x or 1.0])
            axc.barh(yc - 0.18, [x[1] for x in data], height=0.33, color=t["dl"], alpha=0.92, zorder=3)
            axc.barh(yc + 0.18, [x[2] for x in data], height=0.33, color=t["ul"], alpha=0.88, zorder=3)
            for i, (_, dv, uv) in enumerate(data):
                axc.text(dv + mx * 0.025, i - 0.18, f"{dv:.1f}", va="center", ha="left",
                         fontsize=8.0, family="DejaVu Sans Mono", color=t["dl"])
                axc.text(uv + mx * 0.025, i + 0.18, f"{uv:.1f}", va="center", ha="left",
                         fontsize=8.0, family="DejaVu Sans Mono", color=t["ul"])
            if ceil_x:
                axc.axvline(ceil_x, color=t["faint"], linestyle="--", linewidth=1.0, zorder=2)
            axc.set_yticks(yc)
            axc.set_yticklabels([x[0] for x in data], fontsize=8.3, color=t["text"])
            axc.invert_yaxis()
            axc.set_xlim(0, mx * 1.28)
            axc.set_xlabel("Throughput (Mbit/s)", fontsize=8.2, color=t["muted"])

        # Card 4 & 5 (Bottom, 2 side-by-side cards): Upload Counter Integrity & FIFO Bufferbloat Latency
        c3_y, c3_h = 0.20, 3.30
        _draw_card(
            fig, 0.020, c3_y, 0.470, c3_h, t,
            title="4. Upload Counter Check (30M FIFO)",
            direction="≤ 28.7 Mbit/s",
            legend=[("App", t["dl"]), ("Shaper", t["shaper"]), ("Server RX", t["rx"]), ("TCP ceiling", t["bad"])],
        )
        ax4 = _add_ax(fig, 0.180, c3_y + 0.50, 0.285, c3_h - 1.18, t, "x")
        uc_items = [
            ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
            ("OpenSpeedTest · FF", ("openspeedtest", "firefox")),
            ("LibreSpeed PHP · Chr", ("librespeed", "chrome")),
            ("GM Browser · Chr", ("graphite-meter", "chrome")),
            ("GM Terminal", ("graphite-meter-client", None)),
            ("iperf3 (ref)", REFERENCE),
        ]
        uc_rows = []
        for lbl, cl in uc_items:
            app = measure(FIFO, cl, rate(UPLOAD))
            shp = measure(FIFO, cl, shaper_upload)
            rx = measure(FIFO, cl, server_rx)
            if app:
                uc_rows.append((lbl, median(app), median(shp) if shp else 0.0, median(rx) if rx else 0.0))
        y4 = np.arange(len(uc_rows))
        h4 = 0.25
        ax4.barh(y4 - h4, [r[1] for r in uc_rows], height=h4, color=t["dl"], alpha=0.92, zorder=3)
        ax4.barh(y4, [r[2] for r in uc_rows], height=h4, color=t["shaper"], alpha=0.68, zorder=3)
        ax4.barh(y4 + h4, [r[3] for r in uc_rows], height=h4, color=t["rx"], alpha=0.82, zorder=3)
        ax4.axvline(28.69, color=t["bad"], linestyle="--", linewidth=1.2, zorder=4)
        for i, (_, av, _, _) in enumerate(uc_rows):
            ax4.text(av + 0.25, i - h4, f"{av:.1f}", va="center", ha="left", fontsize=8.2,
                     family="DejaVu Sans Mono", color=t["bad"] if av > 29.2 else t["ink"], weight="bold")
        ax4.set_yticks(y4)
        ax4.set_yticklabels([r[0] for r in uc_rows], fontsize=8.3, color=t["text"])
        ax4.invert_yaxis()
        ax4.set_xlim(22, 33.2)
        ax4.set_xlabel("Upload rate (Mbit/s)", fontsize=8.2, color=t["muted"])

        _draw_card(
            fig, 0.510, c3_y, 0.470, c3_h, t,
            title="5. Loaded Latency (200 ms FIFO)",
            direction="App vs Queue",
            legend=[("App reported (+Δ ms)", t["dl"]), ("Shaper queue estimate", t["shaper"])],
        )
        ax5 = _add_ax(fig, 0.675, c3_y + 0.50, 0.285, c3_h - 1.18, t, "x")
        f_rows = []
        for lbl, cl, fld, ddir in [
            ("GM Chrome · Down", ("graphite-meter", "chrome"), "loadedLatencyDownMs", "down"),
            ("GM Chrome · Up", ("graphite-meter", "chrome"), "loadedLatencyUpMs", "up"),
            ("GM Firefox · Down", ("graphite-meter", "firefox"), "loadedLatencyDownMs", "down"),
            ("GM Firefox · Up", ("graphite-meter", "firefox"), "loadedLatencyUpMs", "up"),
            ("GM Terminal · Down", ("graphite-meter-client", None), "loadedLatencyDownMs", "down"),
            ("GM Terminal · Up", ("graphite-meter-client", None), "loadedLatencyUpMs", "up"),
        ]:
            app = measure(FIFO, cl, rate(fld))
            est = measure(FIFO, cl, fifo_latency(ddir))
            if app and est:
                f_rows.append((lbl, median(app), median(est)))
        y5 = np.arange(len(f_rows))
        h5 = 0.34
        m5 = max([max(r[1], r[2]) for r in f_rows] + [200.0])
        ax5.barh(y5 - h5 / 2, [r[1] for r in f_rows], height=h5, color=t["dl"], alpha=0.92, zorder=3)
        ax5.barh(y5 + h5 / 2, [r[2] for r in f_rows], height=h5, color=t["shaper"], alpha=0.72, zorder=3)
        for i, (_, av, ev) in enumerate(f_rows):
            ax5.text(av + 4.0, i - h5 / 2, f"{av:.0f} ({av - ev:+.0f})", va="center", ha="left",
                     fontsize=8.1, family="DejaVu Sans Mono", color=t["ink"], weight="bold")
            ax5.text(ev + 4.0, i + h5 / 2, f"{ev:.0f} ms", va="center", ha="left",
                     fontsize=7.9, family="DejaVu Sans Mono", color=t["muted"])
        ax5.set_yticks(y5)
        ax5.set_yticklabels([r[0] for r in f_rows], fontsize=8.3, color=t["text"])
        ax5.invert_yaxis()
        ax5.set_xlim(0, m5 * 1.46)
        ax5.set_xlabel("Loaded latency (ms)", fontsize=8.2, color=t["muted"])

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Resource Usage Dashboard (1G Phase CPU, 10G/Unshaped CPU, Peak RAM incl. nginx, Client CPU)
# ---------------------------------------------------------------------------

def render_resources_chart(out_stem, *, report_date, vm_count, groups, measure, phase_cpu, peak_memory, client_cpu):
    def total_cpu_per_gb(row):
        cpu = row.get("serverCpuSeconds")
        link = sum(row.get("linkBytes", {}).values())
        return cpu * 1e9 / link if cpu is not None and link else None

    main_items = [
        ("GM Browser · Chr", ("graphite-meter", "chrome")),
        ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
        ("LibreSpeed Go · Chr", ("librespeed-go", "chrome")),
        ("LibreSpeed PHP · Chr", ("librespeed", "chrome")),
        ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
        ("GM Terminal", ("graphite-meter-client", None)),
        ("LibreSpeed CLI", ("librespeed-cli", None)),
        ("iperf3 (ref)", REFERENCE),
    ]

    # Collect ranked 10G & Unshaped Server CPU/GB across all HTTP/1.1 + native + iperf3 + key H2/H3
    def ranked_cpu(scen):
        rows = []
        seen = set()
        for (sc, cl) in groups:
            if sc != scen or cl in seen:
                continue
            seen.add(cl)
            tool, br = cl
            if tool in (NO_LOADED_LATENCY, TERMINAL_NO_LOADED_LATENCY):
                continue
            vs = measure(scen, cl, total_cpu_per_gb)
            if vs:
                rows.append((_short_label(tool, br), cl, median(vs)))
        rows.sort(key=lambda x: x[2])
        return rows

    r_10g = ranked_cpu(FAST)
    r_un = ranked_cpu(UNCAPPED)

    ram_rows = []
    for lbl, sc, cl in [
        ("GM Chrome H3 (10G)", FAST, ("graphite-meter-h3", "chrome")),
        ("GM Chrome H2 (10G)", FAST, ("graphite-meter-h2", "chrome")),
        ("GM Browser · Chr (1G)", PLAIN, ("graphite-meter", "chrome")),
        ("GM Terminal (1G)", PLAIN, ("graphite-meter-client", None)),
        ("iperf3 (1G)", PLAIN, REFERENCE),
        ("LibreSpeed Rust (1G)", PLAIN, ("librespeed-rust", "chrome")),
        ("GM Browser · nginx", PROXY, ("graphite-meter", "chrome")),
        ("OpenSpeedTest (1G)", PLAIN, ("openspeedtest", "chrome")),
        ("LibreSpeed Go (1G)", PLAIN, ("librespeed-go", "chrome")),
        ("LibreSpeed CLI (1G)", PLAIN, ("librespeed-cli", None)),
        ("LibreSpeed PHP (1G)", PLAIN, ("librespeed", "chrome")),
        ("OpenSpeedTest H2 (10G)", FAST, ("openspeedtest-h2", "chrome")),
        ("OpenSpeedTest · nginx", PROXY, ("openspeedtest", "chrome")),
        ("LibreSpeed PHP · nginx", PROXY, ("librespeed", "chrome")),
    ]:
        vs = measure(sc, cl, peak_memory)
        if vs:
            ram_rows.append((lbl, cl, median(vs)))
    ram_rows.sort(key=lambda x: x[2])

    c_rows = []
    for cl in [
        ("graphite-meter", "chrome"), ("librespeed-go", "chrome"), ("openspeedtest", "chrome"),
        ("librespeed-rust", "chrome"), ("librespeed", "chrome"), ("graphite-meter", "firefox"),
        ("openspeedtest", "firefox"), ("librespeed-go", "firefox"), ("librespeed-rust", "firefox"),
        ("librespeed", "firefox"), ("graphite-meter-client", None), ("librespeed-cli", None), REFERENCE,
    ]:
        vs = measure(UNCAPPED, cl, client_cpu)
        if vs:
            c_rows.append((_short_label(cl[0], cl[1]), cl, spread(vs)))
    c_rows.sort(key=lambda x: x[2][0])

    def best_phase(scen, direc):
        cands = []
        for _, cl in main_items[:-1]:
            vs = measure(scen, cl, phase_cpu(direc))
            if vs:
                cands.append((_short_label(cl[0], cl[1]), median(vs)))
        return min(cands, key=lambda x: x[1]) if cands else ("—", None)

    b_dn = best_phase(PLAIN, "down")
    b_up = best_phase(PLAIN, "up")
    b_un = best_phase(UNCAPPED, "up")
    b_ram = ram_rows[0] if ram_rows else ("—", None, None)

    for theme in ("dark", "light"):
        fh = 14.1
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"RESOURCE EFFICIENCY  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "Server CPU per GB (Offloads Off vs On), Peak RAM & Client CPU", t)

        tiles = [
            (f"{b_dn[1]:.3f} s/GB" if b_dn[1] else "—", "Lowest 1G Down CPU", b_dn[0], t["dl"]),
            (f"{b_up[1]:.3f} s/GB" if b_up[1] else "—", "Lowest 1G Up CPU", b_up[0], t["good"]),
            (f"{b_un[1]:.3f} s/GB" if b_un[1] else "—", "Lowest Unshaped Up", b_un[0], t["good"]),
            (f"{b_ram[2]:.1f} MB" if b_ram[2] else "—", "Lowest Peak RAM", b_ram[0], t["dl"]),
        ]
        _draw_kpi_strip(fig, fh - 1.72, 0.94, tiles, t)

        fam_legend = [
            ("GM H1", t["family"]["gm1"]), ("GM H2/H3/WT", t["family"]["gm2"]),
            ("iperf3", t["family"]["ip"]), ("LibreSpeed PHP/CLI", t["family"]["ls"]),
            ("LS Go", t["family"]["lsg"]), ("LS Rust", t["family"]["lsr"]),
            ("OpenSpeedTest", t["family"]["ost"]),
        ]

        # Card 1: 1 Gbit/s Server CPU by Phase (Download vs Upload) + 10G & Unshaped Upload CPU
        c1_y, c1_h = fh - 5.95, 4.05
        _draw_card(
            fig, 0.020, c1_y, 0.470, c1_h, t,
            title="1. 1 Gbit/s Server CPU (offloads off)",
            direction="← Lower",
            legend=[("Download s/GB", t["dl"]), ("Upload s/GB", t["ul"])],
        )
        ax1 = _add_ax(fig, 0.180, c1_y + 0.50, 0.282, c1_h - 1.18, t, "x")
        r1 = []
        for lbl, cl in main_items:
            dc = measure(PLAIN, cl, phase_cpu("down"))
            uc = measure(PLAIN, cl, phase_cpu("up"))
            if dc or uc:
                r1.append((lbl, median(dc) if dc else 0.0, median(uc) if uc else 0.0))
        y1 = np.arange(len(r1))
        m1 = max([max(x[1], x[2]) for x in r1] + [1.0])
        ax1.barh(y1 - 0.18, [x[1] for x in r1], height=0.33, color=t["dl"], alpha=0.92, zorder=3)
        ax1.barh(y1 + 0.18, [x[2] for x in r1], height=0.33, color=t["ul"], alpha=0.88, zorder=3)
        for i, (_, dv, uv) in enumerate(r1):
            ax1.text(dv + m1 * 0.025, i - 0.18, f"{dv:.3f}", va="center", ha="left",
                     fontsize=7.9, family="DejaVu Sans Mono", color=t["dl"])
            ax1.text(uv + m1 * 0.025, i + 0.18, f"{uv:.3f}", va="center", ha="left",
                     fontsize=8.0, family="DejaVu Sans Mono", color=t["ul"], weight="bold")
        ax1.axhline(4.5, color=t["divider"], linestyle=":", linewidth=1.0)
        ax1.set_yticks(y1)
        ax1.set_yticklabels([x[0] for x in r1], fontsize=8.3, color=t["text"])
        ax1.invert_yaxis()
        ax1.set_xlim(0, m1 * 1.28)
        ax1.set_xlabel("Server CPU (s/GB)", fontsize=8.2, color=t["muted"])

        _draw_card(
            fig, 0.510, c1_y, 0.470, c1_h, t,
            title="2. Unshaped Server CPU/GB (offloads on)",
            direction="← Lower",
            legend=[("GM H1", t["family"]["gm1"]), ("GM H2/H3", t["family"]["gm2"]),
                    ("iperf3", t["family"]["ip"]), ("LS", t["family"]["ls"]), ("OST", t["family"]["ost"])],
        )
        ax2 = _add_ax(fig, 0.678, c1_y + 0.50, 0.278, c1_h - 1.18, t, "x")
        y2 = np.arange(len(r_un))
        m2 = max([r[2] for r in r_un] + [0.5])
        for i, (lbl, cl, val) in enumerate(r_un):
            col = t["family"][_family_of(cl[0])]
            ax2.barh(i, val, height=0.66, color=col, alpha=0.88 if i == 0 else 0.78, zorder=3)
            ax2.text(val + m2 * 0.025, i, f"{val:.3f}s", va="center", ha="left",
                     fontsize=7.8, family="DejaVu Sans Mono",
                     color=t["ink"] if i == 0 else t["muted"], weight="bold" if i == 0 else "normal")
        ax2.set_yticks(y2)
        ax2.set_yticklabels([r[0].replace("LibreSpeed ", "LS ").replace("Graphite Meter", "GM") for r in r_un],
                            fontsize=7.9, color=t["text"])
        ax2.invert_yaxis()
        ax2.set_xlim(0, m2 * 1.28)
        ax2.set_xlabel("Total Server CPU / GB (s/GB)", fontsize=8.2, color=t["muted"])

        # Card 3: Peak Server Container RAM across Direct, HTTP/2 & Behind nginx
        c2_y, c2_h = fh - 10.95, 4.80
        _draw_card(
            fig, 0.020, c2_y, 0.960, c2_h, t,
            title="3. Peak Server Memory Across Direct (1G), HTTP/2 (10G) & nginx Reverse Proxy",
            direction="← Lower is better",
            legend=fam_legend,
            footer="cgroup v2 memory.peak per run (MB). Behind-nginx rows count both the server container and its nginx sidecar.",
        )
        ax3 = _add_ax(fig, 0.235, c2_y + 0.84, 0.715, c2_h - 1.52, t, "x")
        y3 = np.arange(len(ram_rows))
        m3 = max([r[2] for r in ram_rows] + [50.0])
        for i, (lbl, cl, val) in enumerate(ram_rows):
            col = t["family"][_family_of(cl[0])]
            ax3.barh(i, val, height=0.66, color=col, alpha=0.90 if i < 3 else 0.80, zorder=3)
            ax3.text(val + m3 * 0.015, i, f"{val:.1f} MB", va="center", ha="left",
                     fontsize=8.3, family="DejaVu Sans Mono",
                     color=t["ink"] if i < 3 else t["muted"], weight="bold" if i < 3 else "normal")
        ax3.set_yticks(y3)
        ax3.set_yticklabels([r[0] for r in ram_rows], fontsize=8.5, color=t["text"])
        ax3.invert_yaxis()
        ax3.set_xlim(0, m3 * 1.15)
        ax3.set_xlabel("Peak server container memory (MB)", fontsize=8.4, color=t["muted"], labelpad=3)

        # Card 4: Client-Side CPU Efficiency on Unshaped
        c3_y, c3_h = 0.20, 2.75
        _draw_card(
            fig, 0.020, c3_y, 0.960, c3_h, t,
            title="4. Client-Side CPU Efficiency on Unshaped (Bar = Median, Whisker = VM IQR)",
            direction="← Lower is better",
            legend=[("Browser process tree + native client cgroup where recorded", t["muted"])],
        )
        ax4 = _add_ax(fig, 0.085, c3_y + 0.50, 0.875, c3_h - 1.18, t, "y")
        xs4 = np.arange(len(c_rows))
        m4 = max([r[2][2] for r in c_rows] + [1.0])
        for i, (lbl, cl, (med, lo, hi)) in enumerate(c_rows):
            col = t["family"][_family_of(cl[0])]
            ax4.bar(i, med, width=0.58, color=col, alpha=0.84, zorder=3)
            ax4.plot([i, i], [lo, hi], color=t["ink"], linewidth=1.7, zorder=4)
            ax4.text(i, max(hi, med) + m4 * 0.04, f"{med:.2f}", ha="center", va="bottom",
                     fontsize=8.2, family="DejaVu Sans Mono", color=t["ink"], weight="bold")
        ax4.set_xticks(xs4)
        ax4.set_xticklabels(
            [r[0].replace("Graphite Meter", "GM").replace("LibreSpeed ", "LS ").replace("OpenSpeedTest", "OST").replace(" · ", "\n")
             for r in c_rows],
            fontsize=7.6 if len(c_rows) > 9 else 8.2,
            color=t["text"],
        )
        ax4.set_ylim(0, m4 * 1.28)
        ax4.set_ylabel("s/GB", fontsize=8.4, color=t["muted"])

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Protocol & Transport Scaling (HTTP/1.1 vs HTTP/2 vs HTTP/3 vs WebTransport)
# ---------------------------------------------------------------------------

def render_transports_chart(out_stem, *, report_date, vm_count, measure, rate):
    def total_cpu_per_gb(row):
        cpu = row.get("serverCpuSeconds")
        link = sum(row.get("linkBytes", {}).values())
        return cpu * 1e9 / link if cpu is not None and link else None

    for theme in ("dark", "light"):
        fh = 6.5
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"PROTOCOL & TRANSPORT SCALING  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "HTTP/1.1 vs HTTP/2 vs HTTP/3 vs WebTransport", t)

        proto_leg = [
            ("HTTP/1.1", t["proto"]["HTTP/1.1"]), ("HTTP/2", t["proto"]["HTTP/2"]),
            ("HTTP/3", t["proto"]["HTTP/3"]), ("WebTransport", t["proto"]["WebTransport"]),
            ("iperf3 TCP", t["proto"]["iperf3"]),
        ]

        # Left card: Chrome 10 Gbit/s
        cy, ch = 0.22, fh - 1.00
        _draw_card(
            fig, 0.020, cy, 0.470, ch, t,
            title="1. Chrome · 10 Gbit/s Shaped",
            direction="Higher →",
            legend=proto_leg[:4],
            footer="Solid = Download · Light = Upload · Dashed = 9.56 Gbit/s TCP ceiling.",
        )
        ax1 = _add_ax(fig, 0.195, cy + 0.84, 0.268, ch - 1.52, t, "x")
        c_spec = [
            ("GM · HTTP/1.1", ("graphite-meter", "chrome"), "HTTP/1.1"),
            ("GM · HTTP/2", ("graphite-meter-h2", "chrome"), "HTTP/2"),
            ("GM · HTTP/3", ("graphite-meter-h3", "chrome"), "HTTP/3"),
            ("GM · WebTransport", ("graphite-meter-wt", "chrome"), "WebTransport"),
            ("LS Go · HTTP/1.1", ("librespeed-go", "chrome"), "HTTP/1.1"),
            ("LS Go · HTTP/2", ("librespeed-go-h2", "chrome"), "HTTP/2"),
            ("OST · HTTP/1.1", ("openspeedtest", "chrome"), "HTTP/1.1"),
            ("OST · HTTP/2", ("openspeedtest-h2", "chrome"), "HTTP/2"),
            ("iperf3 (4 TCP)", REFERENCE, "iperf3"),
        ]
        r1 = []
        for lbl, cl, proto in c_spec:
            d = measure(FAST, cl, rate(DOWNLOAD, 1000))
            u = measure(FAST, cl, rate(UPLOAD, 1000))
            cp = measure(FAST, cl, total_cpu_per_gb)
            if d or u:
                r1.append((lbl, proto, median(d) if d else 0.0, median(u) if u else 0.0, median(cp) if cp else None))
        y1 = np.arange(len(r1))
        h = 0.35
        for i, (_, proto, dv, uv, cp) in enumerate(r1):
            c = t["proto"][proto]
            ax1.barh(i - h / 2, dv, height=h, color=c, alpha=0.92, zorder=3)
            ax1.barh(i + h / 2, uv, height=h, color=c, alpha=0.40, edgecolor=c, linewidth=0.9, zorder=3)
            ax1.text(dv + 0.16, i - h / 2, f"{dv:.2f}", va="center", ha="left",
                     fontsize=7.9, family="DejaVu Sans Mono", color=t["ink"])
            ax1.text(uv + 0.16, i + h / 2, f"{uv:.2f}", va="center", ha="left",
                     fontsize=7.7, family="DejaVu Sans Mono", color=t["muted"])
        ax1.axvline(9.56, color=t["faint"], linestyle="--", linewidth=0.95, zorder=2)
        ax1.set_yticks(y1)
        ax1.set_yticklabels([r[0] for r in r1], fontsize=8.4, color=t["text"])
        ax1.invert_yaxis()
        ax1.set_xlim(0, 11.4)
        ax1.set_xlabel("Throughput (Gbit/s)", fontsize=8.3, color=t["muted"], labelpad=3)

        # Right card: Native Terminal 10G & Unshaped
        _draw_card(
            fig, 0.510, cy, 0.470, ch, t,
            title="2. Native Terminal · 10G & Unshaped",
            direction="Higher →",
            legend=[("Solid = Download", t["dl"]), ("Light = Upload", t["muted"])],
            footer="Terminal TLS variants force ALPN so protocols never silently fall back.",
        )
        ax2 = _add_ax(fig, 0.685, cy + 0.84, 0.268, ch - 1.52, t, "x")
        n_spec = [
            ("GM Term · H1 (10G)", FAST, ("graphite-meter-client", None), "HTTP/1.1"),
            ("GM Term · H2 (10G)", FAST, ("graphite-meter-client-h2", None), "HTTP/2"),
            ("GM Term · H3 (10G)", FAST, ("graphite-meter-client-h3", None), "HTTP/3"),
            ("LS CLI · H1 (10G)", FAST, ("librespeed-cli", None), "HTTP/1.1"),
            ("iperf3 (10G)", FAST, REFERENCE, "iperf3"),
            ("GM Term · H1 (Unsh.)", UNCAPPED, ("graphite-meter-client", None), "HTTP/1.1"),
            ("GM Term · H2 (Unsh.)", UNCAPPED, ("graphite-meter-client-h2", None), "HTTP/2"),
            ("GM Term · H3 (Unsh.)", UNCAPPED, ("graphite-meter-client-h3", None), "HTTP/3"),
            ("iperf3 (Unshaped)", UNCAPPED, REFERENCE, "iperf3"),
        ]
        r2 = []
        for lbl, sc, cl, proto in n_spec:
            d = measure(sc, cl, rate(DOWNLOAD, 1000))
            u = measure(sc, cl, rate(UPLOAD, 1000))
            if d or u:
                r2.append((lbl, proto, median(d) if d else 0.0, median(u) if u else 0.0))
        y2 = np.arange(len(r2))
        m2 = max([max(r[2], r[3]) for r in r2] + [10.0])
        for i, (_, proto, dv, uv) in enumerate(r2):
            c = t["proto"][proto]
            ax2.barh(i - h / 2, dv, height=h, color=c, alpha=0.92, zorder=3)
            ax2.barh(i + h / 2, uv, height=h, color=c, alpha=0.40, edgecolor=c, linewidth=0.9, zorder=3)
            ax2.text(dv + m2 * 0.02, i - h / 2, f"{dv:.1f}", va="center", ha="left",
                     fontsize=7.9, family="DejaVu Sans Mono", color=t["ink"])
            ax2.text(uv + m2 * 0.02, i + h / 2, f"{uv:.1f}", va="center", ha="left",
                     fontsize=7.7, family="DejaVu Sans Mono", color=t["muted"])
        if len(r2) > 5:
            ax2.axhline(4.5, color=t["divider"], linestyle=":", linewidth=1.0)
        ax2.set_yticks(y2)
        ax2.set_yticklabels([r[0] for r in r2], fontsize=8.3, color=t["text"])
        ax2.invert_yaxis()
        ax2.set_xlim(0, m2 * 1.22)
        ax2.set_xlabel("Throughput (Gbit/s)", fontsize=8.3, color=t["muted"], labelpad=3)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Consistency & Runner Hardware Heterogeneity (Cleanly Scaled!)
# ---------------------------------------------------------------------------

def render_consistency_chart(out_stem, *, report_date, vm_count, measure, by_vm, rate, jobs):
    tools_cons = [
        ("GM Term.", ("graphite-meter-client", None), "gm1"),
        ("GM Chr.", ("graphite-meter", "chrome"), "gm2"),
        ("LS CLI", ("librespeed-cli", None), "ls"),
        ("LS Rust", ("librespeed-rust", "chrome"), "lsr"),
        ("OST Chr.", ("openspeedtest", "chrome"), "ost"),
    ]

    def asym_pct(scen, cl):
        d = measure(scen, cl, rate(DOWNLOAD))
        u = measure(scen, cl, rate(UPLOAD))
        if not d or not u:
            return 0.0
        dm, um = median(d), median(u)
        return 100.0 * abs(dm - um) / max(dm, um, 1e-6)

    def iqr_pct(scen, cl):
        vs = measure(scen, cl, rate(UPLOAD))
        if len(vs) < 2:
            return 0.0
        med, lo, hi = spread(vs)
        return 100.0 * (hi - lo) / med if med > 0 else 0.0

    # Keep only comparable shaped consistency metrics on a clean 0..70% scale (no 160% unshaped outlier crushing 1G!)
    groups_cons = [
        ("1G UL\nIQR %", [iqr_pct(PLAIN, cl) for _, cl, _ in tools_cons]),
        ("10G UL\nIQR %", [iqr_pct(FAST, cl) for _, cl, _ in tools_cons]),
        ("1% Loss\n|DL−UL| %", [asym_pct(LOSS, cl) for _, cl, _ in tools_cons]),
        ("160ms RTT\n|DL−UL| %", [asym_pct(LONG, cl) for _, cl, _ in tools_cons]),
    ]

    by_hw = defaultdict(list)
    for j in jobs:
        host = j["host"]
        cpu = re.sub(r"\(R\)|\(TM\)|Processor|CPU|\b\d+-Core\b", "", host.get("cpu", "Unknown")).strip()
        cpu = re.sub(r"\s+", " ", cpu)
        kern = host.get("kernel", "")
        cloud = "AWS" if kern.endswith("-aws") else "Azure" if kern.endswith("-azure") else "Other"
        by_hw[(cloud, cpu)].append(j["job"])
    hw_groups = sorted(by_hw.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    for theme in ("dark", "light"):
        fh = 6.2
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"CONSISTENCY & RUNNER FLEET  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "Shaped Link Consistency & Runner CPU Hardware Breakdown", t)

        cy, ch = 0.22, fh - 1.00
        _draw_card(
            fig, 0.020, cy, 0.470, ch, t,
            title="1. Shaped Spread & Symmetry",
            direction="← Lower is steadier",
            legend=[(lbl, t["family"][fam]) for lbl, _, fam in tools_cons],
            footer="IQR % = VM middle-50% / median; |DL−UL| % = symmetric-link skew.",
        )
        ax1 = _add_ax(fig, 0.072, cy + 0.82, 0.402, ch - 1.54, t, "y")
        n_g, n_b = len(groups_cons), len(tools_cons)
        bw = 0.145
        mx1 = max([v for _, vs in groups_cons for v in vs] + [25.0])
        for bi, (_, _, fam) in enumerate(tools_cons):
            col = t["family"][fam]
            xs = np.arange(n_g) + (bi - (n_b - 1) / 2) * (bw + 0.015)
            vals = [g[1][bi] for g in groups_cons]
            ax1.bar(xs, vals, width=bw, color=col, alpha=0.90, zorder=3)
            for x, v in zip(xs, vals, strict=True):
                if v >= 4 or bi < 2:
                    ax1.text(x, v + mx1 * 0.02, f"{v:.1f}" if v < 10 else f"{v:.0f}",
                             ha="center", va="bottom", fontsize=7.5, family="DejaVu Sans Mono", color=t["muted"])
        ax1.set_xticks(np.arange(n_g))
        ax1.set_xticklabels([g[0] for g in groups_cons], fontsize=8.3, color=t["text"])
        ax1.set_ylim(0, mx1 * 1.22)
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))

        _draw_card(
            fig, 0.510, cy, 0.470, ch, t,
            title="2. Unshaped Upload by Runner CPU",
            direction="Higher →",
            legend=[("GM Terminal", t["family"]["gm1"]), ("iperf3", t["family"]["ip"]), ("LS CLI", t["family"]["ls"])],
            footer="GitHub ubuntu-24.04 mixes Azure EPYC & AWS Xeon VMs.",
        )
        ax2 = _add_ax(fig, 0.675, cy + 0.84, 0.285, ch - 1.54, t, "x")
        hw_clients = [
            ("GM Terminal", ("graphite-meter-client", None), t["family"]["gm1"]),
            ("iperf3", REFERENCE, t["family"]["ip"]),
            ("LS CLI", ("librespeed-cli", None), t["family"]["ls"]),
        ]
        vm_maps = {lbl: by_vm(UNCAPPED, cl, rate(UPLOAD, 1000)) for lbl, cl, _ in hw_clients}
        y2 = np.arange(len(hw_groups))
        h2 = 0.25
        all_hw = []
        for idx, (lbl, _, col) in enumerate(hw_clients):
            off = (idx - 1) * h2
            vals = []
            for _, jnames in hw_groups:
                vs = [vm_maps[lbl][jn] for jn in jnames if jn in vm_maps[lbl]]
                v = median(vs) if vs else 0.0
                vals.append(v)
                all_hw.append(v)
            ax2.barh(y2 + off, vals, height=h2, color=col, alpha=0.90, zorder=3)
            for i, v in enumerate(vals):
                if v > 0:
                    ax2.text(v + 1.4, i + off, f"{v:.1f}", va="center", ha="left",
                             fontsize=8.2, family="DejaVu Sans Mono", color=col, weight="bold")
        ax2.set_yticks(y2)
        ax2.set_yticklabels([f"{cloud} · {cpu}\n(n={len(jnames)} VM{'s' if len(jnames) != 1 else ''})"
                             for (cloud, cpu), jnames in hw_groups], fontsize=8.2, color=t["text"])
        ax2.invert_yaxis()
        ax2.set_xlim(0, max(all_hw or [60.0]) * 1.22)
        ax2.set_xlabel("Unshaped upload median (Gbit/s)", fontsize=8.3, color=t["muted"], labelpad=3)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Auto-Extending 6-Panel Historic Trends (3x2 Large-Text Bento, Dark + Light)
# ---------------------------------------------------------------------------

def _load_ci_run_directory(run_dir):
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
        return {"date": date_str, "run_id": run_id, "pins": prov["pins"],
                "runs": meas["runs"], "jobs": len(prov.get("jobs", []))}
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
        return {"date": date_str, "run_id": run_id, "pins": m0["pins"], "runs": runs, "jobs": len(jobs)}
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
    return spread([median(vs) for vs in per_job.values()]) if per_job else None


def render_historic_trends(results_root, out_stem):
    """Scan all published CI runs in results/*-ci-run-* and render large-text 6-panel Dark + Light trends."""
    entries = []
    for d in sorted(Path(results_root).glob("*-ci-run-*")):
        if d.is_dir():
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
    x_labels, version_markers = [], []
    prev_gm = None
    for idx, e in enumerate(entries):
        dt = datetime.fromisoformat(e["date"])
        d_txt = dt.strftime("%d %b")
        suffix_line = ""
        if date_counts[e["date"]] > 1:
            date_seen[e["date"]] += 1
            suffix_line = f"#{date_seen[e['date']]}"
        gm_ver = e["pins"].get("tools", {}).get("graphite-meter", {}).get("version", "")
        if gm_ver and gm_ver != prev_gm:
            version_markers.append((idx, f"GM {gm_ver}"))
            sub_lbl = gm_ver if not suffix_line else f"{gm_ver} {suffix_line}"
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

    ref_1g_by_entry = []
    for e in entries:
        ref_map = {}
        for r in e["runs"]:
            if r.get("scenario") == PLAIN and r.get("tool") == "iperf3" and r.get("reported", {}).get("outcome") == "complete":
                ref_map[(r.get("job", "0"), r.get("rep"))] = r["reported"].get(UPLOAD)
        ref_1g_by_entry.append(ref_map)

    def upload_agree_summary(entry_idx, tool, browser):
        e = entries[entry_idx]
        ref_map = ref_1g_by_entry[entry_idx]
        per_job = defaultdict(list)
        for r in e["runs"]:
            if r.get("scenario") != PLAIN or r.get("tool") != tool or r.get("browser") != browser:
                continue
            if r.get("reported", {}).get("outcome") != "complete":
                continue
            val = r["reported"].get(UPLOAD)
            base = ref_map.get((r.get("job", "0"), r.get("rep")))
            if val is not None and base and base > 0:
                per_job[r.get("job", "0")].append(100.0 * (val / base - 1.0))
        return spread([median(vs) for vs in per_job.values()]) if per_job else None

    max_ticks = 8
    tick_idxs = (
        list(range(len(entries))) if len(entries) <= max_ticks
        else sorted(set(list(range(0, len(entries), max(1, math.ceil(len(entries) / max_ticks)))) + [len(entries) - 1]))
    )
    first_d = datetime.fromisoformat(entries[0]["date"]).strftime("%d.%m.%Y")
    last_d = datetime.fromisoformat(entries[-1]["date"]).strftime("%d.%m.%Y")

    for theme in ("dark", "light"):
        fh = 12.2
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"HISTORIC TRENDS  ·  {len(entries)} PUBLISHED CI RUNS ({first_d} – {last_d})  ·  AUTO-UPDATED",
                     "Performance, Accuracy & Server Resources Across All Campaigns", t)

        panels = [
            ("1. Unshaped Download · Chrome", "Gbit/s · higher →", UNCAPPED, dl_gbps, [
                ("Graphite Meter", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("LS Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("LS PHP", "librespeed", "chrome", t["family"]["ls"], "^", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
            ], False, False),
            ("2. Unshaped Upload · Native", "Gbit/s · higher →", UNCAPPED, ul_gbps, [
                ("GM Terminal", "graphite-meter-client", None, t["family"]["gm1"], "o", "-"),
                ("iperf3 (ref)", "iperf3", None, t["family"]["ip"], "s", "--"),
                ("LS CLI", "librespeed-cli", None, t["family"]["ls"], "^", "-"),
            ], False, False),
            ("3. 10 Gbit/s Upload · Chrome", "Gbit/s · higher →", FAST, ul_gbps, [
                ("Graphite Meter", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
                ("LS Go", "librespeed-go", "chrome", t["family"]["lsg"], "^", "-"),
                ("LS Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
            ], False, False),
            ("4. 1G Upload vs iperf3", "% diff · closer to 0%", PLAIN, None, [
                ("GM Chr", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("GM FF", "graphite-meter", "firefox", t["family"]["gm2"], "v", "--"),
                ("OST Chr", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
                ("LS PHP FF", "librespeed", "firefox", t["family"]["ls"], "^", "--"),
                ("GM Term", "graphite-meter-client", None, t["ink"], "s", ":"),
            ], False, True),
            ("5. Server Upload CPU · 1 Gbit/s", "s/GB · ← lower", PLAIN, srv_cpu("up"), [
                ("GM Term", "graphite-meter-client", None, t["family"]["gm1"], "D", "--"),
                ("GM Chr", "graphite-meter", "chrome", t["family"]["gm2"], "o", "-"),
                ("OST Chr", "openspeedtest", "chrome", t["family"]["ost"], "v", "-"),
                ("LS Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("LS CLI", "librespeed-cli", None, t["family"]["ls"], "^", "--"),
                ("iperf3", "iperf3", None, t["family"]["ip"], "P", ":"),
            ], True, False),
            ("6. Peak Server RAM · 1 Gbit/s", "MB · ← lower", PLAIN, mem_mb, [
                ("GM Chr", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("GM Term", "graphite-meter-client", None, t["family"]["gm2"], "D", "--"),
                ("LS Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("OST Chr", "openspeedtest", "chrome", t["family"]["ost"], "v", "-"),
                ("LS Go", "librespeed-go", "chrome", t["family"]["lsg"], "^", "-"),
                ("LS PHP", "librespeed", "chrome", t["family"]["ls"], "X", "-"),
                ("iperf3", "iperf3", None, t["family"]["ip"], "P", ":"),
            ], False, False),
        ]

        # 3 rows x 2 columns — big, crisp, effortlessly readable!
        col_xs = [0.020, 0.510]
        card_w = 0.470
        row_h = 3.60
        row_gap = 0.22
        top_in = fh - 0.80

        for idx, (ptitle, dir_txt, scen, fn, series_spec, phase_note, is_signed) in enumerate(panels):
            r_idx, c_idx = divmod(idx, 2)
            cx = col_xs[c_idx]
            cy = top_in - (r_idx + 1) * row_h - r_idx * row_gap
            _draw_card(fig, cx, cy, card_w, row_h, t, title=ptitle, direction=dir_txt)
            ax = _add_ax(fig, cx + 0.056, cy + 0.52, card_w - 0.072, row_h - 0.96, t, "y")
            ax.grid(axis="x", color=t["grid"], linewidth=0.5, alpha=0.5, zorder=0)
            if is_signed:
                ax.axhspan(-1.0, 1.0, color=t["good_band"], alpha=0.78, zorder=0)
                ax.axhline(0.0, color=t["good"], linewidth=1.1, zorder=1)
            for v_idx, _ in version_markers:
                if v_idx > 0:
                    ax.axvline(v_idx, color=t["divider"], linestyle=":", linewidth=1.0, zorder=1)
            all_y, end_labels = [], []
            first_valid = None
            last_x = len(entries) - 1
            for slbl, tool, br, col, mk, ls in series_spec:
                px, py, plo, phi = [], [], [], []
                for i, e in enumerate(entries):
                    sp = upload_agree_summary(i, tool, br) if is_signed else _vm_summary(e["runs"], scen, tool, br, fn)
                    if sp is not None:
                        px.append(i); py.append(sp[0]); plo.append(sp[1]); phi.append(sp[2])
                        all_y.extend([sp[1], sp[2]])
                        if first_valid is None or i < first_valid:
                            first_valid = i
                if not px:
                    continue
                ax.fill_between(px, plo, phi, color=col, alpha=0.11, zorder=2)
                ax.plot(px, py, color=col, linestyle=ls, linewidth=2.2, marker=mk, markersize=5.2,
                        markeredgecolor=t["card"], markeredgewidth=0.7, label=slbl, zorder=4)
                if is_signed:
                    txt = f"{py[-1]:+.1f}%" if abs(round(py[-1], 1)) > 0 else "0.0%"
                elif "s/GB" in dir_txt:
                    txt = f"{py[-1]:.2f}"
                else:
                    txt = f"{py[-1]:.1f}"
                end_labels.append((py[-1], txt, col))

            if is_signed:
                y_lo = min([-2.0, *(all_y or [-2.0])]) * 1.15
                y_hi = max([2.5, *(all_y or [2.5])]) + (abs(y_lo) * 0.50)
            else:
                y_lo = 0.0
                y_hi = max(all_y) * 1.30 if all_y else 10.0
            ax.set_ylim(y_lo, y_hi)
            y_span = y_hi - y_lo
            placed = _deconflict_labels(end_labels, y_lo + y_span * 0.05, y_hi - y_span * 0.05, y_span * 0.095)
            for orig_y, adj_y, txt, col in placed:
                if abs(adj_y - orig_y) > y_span * 0.015:
                    ax.plot([last_x + 0.08, last_x + 0.24], [orig_y, adj_y], color=col, alpha=0.5, linewidth=0.8, zorder=3)
                ax.text(last_x + 0.27, adj_y, txt, va="center", ha="left", fontsize=8.2,
                        family="DejaVu Sans Mono", color=col, weight="bold")

            if phase_note and first_valid and first_valid > 0:
                ax.axvspan(-0.35, first_valid - 0.35, color=t["card_alt"], alpha=0.90, zorder=1)
                ax.text((first_valid - 0.7) / 2, 0.42, "Phase CPU\nadded\nNov 2026",
                        transform=ax.get_xaxis_transform(), ha="center", va="center",
                        fontsize=8.2, color=t["faint"], style="italic")

            ax.set_xticks(tick_idxs)
            ax.set_xticklabels([x_labels[i] for i in tick_idxs], fontsize=7.8, color=t["muted"])
            ax.set_xlim(-0.35, len(entries) - 1 + max(1.05, 0.18 * len(entries)))
            leg = ax.legend(loc="upper left", frameon=True, facecolor=t["card"], framealpha=0.92,
                            edgecolor=t["border"], fontsize=7.5, ncol=3 if len(series_spec) > 4 else 2,
                            handlelength=1.3, borderpad=0.35, labelspacing=0.22, columnspacing=0.8)
            for text in leg.get_texts():
                text.set_color(t["text"])

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)
    return entries
