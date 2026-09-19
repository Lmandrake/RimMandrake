#!/usr/bin/env python3
"""raw -> key -> achromatic -> conform (per-bodytype ref) -> validate -> place.

Companion to gen_matrix.py. Takes whatever has actually been generated in
Transient/art_review_desert_wraps/matrix_raw/ (the codex imagegen quota can
and did run out mid-batch -- rc=1 "resets in about 3 hours 34 minutes",
2026-09-18 ~14:18) and turns it into shippable, validated final PNGs at the
correct Armoury/StarWarsRaces texture paths. Safe to re-run: skips any name
whose FINAL file already exists, so it always processes only what is new
since the last run.
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/mnt/d/Luke/dev/Rimworld")
RAW = ROOT / "Transient/art_review_desert_wraps/matrix_raw"
WORK = ROOT / "Transient/art_review_desert_wraps/matrix_work"
WORK.mkdir(parents=True, exist_ok=True)
BODYREF = ROOT / "Transient/art_review_desert_wraps/bodytype_refs"
GI = ROOT / "skills/generating-images/scripts"
GS = ROOT / "skills/generating-rimworld-sprites/scripts"

# style slug -> Armoury Textures subfolder
WRAP_STYLE_DIR = {
    "wrap_A_bound": "Spiral",
    "wrap_B_coil": "Banded",
    "wrap_C_cowl": "Segmented",
    "wrap_D_weathered": "Draped",
}
HEAD_STYLE_DIR = {
    "head_H1_pot": "HeadPot",
    "head_H2_browridge": "HeadRidged",
}
ARMOURY_TEX = ROOT / "src/RimStarWars/Armoury/Textures/SWApparel/DesertWraps"
RACES_TEX = ROOT / "src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW/SWX/Pawn/HeadType/desert_nomad"

WRAP_RE = re.compile(r"^(wrap_[A-Z]_\w+)__(Male|Female|Fat|Hulk|Thin)_(south|north|east)$")
HEAD_RE = re.compile(r"^(head_H[12]_\w+)__(south|north|east)$")


# validate_sprite.py's ALPHA_SOLID: anything below this is invisible on screen
# (<12.5% opacity) yet still counts as subject, so it inflates the measured bbox
# and makes conform_sprite scale the art DOWN to fit a box the fringe widened.
# Measured 2026-09-19 on the placed 49: Banded/Wraps_Male_east and
# Spiral/Wraps_Female_east carried a fringe reaching 3.0% and 6.8% of canvas
# beyond the silhouette, both REJECT-grade. Snapping it to 0 changes nothing a
# player can see and restores honest geometry -- the skill's own remedy
# ("fix at the export step rather than by re-rendering").
ALPHA_FLOOR = 32


def floor_alpha(p: Path):
    """Snap sub-visible alpha to fully transparent, in place."""
    im = np.asarray(Image.open(p).convert("RGBA")).astype(np.uint8)
    a = np.where(im[..., 3] < ALPHA_FLOOR, 0, im[..., 3]).astype(np.uint8)
    Image.fromarray(np.dstack([im[..., 0], im[..., 1], im[..., 2], a]),
                    "RGBA").save(p)


def achromatic(src: Path, dst: Path):
    im = np.asarray(Image.open(src).convert("RGBA")).astype(np.uint8)
    g = im[..., 1]
    a = np.where(im[..., 3] < ALPHA_FLOOR, 0, im[..., 3]).astype(np.uint8)
    out = np.dstack([g, g, g, a])
    Image.fromarray(out, "RGBA").save(dst)


def hue_report(p: Path):
    im = np.asarray(Image.open(p).convert("RGBA")).astype(int)
    a = im[..., 3] > 0
    rgb = im[..., :3][a]
    if rgb.size == 0:
        return 0.0, 0.0, 0
    mx, mn = rgb.max(1), rgb.min(1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0.0)
    return float(sat.max()), float(sat.mean()), int(a.sum())


def process_one(name: str, bodyref: Path, final: Path):
    raw = RAW / f"{name}.png"
    cut = WORK / f"{name}_cut.png"
    gry = WORK / f"{name}_gray.png"
    subprocess.run([sys.executable, str(GI / "chroma_key.py"),
                    "--input", str(raw), "--out", str(cut)],
                   check=True, capture_output=True)
    achromatic(cut, gry)
    final.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(GS / "conform_sprite.py"),
                        "--reference", str(bodyref), "--input", str(gry),
                        "--out", str(final)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"CONFORM FAIL {name}: {r.stderr.strip()}")
        return False
    # Floor AGAIN, on the conformed output: the downscale averages thin wisps of
    # real art against transparency and lands them at alpha 1-31 -- invisible on
    # screen, but they extend the measured bbox tens of px past the body and so
    # corrupt every geometric check. Measured: 112-131 such px pushed two cells'
    # bbox ~50px left of the silhouette. Flooring before conform cannot catch
    # these because conform is what creates them.
    floor_alpha(final)
    v = subprocess.run([sys.executable, str(GS / "validate_sprite.py"),
                        "--reference", str(final), "--describe"],
                       capture_output=True, text=True)
    mx, mean, npx = hue_report(final)
    ok = mx < 0.02  # achromatic tolerance
    print(f"### {name} -> {final.relative_to(ROOT)}  maxsat={mx:.4f} "
          f"alphapx={npx} {'ACHROMATIC-OK' if ok else 'HUE-DEFECT'}")
    print(v.stdout.strip().splitlines()[-1] if v.stdout.strip() else v.stderr.strip())
    return True


def main():
    done, missing = [], []
    for raw in sorted(RAW.glob("*.png")):
        name = raw.stem
        m = WRAP_RE.match(name)
        if m:
            style, bodytype, direction = m.groups()
            styledir = WRAP_STYLE_DIR[style]
            final = ARMOURY_TEX / styledir / f"Wraps_{bodytype}_{direction}.png"
            bodyref = BODYREF / f"{bodytype}.png"
            if final.exists():
                continue
            if process_one(name, bodyref, final):
                done.append(str(final.relative_to(ROOT)))
            continue
        m = HEAD_RE.match(name)
        if m:
            style, direction = m.groups()
            stem = HEAD_STYLE_DIR[style]
            final = RACES_TEX / f"{stem}_{direction}.png"
            bodyref = BODYREF / "Head.png"
            if final.exists():
                continue
            if process_one(name, bodyref, final):
                done.append(str(final.relative_to(ROOT)))
            continue
        print(f"SKIP (no name match): {name}")
    print(f"\nPROCESSED {len(done)} file(s) this run.")
    for d in done:
        print(" ", d)


if __name__ == "__main__":
    main()
