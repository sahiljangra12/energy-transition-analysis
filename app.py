"""Streamlit explorer for the cleaned World Bank and UN data.

    pip install -e ".[app]"
    streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
ELEC, FINAL = "renewable_electricity_pct", "renewable_final_energy_pct"


@st.cache_data
def load():
    wb = pd.read_csv(ROOT / "data/clean/world_bank_wide.csv")
    un = pd.read_csv(ROOT / "data/clean/un_sdg_7_2_1.csv")
    return wb, un


st.set_page_config(page_title="Energy Transition Explorer", layout="wide")
wb, un = load()
st.title("Renewable energy and development")
st.caption("World Bank Indicators and UN SDG 7.2.1 · descriptive analysis, not causal inference")

years = sorted(wb.loc[wb[ELEC].notna(), "year"].unique())
year = st.sidebar.select_slider("Year", options=years, value=2021 if 2021 in years else years[-1])
measure = st.sidebar.radio("Measure", {ELEC: "Renewable share of electricity",
                                       FINAL: "Renewable share of all final energy"}.items(),
                           format_func=lambda kv: kv[1])[0]

w = wb[wb["year"] == year].dropna(subset=[measure])
c1, c2, c3 = st.columns(3)
c1.metric("Median across countries", f"{w[measure].median():.1f}%")
c2.metric("Countries reporting", f"{w['country_code'].nunique():,}")
u = un[un["year"] == year][FINAL].dropna()
c3.metric(f"UN SDG 7.2.1 median ({year})", f"{u.median():.1f}%" if len(u) else "n/a")

st.plotly_chart(px.choropleth(w, locations="country_code", color=measure, hover_name="country",
                              range_color=(0, 100), color_continuous_scale="Blues",
                              labels={measure: "%"}), width="stretch")

s = w.dropna(subset=["gdp_per_capita_usd"])
s = s[s["gdp_per_capita_usd"] > 0]
st.plotly_chart(px.scatter(s, x="gdp_per_capita_usd", y=measure, hover_name="country", log_x=True,
                           labels={"gdp_per_capita_usd": "GDP per capita, US$ (log scale)", measure: "Share (%)"}),
                width="stretch")

table = w[["country_code", "country", "gdp_per_capita_usd", "population", ELEC, FINAL]]
st.dataframe(table.sort_values(measure, ascending=False), width="stretch", hide_index=True)
st.download_button("Download this table", table.to_csv(index=False).encode("utf-8"),
                   file_name=f"renewables_{year}.csv", mime="text/csv")
