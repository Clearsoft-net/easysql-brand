# EasySQL Brand Kit — export pipeline
#
# Requires ImageMagick 7 (built with librsvg) and Python 3.8+.
# `make` regenerates every raster, platform and social export and validates the result.

MAGICK ?= magick
PYTHON ?= python3
export MAGICK

EXPORT = $(PYTHON) scripts/export.py

.DEFAULT_GOAL := all
.PHONY: all logos icons ico platform macos social outline loaders animated check-animated check clean

all:
	$(PYTHON) scripts/loaders.py
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

social:
	$(EXPORT) social

outline:
	$(PYTHON) scripts/outline.py

loaders:
	$(PYTHON) scripts/loaders.py

animated:
	node scripts/loaders_animated.mjs

check-animated:
	$(PYTHON) scripts/check_animated.py

check:
	$(EXPORT) check

clean:
	rm -rf logo/exports/svg logo/exports/png icon/exports/svg icon/exports/png icon/exports/ico icon/exports/web icon/exports/macos social loaders/static loaders/exports