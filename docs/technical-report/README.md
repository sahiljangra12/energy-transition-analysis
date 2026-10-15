# Technical report

**[Read the PDF →](energy_transition_technical_report.pdf)**

A full write-up of the project: the motivation, every data source, every processing step, each statistical method and why it was chosen, the results, the dashboard, and the limitations. All sources are hyperlinked.

## Edit or rebuild

- **Overleaf:** download this folder as a zip, then in Overleaf choose *New Project → Upload Project*. It compiles as it is (pdfLaTeX with BibTeX).
- **Locally:** run `make` in this folder. It copies the latest figures from `../../figures/`, compiles `main.tex` and updates the PDF.

| File | Contents |
|---|---|
| `main.tex` | The report |
| `references.bib` | Bibliography: data sources, methods and software |
| `figures/` | Figures from the analysis and dashboard screenshots |
| `energy_transition_technical_report.pdf` | Compiled report |
