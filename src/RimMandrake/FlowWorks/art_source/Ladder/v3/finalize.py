"""Conform the v3 raw renders to shipped canvases (whole-image premultiplied resize: the guides are drawn in canvas
space, so position carries over) and write candidate sets.

  ladder  384 px (drawSize 1.5). Set <x>: north = raw north_<n>, east = raw east_<e>, west = east mirrored,
          south = today's RM_Ladder_south (unchanged: the owner raised no south issue).
  spikes  256 px (drawSize 1).

    python3 finalize.py      -> Ladder/v3/out/<set>/RM_Ladder_<facing>.png, Spikes/v3/out/<x>/RM_Spikes.png
"""
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
FA = HERE.parent.parent
R = FA.parents[3]
sys.path.insert(0, str(R / "skills/generating-images/scripts"))
TEX = R / "src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Canals"
LADDER_SETS = {"a": ("A", "A"), "b": ("B", "B"), "c": ("B", "C")}
SPIKE_SETS = ("A", "B", "C")


def premul_resize(im, size):
    """Premultiplied BOX downscale (no dark halo), then alpha < 32 cleared so no faint fringe ships."""
    import numpy as np
    a = np.asarray(im.convert("RGBA"), dtype=np.float64) / 255.0
    a[..., :3] *= a[..., 3:4]
    small = np.asarray(Image.fromarray((a * 255).round().astype(np.uint8)).resize(size, Image.BOX), dtype=np.float64)
    al = small[..., 3:4]
    rgb = np.where(al > 0, small[..., :3] * 255.0 / np.maximum(al, 1), 0)
    out = np.concatenate([np.clip(rgb, 0, 255), al], axis=-1)
    out[out[..., 3] < 32] = 0
    return Image.fromarray(out.round().astype(np.uint8), "RGBA")


def main():
    for s, (n, e) in LADDER_SETS.items():
        out = HERE / "out" / s
        out.mkdir(parents=True, exist_ok=True)
        north = premul_resize(Image.open(HERE / "raw" / f"north_{n}.png"), (384, 384))
        east = premul_resize(Image.open(HERE / "raw" / f"east_{e}.png"), (384, 384))
        # hooks end just over the east rim (cell right edge x 320 on the 384 canvas): slide the drawing so its
        # right edge sits at x 336
        dx = 336 - east.getbbox()[2]
        shifted = Image.new("RGBA", east.size, (0, 0, 0, 0))
        shifted.alpha_composite(east, (dx, 0)) if dx >= 0 else shifted.paste(east.crop((-dx, 0, 384, 384)), (0, 0))
        east = shifted
        north.save(out / "RM_Ladder_north.png")
        east.save(out / "RM_Ladder_east.png")
        east.transpose(Image.FLIP_LEFT_RIGHT).save(out / "RM_Ladder_west.png")
        Image.open(TEX / "RM_Ladder_south.png").save(out / "RM_Ladder_south.png")
    for s in SPIKE_SETS:
        out = FA / "Spikes" / "v3" / "out" / s.lower()
        out.mkdir(parents=True, exist_ok=True)
        premul_resize(Image.open(FA / "Spikes" / "v3" / "raw" / f"spikes_{s}.png"), (256, 256)).save(out / "RM_Spikes.png")
    print("ok")


if __name__ == "__main__":
    main()
