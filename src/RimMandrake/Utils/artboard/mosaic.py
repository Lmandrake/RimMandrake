"""Labelled mosaics: one image a model (tier b) or the owner (tier c) reads instead of N crops."""
import math

from PIL import Image, ImageDraw, ImageFont


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                                   # Pillow < 10.1
        return ImageFont.load_default()


def build(tiles, out_path, tile_px=192, cols=None, caption_lines=2, bg=(40, 32, 26)):
    """tiles: [(label, PIL.Image, [caption lines])]. Crops are scaled UP with NEAREST (never blurred,
    never down-resolved below their captured size unless they exceed tile_px). Returns the layout:
    [{label, x, y, w, h}] in mosaic pixels, so a model's answer can be traced to a tile."""
    n = len(tiles)
    if n == 0:
        return []
    cols = cols or max(1, min(8, int(math.ceil(math.sqrt(n)))))
    rows = int(math.ceil(n / cols))
    cap_h = 18 * caption_lines + 6
    W, H = cols * (tile_px + 8) + 8, rows * (tile_px + cap_h + 8) + 8
    board = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(board)
    f_lab, f_cap = _font(16), _font(13)
    layout = []
    for i, (label, im, caps) in enumerate(tiles):
        c, r = i % cols, i // cols
        x0, y0 = 8 + c * (tile_px + 8), 8 + r * (tile_px + cap_h + 8)
        s = min(tile_px / im.width, tile_px / im.height)
        resample = Image.NEAREST if s >= 1 else Image.LANCZOS
        t = im.convert("RGB").resize((max(1, int(im.width * s)), max(1, int(im.height * s))), resample)
        board.paste(t, (x0 + (tile_px - t.width) // 2, y0 + (tile_px - t.height) // 2))
        d.rectangle([x0 - 1, y0 - 1, x0 + tile_px, y0 + tile_px], outline=(120, 100, 80))
        d.rectangle([x0, y0, x0 + 34, y0 + 20], fill=(0, 0, 0))
        d.text((x0 + 3, y0 + 2), label, fill=(255, 230, 120), font=f_lab)
        for k, line in enumerate((caps or [])[:caption_lines]):
            d.text((x0, y0 + tile_px + 4 + 18 * k), line[:int(tile_px / 6.5)], fill=(235, 225, 210), font=f_cap)
        layout.append({"label": label, "x": x0, "y": y0, "w": tile_px, "h": tile_px})
    board.save(out_path)
    return layout
