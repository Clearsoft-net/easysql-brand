#!/usr/bin/env python3
"""Regenerate the EasySQL brand kit raster exports.

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
ICON_SOURCES = ("07-dark-icon-only", "08-light-icon-only")
SMALL_ICON_SOURCES = {
    "07-dark-icon-only": "07-dark-icon-small",
    "08-light-icon-only": "08-light-icon-small",
}
SMALL_ICON_SIZES = (16, 24)
SMALL_ICO_SIZES = (16, 20, 24)


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

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"check: {checked} files OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=["logos", "icons", "ico", "platform", "macos", "all", "check"],
    )
    args = parser.parse_args()

    actions = {
        "logos": build_logos,
        "icons": build_icons,
        "ico": build_ico,
        "platform": build_platform,
        "macos": build_macos,
        "check": check,
    }
    if args.action == "all":
        require_magick()
        for name in ("logos", "icons", "ico", "platform", "macos"):
            actions[name]()
        check()
    else:
        if args.action != "check":
            require_magick()
        actions[args.action]()


if __name__ == "__main__":
    main()