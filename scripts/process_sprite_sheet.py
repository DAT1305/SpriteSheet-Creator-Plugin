#!/usr/bin/env python3
"""Process a chroma-key sprite sheet into transparent frames, a sheet, and a GIF."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageStat


def parse_hex_color(value: str) -> tuple[int, int, int]:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        raise argparse.ArgumentTypeError("background color must be 6 hex digits, e.g. ff3bbd")
    return tuple(int(cleaned[index:index + 2], 16) for index in (0, 2, 4))


def estimate_border_color(image: Image.Image, sample: int = 3) -> tuple[int, int, int]:
    rgba = image.convert("RGBA")
    sample = max(1, min(sample, rgba.width // 2, rgba.height // 2))
    mask = Image.new("L", rgba.size, 0)
    mask_pixels = mask.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if x < sample or y < sample or x >= rgba.width - sample or y >= rgba.height - sample:
                mask_pixels[x, y] = 255
    mean = ImageStat.Stat(rgba.convert("RGB"), mask).mean
    return tuple(int(round(channel)) for channel in mean[:3])


def remove_chroma_key(image: Image.Image, bg: tuple[int, int, int], tolerance: int) -> Image.Image:
    rgba = image.convert("RGBA")
    sampled_bg = estimate_border_color(rgba)
    pixels = rgba.load()
    alpha = Image.new("L", rgba.size, 255)
    alpha_pixels = alpha.load()

    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, _ = pixels[x, y]
            explicit_distance = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            sampled_distance = abs(r - sampled_bg[0]) + abs(g - sampled_bg[1]) + abs(b - sampled_bg[2])
            if min(explicit_distance, sampled_distance) <= tolerance:
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


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int] | None:
    return image.convert("RGBA").getchannel("A").getbbox()


def trim_to_content(image: Image.Image, padding: int) -> Image.Image:
    bbox = alpha_bbox(image)
    if not bbox:
        return image
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(image.width, bbox[2] + padding)
    bottom = min(image.height, bbox[3] + padding)
    return image.crop((left, top, right, bottom))


def shared_animation_layout(
    frames: list[Image.Image],
    size: int,
    padding: int,
) -> tuple[float, tuple[float, float], list[tuple[int, int, int, int] | None]]:
    bboxes = [alpha_bbox(frame) for frame in frames]
    content_boxes = [bbox for bbox in bboxes if bbox]
    if not content_boxes:
        return 1.0, (size / 2, size / 2), bboxes

    max_width = max(right - left for left, _, right, _ in content_boxes)
    max_height = max(bottom - top for _, top, _, bottom in content_boxes)
    max_width = max(1, max_width)
    max_height = max(1, max_height)
    scale = min((size - padding * 2) / max_width, (size - padding * 2) / max_height, 1.0)
    anchor = (size / 2, size / 2)
    return scale, anchor, bboxes


def alpha_composite_clipped(canvas: Image.Image, image: Image.Image, position: tuple[int, int]) -> None:
    x, y = position
    left = max(0, x)
    top = max(0, y)
    right = min(canvas.width, x + image.width)
    bottom = min(canvas.height, y + image.height)
    if left >= right or top >= bottom:
        return
    crop = image.crop((left - x, top - y, right - x, bottom - y))
    canvas.alpha_composite(crop, (left, top))


def normalize_frame(
    image: Image.Image,
    size: int,
    scale: float,
    anchor: tuple[float, float],
    bbox: tuple[int, int, int, int] | None,
    trim: bool,
) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if not bbox:
        return canvas

    working = trim_to_content(image, 0) if trim else image
    resized = working.resize(
        (max(1, round(working.width * scale)), max(1, round(working.height * scale))),
        Image.Resampling.LANCZOS,
    )
    source_anchor = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
    if trim:
        source_anchor = (source_anchor[0] - bbox[0], source_anchor[1] - bbox[1])
    x = round(anchor[0] - source_anchor[0] * scale)
    y = round(anchor[1] - source_anchor[1] * scale)
    alpha_composite_clipped(canvas, resized, (x, y))
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
    keyed_frames: list[Image.Image] = []
    total = args.cols * args.rows

    for index in range(total):
        cell = crop_cell(source, index % args.cols, index // args.cols, args.cols, args.rows)
        keyed = remove_chroma_key(cell, args.bg, args.tolerance)
        keyed_frames.append(keyed)

    scale, anchor, bboxes = shared_animation_layout(keyed_frames, args.size, args.padding)
    frames: list[Image.Image] = []

    for index, keyed in enumerate(keyed_frames):
        frame = normalize_frame(keyed, args.size, scale, anchor, bboxes[index], trim=not args.no_trim)
        frame.save(frames_dir / f"{args.frame_prefix}-{index + 1:03d}.png")
        frames.append(frame)

    transparent_sheet = make_transparent_sheet(frames, args.cols, args.rows, args.size)
    transparent_sheet.save(args.out_dir / "spritesheet-transparent.png")
    make_preview(frames, args.cols, args.rows, args.size, args.out_dir / "sprite-crops-preview.png")
    rgba_frames_to_gif(frames, args.out_dir / args.gif, args.duration, args.loop)

    print(f"Wrote {total} frames, spritesheet-transparent.png, sprite-crops-preview.png, and {args.gif} to {args.out_dir}")


if __name__ == "__main__":
    main()
