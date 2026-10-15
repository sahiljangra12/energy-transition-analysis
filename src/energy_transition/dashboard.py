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
    rnd = lambda v: None if pd.isna(v) else round(float(v), 2)  # noqa: E731
    data = {
        "years": list(range(config.TREND_START, config.TREND_END + 1)),
        "kpis": [
            {"value": f"{s['median_balanced_panel'][0]:.0f}% → {s['median_balanced_panel'][1]:.0f}%",
             "label": f"Median renewable electricity share, same {s['balanced_panel_countries']} countries, 2000–2021"},
            {"value": f"{s['share_of_countries_increasing_2011_2021']:.0%}",
             "label": "of countries (1M+ people) raised their renewable electricity share, 2011–2021"},
            {"value": f"ρ = {s['correlations']['Renewable energy (% of final energy, World Bank)']:.2f}",
             "label": "Income vs renewable share of all final energy (vs "
                      f"{s['correlations']['Renewable electricity output (% of electricity)']:.2f} for electricity)"},
        ],
        "map": [{"iso3": r.country_code, "name": r.country, "year": int(r.year),
                 "elec": rnd(r.renewable_electricity_pct)} for r in t.itertuples()],
        "scatter": [{"name": r.country, "gdp": rnd(r.gdp_per_capita_usd), "elec": rnd(r.renewable_electricity_pct),
                     "final": rnd(r.renewable_final_energy_pct)} for r in cs.itertuples()],
    }
    html = TEMPLATE.replace("__PLOTLY__", PLOTLY).replace("__DATA__", json.dumps(data, separators=(",", ":")))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
