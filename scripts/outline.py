#!/usr/bin/env python3
"""Outline the text in the brand SVGs from source/ into exports/svg/.

Uses HarfBuzz for shaping (kerning) and fontTools for the glyph outlines.
Requires Inter ExtraBold, Space Grotesk Bold, and Geist Bold installed.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [
    (ROOT / "logo/source", ROOT / "logo/exports/svg"),
    (ROOT / "icon/source", ROOT / "icon/exports/svg"),
]

TEXT_RE = re.compile(r"  <text ([^>]*)>(.*?)</text>", re.S)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
TSPAN_RE = re.compile(r"<tspan ([^>]*)>(.*?)</tspan>", re.S)
FAMILY_RE = re.compile(r"'([^']+)'|\"([^\"]+)\"")


def font_path(family: str, weight: int) -> Path:
    style = "ExtraBold" if weight >= 800 else "Bold" if weight >= 700 else "Regular"
    result = subprocess.run(
        ["fc-match", "-f", "%{family}|%{style}|%{file}", f"{family}:style={style}"],
        check=True,
        capture_output=True,
        text=True,
    )
    matched_family, _, file = result.stdout.strip().split("|", 2)
    if matched_family.split(",")[0].strip() != family:
        raise SystemExit(f"font not found: {family} {style} (fontconfig matched {matched_family})")
    path = Path(file)
    if not path.exists():
        raise SystemExit(f"font file missing: {path}")
    return path


def family_of(value: str) -> str:
    match = FAMILY_RE.search(value)
    return (match.group(1) or match.group(2)) if match else value.split(",")[0].strip()


def shape_run(text, font_file, size, start_x, baseline):
    font = TTFont(font_file)
    upm = font["head"].unitsPerEm
    glyphs = font.getGlyphSet()
    scale = size / upm
    shaped = json.loads(
        subprocess.check_output(
            ["hb-shape", "--output-format=json", str(font_file), text],
            text=True,
        )
    )
    pen = SVGPathPen(glyphs)
    cursor = 0.0
    for glyph in shaped:
        name = glyph["g"]
        dx = glyph.get("dx", 0)
        dy = glyph.get("dy", 0)
        transform = (
            scale,
            0,
            0,
            -scale,
            start_x + (cursor + dx) * scale,
            baseline - dy * scale,
        )
        glyphs[name].draw(TransformPen(pen, transform))
        cursor += glyph["ax"]
    return pen.getCommands(), cursor * scale


def outline_text(attrs, content):
    runs = []
    if "<tspan" in content:
        for span_attrs, span_text in TSPAN_RE.findall(content):
            merged = dict(attrs)
            merged.update(dict(ATTR_RE.findall(span_attrs)))
            runs.append((span_text, merged))
    else:
        runs.append((content, attrs))

    x = float(attrs["x"])
    y = float(attrs["y"])
    anchor = attrs.get("text-anchor", "start")

    first_text, first_attrs = runs[0]
    first_size = float(first_attrs["font-size"])
    first_weight = int(first_attrs.get("font-weight", 400))
    first_family = family_of(first_attrs["font-family"])
    if attrs.get("dominant-baseline") == "central":
        font = TTFont(font_path(first_family, first_weight))
        upm = font["head"].unitsPerEm
        cap = font["OS/2"].sCapHeight
        baseline = y + (cap * first_size / upm) / 2
    else:
        baseline = y

    shaped = []
    total = 0.0
    for text, run_attrs in runs:
        size = float(run_attrs["font-size"])
        weight = int(run_attrs.get("font-weight", 400))
        family = family_of(run_attrs["font-family"])
        dx = float(run_attrs.get("dx", 0))
        _, advance = shape_run(text, font_path(family, weight), size, 0.0, baseline)
        shaped.append((text, run_attrs, advance, dx))
        total += advance + dx

    start_x = x - total / 2 if anchor == "middle" else x
    cursor = start_x
    output = []
    for text, run_attrs, advance, dx in shaped:
        size = float(run_attrs["font-size"])
        weight = int(run_attrs.get("font-weight", 400))
        family = family_of(run_attrs["font-family"])
        cursor += dx
        path, _ = shape_run(text, font_path(family, weight), size, cursor, baseline)
        fill = run_attrs.get("fill", attrs.get("fill", "#000000"))
        output.append(f'  <path d="{path}" fill="{fill}"/>')
        cursor += advance
    return "\n".join(output)


def outline_svg(text: str) -> str:
    def replace(match):
        attrs = dict(ATTR_RE.findall(match.group(1)))
        content = match.group(2).strip()
        return outline_text(attrs, content)

    return TEXT_RE.sub(replace, text)


def main():
    for source_dir, target_dir in PAIRS:
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(source_dir.glob("*.svg")):
            target = target_dir / source.name
            target.write_text(outline_svg(source.read_text(encoding="utf-8")), encoding="utf-8")
            print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()