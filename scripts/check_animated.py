#!/usr/bin/env python3
"""Validate the animated loader exports in loaders/exports/{gif,webp}."""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "scripts/loaders.json").read_text(encoding="utf-8"))
FPS = CONFIG["fps"]
EXPORT_DIR = ROOT / "loaders/exports"
FORMATS = ("gif", "webp")


def gif_info(path):
    """Return logical screen size, frame count, loop and transparency flags."""
    data = path.read_bytes()
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError("not a GIF")

    width, height = struct.unpack("<HH", data[6:10])
    flags = data[10]
    pos = 13
    if flags & 0x80:
        pos += 3 * (2 ** ((flags & 0x07) + 1))

    frames = 0
    loop = False
    transparent = False
    while pos < len(data):
        marker = data[pos]
        if marker == 0x3B:  # trailer
            break
        if marker == 0x21:  # extension
            label = data[pos + 1]
            pos += 2
            while pos < len(data) and data[pos]:
                size = data[pos]
                if label == 0xFF and data[pos + 1 : pos + 1 + size] == b"NETSCAPE2.0":
                    loop = True
                if label == 0xF9 and size >= 4 and data[pos + 1] & 0x01:
                    transparent = True
                pos += size + 1
            pos += 1
        elif marker == 0x2C:  # image descriptor
            frames += 1
            packed = data[pos + 9]
            pos += 10
            if packed & 0x80:
                pos += 3 * (2 ** ((packed & 0x07) + 1))
            pos += 1  # LZW minimum code size
            while pos < len(data) and data[pos]:
                pos += data[pos] + 1
            pos += 1
        else:
            break
    return width, height, frames, loop, transparent


def webp_info(path):
    """Return animated WebP frame count, total duration (ms) and loop count."""
    data = path.read_bytes()
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a WebP")

    pos = 12
    frames = 0
    duration = 0
    loop = None
    while pos + 8 <= len(data):
        fourcc = data[pos : pos + 4]
        size = struct.unpack("<I", data[pos + 4 : pos + 8])[0]
        payload = data[pos + 8 : pos + 8 + size]
        if fourcc == b"ANIM" and len(payload) >= 6:
            loop = struct.unpack("<H", payload[4:6])[0]
        elif fourcc == b"ANMF":
            frames += 1
            if len(payload) >= 15:
                duration += int.from_bytes(payload[12:15], "little")
        pos += 8 + size + (size & 1)
    if frames == 0:
        raise ValueError("no animation frames")
    return frames, duration, loop


def ffprobe(path):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=codec_name,width,height,pix_fmt",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def check_loader(loader):
    errors = []
    expected_frames = round(loader["duration"] * FPS)
    expected_size = (loader["width"], loader["height"])

    for fmt in FORMATS:
        path = EXPORT_DIR / fmt / f"{loader['name']}.{fmt}"
        relative = path.relative_to(ROOT)
        if not path.exists():
            errors.append(f"missing {relative}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"empty {relative}")
            continue

        if fmt == "gif":
            try:
                width, height, frames, loop, transparent = gif_info(path)
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            if (width, height) != expected_size:
                errors.append(
                    f"{relative}: {width}x{height}, expected {expected_size[0]}x{expected_size[1]}"
                )
            if frames != expected_frames:
                errors.append(f"{relative}: {frames} frames, expected {expected_frames}")
            if not loop:
                errors.append(f"{relative}: missing infinite-loop extension")
            if not transparent:
                errors.append(f"{relative}: no transparent color")
            continue

        try:
            info = ffprobe(path)
        except subprocess.CalledProcessError as exc:
            errors.append(f"{relative}: ffprobe failed: {exc.stderr.strip()}")
            continue

        streams = info.get("streams") or []
        if not streams:
            errors.append(f"{relative}: no video stream")
            continue
        stream = streams[0]
        width = int(stream.get("width") or 0)
        height = int(stream.get("height") or 0)
        if (width, height) != expected_size:
            errors.append(
                f"{relative}: {width}x{height}, expected {expected_size[0]}x{expected_size[1]}"
            )

        if stream.get("codec_name") != "webp_anim":
            errors.append(f"{relative}: codec {stream.get('codec_name')}, expected webp_anim")
        if "a" not in (stream.get("pix_fmt") or ""):
            errors.append(f"{relative}: pixel format {stream.get('pix_fmt')} has no alpha")
        try:
            webp_frames, webp_duration, webp_loop = webp_info(path)
        except ValueError as exc:
            errors.append(f"{relative}: {exc}")
        else:
            if webp_frames == 0:
                errors.append(f"{relative}: no animation frames")
            if webp_loop != 0:
                errors.append(f"{relative}: loop count {webp_loop}, expected 0 (infinite)")
            expected_ms = int(round(loader["duration"] * 1000))
            if abs(webp_duration - expected_ms) > 40:
                errors.append(
                    f"{relative}: duration {webp_duration}ms, expected {expected_ms}ms"
                )

    return errors


def main():
    if shutil.which("ffprobe") is None:
        raise SystemExit("ffprobe not found; install FFmpeg to validate the animated exports")

    errors = []
    checked = 0
    for loader in CONFIG["loaders"]:
        errors.extend(check_loader(loader))
        checked += len(FORMATS)

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"animated: {checked} files OK")


if __name__ == "__main__":
    main()