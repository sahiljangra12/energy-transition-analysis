# Data Dictionary

## `data/raw/` (gzipped API responses, unchanged)

| File | Source | Content |
|---|---|---|
| `world_bank_EG_ELC_RNEW_ZS.json.gz` | World Bank Indicators API | Renewable electricity output (% of total electricity output) |
| `world_bank_EG_FEC_RNEW_ZS.json.gz` | World Bank Indicators API | Renewable energy consumption (% of total final energy consumption) |
| `world_bank_EG_USE_ELEC_KH_PC.json.gz` | World Bank Indicators API | Electric power consumption (kWh per capita) |
| `world_bank_NY_GDP_MKTP_KD_ZG.json.gz` | World Bank Indicators API | GDP growth (annual %) |
| `world_bank_NY_GDP_PCAP_CD.json.gz` | World Bank Indicators API | GDP per capita (current US$) |
| `world_bank_SP_POP_TOTL.json.gz` | World Bank Indicators API | Population, total |
| `un_sdg_721_data.json.gz` | UN SDG API, series EG_FEC_RNEW | Renewable energy share in total final energy consumption (%), SDG indicator 7.2.1 |
| `owid_energy_data.csv.gz` | [Our World in Data energy dataset](https://github.com/owid/energy-data), `owid-energy-data.csv`, downloaded 15 October 2026 (SHA-256 of the uncompressed file begins `266f2e2baad79753`) | Energy and electricity by country and source; this project uses electricity generation by source (TWh), compiled by OWID from Ember and the Energy Institute |

The World Bank files cover 1960–2025 for all economies and aggregates; the UN file covers 1990–2024.

## `data/clean/` (built by `python -m energy_transition`)

### `world_bank_wide.csv`: one row per country and year

| Column | Description |
|---|---|
| `country_code` | ISO 3166 alpha-3 code |
| `country` | World Bank country name |
| `year` | Calendar year |
| `renewable_electricity_pct` | Renewable electricity output, % of total electricity output |
| `renewable_final_energy_pct` | Renewable energy, % of total final energy consumption |
| `electricity_use_kwh_per_capita` | Electric power consumption, kWh per person |
| `gdp_growth_pct` | Real GDP growth, annual % |
| `gdp_per_capita_usd` | GDP per capita, current US$ |
| `population` | Total population |

`world_bank_long.csv` holds the same values with one row per country, year and indicator.

### `electricity_by_source.csv`: one row per country and year, 2000–2024

Countries are matched to ISO 3166 alpha-3 codes, so regional aggregates are excluded. Within a reported country-year, a missing source is set to 0, and the sources then add up to the total. `electricity_by_source_world.csv` has the same columns for the world total (code `WLD`).

| Column | Description |
|---|---|
| `country_code` | ISO 3166 alpha-3 code |
| `country` | Our World in Data country name |
| `year` | Calendar year |
| `total_twh` | Total electricity generation, TWh |
| `coal_twh`, `gas_twh`, `oil_twh` | Fossil generation by fuel, TWh |
| `nuclear_twh` | Nuclear generation, TWh |
| `hydro_twh`, `wind_twh`, `solar_twh` | Renewable generation by source, TWh |
| `biofuel_twh` | Bioenergy generation, TWh |
| `other_renewable_exc_biofuel_twh` | Other renewables (geothermal, wave, tidal), TWh |

### `un_sdg_7_2_1.csv`: one row per country/area and year

| Column | Description |
|---|---|
| `country_code` | ISO 3166 alpha-3 code, mapped from the UN M49 numeric code |
| `geo_code` | UN M49 numeric code |
| `country` | UN country or area name |
| `year` | Calendar year |
| `renewable_final_energy_pct` | Renewable energy share in total final energy consumption, % |
| `series`, `units`, `nature` | UN series code (EG_FEC_RNEW), units (PERCENT) and data nature (E = estimated, etc.) |

## Inclusion rules

- World Bank: rows kept when the code is a valid ISO 3166 alpha-3 code (215 countries and areas). This drops all regional and income aggregates, plus Kosovo (XKX) and the Channel Islands (CHI), which have no ISO code.
- UN: rows kept when the M49 code is an ISO 3166 numeric code (230 countries and areas).
- Missing values are left missing, never set to zero.
