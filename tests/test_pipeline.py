"""Checks on the data build and the headline results."""

import pandas as pd
import pytest

from energy_transition import analysis, build

AGGREGATES = ["WLD", "EUU", "SSF", "LMY", "OED", "ARB", "EAS", "AFE"]


@pytest.fixture(scope="module")
def tables():
    long = build.world_bank_long()
    return {"wb": build.world_bank_wide(long), "un": build.un_sdg_721()}


@pytest.fixture(scope="module")
def result(tables):
    return analysis.run(tables["wb"], tables["un"])


def test_world_bank_countries_only(tables):
    wb = tables["wb"]
    assert wb["country_code"].nunique() == 215
    assert not wb["country_code"].isin(AGGREGATES).any()
    assert not wb.duplicated(["country_code", "year"]).any()


def test_percentages_in_range(tables):
    for col in ["renewable_electricity_pct", "renewable_final_energy_pct"]:
        assert tables["wb"][col].dropna().between(0, 100).all()
    assert tables["un"]["renewable_final_energy_pct"].dropna().between(0, 100).all()


def test_un_series_and_coverage(tables):
    un = tables["un"]
    assert (un["series"] == "EG_FEC_RNEW").all() and (un["units"] == "PERCENT").all()
    assert un["country_code"].nunique() == 230
    counts = un.groupby("year")["renewable_final_energy_pct"].count()
    assert counts[2023] == 225 and counts[2024] == 84


def test_balanced_panel_is_constant(result):
    tr = result["tables"]["trend"]
    assert tr["n_balanced_panel"].nunique() == 1
    assert (tr["n_reporting"] >= tr["n_balanced_panel"]).all()


def test_headline_numbers(result):
    s = result["summary"]
    assert s["median_all_reporting"][1] == pytest.approx(22.81, abs=0.01)
    assert s["median_balanced_panel"][0] == pytest.approx(10.29, abs=0.01)
    assert s["un_sdg_7_2_1"]["median"] == pytest.approx(18.32, abs=0.01)
    corr = result["tables"]["correlations"].set_index("indicator")["spearman_rho_with_gdp_per_capita"]
    assert corr.iloc[0] == pytest.approx(-0.167, abs=0.001)


def test_income_quartiles_cover_sample(result):
    ig = result["tables"]["income_gradient"]
    cs = result["tables"]["cross_section_2021"]
    assert ig["countries"].sum() == len(cs)
    assert isinstance(cs["gdp_quartile"].dtype, pd.CategoricalDtype)


def test_change_sample_excludes_small_countries(result):
    ch = result["tables"]["changes_2011_2021"]
    assert (ch["population"] >= 1e6).all()
    assert ch["change_pp"].is_monotonic_decreasing


# --- models ---------------------------------------------------------------

@pytest.fixture(scope="module")
def model_result(tables):
    from energy_transition import models
    return models.run(tables["wb"])


def test_every_country_has_a_continent(tables):
    from energy_transition import models
    assert models.add_continent(tables["wb"])["continent"].notna().all()


def test_convergence(model_result):
    s = model_result["summary"]
    assert s["convergence_start_share"]["coef"] < 0
    assert s["convergence_start_share"]["p_value"] < 0.01
    assert (model_result["convergence_data"]["population"] >= 1e6).all()


def test_coefficient_table(model_result):
    coefs = model_result["coefficients"]
    assert not coefs["term"].str.contains(r"C\(", regex=True).any()
    assert (coefs["ci_low"] <= coefs["coef"]).all() and (coefs["coef"] <= coefs["ci_high"]).all()
