---
name: spritesheet-creator
description: Generate or process 3x2 animation sprite sheets arranged on a flat chroma-key background, then crop them into separate transparent PNG frames, transparent sheets, preview sheets, and GIFs. Use for character attacks, UI micro-animations, mascots, game objects, achievement badges, skill icons, lesson icons, or item icons where generating one grid sheet then processing it is faster and cleaner than one image at a time.
---

# SpriteSheet Creator

Use this skill when the user wants a generated animation sheet turned into
separate frames and a GIF, or when they want multiple icons/assets generated
together and cropped cleanly for an app.

Preferred workflow:

1. Generate one sheet with a clear `3 columns x 2 rows` grid.
2. Use a flat hot-pink chroma-key background `#ff3bbd` by default. Only use
   another color if the user explicitly asks for it.
3. Keep every icon centered in its own equal cell with large spacing.
4. Avoid shadows touching neighboring cells or image borders.
5. Crop by equal grid cells.
6. Remove the flat background with chroma-key tolerance.
7. Save transparent PNGs and a preview grid.

This workflow is good for:

- achievement badges
- skill icons
- lesson icons
- inventory/item icons
- toolbar icons
- category icons
- small decorative UI assets
- character/object animation frames
- loading animations
- mascots and UI micro-interactions

## Prompt Pattern

For a 3x2 sheet, use hot pink by default:

```text
Create a single asset sheet for a mobile app. Exact layout: 3 columns by 2 rows,
six separate icons, each centered in its own equal cell with large empty spacing
between cells. Use a solid flat hot-pink chroma-key background (#ff3bbd) across
the entire image. The background must be one uniform color, with no gradient,
texture, lighting, shadows, vignette, or pattern. No shadows touching cell
borders, no text labels outside icons, no watermark. Icon 1: ...
Icon 2: ...
Icon 3: ...
Icon 4: ...
Icon 5: ...
Icon 6: ...
Polished 3D app icon style, glossy beveled edges, consistent scale, crisp
centered icons, enough margin for clean cropping.
```

Keep sprite sheets at `3 columns by 2 rows` unless the user explicitly asks for
another format.

## Crop Script

Run:

```powershell
python plugins/spritesheet-creator/scripts/crop_icon_sheet.py `
  --input assets/icons/icon-sheet.png `
  --out-dir assets/icons/crops `
  --names icon-one,icon-two,icon-three,icon-four,icon-five,icon-six `
  --cols 3 `
  --rows 2 `
  --bg ff3bbd
```

If global `python` is unavailable, use the bundled Codex Python runtime.

The script writes:

- one PNG per name, e.g. `icon-one.png`
- `icon-crops-preview.png`

## Sprite Sheet Workflow

For sprite sheets, generate a 3x2 grid of sequential animation frames with a
flat hot-pink chroma-key background unless the user explicitly requested another
background color:

```text
Create a sprite sheet for a mobile app animation. Exact layout: 3 columns by 2 rows,
6 sequential frames of the same character/object animation. Use a solid flat
hot-pink chroma-key background (#ff3bbd) across the entire image. The background
must be one uniform color, with no gradient, texture, lighting, shadows,
vignette, or pattern. The subject must stay the same size, same style, centered
in each cell, with large spacing from cell borders. Keep all pixels inside the
central 60% of each cell and leave at least 20% empty margin on every side. No
watermark, no text labels. Polished app/game style.
Frame 1: ...
Frame 2: ...
...
Frame 6: ...
```

Then run:

```powershell
python plugins/spritesheet-creator/scripts/process_sprite_sheet.py `
  --input assets/sprites/character-sheet.png `
  --out-dir assets/sprites/character `
  --cols 3 `
  --rows 2 `
  --bg ff3bbd `
  --frame-prefix frame `
  --gif character.gif `
  --duration 90
```

The script writes:

- `frames/frame-001.png`, `frame-002.png`, ...
- `spritesheet-transparent.png`
- `sprite-crops-preview.png`
- `character.gif`

Use GIF output for previewing timing and motion. For production animation in an
app/game, prefer the transparent PNG frames or `spritesheet-transparent.png`.

## Review

Show the user both:

- the source sheet
- the preview sheet

If the crop is not clean, regenerate with stronger spacing and a flatter
background before trying more complex local post-processing.
