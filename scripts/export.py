#!/usr/bin/env python3
"""Regenerate the EasySQL brand kit raster, platform and social exports.

Requires ImageMagick 7 built with librsvg, and Python 3.8+.
Paths resolve from the repository root, so the script can be run from anywhere.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
MAGICK = os.environ.get("MAGICK", "magick")

LOGO_SOURCES = (
    "01-dark-horizontal",
    "01-dark-horizontal-mono",
    "02-light-horizontal",
    "02-light-horizontal-mono",
    "03-dark-stacked",
    "03-dark-stacked-mono",
    "04-light-stacked",
    "04-light-stacked-mono",
    "05-dark-text-only",
    "05-dark-text-only-mono",
    "06-light-text-only",
    "06-light-text-only-mono",
)
ICON_SOURCES = (
    "07-dark-icon-only",
    "08-light-icon-only",
    "07-dark-icon-only-mono",
    "08-light-icon-only-mono",
)
SMALL_ICON_SOURCES = {
    "07-dark-icon-only": "07-dark-icon-small",
    "08-light-icon-only": "08-light-icon-small",
    "07-dark-icon-only-mono": "07-dark-icon-small-mono",
    "08-light-icon-only-mono": "08-light-icon-small-mono",
}
SMALL_ICON_SIZES = (16, 24)
SMALL_ICO_SIZES = (16, 20, 24)

LOADER_SOURCES = (
    "01-orbit",
    "02-e-assemble",
    "02-e-assemble-light",
    "03-query-bar-dark",
    "03-query-bar-light",
    "04-dots",
    "05-splash-dark",
    "05-splash-light",
)
LOADER_DIR = ROOT / "loaders"
LOADER_STATIC_DIR = LOADER_DIR / "static"
LOADER_GRADIENT = {"#F97316", "#F472B6"}
LOADER_FORBIDDEN = {"text", "script", "image", "foreignObject", "filter"}
LOADER_STYLE_RE = re.compile(r"  <style>.*?</style>\n", re.S)


def icon_source(name, size, small_sizes):
    if size in small_sizes:
        return ROOT / "icon/exports/svg" / f"{SMALL_ICON_SOURCES[name]}.svg"
    return ROOT / "icon/exports/svg" / f"{name}.svg"

LOGO_SCALES = (1, 2, 3)
LOGO_BORDER = 8
ICON_SIZES = (16, 22, 24, 32, 48, 64, 128, 180, 192, 256, 512, 1024)
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)
FAVICON_SIZES = (16, 32, 48)
PLATFORM_ICON_SIZES = (192, 512)
APPLE_TOUCH_SIZE = 180
MASKABLE_SIZES = (192, 512)
ADAPTIVE_SIZE = 432
SOCIAL_DIR = ROOT / "social/exports"
BACKGROUND_SVGS = {
    "01-dark-horizontal-bg": "#0F2B3D",
    "02-light-horizontal-bg": "#FFFFFF",
    "03-dark-stacked-bg": "#0F2B3D",
    "04-light-stacked-bg": "#FFFFFF",
    "05-dark-text-only-bg": "#0F2B3D",
    "06-light-text-only-bg": "#FFFFFF",
}
SVG_TAG_RE = re.compile(r"<svg ([^>]*)>(.*)</svg>", re.S)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')

# ICNS chunk type -> pixel size. 1x and @2x entries share pixel sizes.
ICNS_TYPES = (
    (b"icp4", 16),
    (b"ic11", 32),
    (b"icp5", 32),
    (b"ic12", 64),
    (b"ic07", 128),
    (b"ic13", 256),
    (b"ic08", 256),
    (b"ic14", 512),
    (b"ic09", 512),
    (b"ic10", 1024),
)


def run(cmd):
    subprocess.run([str(part) for part in cmd], check=True)


def copy_asset(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"web     {target.relative_to(ROOT)}")


def require_magick():
    if shutil.which(MAGICK) is None:
        raise SystemExit(f"'{MAGICK}' not found; install ImageMagick 7 or set MAGICK")


def svg_size(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<svg[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"', text)
    if not match:
        raise SystemExit(f"cannot read width/height from {path}")
    return float(match.group(1)), float(match.group(2))


def render(svg, out, target, depth=16, background=None):
    """Render svg at target pixel size, optionally flattening onto a background."""
    width, _ = svg_size(svg)
    cmd = [
        MAGICK,
        "-background", background or "none",
        "-density", f"{96.0 * target / width:g}",
        svg,
    ]
    if background:
        cmd += ["-alpha", "remove", "-alpha", "off"]
    cmd += ["-resize", f"{target}x"]
    cmd += ["-define", "png:exclude-chunk=date,time"]
    cmd += ["-depth", str(depth), out]
    out.parent.mkdir(parents=True, exist_ok=True)
    run(cmd)


def render_logo(svg, out, scale):
    """Render a logo cropped to its artwork with a transparent border.

    The viewBox padding is asymmetric, so exports trim to the content and add
    LOGO_BORDER pixels at 1x; the border scales with the density.
    """
    cmd = [
        MAGICK,
        "-background", "none",
        "-density", f"{96 * scale:g}",
        svg,
        "-trim", "+repage",
        "-bordercolor", "none", "-border", str(LOGO_BORDER * scale),
        "-define", "png:exclude-chunk=date,time",
        "-depth", "16", out,
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    run(cmd)


def png_size(path):
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


def ico_bytes(blobs):
    header = struct.pack("<HHH", 0, 1, len(blobs))
    offset = 6 + 16 * len(blobs)
    entries = b""
    for size, blob in blobs:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    return header + entries + b"".join(blob for _, blob in blobs)


def ico_sizes(path):
    data = path.read_bytes()
    _, _, count = struct.unpack("<HHH", data[:6])
    sizes = []
    for index in range(count):
        dim_w, dim_h, _, _, _, _, _, _ = struct.unpack(
            "<BBBBHHII", data[6 + 16 * index:22 + 16 * index]
        )
        sizes.append((dim_w or 256, dim_h or 256))
    return sizes


def icns_bytes(chunks):
    body = b"".join(
        chunk_type + struct.pack(">I", len(blob) + 8) + blob
        for chunk_type, blob in chunks
    )
    return b"icns" + struct.pack(">I", len(body) + 8) + body


def icns_types(path):
    data = path.read_bytes()
    if data[:4] != b"icns":
        raise SystemExit(f"not an ICNS: {path}")
    types = []
    offset = 8
    while offset < len(data):
        types.append(data[offset:offset + 4])
        offset += struct.unpack(">I", data[offset + 4:offset + 8])[0]
    return types


def build_logos():
    for name in LOGO_SOURCES:
        svg = ROOT / "logo/exports/svg" / f"{name}.svg"
        for scale in LOGO_SCALES:
            out = ROOT / "logo/exports/png" / f"{scale}x" / f"{name}.png"
            render_logo(svg, out, scale)
            print(f"logo    {out.relative_to(ROOT)}")


def build_icons():
    for name in ICON_SOURCES:
        for size in ICON_SIZES:
            out = ROOT / "icon/exports/png" / f"{size}x{size}" / f"{name}.png"
            render(icon_source(name, size, SMALL_ICON_SIZES), out, size)
            print(f"icon    {out.relative_to(ROOT)}")


def build_ico():
    for name in ICON_SOURCES:
        with tempfile.TemporaryDirectory() as tmp:
            blobs = []
            for size in ICO_SIZES:
                frame = Path(tmp) / f"{size}.png"
                render(icon_source(name, size, SMALL_ICO_SIZES), frame, size, depth=8)
                blobs.append((size, frame.read_bytes()))
        out = ROOT / "icon/exports/ico" / f"{name}.ico"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(ico_bytes(blobs))
        print(f"ico     {out.relative_to(ROOT)}")


def build_platform():
    dark = ROOT / "icon/exports/svg" / "07-dark-icon-only.svg"
    light = ROOT / "icon/exports/svg" / "08-light-icon-only.svg"
    web = ROOT / "icon/exports/web"

    for size in FAVICON_SIZES:
        out = web / f"favicon-{size}x{size}.png"
        render(icon_source("07-dark-icon-only", size, (16,)), out, size)
        print(f"web     {out.relative_to(ROOT)}")

    with tempfile.TemporaryDirectory() as tmp:
        blobs = []
        for size in FAVICON_SIZES:
            frame = Path(tmp) / f"{size}.png"
            render(dark, frame, size, depth=8)
            blobs.append((size, frame.read_bytes()))
    favicon = web / "favicon.ico"
    favicon.parent.mkdir(parents=True, exist_ok=True)
    favicon.write_bytes(ico_bytes(blobs))
    print(f"web     {favicon.relative_to(ROOT)}")

    # iOS needs an opaque icon; the light variant is designed for light backgrounds.
    out = web / "apple-touch-icon.png"
    render(light, out, APPLE_TOUCH_SIZE, background="#FFFFFF")
    print(f"web     {out.relative_to(ROOT)}")

    for size in PLATFORM_ICON_SIZES:
        out = web / f"android-chrome-{size}x{size}.png"
        render(dark, out, size)
        print(f"web     {out.relative_to(ROOT)}")

    maskable = ROOT / "icon/exports/svg" / "maskable-icon.svg"
    for size in MASKABLE_SIZES:
        out = web / f"maskable-{size}x{size}.png"
        render(maskable, out, size)
        print(f"web     {out.relative_to(ROOT)}")

    for layer in ("foreground", "background"):
        svg = ROOT / "icon/exports/svg" / f"adaptive-icon-{layer}.svg"
        copy_asset(svg, web / f"android-adaptive-{layer}.svg")
        out = web / f"android-adaptive-{layer}-{ADAPTIVE_SIZE}x{ADAPTIVE_SIZE}.png"
        render(svg, out, ADAPTIVE_SIZE)
        print(f"web     {out.relative_to(ROOT)}")

    themed = ROOT / "icon/exports/svg" / "themed-icon.svg"
    copy_asset(themed, web / "android-themed-icon.svg")
    out = web / f"android-themed-icon-{ADAPTIVE_SIZE}x{ADAPTIVE_SIZE}.png"
    render(themed, out, ADAPTIVE_SIZE)
    print(f"web     {out.relative_to(ROOT)}")

    copy_asset(
        ROOT / "icon/exports/svg" / "07-dark-icon-small.svg",
        web / "favicon.svg",
    )


def build_macos():
    with tempfile.TemporaryDirectory() as tmp:
        frames = {}
        for _, size in ICNS_TYPES:
            if size not in frames:
                frame = Path(tmp) / f"{size}.png"
                render(icon_source("07-dark-icon-only", size, (16,)), frame, size, depth=8)
                frames[size] = frame.read_bytes()
    out = ROOT / "icon/exports/macos/AppIcon.icns"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(icns_bytes([(chunk_type, frames[size]) for chunk_type, size in ICNS_TYPES]))
    print(f"macos   {out.relative_to(ROOT)}")


def svg_view_box(path):
    match = SVG_TAG_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"cannot read SVG: {path}")
    view_box = dict(ATTR_RE.findall(match.group(1))).get("viewBox")
    if not view_box:
        raise SystemExit(f"missing viewBox: {path}")
    return view_box


def view_box_size(path):
    values = [float(value) for value in svg_view_box(path).replace(",", " ").split()]
    if len(values) != 4:
        raise SystemExit(f"invalid viewBox: {path}")
    return values[2], values[3]


def embed_svg(path, x, y, width, height):
    match = SVG_TAG_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"cannot embed SVG: {path}")
    attrs = (
        f'x="{round(x, 2):g}" y="{round(y, 2):g}" '
        f'width="{round(width, 2):g}" height="{round(height, 2):g}" '
        f'viewBox="{svg_view_box(path)}"'
    )
    return f"  <svg {attrs}>\n{match.group(2).strip('\n')}\n  </svg>"


def place_logo(path, target_width, canvas_width, canvas_height):
    view_width, view_height = view_box_size(path)
    width = float(target_width)
    height = width * view_height / view_width
    return embed_svg(
        path,
        (canvas_width - width) / 2,
        (canvas_height - height) / 2,
        width,
        height,
    )


def social_og_svg():
    logo = ROOT / "logo/exports/svg" / "01-dark-horizontal.svg"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">\n'
        '  <rect width="1200" height="630" fill="#0F2B3D"/>\n'
        f"{place_logo(logo, 720, 1200, 630)}\n"
        "</svg>\n"
    )


def social_avatar_svg():
    icon = ROOT / "icon/exports/svg" / "07-dark-icon-only.svg"
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n'
        '  <rect width="512" height="512" fill="#0F2B3D"/>\n'
        f"{embed_svg(icon, 96, 96, 320, 320)}\n"
        "</svg>\n"
    )


def social_cards():
    return (
        ("og-image", social_og_svg(), (1200, 630)),
        ("avatar", social_avatar_svg(), (512, 512)),
    )


def build_social():
    SOCIAL_DIR.mkdir(parents=True, exist_ok=True)
    for name, svg_text, size in social_cards():
        svg = SOCIAL_DIR / f"{name}.svg"
        svg.write_text(svg_text, encoding="utf-8")
        print(f"social  {svg.relative_to(ROOT)}")
        out = SOCIAL_DIR / f"{name}.png"
        render(svg, out, size[0])
        print(f"social  {out.relative_to(ROOT)}")


def check_social():
    errors = []
    checked = 0
    for name, expected, size in social_cards():
        svg = SOCIAL_DIR / f"{name}.svg"
        checked += 1
        if not svg.exists():
            errors.append(f"missing {svg.relative_to(ROOT)}")
        elif svg.read_text(encoding="utf-8") != expected:
            errors.append(f"{svg.relative_to(ROOT)}: stale; run make social")
        png = SOCIAL_DIR / f"{name}.png"
        checked += 1
        if not png.exists():
            errors.append(f"missing {png.relative_to(ROOT)}")
        elif png_size(png) != size:
            errors.append(
                f"{png.relative_to(ROOT)}: {png_size(png)}, expected {size[0]}x{size[1]}"
            )
    return errors, checked


def check_background_svgs():
    errors = []
    checked = 0
    for name, fill in BACKGROUND_SVGS.items():
        checked += 1
        svg = ROOT / "logo/exports/svg" / f"{name}.svg"
        if not svg.exists():
            errors.append(f"missing {svg.relative_to(ROOT)}")
            continue
        try:
            root = ElementTree.parse(svg).getroot()
        except ElementTree.ParseError as exc:
            errors.append(f"{svg.relative_to(ROOT)}: {exc}")
            continue
        if any(local_tag(element.tag) == "text" for element in root.iter()):
            errors.append(f"{svg.relative_to(ROOT)}: live text")
            continue
        view_box = [float(value) for value in root.get("viewBox", "").split()]
        if len(view_box) != 4:
            errors.append(f"{svg.relative_to(ROOT)}: invalid viewBox")
            continue
        rects = [element for element in root.iter() if local_tag(element.tag) == "rect"]
        if not any(
            element.get("fill") == fill
            and all(
                float(element.get(attr, 0)) == value
                for attr, value in zip(("x", "y", "width", "height"), view_box)
            )
            for element in rects
        ):
            errors.append(f"{svg.relative_to(ROOT)}: missing opaque background")
    return errors, checked


def local_tag(tag):
    return tag.rsplit("}", 1)[-1]


def loader_structure_errors(path, animated):
    """Validate one loader SVG: no text/scripts/filters, brand gradient, CSS rules."""
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"]

    relative = path.relative_to(ROOT)
    errors = []
    if not all(root.get(attr) for attr in ("viewBox", "width", "height")):
        errors.append(f"{relative}: missing viewBox/width/height")

    tags = {local_tag(element.tag) for element in root.iter()}
    for tag in sorted(tags & LOADER_FORBIDDEN):
        errors.append(f"{relative}: forbidden <{tag}>")

    stops = {
        element.get("stop-color")
        for element in root.iter()
        if local_tag(element.tag) == "stop"
    }
    if stops != LOADER_GRADIENT:
        errors.append(f"{relative}: gradient stops {sorted(stops)}")

    style = "".join(
        element.text or ""
        for element in root.iter()
        if local_tag(element.tag) == "style"
    )
    if animated:
        if "prefers-reduced-motion: reduce" not in style:
            errors.append(f"{relative}: missing reduced-motion rule")
        if "@keyframes" not in style:
            errors.append(f"{relative}: missing @keyframes")
    elif style:
        errors.append(f"{relative}: static poster contains CSS")

    for element in root.iter():
        for attr, value in element.attrib.items():
            if attr.startswith("xmlns"):
                continue
            if "http://" in value or "https://" in value:
                errors.append(f"{relative}: external reference {attr}={value}")
                break
    return errors


def check_loaders():
    errors = []
    for name in LOADER_SOURCES:
        source = LOADER_DIR / f"{name}.svg"
        static = LOADER_STATIC_DIR / f"{name}-static.svg"
        if not source.exists():
            errors.append(f"missing {source.relative_to(ROOT)}")
            continue
        errors.extend(loader_structure_errors(source, animated=True))
        if not static.exists():
            errors.append(f"missing {static.relative_to(ROOT)}")
            continue
        errors.extend(loader_structure_errors(static, animated=False))
        expected, count = LOADER_STYLE_RE.subn("", source.read_text(encoding="utf-8"))
        if count != 1:
            errors.append(
                f"{source.relative_to(ROOT)}: expected one <style> block, found {count}"
            )
        elif static.read_text(encoding="utf-8") != expected:
            errors.append(
                f"{static.relative_to(ROOT)}: stale; run python3 scripts/loaders.py"
            )
    return errors


def check():
    errors = []
    checked = 0

    def expect_png(path, size):
        nonlocal checked
        checked += 1
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
            return
        actual = png_size(path)
        if actual != size:
            errors.append(
                f"{path.relative_to(ROOT)}: {actual[0]}x{actual[1]}, "
                f"expected {size[0]}x{size[1]}"
            )

    with tempfile.TemporaryDirectory() as tmp:
        for name in LOGO_SOURCES:
            svg = ROOT / "logo/exports/svg" / f"{name}.svg"
            for scale in LOGO_SCALES:
                reference = Path(tmp) / f"{name}-{scale}x.png"
                render_logo(svg, reference, scale)
                expect_png(
                    ROOT / "logo/exports/png" / f"{scale}x" / f"{name}.png",
                    png_size(reference),
                )

    for name in ICON_SOURCES:
        for size in ICON_SIZES:
            expect_png(
                ROOT / "icon/exports/png" / f"{size}x{size}" / f"{name}.png",
                (size, size),
            )
        ico = ROOT / "icon/exports/ico" / f"{name}.ico"
        checked += 1
        if not ico.exists():
            errors.append(f"missing {ico.relative_to(ROOT)}")
        elif tuple(ico_sizes(ico)) != tuple((size, size) for size in ICO_SIZES):
            errors.append(f"{ico.relative_to(ROOT)}: frames {ico_sizes(ico)}")

    web = ROOT / "icon/exports/web"
    for size in FAVICON_SIZES:
        expect_png(web / f"favicon-{size}x{size}.png", (size, size))
    expect_png(web / "apple-touch-icon.png", (APPLE_TOUCH_SIZE, APPLE_TOUCH_SIZE))
    for size in PLATFORM_ICON_SIZES:
        expect_png(web / f"android-chrome-{size}x{size}.png", (size, size))
    for size in MASKABLE_SIZES:
        expect_png(web / f"maskable-{size}x{size}.png", (size, size))
    for name in (
        "android-adaptive-foreground",
        "android-adaptive-background",
        "android-themed-icon",
    ):
        expect_png(
            web / f"{name}-{ADAPTIVE_SIZE}x{ADAPTIVE_SIZE}.png",
            (ADAPTIVE_SIZE, ADAPTIVE_SIZE),
        )
    for name in (
        "favicon.svg",
        "android-adaptive-foreground.svg",
        "android-adaptive-background.svg",
        "android-themed-icon.svg",
    ):
        checked += 1
        if not (web / name).exists():
            errors.append(f"missing {web.relative_to(ROOT)}/{name}")
    favicon = web / "favicon.ico"
    checked += 1
    if not favicon.exists():
        errors.append("missing icon/exports/web/favicon.ico")
    elif tuple(ico_sizes(favicon)) != tuple((size, size) for size in FAVICON_SIZES):
        errors.append(f"favicon.ico: frames {ico_sizes(favicon)}")

    icns = ROOT / "icon/exports/macos/AppIcon.icns"
    checked += 1
    if not icns.exists():
        errors.append("missing icon/exports/macos/AppIcon.icns")
    elif tuple(icns_types(icns)) != tuple(chunk_type for chunk_type, _ in ICNS_TYPES):
        errors.append(f"AppIcon.icns: chunks {icns_types(icns)}")

    errors.extend(check_loaders())
    checked += len(LOADER_SOURCES) * 2

    social_errors, social_checked = check_social()
    errors.extend(social_errors)
    checked += social_checked

    background_errors, background_checked = check_background_svgs()
    errors.extend(background_errors)
    checked += background_checked

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"check: {checked} files OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "logos",
            "icons",
            "ico",
            "platform",
            "macos",
            "social",
            "all",
            "check",
        ],
    )
    args = parser.parse_args()

    actions = {
        "logos": build_logos,
        "icons": build_icons,
        "ico": build_ico,
        "platform": build_platform,
        "macos": build_macos,
        "social": build_social,
        "check": check,
    }
    if args.action == "all":
        require_magick()
        for name in ("logos", "icons", "ico", "platform", "macos", "social"):
            actions[name]()
        check()
    else:
        if args.action != "check":
            require_magick()
        actions[args.action]()


if __name__ == "__main__":
    main()