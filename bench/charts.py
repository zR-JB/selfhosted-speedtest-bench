"""Bento-card dark/light dashboards, per-VM strip plots, and auto-extending historic trends."""

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

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "card": "#151b23",
        "card_alt": "#1a222d",
        "border": "#2b3442",
        "ink": "#e6edf3",
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
        "colors": {
            "graphite-meter": "#58a6ff",
            "graphite-meter-no-loaded-latency": "#79c0ff",
            "graphite-meter-h2": "#39c5cf",
            "graphite-meter-h3": "#d29922",
            "graphite-meter-wt": "#bc8cff",
            "graphite-meter-client": "#58a6ff",
            "graphite-meter-client-no-loaded-latency": "#79c0ff",
            "graphite-meter-client-h2": "#39c5cf",
            "graphite-meter-client-h3": "#d29922",
            "librespeed": "#3fb950",
            "librespeed-go": "#f0883e",
            "librespeed-go-h2": "#f0883e",
            "librespeed-rust": "#bc8cff",
            "librespeed-cli": "#3fb950",
            "openspeedtest": "#f778ba",
            "openspeedtest-h2": "#f778ba",
            "iperf3": "#94a3b8",
        },
        "family": {
            "gm1": "#58a6ff",
            "gm2": "#39c5cf",
            "ip": "#94a3b8",
            "ls": "#3fb950",
            "lsg": "#f0883e",
            "lsr": "#bc8cff",
            "ost": "#f778ba",
        },
    },
    "light": {
        "bg": "#f6f8fa",
        "card": "#ffffff",
        "card_alt": "#f8fafc",
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
        "colors": {
            "graphite-meter": "#1d4ed8",
            "graphite-meter-no-loaded-latency": "#5b7fd4",
            "graphite-meter-h2": "#0891b2",
            "graphite-meter-h3": "#b45309",
            "graphite-meter-wt": "#7c3aed",
            "graphite-meter-client": "#1d4ed8",
            "graphite-meter-client-no-loaded-latency": "#5b7fd4",
            "graphite-meter-client-h2": "#0891b2",
            "graphite-meter-client-h3": "#b45309",
            "librespeed": "#0f766e",
            "librespeed-go": "#c2410c",
            "librespeed-go-h2": "#c2410c",
            "librespeed-rust": "#7c3aed",
            "librespeed-cli": "#0f766e",
            "openspeedtest": "#be185d",
            "openspeedtest-h2": "#be185d",
            "iperf3": "#475569",
        },
        "family": {
            "gm1": "#1d4ed8",
            "gm2": "#0891b2",
            "ip": "#475569",
            "ls": "#0f766e",
            "lsg": "#c2410c",
            "lsr": "#7c3aed",
            "ost": "#be185d",
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


def _short_client_label(tool, browser):
    base = {
        "graphite-meter": "GM Browser",
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


def _new_bento_fig(w, h, theme):
    t = THEMES[theme]
    fig = plt.figure(figsize=(w, h), facecolor=t["bg"])
    return fig, t


def _draw_card(fig, rect, t, title=None, subtitle=None, footer=None, radius=0.012):
    """Draw a rounded Bento card in figure coordinates [x, y, w, h] with inch-accurate header & footer."""
    x, y, w, h = rect
    fh = fig.get_figheight()
    patch = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        transform=fig.transFigure,
        facecolor=t["card"],
        edgecolor=t["border"],
        linewidth=1.0,
        zorder=0.1,
    )
    fig.patches.append(patch)
    if title:
        fig.text(x + 0.014, y + h - 0.14 / fh, title, color=t["ink"], fontsize=9.8,
                 weight="bold", va="top", ha="left", zorder=5)
    if subtitle:
        if w < 0.60:
            fig.text(x + 0.014, y + h - 0.36 / fh, subtitle, color=t["muted"], fontsize=7.3,
                     family="DejaVu Sans Mono", va="top", ha="left", zorder=5)
        else:
            fig.text(x + w - 0.014, y + h - 0.16 / fh, subtitle, color=t["muted"], fontsize=7.5,
                     family="DejaVu Sans Mono", va="top", ha="right", zorder=5)
    if footer:
        fy = y + 0.25 / fh
        fig.add_artist(plt.Line2D([x + 0.012, x + w - 0.012], [fy + 0.09 / fh, fy + 0.09 / fh],
                                  transform=fig.transFigure, color=t["border"], linewidth=0.7, zorder=4))
        fig.text(x + 0.014, fy + 0.02 / fh, footer, color=t["muted"], fontsize=7.3, va="top", ha="left", zorder=5)


def _draw_kpi_strip(fig, y_bottom, h, tiles, t):
    """Draw a 4-tile KPI summary row matching the T3 Code dashboard aesthetic."""
    n = len(tiles)
    margin = 0.018
    gap = 0.012
    tile_w = (1.0 - 2 * margin - gap * (n - 1)) / n
    for i, (val, label, note, accent) in enumerate(tiles):
        x = margin + i * (tile_w + gap)
        patch = mpatches.FancyBboxPatch(
            (x, y_bottom), tile_w, h,
            boxstyle="round,pad=0,rounding_size=0.010",
            transform=fig.transFigure,
            facecolor=t["card"],
            edgecolor=t["border"],
            linewidth=1.0,
            zorder=0.1,
        )
        fig.patches.append(patch)
        bar = mpatches.FancyBboxPatch(
            (x + 0.003, y_bottom + h * 0.16), 0.0035, h * 0.68,
            boxstyle="round,pad=0,rounding_size=0.002",
            transform=fig.transFigure,
            facecolor=accent,
            edgecolor="none",
            zorder=3,
        )
        fig.patches.append(bar)
        fig.text(x + 0.016, y_bottom + h - 0.012, val, color=accent, fontsize=14.0,
                 family="DejaVu Sans Mono", weight="bold", va="top", ha="left", zorder=5)
        fig.text(x + 0.016, y_bottom + h * 0.42, label, color=t["ink"], fontsize=8.3,
                 weight="bold", va="center", ha="left", zorder=5)
        fig.text(x + 0.016, y_bottom + 0.011, note, color=t["muted"], fontsize=7.2,
                 family="DejaVu Sans Mono", va="bottom", ha="left", zorder=5)


def _draw_banner(fig, kicker, title, subtitle, t, top_y=0.985):
    fig.text(0.018, top_y, kicker, color=t["muted"], fontsize=7.6, family="DejaVu Sans Mono",
             weight="bold", va="top", ha="left", zorder=5)
    fig.text(0.982, top_y, subtitle, color=t["muted"], fontsize=7.4,
             family="DejaVu Sans Mono", va="top", ha="right", zorder=5)
    fig.text(0.018, top_y - 0.018, title, color=t["ink"], fontsize=14.4,
             weight="bold", va="top", ha="left", zorder=5)


def _style_bento_ax(ax, t, grid_axis="x"):
    ax.set_zorder(2)
    ax.set_facecolor(t["card"])
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=t["grid"], linewidth=0.7, linestyle=(0, (2, 2)))
    ax.tick_params(colors=t["muted"], labelsize=7.6, length=0, pad=4)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)


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
# 1. Flagship Bento Dashboard: Campaign Overview (Dark + Light)
# ---------------------------------------------------------------------------

def render_overview_bento(out_stem, *, report_date, vm_count, measure, rate, paired, total_server_cpu, peak_memory):
    """Headline Bento dashboard: 4 KPI tiles + 10G & Unshaped w/ CPU/RAM meta + Challenging paths."""
    # Precompute KPI tiles
    gm_chr_ul_ag = measure(PLAIN, ("graphite-meter", "chrome"), lambda r: paired(r, UPLOAD))
    gm_trm_ul_ag = measure(PLAIN, ("graphite-meter-client", None), lambda r: paired(r, UPLOAD))
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

    for theme in ("dark", "light"):
        fig, t = _new_bento_fig(12.6, 10.8, theme)
        _draw_banner(
            fig,
            f"GITHUB RUNNER BENCHMARK  ·  {report_date}  ·  {vm_count} INDEPENDENT VMs",
            "Campaign Overview: Throughput, Footprint & Challenging Paths",
            "Per-VM medians · 4-vCPU runners (1 server / 2 client / 1 shaper)",
            t,
            top_y=0.986,
        )

        tiles = [
            (
                f"{fmt_num(median(gm_trm_ul_ag) if gm_trm_ul_ag else None, 1, True)}% / {fmt_num(median(gm_chr_ul_ag) if gm_chr_ul_ag else None, 1, True)}%",
                "1 Gbit/s Upload vs iperf3",
                "GM Terminal / GM Chrome (paired)",
                t["good"],
            ),
            (
                f"{fmt_num(median(gm_ff_10g) if gm_ff_10g else None, 2)} / {fmt_num(median(gm_ch_10g) if gm_ch_10g else None, 2)} Gbps",
                "10 Gbit/s Browser Upload",
                f"GM FF / Chr vs OST {fmt_num(median(ost_ch_10g) if ost_ch_10g else None, 2)} Gbps",
                t["dl"],
            ),
            (
                f"{fmt_num(median(gm_un_dl) if gm_un_dl else None, 1)} / {fmt_num(median(gm_un_ul) if gm_un_ul else None, 1)} Gbps",
                "Unshaped Native (DL / UL)",
                f"vs iperf3 {fmt_num(median(ip_un_dl) if ip_un_dl else None, 1)} / {fmt_num(median(ip_un_ul) if ip_un_ul else None, 1)} Gbps",
                t["dl"],
            ),
            (
                f"{fmt_num(median(gm_ram) if gm_ram else None, 1)} MB",
                "Lowest 1G Peak Server RAM",
                f"GM Chr vs {fmt_num(median(lsr_ram) if lsr_ram else None, 1)}–{fmt_num(median(ls_ram) if ls_ram else None, 1)} MB LibreSpeed",
                t["good"],
            ),
        ]
        _draw_kpi_strip(fig, 0.858, 0.084, tiles, t)

        # Card 1: 10G & Unshaped Throughput + Server CPU & Peak RAM metadata per row
        _draw_card(
            fig, (0.018, 0.405, 0.964, 0.438), t,
            title="1. High-Speed Throughput + Server Cost (10 Gbit/s Shaped & Unshaped)",
            subtitle="Blue = Download · Orange = Upload · Right tag = Total Server CPU · Peak RAM",
            footer="10 Gbit/s shaped TCP payload ceiling is 9.56 Gbit/s (2 ms RTT, offloads on). Unshaped measures host-local virtual link capacity.",
        )

        # Left sub-plot inside Card 1: 10 Gbit/s Shaped
        ax_10g = fig.add_axes([0.145, 0.468, 0.275, 0.312])
        _style_bento_ax(ax_10g, t, "x")
        rows_10g_spec = [
            ("GM Terminal · H1", ("graphite-meter-client", None)),
            ("iperf3 (4 TCP)", REFERENCE),
            ("GM Terminal · H2", ("graphite-meter-client-h2", None)),
            ("LibreSpeed CLI", ("librespeed-cli", None)),
            ("GM Terminal · H3", ("graphite-meter-client-h3", None)),
            ("GM Browser · Chr", ("graphite-meter", "chrome")),
            ("GM Browser · FF", ("graphite-meter", "firefox")),
            ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
            ("LibreSpeed Go · Chr", ("librespeed-go", "chrome")),
            ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
            ("GM Chrome · H2", ("graphite-meter-h2", "chrome")),
            ("GM Chrome · H3", ("graphite-meter-h3", "chrome")),
        ]
        rows_10g = []
        for lbl, cl in rows_10g_spec:
            d = measure(FAST, cl, rate(DOWNLOAD, 1000))
            u = measure(FAST, cl, rate(UPLOAD, 1000))
            cpu = measure(FAST, cl, total_server_cpu)
            ram = measure(FAST, cl, peak_memory)
            if d or u:
                meta = f"{median(cpu):.1f}s · {median(ram):.0f}M" if (cpu and ram) else ""
                rows_10g.append((lbl, cl, median(d) if d else 0.0, median(u) if u else 0.0, meta))
        y = np.arange(len(rows_10g))
        h = 0.36
        ax_10g.barh(y - h / 2, [r[2] for r in rows_10g], height=h, color=t["dl"], alpha=0.92, zorder=3)
        ax_10g.barh(y + h / 2, [r[3] for r in rows_10g], height=h, color=t["ul"], alpha=0.88, zorder=3)
        ax_10g.axvline(9.56, color=t["faint"], linestyle="--", linewidth=0.9, zorder=2)
        for i, (_, _, dv, uv, meta) in enumerate(rows_10g):
            ax_10g.text(10.35, i, meta, va="center", ha="left", fontsize=7.1,
                        family="DejaVu Sans Mono", color=t["muted"], clip_on=False)
        ax_10g.set_yticks(y)
        ax_10g.set_yticklabels([r[0] for r in rows_10g], fontsize=7.8, color=t["text"])
        ax_10g.invert_yaxis()
        ax_10g.set_xlim(0, 10.2)
        ax_10g.set_title("10 Gbit/s Shaped (max 9.56 Gbps)", fontsize=8.6, color=t["muted"],
                         family="DejaVu Sans Mono", loc="left", pad=6)

        # Right sub-plot inside Card 1: Unshaped
        ax_un = fig.add_axes([0.620, 0.468, 0.275, 0.312])
        _style_bento_ax(ax_un, t, "x")
        rows_un_spec = [
            ("GM Terminal · H1", ("graphite-meter-client", None)),
            ("iperf3 (4 TCP)", REFERENCE),
            ("LibreSpeed CLI", ("librespeed-cli", None)),
            ("GM Terminal · H2", ("graphite-meter-client-h2", None)),
            ("GM Browser · Chr", ("graphite-meter", "chrome")),
            ("LibreSpeed Go · Chr", ("librespeed-go", "chrome")),
            ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
            ("LibreSpeed PHP · Chr", ("librespeed", "chrome")),
            ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
            ("GM Terminal · H3", ("graphite-meter-client-h3", None)),
            ("GM Browser · FF", ("graphite-meter", "firefox")),
            ("OpenSpeedTest · FF", ("openspeedtest", "firefox")),
        ]
        rows_un = []
        for lbl, cl in rows_un_spec:
            d = measure(UNCAPPED, cl, rate(DOWNLOAD, 1000))
            u = measure(UNCAPPED, cl, rate(UPLOAD, 1000))
            cpu = measure(UNCAPPED, cl, total_server_cpu)
            ram = measure(UNCAPPED, cl, peak_memory)
            if d or u:
                meta = f"{median(cpu):.1f}s · {median(ram):.0f}M" if (cpu and ram) else ""
                rows_un.append((lbl, cl, median(d) if d else 0.0, median(u) if u else 0.0, meta))
        y2 = np.arange(len(rows_un))
        max_un = max([max(r[2], r[3]) for r in rows_un] + [55.0])
        ax_un.barh(y2 - h / 2, [r[2] for r in rows_un], height=h, color=t["dl"], alpha=0.92, zorder=3)
        ax_un.barh(y2 + h / 2, [r[3] for r in rows_un], height=h, color=t["ul"], alpha=0.88, zorder=3)
        for i, (_, _, dv, uv, meta) in enumerate(rows_un):
            ax_un.text(max_un * 1.06, i, meta, va="center", ha="left", fontsize=7.1,
                       family="DejaVu Sans Mono", color=t["muted"], clip_on=False)
        ax_un.set_yticks(y2)
        ax_un.set_yticklabels([r[0] for r in rows_un], fontsize=7.8, color=t["text"])
        ax_un.invert_yaxis()
        ax_un.set_xlim(0, max_un * 1.04)
        ax_un.set_title("Unshaped Virtual Link (Gbit/s)", fontsize=8.6, color=t["muted"],
                        family="DejaVu Sans Mono", loc="left", pad=6)

        # Card 2: Challenging paths 3-column mini-grid inside one Bento card
        _draw_card(
            fig, (0.018, 0.022, 0.964, 0.365), t,
            title="2. Challenging Network Paths — 1% Loss, 160 ms High-BDP & Behind nginx Reverse Proxy",
            subtitle="Per-VM medians · Mbit/s (Blue = Download, Orange = Upload)",
            footer="Connection count & congestion ramp dominate under 1% loss and 160 ms RTT; proxy runs place identical nginx in front of each server.",
        )

        chall_specs = [
            (LOSS, "100 Mbit/s · 1% Loss (40 ms)", None, [0.120, 0.088, 0.195, 0.238], [
                ("GM Browser · Chr", ("graphite-meter", "chrome")),
                ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
                ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
                ("GM Browser · FF", ("graphite-meter", "firefox")),
                ("GM Terminal", ("graphite-meter-client", None)),
                ("LibreSpeed CLI", ("librespeed-cli", None)),
                ("iperf3 (ref)", REFERENCE),
            ]),
            (LONG, "300 Mbit/s · 160 ms RTT", 286.9, [0.435, 0.088, 0.195, 0.238], [
                ("GM Browser · Chr", ("graphite-meter", "chrome")),
                ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
                ("LibreSpeed Rust · Chr", ("librespeed-rust", "chrome")),
                ("GM Browser · FF", ("graphite-meter", "firefox")),
                ("GM Terminal", ("graphite-meter-client", None)),
                ("LibreSpeed CLI", ("librespeed-cli", None)),
                ("iperf3 (ref)", REFERENCE),
            ]),
            (PROXY, "1 Gbit/s Behind nginx", 956.4, [0.750, 0.088, 0.205, 0.238], [
                ("GM Browser · Chr", ("graphite-meter", "chrome")),
                ("LibreSpeed PHP · Chr", ("librespeed", "chrome")),
                ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
                ("GM Browser · FF", ("graphite-meter", "firefox")),
                ("LibreSpeed PHP · FF", ("librespeed", "firefox")),
                ("OpenSpeedTest · FF", ("openspeedtest", "firefox")),
                ("iperf3 (direct)", REFERENCE),
            ]),
        ]
        for sc_id, stitle, ceil_x, ax_rect, subset in chall_specs:
            axc = fig.add_axes(ax_rect)
            _style_bento_ax(axc, t, "x")
            data = []
            for lbl, cl in subset:
                d = measure(sc_id, cl, rate(DOWNLOAD))
                u = measure(sc_id, cl, rate(UPLOAD))
                if d or u:
                    data.append((lbl, median(d) if d else 0.0, median(u) if u else 0.0))
            yc = np.arange(len(data))
            max_v = max([*(x[1] for x in data), *(x[2] for x in data), ceil_x or 1.0])
            axc.barh(yc - 0.18, [x[1] for x in data], height=0.33, color=t["dl"], alpha=0.90, zorder=3)
            axc.barh(yc + 0.18, [x[2] for x in data], height=0.33, color=t["ul"], alpha=0.86, zorder=3)
            for i, (_, dv, uv) in enumerate(data):
                axc.text(dv + max_v * 0.02, i - 0.18, f"{dv:.1f}", va="center", ha="left",
                         fontsize=6.9, family="DejaVu Sans Mono", color=t["dl"])
                axc.text(uv + max_v * 0.02, i + 0.18, f"{uv:.1f}", va="center", ha="left",
                         fontsize=6.9, family="DejaVu Sans Mono", color=t["ul"])
            if ceil_x:
                axc.axvline(ceil_x, color=t["faint"], linestyle="--", linewidth=0.85, zorder=2)
            axc.set_yticks(yc)
            axc.set_yticklabels([x[0] for x in data], fontsize=7.4, color=t["text"])
            axc.invert_yaxis()
            axc.set_xlim(0, max_v * 1.25)
            axc.set_title(stitle, fontsize=8.4, color=t["muted"], family="DejaVu Sans Mono", loc="left", pad=5)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Flagship Bento Dashboard: Complete Resource Efficiency (Dark + Light)
# ---------------------------------------------------------------------------

def render_resources_bento(out_stem, *, report_date, vm_count, groups, measure, phase_cpu, total_server_cpu, peak_memory, client_cpu):
    """Modeled on resource_graphs.html: ALL implementations ranked best->worst across 1G, 10G, Unshaped, RAM & Client CPU."""
    def total_cpu_per_gb(row):
        cpu = row.get("serverCpuSeconds")
        link = sum(row.get("linkBytes", {}).values())
        return cpu * 1e9 / link if cpu is not None and link else None

    def collect_ranked(scenario, metric, exclude_no_lat=True):
        rows = []
        seen = set()
        for (sc, cl), rs in groups.items():
            if sc != scenario or cl in seen:
                continue
            seen.add(cl)
            tool, br = cl
            if exclude_no_lat and tool in (NO_LOADED_LATENCY, TERMINAL_NO_LOADED_LATENCY):
                continue
            vals = measure(scenario, cl, metric)
            if vals:
                rows.append((_short_client_label(tool, br), cl, median(vals)))
        rows.sort(key=lambda x: x[2])
        return rows

    r_1g = collect_ranked(PLAIN, total_cpu_per_gb)
    r_10g = collect_ranked(FAST, total_cpu_per_gb)
    r_un = collect_ranked(UNCAPPED, total_cpu_per_gb)

    # Peak RAM across 1G direct, H2 variants, and Behind nginx proxy
    ram_rows = []
    for lbl, sc, cl in [
        ("GM Browser · Chr (1G)", PLAIN, ("graphite-meter", "chrome")),
        ("GM Browser · FF (1G)", PLAIN, ("graphite-meter", "firefox")),
        ("GM Terminal (1G)", PLAIN, ("graphite-meter-client", None)),
        ("GM Chrome H2 (10G)", FAST, ("graphite-meter-h2", "chrome")),
        ("GM Chrome H3 (10G)", FAST, ("graphite-meter-h3", "chrome")),
        ("iperf3 (1G)", PLAIN, REFERENCE),
        ("LibreSpeed Rust · Chr (1G)", PLAIN, ("librespeed-rust", "chrome")),
        ("OpenSpeedTest · Chr (1G)", PLAIN, ("openspeedtest", "chrome")),
        ("GM Browser · Chr (nginx)", PROXY, ("graphite-meter", "chrome")),
        ("LibreSpeed Go · Chr (1G)", PLAIN, ("librespeed-go", "chrome")),
        ("LibreSpeed Go H2 (10G)", FAST, ("librespeed-go-h2", "chrome")),
        ("OpenSpeedTest · Chr (nginx)", PROXY, ("openspeedtest", "chrome")),
        ("LibreSpeed CLI (1G)", PLAIN, ("librespeed-cli", None)),
        ("LibreSpeed PHP · Chr (1G)", PLAIN, ("librespeed", "chrome")),
        ("LibreSpeed PHP · Chr (nginx)", PROXY, ("librespeed", "chrome")),
        ("OpenSpeedTest H2 (10G)", FAST, ("openspeedtest-h2", "chrome")),
    ]:
        vals = measure(sc, cl, peak_memory)
        if vals:
            ram_rows.append((lbl, cl, median(vals)))
    ram_rows.sort(key=lambda x: x[2])

    # Client CPU (Unshaped)
    c_rows = []
    for cl in [
        ("graphite-meter", "chrome"),
        ("librespeed-go", "chrome"),
        ("openspeedtest", "chrome"),
        ("librespeed-rust", "chrome"),
        ("librespeed", "chrome"),
        ("graphite-meter", "firefox"),
        ("openspeedtest", "firefox"),
        ("librespeed-go", "firefox"),
        ("librespeed-rust", "firefox"),
        ("librespeed", "firefox"),
        ("graphite-meter-client", None),
        ("librespeed-cli", None),
        REFERENCE,
    ]:
        vals = measure(UNCAPPED, cl, client_cpu)
        if vals:
            c_rows.append((_short_client_label(cl[0], cl[1]), cl, spread(vals)))
    c_rows.sort(key=lambda x: x[2][0])

    # KPI winners (strictly neutral: lowest measured median)
    def best_phase(scen, direc):
        cands = []
        for cl in [("graphite-meter", "chrome"), ("librespeed", "chrome"), ("librespeed-go", "chrome"),
                   ("librespeed-rust", "chrome"), ("openspeedtest", "chrome"),
                   ("graphite-meter-client", None), ("librespeed-cli", None)]:
            vs = measure(scen, cl, phase_cpu(direc))
            if vs:
                cands.append((_short_client_label(cl[0], cl[1]), median(vs)))
        return min(cands, key=lambda x: x[1]) if cands else ("—", None)

    b_1g_dn = best_phase(PLAIN, "down")
    b_1g_up = best_phase(PLAIN, "up")
    b_un_up = best_phase(UNCAPPED, "up")
    b_ram = ram_rows[0] if ram_rows else ("—", None, None)

    for theme in ("dark", "light"):
        fig, t = _new_bento_fig(12.6, 12.2, theme)
        _draw_banner(
            fig,
            f"RESOURCE EFFICIENCY BENCHMARK  ·  {report_date}  ·  {vm_count} VMs",
            "All Implementations — Server CPU per GB, Peak Memory & Client CPU",
            "cgroup v2 per run · Ranked lowest → highest (lower is better)",
            t,
            top_y=0.988,
        )
        tiles = [
            (f"{b_1g_dn[1]:.3f} s/GB" if b_1g_dn[1] else "—", "Lowest 1G Download CPU", b_1g_dn[0], t["dl"]),
            (f"{b_1g_up[1]:.3f} s/GB" if b_1g_up[1] else "—", "Lowest 1G Upload CPU", b_1g_up[0], t["good"]),
            (f"{b_un_up[1]:.3f} s/GB" if b_un_up[1] else "—", "Lowest Unshaped Upload CPU", b_un_up[0], t["good"]),
            (f"{b_ram[2]:.1f} MB" if b_ram[2] else "—", "Lowest Peak Server RAM", b_ram[0], t["dl"]),
        ]
        _draw_kpi_strip(fig, 0.875, 0.074, tiles, t)

        # Shared family color legend pill strip between KPI and Card 1
        leg_items = [
            ("GM HTTP/1.1", t["family"]["gm1"]),
            ("GM H2/H3/WT", t["family"]["gm2"]),
            ("iperf3 (ref)", t["family"]["ip"]),
            ("LibreSpeed PHP/CLI", t["family"]["ls"]),
            ("LibreSpeed Go", t["family"]["lsg"]),
            ("LibreSpeed Rust", t["family"]["lsr"]),
            ("OpenSpeedTest", t["family"]["ost"]),
        ]
        handles = [mpatches.Patch(color=c, label=l) for l, c in leg_items]
        fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.869), ncol=7,
                   frameon=False, fontsize=7.6, labelcolor=t["muted"], handlelength=1.0, columnspacing=1.2)

        def draw_ranked(ax, title_s, rows_s, fmt_val, max_pad=1.22):
            _style_bento_ax(ax, t, "x")
            ys = np.arange(len(rows_s))
            mx = max([r[2] for r in rows_s] + [0.1])
            for i, (lbl, cl, val) in enumerate(rows_s):
                fam = _family_of(cl[0])
                col = t["family"][fam]
                is_top = i == 0
                ax.barh(i, val, height=0.66, color=col, alpha=0.90 if is_top else 0.78, zorder=3)
                ax.text(val + mx * 0.02, i, fmt_val(val), va="center", ha="left",
                        fontsize=7.2, family="DejaVu Sans Mono",
                        color=t["ink"] if is_top else t["muted"], weight="bold" if is_top else "normal")
            ax.set_yticks(ys)
            ax.set_yticklabels([r[0] for r in rows_s], fontsize=7.4, color=t["text"])
            ax.invert_yaxis()
            ax.set_xlim(0, mx * max_pad)
            ax.set_title(title_s, fontsize=8.4, color=t["muted"], family="DejaVu Sans Mono", loc="left", pad=5)

        # Card 1: 1G & 10G Server CPU/GB across ALL implementations
        _draw_card(
            fig, (0.018, 0.495, 0.964, 0.348), t,
            title="1. All Implementations — Total Server CPU per GB Moved (1 Gbit/s & 10 Gbit/s)",
            subtitle="median serverCpuSeconds / total link GB",
        )
        ax_c1 = fig.add_axes([0.148, 0.518, 0.325, 0.278])
        ax_c2 = fig.add_axes([0.625, 0.518, 0.335, 0.278])
        draw_ranked(ax_c1, "1 Gbit/s (s/GB, offloads off)", r_1g, lambda v: f"{v:.3f}s")
        draw_ranked(ax_c2, "10 Gbit/s (s/GB, offloads on)", r_10g, lambda v: f"{v:.3f}s")

        # Card 2: Unshaped Server CPU/GB & Peak Server RAM across scenarios
        _draw_card(
            fig, (0.018, 0.195, 0.964, 0.286), t,
            title="2. Unshaped Server CPU/GB & Peak Server RAM Across Direct, HTTP/2 & nginx Proxy",
            subtitle="Lower = better",
        )
        ax_c3 = fig.add_axes([0.148, 0.218, 0.325, 0.218])
        ax_c4 = fig.add_axes([0.635, 0.218, 0.325, 0.218])
        draw_ranked(ax_c3, "Unshaped Server CPU (s/GB)", r_un, lambda v: f"{v:.3f}s")
        draw_ranked(ax_c4, "Peak Server Container RAM (MB)", ram_rows, lambda v: f"{v:.1f}M")

        # Card 3: Client-side CPU Efficiency (Unshaped)
        _draw_card(
            fig, (0.018, 0.018, 0.964, 0.163), t,
            title="3. Client-Side CPU Efficiency on Unshaped (s/GB moved · Bar = Median, Line = VM IQR)",
            subtitle="Browser process tree + native client cgroup where recorded",
        )
        ax_c5 = fig.add_axes([0.148, 0.042, 0.805, 0.100])
        _style_bento_ax(ax_c5, t, "y")
        xs5 = np.arange(len(c_rows))
        m5 = max([r[2][2] for r in c_rows] + [1.0])
        for i, (lbl, cl, (med, lo, hi)) in enumerate(c_rows):
            col = t["family"][_family_of(cl[0])]
            ax_c5.bar(i, med, width=0.56, color=col, alpha=0.80, zorder=3)
            ax_c5.plot([i, i], [lo, hi], color=t["ink"], linewidth=1.6, zorder=4)
            ax_c5.text(i, max(hi, med) + m5 * 0.04, f"{med:.2f}", ha="center", va="bottom",
                       fontsize=7.3, family="DejaVu Sans Mono", color=t["ink"], weight="bold")
        ax_c5.set_xticks(xs5)
        ax_c5.set_xticklabels(
            [r[0].replace("LibreSpeed ", "LS ").replace("OpenSpeedTest", "OST").replace(" · ", "\n") for r in c_rows],
            fontsize=6.5 if len(c_rows) > 9 else 7.0,
            color=t["text"],
        )
        ax_c5.set_ylim(0, m5 * 1.24)
        ax_c5.set_ylabel("s/GB", fontsize=7.6, color=t["muted"])

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Flagship Bento Dashboard: Accuracy, Upload Integrity & Latency (Dark + Light)
# ---------------------------------------------------------------------------

def render_accuracy_bento(out_stem, *, report_date, vm_count, measure, paired, rate, shaper_upload, server_rx, idle_delta, fifo_latency):
    """3-card Bento: 1G Upload Agreement dot-strip + 30M FIFO Upload Integrity + Idle & FIFO Latency."""
    for theme in ("dark", "light"):
        fig, t = _new_bento_fig(12.6, 9.2, theme)
        _draw_banner(
            fig,
            f"ACCURACY, COUNTER INTEGRITY & LATENCY  ·  {report_date}  ·  {vm_count} VMs",
            "1 Gbit/s Agreement, Upload Counter Check & Bufferbloat Latency",
            "Same-pass iperf3 baseline · ICMP idle baseline · 100 ms shaper queue sampler",
            t,
            top_y=0.986,
        )

        # Left Card (full height): 1 Gbit/s Upload Agreement vs same-pass iperf3
        _draw_card(
            fig, (0.018, 0.022, 0.475, 0.905), t,
            title="1. 1 Gbit/s Upload Agreement vs iperf3",
            subtitle="Shaded = ±1% · Dots = VMs",
            footer="0% matches same-pass iperf3 receiver payload rate; IQR shown right.",
        )
        ax1 = fig.add_axes([0.165, 0.095, 0.215, 0.765])
        _style_bento_ax(ax1, t, "x")
        agree_spec = [
            ("Chrome", [
                ("GM Browser", ("graphite-meter", "chrome")),
                ("OpenSpeedTest", ("openspeedtest", "chrome")),
                ("LibreSpeed Go", ("librespeed-go", "chrome")),
                ("LibreSpeed Rust", ("librespeed-rust", "chrome")),
                ("LibreSpeed PHP", ("librespeed", "chrome")),
            ]),
            ("Firefox", [
                ("GM Browser", ("graphite-meter", "firefox")),
                ("OpenSpeedTest", ("openspeedtest", "firefox")),
                ("LibreSpeed Go", ("librespeed-go", "firefox")),
                ("LibreSpeed Rust", ("librespeed-rust", "firefox")),
                ("LibreSpeed PHP", ("librespeed", "firefox")),
            ]),
            ("Native Terminal", [
                ("GM Terminal", ("graphite-meter-client", None)),
                ("LibreSpeed CLI", ("librespeed-cli", None)),
            ]),
        ]
        y_rows = []
        for sec, items in agree_spec:
            y_rows.append(("sec", sec, None, None))
            for lbl, cl in items:
                vals = measure(PLAIN, cl, lambda r: paired(r, UPLOAD))
                y_rows.append(("row", lbl, cl, vals))

        all_v = [v for kind, _, _, vs in y_rows if kind == "row" and vs for v in vs]
        ax1.axvspan(-1.0, 1.0, color=t["good_band"], alpha=0.75, zorder=0)
        ax1.axvline(0.0, color=t["good"], linewidth=1.1, zorder=2)
        blended1 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax1.transData)
        for i, (kind, lbl, cl, vs) in enumerate(y_rows):
            if kind == "sec":
                ax1.text(0.032, i, lbl, transform=blended1, va="center", ha="left",
                         fontsize=8.3, weight="bold", color=t["ink"])
                continue
            col = t["colors"].get(cl[0], t["muted"])
            ax1.text(0.042, i, lbl, transform=blended1, va="center", ha="left", fontsize=7.8, color=t["text"])
            ax1.scatter(0.035, i, transform=blended1, color=col, s=16, clip_on=False, zorder=5)
            if vs:
                med, lo, hi = spread(vs)
                offs = [i + ((k % 5) - 2) * 0.065 for k in range(len(vs))]
                ax1.scatter(vs, offs, color=col, s=11, alpha=0.42, linewidth=0, zorder=3)
                ax1.plot([lo, hi], [i, i], color=col, linewidth=2.8, solid_capstyle="round", zorder=4)
                ax1.scatter(med, i, color=col, s=36, edgecolor=t["card"], linewidth=0.8, zorder=5)
                ax1.text(0.432, i, f"{fmt_num(med, 1, True)}%", transform=blended1, va="center", ha="right",
                         fontsize=7.7, family="DejaVu Sans Mono", color=t["ink"], weight="bold")
                ax1.text(0.482, i, f"[{fmt_num(lo, 1)},{fmt_num(hi, 1)}]", transform=blended1, va="center", ha="right",
                         fontsize=6.6, family="DejaVu Sans Mono", color=t["muted"])
        ax1.set_yticks([])
        ax1.set_ylim(len(y_rows) - 0.3, -0.7)
        lo_x = min([-2.0, *(all_v or [-2.0])])
        hi_x = max([2.0, *(all_v or [2.0])])
        ax1.set_xlim(lo_x - 0.8, hi_x + 0.8)
        ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+g}%" if v else "0%"))
        ax1.set_xlabel("Difference vs same-pass iperf3 (%)", fontsize=7.8, color=t["muted"])

        # Top-Right Card: Upload Counter Integrity on 30 Mbit/s FIFO
        _draw_card(
            fig, (0.506, 0.485, 0.476, 0.442), t,
            title="2. Upload Counter Check (30 Mbit/s · 200 ms FIFO)",
            subtitle="Red dashed = 28.7 Mbit/s TCP payload ceiling",
            footer="Shaper & Server RX include framing overhead; payload-reporting apps stay ≤ 28.7 Mbit/s.",
        )
        ax2 = fig.add_axes([0.640, 0.568, 0.320, 0.268])
        _style_bento_ax(ax2, t, "x")
        uc_items = [
            ("OpenSpeedTest · Chr", ("openspeedtest", "chrome")),
            ("OpenSpeedTest · FF", ("openspeedtest", "firefox")),
            ("LibreSpeed PHP · Chr", ("librespeed", "chrome")),
            ("GM Browser · Chr", ("graphite-meter", "chrome")),
            ("GM Browser · FF", ("graphite-meter", "firefox")),
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
        y2 = np.arange(len(uc_rows))
        h2 = 0.25
        ax2.barh(y2 - h2, [r[1] for r in uc_rows], height=h2, color=t["dl"], alpha=0.92, label="App reported", zorder=3)
        ax2.barh(y2, [r[2] for r in uc_rows], height=h2, color=t["shaper"], alpha=0.68, label="Shaper busy", zorder=3)
        ax2.barh(y2 + h2, [r[3] for r in uc_rows], height=h2, color=t["rx"], alpha=0.82, label="Server RX", zorder=3)
        ax2.axvline(28.69, color=t["bad"], linestyle="--", linewidth=1.1, zorder=4)
        for i, (_, av, _, rv) in enumerate(uc_rows):
            col_a = t["bad"] if av > 29.2 else t["ink"]
            ax2.text(av + 0.22, i - h2, f"{av:.1f}", va="center", ha="left", fontsize=7.3,
                     family="DejaVu Sans Mono", color=col_a, weight="bold")
        ax2.set_yticks(y2)
        ax2.set_yticklabels([r[0] for r in uc_rows], fontsize=7.6, color=t["text"])
        ax2.invert_yaxis()
        ax2.set_xlim(22, 33.0)
        ax2.set_xlabel("Upload rate (Mbit/s)", fontsize=7.6, color=t["muted"])
        ax2.legend(loc="upper left", bbox_to_anchor=(0.0, 1.11), ncol=3, frameon=False,
                   fontsize=7.2, labelcolor=t["muted"], handlelength=1.0)

        # Bottom-Right Card: FIFO Loaded Latency Tracking
        _draw_card(
            fig, (0.506, 0.022, 0.476, 0.448), t,
            title="3. Bufferbloat Loaded Latency (300/30 · 200 ms FIFO)",
            subtitle="App reported vs Queue estimate (+Δ ms)",
            footer="Idle baseline = min of 10 ICMP pings; estimate adds median shaper queue delay.",
        )
        ax3 = fig.add_axes([0.640, 0.106, 0.320, 0.270])
        _style_bento_ax(ax3, t, "x")
        fifo_items = [
            ("GM Chrome · Download", ("graphite-meter", "chrome"), "loadedLatencyDownMs", "down"),
            ("GM Chrome · Upload", ("graphite-meter", "chrome"), "loadedLatencyUpMs", "up"),
            ("GM Firefox · Download", ("graphite-meter", "firefox"), "loadedLatencyDownMs", "down"),
            ("GM Firefox · Upload", ("graphite-meter", "firefox"), "loadedLatencyUpMs", "up"),
            ("GM Terminal · Download", ("graphite-meter-client", None), "loadedLatencyDownMs", "down"),
            ("GM Terminal · Upload", ("graphite-meter-client", None), "loadedLatencyUpMs", "up"),
        ]
        f_rows = []
        for lbl, cl, fld, ddir in fifo_items:
            app = measure(FIFO, cl, rate(fld))
            est = measure(FIFO, cl, fifo_latency(ddir))
            if app and est:
                f_rows.append((lbl, median(app), median(est)))
        y3 = np.arange(len(f_rows))
        h3 = 0.34
        m3 = max([max(r[1], r[2]) for r in f_rows] + [200.0])
        ax3.barh(y3 - h3 / 2, [r[1] for r in f_rows], height=h3, color=t["dl"], alpha=0.92, label="App reported", zorder=3)
        ax3.barh(y3 + h3 / 2, [r[2] for r in f_rows], height=h3, color=t["shaper"], alpha=0.72, label="Queue estimate", zorder=3)
        for i, (_, av, ev) in enumerate(f_rows):
            ax3.text(av + 3.5, i - h3 / 2, f"{av:.1f} ({av - ev:+.1f})", va="center", ha="left",
                     fontsize=7.3, family="DejaVu Sans Mono", color=t["ink"], weight="bold")
            ax3.text(ev + 3.5, i + h3 / 2, f"{ev:.1f} ms", va="center", ha="left",
                     fontsize=7.1, family="DejaVu Sans Mono", color=t["muted"])
        ax3.set_yticks(y3)
        ax3.set_yticklabels([r[0] for r in f_rows], fontsize=7.6, color=t["text"])
        ax3.invert_yaxis()
        ax3.set_xlim(0, m3 * 1.44)
        ax3.set_xlabel("Loaded latency (ms)", fontsize=7.6, color=t["muted"])
        ax3.legend(loc="upper left", bbox_to_anchor=(0.0, 1.11), ncol=2, frameon=False,
                   fontsize=7.3, labelcolor=t["muted"], handlelength=1.0)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Flagship Bento Dashboard: Consistency & Runner Hardware (Dark + Light)
# ---------------------------------------------------------------------------

def render_consistency_bento(out_stem, *, report_date, vm_count, measure, by_vm, rate, jobs):
    """2-card Bento: Grouped vertical Consistency/Asymmetry bars + Runner Hardware split."""
    tools_cons = [
        ("GM Terminal", ("graphite-meter-client", None), "gm1"),
        ("GM Chrome", ("graphite-meter", "chrome"), "gm2"),
        ("LibreSpeed CLI", ("librespeed-cli", None), "ls"),
        ("LibreSpeed Rust", ("librespeed-rust", "chrome"), "lsr"),
        ("OpenSpeedTest", ("openspeedtest", "chrome"), "ost"),
    ]

    def iqr_pct(scen, cl):
        vs = measure(scen, cl, rate(UPLOAD))
        if len(vs) < 2:
            return 0.0
        med, lo, hi = spread(vs)
        return 100.0 * (hi - lo) / med if med > 0 else 0.0

    def asym_pct(scen, cl):
        d = measure(scen, cl, rate(DOWNLOAD))
        u = measure(scen, cl, rate(UPLOAD))
        if not d or not u:
            return 0.0
        dm, um = median(d), median(u)
        return 100.0 * abs(dm - um) / max(dm, um, 1e-6)

    def unshaped_iqr(cl):
        return iqr_pct(UNCAPPED, cl)

    groups_cons = [
        ("1G UL\nIQR %", [iqr_pct(PLAIN, cl) for _, cl, _ in tools_cons]),
        ("10G UL\nIQR %", [iqr_pct(FAST, cl) for _, cl, _ in tools_cons]),
        ("1% Loss\n|D−U| %", [asym_pct(LOSS, cl) for _, cl, _ in tools_cons]),
        ("160ms RTT\n|D−U| %", [asym_pct(LONG, cl) for _, cl, _ in tools_cons]),
        ("Unshaped\nIQR %", [unshaped_iqr(cl) for _, cl, _ in tools_cons]),
    ]

    # Runner hardware grouping
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
        fig, t = _new_bento_fig(12.6, 5.9, theme)
        _draw_banner(
            fig,
            f"CONSISTENCY, SYMMETRY & RUNNER HARDWARE  ·  {report_date}  ·  {vm_count} VMs",
            "Spread Across VMs, Directional Asymmetry & Runner CPU Heterogeneity",
            "Lower spread/asymmetry = more consistent · AWS vs Azure runner split",
            t,
            top_y=0.980,
        )

        # Left Card: Grouped vertical bars (perf_rundown Panel 4 style)
        _draw_card(
            fig, (0.018, 0.030, 0.480, 0.860), t,
            title="1. Spread & Directional Asymmetry (Lower = Steadier)",
            subtitle="IQR/median % · |DL−UL|/max %",
            footer="1G & 10G IQR% reflects VM-to-VM variance; |D−U|% measures symmetric-link directional skew.",
        )
        ax1 = fig.add_axes([0.058, 0.175, 0.422, 0.525])
        _style_bento_ax(ax1, t, "y")
        n_g = len(groups_cons)
        n_b = len(tools_cons)
        bw = 0.145
        max_c = max([v for _, vs in groups_cons for v in vs] + [50.0])
        for bi, (tlbl, _, fam) in enumerate(tools_cons):
            col = t["family"][fam]
            xs = np.arange(n_g) + (bi - (n_b - 1) / 2) * (bw + 0.015)
            vals = [g[1][bi] for g in groups_cons]
            ax1.bar(xs, vals, width=bw, color=col, alpha=0.88, label=tlbl, zorder=3)
            for x, v in zip(xs, vals, strict=True):
                if v >= 5 or bi < 2:
                    lbl_v = f"{v:.1f}" if v < 10 else f"{v:.0f}"
                    ax1.text(x, v + max_c * 0.018, lbl_v, ha="center", va="bottom",
                             fontsize=6.4, family="DejaVu Sans Mono", color=t["muted"])
        ax1.set_xticks(np.arange(n_g))
        ax1.set_xticklabels([g[0] for g in groups_cons], fontsize=7.5, color=t["text"])
        ax1.set_ylim(0, max_c * 1.18)
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
        ax1.legend(loc="upper left", bbox_to_anchor=(-0.02, 1.15), ncol=3, frameon=False,
                   fontsize=7.0, labelcolor=t["muted"], handlelength=1.0, columnspacing=0.9)

        # Right Card: Unshaped Native Upload by Runner Hardware
        _draw_card(
            fig, (0.512, 0.030, 0.470, 0.860), t,
            title="2. Unshaped Native Upload by Runner CPU & Cloud",
            subtitle="Gbit/s median per host class",
            footer="GitHub ubuntu-24.04 mixes Azure EPYC and AWS Xeon VMs, explaining bimodal unshaped IQRs.",
        )
        ax2 = fig.add_axes([0.650, 0.175, 0.315, 0.525])
        _style_bento_ax(ax2, t, "x")
        hw_clients = [
            ("GM Terminal", ("graphite-meter-client", None), t["family"]["gm1"]),
            ("iperf3 (ref)", REFERENCE, t["family"]["ip"]),
            ("LibreSpeed CLI", ("librespeed-cli", None), t["family"]["ls"]),
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
            ax2.barh(y2 + off, vals, height=h2, color=col, alpha=0.88, label=lbl, zorder=3)
            for i, v in enumerate(vals):
                if v > 0:
                    ax2.text(v + 1.2, i + off, f"{v:.1f}", va="center", ha="left",
                             fontsize=7.3, family="DejaVu Sans Mono", color=col, weight="bold")
        ax2.set_yticks(y2)
        ax2.set_yticklabels([f"{cloud} · {cpu}\n(n={len(jnames)} VM{'s' if len(jnames) != 1 else ''})"
                             for (cloud, cpu), jnames in hw_groups], fontsize=7.5, color=t["text"])
        ax2.invert_yaxis()
        ax2.set_xlim(0, max(all_hw or [60.0]) * 1.20)
        ax2.set_xlabel("Unshaped upload median (Gbit/s)", fontsize=7.6, color=t["muted"])
        ax2.legend(loc="upper left", bbox_to_anchor=(0.0, 1.13), ncol=3, frameon=False,
                   fontsize=7.2, labelcolor=t["muted"], handlelength=1.0)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Per-VM Detail Dot-Strip Charts (Dark + Light, used inside <details>)
# ---------------------------------------------------------------------------

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
    theme="light",
):
    """Crisp per-VM dot strip + IQR bar + median + IQR readout chart."""
    t = THEMES[theme]
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

    row_h = 0.32
    top_pad = 1.28
    bot_pad = 0.60
    height = top_pad + bot_pad + row_h * len(rows)
    fig_w = 11.2 if has_third else 10.2
    fig, ax = plt.subplots(figsize=(fig_w, height), facecolor=t["card"])
    ax.set_facecolor(t["card"])
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
    ax.set_xlabel(unit, fontsize=8.8, labelpad=6, color=t["text"])
    ax.set_axisbelow(True)
    ax.set_yticks([])
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
    if difference:
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+g}%" if v else "0%"))
        ax.axvspan(-1.0, 1.0, color=t["good_band"], alpha=0.80, zorder=0)
        ax.axvline(0.0, color=t["good"], linewidth=1.15, zorder=2)
    ax.tick_params(axis="x", length=3, color=t["divider"], colors=t["muted"], labelsize=8.4, pad=4)
    ax.grid(axis="x", color=t["grid"], linewidth=0.75, zorder=1)
    for spine in ax.spines.values():
        spine.set_visible(False)

    blended = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax.transData)
    x_sec, x_dot, x_lbl = 0.024, 0.032, 0.044
    col_med = 0.742 if has_third else 0.820
    col_iqr = 0.875 if has_third else 0.974
    col_ext = 0.976

    ax.text(col_med, -0.82, "MEDIAN", transform=blended, ha="right", va="bottom", fontsize=7.5, color=t["muted"], weight="bold")
    ax.text(col_iqr, -0.82, "IQR [p25, p75]", transform=blended, ha="right", va="bottom", fontsize=7.5, color=t["muted"], weight="bold")
    if show_max:
        ax.text(col_ext, -0.82, "MAX", transform=blended, ha="right", va="bottom", fontsize=7.5, color=t["muted"], weight="bold")
    elif context_fn:
        ax.text(col_ext, -0.82, "RATE", transform=blended, ha="right", va="bottom", fontsize=7.5, color=t["muted"], weight="bold")

    for y, heading in sections:
        ax.add_patch(mpatches.Rectangle((0.022, y - 0.44), 0.958, 0.88, transform=blended,
                                        facecolor=t["card_alt"], edgecolor="none", clip_on=False, zorder=0))
        ax.text(x_sec, y, heading, transform=blended, ha="left", va="center", fontsize=9.1, color=t["ink"], weight="bold")

    stripe_idx = 0
    for y, row in enumerate(rows):
        if row is None:
            stripe_idx = 0
            continue
        client, series, highlighted = row
        color = t["colors"].get(client[0], t["muted"])
        if stripe_idx % 2 == 1:
            ax.add_patch(mpatches.Rectangle((0.022, y - 0.48), 0.958, 0.96, transform=blended,
                                            facecolor=t["bg"], edgecolor="none", clip_on=False, zorder=0))
        stripe_idx += 1
        lbl = show_version(client)
        txt = ax.text(x_lbl, y, lbl, transform=blended, ha="left", va="center", fontsize=8.5,
                      color=t["ink"] if highlighted else t["text"], weight="bold" if highlighted else "normal")
        if "\n" in lbl:
            txt.set_linespacing(0.88)
        ax.scatter(x_dot, y, transform=blended, color=color, s=22, clip_on=False, zorder=5)
        ax.plot([0.022, 0.980], [y + 0.5, y + 0.5], transform=blended, color=t["grid"], linewidth=0.5, clip_on=False, zorder=1)
        med_text, iqr_text, extra_text = "—", "—", "—"
        if series:
            center, low, high = spread(series)
            offsets = [y + ((i % 5) - 2) * 0.068 for i in range(len(series))]
            ax.scatter(series, offsets, color=color, s=15, alpha=0.45, linewidth=0, zorder=3)
            ax.plot([low, high], [y, y], color=color, linewidth=3.2, solid_capstyle="round", alpha=0.90, zorder=4)
            marker = (
                "D" if client in native_clients
                else "s" if client == REFERENCE
                else "^" if client[0] in (NO_LOADED_LATENCY, TERMINAL_NO_LOADED_LATENCY)
                else "v" if client[1] == "firefox"
                else "o"
            )
            if highlighted:
                ax.scatter(center, y, s=125, facecolor="none", edgecolor=color, linewidth=1.4, marker=marker, zorder=5)
            ax.scatter(center, y, color=color, s=44, edgecolor=t["card"], linewidth=0.9, marker=marker, zorder=6)
            suffix = "%" if difference else ""
            med_text = fmt_num(center, digits, signed=difference) + suffix
            iqr_text = f"[{fmt_num(low, digits, signed=difference)}, {fmt_num(high, digits, signed=difference)}]"
            if show_max:
                extra_text = fmt_num(max(series), digits)
            elif context_fn:
                extra_text = context_fn(client)
        ax.text(col_med, y, med_text, transform=blended, ha="right", va="center", fontsize=8.9,
                family="DejaVu Sans Mono", color=t["ink"] if highlighted else t["text"], weight="bold" if highlighted else "normal")
        ax.text(col_iqr, y, iqr_text, transform=blended, ha="right", va="center", fontsize=7.8,
                family="DejaVu Sans Mono", color=t["muted"])
        if has_third:
            ax.text(col_ext, y, extra_text, transform=blended, ha="right", va="center", fontsize=7.8,
                    family="DejaVu Sans Mono", color=t["muted"])

    highlight_desc = {"closest": "closest to 0%", "highest": "highest median", "lowest": "lowest median"}[preference]
    sub = f"Dots: {vm_count} runner VMs  ·  Bar: middle 50% (IQR)  ·  Ring & bold: {highlight_desc} per group"
    if difference:
        sub += "  ·  Shaded band: ±1%"
    if subtitle_extra:
        sub += f"  ·  {subtitle_extra}"
    fig.text(0.022, 1 - 0.14 / height, f"GITHUB RUNNER BENCHMARK  ·  {report_date}  ·  {vm_count} VMs",
             color=t["muted"], fontsize=7.8, family="DejaVu Sans Mono", weight="bold", va="top")
    fig.text(0.022, 1 - 0.34 / height, title, color=t["ink"], fontsize=14.8, weight="bold", va="top")
    fig.text(0.022, 1 - 0.65 / height, sub, color=t["muted"], fontsize=8.1, va="top")
    fig.add_artist(plt.Line2D([0.022, 0.978], [1 - 0.88 / height, 1 - 0.88 / height],
                              transform=fig.transFigure, color=t["grid"], linewidth=0.9))
    fig.savefig(out_path, dpi=185, facecolor=t["card"], bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Auto-Extending 8-Panel Historic Trends Bento (Dark + Light)
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
        return {
            "date": date_str, "run_id": run_id, "pins": prov["pins"],
            "runs": meas["runs"], "jobs": len(prov.get("jobs", [])),
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
    if not per_job:
        return None
    return spread([median(vs) for vs in per_job.values()])


def render_historic_trends(results_root, out_stem):
    """Scan all published CI runs in results/*-ci-run-* and render Dark + Light 8-panel Bento trends."""
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
    x_labels, version_markers = [], []
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
            sub_lbl = gm_ver if not suffix_line else f"{gm_ver} #{date_seen[e['date']]}"
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

    max_ticks = 9
    if len(entries) <= max_ticks:
        tick_idxs = list(range(len(entries)))
    else:
        step = max(1, math.ceil(len(entries) / max_ticks))
        tick_idxs = sorted(set(list(range(0, len(entries), step)) + [len(entries) - 1]))

    first_d = datetime.fromisoformat(entries[0]["date"]).strftime("%d.%m.%Y")
    last_d = datetime.fromisoformat(entries[-1]["date"]).strftime("%d.%m.%Y")

    for theme in ("dark", "light"):
        fig, t = _new_bento_fig(12.6, 14.4, theme)
        _draw_banner(
            fig,
            f"HISTORIC BENCHMARK TRENDS  ·  {len(entries)} PUBLISHED CI CAMPAIGNS ({first_d} – {last_d})",
            "Performance, Accuracy & Server Resource Trends Over Time",
            "Points: VM median · Ribbons: VM IQR · Dotted lines: GM releases · Auto-extended each run",
            t,
            top_y=0.988,
        )

        panels = [
            ("1. Unshaped Download · Chrome", "Gbit/s", UNCAPPED, dl_gbps, [
                ("Graphite Meter", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("LibreSpeed PHP", "librespeed", "chrome", t["family"]["ls"], "^", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
            ], False, False),
            ("2. Unshaped Upload · Chrome", "Gbit/s", UNCAPPED, ul_gbps, [
                ("Graphite Meter", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
                ("LibreSpeed Go", "librespeed-go", "chrome", t["family"]["lsg"], "^", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
            ], False, False),
            ("3. Unshaped Upload · Native Clients", "Gbit/s", UNCAPPED, ul_gbps, [
                ("GM Terminal", "graphite-meter-client", None, t["family"]["gm1"], "o", "-"),
                ("iperf3 (ref)", "iperf3", None, t["family"]["ip"], "s", "--"),
                ("LibreSpeed CLI", "librespeed-cli", None, t["family"]["ls"], "^", "-"),
            ], False, False),
            ("4. 10 Gbit/s Upload · Chrome", "Gbit/s", FAST, ul_gbps, [
                ("Graphite Meter", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
                ("LibreSpeed Go", "librespeed-go", "chrome", t["family"]["lsg"], "^", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
            ], False, False),
            ("5. 1 Gbit/s Upload Agreement vs iperf3", "% diff", PLAIN, None, [
                ("GM Browser (Chr)", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("GM Browser (FF)", "graphite-meter", "firefox", t["family"]["gm2"], "v", "--"),
                ("OpenSpeedTest (Chr)", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
                ("LibreSpeed PHP (FF)", "librespeed", "firefox", t["family"]["ls"], "^", "--"),
                ("GM Terminal", "graphite-meter-client", None, t["ink"], "s", ":"),
            ], False, True),
            ("6. Server Download CPU · 1 Gbit/s", "CPU s/GB", PLAIN, srv_cpu("down"), [
                ("GM Browser (Chr)", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("GM Terminal", "graphite-meter-client", None, t["family"]["gm2"], "D", "--"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "v", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("LibreSpeed CLI", "librespeed-cli", None, t["family"]["ls"], "^", "--"),
                ("iperf3 (ref)", "iperf3", None, t["family"]["ip"], "P", ":"),
            ], True, False),
            ("7. Server Upload CPU · 1 Gbit/s", "CPU s/GB", PLAIN, srv_cpu("up"), [
                ("GM Terminal", "graphite-meter-client", None, t["family"]["gm1"], "D", "--"),
                ("GM Browser (Chr)", "graphite-meter", "chrome", t["family"]["gm2"], "o", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "v", "-"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("LibreSpeed CLI", "librespeed-cli", None, t["family"]["ls"], "^", "--"),
                ("iperf3 (ref)", "iperf3", None, t["family"]["ip"], "P", ":"),
            ], True, False),
            ("8. Peak Server Memory · 1 Gbit/s", "MB", PLAIN, mem_mb, [
                ("GM Browser (Chr)", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("GM Terminal", "graphite-meter-client", None, t["family"]["gm2"], "D", "--"),
                ("LibreSpeed Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("OpenSpeedTest", "openspeedtest", "chrome", t["family"]["ost"], "v", "-"),
                ("LibreSpeed Go", "librespeed-go", "chrome", t["family"]["lsg"], "^", "-"),
                ("LibreSpeed PHP", "librespeed", "chrome", t["family"]["ls"], "X", "-"),
                ("iperf3 (ref)", "iperf3", None, t["family"]["ip"], "P", ":"),
            ], False, False),
        ]

        # 4 rows x 2 columns of Bento cards
        col_xs = [0.018, 0.506]
        card_w = 0.476
        row_h = 0.220
        row_gap = 0.014
        top_start = 0.942

        for idx, (ptitle, ylabel, scen, fn, series_spec, phase_note, is_signed) in enumerate(panels):
            r_idx = idx // 2
            c_idx = idx % 2
            cx = col_xs[c_idx]
            cy = top_start - (r_idx + 1) * row_h - r_idx * row_gap
            sub_hint = "closer to 0% = tighter" if is_signed else ("lower = better" if ylabel in ("CPU s/GB", "MB") else "higher = faster")
            _draw_card(fig, (cx, cy, card_w, row_h), t, title=ptitle, subtitle=f"{ylabel} · {sub_hint}")
            ax = fig.add_axes([cx + 0.048, cy + 0.034, card_w - 0.062, row_h - 0.076])
            _style_bento_ax(ax, t, "y")
            ax.grid(axis="x", color=t["grid"], linewidth=0.5, alpha=0.5, zorder=0)
            if is_signed:
                ax.axhspan(-1.0, 1.0, color=t["good_band"], alpha=0.75, zorder=0)
                ax.axhline(0.0, color=t["good"], linewidth=1.0, zorder=1)
            for v_idx, _ in version_markers:
                if v_idx > 0:
                    ax.axvline(v_idx, color=t["divider"], linestyle=":", linewidth=0.9, zorder=1)
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
                ax.plot(px, py, color=col, linestyle=ls, linewidth=2.0, marker=mk, markersize=4.8,
                        markeredgecolor=t["card"], markeredgewidth=0.7, label=slbl, zorder=4)
                if is_signed:
                    txt = f"{py[-1]:+.1f}%" if abs(round(py[-1], 1)) > 0 else "0.0%"
                elif ylabel == "CPU s/GB":
                    txt = f"{py[-1]:.2f}"
                else:
                    txt = f"{py[-1]:.1f}"
                end_labels.append((py[-1], txt, col))

            if is_signed:
                y_lo = min([-2.0, *(all_y or [-2.0])]) * 1.15
                y_hi = max([2.0, *(all_y or [2.0])]) + (abs(y_lo) * 0.48)
            else:
                y_lo = 0.0
                y_hi = max(all_y) * 1.26 if all_y else 10.0
            ax.set_ylim(y_lo, y_hi)
            y_span = y_hi - y_lo
            placed = _deconflict_labels(end_labels, y_lo + y_span * 0.05, y_hi - y_span * 0.05, y_span * 0.088)
            for orig_y, adj_y, txt, col in placed:
                if abs(adj_y - orig_y) > y_span * 0.015:
                    ax.plot([last_x + 0.08, last_x + 0.24], [orig_y, adj_y], color=col, alpha=0.45, linewidth=0.75, zorder=3)
                ax.text(last_x + 0.26, adj_y, txt, va="center", ha="left", fontsize=7.4,
                        family="DejaVu Sans Mono", color=col, weight="bold")

            if phase_note and first_valid and first_valid > 0:
                ax.axvspan(-0.35, first_valid - 0.35, color=t["card_alt"], alpha=0.88, zorder=1)
                ax.text((first_valid - 0.7) / 2, 0.44, "Phase CPU\ntracking\nadded\nNov 2026",
                        transform=ax.get_xaxis_transform(), ha="center", va="center",
                        fontsize=7.3, color=t["faint"], style="italic")

            ax.set_xticks(tick_idxs)
            ax.set_xticklabels([x_labels[i] for i in tick_idxs], fontsize=7.2, color=t["muted"])
            ax.set_xlim(-0.35, len(entries) - 1 + max(0.95, 0.16 * len(entries)))
            leg = ax.legend(loc="upper left", frameon=True, facecolor=t["card"], framealpha=0.92,
                            edgecolor=t["border"], fontsize=6.7, ncol=2 if len(series_spec) > 3 else 1,
                            handlelength=1.3, borderpad=0.32, labelspacing=0.22)
            for text in leg.get_texts():
                text.set_color(t["text"])

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)
    return entries
