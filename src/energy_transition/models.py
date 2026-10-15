"""Regression models: what is associated with renewable shares, and who is catching up?

All models are observational. Coefficients describe conditional associations, not causal effects.
"""

from __future__ import annotations

import country_converter as coco
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from . import config

ELEC = "renewable_electricity_pct"
FINAL = "renewable_final_energy_pct"
BASE_CONTINENT = "Africa"


def add_continent(wb: pd.DataFrame) -> pd.DataFrame:
    codes = wb["country_code"].unique()
    names = coco.CountryConverter().convert(list(codes), src="ISO3", to="continent", not_found=None)
    out = wb.copy()
    out["continent"] = out["country_code"].map(dict(zip(codes, names, strict=True)))
    return out


def _tidy(fit, model: str) -> pd.DataFrame:
    ci = fit.conf_int()
    out = pd.DataFrame({
        "model": model,
        "term": fit.params.index,
        "coef": fit.params.values,
        "std_err": fit.bse.values,
        "p_value": fit.pvalues.values,
        "ci_low": ci[0].values,
        "ci_high": ci[1].values,
    })
    out["n"] = int(fit.nobs)
    out["r_squared"] = fit.rsquared
    out["term"] = (out["term"].str.replace(r"C\(continent, Treatment\('Africa'\)\)\[T\.(.*)\]", r"\1 (vs Africa)",
                                           regex=True)
                              .replace({"log_gdp": "log GDP per capita", "log_pop": "log population",
                                        "start_share": f"Starting share, {config.CHANGE_START}"}))
    return out[~out["term"].str.startswith("C(")]


def cross_section(wb: pd.DataFrame, year: int = config.CROSS_SECTION_YEAR):
    """Renewable shares on log income, log population and continent, one year, HC3 standard errors."""
    c = wb[wb["year"] == year].dropna(subset=["gdp_per_capita_usd", "population", "continent"]).copy()
    c = c[c["gdp_per_capita_usd"] > 0]
    c["log_gdp"] = np.log(c["gdp_per_capita_usd"])
    c["log_pop"] = np.log(c["population"])
    rhs = f"log_gdp + log_pop + C(continent, Treatment('{BASE_CONTINENT}'))"
    fits = {}
    for y, label in [(ELEC, "Electricity share, 2021"), (FINAL, "Final-energy share, 2021")]:
        fits[label] = smf.ols(f"{y} ~ {rhs}", data=c.dropna(subset=[y])).fit(cov_type="HC3")
    return fits


def convergence_data(wb: pd.DataFrame) -> pd.DataFrame:
    start, end = config.CHANGE_START, config.CROSS_SECTION_YEAR
    d = wb[wb["year"].isin([start, end])].pivot(index="country_code", columns="year", values=ELEC).dropna()
    cols = ["country", "gdp_per_capita_usd", "population", "continent"]
    meta = wb[wb["year"] == start].set_index("country_code")[cols]
    d = d.join(meta).dropna()
    d = d[d["population"] >= config.MIN_POPULATION]
    d["start_share"] = d[start]
    d["change_pp"] = d[end] - d[start]
    d["log_gdp"] = np.log(d["gdp_per_capita_usd"])
    return d.reset_index()


def convergence(wb: pd.DataFrame):
    """Change in renewable electricity share on the starting share, income and continent (HC3)."""
    d = convergence_data(wb)
    rhs = f"start_share + log_gdp + C(continent, Treatment('{BASE_CONTINENT}'))"
    return smf.ols(f"change_pp ~ {rhs}", data=d).fit(cov_type="HC3"), d


def within_country(wb: pd.DataFrame):
    """Country and year fixed effects: does a country's share move with its own income? Clustered by country."""
    p = wb[wb["year"].between(config.TREND_START, config.TREND_END)].dropna(subset=[ELEC, "gdp_per_capita_usd"]).copy()
    p = p[p["gdp_per_capita_usd"] > 0]
    p["log_gdp"] = np.log(p["gdp_per_capita_usd"])
    fit = smf.ols(f"{ELEC} ~ log_gdp + C(country_code) + C(year)", data=p).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(p["country_code"])[0]})
    return fit


def run(wb: pd.DataFrame) -> dict:
    wb = add_continent(wb)
    cs = cross_section(wb)
    conv, conv_data = convergence(wb)
    fe = within_country(wb)
    coefs = pd.concat([_tidy(f, name) for name, f in cs.items()]
                      + [_tidy(conv, f"Change in electricity share, {config.CHANGE_START}–{config.CROSS_SECTION_YEAR}"),
                         _tidy(fe, "Electricity share, country and year fixed effects")], ignore_index=True)
    coefs = coefs[coefs["term"] != "Intercept"].reset_index(drop=True)

    def coef(fit, term):
        return {"coef": float(fit.params[term]), "p_value": float(fit.pvalues[term]), "n": int(fit.nobs)}

    summary = {
        "cross_section_log_gdp": {k: coef(f, "log_gdp") for k, f in cs.items()},
        "cross_section_r_squared": {k: float(f.rsquared) for k, f in cs.items()},
        "convergence_start_share": coef(conv, "start_share"),
        "convergence_log_gdp": coef(conv, "log_gdp"),
        "convergence_r_squared": float(conv.rsquared),
        "within_country_log_gdp": coef(fe, "log_gdp"),
    }
    return {"coefficients": coefs, "convergence_data": conv_data, "convergence_fit": conv, "summary": summary}
