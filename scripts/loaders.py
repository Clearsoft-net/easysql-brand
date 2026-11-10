#!/usr/bin/env python3
"""Generate the static loader posters from the animated SVG sources.

The animated files in loaders/ are the sources. Each static poster is the
same SVG with the <style> block removed, so it renders the base state without
motion. This is the file to swap in under prefers-reduced-motion.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "loaders"
TARGET_DIR = SOURCE_DIR / "static"
STYLE_RE = re.compile(r"  <style>.*?</style>\n", re.S)


def strip_style(text: str) -> str:
    static, count = STYLE_RE.subn("", text)
    if count != 1:
        raise SystemExit(f"expected exactly one <style> block, found {count}")
    return static


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE_DIR.glob("*.svg")):
        target = TARGET_DIR / f"{source.stem}-static.svg"
        target.write_text(strip_style(source.read_text(encoding="utf-8")), encoding="utf-8")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()