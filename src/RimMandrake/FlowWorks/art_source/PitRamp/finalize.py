"""raw/ picks -> out/RM_PitRamp_<facing>.png at 256 px (128 px/cell target x2, as RM_Ladder).

Picks (2026-10-15, owner by card "Make both today"): north = raw/ramp_north_b, south = raw/ramp_south_b,
east = raw/ramp_east_c (edit of north_b rotated, relit so the right/high end is brightest, side wedge added),
west = east mirrored. Premultiplied BOX downscale (no dark halo, no LANCZOS ringing), alpha < 32 zeroed.
Each facing was generated as `codex_image.py edit --model gpt-6.1-sol` with guides/guide_<facing>.png (guide.py)
as image 1; prompts are in Transient/ramp_ladder_art_2026-10-15/ART.md.
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
PICKS = {"north": "ramp_north_b", "south": "ramp_south_b", "east": "ramp_east_c"}
SIZE = 256


def conform(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA").convert("RGBa").resize((SIZE, SIZE), Image.BOX).convert("RGBA")
    a = im.getchannel("A").point(lambda v: 0 if v < 32 else (255 if v > 235 else v))
    im.putalpha(a)
    return im


def main():
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    done = {f: conform(Image.open(HERE / "raw" / f"{p}.png")) for f, p in PICKS.items()}
    # east_c's side wedge reaches the canvas bottom: inset it 12 px so the silhouette sits inside the cell like N/S.
    e = done["east"].convert("RGBa").resize((SIZE - 12, SIZE - 12), Image.BOX).convert("RGBA")
    done["east"] = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    done["east"].alpha_composite(e, (6, 3))
    done["west"] = done["east"].transpose(Image.FLIP_LEFT_RIGHT)
    for f, im in done.items():
        im.save(out / f"RM_PitRamp_{f}.png")
        print(f, im.size, im.getchannel("A").getbbox())


if __name__ == "__main__":
    main()
