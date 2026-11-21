#!/usr/bin/env python3
"""install_vea_art.py — conform, sheet and install the 2026-11-20 commissions (item RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART).

    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/install_vea_art.py conform
    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/install_vea_art.py judgesheet <out.png> [kind]
    python3 design/specs/2026-11-20-vanilla-electrical-art-home/art/install_vea_art.py install --verdicts V.json [--dry]

conform: raw renders (gen_direct.py) -> Transient/vea_20261120/conf/<dest rel path> (in the clone; art.py needs that), at the shipping size:
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

install: only pictures whose verdict is KEEP go into the art store (`art.py put`); see cmd_install for why none is
written into a mod's Textures folder yet. put_record.json (this folder) maps each to its sha and planned texture paths.
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
RAW = ROOT / "raw"
CONF = REPO / "Transient" / "vea_20261120" / "conf"   # inside the clone: art.py put/install take only files in the clone
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
        P.append(("vea_battery_v%d_%s_north" % (3 if L == "Modern" else 1, l), "battery", "north",
                  ["MachineLooks/%s/Battery_north.png" % L, "MachineLooks/%s/Battery_south.png" % L]))
        for f in ("east", "north", "south"):
            P.append(("vea_walllamp_v%d_%s_%s" % (2 if (L == "Modern" and f != "south") else 1, l, f), "walllamp", f,
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
    human = None
    if kind != "icon":   # D1: a vanilla colonist at the same 128 px per cell (scale_panel.human_sprite, the sheet's own)
        sys.path.insert(0, str(REPO / "src" / "RimMandrake" / "Utils" / "art"))
        import scale_panel
        human = scale_panel.human_sprite(128)[0]
    for rid, im in rows:
        small = resize(im, max(1, im.width // 4), max(1, im.height // 4))  # 128 -> 32 px per cell
        hw = human.width + pad if human else 0
        hh = human.height if human else 0
        t = checker(im.width + hw + small.width + pad * 3, max(im.height, small.height, hh) + pad * 2)
        base = pad + max(im.height, hh)   # both stand on one ground line
        t.alpha_composite(im, (pad, base - im.height))
        if human:
            t.alpha_composite(human, (pad + im.width + pad // 2, base - human.height))
        t.alpha_composite(small, (im.width + hw + pad * 2, pad))
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
    """KEEP pictures go into the art store (`art.py put`), each with its planned texture path recorded in
    commissions.md. Nothing is written into a mod's Textures folder by this item: a new PNG under GSS's Textures fails
    selftest_gss_stub_art_census.py until a row is added to Source/Core/StubJoinAudit.cs, i.e. a GSS code change and
    DLL rebuild, which belongs to the GSS version that wires the art (icons: 0.1.1; wall lamp: 0.2.0), and the battery's
    mod does not exist yet."""
    keep = {v["picture"] for f in verdicts for v in json.load(open(f))["verdicts"] if v["verdict"] == "KEEP"}
    out = {}
    for rid, kind, facing, dests in plan():
        if rid not in keep:
            print("NOT PUT %s (verdict not KEEP)" % rid)
            continue
        src = conf_path(dests[0])
        if dry:
            print("DRY put", src)
            continue
        p = subprocess.run([sys.executable, str(ART), "put", str(src)], capture_output=True, text=True, cwd=str(REPO))
        sha = (p.stdout.strip().split() or ["?"])[0] if p.returncode == 0 else None
        out[rid] = {"sha": sha, "conformed": str(src.relative_to(REPO)), "planned_textures": dests}
        print(("OK %s %s" % (rid, sha)) if sha else ("FAIL %s %s" % (rid, (p.stdout + p.stderr)[-200:])))
    if not dry:
        json.dump(out, open(HERE / "put_record.json", "w"), indent=1)


VAN = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures/ludeon.rimworld.core")


def cmd_manifest(out, verdicts=None):
    """The --textures manifest for ONE review sheet (art_sheet.py): a row per look for the wall lamp (installed in GSS),
    the battery (installed nowhere yet: its pictures are read-only reference_textures at true scale) and the icons.
    Only pictures the judge kept are shown when a verdicts file is given."""
    keep = None
    if verdicts:
        keep = {v["picture"] for f in verdicts for v in json.load(open(f))["verdicts"] if v["verdict"] == "KEEP"}
    rows = []
    ui = {"drawSize": [1, 1], "footprint": [1, 1],
          "source": "UI command icon, drawn 75 px square in the command bar at UI scale 1; it has no world size, the "
                    "1-cell panel only shows it beside a person for comparison"}
    def ref(dest, ds, fp, src):
        return {"path": str(conf_path(dest).relative_to(REPO)), "size": {"drawSize": ds, "footprint": fp, "source": src}}

    for L in LOOKS:
        l = L.lower()
        ids = ["vea_walllamp_v%d_%s_%s" % (2 if (L == "Modern" and f != "south") else 1, l, f) for f in ("east", "north", "south")]
        if keep is None or all(i in keep for i in ids):
            refs = [ref("%s/Textures/RimMandrake/GimmeSomeSlack/Styles/%s/WallLamp_%s.png" % (GSS, L, f), [1, 1], [1, 1],
                        "Core WallLamp drawSize 1x1 on a 1x1 footprint; %s facing" % f) for f in ("north", "east", "south")]
            rows.append({"key": "VEA_WallLamp_%s" % L, "part": "WallLamp", "look": L, "variant": "", "section": "GSS",
                         "label": "wall lamp - %s look (new; the IN GAME column is vanilla's)" % L,
                         "resources": ["Things/Building/Furniture/WallLamp/WallLamp"], "former": [], "reopen": True,
                         "standin": {"res": "Things/Building/Furniture/WallLamp/WallLamp", "label": "vanilla wall lamp (Core)",
                                     "source": "Core resources.assets, extracted: " + str(VAN),
                                     "faces": {f: str(VAN / ("WallLamp_%s.png" % f)) for f in ("north", "east", "south")}},
                         "reference_textures": refs,
                         "size": {"drawSize": [1, 1], "footprint": [1, 1],
                                  "source": "Core WallLamp: graphicData drawSize default 1x1 on a 1x1 footprint"}})
        bids = ["vea_battery_v1_%s_east" % l, "vea_battery_v%d_%s_north" % (3 if L == "Modern" else 1, l)]
        if keep is None or all(i in keep for i in bids):
            refs = [ref("MachineLooks/%s/Battery_%s.png" % (L, f), [3, 2] if f == "east" else [2, 3],
                        [2, 1] if f == "east" else [1, 2],
                        "Core Battery drawSize (2,3) on a 1x2 footprint (Buildings_Power.xml); %s facing" % f)
                    for f in ("north", "east", "south")]
            rows.append({"key": "VEA_Battery_%s" % L, "part": "Battery", "look": L, "variant": "", "section": "MachineLooks",
                         "label": "battery - %s look (new, for the future Machine Looks mod; the IN GAME column is vanilla's)" % L,
                         "resources": ["Things/Building/Power/Battery"], "former": [], "reopen": True,
                         "standin": {"res": "Things/Building/Power/Battery", "label": "vanilla battery (Core)",
                                     "source": "Core resources.assets, extracted: " + str(VAN),
                                     "faces": {"north": str(VAN / "Battery_north.png"), "east": str(VAN / "Battery_east.png"),
                                               "south": str(VAN / "Battery_north.png")}},
                         "reference_textures": refs,
                         "size": {"drawSize": [2, 3], "footprint": [1, 2], "source": "Core Battery drawSize (2,3), footprint 1x2"}})
        if keep is None or ("vea_lookicon_v1_%s" % l) in keep:
            rows.append({"key": "VEA_LookIcon_%s" % L, "part": "LookIcon", "look": L, "variant": "", "section": "Icons",
                         "label": "style-menu icon for the %s look (one picture, shipped by Gimme Some Slack and FlowWorks)" % L,
                         "resources": [], "former": [], "reopen": True,
                         "reference_textures": [ref("%s/Textures/RimMandrake/GimmeSomeSlack/UI/Looks/%s.png" % (GSS, L),
                                                    [1, 1], [1, 1], ui["source"])], "size": ui})
    for k, n in POLE.items():
        if keep is None or ("vea_poleicon_v1_%s" % k) in keep:
            rows.append({"key": "VEA_PoleIcon_%s" % n, "part": "PoleIcon", "look": "", "variant": n, "section": "Icons",
                         "label": "power pole button icon: %s (today a red X)" % {"LinkWire": "Link wire", "UnlinkWire": "Unlink wire",
                                                                                "UnlinkAll": "Unlink all"}[n],
                         "resources": [], "former": [], "reopen": True,
                         "reference_textures": [ref("%s/Textures/RimMandrake/GimmeSomeSlack/UI/Commands/%s.png" % (GSS, n),
                                                    [1, 1], [1, 1], ui["source"])], "size": ui})
    lead = ("<div style='border:2px solid #c9a227;padding:10px 14px;margin:0 0 12px;font-size:15px;line-height:1.5'>"
            "<b>1. What this is:</b> the new art you ordered on 2026-11-20: the wall lamp and the battery in each of the "
            "four looks, an icon per look for every style menu, and the three power-pole buttons that showed a red X. "
            "Every picture here was judged by an art judge that did not make it; only the ones it kept are shown.<br>"
            "<b>2. What you rule on:</b> keep or redo each picture (say why in the note). The looks are not rivals: "
            "accept all four together when they are right.<br><b>3. Not wired yet:</b> nothing here shows in the game "
            "until the code that uses it is built (Gimme Some Slack's next version; the battery waits for the new "
            "Machine Looks mod).</div>")
    json.dump({"schema": 1, "rows": rows, "lead_html": lead}, open(out, "w"), indent=1)
    print("manifest", out, len(rows), "rows")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "conform":
        cmd_conform()
    elif a[0] == "judgesheet":
        cmd_judgesheet(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == "manifest":
        cmd_manifest(a[1], a[a.index("--verdicts") + 1:] if "--verdicts" in a else None)
    elif a[0] == "install":
        cmd_install([x for x in a[a.index("--verdicts") + 1:] if x != "--dry"], "--dry" in a)
