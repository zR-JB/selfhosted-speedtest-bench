"""Unified Dark/Light dashboards and auto-extending historic trends for selfhosted-speedtest-bench.

Sized at 9.8 inches wide (~850 px GitHub README width) with >= 8.6 pt typography (~11.5+ CSS px),
high-contrast dark/light palettes, explicit per-panel legends using matching visual glyphs,
consistent tool rosters, paired VM differences, and zero fabricated zeros for missing data.
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
from matplotlib.ticker import FuncFormatter

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
        "text": "#d0d7de",
        "muted": "#9aa4b2",
        "faint": "#7d8590",
        "grid": "#242c38",
        "divider": "#343d4b",
        "good_band": "#153d29",
        "good": "#3fb950",
        "warn": "#e3b341",
        "bad": "#f85149",
        "dl": "#58a6ff",
        "dl_txt": "#79c0ff",
        "ul": "#f0883e",
        "ul_txt": "#ffa657",
        "shaper": "#94a3b8",
        "rx": "#3fb950",
        "aws": "#f0883e",
        "azure": "#58a6ff",
        "other": "#bc8cff",
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
            "HTTP/3": "#e3b341",
            "WebTransport": "#bc8cff",
            "iperf3": "#94a3b8",
        },
    },
    "light": {
        "bg": "#f6f8fa",
        "card": "#ffffff",
        "card_alt": "#f3f6fa",
        "border": "#cfd7df",
        "ink": "#1f2328",
        "text": "#2c3540",
        "muted": "#525c68",
        "faint": "#6e7781",
        "grid": "#e5e9f0",
        "divider": "#cbd5e1",
        "good_band": "#e6f6ec",
        "good": "#1a7f37",
        "warn": "#9a6700",
        "bad": "#cf222e",
        "dl": "#1d4ed8",
        "dl_txt": "#1e40af",
        "ul": "#c2410c",
        "ul_txt": "#9a3412",   # >= 6.4:1 contrast against white
        "shaper": "#475569",
        "rx": "#0f766e",
        "aws": "#c2410c",
        "azure": "#1d4ed8",
        "other": "#7c3aed",
        "family": {
            "gm1": "#1d4ed8",
            "gm2": "#0e7490",
            "ip": "#475569",
            "ls": "#0f766e",
            "lsg": "#c2410c",
            "lsr": "#6d28d9",
            "ost": "#be185d",
        },
        "proto": {
            "HTTP/1.1": "#1d4ed8",
            "HTTP/2": "#0f766e",
            "HTTP/3": "#b45309",
            "WebTransport": "#6d28d9",
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
    if not values:
        return None
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
    fig.text(0.020, 1.0 - 0.13 / fh, kicker, color=t["muted"], fontsize=8.8,
             family="DejaVu Sans Mono", weight="bold", va="top", ha="left", zorder=5)
    fig.text(0.020, 1.0 - 0.36 / fh, title, color=t["ink"], fontsize=14.8,
             weight="bold", va="top", ha="left", zorder=5)


def _draw_legend_glyph(fig, x, y, col, kind, t, fh):
    """Draw a visual legend glyph that matches the exact mark used on the axes."""
    sw_w = 0.014
    sw_h = 0.095 / fh
    if kind == "bar":
        fig.patches.append(mpatches.FancyBboxPatch(
            (x, y - sw_h * 0.5), sw_w, sw_h,
            boxstyle="round,pad=0,rounding_size=0.002",
            transform=fig.transFigure, facecolor=col, edgecolor="none", zorder=5,
        ))
    elif kind == "outline":
        fig.patches.append(mpatches.FancyBboxPatch(
            (x, y - sw_h * 0.5), sw_w, sw_h,
            boxstyle="round,pad=0,rounding_size=0.002",
            transform=fig.transFigure, facecolor=t["card_alt"], edgecolor=col, linewidth=1.35, zorder=5,
        ))
    elif kind == "dashed":
        fig.add_artist(plt.Line2D([x, x + sw_w * 1.25], [y, y],
                                  transform=fig.transFigure, color=col, linewidth=1.5, linestyle="--", zorder=5))
        return sw_w * 1.25
    elif kind == "whisker":
        fig.add_artist(plt.Line2D([x, x + sw_w * 1.35], [y, y],
                                  transform=fig.transFigure, color=col, linewidth=2.2, solid_capstyle="round", zorder=5))
        fig.add_artist(plt.Line2D([x + sw_w * 0.675], [y], transform=fig.transFigure, marker="o",
                                  markersize=4.5, markerfacecolor=col, markeredgecolor=t["card"],
                                  markeredgewidth=0.7, linestyle="none", zorder=6))
        return sw_w * 1.35
    elif kind in ("dot", "diamond", "triangle"):
        mk = {"dot": "o", "diamond": "D", "triangle": "^"}[kind]
        fig.add_artist(plt.Line2D([x + sw_w * 0.5], [y], transform=fig.transFigure, marker=mk,
                                  markersize=5.6, markerfacecolor=col, markeredgecolor=t["card"],
                                  markeredgewidth=0.6, linestyle="none", zorder=6))
        return sw_w * 0.95
    elif kind == "band":
        fig.patches.append(mpatches.Rectangle(
            (x, y - sw_h * 0.65), sw_w * 1.2, sw_h * 1.3,
            transform=fig.transFigure, facecolor=t["good_band"], edgecolor=col, linewidth=0.8, zorder=5,
        ))
        fig.add_artist(plt.Line2D([x + sw_w * 0.6, x + sw_w * 0.6], [y - sw_h * 0.65, y + sw_h * 0.65],
                                  transform=fig.transFigure, color=col, linewidth=1.1, zorder=6))
        return sw_w * 1.2
    return sw_w


def _draw_card(fig, x_frac, y_in, w_frac, h_in, t, *, title, direction=None, legend=None, footer=None):
    """Draw a Bento card using inch-accurate vertical spacing and optional multi-row glyph legend."""
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
        fig.text(x_frac + w_frac - 0.016, y + h - 0.16 / fh, direction, color=t["muted"], fontsize=8.5,
                 family="DejaVu Sans Mono", weight="bold", va="top", ha="right", zorder=5)
    legend_rows = 0
    if legend:
        legend_rows = 1
        lx = x_frac + 0.016
        ly = y + h - 0.44 / fh
        max_x = x_frac + w_frac - 0.020
        for item in legend:
            lbl, col = item[0], item[1]
            kind = item[2] if len(item) > 2 else "bar"
            est_w = 0.026 + len(lbl) * 0.0074
            if lx > x_frac + 0.018 and lx + est_w > max_x:
                lx = x_frac + 0.016
                ly -= 0.22 / fh
                legend_rows += 1
            gw = _draw_legend_glyph(fig, lx, ly, col, kind, t, fh)
            fig.text(lx + gw + 0.006, ly, lbl, color=t["text"], fontsize=8.5,
                     va="center", ha="left", zorder=5)
            lx += gw + 0.020 + len(lbl) * 0.0074
    if footer:
        fy = y + 0.28 / fh
        fig.add_artist(plt.Line2D([x_frac + 0.015, x_frac + w_frac - 0.015], [fy + 0.09 / fh, fy + 0.09 / fh],
                                  transform=fig.transFigure, color=t["border"], linewidth=0.8, zorder=4))
        fig.text(x_frac + 0.016, fy + 0.01 / fh, footer, color=t["muted"], fontsize=8.3,
                 va="top", ha="left", zorder=5)
    return legend_rows


def _add_ax(fig, x_frac, y_in, w_frac, h_in, t, grid_axis="x"):
    fh = fig.get_figheight()
    ax = fig.add_axes([x_frac, y_in / fh, w_frac, h_in / fh])
    ax.set_zorder(2)
    ax.set_facecolor(t["card"])
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=t["grid"], linewidth=0.75, linestyle=(0, (2, 2)))
    ax.tick_params(colors=t["muted"], labelsize=8.7, length=0, pad=5)
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
# 1. Throughput Dashboard (Complete Default Roster + VM IQR Whiskers)
# ---------------------------------------------------------------------------

def render_throughput_chart(out_stem, *, report_date, vm_count, measure, rate):
    roster = [
        ("Native & TCP Reference", [
            ("GM Terminal", ("graphite-meter-client", None)),
            ("LibreSpeed CLI", ("librespeed-cli", None)),
            ("iperf3 (4 TCP ref)", REFERENCE),
        ]),
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
    ]

    def build_rows(scenario):
        rows = []
        for sec, items in roster:
            rows.append(("sec", sec, None, None))
            for lbl, cl in items:
                ds = spread(measure(scenario, cl, rate(DOWNLOAD, 1000)))
                us = spread(measure(scenario, cl, rate(UPLOAD, 1000)))
                rows.append(("row", lbl, ds, us))
        return rows

    rows_10g = build_rows(FAST)
    rows_un = build_rows(UNCAPPED)

    for theme in ("dark", "light"):
        fh = 13.0
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"THROUGHPUT & VM SPREAD  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "10 Gbit/s Shaped & Unshaped Throughput (All Default Clients)", t)

        def draw_panel(c_y, c_h, title, rows, ceiling, digits, footer, legend):
            _draw_card(fig, 0.020, c_y, 0.960, c_h, t, title=title,
                       direction="Higher is faster →", legend=legend, footer=footer)
            ax = _add_ax(fig, 0.215, c_y + 0.84, 0.470, c_h - 1.62, t, "x")
            bl = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax.transData)
            vals = []
            for kind, _, ds, us in rows:
                if kind == "row":
                    if ds:
                        vals.append(ds[2])
                    if us:
                        vals.append(us[2])
            mx = max([*(vals or [10.0]), ceiling or 0.0])
            ax.text(0.818, -0.78, "DOWN / UP", transform=bl, ha="right", va="bottom",
                    fontsize=8.1, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
            ax.text(0.964, -0.78, "UL IQR [p25, p75]", transform=bl, ha="right", va="bottom",
                    fontsize=8.1, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
            # Identify per-section median leaders neutrally so the winning median in each group pops at a glance
            sec_best_dl, sec_best_ul = {}, {}
            cur_sec = None
            for kind, lbl, ds, us in rows:
                if kind == "sec":
                    cur_sec = lbl
                    continue
                if ds is not None:
                    sec_best_dl[cur_sec] = max(sec_best_dl.get(cur_sec, -1.0), round(ds[0], digits))
                if us is not None:
                    sec_best_ul[cur_sec] = max(sec_best_ul.get(cur_sec, -1.0), round(us[0], digits))

            bar_h = 0.34
            cur_sec = None
            for i, (kind, lbl, ds, us) in enumerate(rows):
                if kind == "sec":
                    cur_sec = lbl
                    if i > 0:
                        ax.axhline(i - 0.52, color=t["divider"], linewidth=0.75, zorder=1)
                    ax.text(0.036, i, lbl, transform=bl, va="center", ha="left",
                            fontsize=9.1, weight="bold", color=t["ink"])
                    continue
                is_best_d = ds is not None and round(ds[0], digits) == sec_best_dl.get(cur_sec)
                is_best_u = us is not None and round(us[0], digits) == sec_best_ul.get(cur_sec)
                ax.text(0.048, i, lbl, transform=bl, va="center", ha="left", fontsize=8.8,
                        color=t["ink"] if (is_best_d or is_best_u) else t["text"],
                        weight="bold" if (is_best_d and is_best_u) else "normal")
                if ds is not None:
                    ax.barh(i - bar_h / 2, ds[0], height=bar_h, color=t["dl"], alpha=0.92, zorder=3)
                    if ds[2] > ds[1]:
                        ax.plot([ds[1], ds[2]], [i - bar_h / 2, i - bar_h / 2], color=t["muted"],
                                alpha=0.72, linewidth=1.15, marker="|", markersize=4.2, markeredgewidth=1.0, zorder=5)
                if us is not None:
                    ax.barh(i + bar_h / 2, us[0], height=bar_h, color=t["ul"], alpha=0.90, zorder=3)
                    if us[2] > us[1]:
                        ax.plot([us[1], us[2]], [i + bar_h / 2, i + bar_h / 2], color=t["muted"],
                                alpha=0.72, linewidth=1.15, marker="|", markersize=4.2, markeredgewidth=1.0, zorder=5)
                d_txt = fmt_num(ds[0], digits) if ds else "—"
                u_txt = fmt_num(us[0], digits) if us else "—"
                ax.text(0.752, i, f"{d_txt:>5}", transform=bl, ha="right", va="center",
                        fontsize=8.5, family="DejaVu Sans Mono",
                        color=t["dl_txt"] if is_best_d else t["text"], weight="bold" if is_best_d else "normal")
                ax.text(0.768, i, "/", transform=bl, ha="center", va="center",
                        fontsize=8.3, family="DejaVu Sans Mono", color=t["faint"])
                ax.text(0.822, i, f"{u_txt:>5}", transform=bl, ha="right", va="center",
                        fontsize=8.5, family="DejaVu Sans Mono",
                        color=t["ul_txt"] if is_best_u else t["text"], weight="bold" if is_best_u else "normal")
                iqr_txt = f"[{fmt_num(us[1], digits)}, {fmt_num(us[2], digits)}]" if us else "—"
                ax.text(0.964, i, iqr_txt, transform=bl, ha="right", va="center",
                        fontsize=8.1, family="DejaVu Sans Mono", color=t["muted"])
            if ceiling is not None:
                ax.axvline(ceiling, color=t["muted"], linestyle="--", linewidth=1.25, zorder=4)
            ax.set_yticks([])
            ax.set_ylim(len(rows) - 0.35, -0.75)
            ax.set_xlim(0, max(mx * 1.08, (ceiling or 0.0) * 1.07))
            ax.set_xlabel("Throughput (Gbit/s)", fontsize=8.8, color=t["muted"], labelpad=3)

        c1_h = 5.90
        draw_panel(
            fh - 0.78 - c1_h, c1_h,
            "1. 10 Gbit/s Shaped Link (2 ms RTT, offloads on)",
            rows_10g, 9.56, 2,
            "Bars = median across VMs (bold = group leader); thin capped ticks = middle 50% (IQR).",
            [("Download", t["dl"], "bar"), ("Upload", t["ul"], "bar"),
             ("VM middle 50% (IQR)", t["muted"], "whisker"),
             ("9.56 Gbit/s modeled TCP ceiling", t["muted"], "dashed")],
        )
        c2_h = 5.90
        draw_panel(
            0.22, c2_h,
            "2. Unshaped Virtual Link (No Rate Limit, 1 Server vCPU / 2 Client vCPUs)",
            rows_un, None, 1,
            "Observed single-test throughput on host-local virtual link (median across VMs; bold = group leader; ticks = VM IQR).",
            [("Download", t["dl"], "bar"), ("Upload", t["ul"], "bar"),
             ("VM middle 50% (IQR)", t["muted"], "whisker")],
        )

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Accuracy, Hard Links, FIFO Counter Comparison & Paired Loaded RTT
# ---------------------------------------------------------------------------

def render_accuracy_chart(
    out_stem, *, report_date, vm_count, measure, paired, rate,
    shaper_upload, server_rx, fifo_latency, loaded_delta, above_reference,
):
    for theme in ("dark", "light"):
        fh = 14.4
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"ACCURACY, HARD LINKS & LATENCY  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "1 Gbit/s Agreement, Loss/High-RTT Paths, FIFO Counters & Loaded RTT", t)

        # Card 1: 1 Gbit/s Upload Agreement vs Same-Pass iperf3
        c1_h = 5.05
        c1_y = fh - 0.78 - c1_h
        _draw_card(
            fig, 0.020, c1_y, 0.960, c1_h, t,
            title="1. 1 Gbit/s Upload Agreement vs Same-Pass iperf3 (Default Clients)",
            direction="← Closer to 0% is tighter →",
            legend=[("±1% display guide", t["good"], "band"),
                    ("VM median", t["muted"], "dot"),
                    ("Campaign median + IQR", t["muted"], "whisker")],
            footer="Paired vs sequential iperf3 on the same VM and pass; differences include both reporting and achieved throughput.",
        )
        ax1 = _add_ax(fig, 0.255, c1_y + 0.86, 0.475, c1_h - 1.62, t, "x")
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
        ax1.axvspan(-1.0, 1.0, color=t["good_band"], alpha=0.88 if theme == "dark" else 0.75, zorder=0)
        ax1.axvline(0.0, color=t["good"], linewidth=1.2, zorder=2)
        bl1 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax1.transData)
        ax1.text(0.832, -0.78, "MEDIAN", transform=bl1, ha="right", va="bottom",
                 fontsize=8.1, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        ax1.text(0.962, -0.78, "IQR [p25, p75]", transform=bl1, ha="right", va="bottom",
                 fontsize=8.1, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        for i, (kind, lbl, cl, vs) in enumerate(agree_rows):
            if kind == "sec":
                if i > 0:
                    ax1.axhline(i - 0.50, color=t["divider"], linewidth=0.7, zorder=1)
                ax1.text(0.036, i, lbl, transform=bl1, va="center", ha="left",
                         fontsize=9.1, weight="bold", color=t["ink"])
                continue
            col = t["family"][_family_of(cl[0])]
            ax1.scatter(0.044, i, transform=bl1, color=col, s=26, clip_on=False, zorder=5)
            ax1.text(0.058, i, lbl, transform=bl1, va="center", ha="left", fontsize=8.8, color=t["text"])
            if vs:
                med, lo, hi = spread(vs)
                offs = [i + ((k % 5) - 2) * 0.065 for k in range(len(vs))]
                ax1.scatter(vs, offs, color=col, s=18, alpha=0.62 if theme == "dark" else 0.48, linewidth=0, zorder=3)
                ax1.plot([lo, hi], [i, i], color=col, linewidth=3.3, solid_capstyle="round", zorder=4)
                ax1.scatter(med, i, color=col, s=48, edgecolor=t["card"], linewidth=1.0, zorder=5)
                ax1.text(0.832, i, f"{fmt_num(med, 1, True)}%", transform=bl1, ha="right", va="center",
                         fontsize=8.6, family="DejaVu Sans Mono", color=t["ink"])
                ax1.text(0.962, i, f"[{fmt_num(lo, 1)}, {fmt_num(hi, 1)}]", transform=bl1, ha="right", va="center",
                         fontsize=8.2, family="DejaVu Sans Mono", color=t["muted"])
        ax1.set_yticks([])
        ax1.set_ylim(len(agree_rows) - 0.3, -0.78)
        ax1.set_xlim(min([-2.0, *(all_a or [-2.0])]) - 0.8, max([2.0, *(all_a or [2.0])]) + 0.8)
        ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+g}%" if v else "0%"))
        ax1.set_xlabel("Difference from same-pass iperf3 (%)", fontsize=8.7, color=t["muted"], labelpad=3)

        # Card 2 & 3: Complete Chrome & Native Roster on 1% Loss & 160 ms High-BDP
        c2_h = 4.10
        c2_y = c1_y - 0.20 - c2_h
        hard_items = [
            ("GM · Chr", ("graphite-meter", "chrome")),
            ("OST · Chr", ("openspeedtest", "chrome")),
            ("LS Go · Chr", ("librespeed-go", "chrome")),
            ("LS Rust · Chr", ("librespeed-rust", "chrome")),
            ("LS PHP · Chr", ("librespeed", "chrome")),
            ("GM Terminal", ("graphite-meter-client", None)),
            ("LS CLI", ("librespeed-cli", None)),
            ("iperf3 (ref)", REFERENCE),
        ]
        for x_c, sc_id, ctitle, ceil_x, leg in [
            (0.020, LOSS, "2. 100M · 1% Loss (Chrome & Native)", None,
             [("Download", t["dl"], "bar"), ("Upload", t["ul"], "bar")]),
            (0.510, LONG, "3. 300M · 160ms RTT (Chrome & Native)", 286.9,
             [("Download", t["dl"], "bar"), ("Upload", t["ul"], "bar"),
              ("286.9M TCP model", t["muted"], "dashed")]),
        ]:
            _draw_card(fig, x_c, c2_y, 0.470, c2_h, t, title=ctitle, direction="Higher →", legend=leg)
            axc = _add_ax(fig, x_c + 0.135, c2_y + 0.54, 0.315, c2_h - 1.24, t, "x")
            data = []
            for lbl, cl in hard_items:
                dv = measure(sc_id, cl, rate(DOWNLOAD))
                uv = measure(sc_id, cl, rate(UPLOAD))
                if dv or uv:
                    data.append((lbl, median(dv) if dv else None, median(uv) if uv else None))
            yc = np.arange(len(data))
            all_h = [v for _, dv, uv in data for v in (dv, uv) if v is not None]
            mx = max([*(all_h or [1.0]), ceil_x or 1.0])
            for i, (_, dv, uv) in enumerate(data):
                lb_box = dict(facecolor=t["card"], edgecolor="none", pad=0.5, alpha=0.85) if ceil_x else None
                if dv is not None:
                    axc.barh(i - 0.19, dv, height=0.34, color=t["dl"], alpha=0.90, zorder=3)
                    axc.text(dv + mx * 0.024, i - 0.19, f"{dv:.1f}", va="center", ha="left",
                             fontsize=8.3, family="DejaVu Sans Mono", color=t["dl_txt"], bbox=lb_box, zorder=5)
                if uv is not None:
                    axc.barh(i + 0.19, uv, height=0.34, color=t["ul"], alpha=0.88, zorder=3)
                    axc.text(uv + mx * 0.024, i + 0.19, f"{uv:.1f}", va="center", ha="left",
                             fontsize=8.3, family="DejaVu Sans Mono", color=t["ul_txt"], bbox=lb_box, zorder=5)
            if ceil_x:
                axc.axvline(ceil_x, color=t["muted"], linestyle="--", linewidth=1.1, zorder=1)
            axc.axhline(4.5, color=t["divider"], linestyle=":", linewidth=0.9)
            axc.set_yticks(yc)
            axc.set_yticklabels([x[0] for x in data], fontsize=8.6, color=t["text"])
            axc.invert_yaxis()
            axc.set_xlim(0, mx * 1.32)
            axc.set_xlabel("Throughput (Mbit/s)", fontsize=8.5, color=t["muted"], labelpad=3)

        # Card 4 (Dot plot — NO clipped baseline bars!): 30 Mbit/s FIFO Upload Counters
        c3_h = 4.05
        c3_y = 0.20
        _draw_card(
            fig, 0.020, c3_y, 0.470, c3_h, t,
            title="4. 30M FIFO Upload Counters",
            direction="App closest to 28.7M",
            legend=[("App payload", t["dl"], "dot"), ("Shaper", t["shaper"], "diamond"),
                    ("Server RX", t["rx"], "triangle"), ("28.7M TCP max", t["muted"], "dashed")],
            footer="28.7M = TCP max; Shaper/RX include overhead. APP/RX · >ip3.",
        )
        ax4 = _add_ax(fig, 0.145, c3_y + 0.86, 0.240, c3_h - 1.72, t, "x")
        uc_items = [
            ("OST · Chr", ("openspeedtest", "chrome")),
            ("OST · FF", ("openspeedtest", "firefox")),
            ("LS PHP · Chr", ("librespeed", "chrome")),
            ("GM · Chr", ("graphite-meter", "chrome")),
            ("GM Term.", ("graphite-meter-client", None)),
            ("iperf3 (ref)", REFERENCE),
        ]
        uc_rows = []
        for lbl, row_cl in uc_items:
            av = measure(FIFO, row_cl, rate(UPLOAD))
            sv = measure(FIFO, row_cl, shaper_upload)
            rv = measure(FIFO, row_cl, server_rx)
            ab = above_reference(FIFO, row_cl)
            if av:
                uc_rows.append((lbl, row_cl, median(av), median(sv) if sv else None, median(rv) if rv else None, ab))
        y4 = np.arange(len(uc_rows))
        bl4 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax4.transData)
        ax4.axvline(28.69, color=t["muted"], linestyle="--", linewidth=1.2, zorder=2)
        ax4.text(0.474, -0.72, "APP/RX · >ip3", transform=bl4, ha="right", va="bottom",
                 fontsize=7.7, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        all_u = [28.69]
        for i, (_, row_cl, av, sv, rv, ab) in enumerate(uc_rows):
            all_u.append(av)
            if sv is not None:
                all_u.append(sv)
                ax4.scatter(sv, i + 0.14, color=t["shaper"], marker="D", s=34, edgecolor=t["card"], linewidth=0.6, zorder=4)
            if rv is not None:
                all_u.append(rv)
                ax4.scatter(rv, i - 0.14, color=t["rx"], marker="^", s=40, edgecolor=t["card"], linewidth=0.6, zorder=4)
            ax4.scatter(av, i, color=t["dl"], marker="o", s=48, edgecolor=t["card"], linewidth=0.8, zorder=5)
            ab_txt = "ref" if row_cl == REFERENCE else (f"{ab[0]}/{ab[1]}" if ab else "—")
            rx_txt = f"{rv:.1f}" if rv is not None else "—"
            ax4.text(0.474, i, f"{av:.1f}/{rx_txt} · {ab_txt}", transform=bl4, ha="right", va="center",
                     fontsize=7.9, family="DejaVu Sans Mono", color=t["ink"])
        ax4.set_yticks(y4)
        ax4.set_yticklabels([r[0] for r in uc_rows], fontsize=8.5, color=t["text"])
        ax4.set_ylim(len(uc_rows) - 0.35, -0.75)
        ax4.set_xlim(min(all_u) - 0.8, max(all_u) + 0.9)
        ax4.set_xlabel("Upload rate (Mbit/s)", fontsize=8.5, color=t["muted"], labelpad=3)

        # Card 5: Graphite Meter Paired Loaded RTT vs Idle ICMP + FIFO Queue Estimate
        lr5 = _draw_card(
            fig, 0.510, c3_y, 0.470, c3_h, t,
            title="5. GM Loaded RTT (FIFO)",
            direction="← Closer to 0 ms →",
            legend=[("Paired median + VM IQR", t["dl"], "whisker"),
                    ("0 = ICMP + FIFO queue", t["good"], "dashed")],
            footer="Paired per-run App − (Idle ICMP + median FIFO queue), in ms.",
        )
        top5 = 0.78 + 0.22 * max(0, lr5 - 1)
        ax5 = _add_ax(fig, 0.625, c3_y + 0.86, 0.195, c3_h - 0.86 - top5, t, "x")
        f_rows = []
        for lbl, cl, fld, ddir in [
            ("Chr · Down", ("graphite-meter", "chrome"), "loadedLatencyDownMs", "down"),
            ("Chr · Up", ("graphite-meter", "chrome"), "loadedLatencyUpMs", "up"),
            ("FF · Down", ("graphite-meter", "firefox"), "loadedLatencyDownMs", "down"),
            ("FF · Up", ("graphite-meter", "firefox"), "loadedLatencyUpMs", "up"),
            ("Term · Down", ("graphite-meter-client", None), "loadedLatencyDownMs", "down"),
            ("Term · Up", ("graphite-meter-client", None), "loadedLatencyUpMs", "up"),
        ]:
            dv = spread(measure(FIFO, cl, loaded_delta(fld, ddir)))
            if dv is not None:
                f_rows.append((lbl, dv))
        y5 = np.arange(len(f_rows))
        bl5 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax5.transData)
        ax5.axvline(0.0, color=t["good"], linestyle="--", linewidth=1.2, zorder=2)
        ax5.text(0.964, -0.72, "MEDIAN [IQR] ms", transform=bl5, ha="right", va="bottom",
                 fontsize=7.7, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        all_d = [0.0]
        for i, (_, (med, lo, hi)) in enumerate(f_rows):
            all_d.extend([lo, hi])
            ax5.plot([lo, hi], [i, i], color=t["dl"], linewidth=3.0, solid_capstyle="round", zorder=4)
            ax5.scatter(med, i, color=t["dl"], s=46, edgecolor=t["card"], linewidth=0.9, zorder=5)
            ax5.text(0.964, i, f"{med:+.1f} [{lo:+.1f}, {hi:+.1f}]", transform=bl5, ha="right", va="center",
                     fontsize=7.9, family="DejaVu Sans Mono", color=t["ink"])
        ax5.set_yticks(y5)
        ax5.set_yticklabels([r[0] for r in f_rows], fontsize=8.5, color=t["text"])
        ax5.set_ylim(len(f_rows) - 0.35, -0.75)
        ax5.set_xlim(min(all_d) - 4.0, max(all_d) + 4.0)
        ax5.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+g}" if v else "0"))
        ax5.set_xlabel("App − estimate (ms)", fontsize=8.5, color=t["muted"], labelpad=3)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Resource Efficiency Dashboard (Split 1G CPU, Complete Legends, Faceted RAM, Grouped Client CPU)
# ---------------------------------------------------------------------------

def render_resources_chart(out_stem, *, report_date, vm_count, groups, measure, phase_cpu, peak_memory, client_cpu, rate):
    def total_cpu_per_gb(row):
        cpu = row.get("serverCpuSeconds")
        link = sum(row.get("linkBytes", {}).values())
        return cpu * 1e9 / link if cpu is not None and link else None

    main_items = [
        ("GM · Chr", ("graphite-meter", "chrome")),
        ("OST · Chr", ("openspeedtest", "chrome")),
        ("LS Go · Chr", ("librespeed-go", "chrome")),
        ("LS Rust · Chr", ("librespeed-rust", "chrome")),
        ("LS PHP · Chr", ("librespeed", "chrome")),
        ("GM Terminal", ("graphite-meter-client", None)),
        ("LS CLI", ("librespeed-cli", None)),
        ("iperf3 (ref)", REFERENCE),
    ]

    r_un = []
    seen = set()
    for (sc, cl) in groups:
        if sc != UNCAPPED or cl in seen:
            continue
        seen.add(cl)
        tool, br = cl
        if tool in (NO_LOADED_LATENCY, TERMINAL_NO_LOADED_LATENCY):
            continue
        vs = measure(UNCAPPED, cl, total_cpu_per_gb)
        if vs:
            r_un.append((_short_label(tool, br), cl, median(vs)))
    r_un.sort(key=lambda x: x[2])

    def ram_facet(items, div, dig, unit):
        out = []
        for lbl, sc, cl in items:
            vs = measure(sc, cl, peak_memory)
            dv = measure(sc, cl, rate(DOWNLOAD, div))
            uv = measure(sc, cl, rate(UPLOAD, div))
            if vs:
                rt = f"{median(dv):.{dig}f}/{median(uv):.{dig}f}{unit}" if dv and uv else ""
                out.append((lbl, cl, median(vs), rt))
        out.sort(key=lambda x: x[2])
        return out

    ram_direct = ram_facet([
        ("GM · Chr", PLAIN, ("graphite-meter", "chrome")),
        ("GM Terminal", PLAIN, ("graphite-meter-client", None)),
        ("iperf3 (ref)", PLAIN, REFERENCE),
        ("LS Rust · Chr", PLAIN, ("librespeed-rust", "chrome")),
        ("OST · Chr", PLAIN, ("openspeedtest", "chrome")),
        ("LS Go · Chr", PLAIN, ("librespeed-go", "chrome")),
        ("LS CLI", PLAIN, ("librespeed-cli", None)),
        ("LS PHP · Chr", PLAIN, ("librespeed", "chrome")),
    ], 1, 0, "M")
    ram_tls = ram_facet([
        ("GM H3 · Chr", FAST, ("graphite-meter-h3", "chrome")),
        ("GM H2 · Chr", FAST, ("graphite-meter-h2", "chrome")),
        ("LS Go H2 · Chr", FAST, ("librespeed-go-h2", "chrome")),
        ("OST H2 · Chr", FAST, ("openspeedtest-h2", "chrome")),
    ], 1000, 1, "G")
    ram_proxy = ram_facet([
        ("GM + nginx", PROXY, ("graphite-meter", "chrome")),
        ("OST + nginx", PROXY, ("openspeedtest", "chrome")),
        ("LS PHP + nginx", PROXY, ("librespeed", "chrome")),
    ], 1, 0, "M")

    # Grouped horizontal client-side CPU roster (handles both 10 browser rows and 13 rows with native cgroup)
    client_groups_spec = [
        ("Chrome (browser process tree)", [
            ("Graphite Meter", ("graphite-meter", "chrome")),
            ("OpenSpeedTest", ("openspeedtest", "chrome")),
            ("LibreSpeed Go", ("librespeed-go", "chrome")),
            ("LibreSpeed Rust", ("librespeed-rust", "chrome")),
            ("LibreSpeed PHP", ("librespeed", "chrome")),
        ]),
        ("Firefox (browser process tree)", [
            ("Graphite Meter", ("graphite-meter", "firefox")),
            ("OpenSpeedTest", ("openspeedtest", "firefox")),
            ("LibreSpeed Go", ("librespeed-go", "firefox")),
            ("LibreSpeed Rust", ("librespeed-rust", "firefox")),
            ("LibreSpeed PHP", ("librespeed", "firefox")),
        ]),
        ("Native & Reference (container cgroup)", [
            ("GM Terminal", ("graphite-meter-client", None)),
            ("LibreSpeed CLI", ("librespeed-cli", None)),
            ("iperf3 (ref)", REFERENCE),
        ]),
    ]
    c_rows = []
    for sec, items in client_groups_spec:
        sec_items = []
        for lbl, cl in items:
            vs = measure(UNCAPPED, cl, client_cpu)
            if vs:
                sec_items.append((lbl, cl, spread(vs), len(vs)))
        if sec_items:
            sec_items.sort(key=lambda x: x[2][0])
            c_rows.append(("sec", sec, None, None, 0))
            for lbl, cl, sp, n in sec_items:
                c_rows.append(("row", lbl, cl, sp, n))

    for theme in ("dark", "light"):
        c4_h = 3.95 if len(c_rows) <= 13 else 4.75
        fh = 0.80 + 4.45 + 0.20 + 4.30 + 0.20 + c4_h + 0.22
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"RESOURCE EFFICIENCY  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "Server CPU per GB, Faceted Peak RAM & Client-Side CPU", t)

        fam_legend_full = [
            ("GM H1", t["family"]["gm1"], "bar"), ("GM H2/H3", t["family"]["gm2"], "bar"),
            ("iperf3", t["family"]["ip"], "bar"), ("LS PHP/CLI", t["family"]["ls"], "bar"),
            ("LS Go", t["family"]["lsg"], "bar"), ("LS Rust", t["family"]["lsr"], "bar"),
            ("OST", t["family"]["ost"], "bar"),
        ]

        # Row 1 Left: 1 Gbit/s Server CPU SPLIT into separate Download & Upload axes!
        c1_h = 4.45
        c1_y = fh - 0.80 - c1_h
        _draw_card(
            fig, 0.020, c1_y, 0.470, c1_h, t,
            title="1. 1 Gbit/s Server CPU (offloads off)",
            direction="← Lower s/GB",
            legend=[("Download s/GB (left)", t["dl"], "bar"), ("Upload s/GB (right)", t["ul"], "bar")],
            footer="Phase CPU / server-interface GB; brackets show achieved rate (Mbit/s).",
        )
        r1 = []
        for lbl, cl in main_items:
            dc = measure(PLAIN, cl, phase_cpu("down"))
            uc = measure(PLAIN, cl, phase_cpu("up"))
            dr = measure(PLAIN, cl, rate(DOWNLOAD))
            ur = measure(PLAIN, cl, rate(UPLOAD))
            if dc or uc:
                r1.append((lbl, median(dc) if dc else None, median(uc) if uc else None,
                           median(dr) if dr else None, median(ur) if ur else None))
        y1 = np.arange(len(r1))
        ax1d = _add_ax(fig, 0.130, c1_y + 0.84, 0.165, c1_h - 1.56, t, "x")
        ax1u = _add_ax(fig, 0.312, c1_y + 0.84, 0.165, c1_h - 1.56, t, "x")
        md = max([x[1] for x in r1 if x[1] is not None] + [0.5])
        mu = max([x[2] for x in r1 if x[2] is not None] + [5.0])
        for i, (_, dv, uv, dr, ur) in enumerate(r1):
            if dv is not None:
                ax1d.barh(i, dv, height=0.62, color=t["dl"], alpha=0.90, zorder=3)
                drt = f" ({dr:.0f}M)" if dr is not None else ""
                ax1d.text(dv + md * 0.03, i, f"{dv:.2f}{drt}", va="center", ha="left",
                          fontsize=7.8, family="DejaVu Sans Mono", color=t["dl_txt"])
            if uv is not None:
                ax1u.barh(i, uv, height=0.62, color=t["ul"], alpha=0.88, zorder=3)
                urt = f" ({ur:.0f}M)" if ur is not None else ""
                ax1u.text(uv + mu * 0.03, i, f"{uv:.2f}{urt}", va="center", ha="left",
                          fontsize=7.8, family="DejaVu Sans Mono", color=t["ul_txt"])
        for axp in (ax1d, ax1u):
            axp.axhline(4.5, color=t["divider"], linestyle=":", linewidth=0.9)
            axp.set_yticks(y1)
            axp.invert_yaxis()
        ax1d.set_yticklabels([x[0] for x in r1], fontsize=8.4, color=t["text"])
        ax1u.set_yticklabels([])
        ax1d.set_xlim(0, md * 1.98)
        ax1u.set_xlim(0, mu * 1.85)
        ax1d.set_xlabel("Down (s/GB)", fontsize=8.3, color=t["muted"], labelpad=3)
        ax1u.set_xlabel("Upload (s/GB)", fontsize=8.3, color=t["muted"], labelpad=3)

        # Row 1 Right: Unshaped Server CPU/GB with COMPLETE tool-family legend!
        leg_rows = _draw_card(
            fig, 0.510, c1_y, 0.470, c1_h, t,
            title="2. Unshaped Server CPU (offloads on)",
            direction="← Lower s/GB",
            legend=fam_legend_full,
            footer="Total server container CPU / shaper GB across both directions.",
        )
        top_pad = 0.72 + (0.22 if leg_rows > 1 else 0.0)
        ax2 = _add_ax(fig, 0.655, c1_y + 0.84, 0.305, c1_h - 0.84 - top_pad, t, "x")
        y2 = np.arange(len(r_un))
        m2 = max([r[2] for r in r_un] + [0.5])
        for i, (_, cl, val) in enumerate(r_un):
            col = t["family"][_family_of(cl[0])]
            ax2.barh(i, val, height=0.66, color=col, alpha=0.88, zorder=3)
            ax2.text(val + m2 * 0.025, i, f"{val:.3f} s/GB", va="center", ha="left",
                     fontsize=7.9, family="DejaVu Sans Mono", color=t["text"])
        ax2.set_yticks(y2)
        ax2.set_yticklabels([r[0].replace("LibreSpeed ", "LS ").replace("Graphite Meter", "GM") for r in r_un],
                            fontsize=8.0, color=t["text"])
        ax2.invert_yaxis()
        ax2.set_xlim(0, m2 * 1.45)
        ax2.set_xlabel("Total Server CPU / shaper GB (s/GB)", fontsize=8.3, color=t["muted"], labelpad=3)

        # Row 2: Faceted Peak Server Memory (Direct 1G | TLS H2/H3 10G | Behind nginx)
        c2_h = 4.30
        c2_y = c1_y - 0.20 - c2_h
        _draw_card(
            fig, 0.020, c2_y, 0.960, c2_h, t,
            title="3. Peak Server Memory by Deployment (With Achieved DL/UL Rate)",
            direction="← Lower MB",
            legend=fam_legend_full,
            footer="cgroup v2 memory.peak per run (MB). Behind-nginx values are the sum of server + nginx container peaks (not simultaneous).",
        )
        # Left facet: Direct 1 Gbit/s (0..95 MB zoomed!)
        ax3a = _add_ax(fig, 0.130, c2_y + 0.84, 0.365, c2_h - 1.72, t, "x")
        ax3a.set_title("Direct · 1 Gbit/s (offloads off)", fontsize=9.0, color=t["ink"], loc="left", pad=6)
        m3a = max([r[2] for r in ram_direct] + [20.0])
        for i, (_, cl, val, rt) in enumerate(ram_direct):
            ax3a.barh(i, val, height=0.64, color=t["family"][_family_of(cl[0])], alpha=0.88, zorder=3)
            ax3a.text(val + m3a * 0.025, i, f"{val:.1f} MB ({rt})", va="center", ha="left",
                      fontsize=8.1, family="DejaVu Sans Mono", color=t["text"])
        ax3a.set_yticks(np.arange(len(ram_direct)))
        ax3a.set_yticklabels([r[0] for r in ram_direct], fontsize=8.5, color=t["text"])
        ax3a.invert_yaxis()
        ax3a.set_xlim(0, m3a * 1.62)
        ax3a.set_xlabel("Peak RAM (MB)", fontsize=8.4, color=t["muted"], labelpad=3)

        # Right-top facet: TLS HTTP/2 & HTTP/3 on 10 Gbit/s
        ax3b = _add_ax(fig, 0.625, c2_y + 2.22, 0.335, 1.18, t, "x")
        ax3b.set_title("TLS HTTP/2 & HTTP/3 · 10 Gbit/s", fontsize=9.0, color=t["ink"], loc="left", pad=5)
        m3b = max([r[2] for r in ram_tls] + [50.0])
        for i, (_, cl, val, rt) in enumerate(ram_tls):
            ax3b.barh(i, val, height=0.62, color=t["family"][_family_of(cl[0])], alpha=0.88, zorder=3)
            ax3b.text(val + m3b * 0.025, i, f"{val:.1f} MB ({rt})", va="center", ha="left",
                      fontsize=8.1, family="DejaVu Sans Mono", color=t["text"])
        ax3b.set_yticks(np.arange(len(ram_tls)))
        ax3b.set_yticklabels([r[0] for r in ram_tls], fontsize=8.4, color=t["text"])
        ax3b.invert_yaxis()
        ax3b.set_xlim(0, m3b * 1.68)

        # Right-bottom facet: Behind nginx · 1 Gbit/s (sum of peaks)
        ax3c = _add_ax(fig, 0.625, c2_y + 0.84, 0.335, 0.96, t, "x")
        ax3c.set_title("Behind nginx · 1 Gbit/s (sum of 2 peaks)", fontsize=9.0, color=t["ink"], loc="left", pad=5)
        m3c = max([r[2] for r in ram_proxy] + [100.0])
        for i, (_, cl, val, rt) in enumerate(ram_proxy):
            ax3c.barh(i, val, height=0.60, color=t["family"][_family_of(cl[0])], alpha=0.88, zorder=3)
            ax3c.text(val + m3c * 0.025, i, f"{val:.1f} MB ({rt})", va="center", ha="left",
                      fontsize=8.1, family="DejaVu Sans Mono", color=t["text"])
        ax3c.set_yticks(np.arange(len(ram_proxy)))
        ax3c.set_yticklabels([r[0] for r in ram_proxy], fontsize=8.4, color=t["text"])
        ax3c.invert_yaxis()
        ax3c.set_xlim(0, m3c * 1.65)
        ax3c.set_xlabel("Sum of peaks (MB)", fontsize=8.4, color=t["muted"], labelpad=3)

        # Row 3: Grouped Horizontal Client-Side CPU Efficiency on Unshaped (scales cleanly to 10 or 13 rows!)
        c3_y = 0.22
        _draw_card(
            fig, 0.020, c3_y, 0.960, c4_h, t,
            title="4. Client-Side CPU Efficiency on Unshaped (Default Clients & iperf3)",
            direction="← Lower s/GB",
            legend=[("GM H1", t["family"]["gm1"], "bar"), ("iperf3", t["family"]["ip"], "bar"),
                    ("LS PHP/CLI", t["family"]["ls"], "bar"), ("LS Go", t["family"]["lsg"], "bar"),
                    ("LS Rust", t["family"]["lsr"], "bar"), ("OST", t["family"]["ost"], "bar"),
                    ("VM IQR", t["muted"], "whisker")],
            footer="CPU seconds per shaper GB over the full run (bold = lowest in group; ticks = VM IQR). Browser = process tree; native = cgroup.",
        )
        ax4 = _add_ax(fig, 0.250, c3_y + 0.84, 0.545, c4_h - 1.56, t, "x")
        bl4 = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax4.transData)
        m4 = max([r[3][2] for r in c_rows if r[0] == "row"] + [1.0])
        ax4.text(0.962, -0.78, "MEDIAN [IQR] (n)", transform=bl4, ha="right", va="bottom",
                 fontsize=8.0, family="DejaVu Sans Mono", color=t["muted"], weight="bold")
        sec_best_c = {}
        cur_sec = None
        for kind, lbl, _, sp, _ in c_rows:
            if kind == "sec":
                cur_sec = lbl
            elif sp is not None:
                sec_best_c[cur_sec] = min(sec_best_c.get(cur_sec, 1e9), round(sp[0], 2))
        cur_sec = None
        for i, (kind, lbl, cl, sp, n) in enumerate(c_rows):
            if kind == "sec":
                cur_sec = lbl
                if i > 0:
                    ax4.axhline(i - 0.50, color=t["divider"], linewidth=0.75, zorder=1)
                ax4.text(0.036, i, lbl, transform=bl4, va="center", ha="left",
                         fontsize=8.9, weight="bold", color=t["ink"])
                continue
            med, lo, hi = sp
            is_best = round(med, 2) == sec_best_c.get(cur_sec)
            col = t["family"][_family_of(cl[0])]
            ax4.text(0.050, i, lbl, transform=bl4, va="center", ha="left", fontsize=8.6,
                     color=t["ink"] if is_best else t["text"], weight="bold" if is_best else "normal")
            ax4.barh(i, med, height=0.58, color=col, alpha=0.90, zorder=3)
            if hi > lo:
                ax4.plot([lo, hi], [i, i], color=t["muted"], alpha=0.75, linewidth=1.25,
                         marker="|", markersize=4.5, markeredgewidth=1.0, zorder=5)
            ax4.text(0.962, i, f"{med:.2f} [{lo:.2f}, {hi:.2f}] (n={n})", transform=bl4, ha="right", va="center",
                     fontsize=8.2, family="DejaVu Sans Mono",
                     color=t["ink"] if is_best else t["text"], weight="bold" if is_best else "normal")
        ax4.set_yticks([])
        ax4.set_ylim(len(c_rows) - 0.35, -0.78)
        ax4.set_xlim(0, m4 * 1.12)
        ax4.set_xlabel("Client CPU / shaper GB (s/GB)", fontsize=8.6, color=t["muted"], labelpad=3)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Protocol & Transport Scaling (Complete Keys + Separate 10G & Unshaped Scales)
# ---------------------------------------------------------------------------

def render_transports_chart(out_stem, *, report_date, vm_count, measure, rate):
    for theme in ("dark", "light"):
        fh = 7.4
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"PROTOCOL & TRANSPORT SCALING  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "HTTP/1.1 vs HTTP/2 vs HTTP/3 vs WebTransport", t)

        cy, ch = 0.22, fh - 1.00
        full_leg = [
            ("HTTP/1.1", t["proto"]["HTTP/1.1"], "bar"),
            ("HTTP/2", t["proto"]["HTTP/2"], "bar"),
            ("HTTP/3", t["proto"]["HTTP/3"], "bar"),
            ("WebTransport", t["proto"]["WebTransport"], "bar"),
            ("iperf3 TCP", t["proto"]["iperf3"], "bar"),
            ("Solid = Down", t["ink"], "bar"),
            ("Outlined = Up", t["ink"], "outline"),
        ]

        # Left card: Chrome 10 Gbit/s
        lr1 = _draw_card(
            fig, 0.020, cy, 0.470, ch, t,
            title="1. Chrome · 10 Gbit/s Shaped",
            direction="Higher →",
            legend=[*full_leg, ("9.56G TCP model", t["muted"], "dashed")],
            footer="Dashed = 9.56 Gbit/s modeled TCP payload ceiling (for TCP rows).",
        )
        top1 = 0.72 + 0.22 * max(0, lr1 - 1)
        ax1 = _add_ax(fig, 0.190, cy + 0.84, 0.278, ch - 0.84 - top1, t, "x")
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
            dv = measure(FAST, cl, rate(DOWNLOAD, 1000))
            uv = measure(FAST, cl, rate(UPLOAD, 1000))
            if dv or uv:
                r1.append((lbl, proto, median(dv) if dv else None, median(uv) if uv else None))
        h = 0.34
        lbl_box = dict(facecolor=t["card"], edgecolor="none", pad=0.6, alpha=0.92)
        for i, (_, proto, dv, uv) in enumerate(r1):
            c = t["proto"][proto]
            if dv is not None:
                ax1.barh(i - h / 2, dv, height=h, color=c, alpha=0.92, zorder=3)
                ax1.text(dv + 0.16, i - h / 2, f"{dv:.2f}", va="center", ha="left",
                         fontsize=8.2, family="DejaVu Sans Mono", color=t["ink"], bbox=lbl_box, zorder=5)
            if uv is not None:
                ax1.barh(i + h / 2, uv, height=h, color=t["card_alt"], edgecolor=c, linewidth=1.35, zorder=3)
                ax1.text(uv + 0.16, i + h / 2, f"{uv:.2f}", va="center", ha="left",
                         fontsize=8.1, family="DejaVu Sans Mono", color=t["muted"], bbox=lbl_box, zorder=5)
        ax1.axvline(9.56, color=t["muted"], linestyle="--", linewidth=1.1, zorder=1)
        ax1.set_yticks(np.arange(len(r1)))
        ax1.set_yticklabels([r[0] for r in r1], fontsize=8.6, color=t["text"])
        ax1.invert_yaxis()
        ax1.set_xlim(0, 11.6)
        ax1.set_xlabel("Throughput (Gbit/s)", fontsize=8.6, color=t["muted"], labelpad=3)

        # Right card: Native Terminal split into TWO properly scaled facets (10G Shaped top, Unshaped bottom)
        lr2 = _draw_card(
            fig, 0.510, cy, 0.470, ch, t,
            title="2. Native Terminal · 10G & Unshaped",
            direction="Higher →",
            legend=[
                ("HTTP/1.1", t["proto"]["HTTP/1.1"], "bar"),
                ("HTTP/2", t["proto"]["HTTP/2"], "bar"),
                ("HTTP/3", t["proto"]["HTTP/3"], "bar"),
                ("iperf3 TCP", t["proto"]["iperf3"], "bar"),
                ("Solid = Down", t["ink"], "bar"),
                ("Outlined = Up", t["ink"], "outline"),
                ("9.56G TCP model", t["muted"], "dashed"),
            ],
            footer="Separate scales prevent 10 Gbit/s rows from compressing against unshaped.",
        )
        top2 = 0.88 + 0.22 * max(0, lr2 - 1)
        avail = ch - 0.84 - top2
        gap_f = 0.58
        h_f = (avail - gap_f) / 2.0

        def draw_native_facet(y_in, fh_in, sub_title, spec, ceil_x, digits):
            ax = _add_ax(fig, 0.655, y_in, 0.305, fh_in, t, "x")
            ax.set_title(sub_title, fontsize=8.9, color=t["ink"], loc="left", pad=5)
            rows = []
            for lbl, sc, cl, proto in spec:
                dv = measure(sc, cl, rate(DOWNLOAD, 1000))
                uv = measure(sc, cl, rate(UPLOAD, 1000))
                if dv or uv:
                    rows.append((lbl, proto, median(dv) if dv else None, median(uv) if uv else None))
            vals = [v for _, _, dv, uv in rows for v in (dv, uv) if v is not None]
            mx = max([*(vals or [10.0]), ceil_x or 0.0])
            tbox = dict(facecolor=t["card"], edgecolor="none", pad=0.6, alpha=0.92) if ceil_x else None
            for i, (_, proto, dv, uv) in enumerate(rows):
                c = t["proto"][proto]
                if dv is not None:
                    ax.barh(i - 0.17, dv, height=0.32, color=c, alpha=0.92, zorder=3)
                    ax.text(dv + mx * 0.024, i - 0.17, f"{dv:.{digits}f}", va="center", ha="left",
                            fontsize=8.2, family="DejaVu Sans Mono", color=t["ink"], bbox=tbox, zorder=5)
                if uv is not None:
                    ax.barh(i + 0.17, uv, height=0.32, color=t["card_alt"], edgecolor=c, linewidth=1.35, zorder=3)
                    ax.text(uv + mx * 0.024, i + 0.17, f"{uv:.{digits}f}", va="center", ha="left",
                            fontsize=8.1, family="DejaVu Sans Mono", color=t["muted"], bbox=tbox, zorder=5)
            if ceil_x:
                ax.axvline(ceil_x, color=t["muted"], linestyle="--", linewidth=1.1, zorder=1)
            ax.set_yticks(np.arange(len(rows)))
            ax.set_yticklabels([r[0] for r in rows], fontsize=8.5, color=t["text"])
            ax.invert_yaxis()
            ax.set_xlim(0, mx * 1.25)
            ax.set_xlabel("Throughput (Gbit/s)", fontsize=8.4, color=t["muted"], labelpad=2)

        draw_native_facet(
            cy + 0.84 + h_f + gap_f, h_f, "10 Gbit/s Shaped (2 ms RTT)",
            [
                ("GM Term · H1", FAST, ("graphite-meter-client", None), "HTTP/1.1"),
                ("GM Term · H2", FAST, ("graphite-meter-client-h2", None), "HTTP/2"),
                ("GM Term · H3", FAST, ("graphite-meter-client-h3", None), "HTTP/3"),
                ("LS CLI · H1", FAST, ("librespeed-cli", None), "HTTP/1.1"),
                ("iperf3 (ref)", FAST, REFERENCE, "iperf3"),
            ], 9.56, 2,
        )
        draw_native_facet(
            cy + 0.84, h_f, "Unshaped Virtual Link",
            [
                ("GM Term · H1", UNCAPPED, ("graphite-meter-client", None), "HTTP/1.1"),
                ("GM Term · H2", UNCAPPED, ("graphite-meter-client-h2", None), "HTTP/2"),
                ("GM Term · H3", UNCAPPED, ("graphite-meter-client-h3", None), "HTTP/3"),
                ("LS CLI · H1", UNCAPPED, ("librespeed-cli", None), "HTTP/1.1"),
                ("iperf3 (ref)", UNCAPPED, REFERENCE, "iperf3"),
            ], None, 1,
        )

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Runner Hardware & Cloud Kernel Split (Per-VM Paired Dots + Paired Delta)
# ---------------------------------------------------------------------------

def render_hardware_chart(out_stem, *, report_date, vm_count, by_vm, paired_vms, rate, jobs):
    by_hw = defaultdict(list)
    job_meta = {}
    for j in jobs:
        host = j["host"]
        cpu = re.sub(r"\(R\)|\(TM\)|Processor|CPU|\b\d+-Core\b", "", host.get("cpu", "Unknown")).strip()
        cpu = re.sub(r"\s+", " ", cpu)
        kern = host.get("kernel", "")
        cloud = "AWS" if kern.endswith("-aws") else "Azure" if kern.endswith("-azure") else "Other"
        by_hw[(cloud, cpu)].append(j["job"])
        job_meta[j["job"]] = (cloud, cpu)
    hw_groups = sorted(by_hw.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    vm_gm = by_vm(UNCAPPED, ("graphite-meter-client", None), rate(UPLOAD, 1000))
    vm_ip = by_vm(UNCAPPED, REFERENCE, rate(UPLOAD, 1000))
    vm_ls = by_vm(UNCAPPED, ("librespeed-cli", None), rate(UPLOAD, 1000))
    pair_diff = paired_vms(UNCAPPED, ("graphite-meter-client", None), REFERENCE, rate(UPLOAD, 1000))

    for theme in ("dark", "light"):
        fh = 6.4
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"RUNNER HARDWARE & KERNEL SPLIT  ·  {report_date}  ·  {vm_count} RUNNER VMs",
                     "Unshaped Native Upload by Runner CPU & Kernel (Per-VM Observations)", t)

        cy, ch = 0.22, fh - 1.00

        def _beeswarm_offsets(xs, base_y, step, x_tol):
            """Deterministic collision-aware vertical offsets so clustered VM dots never hide each other."""
            order = sorted(range(len(xs)), key=lambda k: xs[k])
            placed = []
            ys = [base_y] * len(xs)
            slots = [0, 1, -1, 2, -2, 3, -3]
            for idx in order:
                xv = xs[idx]
                used = {slot for px, slot in placed if abs(xv - px) < x_tol}
                chosen = next((s for s in slots if s not in used), 0)
                ys[idx] = base_y + chosen * step
                placed.append((xv, chosen))
            return ys

        def _short_cpu(cpu):
            s = re.sub(r"(?i)\(r\)|\(tm\)|\b(intel|amd|platinum|gold|silver|bronze|processor|cpu|\d+-core)\b", "", cpu)
            s = re.sub(r"\s+", " ", s).strip()
            s = re.sub(r"(?i)\bxeon\b", "Xeon", s)
            s = re.sub(r"(?i)\bepyc\b", "EPYC", s)
            return s

        # Panel 1: Per-VM dots + group medians by CPU & kernel (n=1 visibly single dot!)
        lr1 = _draw_card(
            fig, 0.020, cy, 0.500, ch, t,
            title="1. Unshaped Upload by CPU & Kernel",
            direction="Higher →",
            legend=[("GM Term.", t["family"]["gm1"], "dot"),
                    ("iperf3", t["family"]["ip"], "dot"),
                    ("LS CLI", t["family"]["ls"], "dot"),
                    ("Diamond = median; bar = min–max", t["ink"], "diamond")],
            footer="Dots = individual VM medians; bar = min–max span; n=1 shows one dot.",
        )
        top1 = 0.78 + 0.22 * max(0, lr1 - 1)
        ax1 = _add_ax(fig, 0.200, cy + 0.84, 0.300, ch - 0.84 - top1, t, "x")
        all_v = []
        series_hw = [
            ("GM", vm_gm, t["family"]["gm1"], -0.25),
            ("ip3", vm_ip, t["family"]["ip"], 0.0),
            ("LS", vm_ls, t["family"]["ls"], 0.25),
        ]
        for gi, ((cloud, cpu), jnames) in enumerate(hw_groups):
            if gi > 0:
                ax1.axhline(gi - 0.5, color=t["divider"], linewidth=0.75, zorder=1)
            for _, vmap, col, off in series_hw:
                vs = [vmap[jn] for jn in jnames if jn in vmap]
                if not vs:
                    continue
                all_v.extend(vs)
                med = median(vs)
                if len(vs) >= 2:
                    lo, hi = min(vs), max(vs)
                    ax1.plot([lo, hi], [gi + off, gi + off], color=col, linewidth=1.6, alpha=0.55, zorder=2)
                    dot_ys = _beeswarm_offsets(vs, gi + off, 0.048, 4.5)
                    ax1.scatter(vs, dot_ys, color=col, s=28, alpha=0.75,
                                edgecolor=t["card"], linewidth=0.5, zorder=4)
                    ax1.scatter([med], [gi + off], color="none", marker="D", s=58,
                                edgecolor=t["ink"], linewidth=1.25, zorder=5)
                else:
                    ax1.scatter(vs, [gi + off], color=col, s=36, alpha=0.95,
                                edgecolor=t["card"], linewidth=0.6, zorder=4)
                ax1.text(max(vs) + 2.4, gi + off, f"{med:.1f}", va="center", ha="left",
                         fontsize=8.2, family="DejaVu Sans Mono", color=col, weight="bold")
        ax1.set_yticks(np.arange(len(hw_groups)))
        ax1.set_yticklabels(
            [f"{cloud} · {_short_cpu(cpu)}\n(n={len(jnames)} VM{'s' if len(jnames) != 1 else ''})"
             for (cloud, cpu), jnames in hw_groups],
            fontsize=8.3, color=t["text"],
        )
        ax1.invert_yaxis()
        ax1.set_xlim(0, max(all_v or [100.0]) * 1.18)
        ax1.set_xlabel("Unshaped upload (Gbit/s)", fontsize=8.6, color=t["muted"], labelpad=3)

        # Panel 2: Paired Per-VM Difference (GM Terminal minus iperf3) colored by Cloud Kernel!
        lr2 = _draw_card(
            fig, 0.538, cy, 0.442, ch, t,
            title="2. Paired Delta: GM − iperf3",
            direction="← iperf3 | GM →",
            legend=[("AWS-kernel", t["aws"], "dot"), ("Azure-kernel", t["azure"], "dot"),
                    ("Bar = min–max", t["muted"], "whisker"), ("0 = tie", t["muted"], "dashed")],
            footer="One dot per VM (same-pass median diff); bar = min–max span.",
        )
        top2 = 0.78 + 0.22 * max(0, lr2 - 1)
        ax2 = _add_ax(fig, 0.708, cy + 0.84, 0.252, ch - 0.84 - top2, t, "x")
        ax2.axvline(0.0, color=t["muted"], linestyle="--", linewidth=1.2, zorder=2)
        all_d = [-20.0, 20.0]
        for gi, ((cloud, cpu), jnames) in enumerate(hw_groups):
            if gi > 0:
                ax2.axhline(gi - 0.5, color=t["divider"], linewidth=0.75, zorder=1)
            ds = [pair_diff[jn] for jn in jnames if jn in pair_diff]
            if not ds:
                continue
            all_d.extend(ds)
            col = t["aws"] if cloud == "AWS" else t["azure"] if cloud == "Azure" else t["other"]
            dot_ys = _beeswarm_offsets(ds, gi, 0.085, 4.5)
            if len(ds) >= 2:
                ax2.plot([min(ds), max(ds)], [gi, gi], color=col, linewidth=2.0, alpha=0.55, zorder=2)
            ax2.scatter(ds, dot_ys, color=col, s=42, edgecolor=t["card"], linewidth=0.7, zorder=4)
            med = median(ds)
            ax2.text(med, gi - 0.30, f"{med:+.1f}G", ha="center", va="bottom",
                     fontsize=8.3, family="DejaVu Sans Mono", color=col, weight="bold")
        ax2.set_yticks(np.arange(len(hw_groups)))
        ax2.set_yticklabels([f"{cloud} · {_short_cpu(cpu)}\n(n={sum(jn in pair_diff for jn in jnames)})"
                             for (cloud, cpu), jnames in hw_groups], fontsize=8.0, color=t["text"])
        ax2.set_ylim(len(hw_groups) - 0.35, -0.72)
        span = max(abs(min(all_d)), abs(max(all_d))) * 1.22
        ax2.set_xlim(-span, span)
        ax2.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+g}" if v else "0"))
        ax2.set_xlabel("GM Terminal − iperf3 (Gbit/s)", fontsize=8.6, color=t["muted"], labelpad=3)

        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Auto-Extending 6-Panel Historic Trends (Complete Rosters, Gap-Safe, Release-Preserving Ticks)
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
    if len(jobs) == 15 and (jobs[0] / "manifest.json").exists():
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
    """Scan all published CI runs in results/*-ci-run-* and render 6-panel Dark + Light trends."""
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

    # Preserve release transition ticks + first & last when thinning for long history
    max_ticks = 8
    if len(entries) <= max_ticks:
        tick_idxs = list(range(len(entries)))
    else:
        must = {0, len(entries) - 1, *(v_idx for v_idx, _ in version_markers)}
        stride = max(1, math.ceil(len(entries) / max_ticks))
        tick_idxs = sorted(must | set(range(0, len(entries), stride)))
        # Trim non-release interior ticks if still > max_ticks + 2
        while len(tick_idxs) > max_ticks + 2:
            droppable = [i for i in tick_idxs if i not in must]
            if not droppable:
                break
            tick_idxs.remove(droppable[len(droppable) // 2])

    first_d = datetime.fromisoformat(entries[0]["date"]).strftime("%d.%m.%Y")
    last_d = datetime.fromisoformat(entries[-1]["date"]).strftime("%d.%m.%Y")

    for theme in ("dark", "light"):
        fh = 12.8
        fig, t = _new_fig(fh, theme)
        _draw_banner(fig, f"HISTORIC TRENDS  ·  {len(entries)} PUBLISHED CI CAMPAIGNS ({first_d} – {last_d})",
                     "Throughput, Accuracy & Server Resources Across Published Campaigns", t)

        chrome_all = [
            ("GM", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
            ("LS Go", "librespeed-go", "chrome", t["family"]["lsg"], "^", "-"),
            ("LS Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
            ("LS PHP", "librespeed", "chrome", t["family"]["ls"], "X", "--"),
            ("OST", "openspeedtest", "chrome", t["family"]["ost"], "D", "-"),
        ]
        panels = [
            ("1. Unshaped Download · Chrome", "Gbit/s · higher →", UNCAPPED, dl_gbps, chrome_all, False, False),
            ("2. Unshaped Upload · Native", "Gbit/s · higher →", UNCAPPED, ul_gbps, [
                ("GM Term.", "graphite-meter-client", None, t["family"]["gm1"], "o", "-"),
                ("iperf3 (ref)", "iperf3", None, t["family"]["ip"], "s", "--"),
                ("LS CLI", "librespeed-cli", None, t["family"]["ls"], "^", "-"),
            ], False, False),
            ("3. 10 Gbit/s Upload · Chrome", "Gbit/s · higher →", FAST, ul_gbps, chrome_all, False, False),
            ("4. 1G Upload vs iperf3 · Chrome", "% diff · closer to 0%", PLAIN, None, chrome_all, False, True),
            ("5. Server Upload CPU · 1 Gbit/s", "s/GB · ← lower", PLAIN, srv_cpu("up"), [
                ("GM Term.", "graphite-meter-client", None, t["family"]["gm1"], "D", "--"),
                ("GM Chr", "graphite-meter", "chrome", t["family"]["gm2"], "o", "-"),
                ("OST Chr", "openspeedtest", "chrome", t["family"]["ost"], "v", "-"),
                ("LS Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("LS CLI", "librespeed-cli", None, t["family"]["ls"], "^", "--"),
                ("iperf3", "iperf3", None, t["family"]["ip"], "P", ":"),
            ], True, False),
            ("6. Peak Server RAM · 1 Gbit/s", "MB · ← lower", PLAIN, mem_mb, [
                ("GM Chr", "graphite-meter", "chrome", t["family"]["gm1"], "o", "-"),
                ("GM Term.", "graphite-meter-client", None, t["family"]["gm2"], "D", "--"),
                ("LS Rust", "librespeed-rust", "chrome", t["family"]["lsr"], "s", "-"),
                ("OST Chr", "openspeedtest", "chrome", t["family"]["ost"], "v", "-"),
                ("LS Go", "librespeed-go", "chrome", t["family"]["lsg"], "^", "-"),
                ("LS PHP", "librespeed", "chrome", t["family"]["ls"], "X", "-"),
                ("iperf3", "iperf3", None, t["family"]["ip"], "P", ":"),
            ], False, False),
        ]

        col_xs = [0.020, 0.510]
        card_w = 0.470
        row_h = 3.72
        row_gap = 0.20
        top_in = fh - 0.80
        last_x = len(entries) - 1

        for idx, (ptitle, dir_txt, scen, fn, series_spec, phase_note, is_signed) in enumerate(panels):
            r_idx, c_idx = divmod(idx, 2)
            cx = col_xs[c_idx]
            cy = top_in - (r_idx + 1) * row_h - r_idx * row_gap
            _draw_card(fig, cx, cy, card_w, row_h, t, title=ptitle, direction=dir_txt)
            ax = _add_ax(fig, cx + 0.056, cy + 0.62, card_w - 0.072, row_h - 1.06, t, "y")
            ax.grid(axis="x", color=t["grid"], linewidth=0.5, alpha=0.5, zorder=0)
            if is_signed:
                ax.axhspan(-1.0, 1.0, color=t["good_band"], alpha=0.82 if theme == "dark" else 0.72, zorder=0, label="±1% guide")
                ax.axhline(0.0, color=t["good"], linewidth=1.1, zorder=1)
            for v_idx, _ in version_markers:
                if v_idx > 0:
                    ax.axvline(v_idx, color=t["divider"], linestyle=":", linewidth=1.0, zorder=1)
            all_y, end_labels = [], []
            first_valid = None
            for slbl, tool, br, col, mk, ls in series_spec:
                xs_full = np.arange(len(entries), dtype=float)
                ys_full = np.full(len(entries), np.nan)
                lo_full = np.full(len(entries), np.nan)
                hi_full = np.full(len(entries), np.nan)
                for i, e in enumerate(entries):
                    sp = upload_agree_summary(i, tool, br) if is_signed else _vm_summary(e["runs"], scen, tool, br, fn)
                    if sp is not None:
                        ys_full[i], lo_full[i], hi_full[i] = sp[0], sp[1], sp[2]
                        all_y.extend([sp[1], sp[2]])
                        if first_valid is None or i < first_valid:
                            first_valid = i
                if np.all(np.isnan(ys_full)):
                    continue
                # Preserve missing-campaign gaps cleanly (NaN breaks line); use crisp thin vertical IQR ticks instead of muddy overlapping ribbons
                valid = ~np.isnan(ys_full)
                if np.any(valid):
                    ax.vlines(xs_full[valid], lo_full[valid], hi_full[valid], color=col,
                              alpha=0.36 if theme == "dark" else 0.34, linewidth=1.3, zorder=2)
                ax.plot(xs_full, ys_full, color=col, linestyle=ls, linewidth=2.3, marker=mk, markersize=5.4,
                        markeredgecolor=t["card"], markeredgewidth=0.75, label=slbl, zorder=4)
                # Only attach right-edge label when the latest campaign actually has a measurement!
                if not np.isnan(ys_full[last_x]):
                    lv = float(ys_full[last_x])
                    if is_signed:
                        txt = f"{lv:+.1f}%" if abs(round(lv, 1)) > 0 else "0.0%"
                    elif "s/GB" in dir_txt:
                        txt = f"{lv:.2f}"
                    else:
                        txt = f"{lv:.1f}"
                    end_labels.append((lv, txt, col))

            if is_signed:
                y_lo = min([-2.2, *(all_y or [-2.2])]) * 1.18
                y_hi = max([2.5, *(all_y or [2.5])]) + abs(y_lo) * 0.65
            else:
                y_lo = 0.0
                y_hi = max(all_y) * 1.34 if all_y else 10.0
            ax.set_ylim(y_lo, y_hi)
            y_span = y_hi - y_lo
            placed = _deconflict_labels(end_labels, y_lo + y_span * 0.05, y_hi - y_span * 0.06, y_span * 0.105)
            for orig_y, adj_y, txt, col in placed:
                if abs(adj_y - orig_y) > y_span * 0.015:
                    ax.plot([last_x + 0.08, last_x + 0.24], [orig_y, adj_y], color=col, alpha=0.5, linewidth=0.8, zorder=3)
                ax.text(last_x + 0.27, adj_y, txt, va="center", ha="left", fontsize=8.4,
                        family="DejaVu Sans Mono", color=col, weight="bold")

            if phase_note and first_valid and first_valid > 0:
                ax.axvspan(-0.35, first_valid - 0.35, color=t["card_alt"], alpha=0.90, zorder=1)
                ax.text((first_valid - 0.7) / 2, 0.42, "Phase CPU\nadded\nNov 2026",
                        transform=ax.get_xaxis_transform(), ha="center", va="center",
                        fontsize=8.3, color=t["faint"], style="italic")

            ax.set_xticks(tick_idxs)
            ax.set_xticklabels([x_labels[i] for i in tick_idxs], fontsize=8.0, color=t["muted"])
            ax.set_xlim(-0.35, len(entries) - 1 + max(1.15, 0.18 * len(entries)))
            if r_idx == 2:
                ax.set_xlabel("Campaign (chronological order; unequal intervals)", fontsize=8.1, color=t["muted"], labelpad=3)
            leg = ax.legend(loc="upper left", frameon=True, facecolor=t["card"], framealpha=0.94,
                            edgecolor=t["border"], fontsize=7.8, ncol=3 if len(series_spec) > 3 else 2,
                            handlelength=1.4, borderpad=0.35, labelspacing=0.22, columnspacing=0.75)
            for text in leg.get_texts():
                text.set_color(t["text"])

        fig.text(0.020, 0.08 / fh,
                 "Points = campaign median of VM medians; thin vertical ticks = middle 50% (IQR) of VMs. Dotted = GM releases. Oct runs use pre-pass filter.",
                 color=t["muted"], fontsize=8.1, va="bottom", ha="left")
        fig.savefig(f"{out_stem}-{theme}.png", dpi=185, facecolor=t["bg"])
        plt.close(fig)
    return entries
