"""Summary statistics and tables. Every function takes the clean tables and returns a DataFrame or dict."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from . import config

ELEC = "renewable_electricity_pct"
FINAL = "renewable_final_energy_pct"


def trend(wb: pd.DataFrame) -> pd.DataFrame:
    """Renewable electricity share over time, three ways.

    - median across all reporting countries (the coverage changes over time),
    - median across a balanced panel of countries that report every year,
    - population-weighted mean share.
    """
    t = wb[wb["year"].between(config.TREND_START, config.TREND_END)].dropna(subset=[ELEC])
    years = config.TREND_END - config.TREND_START + 1
    counts = t.groupby("country_code")["year"].nunique()
    balanced = counts[counts == years].index

    rows = []
    for year, g in t.groupby("year"):
        b = g[g["country_code"].isin(balanced)]
        w = g.dropna(subset=["population"])
        rows.append({
            "year": int(year),
            "median_all_reporting": g[ELEC].median(),
            "n_reporting": g["country_code"].nunique(),
            "median_balanced_panel": b[ELEC].median(),
            "n_balanced_panel": len(balanced),
            "population_weighted_mean": np.average(w[ELEC], weights=w["population"]),
        })
    return pd.DataFrame(rows)


def cross_section(wb: pd.DataFrame, un: pd.DataFrame, year: int = config.CROSS_SECTION_YEAR) -> pd.DataFrame:
    """Countries with GDP per capita and renewable electricity share in one year, with GDP quartiles."""
    c = wb[wb["year"] == year].dropna(subset=["gdp_per_capita_usd", ELEC])
    c = c[c["gdp_per_capita_usd"] > 0].copy()
    un_year = un[un["year"] == year][["country_code", FINAL]].rename(columns={FINAL: "un_" + FINAL})
    c = c.merge(un_year, on="country_code", how="left")
    c["gdp_quartile"] = pd.qcut(c["gdp_per_capita_usd"], 4, labels=["Q1 (poorest)", "Q2", "Q3", "Q4 (richest)"])
    return c


def income_gradient(cs: pd.DataFrame) -> pd.DataFrame:
    return (cs.groupby("gdp_quartile", observed=True)
              .agg(countries=(ELEC, "size"),
                   median_gdp_per_capita_usd=("gdp_per_capita_usd", "median"),
                   median_renewable_electricity_pct=(ELEC, "median"),
                   median_renewable_final_energy_pct=(FINAL, "median"))
              .reset_index())


def correlations(cs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, label in [(ELEC, "Renewable electricity output (% of electricity)"),
                       (FINAL, "Renewable energy (% of final energy, World Bank)"),
                       ("un_" + FINAL, "Renewable energy (% of final energy, UN SDG 7.2.1)")]:
        d = cs[["gdp_per_capita_usd", col]].dropna()
        rho, p = spearmanr(d["gdp_per_capita_usd"], d[col])
        rows.append({"indicator": label, "spearman_rho_with_gdp_per_capita": rho, "p_value": p, "n": len(d)})
    return pd.DataFrame(rows)


def changes(wb: pd.DataFrame, start: int = config.CHANGE_START, end: int = config.CROSS_SECTION_YEAR,
            min_population: float = config.MIN_POPULATION) -> pd.DataFrame:
    """Change in renewable electricity share between two years, for countries of at least 1 million people."""
    d = wb[wb["year"].isin([start, end])].pivot(index="country_code", columns="year", values=ELEC).dropna()
    meta = wb[wb["year"] == end].set_index("country_code")[["country", "population"]]
    d = d.join(meta)
    d = d[d["population"] >= min_population]
    d = d.rename(columns={start: f"share_{start}", end: f"share_{end}"})
    d["change_pp"] = d[f"share_{end}"] - d[f"share_{start}"]
    return (d.reset_index().sort_values(["change_pp", "country_code"], ascending=[False, True], kind="stable")
             .reset_index(drop=True))


def un_summary(un: pd.DataFrame, year: int = config.UN_YEAR) -> dict:
    v = un.loc[un["year"] == year, FINAL].dropna()
    return {"year": year, "countries": int(v.size), "median": float(v.median()), "mean": float(v.mean()),
            "values_in_2024": int(un.loc[un["year"] == 2024, FINAL].notna().sum())}


def run(wb: pd.DataFrame, un: pd.DataFrame) -> dict:
    tr = trend(wb)
    cs = cross_section(wb, un)
    ch = changes(wb)
    tables = {
        "trend": tr,
        "income_gradient": income_gradient(cs),
        "correlations": correlations(cs),
        "changes_2011_2021": ch,
        "cross_section_2021": cs,
    }
    first, last = tr.iloc[0], tr.iloc[-1]
    summary = {
        "trend_years": [int(first.year), int(last.year)],
        "median_all_reporting": [first.median_all_reporting, last.median_all_reporting],
        "median_balanced_panel": [first.median_balanced_panel, last.median_balanced_panel],
        "balanced_panel_countries": int(first.n_balanced_panel),
        "population_weighted_mean": [first.population_weighted_mean, last.population_weighted_mean],
        "share_of_countries_increasing_2011_2021": float((ch["change_pp"] > 0).mean()),
        "median_change_2011_2021_pp": float(ch["change_pp"].median()),
        "countries_in_change_analysis": int(len(ch)),
        "un_sdg_7_2_1": un_summary(un),
        "correlations": tables["correlations"].set_index("indicator")["spearman_rho_with_gdp_per_capita"].to_dict(),
    }
    return {"tables": tables, "summary": summary}
