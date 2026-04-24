# SpriteSheet Creator

Languages: [English](README.md) | [Tiếng Việt](README.vi.md) | [简体中文](README.zh-CN.md)

SpriteSheet Creator is a local Codex plugin for generating and processing
`3 columns x 2 rows` chroma-key sprite sheets. It helps turn one generated image
sheet into transparent PNG frames, a transparent sprite sheet, a crop preview,
and a GIF preview.

## What It Does

- Generates prompts for clean 3x2 sprite sheets.
- Removes flat chroma-key backgrounds such as green `#00ff00` or pink `#ff3bbd`.
- Crops 6 frames from a grid sheet.
- Exports transparent PNG frames.
- Exports a transparent sprite sheet.
- Exports a GIF preview for animation checks.
- Includes an optional helper for batch icon sheets.

## Recommended Generation Rules

Use these rules when asking an image model to create a sprite sheet:

- Exact layout: `3 columns by 2 rows`.
- Total frames: `6`.
- Background: one flat chroma-key color, usually `#00ff00` or `#ff3bbd`.
- Keep the character or object centered in every cell.
- Keep all pixels inside the central 60% of each cell.
- Leave at least 20% empty margin on every side.
- Do not add labels, watermarks, shadows crossing cell borders, or extra panels.

Example prompt:

```text
Create a sprite sheet for a mobile app animation. Exact layout: 3 columns by 2 rows,
6 sequential frames of the same character. Use a solid flat green chroma-key
background (#00ff00). The character must stay the same size, same style, centered
in each cell, with large spacing from cell borders. Keep all character and effect
pixels inside the central 60% of each cell and leave at least 20% empty margin on
every side. No watermark, no text labels.
```

## Usage

Process a generated 3x2 sprite sheet:

```powershell
python plugins/spritesheet-creator/scripts/process_sprite_sheet.py `
  --input assets/sprites/character-sheet.png `
  --out-dir assets/sprites/character `
  --bg 00ff00 `
  --frame-prefix frame `
  --gif character.gif `
  --duration 90
```

`process_sprite_sheet.py` defaults to `--cols 3 --rows 2`, so a normal run
exports 6 frames.

## Output

The sprite processing script writes:

- `frames/frame-001.png`, `frames/frame-002.png`, ...
- `spritesheet-transparent.png`
- `sprite-crops-preview.png`
- the GIF file passed to `--gif`

Use the GIF for previewing timing and motion. Use the transparent PNG frames or
`spritesheet-transparent.png` in production apps and games.

## Optional Icon Sheet Crop

The plugin also includes a helper for simple icon grids:

```powershell
python plugins/spritesheet-creator/scripts/crop_icon_sheet.py `
  --input assets/icons/icon-sheet.png `
  --out-dir assets/icons/crops `
  --names icon-one,icon-two,icon-three,icon-four,icon-five,icon-six `
  --cols 3 `
  --rows 2 `
  --bg ff3bbd
```

## Local Codex Marketplace

For local testing, add this plugin to `.agents/plugins/marketplace.json`:

```json
{
  "name": "spritesheet-creator",
  "source": {
    "source": "local",
    "path": "./plugins/spritesheet-creator"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Design"
}
```

## Requirements

- Python 3
- Pillow

Install Pillow if your Python environment does not already include it:

```powershell
python -m pip install pillow
```

## Repository Layout

```text
plugins/spritesheet-creator/
  .codex-plugin/plugin.json
  README.md
  assets/
  scripts/
    crop_icon_sheet.py
    process_sprite_sheet.py
  skills/
    spritesheet-creator/
      SKILL.md
```

## License

MIT
