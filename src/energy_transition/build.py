"""Turn the raw API responses into analysis-ready country tables."""

from __future__ import annotations

import gzip
import json

import pandas as pd
import pycountry

from . import config

ISO3 = {c.alpha_3 for c in pycountry.countries}
ISO_NUMERIC_TO_ALPHA3 = {int(c.numeric): c.alpha_3 for c in pycountry.countries}


def _load(name):
    with gzip.open(config.RAW / name, "rt", encoding="utf-8") as f:
        return json.load(f)


def world_bank_long() -> pd.DataFrame:
    """One row per country, year and indicator, countries only.

    World Bank responses mix countries with regional and income aggregates.
    Only rows whose code is a valid ISO 3166 alpha-3 country code are kept,
    which removes every aggregate (and the non-ISO codes for Kosovo and the
    Channel Islands).
    """
    frames = []
    for code, column in config.WB_INDICATORS.items():
        rows = _load(config.WB_FILES[code])
        df = pd.DataFrame({
            "country_code": [r["countryiso3code"] for r in rows],
            "country": [r["country"]["value"] for r in rows],
            "year": [int(r["date"]) for r in rows],
            "indicator": column,
            "value": [r["value"] for r in rows],
        })
        frames.append(df[df["country_code"].isin(ISO3)])
    out = pd.concat(frames, ignore_index=True)
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out.sort_values(["indicator", "country_code", "year"]).reset_index(drop=True)


def world_bank_wide(long: pd.DataFrame) -> pd.DataFrame:
    """One row per country and year, one column per indicator."""
    wide = long.pivot(index=["country_code", "year"], columns="indicator", values="value").reset_index()
    wide.columns.name = None
    names = long.drop_duplicates("country_code").set_index("country_code")["country"]
    wide.insert(1, "country", wide["country_code"].map(names))
    cols = ["country_code", "country", "year"] + list(config.WB_INDICATORS.values())
    return wide.reindex(columns=cols).sort_values(["country_code", "year"]).reset_index(drop=True)


def un_sdg_721() -> pd.DataFrame:
    """UN SDG 7.2.1 for countries and areas, keyed by ISO alpha-3.

    The UN uses M49 numeric codes. Rows whose code is an ISO 3166 numeric
    country code are kept; regional aggregates have no ISO code and drop out.
    """
    raw = _load(config.UN_FILE)["data"]
    df = pd.DataFrame({
        "geo_code": [int(r["geoAreaCode"]) for r in raw],
        "country": [r["geoAreaName"] for r in raw],
        "year": [int(r["timePeriodStart"]) for r in raw],
        "value": [r["value"] for r in raw],
        "series": [r["series"] for r in raw],
        "units": [r["attributes"]["Units"] for r in raw],
        "nature": [r["attributes"]["Nature"] for r in raw],
    })
    df = df[df["geo_code"].isin(ISO_NUMERIC_TO_ALPHA3)].copy()
    df.insert(0, "country_code", df["geo_code"].map(ISO_NUMERIC_TO_ALPHA3))
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.rename(columns={"value": "renewable_final_energy_pct"}) \
             .sort_values(["country_code", "year"]).reset_index(drop=True)


def build() -> dict[str, pd.DataFrame]:
    config.CLEAN.mkdir(parents=True, exist_ok=True)
    long = world_bank_long()
    tables = {
        "world_bank_long": long,
        "world_bank_wide": world_bank_wide(long),
        "un_sdg_7_2_1": un_sdg_721(),
    }
    for name, df in tables.items():
        df.to_csv(config.CLEAN / f"{name}.csv", index=False, float_format="%.6g")
    return tables
