#!/usr/bin/env python3
"""FW_ART_POLISH_REDRAW_FOUR_SMALL_MISSES: the four small FlowWorks art misses stay fixed.

  scorch  RM_ScorchDebris_Char0..11 (installed): the outer rim is a 1 px keyline, not a ~3 px black band
          (ring 2 of the silhouette no longer near-black).
  sign    RM_StationSign (installed): no baked ground shadow (no near-black semi-transparent pixels below the board).
  bottle  Industrial RM_Bottle (installed; RM_Bottle_FreshWater draws it): keylined (outer ring dark) and simplified
          (fewer coarse colours), with the very same alpha as the kept original, so RM_Bottle_m.png still fits.
  weir    the staged spill sheets (art_source/Weir/out_photo, from weir_by_photo.crest_spill; the installed set is
          owner-kept until WEIR_LOOKS_REDRAW_ONE_PER_PIPE_STYLE installs these): a visible sheet with a white lip
          over the crest and a white foam toe at the foot, in every look and falling facing.
  judge   art_source/FourMisses/verdict.json: a judge that did not make the art ACCEPTs each of the four on the
          true-scale sheet beside it.

Sanity probes: each measure must flag the kept originals in art_source/FourMisses/before (and the installed
kept weir spills), or the instrument is blind.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
FW = ROOT / "src/RimMandrake/FlowWorks"
FM = FW / "art_source/FourMisses"
sys.path.insert(0, str(FM))
from fix_four_misses import CHARS, coarse_colours, ring_lum, rings, shadow_pixels  # noqa: E402

TEX = FW / "Textures"
LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
FAIL = []


def rgba(p):
    return np.array(Image.open(p).convert("RGBA"))


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAIL.append(msg)


def spill(p, facing):
    """(mean visible alpha, share of columns with a white lip, share with a white foam toe). North is the east art
    turned (falls east) and south its mirror (falls west): each is turned back to fall down-screen."""
    a = rgba(p).astype(float)
    if facing == "south":
        a = a[:, ::-1]
    if facing in ("north", "south"):
        a = a.transpose(1, 0, 2)
    vis = a[..., 3] > 20
    lum = a[..., :3].mean(-1)
    cols = [(x, np.nonzero(vis[:, x])[0]) for x in range(a.shape[1])]
    cols = [(x, c) for x, c in cols if len(c) >= 12]
    if not cols:
        return 0.0, 0.0, 0.0
    white = (a[..., 3] > 180) & (lum > 230)
    lip = np.mean([white[c[:2], x].any() for x, c in cols])
    toe = np.mean([white[c[-10:], x].any() for x, c in cols])
    return float(a[..., 3][vis].mean()), float(lip), float(toe)


def main():
    # scorch
    for n in CHARS:
        b, o = rgba(FM / "before" / f"{n}.png"), rgba(TEX / f"Terrain/FlowWorks/Debris/{n}.png")
        check(ring_lum(b, 2) < 6, f"probe {n} kept original has the black band (ring2 lum {ring_lum(b, 2):.0f} < 6)")
        check(ring_lum(o, 2) >= 8 and ring_lum(o, 1) < 15,
              f"{n} installed: 1 px keyline (ring1 {ring_lum(o, 1):.0f} < 15), ring2 not black ({ring_lum(o, 2):.0f} >= 8; the band read 0-2)")
        kept = (b[..., 3] == o[..., 3]) | (o[..., 3] == 0)
        check(kept.all() and (b[..., 3] != o[..., 3]).sum() < 64, f"{n} footprint (alpha) unchanged but for a cut speck")
    # sign
    b, o = rgba(FM / "before/RM_StationSign.png"), rgba(TEX / "Things/Item/DevProps/RM_StationSign.png")
    check(shadow_pixels(b) > 500, f"probe sign kept original has a baked shadow ({shadow_pixels(b)} px > 500)")
    check(shadow_pixels(o) == 0, f"RM_StationSign installed: no ground-shadow pixels ({shadow_pixels(o)})")
    check(((o[..., 3] > 0) <= (b[..., 3] > 0)).all(), "RM_StationSign: only removed pixels, nothing added")
    # bottle
    b, o = rgba(FM / "before/RM_Bottle_Industrial.png"), rgba(TEX / "Things/Item/Resource/FlowWorks/Industrial/RM_Bottle.png")
    check(ring_lum(b, 1) > 70 and coarse_colours(b) > 50,
          f"probe bottle kept original is unkeyed and photographic (ring1 {ring_lum(b, 1):.0f} > 70, colours {coarse_colours(b)} > 50)")
    check(ring_lum(o, 1) < 60, f"Industrial RM_Bottle installed: keylined (ring1 lum {ring_lum(o, 1):.0f} < 60)")
    body = rings(o[..., 3] > 128)
    lum = o[..., :3].astype(float).mean(-1)
    check(lum[body == 1].mean() < 60 and lum[body == 2].mean() < 90,
          f"Industrial RM_Bottle: the opaque body's own rings 1-2 are painted dark ({lum[body == 1].mean():.0f} < 60, {lum[body == 2].mean():.0f} < 90)")
    check(coarse_colours(o) < 0.7 * coarse_colours(b), f"Industrial RM_Bottle simplified ({coarse_colours(o)} < 0.7 x {coarse_colours(b)} coarse colours)")
    check((b[..., 3] == o[..., 3]).all(), "Industrial RM_Bottle alpha identical to the kept original (its mask still fits)")
    # weir
    for look in LOOKS:
        for f in ("east", "north", "south"):
            kept = spill(FW / f"art_source/Weir/out/{look}/RM_BankWeirSpill_{f}.png", f)
            check(kept[0] < 60 and kept[2] < 0.2, f"probe kept {look} {f} spill is a weak strip (alpha {kept[0]:.0f}, toe {kept[2]:.2f})")
            al, lip, toe = spill(FW / f"art_source/Weir/out_photo/{look}/RM_BankWeirSpill_{f}.png", f)
            check(al >= 100 and lip >= 0.9 and toe >= 0.9,
                  f"staged {look} {f} spill: a visible sheet (alpha {al:.0f} >= 100), white lip ({lip:.2f}) and foam toe ({toe:.2f}) >= 0.9")
    # judge
    vp = FM / "verdict.json"
    v = json.loads(vp.read_text()) if vp.exists() else {}
    check(bool(v.get("judge")) and v.get("judge") != v.get("maker"), f"verdict.json names a judge that is not the maker ({v.get('judge')})")
    check((FM / "sheet.png").exists() and v.get("sheet") == "sheet.png", "verdict.json judged the true-scale sheet.png beside it")
    for k in ("scorch", "sign", "bottle", "weir_spill"):
        check(str(v.get("items", {}).get(k, {}).get("verdict", "")).upper() == "ACCEPT", f"judge verdict for {k} is ACCEPT")
    print("FAIL" if FAIL else "PASS", f"{len(FAIL)} failure(s)")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
