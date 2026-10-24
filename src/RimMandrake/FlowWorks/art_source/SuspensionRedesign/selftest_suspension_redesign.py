#!/usr/bin/env python3
"""Pins SUSPENSION_BRIDGE_REDRAW_HEAVY_JUST_PAINTED: the Steel and Heavy suspension bridges are two drawings, neither is
red, and both are wired for the player's paint.

The owner (2026-10-24): "the heavy one is just a recolored timber one, and that makes NO sense"; "Nothing in the
suspension bridge should have red"; "the player can paint them, however Rimworld does that". Each check is probed both
ways: it fails on the art he rejected (the Scrapper look he saw in game: Heavy deck = the Timber deck in rust plates)
and on a synthetic case, so a pass is the instrument seeing, not a blind zero.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
FW = HERE.parents[1]
sys.path.insert(0, str(HERE))
import suspension_redesign as S  # noqa: E402

SCRAP = FW / "Textures/RimMandrake/FlowWorks/SuspensionBridge/Scrapper"
BASE = FW / "Textures" / S.THINGS
DEFS = FW / "Defs/Pits/ThingDefs/RM_SuspensionBridges.xml"
PAINTABLE = ("RM_SuspensionDeck_Steel", "RM_SuspensionDeck_SteelGrated", "RM_SuspensionAnchor_Steel",
             "RM_SuspensionDeck_Heavy", "RM_SuspensionDeck_HeavyGrated", "RM_SuspensionAnchor_Heavy",
             "RM_SuspensionJetty_Steel", "RM_SuspensionJetty_Heavy")

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def piece(name):
    return PCS[f"{S.THINGS}/{name}"]


PCS = S.pieces()


def test_no_red():
    # the instrument sees red: the rejected Scrapper Steel/Heavy art and a plain red square fail it
    for n in ("RM_SuspensionDeck_Steel", "RM_SuspensionDeck_Heavy", "RM_SuspensionAnchor_Steel_south",
              "RM_SuspensionAnchor_Heavy_south"):
        im = Image.open(SCRAP / f"{n}.png")
        check(not S.no_red(im), f"no_red rejects the Scrapper {n} he saw (red share {S.red_share(im):.3f})")
    check(not S.no_red(Image.new("RGBA", (64, 64), (170, 60, 40, 255))), "no_red rejects a rust-red square")
    check(S.no_red(Image.new("RGBA", (64, 64), (150, 126, 96, 255))), "no_red passes bare wood (hue 34)")
    allp = dict(PCS)
    allp.update(S.atlases(PCS, _tmp()))
    for rel, (im, _) in allp.items():
        check(S.no_red(im), f"no red in {Path(rel).name} (share {S.red_share(im):.4f})")


def test_distinct():
    # the instrument sees a recolour: Scrapper Heavy deck vs Scrapper Timber deck, and a picture vs its channel swap
    a, b = Image.open(SCRAP / "RM_SuspensionDeck_Heavy.png"), Image.open(SCRAP / "RM_SuspensionDeck.png")
    check(not S.distinct(a, b), f"distinct() calls the Scrapper Heavy deck a recoloured Timber deck "
                                f"(edge corr {S.structural_similarity(a, b):.2f})")
    im = piece("RM_SuspensionDeck_Steel")[0]
    arr = np.asarray(im).copy()
    arr[..., [0, 2]] = arr[..., [2, 0]]
    check(not S.distinct(im, Image.fromarray(arr)), "distinct() calls a channel-swapped picture the same drawing")
    timber = {"deck": Image.open(BASE / "RM_SuspensionDeck_Timber.png"),
              "scrap_deck": Image.open(SCRAP / "RM_SuspensionDeck.png")}
    for kind in ("RM_SuspensionDeck_Steel", "RM_SuspensionDeck_Heavy"):
        for tn, t in timber.items():
            check(S.distinct(piece(kind)[0], t), f"{kind} is not a recoloured timber {tn}")
    check(S.distinct(piece("RM_SuspensionDeck_Steel")[0], piece("RM_SuspensionDeck_Heavy")[0]),
          "the Steel and Heavy decks are different drawings")
    check(S.distinct(piece("RM_SuspensionDeck_SteelGrated")[0], piece("RM_SuspensionDeck_HeavyGrated")[0]),
          "the Steel and Heavy grated decks are different drawings")
    for f in S.FACINGS:
        h, s = piece(f"RM_SuspensionAnchor_Heavy_{f}")[0], piece(f"RM_SuspensionAnchor_Steel_{f}")[0]
        check(S.distinct(h, s), f"the Steel and Heavy {f} anchors are different drawings")
        t = Image.open(BASE / f"RM_SuspensionAnchor_Timber_{f}.png")
        check(S.distinct(h, t) and S.distinct(s, t), f"neither {f} anchor is a recoloured timber anchor")


def _opaque_unmasked(im, mk):
    a = np.asarray(im)[..., 3] > 200
    r = np.asarray(mk)[..., 0] < 64
    return int((a & r).sum())


def test_paint():
    root = ET.parse(DEFS).getroot()
    by = {d.findtext("defName"): d for d in root.iter("ThingDef")}
    for n in PAINTABLE:
        d = by.get(n)
        check(d is not None and d.findtext("building/paintable") == "true", f"{n} has <building><paintable>true")
    for rel, (im, mk) in PCS.items():
        check(S.mask_ok(im, mk), f"{Path(rel).name} has a paint mask on its steel")
    # cement and wood stay out of the paint: the plank deck, the paved deck and every anchor leave some opaque unmasked
    for n in ["RM_SuspensionDeck_Steel", "RM_SuspensionDeck_Heavy"] + \
             [f"RM_SuspensionAnchor_{t}_{f}" for t in ("Steel", "Heavy") for f in S.FACINGS]:
        im, mk = piece(n)
        k = _opaque_unmasked(im, mk)
        check(k > 0.2 * 256 * 256, f"{n}: cement/wood stays unpainted ({k} px outside the mask)")
    check(not S.mask_ok(Image.new("RGBA", (256, 256)), Image.new("RGBA", (256, 256), (255, 0, 0, 255))),
          "mask_ok rejects a mask painting thin air")


_T = []


def _tmp():
    if not _T:
        import tempfile
        _T.append(tempfile.mkdtemp(prefix="susp_redesign_"))
    return _T[0]


def main():
    test_no_red()
    test_distinct()
    test_paint()
    if _T:
        import shutil
        shutil.rmtree(_T[0], ignore_errors=True)
    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all ok'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
