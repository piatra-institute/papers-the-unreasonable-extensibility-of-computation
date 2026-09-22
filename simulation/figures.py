"""Figures for *The Unreasonable Extensibility of Computation*. Each reads the
results dict and writes one PNG.

Palette (CVD-checked in a prior validation; line style and direct labels
carry the encoding as well as hue): amber, green, blue, warm gray, with red
reserved for a failure.
"""
from __future__ import annotations

import numpy as np
import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#1a1a1a"
GRID = "#d9d9d9"
AMBER = "#b45309"
GREEN = "#15803d"
BLUE = "#2563eb"
GRAY = "#57534e"
RED = "#b3202c"


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK)
    ax.tick_params(colors=INK, labelsize=8.5)
    ax.set_axisbelow(True)
    ax.grid(True, color=GRID, lw=0.6)


def plot_lattice(res: dict, path: str) -> None:
    L = res["lattice"]
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.6),
                             gridspec_kw={"width_ratios": [1.0, 1.15, 1.05]})

    ax = axes[0]
    names = [r["format"] for r in L["ladder"]]
    vals = [r["weights_mb"] for r in L["ladder"]]
    cache = L["cache_mb"]
    legacy = L["legacy_ram_mb"] - L["runtime_state_mb"]
    cols = [RED if v > cache else GREEN for v in vals]
    bars = ax.bar(range(len(names)), vals, color=cols, width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.06, f"{v:.0f}",
                ha="center", fontsize=8, color=INK)
    ax.axhline(cache, color=BLUE, lw=1.4)
    ax.text(3.62, cache * 1.10, f"weight cache\n{cache:.0f} MB", fontsize=7.2,
            color=BLUE)
    ax.axhline(legacy, color=GRAY, lw=1.2, ls="--")
    ax.text(3.62, legacy * 0.48, f"earlier\nrevision\n{legacy:.0f} MB",
            fontsize=7.2, color=GRAY)
    ax.set_yscale("log")
    ax.set_ylim(6, 1400)
    ax.set_xlim(-0.6, 5.1)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(["fp32", "fp16", "int8", "four-bit\nblocks"],
                       fontsize=8)
    ax.set_ylabel("weights, MB", fontsize=8.5)
    ax.set_title("a. weight memory by representation", fontsize=9.5,
                 color=INK, loc="left")
    _style(ax)

    ax = axes[1]
    mig = L["migration"]
    bits = [m["bits"] for m in mig]
    ax.plot(bits, [m["t_io"] for m in mig], color=AMBER, lw=1.9, marker="o",
            ms=3.6, label="streaming, seconds per token")
    ax.plot(bits, [m["t_cpu"] for m in mig], color=BLUE, lw=1.9,
            label="arithmetic, seconds per token")
    cross = L["compute_bound_at_or_below_bits"]
    ax.axvspan(min(bits) - 0.5, cross + 0.5, color=GRID, alpha=0.55, lw=0)
    ax.text(2.0, 6.0, "compute-bound", fontsize=7.4, color=GRAY, ha="center")
    ax.text(12.0, 6.0, "storage-bound", fontsize=7.4, color=GRAY,
            ha="center")
    ax.axvline(4, color=GREEN, lw=1.1, ls=":")
    ax.text(4.15, 0.13, "the format\nin use", fontsize=7.4, color=GREEN)
    ax.set_yscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("bits per weight", fontsize=9)
    ax.set_ylabel("seconds per token", fontsize=8.5)
    ax.set_title("b. time per token by bit width",
                 fontsize=9.5, color=INK, loc="left")
    ax.legend(fontsize=7.2, frameon=False, loc="lower left")
    _style(ax)

    ax = axes[2]
    labels = ["q4 weights", "eight-bit\ncache", "vector unit", "streaming"]
    keys = ["q4_weights", "int8_kv", "vfpu", "streaming"]
    sup = set(L["supported"]["necessary_techniques"])
    heights = [1.0 if k in sup else 0.45 for k in keys]
    cols = [BLUE if k in sup else GRAY for k in keys]
    bars = ax.bar(range(4), heights, color=cols, width=0.6)
    for b, k in zip(bars, keys):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.04,
                "necessary" if k in sup else "speed only", ha="center",
                fontsize=7.2, color=INK)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=7.6)
    ax.set_yticks([])
    ax.set_ylim(0, 1.5)
    n_v, n_s = L["supported"]["n_viable"], L["supported"]["n_subsets"]
    ax.text(1.5, 1.26, f"{n_v} of {n_s} subsets reach the latency floor.\n"
                       f"On the earlier revision, "
                       f"{L['legacy']['n_viable']} of {n_s}.",
            fontsize=7.6, color=INK, ha="center")
    ax.set_title("c. techniques in viable configurations", fontsize=9.5,
                 color=INK, loc="left")
    _style(ax)
    ax.grid(False)

    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_thresholds(res: dict, path: str) -> None:
    T = res["thresholds"]
    head = T["headline"]
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.6))

    ax = axes[0]
    years = np.arange(T["years"])
    le = np.array(head["annual_logefficiency"])
    cr = np.array(head["annual_crossings"], dtype=float)
    ax.bar(years, le / le.max(), color=GRAY, width=0.85,
           label="efficiency gained that year")
    ax.plot(years, cr / max(cr.max(), 1), color=RED, lw=1.8, marker="o",
            ms=3.2, label="capabilities crossing the budget")
    ax.set_xlabel("year", fontsize=9)
    ax.set_ylabel("share of the series maximum", fontsize=8.5)
    ax.set_title("a. efficiency gains and capability crossings", fontsize=9.5, color=INK,
                 loc="left")
    ax.legend(fontsize=7.2, frameon=False, loc="upper left")
    _style(ax)

    ax = axes[1]
    m = [w["over_budget_median"] for w in T["worlds"]]
    ax.plot(m, [w["burstiness_ratio"] for w in T["worlds"]], color=RED,
            lw=1.9, marker="o", ms=4.4, label="burstiness of crossings\nover burstiness of gains")
    ax.plot(m, [w["top_decile_crossing_share"] for w in T["worlds"]],
            color=AMBER, lw=1.9, marker="s", ms=4,
            label="share of crossings from\nthe top decile of families")
    ax.plot(m, [w["invisible_share"] for w in T["worlds"]], color=BLUE,
            lw=1.9, marker="^", ms=4,
            label="improvements that change\nno capability")
    ax.axhline(1.0, color=GRAY, lw=0.9, ls="--")
    ax.set_xscale("log")
    ax.set_xticks(m)
    ax.set_xticklabels([f"{x:g}x" for x in m])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_xlabel("median distance from the budget at the outset", fontsize=9)
    ax.set_ylim(0, 1.85)
    ax.set_title("b. amplification by distance from budget", fontsize=9.5,
                 color=INK, loc="left")
    ax.legend(fontsize=6.8, frameon=False, loc="upper left")
    _style(ax)

    ax = axes[2]
    hard = T["worlds"][-1]
    ax.plot(years, hard["feasible_curve"], color=GREEN, lw=2.0,
            label="fixed device, software of the day")
    ax.axhline(hard["new_device_feasible"], color=BLUE, lw=1.6, ls="--",
               label=f"device with {T['new_device_budget_factor']:.0f}x the "
                     f"budget,\nsoftware frozen at the outset")
    oy = hard["overtake_year"]
    if oy is not None:
        ax.axvline(oy, color=GRAY, lw=0.9, ls=":")
        ax.text(oy + 1, 3, f"overtaken after\n{oy:.1f} years", fontsize=7.4,
                color=GRAY)
    ax.set_xlabel("year", fontsize=9)
    ax.set_ylabel("task families within budget", fontsize=8.5)
    ax.set_title("c. fixed device against a faster device", fontsize=9.5,
                 color=INK, loc="left")
    ax.legend(fontsize=7.0, frameon=False, loc="upper left")
    _style(ax)

    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_decay(res: dict, path: str) -> None:
    D = res["decay"]
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.6))

    ax = axes[0]
    yrs = np.arange(D["years"])
    ax.plot(yrs, D["psp_depth_curve"]["known"], color=GRAY, lw=1.9,
            label="known")
    ax.plot(yrs, D["psp_depth_curve"]["deployable"], color=BLUE, lw=1.9,
            label="deployable, sustained interest")
    ax.plot(yrs, D["psp_waning_curve"]["deployable"], color=RED, lw=1.9,
            label="deployable, interest waning")
    ax.set_xlabel("year", fontsize=9)
    ax.set_ylabel("artifacts, five-deep stack", fontsize=8.5)
    ax.set_title("a. known and deployable artifacts",
                 fontsize=9.5, color=INK, loc="left")
    ax.legend(fontsize=7.2, frameon=False, loc="upper left")
    _style(ax)

    ax = axes[1]
    d = [a["depth"] for a in D["analytic"]]
    ax.plot(d, [a["stationary_fraction"] for a in D["analytic"]], color=BLUE,
            lw=1.9, marker="o", ms=4, label="stationary deployable fraction")
    ax.plot(d, [w["ratio_at_40"] for w in D["by_depth"]], color=GREEN,
            lw=1.7, ls="--", marker="s", ms=3.6,
            label="simulated, at forty years")
    ax.axhline(0.5, color=GRAY, lw=0.9, ls=":")
    ax.axvline(D["depth_below_half"], color=GRAY, lw=0.9, ls=":")
    ax.text(D["depth_below_half"] + 0.3, 0.72,
            f"deployable share below\n0.5 from depth "
            f"{D['depth_below_half']}", fontsize=7.4, color=GRAY)
    ax.axvline(D["stack_depth"], color=AMBER, lw=1.1)
    ax.text(D["stack_depth"] + 0.3, 0.05, "console stack", fontsize=7.4,
            color=AMBER)
    ax.set_xlabel("components a stack depends on", fontsize=9)
    ax.set_ylabel("share of known artifacts still runnable", fontsize=8.5)
    ax.set_ylim(0, 1.02)
    ax.set_title("b. deployable share by stack depth", fontsize=9.5,
                 color=INK, loc="left")
    ax.legend(fontsize=7.2, frameon=False, loc="upper right")
    _style(ax)

    ax = axes[2]
    ch = [a["critical_hazard"] for a in D["analytic"]]
    ax.plot(d, [1.0 / c for c in ch], color=RED, lw=1.9, marker="o", ms=4)
    ax.axhline(D["mean_improvement_interval_years"], color=GRAY, lw=1.2,
               ls="--")
    ax.text(1.0, D["mean_improvement_interval_years"] * 1.10,
            f"mean interval between improvements, "
            f"{D['mean_improvement_interval_years']:.0f} years", fontsize=7.2,
            color=GRAY)
    ax.scatter([D["stack_depth"]], [D["critical_interval_years_stack"]],
               s=60, color=AMBER, zorder=5)
    ax.annotate(f"five-component stack:\nmean component life "
                f"{D['critical_interval_years_stack']:.0f} years",
                xy=(D["stack_depth"], D["critical_interval_years_stack"]),
                xytext=(5.4, 55), fontsize=7.2, color=AMBER,
                arrowprops=dict(arrowstyle="->", color=AMBER, lw=0.8))
    ax.set_yscale("log")
    ax.set_xlabel("components a stack depends on", fontsize=9)
    ax.set_ylim(18, 900)
    ax.set_ylabel("required mean life of each component, years",
                  fontsize=8.5)
    ax.set_title("c. required component lifetime", fontsize=9.5,
                 color=INK, loc="left")
    _style(ax)

    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
