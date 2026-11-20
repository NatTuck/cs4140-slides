preview:
	quarto preview index.qmd

render:
	quarto render index.qmd

figs:
	python3 figs/makefigs.py

check-figs:
	python3 figs/check.py

check:
	python3 figs/check.py
	python3 figs/lint.py

.PHONY: preview render figs check-figs check
