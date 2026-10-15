"""Paths, indicator definitions and analysis settings."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"

# World Bank indicators: API code -> column name in the clean data
WB_INDICATORS = {
    "EG.ELC.RNEW.ZS": "renewable_electricity_pct",       # renewable electricity output, % of total output
    "EG.FEC.RNEW.ZS": "renewable_final_energy_pct",      # renewable energy, % of total final energy consumption
    "EG.USE.ELEC.KH.PC": "electricity_use_kwh_per_capita",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "SP.POP.TOTL": "population",
}
WB_FILES = {code: f"world_bank_{code.replace('.', '_')}.json.gz" for code in WB_INDICATORS}
UN_FILE = "un_sdg_721_data.json.gz"
UN_SERIES = "EG_FEC_RNEW"

# Analysis settings
TREND_START, TREND_END = 2000, 2021     # years with near-complete country coverage
CROSS_SECTION_YEAR = 2021               # latest year with broad coverage for both electricity and GDP
UN_YEAR = 2023                          # latest complete UN year (2024 has 84 of 225 values)

# Colour-blind-checked palette (validated with the dataviz palette checker)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK_2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
QUARTILE_BLUES = ["#c6dbf5", "#8fb8ea", "#4f8fdc", "#1d5aa6"]
