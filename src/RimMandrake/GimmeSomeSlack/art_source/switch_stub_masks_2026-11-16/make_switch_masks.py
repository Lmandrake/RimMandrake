#!/usr/bin/env python3
"""The power switch drawn with only the stubs that carry a cord (RIMMANDRAKE_FINISH_SLACK_TONIGHT_TWO_DECIDERS_RED_AT_CERTIFICATE).

Owner 2026-11-16 (holding file row 2): "the junction box has stubby connectors that don't line up"; the bar
cords_join_stubs_on_position_and_slope: "no stub is drawn bare while a cord is attached elsewhere on its piece". Every look's
PowerSwitch art paints four stubs. This derives, from the kept art and nothing else, one texture per set of used stubs: each unused
arm is cut away at the box's edge (where the opaque width across the arm first drops under BODY px), only inside the arm's own
corridor, so the lever and the box stay whole. The cut positions are read off the ON art and used for both states.

Output beside each source: PowerSwitch[_Off]_p<mask>.png, mask bits E=1 N=2 W=4 S=8 (texture up is north), masks 1..14
(0 and 15 draw the full art). The C# side: Core/StubJoinAudit.cs SwitchStubs; Aerial/ConduitStylePicker.cs SwitchPath.
The device stub's small + box carries one cord: Junction_X_p4 / Junction_Tin_p4 keep only its -X (west) arm (CordDecal.Ports,
CordMaterials.OnePortBox); the box art's body is narrower, so its edge is read at BOX_BODY.

    python3 src/RimMandrake/GimmeSomeSlack/art_source/switch_stub_masks_2026-11-16/make_switch_masks.py          # write
    python3 src/RimMandrake/GimmeSomeSlack/art_source/switch_stub_masks_2026-11-16/make_switch_masks.py --check  # rc 1 if stale
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.normpath(os.path.join(HERE, "..", "..", "Textures", "RimMandrake", "GimmeSomeSlack"))
LOOKS = {"Scrapper": "PowerSwitch", "Industrial": "Styles/Industrial/PowerSwitch", "Modern": "Styles/Modern/PowerSwitch",
         "Futuristic": "Styles/Futuristic/PowerSwitch"}
BODY = 40      # px of 128: narrower than this across the arm is arm, not box
BOX_BODY = 40  # the same for the + junction box art (bodies 24 to 62 px wide)
BOXES = ["Junction_Tin"] + ["Styles/%s/Junction_X" % s for s in ("Cybertek", "ExtCord", "ExtCord/Blue", "ExtCord/Brown", "ExtCord/Green",
                                                                   "ExtCord/Yellow", "StarWars")]
CORRIDOR = 26  # px either side of the centre line an arm (and its gland) lies in
E, N, W, S = 1, 2, 4, 8


def cuts(alpha, body=BODY):
    m = alpha > 20
    cc, rc = m.sum(0), m.sum(1)

    def first(counts, rng):
        for x in rng:
            if counts[x] < body:
                return x
        raise SystemExit("no box edge found")
    return {E: first(cc, range(64, 128)), W: first(cc, range(63, -1, -1)), N: first(rc, range(63, -1, -1)), S: first(rc, range(64, 128))}


def band(m, axis):
    hit = m.any(axis=axis).copy()
    hit[:64 - CORRIDOR] = False
    hit[64 + CORRIDOR:] = False
    nz = np.nonzero(hit)[0]
    return nz.min() - 3, nz.max() + 4


def masked(rgba, mask, c):
    b = rgba.copy()
    m = rgba[:, :, 3] > 20
    if not mask & E:
        r0, r1 = band(m[:, c[E]:], 1); b[r0:r1, c[E]:, 3] = 0
    if not mask & W:
        r0, r1 = band(m[:, :c[W] + 1], 1); b[r0:r1, :c[W] + 1, 3] = 0
    if not mask & N:
        c0, c1 = band(m[:c[N] + 1, :], 0); b[:c[N] + 1, c0:c1, 3] = 0
    if not mask & S:
        c0, c1 = band(m[c[S]:, :], 0); b[c[S]:, c0:c1, 3] = 0
    return b


def outputs():
    for look, rel in LOOKS.items():
        on = np.array(Image.open(os.path.join(TEX, rel + ".png")).convert("RGBA"))
        c = cuts(on[:, :, 3])
        for state in ("", "_Off"):
            src = np.array(Image.open(os.path.join(TEX, rel + state + ".png")).convert("RGBA"))
            for mask in range(1, 15):
                yield os.path.join(TEX, "%s%s_p%d.png" % (rel, state, mask)), masked(src, mask, c)
    for rel in BOXES:
        box = np.array(Image.open(os.path.join(TEX, rel + ".png")).convert("RGBA"))
        yield os.path.join(TEX, rel + "_p4.png"), masked(box, W, cuts(box[:, :, 3], BOX_BODY))


def main():
    check = "--check" in sys.argv
    stale = 0
    for path, arr in outputs():
        if check:
            if not os.path.exists(path) or not np.array_equal(np.array(Image.open(path).convert("RGBA")), arr):
                stale += 1
                print("STALE", path)
        else:
            Image.fromarray(arr).save(path, optimize=True)
    print(("%d stale" % stale) if check else "wrote 120 textures")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
