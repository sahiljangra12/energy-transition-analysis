"""Interactive dashboard (a single HTML page served by GitHub Pages)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from . import config

PLOTLY = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"

TEMPLATE = (Path(__file__).parent / "dashboard_template.html").read_text(encoding="utf-8")


def build(wb: pd.DataFrame, result: dict, out: Path) -> Path:
    s = result["summary"]
    t = wb[wb["year"].between(config.TREND_START, config.TREND_END)].dropna(subset=["renewable_electricity_pct"])
    cs = result["tables"]["cross_section_2021"]
    ig = result["tables"]["income_gradient"]["median_renewable_final_energy_pct"]
    rnd = lambda v: None if pd.isna(v) else round(float(v), 2)  # noqa: E731
    data = {
        "years": list(range(config.TREND_START, config.TREND_END + 1)),
        "kpis": [
            {"value": f"{s['median_balanced_panel'][0]:.0f}% → {s['median_balanced_panel'][1]:.0f}%",
             "label": "Renewable share of electricity in the typical country, 2000 → 2021 "
                      f"(median of the same {s['balanced_panel_countries']} countries)"},
            {"value": f"{s['share_of_countries_increasing_2011_2021']:.0%}",
             "label": "of countries (over 1 million people) increased their renewable electricity share, 2011–2021"},
            {"value": f"{ig.iloc[0]:.0f}% vs {ig.iloc[-1]:.0f}%",
             "label": "Renewable share of all energy use in the poorest vs richest quarter of countries, 2021 "
                      "(mostly traditional biomass in the poorest)"},
        ],
        "map": [{"iso3": r.country_code, "name": r.country, "year": int(r.year),
                 "elec": rnd(r.renewable_electricity_pct)} for r in t.itertuples()],
        "scatter": [{"name": r.country, "gdp": rnd(r.gdp_per_capita_usd), "elec": rnd(r.renewable_electricity_pct),
                     "final": rnd(r.renewable_final_energy_pct)} for r in cs.itertuples()],
    }
    rho = s["correlations"]
    html = (TEMPLATE.replace("__RHO_FINAL__", f"{rho['Renewable energy (% of final energy, World Bank)']:.2f}")
            .replace("__RHO_ELEC__", f"{rho['Renewable electricity output (% of electricity)']:.2f}"))
    html = html.replace("__PLOTLY__", PLOTLY).replace("__DATA__", json.dumps(data, separators=(",", ":")))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
