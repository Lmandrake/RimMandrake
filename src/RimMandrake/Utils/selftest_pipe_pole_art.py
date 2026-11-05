"""PIPE_POLE_REDRAW_NOT_A_POWER_POLE: every pipe-pole look wears its own pipe-clamp support, never the GSS power mast.

  python3 src/RimMandrake/Utils/selftest_pipe_pole_art.py

Checks, offline:
  1. RM_PipePole and each RM_PipePole_<Look> ThingStyleDef point at RimMandrake/FlowWorks/PipePole/<Look>/PipePole (the base
     def at Scrapper's), none at a GSS AerialMast, none tinted (the steel-blue stand-in tint is gone).
  2. Each of the four PipePole.png exists, is 256x512 RGBA, and is an installed art-ledger picture (its sha is the ledger's
     current one for that path).
  3. The clamp seat: the pipe stub's centre row, read at the stub's two ends, is the def's attachZ row ((3.5 - attachZ) *
     128 for drawSize (2,4) at drawOffset z 1.5) within 1.5 px; and no insulator crown: nothing opaque stands wider than the
     post more than 40 px above the seat, and no row more than 24 px above it holds two or more separate opaque runs
     (insulator tips; probed 2026-11-05: the four GSS AerialMast pictures fail one or both, Futuristic's thin crystals the
     second only).
  4. The judge's verdict file names the four installed shas and reads PASS for each look.
"""
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FW = os.path.join(REPO, "src", "RimMandrake", "FlowWorks")
XML = os.path.join(FW, "Defs", "Machinery", "RM_PipePoles.xml")
TEXREL = "RimMandrake/FlowWorks/PipePole/%s/PipePole"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
VERDICT = os.path.join(FW, "art_source", "PipePole", "judge_verdict.json")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art"))

fails = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def png(look):
    return os.path.join(FW, "Textures", *(TEXREL % look).split("/")) + ".png"


def defs():
    root = ET.parse(XML).getroot()
    out = {}
    for d in root:
        dn = d.findtext("defName")
        gd = d.find("graphicData")
        if dn and gd is not None:
            out[dn] = (gd.findtext("texPath"), gd.find("color"))
    ext = root.find("./ThingDef[defName='RM_PipePole']/modExtensions/li/attachZ")
    return out, float(ext.text)


def runs_in_row(row):
    """Opaque runs in a row, ignoring gaps under 4 px (an insulator crown is 2-3 runs; a post head is 1)."""
    xs = np.where(row)[0]
    if xs.size == 0:
        return 0
    return 1 + int((np.diff(xs) > 4).sum())


def stub(alpha, limit=256):
    cols = np.where(alpha[:limit].max(0) > 128)[0]
    rows = []
    for c in (cols.min() + 4, cols.max() - 4):
        r = np.where(alpha[:limit, c] > 128)[0]
        rows.append((r.min() + r.max()) / 2.0 + 0.5)
    return sum(rows) / 2.0


def main():
    d, attach = defs()
    seat_want = (3.5 - attach) * 128.0
    want = {"RM_PipePole": TEXREL % "Scrapper"}
    want.update({"RM_PipePole_%s" % l: TEXREL % l for l in LOOKS})
    for dn, tp in want.items():
        got = d.get(dn)
        check(got is not None and got[0] == tp, "%s texPath %s" % (dn, got and got[0]))
        check(got is not None and got[1] is None, "%s carries no stand-in tint" % dn)
    check(not any("AerialMast" in (v[0] or "") for v in d.values()), "no pipe-pole def wears a GSS AerialMast")

    import artledger as L
    events = L.read_events()
    check(len(events) > 100, "art ledger readable (%d events)" % len(events))     # sanity: a blind reader would see none
    shas = {}
    for look in LOOKS:
        p = png(look)
        if not os.path.isfile(p):
            check(False, "%s PipePole.png exists" % look)
            continue
        data = open(p, "rb").read()
        shas[look] = hashlib.sha256(data).hexdigest()
        im = Image.open(p)
        check(im.size == (256, 512) and im.mode == "RGBA", "%s 256x512 RGBA (%s %s)" % (look, im.size, im.mode))
        a = np.asarray(im.convert("RGBA"))[:, :, 3].astype(int)
        seat = stub(a)
        check(abs(seat - seat_want) <= 1.5, "%s clamp seat row %.1f vs attachZ row %.1f" % (look, seat, seat_want))
        w = (a > 128).sum(1)
        post = float(np.median(w[200:400]))
        high = w[: max(0, int(seat_want) - 40)]
        check(high.size == 0 or high.max() <= post * 1.35 + 6,
              "%s no insulator crown above the clamp (widest %d px vs post %.0f)" % (look, high.max() if high.size else 0, post))
        runs = max(runs_in_row(a[r] > 128) for r in range(int(seat_want) - 24))
        check(runs <= 1, "%s one solid head above the clamp, no separate insulator tips (max %d opaque runs a row)" % (look, runs))
        rel = (TEXREL % look) + ".png"
        live = [e for e in events if e.get("rel") == rel and e.get("type") == "live"]
        check(bool(live) and live[-1].get("sha") == shas[look] and "PipePole/make_pipe_pole.py" in live[-1].get("reason", ""),
              "%s is the art ledger's installed picture, by make_pipe_pole.py" % look)

    if not os.path.isfile(VERDICT):
        check(False, "judge verdict file %s" % os.path.relpath(VERDICT, REPO))
    else:
        v = json.load(open(VERDICT))
        for look in LOOKS:
            r = v.get("looks", {}).get(look, {})
            check(r.get("sha256") == shas.get(look), "%s verdict judged the installed bytes" % look)
            check(r.get("verdict") == "PASS", "%s judge verdict %s" % (look, r.get("verdict")))
        check(bool(v.get("sheet")) and bool(v.get("judge")), "verdict names its sheet and judge")
    print("FAILED %d" % len(fails) if fails else "ALL PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
