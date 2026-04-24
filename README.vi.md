# SpriteSheet Creator

Ngôn ngữ: [English](README.md) | [Tiếng Việt](README.vi.md) | [简体中文](README.zh-CN.md)

SpriteSheet Creator là plugin Codex local dùng để tạo và xử lý sprite sheet
theo bố cục `3 cột x 2 hàng`. Plugin giúp chuyển một ảnh sheet được tạo bằng AI
thành các frame PNG nền trong suốt, một sprite sheet nền trong suốt, ảnh preview
kiểm tra crop, và GIF preview.

## Plugin Làm Được Gì

- Tạo prompt chuẩn cho sprite sheet 3x2.
- Xóa nền chroma-key phẳng như xanh lá `#00ff00` hoặc hồng `#ff3bbd`.
- Cắt 6 frame từ một ảnh sheet dạng grid.
- Xuất từng frame PNG nền trong suốt.
- Xuất sprite sheet nền trong suốt.
- Xuất GIF preview để kiểm tra animation.
- Có thêm script phụ để cắt icon sheet theo batch.

## Quy Tắc Tạo Ảnh Nên Dùng

Khi yêu cầu model tạo sprite sheet, nên dùng các quy tắc này:

- Bố cục chính xác: `3 cột x 2 hàng`.
- Tổng số frame: `6`.
- Nền: một màu chroma-key phẳng, thường là `#00ff00` hoặc `#ff3bbd`.
- Nhân vật hoặc vật thể phải nằm giữa từng ô.
- Toàn bộ pixel của nhân vật và hiệu ứng nên nằm trong 60% vùng giữa của mỗi ô.
- Chừa ít nhất 20% khoảng trống ở mọi cạnh.
- Không thêm chữ, watermark, bóng đổ chạm qua ô khác, hoặc panel thừa.

Ví dụ prompt:

```text
Create a sprite sheet for a mobile app animation. Exact layout: 3 columns by 2 rows,
6 sequential frames of the same character. Use a solid flat green chroma-key
background (#00ff00). The character must stay the same size, same style, centered
in each cell, with large spacing from cell borders. Keep all character and effect
pixels inside the central 60% of each cell and leave at least 20% empty margin on
every side. No watermark, no text labels.
```

## Cách Dùng

Xử lý một sprite sheet 3x2 đã tạo:

```powershell
python plugins/spritesheet-creator/scripts/process_sprite_sheet.py `
  --input assets/sprites/character-sheet.png `
  --out-dir assets/sprites/character `
  --bg 00ff00 `
  --frame-prefix frame `
  --gif character.gif `
  --duration 90
```

`process_sprite_sheet.py` mặc định dùng `--cols 3 --rows 2`, nên lệnh thông
thường sẽ xuất ra 6 frame.

## Output

Script xử lý sprite sẽ tạo:

- `frames/frame-001.png`, `frames/frame-002.png`, ...
- `spritesheet-transparent.png`
- `sprite-crops-preview.png`
- file GIF được truyền vào qua `--gif`

Dùng GIF để xem nhanh timing và chuyển động. Khi đưa vào app hoặc game thật,
nên dùng các frame PNG trong suốt hoặc `spritesheet-transparent.png`.

## Cắt Icon Sheet Tùy Chọn

Plugin cũng có helper để cắt icon grid đơn giản:

```powershell
python plugins/spritesheet-creator/scripts/crop_icon_sheet.py `
  --input assets/icons/icon-sheet.png `
  --out-dir assets/icons/crops `
  --names icon-one,icon-two,icon-three,icon-four,icon-five,icon-six `
  --cols 3 `
  --rows 2 `
  --bg ff3bbd
```

## Marketplace Local Của Codex

Để test local, thêm plugin này vào `.agents/plugins/marketplace.json`:

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

## Yêu Cầu

- Python 3
- Pillow

Cài Pillow nếu môi trường Python của bạn chưa có:

```powershell
python -m pip install pillow
```

## Cấu Trúc Repo

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

## License

MIT
