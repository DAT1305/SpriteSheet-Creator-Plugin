#!/usr/bin/env python3
"""Process a chroma-key sprite sheet into transparent frames, a sheet, and a GIF."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


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


def trim_to_content(image: Image.Image, padding: int) -> Image.Image:
    bbox = image.getbbox()
    if not bbox:
        return image
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(image.width, bbox[2] + padding)
    bottom = min(image.height, bbox[3] + padding)
    return image.crop((left, top, right, bottom))


def normalize_frame(image: Image.Image, size: int, padding: int, trim: bool) -> Image.Image:
    if trim:
        image = trim_to_content(image, padding)
    image.thumbnail((size - padding * 2, size - padding * 2), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(image, ((size - image.width) // 2, (size - image.height) // 2))
    return canvas


def make_transparent_sheet(frames: list[Image.Image], cols: int, rows: int, size: int) -> Image.Image:
    sheet = Image.new("RGBA", (cols * size, rows * size), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        x = (index % cols) * size
        y = (index // cols) * size
        sheet.alpha_composite(frame, (x, y))
    return sheet


def make_preview(frames: list[Image.Image], cols: int, rows: int, size: int, output: Path) -> None:
    gap = 18
    preview = Image.new("RGBA", (cols * size + (cols + 1) * gap, rows * size + (rows + 1) * gap), (248, 251, 255, 255))
    for index, frame in enumerate(frames):
        x = gap + (index % cols) * (size + gap)
        y = gap + (index // cols) * (size + gap)
        preview.alpha_composite(frame, (x, y))
    preview.save(output)


def rgba_frames_to_gif(frames: list[Image.Image], output: Path, duration: int, loop: int) -> None:
    # GIF transparency is palette based. Composite on transparent index 0 by
    # quantizing each RGBA frame after reserving fully transparent pixels.
    gif_frames = []
    for frame in frames:
        rgba = frame.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 0))
        background.alpha_composite(rgba)
        paletted = background.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
        alpha = rgba.getchannel("A")
        mask = alpha.point(lambda value: 255 if value <= 8 else 0)
        paletted.paste(255, mask)
        gif_frames.append(paletted)

    gif_frames[0].save(
        output,
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration,
        loop=loop,
        transparency=255,
        disposal=2,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to the generated sprite sheet PNG.")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for outputs.")
    parser.add_argument("--cols", default=3, type=int, help="Grid columns.")
    parser.add_argument("--rows", default=2, type=int, help="Grid rows.")
    parser.add_argument("--bg", default="ff3bbd", type=parse_hex_color, help="Chroma-key hex color.")
    parser.add_argument("--tolerance", default=115, type=int, help="Chroma-key tolerance.")
    parser.add_argument("--size", default=256, type=int, help="Square normalized frame size.")
    parser.add_argument("--padding", default=24, type=int, help="Padding around detected content.")
    parser.add_argument("--no-trim", action="store_true", help="Keep full cell framing instead of trimming content.")
    parser.add_argument("--frame-prefix", default="frame", help="Frame filename prefix.")
    parser.add_argument("--gif", default="animation.gif", help="GIF filename.")
    parser.add_argument("--duration", default=90, type=int, help="GIF frame duration in ms.")
    parser.add_argument("--loop", default=0, type=int, help="GIF loop count. 0 means forever.")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = args.out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    source = Image.open(args.input).convert("RGBA")
    frames: list[Image.Image] = []
    total = args.cols * args.rows

    for index in range(total):
        cell = crop_cell(source, index % args.cols, index // args.cols, args.cols, args.rows)
        keyed = remove_chroma_key(cell, args.bg, args.tolerance)
        frame = normalize_frame(keyed, args.size, args.padding, trim=not args.no_trim)
        frame.save(frames_dir / f"{args.frame_prefix}-{index + 1:03d}.png")
        frames.append(frame)

    transparent_sheet = make_transparent_sheet(frames, args.cols, args.rows, args.size)
    transparent_sheet.save(args.out_dir / "spritesheet-transparent.png")
    make_preview(frames, args.cols, args.rows, args.size, args.out_dir / "sprite-crops-preview.png")
    rgba_frames_to_gif(frames, args.out_dir / args.gif, args.duration, args.loop)

    print(f"Wrote {total} frames, spritesheet-transparent.png, sprite-crops-preview.png, and {args.gif} to {args.out_dir}")


if __name__ == "__main__":
    main()
