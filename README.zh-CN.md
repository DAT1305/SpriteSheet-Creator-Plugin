# SpriteSheet Creator

语言：[English](README.md) | [Tiếng Việt](README.vi.md) | [简体中文](README.zh-CN.md)

SpriteSheet Creator 是一个本地 Codex 插件，用于生成和处理
`3 列 x 2 行` 的色键背景精灵图。它可以把一张 AI 生成的精灵图表
转换为透明 PNG 帧、透明精灵图、裁剪预览图，以及 GIF 动画预览。

## 功能

- 为干净的 3x2 精灵图生成提示词。
- 移除纯色色键背景，例如绿色 `#00ff00` 或粉色 `#ff3bbd`。
- 从网格图中裁剪 6 个动画帧。
- 导出透明 PNG 帧。
- 导出透明精灵图。
- 导出 GIF 预览，方便检查动画效果。
- 额外提供一个批量图标裁剪辅助脚本。

## 推荐生成规则

向图像模型请求生成精灵图时，建议使用以下规则：

- 精确布局：`3 列 x 2 行`。
- 总帧数：`6`。
- 背景：单一纯色色键，通常使用 `#00ff00` 或 `#ff3bbd`。
- 角色或物体必须居中放在每个格子里。
- 所有角色和特效像素应保持在每个格子中央 60% 的范围内。
- 每一侧至少保留 20% 的空白边距。
- 不要添加文字、水印、跨格阴影或多余面板。

提示词示例：

```text
Create a sprite sheet for a mobile app animation. Exact layout: 3 columns by 2 rows,
6 sequential frames of the same character. Use a solid flat green chroma-key
background (#00ff00). The character must stay the same size, same style, centered
in each cell, with large spacing from cell borders. Keep all character and effect
pixels inside the central 60% of each cell and leave at least 20% empty margin on
every side. No watermark, no text labels.
```

## 使用方法

处理一张生成好的 3x2 精灵图：

```powershell
python plugins/spritesheet-creator/scripts/process_sprite_sheet.py `
  --input assets/sprites/character-sheet.png `
  --out-dir assets/sprites/character `
  --bg 00ff00 `
  --frame-prefix frame `
  --gif character.gif `
  --duration 90
```

`process_sprite_sheet.py` 默认使用 `--cols 3 --rows 2`，因此正常运行会
导出 6 个帧。

## 输出文件

精灵图处理脚本会生成：

- `frames/frame-001.png`, `frames/frame-002.png`, ...
- `spritesheet-transparent.png`
- `sprite-crops-preview.png`
- 通过 `--gif` 指定的 GIF 文件

GIF 适合快速检查动画节奏和动作。实际用于 app 或游戏时，建议使用透明
PNG 帧或 `spritesheet-transparent.png`。

## 可选图标表裁剪

插件也包含一个简单图标网格裁剪工具：

```powershell
python plugins/spritesheet-creator/scripts/crop_icon_sheet.py `
  --input assets/icons/icon-sheet.png `
  --out-dir assets/icons/crops `
  --names icon-one,icon-two,icon-three,icon-four,icon-five,icon-six `
  --cols 3 `
  --rows 2 `
  --bg ff3bbd
```

## Codex 本地 Marketplace

本地测试时，可以把插件加入 `.agents/plugins/marketplace.json`：

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

## 环境要求

- Python 3
- Pillow

如果当前 Python 环境没有 Pillow，可以安装：

```powershell
python -m pip install pillow
```

## 仓库结构

```text
plugins/spritesheet-creator/
  .codex-plugin/plugin.json
  README.md
  README.vi.md
  README.zh-CN.md
  assets/
  scripts/
    crop_icon_sheet.py
    process_sprite_sheet.py
  skills/
    spritesheet-creator/
      SKILL.md
```

## 许可证

MIT
