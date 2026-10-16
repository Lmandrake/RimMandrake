"""raw/<tag>_<look>.png -> out/<tag>/RM_Ladder{Hung,Stowed}_<facing>.png (every candidate) and out/ (the picks).

Premultiplied BOX downscale of the WHOLE canvas to 256 px (128 px/cell x2, drawSize 1x1) so the placement the guide
fixed -- hooks on the top / bottom / right edge -- is kept; alpha < 32 zeroed, > 235 made solid. West = east mirrored.

    python3 finalize.py            (edit PICKS after looking at the candidates)
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SIZE = 256
LOOKS = {"hung_north": ("Hung", "north"), "hung_south": ("Hung", "south"), "hung_east": ("Hung", "east"),
         "stowed_north": ("Stowed", "north"), "stowed_south": ("Stowed", "south"), "stowed_east": ("Stowed", "east")}
PICKS = {look: "B" for look in LOOKS}   # 2026-10-16: whole B set (6 rungs, bolder iron, one master) -- A kept in out/A for the sheet


def conform(p: Path) -> Image.Image:
    im = Image.open(p).convert("RGBA")
    if im.size[0] != im.size[1]:
        s = max(im.size)
        sq = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        sq.alpha_composite(im, ((s - im.size[0]) // 2, (s - im.size[1]) // 2))
        im = sq
    im = im.convert("RGBa").resize((SIZE, SIZE), Image.BOX).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda v: 0 if v < 32 else (255 if v > 235 else v)))
    return im


def write(dest: Path, look: str, im: Image.Image):
    kind, fac = LOOKS[look]
    dest.mkdir(parents=True, exist_ok=True)
    im.save(dest / f"RM_Ladder{kind}_{fac}.png")
    if fac == "east":
        im.transpose(Image.FLIP_LEFT_RIGHT).save(dest / f"RM_Ladder{kind}_west.png")


def main():
    for p in sorted((HERE / "raw").glob("*_*.png")):
        tag, look = p.stem.split("_", 1)
        if look in LOOKS:
            write(HERE / "out" / tag, look, conform(p))
    for look, tag in PICKS.items():
        write(HERE / "out", look, conform(HERE / "raw" / f"{tag}_{look}.png"))
    for f in sorted((HERE / "out").glob("*.png")):
        im = Image.open(f)
        print(f.name, im.size, im.getchannel("A").getbbox())


if __name__ == "__main__":
    main()
