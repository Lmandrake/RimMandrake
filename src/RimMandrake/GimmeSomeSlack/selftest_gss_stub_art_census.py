#!/usr/bin/env python3
"""Every texture Gimme Some Slack draws is classed by how a cord joins it (RIMMANDRAKE_BIND_SLACK_STUB_ANGLE_RULE_FOURTH_ASK).

Owner 2026-11-16: "It should be true for every art piece that has stubs/connectors at particular angles that need to be matched." The
position-and-slope check (Source/Core/StubJoinAudit.cs, StubArt.Census) reads one table; this test fails when a PNG under Textures/ is not
in it, so a new connector cannot ship unclassed and silently outside the check. It also proves it can fail, on a planted unknown name.

A cut texture `<Art>_p<mask>` (the + box and the power switch drawing only the arms in use, E1 N2 W4 S8: CordDecal.Ports, SwitchStubs,
art_source/switch_stub_masks_2026-11-16/make_switch_masks.py) is classed as its parent is, and its pixels must say the same as its mask:
along each arm's centre ray a kept arm reaches exactly as far as the parent's, a cut one stops short of it. The joins check
(StubJoinAudit.OfPiece) puts a stub only on the mask's arms, so a cut texture that drew another arm would be a bare stub it never reads.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "Source", "Core", "StubJoinAudit.cs")
TEX = os.path.join(HERE, "Textures")
ROW = re.compile(r'\("([A-Za-z0-9_]+)",\s*Join\.(\w+),')
CUT = re.compile(r"(.+)_p(\d+)$")
ARMS = ((1, 0), (0, -1), (-1, 0), (0, 1))   # E N W S in image rows (row 0 is north), bits 1 2 4 8


def census(src):
    return {m.group(1): m.group(2) for m in ROW.finditer(src)}


def textures(root):
    return sorted({os.path.splitext(f)[0] for _d, _s, fs in os.walk(root) for f in fs if f.lower().endswith(".png")})


def unclassed(names, table):
    return [n for n in names if n not in table]


def png_files(root):
    return sorted(os.path.join(d, f) for d, _s, fs in os.walk(root) for f in fs if f.lower().endswith(".png"))


def reach(alpha, dx, dy):
    """The farthest opaque pixel along one arm's centre ray, px from the centre."""
    h, w = alpha.shape
    r = 0
    for k in range(min(h, w) // 2):
        if alpha[int(h / 2 + dy * k), int(w / 2 + dx * k)] > 128:
            r = k
    return r


def cut_arm_fails(pairs):
    """pairs: (label, mask, cut alpha, parent alpha). Returns (fails, kept-arm worst loss, cut-arm least loss, arms read)."""
    fails, kept, cut, n = [], 0, None, 0
    for label, mask, a, parent in pairs:
        if not 0 < mask < 15:
            fails.append("%s: mask %d is not a cut of four arms (1-14)" % (label, mask))
            continue
        for b, (dx, dy) in enumerate(ARMS):
            lost = reach(parent, dx, dy) - reach(a, dx, dy)
            n += 1
            if mask >> b & 1:
                kept = max(kept, lost)
                if lost != 0:
                    fails.append("%s: arm bit %d is in the mask but reaches %d px short of its parent" % (label, 1 << b, lost))
            else:
                cut = lost if cut is None else min(cut, lost)
                if lost <= 0:
                    fails.append("%s: arm bit %d is cut by the mask but still drawn as far as its parent's" % (label, 1 << b))
    return fails, kept, cut, n


def main():
    with open(TABLE, encoding="utf-8") as f:
        table = census(f.read())
    names = textures(TEX)
    fails = []
    if len(names) < 20:
        fails.append("instrument: only %d textures found under %s" % (len(names), TEX))
    if len(table) < 20:
        fails.append("instrument: only %d census rows parsed from %s" % (len(table), TABLE))
    miss = unclassed(names, table)
    if miss:
        fails.append("unclassed textures (add each to StubArt.Census with how a cord joins it): " + ", ".join(miss))
    stale = sorted(set(table) - set(names))
    if stale:
        fails.append("census rows naming no texture: " + ", ".join(stale))
    stubbed = sorted(n for n, k in table.items() if k == "Stubs")
    for must in ("Junction_X", "Junction_T", "PowerSwitch", "Plug", "PlugTop", "PowerStrip", "StubWall", "StubRock", "WallOutlet"):
        if table.get(must) != "Stubs":
            fails.append("%s must be classed Stubs, is %s" % (must, table.get(must)))
    for must in ("WallBracket", "AerialMastTop", "StandingLamp"):
        if table.get(must) != "PositionOnly":
            fails.append("%s is stubless (owner 2026-11-16), must be PositionOnly, is %s" % (must, table.get(must)))
    # a cut texture is classed as its parent, and draws exactly its mask's arms
    try:
        import numpy as np
        from PIL import Image
    except ImportError as e:
        fails.append("instrument: cut-arm check cannot read PNGs (%s)" % e)
        np = None
    pairs = []
    for path in png_files(TEX):
        m = CUT.match(os.path.splitext(os.path.basename(path))[0])
        if not m:
            continue
        parent = os.path.join(os.path.dirname(path), m.group(1) + ".png")
        label = os.path.relpath(path, TEX)
        if not os.path.exists(parent):
            fails.append("%s: no parent %s.png beside it" % (label, m.group(1)))
            continue
        if table.get(m.group(1) + "_p" + m.group(2)) != table.get(m.group(1)):
            fails.append("%s is classed %s, its parent %s %s" % (m.group(0), table.get(m.group(0)), m.group(1), table.get(m.group(1))))
        if np is not None:
            pairs.append((label, int(m.group(2)), np.array(Image.open(path).convert("RGBA"))[:, :, 3],
                          np.array(Image.open(parent).convert("RGBA"))[:, :, 3]))
    if np is not None:
        if len(pairs) < 20:
            fails.append("instrument: only %d cut textures read" % len(pairs))
        arm_fails, kept, cut, arms = cut_arm_fails(pairs)
        fails += arm_fails
        print("cut textures: %d read (%d arms); kept arm worst loss %d px (limit 0), cut arm least loss %s px (limit > 0)"
              % (len(pairs), arms, kept, cut))
        # the guard can fail: a cut texture read against the wrong mask, and one against its own uncut parent, are caught
        if pairs:
            label, mask, a, parent = pairs[0]
            if not cut_arm_fails([(label, mask ^ 15, a, parent)])[0]:
                fails.append("guard: a cut texture read against the complementary mask was not caught")
            if not cut_arm_fails([(label, mask, parent, parent)])[0]:
                fails.append("guard: an uncut parent posing as a cut texture was not caught")
    # the guard can fail: a planted unknown texture is caught
    if unclassed(names + ["Junction_Y_Planted"], table) != miss + ["Junction_Y_Planted"]:
        fails.append("guard: a planted unclassed texture was not caught")
    print("stub art census: %d textures (%d PNG files over all styles), %d census rows, %d stubbed (%s)"
          % (len(names), len(png_files(TEX)), len(table), len(stubbed), " ".join(stubbed)))
    for f in fails:
        print("FAIL " + f)
    print("%s" % ("PASS" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
