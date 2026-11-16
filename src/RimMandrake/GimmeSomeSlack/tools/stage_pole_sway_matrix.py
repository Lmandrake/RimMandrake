#!/usr/bin/env python3
"""Stage the owner's pole-wire sway matrix (RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT, owner 2026-11-16:
"They look like they're swaying, though it's not a great effect. They're too stiff.").

27 numbered, signed stations on the current map: look (Pendulum, Rope, Gust) x span (short 5, medium 10, long 18 cells)
x wind (calm 0.15, breezy 0.9, storm 2.2). Wind and look are map-wide in play, so each span is pinned to its station's
look and wind through AerialProbe swaystation: (RM_MapComponent_Aerial.reviewSwayStations, saved with the map). The game
is left PAUSED (unpause to watch them swing; the clock is never advanced here), saved as a keeper, and a key sheet is
written beside the showing.

    python.exe src/RimMandrake/GimmeSomeSlack/tools/stage_pole_sway_matrix.py --x0 20 --z0 20 [--name RM_gss_pole_sway_matrix]

Hold the bridge first (rimflow bridge take --idle-ok --for "pole sway review matrix"); release it after.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GSS = os.path.dirname(HERE)
sys.path.insert(0, GSS)
sys.path.insert(0, os.path.join(GSS, "..", "Utils"))
import validation_aerial as VA  # noqa: E402
from modcheck import reviewmap as RMH  # noqa: E402
import rmpaths  # noqa: E402

LOOKS = ("Pendulum", "Rope", "Gust")
SPANS = (("short", 5), ("medium", 10), ("long", 18))
WINDS = (("calm", 0.15), ("breezy", 0.9), ("storm", 2.2))
# from the storage helper, spelled for the Python running this (python.exe got a WSL path and died after saving, 2026-11-16)
SHOW = rmpaths.rm_str("showings", "RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT")
COL_W, ROW_H = 24, 6        # 18-cell long span + masts + gap; rows far enough apart that sags never overlap


def layout(x0, z0):
    """-> station dicts: n, look, span, wind, a, b (mast cells), mid (the span's midpoint cell)."""
    st, n = [], 0
    for li, look in enumerate(LOOKS):
        for si, (sname, L) in enumerate(SPANS):
            for wi, (wname, w) in enumerate(WINDS):
                n += 1
                x, z = x0 + wi * COL_W, z0 + (li * len(SPANS) + si) * ROW_H
                a, b = (x, z), (x + L, z)
                st.append(dict(n=n, look=look, span=sname, cells=L, wind=wname, windSpeed=w, a=a, b=b,
                               mid=((a[0] + b[0] + 1) // 2, z)))
    return st


def row_order_text(st):
    """The key sheet's row order as it reads ON SCREEN: north (higher z) is up, so the last-laid row is the top one."""
    rows = []
    for s in sorted(st, key=lambda s: -s["a"][1]):
        name = "%s %s" % (s["look"], s["span"])
        if name not in rows:
            rows.append(name)
    return ("Rows top to bottom: %s. Columns west to east: calm, breezy, storm. Each station's number is on its sign book, "
            "two cells west of its left mast." % ", ".join(rows))


def sign_cell(s):
    """Two cells west of mast A, one north of its base: clear of the mast (drawn ~3 cells tall above its base cell, where a sign
    book hid the mast art in the first live capture, 2026-11-16) and of the previous column's span (COL_W leaves 6 cells)."""
    return (s["a"][0] - 2, s["a"][1] + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x0", type=int, default=20)
    ap.add_argument("--z0", type=int, default=20)
    ap.add_argument("--name", default="RM_gss_pole_sway_matrix_%s" % time.strftime("%Y%m%d"))
    a = ap.parse_args()
    B = VA.A()
    st = layout(a.x0, a.z0)
    w = COL_W * len(WINDS) + 2
    h = ROW_H * len(LOOKS) * len(SPANS) + 2
    rect = (a.x0 - 2, a.z0 - 3, w, h)
    B.call("rimworld/pause_game", pause=True)
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % rect, categories="All")
    B.ap("set:autoLink=False")                     # stations sit within maxSpan of each other: link only the pairs
    for s in st:
        VA.build_mast(B, s["a"]); VA.build_mast(B, s["b"])
    c = B.ap("census")
    pos = VA.anchors_by_pos(c)
    links, bad = 0, []
    for s in st:
        pa, pb = pos.get(s["a"]), pos.get(s["b"])
        if not pa or not pb:
            bad.append(s["n"]); continue
        r = B.ap("link:%d,%d" % (pa["id"], pb["id"]))
        links += r.get("verdict") == "Ok"
        if r.get("verdict") != "Ok":
            bad.append(s["n"])
    B.ap("set:autoLink=True")
    spec = ";".join("%d,%d,%s,%s" % (s["mid"][0], s["mid"][1], s["look"], s["windSpeed"]) for s in st)
    reg = B.ap("swaystation:" + spec)
    signs = [RMH.sign_book(sign_cell(s)[0], sign_cell(s)[1], str(s["n"]), "%s %s span, %s" % (s["look"], s["span"], s["wind"]),
                           clause="%d-cell span, wind %.2f fixed for this station" % (s["cells"], s["windSpeed"]),
                           look="does the wire swing like a hanging wire, ends fixed, belly moving most?",
                           do="unpause and watch a few swings at 1x", decide="keep this look / too much / too little")
             for s in st]
    RMH.place_signs(B, signs)
    B.call("rimworld/pause_game", pause=True)
    centre = (a.x0 + w // 2, a.z0 + h // 2)
    B.call("rimworld/jump_camera_to_cell", x=centre[0], z=centre[1])
    saved = RMH.save_keeper(B, a.name)
    os.makedirs(SHOW, exist_ok=True)
    rows = ["| # | look | span | wind | cells (mast A -> B) |", "|---|---|---|---|---|"]
    rows += ["| %d | %s | %s (%d) | %s (%.2f) | %s -> %s |" % (s["n"], s["look"], s["span"], s["cells"], s["wind"], s["windSpeed"], s["a"], s["b"])
             for s in st]
    sheet = ["# Pole-wire sway matrix", "", "Save: `%s` (game left paused; unpause to watch, 1x speed)." % a.name, "",
             row_order_text(st), ""] + rows
    open(os.path.join(SHOW, "KEYSHEET.md"), "w").write("\n".join(sheet) + "\n")
    out = dict(stations=len(st), linked=links, bad=bad, registered=reg.get("stations"), save=saved, rect=rect)
    json.dump(out, open(os.path.join(SHOW, "staging.json"), "w"), indent=1)
    print(json.dumps(dict(out, save=saved.get("ok"))))
    return 0 if links == len(st) and saved.get("ok") and reg.get("stations") == len(st) else 1


if __name__ == "__main__":
    sys.exit(main())
