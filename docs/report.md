# Renewable Energy and Development, 2000–2021: Research Note

## Questions

1. How has the renewable share of electricity changed across countries since 2000, and does the answer depend on how the trend is measured?
2. How does renewable energy relate to national income, and does that depend on whether we look at electricity or at all energy use?
3. Which countries changed most between 2011 and 2021?

## Data

| Source | Indicator | Coverage used |
|---|---|---|
| World Bank (EG.ELC.RNEW.ZS) | Renewable electricity output, % of total electricity output | 2000–2021, 198–205 countries a year |
| World Bank (EG.FEC.RNEW.ZS) | Renewable energy, % of total final energy consumption | 2021 cross-section |
| UN SDG database, indicator 7.2.1 | Renewable energy share in total final energy consumption | 2021 and 2023; 225 countries and areas |
| World Bank | GDP per capita (current US$), population | Weights and income groups |

Only countries and areas are kept. World Bank rows are matched against ISO 3166 alpha-3 codes and UN rows against ISO 3166 numeric codes, which removes every regional and income aggregate. Missing values stay missing.

## Findings

### 1. The typical country's renewable electricity share doubled, and the headline median understates it

| Measure | 2000 | 2021 |
|---|---|---|
| Median, all reporting countries | 13.9% | 22.8% |
| Median, the same 187 countries every year | 10.3% | 22.0% |
| Population-weighted average | 24.0% | 30.1% |

The set of reporting countries changes over time. It jumps from 136 in 1999 to 198 in 2000, and the median falls from 17.8% to 13.9% in that year purely because of who joins. Holding the panel fixed at 187 countries, the median share more than doubles. The population-weighted average is higher throughout, pulled up by populous hydro-rich countries such as Brazil, but it rises more slowly.

### 2. Income tells two different stories depending on the indicator

| GDP per capita quartile, 2021 | Median GDP per capita | Renewable share of electricity | Renewable share of all final energy |
|---|---|---|---|
| Q1 (poorest) | $1,201 | 44% | 65% |
| Q2 | $4,287 | 24% | 19% |
| Q3 | $12,748 | 19% | 13% |
| Q4 (richest) | $43,725 | 23% | 12% |

- **All final energy:** renewable share falls steeply with income (Spearman ρ = −0.56 for both the World Bank and UN SDG 7.2.1 series, n ≈ 197). In the poorest countries this mostly reflects traditional biomass (wood and charcoal for cooking), not modern renewables.
- **Electricity:** the association is weak (ρ = −0.17, p = 0.019). Rich countries span almost the whole range, from near 0% to near 100%, depending largely on hydro resources and policy.

So "renewable share" is not a single measure of a clean-energy transition. The final-energy indicator partly tracks poverty, and the electricity indicator partly tracks geography.

### 3. Most countries moved up between 2011 and 2021, but some hydro-dependent countries fell sharply

Among 151 countries with at least 1 million people, 74% increased their renewable electricity share between 2011 and 2021 (median change +4.6 percentage points).

- **Largest increases:** Cambodia (+50 pp, new hydropower), Denmark (+39, wind), Liberia (+36), Nicaragua (+36), El Salvador, Estonia, Lithuania and the United Kingdom (around +30 each).
- **Largest decreases:** Ghana (−33), the Republic of Congo (−32), Burundi (−30), Myanmar (−22) and Malawi (−19). All are hydro-dependent systems; the usual explanations are demand growth met with new fossil generation, or droughts cutting hydro output.

## Limitations

- These are descriptive comparisons. Income, geography, resource endowment and policy are intertwined, and nothing here identifies a causal effect.
- A country median gives each country equal weight. The population-weighted average is not a generation-weighted global share, which would need total generation by country.
- Renewable electricity data end in 2021 for most countries; UN SDG 7.2.1 has only 84 of 225 values for 2024, so 2023 is the latest comparable year.
- The World Bank and UN final-energy series come from overlapping sources and are not independent confirmations of each other.
