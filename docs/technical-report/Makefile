# Rebuild the technical report PDF (needs a TeX Live installation with pdflatex and bibtex).
# Overleaf: upload this folder as a zip; it compiles without this file.
PDF = energy_transition_technical_report.pdf

$(PDF): main.tex references.bib figures
	cp ../../figures/fig*.png figures/
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
	cp main.pdf $(PDF)

clean:
	latexmk -C main.tex

.PHONY: clean
