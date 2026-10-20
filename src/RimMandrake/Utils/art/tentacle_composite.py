#!/usr/bin/env python3
"""tentacle_composite.py — ONE phone picture per twitch creature: body + bell + four pieces, one row per facing.

Tentacle-twitch pieces (tt_bulloo_*, tt_zhool_*) are fragments of a creature, so chat_review.py's per-job images mean
nothing for them. This lays the creature's finished body render and every piece render side by side (south, east, north
rows) at their native pixel size (shrunk only to fit a 256 px tile), labelled with job id, pixel size and drawSize.

    python3 tentacle_composite.py [--out DIR]     writes <out>/tt_bulloo_composite.png and tt_zhool_composite.png

Read-only: never installs, never touches the ledger. Art folder: ARTPIPE_STATE_DIR or /mnt/d/ClaudeWork/rimmandrake/artpipe.
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ART = Path(os.environ.get("ARTPIPE_STATE_DIR") or rm_str("artpipe")) / "_artsrc"
MIRROR = Path("/mnt/d/Luke/dev/RimMandrake/infrastructure/artpipe/_artsrc")
FACES = ("south", "east", "north")
TILE = 256
CREATURES = {
    "tt_bulloo": ("greater bulloo (RM_ColossalAerofleet)", "gapall_AA_ColossalAerofleet_v1",
                  [("bell", "tt_bulloo_bell_v1", 2.5)] + [(f"feeler {c}", f"tt_bulloo_feeler{c.lower()}_v1", 1.0) for c in "ABCD"]),
    "tt_zhool": ("zhool (RM_OcularJelly)", "gapall_AA_OcularJelly_v1",
                 [("bell", "tt_zhool_bell_v1", 1.75)] + [(f"tentacle {c}", f"tt_zhool_tentacle{c.lower()}_v1", 1.0) for c in "ABCD"]),
}


def render(job: str) -> Image.Image:
    for base in (ART, MIRROR):
        p = base / job / f"{job}.png"
        if p.is_file():
            return Image.open(p).convert("RGBA")
    raise SystemExit(f"no render PNG for {job}")


def checker(w, h):
    im = Image.new("RGBA", (w, h), (52, 48, 44, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, 16):
        for x in range(0, w, 16):
            if (x // 16 + y // 16) % 2:
                d.rectangle([x, y, x + 15, y + 15], fill=(66, 61, 56, 255))
    return im


def build(key: str, out: Path) -> Path:
    title, body, pieces = CREATURES[key]
    cols = [("body (finished render)", body, None)] + [(n, j, ds) for n, j, ds in pieces]
    f = ImageFont.load_default()
    pad, head, lab = 8, 34, 30
    W = pad + len(cols) * (TILE + pad)
    H = head + len(FACES) * (TILE + lab + pad)
    img = Image.new("RGBA", (W, H), (18, 16, 13, 255))
    d = ImageDraw.Draw(img)
    d.text((pad, 8), f"{title}: body + bell + 4 pieces, south / east / north rows. Tiles shrunk only to fit {TILE}px.", font=f, fill=(240, 200, 120))
    for r, face in enumerate(FACES):
        y0 = head + r * (TILE + lab + pad)
        for c, (name, job, ds) in enumerate(cols):
            x0 = pad + c * (TILE + pad)
            tile = checker(TILE, TILE)
            a = render(f"{job}_{face}")
            k = min(1.0, TILE / max(a.size))
            a2 = a.resize((max(1, round(a.width * k)), max(1, round(a.height * k))), Image.LANCZOS)
            tile.alpha_composite(a2, ((TILE - a2.width) // 2, (TILE - a2.height) // 2))
            img.alpha_composite(tile, (x0, y0))
            d.text((x0, y0 + TILE + 2), f"{face}: {name}", font=f, fill=(232, 220, 200))
            d.text((x0, y0 + TILE + 14), f"{job}  {a.width}x{a.height}" + (f"  draw {ds}" if ds else ""), font=f, fill=(170, 160, 140))
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{key}_composite.png"
    img.convert("RGB").save(p, optimize=True)
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default="Transient/tentacle_composites")
    a = ap.parse_args()
    for k in CREATURES:
        print(build(k, Path(a.out)))
