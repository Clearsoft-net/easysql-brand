#!/usr/bin/env python3
"""Outline the text in the brand SVGs from source/ into exports/svg/.

Uses HarfBuzz for shaping (kerning) and fontTools for the glyph outlines.
Requires Inter ExtraBold, Space Grotesk Bold, and Geist Bold installed.

Logo exports are cropped to the artwork with a transparent border so the
distribution SVG matches the 1x PNG; icon exports keep the full canvas.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [
    (ROOT / "logo/source", ROOT / "logo/exports/svg", 8),
    (ROOT / "icon/source", ROOT / "icon/exports/svg", None),
]

TEXT_RE = re.compile(r"  <text ([^>]*)>(.*?)</text>", re.S)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
TSPAN_RE = re.compile(r"<tspan ([^>]*)>(.*?)</tspan>", re.S)
FAMILY_RE = re.compile(r"'([^']+)'|\"([^\"]+)\"")
RECT_RE = re.compile(r"  <rect ([^>]*)/>")
POLYGON_RE = re.compile(r"  <polygon ([^>]*)/>")
SVG_RE = re.compile(r"<svg ([^>]*)>")


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


def merge_bounds(first, second):
    if first is None:
        return second
    if second is None:
        return first
    return (
        min(first[0], second[0]),
        min(first[1], second[1]),
        max(first[2], second[2]),
        max(first[3], second[3]),
    )


def split_runs(content):
    """Split text content into (text, tspan attrs or None) runs.

    Handles both <tspan>Easy</tspan><tspan>SQL</tspan> and the mono form
    Easy<tspan>SQL</tspan>, where the leading text uses the <text> attrs.
    """
    runs = []
    cursor = 0
    for match in TSPAN_RE.finditer(content):
        if match.start() > cursor:
            runs.append((content[cursor:match.start()], None))
        runs.append((match.group(2), match.group(1)))
        cursor = match.end()
    if cursor < len(content):
        runs.append((content[cursor:], None))
    return runs


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
    bounds_pen = BoundsPen(glyphs)
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
        glyphs[name].draw(TransformPen(bounds_pen, transform))
        cursor += glyph["ax"]
    return pen.getCommands(), cursor * scale, bounds_pen.bounds


def outline_text(attrs, content):
    runs = []
    for text, span_attrs in split_runs(content):
        merged = dict(attrs)
        if span_attrs is not None:
            merged.update(dict(ATTR_RE.findall(span_attrs)))
        runs.append((text, merged))

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
        _, advance, _ = shape_run(text, font_path(family, weight), size, 0.0, baseline)
        shaped.append((text, run_attrs, advance, dx))
        total += advance + dx

    start_x = x - total / 2 if anchor == "middle" else x
    cursor = start_x
    output = []
    bounds = None
    for text, run_attrs, advance, dx in shaped:
        size = float(run_attrs["font-size"])
        weight = int(run_attrs.get("font-weight", 400))
        family = family_of(run_attrs["font-family"])
        cursor += dx
        path, _, run_bounds = shape_run(text, font_path(family, weight), size, cursor, baseline)
        fill = run_attrs.get("fill", attrs.get("fill", "#000000"))
        output.append(f'  <path d="{path}" fill="{fill}"/>')
        bounds = merge_bounds(bounds, run_bounds)
        cursor += advance
    return "\n".join(output), bounds


def rect_bounds(attrs):
    if attrs.get("width", "").endswith("%") or attrs.get("height", "").endswith("%"):
        return None
    x = float(attrs.get("x", 0))
    y = float(attrs.get("y", 0))
    width = float(attrs["width"])
    height = float(attrs["height"])
    return (x, y, x + width, y + height)


def polygon_bounds(attrs):
    values = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", attrs["points"])]
    xs = values[0::2]
    ys = values[1::2]
    return (min(xs), min(ys), max(xs), max(ys))


def outline_svg(text, padding=None):
    bounds = None

    def replace(match):
        nonlocal bounds
        attrs = dict(ATTR_RE.findall(match.group(1)))
        content = match.group(2).strip()
        output, text_bounds = outline_text(attrs, content)
        bounds = merge_bounds(bounds, text_bounds)
        return output

    result = TEXT_RE.sub(replace, text)
    if padding is None:
        return result

    for match in RECT_RE.finditer(text):
        bounds = merge_bounds(bounds, rect_bounds(dict(ATTR_RE.findall(match.group(1)))))
    for match in POLYGON_RE.finditer(text):
        bounds = merge_bounds(bounds, polygon_bounds(dict(ATTR_RE.findall(match.group(1)))))
    if bounds is None:
        raise SystemExit("cannot crop: no artwork bounds")

    min_x = math.floor(bounds[0]) - padding
    min_y = math.floor(bounds[1]) - padding
    max_x = math.ceil(bounds[2]) + padding
    max_y = math.ceil(bounds[3]) + padding
    width = max_x - min_x
    height = max_y - min_y

    def crop_svg(match):
        attrs = dict(ATTR_RE.findall(match.group(1)))
        attrs["viewBox"] = f"{min_x} {min_y} {width} {height}"
        attrs["width"] = str(width)
        attrs["height"] = str(height)
        order = ("xmlns", "viewBox", "width", "height")
        keys = [key for key in order if key in attrs]
        return "<svg " + " ".join(f'{key}="{attrs[key]}"' for key in keys) + ">"

    result = SVG_RE.sub(crop_svg, result, count=1)

    def crop_background(match):
        attrs = dict(ATTR_RE.findall(match.group(1)))
        if not (
            attrs.get("width", "").endswith("%")
            or attrs.get("height", "").endswith("%")
        ):
            return match.group(0)
        attrs["x"] = str(min_x)
        attrs["y"] = str(min_y)
        attrs["width"] = str(width)
        attrs["height"] = str(height)
        order = ("x", "y", "width", "height")
        rest = [f'{key}="{value}"' for key, value in attrs.items() if key not in order]
        values = [f'{key}="{attrs[key]}"' for key in order] + rest
        return "  <rect " + " ".join(values) + "/>"

    return RECT_RE.sub(crop_background, result)


def main():
    for source_dir, target_dir, padding in PAIRS:
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in sorted(source_dir.glob("*.svg")):
            target = target_dir / source.name
            target.write_text(
                outline_svg(source.read_text(encoding="utf-8"), padding),
                encoding="utf-8",
            )
            print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()