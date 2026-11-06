#!/usr/bin/env python3
"""Selftest for tooltip_detect.py (PLAYER_HOVER_PROBE_TOOLTIP_DRAWN): planted frames the detector must sort right.

Cases: a dark text box drawn over a busy map (DRAWN); the same box with no text (not drawn: a box nobody can read);
a gizmo's mouse-over brightening alone (not drawn); identical frames (not drawn); a full-scene change (not drawn:
too big to be a tooltip); a bottom-left readout text change (readout changed, no tooltip). Also checks the probe
module imports and its verdict rule counts the readout only for the map-thing clause.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw  # noqa: E402

import tooltip_detect as td  # noqa: E402

W, H = 1280, 720


def scene(seed=1):
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H), (120, 105, 80))
    d = ImageDraw.Draw(im)
    for _ in range(400):   # sandy terrain, rocks, things
        x, y = rnd.randrange(W), rnd.randrange(H)
        c = tuple(rnd.randrange(60, 200) for _ in range(3))
        d.rectangle([x, y, x + rnd.randrange(4, 30), y + rnd.randrange(4, 30)], fill=c)
    d.rectangle([400, 620, 880, 720], fill=(50, 50, 50))          # gizmo bar
    for i in range(5):
        d.rectangle([410 + 90 * i, 630, 485 + 90 * i, 705], fill=(90, 90, 90))
    d.text((10, 690), "Sand (walk speed 87%)", fill=(230, 230, 230))
    return im


def tooltip(im, text=True):
    im = im.copy()
    d = ImageDraw.Draw(im)
    d.rectangle([500, 400, 820, 560], fill=(21, 25, 29), outline=(97, 108, 118))
    if text:
        for i, line in enumerate(("Draft", "Draft this colonist so you can control", "them directly. Hotkey: R")):
            d.text((512, 412 + 18 * i), line, fill=(235, 235, 235))
    return im


def main():
    base = scene()
    fails = []

    def expect(name, got, want):
        print("%-28s %s" % (name, "ok" if got == want else "WRONG (got %r want %r)" % (got, want)))
        if got != want:
            fails.append(name)

    r = td.find_tooltip(base, tooltip(base))
    expect("text box drawn", r["drawn"], True)
    if r["drawn"]:
        x0, y0, x1, y1 = r["box"]
        expect("box covers the tooltip", x0 <= 512 and y0 <= 412 and x1 >= 700 and y1 >= 440, True)
    expect("empty box not readable", td.find_tooltip(base, tooltip(base, text=False))["drawn"], False)
    hl = base.copy()
    ImageDraw.Draw(hl).rectangle([410, 630, 485, 705], fill=(170, 170, 170))
    expect("gizmo highlight only", td.find_tooltip(base, hl)["drawn"], False)
    expect("identical frames", td.find_tooltip(base, base.copy())["drawn"], False)
    expect("whole scene changed", td.find_tooltip(base, scene(seed=2))["drawn"], False)
    ro = base.copy()
    d = ImageDraw.Draw(ro)
    d.rectangle([0, 680, 300, 720], fill=(120, 105, 80))
    d.text((10, 690), "Butcher spot / Sand", fill=(230, 230, 230))
    expect("readout changed", td.readout_changed(base, ro)["changed"], True)
    expect("readout unchanged", td.readout_changed(base, base.copy())["changed"], False)
    expect("readout is no tooltip", td.find_tooltip(base, ro)["drawn"], False)
    expect("size mismatch refused", td.find_tooltip(base, base.resize((640, 360)))["drawn"], False)

    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import prove_hover_tooltip as ph
    row_ro = {"tooltip": {"drawn": False}, "readout": {"changed": True}}
    expect("readout counts for A3", ph.verdict([row_ro], readout_counts=True), True)
    expect("readout ignored for A1/A2", ph.verdict([row_ro], readout_counts=False), False)
    print("FAIL" if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
