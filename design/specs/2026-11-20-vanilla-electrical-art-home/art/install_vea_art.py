#!/usr/bin/env python3
"""install_vea_art.py — conform, sheet and install the 2026-11-20 commissions (item RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART).

    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/install_vea_art.py conform
    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/install_vea_art.py judgesheet <out.png> [kind]
    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/install_vea_art.py install --verdicts V.json [--dry]

conform: raw renders (gen_direct.py) -> <scratch>/vea_20261120/conf/<dest rel path>, at the shipping size:
  Battery    north/south 256x384, east 384x256 (drawSize (2,3) x 128 px per cell). The subject is fitted, aspect kept,
             into vanilla's own alpha box scaled to our canvas (Battery_north x 0.24-0.76, y 0.16-0.88; Battery_east
             x 0.16-0.84, y 0.24-0.82), so it covers the same ground as vanilla. South = the north picture (vanilla
             ships no Battery_south; Graphic_Multi then draws north for south).
  WallLamp   128 per facing (drawSize 1 x 128). Vanilla's lamp is a 34x8 px bar on a 64 canvas, too thin for any
             look to read, so the box is larger but keeps vanilla's anchor on the wall edge: south = top edge,
             east = left edge, north = vanilla's lower bar line (y 0.84). West mirrors east (vanilla ships no west).
  Icons      256 square, subject fitted into the middle 88%.
Downscale: premultiplied alpha (PIL "RGBa") with LANCZOS, then alpha < 8 cleared (no faint fringe).

Look icons: ONE picture per look, shipped by every mod that offers the looks, each at its own texPath root
(RimMandrake/<Mod>/UI/Looks/<Look>, design/NAMING_SCHEME_PLAN.md: texPaths move with their mod) with the same bytes.

install: only pictures whose verdict in V.json is KEEP, through `art.py install` (the art ledger) with
`--reason script:<this file>`. The battery is NOT installed into any mod: its home, "Machine Looks", does not exist
yet (design.md); its pictures go into the art store with `art.py put` and wait there.
"""
import json, os, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_str  # noqa: E402

ROOT = Path(rm_str("scratch", "vea_20261120"))
RAW, CONF = ROOT / "raw", ROOT / "conf"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
ART = REPO / "src" / "RimMandrake" / "Utils" / "art" / "art.py"
REASON = "script:design/specs/2026-11-20-vanilla-electrical-art-home/art/install_vea_art.py"
GSS = "src/RimMandrake/GimmeSomeSlack"
FW = "src/RimMandrake/FlowWorks"
POLE = {"linkwire": "LinkWire", "unlinkwire": "UnlinkWire", "unlinkall": "UnlinkAll"}

# (canvas w, h, box x0, y0, x1, y1 as fractions, anchor) per kind/facing
BOXES = {
    ("battery", "north"): (256, 384, (0.24, 0.16, 0.76, 0.88), "centre"),
    ("battery", "east"): (384, 256, (0.16, 0.24, 0.84, 0.82), "centre"),
    ("walllamp", "south"): (128, 128, (0.16, 0.00, 0.84, 0.46), "top"),
    ("walllamp", "north"): (128, 128, (0.16, 0.40, 0.84, 0.84), "bottom"),
    ("walllamp", "east"): (128, 128, (0.00, 0.10, 0.46, 0.80), "left"),
    ("icon", None): (256, 256, (0.06, 0.06, 0.94, 0.94), "centre"),
}


def trim(im, floor=16):
    a = np.asarray(im)[..., 3] >= floor
    ys, xs = np.where(a)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def resize(im, w, h):
    out = im.convert("RGBa").resize((w, h), Image.LANCZOS).convert("RGBA")
    arr = np.asarray(out).copy()
    arr[arr[..., 3] < 8] = 0
    return Image.fromarray(arr, "RGBA")


def fit(raw_png, kind, facing):
    cw, ch, (fx0, fy0, fx1, fy1), anchor = BOXES[(kind, facing)]
    sub = trim(Image.open(raw_png).convert("RGBA"))
    bw, bh = (fx1 - fx0) * cw, (fy1 - fy0) * ch
    s = min(bw / sub.width, bh / sub.height)
    w, h = max(1, round(sub.width * s)), max(1, round(sub.height * s))
    sub = resize(sub, w, h)
    x = round(fx0 * cw + (bw - w) / 2)
    y = round(fy0 * ch + (bh - h) / 2)
    if anchor == "top":
        y = round(fy0 * ch)
    elif anchor == "bottom":
        y = round(fy1 * ch) - h
    elif anchor == "left":
        x = round(fx0 * cw)
    can = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    can.alpha_composite(sub, (x, y))
    return can


def plan():
    """-> [(raw id, kind, facing, [dest rel paths])]. Dest paths are repo-relative texture files."""
    P = []
    for L in LOOKS:
        l = L.lower()
        P.append(("vea_battery_v1_%s_east" % l, "battery", "east", ["MachineLooks/%s/Battery_east.png" % L]))
        P.append(("vea_battery_v1_%s_north" % l, "battery", "north",
                  ["MachineLooks/%s/Battery_north.png" % L, "MachineLooks/%s/Battery_south.png" % L]))
        for f in ("east", "north", "south"):
            P.append(("vea_walllamp_v1_%s_%s" % (l, f), "walllamp", f,
                      ["%s/Textures/RimMandrake/GimmeSomeSlack/Styles/%s/WallLamp_%s.png" % (GSS, L, f)]))
        P.append(("vea_lookicon_v1_%s" % l, "icon", None,
                  ["%s/Textures/RimMandrake/%s/UI/Looks/%s.png" % (m, m.rsplit("/", 1)[1], L) for m in (GSS, FW)]))
    for k, n in POLE.items():
        P.append(("vea_poleicon_v1_%s" % k, "icon", None,
                  ["%s/Textures/RimMandrake/GimmeSomeSlack/UI/Commands/%s.png" % (GSS, n)]))
    return P


def conf_path(dest):
    return CONF / dest


def cmd_conform():
    n = miss = 0
    for rid, kind, facing, dests in plan():
        raw = RAW / (rid + ".png")
        if not raw.exists():
            print("MISSING %s (not rendered)" % rid)
            miss += 1
            continue
        im = fit(raw, kind, facing)
        for d in dests:
            p = conf_path(d)
            p.parent.mkdir(parents=True, exist_ok=True)
            im.save(p)
        n += 1
    print("conformed %d, missing %d -> %s" % (n, miss, CONF))


def checker(w, h, s=8):
    yy, xx = np.mgrid[0:h, 0:w]
    c = (((xx // s) + (yy // s)) % 2).astype(np.uint8)
    arr = np.where(c[..., None] == 1, 205, 160).astype(np.uint8)
    return Image.fromarray(np.dstack([arr[..., 0]] * 3 + [np.full((h, w), 255, np.uint8)]), "RGBA")


def cmd_judgesheet(out, kind=None):
    """One PNG per kind: each look a row, every facing at shipping size and at 32 px per cell, on a checkerboard."""
    rows = []
    for rid, k, facing, dests in plan():
        if kind and k != kind:
            continue
        p = conf_path(dests[0])
        if p.exists():
            rows.append((rid, Image.open(p).convert("RGBA")))
    if not rows:
        print("nothing conformed for", kind)
        return
    pad = 12
    tiles = []
    for rid, im in rows:
        small = resize(im, max(1, im.width // 4), max(1, im.height // 4))  # 128 -> 32 px per cell
        t = checker(im.width + small.width + pad * 3, max(im.height, small.height) + pad * 2)
        t.alpha_composite(im, (pad, pad))
        t.alpha_composite(small, (im.width + pad * 2, pad))
        tiles.append((rid, t))
    W = max(t.width for _, t in tiles)
    H = sum(t.height + 18 for _, t in tiles)
    from PIL import ImageDraw
    sheet = Image.new("RGBA", (W, H), (40, 40, 40, 255))
    y = 0
    d = ImageDraw.Draw(sheet)
    for rid, t in tiles:
        d.text((4, y + 2), rid, fill=(255, 255, 255, 255))
        sheet.alpha_composite(t, (0, y + 18))
        y += t.height + 18
    sheet.save(out)
    print("sheet", out, len(tiles), "pictures")


def cmd_install(verdicts, dry):
    V = json.load(open(verdicts))
    keep = {v["picture"] for v in V["verdicts"] if v["verdict"] == "KEEP"}
    for rid, kind, facing, dests in plan():
        if rid not in keep:
            print("NOT INSTALLED %s (verdict not KEEP)" % rid)
            continue
        for d in dests:
            src = conf_path(d)
            if d.startswith("MachineLooks/"):
                cmd = [sys.executable, str(ART), "put", str(src)]
            else:
                rel = d.split("/Textures/", 1)[1]
                mod = d.split("/Textures/", 1)[0]
                dst = REPO / d
                dst.parent.mkdir(parents=True, exist_ok=True)
                cmd = [sys.executable, str(ART), "install", mod, "Textures/" + rel, "--file", str(src),
                       "--reason", REASON, "--why", "delegated: art %s" % verdicts]
                if dry:
                    cmd.append("--dry-run")
            if dry and cmd[2] == "put":
                print("DRY put", src)
                continue
            p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
            print(("OK " if p.returncode == 0 else "FAIL %d " % p.returncode) + d + " " +
                  (p.stdout + p.stderr).strip().replace("\n", " | ")[-240:])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "conform":
        cmd_conform()
    elif a[0] == "judgesheet":
        cmd_judgesheet(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == "install":
        cmd_install(a[a.index("--verdicts") + 1], "--dry" in a)
