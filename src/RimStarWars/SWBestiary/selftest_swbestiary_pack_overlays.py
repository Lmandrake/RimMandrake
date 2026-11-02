#!/usr/bin/env python3
"""selftest_swbestiary_pack_overlays.py -- every adult land body of every packAnimal race in src/ shows
real saddlebags when loaded (PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS).

Run bare: python3 src/RimStarWars/SWBestiary/selftest_swbestiary_pack_overlays.py   (exit 0 = clean)

Rule, per adult graphic and facing: <texPath>Pack_<facing>.png exists, is not the transparent placeholder,
is not a byte copy of the body, has the body's aspect (same quad), and its gear lies mostly on the
body's silhouette. Juvenile `_j` and `*_Swimming` bodies are waived by the item. Break probes prove each
check can fail; the census must see at least 50 races and Ronto, and the group table must hold them all.

Shared, fitted: every graphic the fit installed (art/pack_overlay_installed.json) must be pixel-equal to
pack_overlay_fit.render() of its group's shared render packoverlay_<group>_v1_<facing> (artpipe state dir)
on the body as it is NOW. A hand-painted or flat-filled Pack fails, and so does a Pack fitted to a body that
was redrawn after the fit (re-run `pack_overlay_fit.py --apply --refit`). Every other adult Pack is named
donor art in DONOR_PACK, so nothing reaches the gear checks by being neither.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "art"))
import pack_overlay_fit as fit  # noqa: E402

FAILS = []
MIN_ON_BODY = 0.35     # share of gear pixels over opaque body; winged bodies keep gear on a thin trunk
MIN_COVER = 0.004      # the gear must show at play zoom
# donor Pack art drawn for these very bodies, which rims a foreshortened back by design (looked at 2026-11-02)
DRAWN_FOR_THE_BODY = ("swanimals/Behemoth/JawaBehemoth_f", "swanimals/Behemoth/JawaBehemoth_m")
# drawn Pack art the fit kept (real_pack_exists), not made from the shared overlays (measured 2026-11-02)
DONOR_PACK = DRAWN_FOR_THE_BODY + ("swanimals/Bantha/Bantha", "Things/Pawn/Animal/RM_Holcorobeus/RM_Holcorobeus")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def judge(pack, body, on_body=True):
    """Why this Pack picture is not real gear on this body, or None."""
    if pack.size == (4, 4) or pack.getchannel("A").getbbox() is None:
        return "placeholder"
    if abs(pack.width / pack.height - body.width / body.height) > 0.01:
        return "aspect differs from the body"
    b = body.resize(pack.size, Image.BILINEAR)
    if np.array_equal(np.array(b), np.array(pack)):
        return "byte copy of the body"
    g = np.array(pack.getchannel("A")) > 128
    if g.mean() < MIN_COVER:
        return "gear too small: %.3f of canvas" % g.mean()
    on = (np.array(b.getchannel("A")) > 128)[g].mean()
    if on_body and on < MIN_ON_BODY:
        return "gear off the body: %.2f on silhouette" % on
    return None


def same(a, b):
    """Pixel-equal RGBA pictures of the same size."""
    return a.size == b.size and np.array_equal(np.array(a.convert("RGBA")), np.array(b.convert("RGBA")))


def main():
    rows = fit.census()
    races = {r for r, _t in rows}
    with open(fit.GROUPS, encoding="utf-8") as fh:
        cfg = json.load(fh)
    grouped = {r for rs in cfg["groups"].values() for r in rs}
    check("census sees RSW_Ronto and >= 50 pack races", "RSW_Ronto" in races and len(races) >= 50, len(races))
    check("every pack race is in a group", races <= grouped, sorted(races - grouped))
    check("no stale race in the groups", grouped <= races, sorted(grouped - races))

    # break probes
    body = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    body.paste((90, 60, 40, 255), (10, 20, 54, 50))
    gear = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    gear.paste((120, 80, 40, 255), (20, 22, 44, 40))
    off = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    off.paste((120, 80, 40, 255), (0, 0, 40, 14))
    check("probe: good gear passes", judge(gear, body) is None, judge(gear, body))
    check("probe: placeholder reddens", judge(Image.new("RGBA", (4, 4)), body) == "placeholder")
    check("probe: body copy reddens", judge(body, body) == "byte copy of the body")
    check("probe: off-body gear reddens", "off the body" in (judge(off, body) or ""))

    ours = fit.fitted()
    by_race = {r: g for g, rs in cfg["groups"].items() for r in rs}
    try:
        overs = fit.overlays(fit.art_state())
    except Exception as exc:                       # the shared sources are the proof; never skip without them
        check("shared overlay sources packoverlay_<group>_v1_<facing> readable", False, repr(exc))
        overs = None
    probe = None
    if overs is not None:
        check("all 12 shared overlay sources load", len(overs) == 12, len(overs))
        probe = next(((race, tex) for race, tex in rows if tex in ours), None)
    if probe:
        race, tex = probe
        root = fit.tex_root(tex)
        row = (race, tex, by_race[race], root, cfg["overrides"].get(tex, {}))
        fitted_e = fit.render(row, overs)["east"][1]
        a = np.array(fitted_e)
        x0, y0, x1, y1 = fitted_e.getchannel("A").getbbox()
        flat = np.zeros_like(a)
        flat[y0:y1, x0:x1] = (120, 80, 40, 255)    # the blind checker's mutant: one brown fill over the gear bbox
        flat = Image.fromarray(flat, "RGBA")
        other = (by_race[race] == "quadruped") and "biped" or "quadruped"
        wrong = fit.render((race, tex, other, root, {}), overs)["east"][1]
        check("probe: fit reproduces itself", same(fitted_e, fit.render(row, overs)["east"][1]))
        check("probe: flat fill over the gear is not the shared overlay", not same(flat, fitted_e))
        check("probe: flat fill still passes the gear checks (why the reproduction check exists)",
              judge(flat, fit.raw_body(root, tex, "east")) is None)
        check("probe: another group's overlay is not this group's", not same(wrong, fitted_e))

    checked = reproduced = 0
    for race, tex in rows:
        if fit.waived(tex) or overs is None:
            continue
        if tex not in ours:
            check("%s is fitted or named donor Pack art" % tex, tex in DONOR_PACK, "neither (%s)" % race)
            continue
        root = fit.tex_root(tex)
        if root is None:
            continue                               # reported by the loop below
        row = (race, tex, by_race.get(race), root, cfg["overrides"].get(tex, {}))
        if row[2] is None:
            continue                               # reported by the group checks above
        for f, (_b, want) in fit.render(row, overs).items():
            p = os.path.join(root, tex + "Pack_%s.png" % f)
            if not os.path.isfile(p):
                continue                           # reported by the loop below
            reproduced += 1
            if not same(Image.open(p), want):
                check("%s %s is the shared %s overlay fitted to the current body" % (tex, f, row[2]), False,
                      "differs from pack_overlay_fit.render(); hand-made, or the body changed after the fit")
    check("%d fitted Pack facings reproduce from the shared overlays" % reproduced,
          reproduced >= 150 and not [x for x in FAILS if "shared" in x or "fitted or named" in x],
          "%d reproduced" % reproduced)

    checked = 0
    for race, tex in rows:
        if fit.waived(tex):
            continue
        root = fit.tex_root(tex)
        if root is None:
            check(tex, False, "body texture not found in src/ (%s)" % race)
            continue
        for f in fit.FACINGS + (("west",) if fit.is_single(root, tex) else ()):
            p = os.path.join(root, tex + "Pack_%s.png" % f)
            if not os.path.isfile(p):
                check("%s %s" % (tex, f), False, "no Pack file (%s)" % race)
                continue
            pack = Image.open(p).convert("RGBA")
            why = judge(pack, fit.raw_body(root, tex, f), tex not in DRAWN_FOR_THE_BODY)
            checked += 1
            if why:
                check("%s %s" % (tex, f), False, why)
    check("%d adult Pack facings of %d races are real gear" % (checked, len(races)), checked >= 120 and not FAILS,
          "%d checked" % checked)
    if FAILS:
        print("\n%d pack-overlay check(s) FAILED" % len(FAILS))
        return 1
    print("\nall pack-overlay checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
