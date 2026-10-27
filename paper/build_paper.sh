#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex
pdfinfo manuscript.pdf | grep Pages
