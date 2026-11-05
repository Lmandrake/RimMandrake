#!/usr/bin/env python3
"""Pins SUSPENSION_BRIDGE_REDRAW_HEAVY_JUST_PAINTED on the art the game LOADS: the installed FlowWorks Textures, the base
set and every look (Scrapper, Industrial, Modern, Futuristic) the style picker can draw.

The owner (2026-10-24): "the heavy one is just a recolored timber one, and that makes NO sense"; Steel: "a real
'suspension bridge' here with raised towers at the anchor and criss-cross cables"; Heavy: "Steel construction, paved
crossing, no cables, cement base"; "Nothing in the suspension bridge should have red"; "the player can paint them, however
Rimworld does that". He asked for a permanent check that FAILS on the old art (2026-10-24, "find ways to test for those
defects ... so we don't repeat mistakes"). Every check is probed both ways: on the art he rejected (frozen in
fixtures_rejected/, the Scrapper look he saw in game: its Heavy deck is the Timber deck in rust plates) and on a synthetic
case, so a pass is the instrument seeing, not a blind zero.
"""
from __future__ import annotations

import inspect
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
FW = HERE.parents[1]
sys.path.insert(0, str(HERE))
import suspension_redesign as S  # noqa: E402

TEX = FW / "Textures"
REJECTED = HERE / "fixtures_rejected"
DEFS = FW / "Defs/Pits/ThingDefs/RM_SuspensionBridges.xml"
STYLES = FW / "Defs/Pits/ThingDefs/RM_SuspensionStyles.xml"
ROPES = FW / "Source/RM_DrawbridgeMath.cs"
PAINTABLE = ("RM_SuspensionDeck_Steel", "RM_SuspensionDeck_SteelGrated", "RM_SuspensionAnchor_Steel",
             "RM_SuspensionDeck_Heavy", "RM_SuspensionDeck_HeavyGrated", "RM_SuspensionAnchor_Heavy",
             "RM_SuspensionJetty_Steel", "RM_SuspensionJetty_Heavy")
MASKED = PAINTABLE[:6]                       # the redrawn parts: CutoutComplex with a _m mask on every picture
SETS = ("base",) + S.LOOKS

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def rel(look, name):
    """Textures-relative path (no .png) of a redrawn piece in a set, named as the base set names it."""
    if look == "base":
        return f"{S.THINGS}/{name}"
    return f"{S.LOOK_DIR}/{look}/{S.LOOK_NAME.get(name, name)}"


def load(r):
    return Image.open(TEX / (r + ".png")).convert("RGBA")


def load_mask(r):
    return Image.open(TEX / (r + "_m.png")).convert("RGBA")


def timber(look):
    if look == "base":
        return load(f"{S.THINGS}/RM_SuspensionDeck_Timber"), load(f"{S.THINGS}/RM_SuspensionAnchor_Timber_south")
    d = f"{S.LOOK_DIR}/{look}"
    deck = TEX / f"{d}/RM_SuspensionDeck_Timber.png"
    deck = deck if deck.is_file() else TEX / f"{d}/RM_SuspensionDeck.png"
    return Image.open(deck).convert("RGBA"), load(f"{d}/RM_SuspensionAnchor_Timber_south")


def test_no_red():
    for n in ("RM_SuspensionDeck_Steel", "RM_SuspensionDeck_Heavy", "RM_SuspensionAnchor_Steel_south",
              "RM_SuspensionAnchor_Heavy_south"):
        im = Image.open(REJECTED / f"Scrapper_{n}.png")
        check(not S.no_red(im), f"no_red rejects the rejected Scrapper {n} (red share {S.red_share(im):.3f})")
    check(not S.no_red(Image.new("RGBA", (64, 64), (170, 60, 40, 255))), "no_red rejects a rust-red square")
    check(S.no_red(Image.new("RGBA", (64, 64), (150, 126, 96, 255))), "no_red passes bare wood (hue 34)")
    for look in SETS:
        for n in list(S.pieces_names()) + [d + "_Atlas" for d in S.DECKS]:
            r = rel(look, n) if not n.endswith("_Atlas") else rel(look, n[:-6]) + "_Atlas"
            im = load(r)
            check(S.no_red(im), f"no red in {r} (share {S.red_share(im):.4f})")


def test_distinct():
    a, b = Image.open(REJECTED / "Scrapper_RM_SuspensionDeck_Heavy.png"), timber("Scrapper")[0]
    check(not S.distinct(a, b), f"distinct() calls the rejected Scrapper Heavy deck a recoloured Timber deck "
                                f"(edge corr {S.structural_similarity(a, b):.2f})")
    im = load(rel("base", "RM_SuspensionDeck_Steel"))
    arr = np.asarray(im).copy()
    arr[..., [0, 2]] = arr[..., [2, 0]]
    check(not S.distinct(im, Image.fromarray(arr)), "distinct() calls a channel-swapped picture the same drawing")
    for look in SETS:
        tdeck, tanchor = timber(look)
        sd, hd = load(rel(look, "RM_SuspensionDeck_Steel")), load(rel(look, "RM_SuspensionDeck_Heavy"))
        for kind, im in (("Steel", sd), ("Heavy", hd)):
            check(S.distinct(im, tdeck), f"{look}: the {kind} deck is not a recoloured Timber deck "
                                         f"(corr {S.structural_similarity(im, tdeck):.2f})")
        check(S.distinct(sd, hd), f"{look}: the Steel and Heavy decks are different drawings")
        check(S.distinct(load(rel(look, "RM_SuspensionDeck_SteelGrated")), load(rel(look, "RM_SuspensionDeck_HeavyGrated"))),
              f"{look}: the Steel and Heavy grated decks are different drawings")
        for f in S.FACINGS:
            h, s = load(rel(look, f"RM_SuspensionAnchor_Heavy_{f}")), load(rel(look, f"RM_SuspensionAnchor_Steel_{f}"))
            check(S.distinct(h, s), f"{look}: the Steel and Heavy {f} anchors are different drawings")
        h, s = load(rel(look, "RM_SuspensionAnchor_Heavy_south")), load(rel(look, "RM_SuspensionAnchor_Steel_south"))
        check(S.distinct(h, tanchor) and S.distinct(s, tanchor), f"{look}: neither south anchor is a recoloured Timber anchor")


def _post_runs(im, mk, x0, x1):
    """Tallest vertical run of opaque steel (mask red) in columns x0..x1 of a 256 px picture."""
    a = np.asarray(im)[..., 3] > 200
    r = np.asarray(mk)[..., 0] > 128
    col = (a & r)[:, x0:x1].any(axis=1)
    best = cur = 0
    for v in col:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def towers(im, mk):
    """The Steel portal: a steel post at least 120 px tall standing at each side of the picture (the I-beam towers)."""
    return min(_post_runs(im, mk, 4, 24), _post_runs(im, mk, S.N - 24, S.N - 4)) >= 120


def main_cable(im, mk):
    """A steel main cable running the whole outer edge of a Steel deck picture (opaque, masked, in every row)."""
    w = int(10 * S.K)
    a, m = np.asarray(im)[:, :w, 3] > 200, np.asarray(mk)[:, :w, 0] > 128
    return bool((a & m).any(axis=1).mean() > 0.98)


def unpainted(im, mk):
    """Opaque pixels left out of the paint mask (the cement and wood that must keep their own colour)."""
    return int(((np.asarray(im)[..., 3] > 200) & (np.asarray(mk)[..., 0] < 64)).sum())


def test_steel_shape():
    old = Image.open(REJECTED / "Scrapper_RM_SuspensionAnchor_Steel_south.png").convert("RGBA")
    check(not towers(old, Image.new("RGBA", old.size, (255, 0, 0, 255))),
          "towers() finds no portal on the rejected Scrapper Steel anchor (its bollards), even with all of it masked")
    for look in SETS:
        for f in ("south", "north"):
            r = rel(look, f"RM_SuspensionAnchor_Steel_{f}")
            check(towers(load(r), load_mask(r)), f"{r}: raised steel towers at both sides")
        r = rel(look, "RM_SuspensionDeck_Steel")
        check(main_cable(load(r), load_mask(r)), f"{r}: a steel main cable runs the whole edge")
    full = Image.new("RGBA", (S.N, S.N), (255, 0, 0, 255))
    check(not main_cable(Image.new("RGBA", (S.N, S.N)), full), "main_cable() finds no cable on an empty picture")
    hv = rel("base", "RM_SuspensionDeck_Heavy")
    check(not main_cable(load(hv), Image.new("RGBA", (S.N, S.N))), "main_cable() finds no cable where nothing is steel")
    # the owner: Heavy has "no cables". Every Heavy drawing is built without the cable stroke the Steel ones use, and the
    # installed pictures are exactly those drawings (test_generator_match)
    heavy_src = "".join(inspect.getsource(f) for f in (S.heavy_deck, S._truss_band, S.heavy_anchor, S._portal_face))
    check("_cable(" in inspect.getsource(S.steel_anchor), "the cable stroke is visible to this check (Steel uses it)")
    check("_cable(" not in heavy_src and "CABLE" not in heavy_src, "no Heavy drawing strokes a cable")


def _rope_keys(src):
    return set(re.findall(r'\{\s*"([^"]+)",\s*new\[\]\s*\{\s*new RopeArt', src))


def test_no_ropes():
    probe = '{ "Scrapper/Heavy/east", new[] { new RopeArt(0.2, 0.05, 0.4, 0.9) } },'
    check(_rope_keys(probe) == {"Scrapper/Heavy/east"}, "the rope-table reader sees a Heavy row")
    keys = _rope_keys(ROPES.read_text())
    check(any("/Timber/" in k for k in keys), f"the rope-table reader sees the Timber rows ({len(keys)} rows)")
    bad = sorted(k for k in keys if "/Steel/" in k or "/Heavy/" in k)
    check(not bad, f"no rope is drawn on a Steel or Heavy anchor (rows: {bad[:4]})")


def test_paint():
    root = ET.parse(DEFS).getroot()
    by = {d.findtext("defName"): d for d in root.iter("ThingDef")}
    for n in PAINTABLE:
        d = by.get(n)
        check(d is not None and d.findtext("building/paintable") == "true", f"{n} has <building><paintable>true")
    for n in MASKED:
        check(by[n].findtext("graphicData/shaderType") == "CutoutComplex", f"{n} draws CutoutComplex (its _m mask)")
    styles = {d.findtext("defName"): d for d in ET.parse(STYLES).getroot().iter("ThingStyleDef")}
    for n in MASKED:
        for look in S.LOOKS:
            st = styles.get(f"{n}_{look}")
            ok = st is not None and st.findtext("graphicData/shaderType") == "CutoutComplex"
            tp = st.findtext("graphicData/texPath") if st is not None else None
            files = [tp] if tp and tp.endswith("_Atlas") else [f"{tp}_{f}" for f in S.FACINGS] if tp else []
            ok = ok and all((TEX / (p + ".png")).is_file() and (TEX / (p + "_m.png")).is_file() for p in files)
            check(ok, f"{n}_{look}: CutoutComplex, and its texPath {tp} resolves with a mask")
    for look in SETS:
        for n in S.pieces_names():
            r = rel(look, n)
            check(S.mask_ok(load(r), load_mask(r)), f"{r} has a paint mask on its steel")
        for n in ["RM_SuspensionDeck_Steel", "RM_SuspensionDeck_Heavy"] + \
                 [f"RM_SuspensionAnchor_{t}_{f}" for t in ("Steel", "Heavy") for f in S.FACINGS]:
            r = rel(look, n)
            k = unpainted(load(r), load_mask(r))
            check(k > 0.2 * 256 * 256, f"{r}: cement/wood stays unpainted ({k} px outside the mask)")
    r = rel("base", "RM_SuspensionDeck_Steel")
    check(unpainted(load(r), Image.new("RGBA", (S.N, S.N), (255, 0, 0, 255))) == 0,
          "unpainted() sees a mask that paints everything (cement and wood would take the paint)")
    check(not S.mask_ok(Image.new("RGBA", (256, 256)), Image.new("RGBA", (256, 256), (255, 0, 0, 255))),
          "mask_ok rejects a mask painting thin air")


def test_generator_match():
    """The installed pictures and masks ARE the generator's (so the checks on the drawings hold for the shipped files)."""
    with tempfile.TemporaryDirectory(prefix="susp_redesign_") as tmp:
        want = S.install_set(tmp)
    diff = []
    for r, (im, mk) in want.items():
        for got, exp in ((TEX / (r + ".png"), im), (TEX / (r + "_m.png"), mk)):
            if not got.is_file() or not np.array_equal(np.asarray(Image.open(got).convert("RGBA")), np.asarray(exp.convert("RGBA"))):
                diff.append(got.name)
    check(len(want) == 14 * len(SETS), f"the generator makes {len(want)} pictures (14 per set x {len(SETS)} sets)")
    check(not diff, f"every installed picture and mask matches the generator ({len(diff)} differ: {diff[:3]})")
    im, mk = want[rel("base", "RM_SuspensionDeck_Heavy")]
    bad = np.asarray(im).copy()
    bad[100, 100, 0] ^= 1
    check(not np.array_equal(np.asarray(im), bad), "a one-pixel edit is a mismatch to this check")


def main():
    test_no_red()
    test_distinct()
    test_steel_shape()
    test_no_ropes()
    test_paint()
    test_generator_match()
    print(f"{'FAILED ' + str(len(FAILS)) if FAILS else 'all ok'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
