#!/usr/bin/env python3
"""Crop a chroma-key icon sheet into transparent PNGs."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


DEFAULT_NAMES = [
    "streak",
    "first-steps",
    "active-listener",
    "conversation",
    "word-explorer",
    "xp",
]


def parse_hex_color(value: str) -> tuple[int, int, int]:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        raise argparse.ArgumentTypeError("background color must be 6 hex digits, e.g. ff3bbd")
    return tuple(int(cleaned[index:index + 2], 16) for index in (0, 2, 4))


def remove_chroma_key(image: Image.Image, bg: tuple[int, int, int], tolerance: int) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    alpha = Image.new("L", rgba.size, 255)
    alpha_pixels = alpha.load()

    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, _ = pixels[x, y]
            distance = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            if distance <= tolerance:
                alpha_pixels[x, y] = 0

    rgba.putalpha(alpha)
    return rgba


def crop_cell(sheet: Image.Image, col: int, row: int, cols: int, rows: int) -> Image.Image:
    width, height = sheet.size
    return sheet.crop(
        (
            int(col * width / cols),
            int(row * height / rows),
            int((col + 1) * width / cols),
            int((row + 1) * height / rows),
        )
    )


def trim_and_center(image: Image.Image, size: int, padding: int) -> Image.Image:
    bbox = image.getbbox()
    if bbox:
        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(image.width, bbox[2] + padding)
        bottom = min(image.height, bbox[3] + padding)
        image = image.crop((left, top, right, bottom))

    image.thumbnail((size - padding * 2, size - padding * 2), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(image, ((size - image.width) // 2, (size - image.height) // 2))
    return canvas


def make_preview(images: list[tuple[str, Image.Image]], output: Path, cell_size: int) -> None:
    gap = 24
    label_space = 36
    preview = Image.new(
        "RGBA",
        (3 * cell_size + 4 * gap, 2 * (cell_size + label_space) + 3 * gap),
        (248, 251, 255, 255),
    )
    for index, (_, image) in enumerate(images):
        x = gap + (index % 3) * (cell_size + gap)
        y = gap + (index // 3) * (cell_size + label_space + gap)
        preview.alpha_composite(image, (x, y))
    preview.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to the generated icon sheet PNG.")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for cropped PNG outputs.")
    parser.add_argument("--names", default=",".join(DEFAULT_NAMES), help="Comma-separated output names.")
    parser.add_argument("--bg", default="ff3bbd", type=parse_hex_color, help="Chroma-key hex color.")
    parser.add_argument("--tolerance", default=115, type=int, help="Chroma-key tolerance.")
    parser.add_argument("--size", default=256, type=int, help="Square output size in pixels.")
    parser.add_argument("--padding", default=24, type=int, help="Padding around detected badge.")
    parser.add_argument("--cols", default=3, type=int, help="Grid columns.")
    parser.add_argument("--rows", default=2, type=int, help="Grid rows.")
    args = parser.parse_args()

    names = [name.strip() for name in args.names.split(",") if name.strip()]
    expected = args.cols * args.rows
    if len(names) != expected:
        raise SystemExit(f"expected {expected} names for a {args.cols}x{args.rows} grid, got {len(names)}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(args.input).convert("RGBA")
    outputs: list[tuple[str, Image.Image]] = []

    for index, name in enumerate(names):
        col = index % args.cols
        row = index // args.cols
        cell = crop_cell(sheet, col, row, args.cols, args.rows)
        keyed = remove_chroma_key(cell, args.bg, args.tolerance)
        final = trim_and_center(keyed, args.size, args.padding)
        final.save(args.out_dir / f"{name}.png")
        outputs.append((name, final))

    make_preview(outputs, args.out_dir / "icon-crops-preview.png", args.size)
    print(f"Wrote {len(outputs)} icons and preview to {args.out_dir}")


if __name__ == "__main__":
    main()
