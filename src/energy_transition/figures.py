"""Static figures for the README and report."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .config import AQUA, BLUE, GRID, INK, INK_2, ORANGE, SURFACE  # noqa: E402

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 200, "savefig.bbox": "tight",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.size": 10, "axes.titlesize": 11.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2, "text.color": INK,
    "axes.edgecolor": GRID, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})


def _save(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def trend(tr: pd.DataFrame, path: Path) -> Path:
    """Three views of the same trend, directly labelled."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    series = [
        ("population_weighted_mean", "Population-weighted average", AQUA),
        ("median_all_reporting", "Median, all reporting countries", ORANGE),
        ("median_balanced_panel", f"Median, same {int(tr.n_balanced_panel.iloc[0])} countries every year", BLUE),
    ]
    nudge = {"median_all_reporting": 6, "median_balanced_panel": -6}   # keep close end labels apart
    for col, label, color in series:
        ax.plot(tr["year"], tr[col], color=color, lw=2, marker="o", ms=3.5)
        ax.annotate(label, (tr["year"].iloc[-1], tr[col].iloc[-1]), xytext=(8, nudge.get(col, 0)),
                    textcoords="offset points", va="center", fontsize=9, color=INK)
    ax.set_xlim(tr["year"].min() - 0.5, tr["year"].max() + 0.5)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.set_ylim(0, 35)
    ax.set_ylabel("Renewable share of electricity output (%)")
    ax.set_title("Renewable electricity has doubled for the typical country since 2000")
    return _save(fig, path)


def income_gradient(ig: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    x = np.arange(len(ig))
    width = 0.38
    bars = [
        ("median_renewable_final_energy_pct", "Renewable share of all final energy", ORANGE, -width / 2),
        ("median_renewable_electricity_pct", "Renewable share of electricity", BLUE, width / 2),
    ]
    for col, label, color, off in bars:
        b = ax.bar(x + off, ig[col], width - 0.04, color=color, label=label)
        ax.bar_label(b, fmt="%.0f%%", padding=3, fontsize=8.5, color=INK)
    labels = [f"{q}\n${g:,.0f}" for q, g in zip(ig["gdp_quartile"], ig["median_gdp_per_capita_usd"], strict=True)]
    ax.set_xticks(x, labels)
    ax.set_xlabel("Countries grouped by GDP per capita (median shown), 2021")
    ax.set_ylabel("Median share (%)")
    ax.set_ylim(0, 75)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right")
    ax.set_title("Poorer countries rely more on renewables overall, mostly traditional biomass")
    return _save(fig, path)


def scatter(cs: pd.DataFrame, path: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharex=True, sharey=True)
    panels = [
        ("renewable_final_energy_pct", "Renewable share of final energy", ORANGE),
        ("renewable_electricity_pct", "Renewable share of electricity", BLUE),
    ]
    for ax, (col, title, color) in zip(axes, panels, strict=True):
        d = cs[["gdp_per_capita_usd", col]].dropna()
        ax.scatter(d["gdp_per_capita_usd"], d[col], s=22, color=color, alpha=0.7, edgecolor=SURFACE, lw=0.6)
        ax.set_xscale("log")
        ax.set_title(f"{title} (n = {len(d)})")
        ax.set_xlabel("GDP per capita, US$ (log scale)")
    axes[0].set_ylabel("Share (%)")
    axes[0].set_ylim(-2, 102)
    fig.suptitle("Income and renewables, 2021: a strong gradient for all energy, a weak one for electricity",
                 x=0.01, ha="left", fontweight="bold", fontsize=11.5)
    fig.tight_layout()
    return _save(fig, path)


def changes(ch: pd.DataFrame, path: Path, n: int = 8) -> Path:
    top = pd.concat([ch.head(n), ch.tail(n)])
    top = top.iloc[::-1].reset_index(drop=True)
    start, end = [c for c in ch.columns if c.startswith("share_")]
    fig, ax = plt.subplots(figsize=(8.5, 6.2))
    y = np.arange(len(top))
    for i, r in top.iterrows():
        color = BLUE if r["change_pp"] > 0 else ORANGE
        ax.plot([r[start], r[end]], [i, i], color=color, lw=2, alpha=0.6)
        ax.scatter(r[start], i, s=36, color=SURFACE, edgecolor=color, lw=1.6, zorder=3)
        ax.scatter(r[end], i, s=36, color=color, zorder=3)
    ax.set_yticks(y, [f"{c}  ({v:+.0f} pp)" for c, v in zip(top["country"], top["change_pp"], strict=True)])
    ax.axhline(n - 0.5, color=GRID, lw=1)
    ax.set_xlim(-2, 102)
    ax.set_xlabel(f"Renewable share of electricity (%):  ○ {start[-4:]}   ● {end[-4:]}")
    ax.grid(axis="y", visible=False)
    ax.set_title(f"Biggest risers and fallers, {start[-4:]}–{end[-4:]} (countries over 1 million people)")
    return _save(fig, path)


def make_all(tables: dict, out: Path) -> list[Path]:
    return [
        trend(tables["trend"], out / "fig1_trend.png"),
        income_gradient(tables["income_gradient"], out / "fig2_income_gradient.png"),
        scatter(tables["cross_section_2021"], out / "fig3_gdp_scatter.png"),
        changes(tables["changes_2011_2021"], out / "fig4_risers_fallers.png"),
    ]
