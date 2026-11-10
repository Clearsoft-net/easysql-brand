# EasySQL Brand Kit — export pipeline
#
# Requires ImageMagick 7 (built with librsvg) and Python 3.8+.
# `make` regenerates every raster export and validates the result.

MAGICK ?= magick
PYTHON ?= python3
export MAGICK

EXPORT = $(PYTHON) scripts/export.py

.DEFAULT_GOAL := all
.PHONY: all logos icons ico platform macos outline check clean

all:
	$(EXPORT) all

logos:
	$(EXPORT) logos

icons:
	$(EXPORT) icons

ico:
	$(EXPORT) ico

platform:
	$(EXPORT) platform

macos:
	$(EXPORT) macos

outline:
	$(PYTHON) scripts/outline.py

check:
	$(EXPORT) check

clean:
	rm -rf logo/exports/svg logo/exports/png icon/exports/svg icon/exports/png icon/exports/ico icon/exports/web icon/exports/macos