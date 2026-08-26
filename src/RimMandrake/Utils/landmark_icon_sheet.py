"""Every landmark icon Ash'karr draws, on one sheet, flagged by how flat it is.

Three things here are not guessable and cost an afternoon each if you guess wrong:

  * A LandmarkDef's icon is `iconTexturePath`, which is NOT the defName --
    `VEE_RockRidge` draws `World/Landmarks/VEE_Ridge`.  When the field is absent the
    engine falls back to `World/Landmarks/<defName>`, and most vanilla defs rely on it.
  * `<LandmarkDef ParentName="...">` carries attributes, so a regex for the bare tag
    misses 23 of 110 defs -- Bay and Ruins among them.
  * Vanilla icons are NOT loose PNGs.  They live in the Odyssey AssetBundle; read them
    from the extracted cache under observed/inventory/bundle_textures/.

The flat/pattern split is measured, not eyeballed: a one-colour icon at 52% coverage is
a solid stamp and looks it, while a one-colour icon at 15% coverage is a line drawing
whose SHAPE carries it (Dunes, VEE_DryRiver) and repainting it would be vandalism.
"""
import csv, glob, json, os, re
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld"
BUNDLE = os.path.join(REPO, "observed/inventory/bundle_textures")
REPAINT = os.path.join(REPO, "src/RimMandrake/AshkarrLandmarkArt/Textures/World/Landmarks")
DEF_FILES = [
    f"{GAME}/Data/Odyssey/Defs/TileMutators/Landmarks.xml",
    f"{WORKSHOP}/1841354677/1.6/Mods/Odyssey/Defs/TileMutators/Landmarks.xml",
    f"{WORKSHOP}/3656316229/1.6/Defs/TileMutators/Landmarks.xml",
    # Star Wars Animal Collection files its two Sarlacc landmarks with the BUILDINGS,
    # not under TileMutators, and their icons are named Landmark_* not sw_*.
    f"{WORKSHOP}/3497316713/1.6/Defs/ThingDefs_Buildings/SW_Buildings_Natural.xml",
]
SOLID_COVERAGE = 32.0        # >= this and few colours -> a solid stamp, worth repainting
FLAT_COLOURS = 6


def landmark_defs():
    raw, named = {}, {}
    for f in DEF_FILES:
        if not os.path.exists(f):
            continue
        s = open(f, encoding="utf-8").read()
        for m in re.finditer(r"<LandmarkDef([^>]*)>(.*?)</LandmarkDef>", s, re.S):
            attr, blk = m.group(1), m.group(2)
            icon = re.search(r"<iconTexturePath>(.*?)</iconTexturePath>", blk)
            atlas = re.search(r"<atlasSize>\((\d+),\s*(\d+)\)</atlasSize>", blk)
            rec = {"icon": icon.group(1) if icon else None,
                   "atlas": (int(atlas.group(1)), int(atlas.group(2))) if atlas else None,
                   "parent": (re.search(r'ParentName="([^"]+)"', attr) or [None, None])[1]
                             if re.search(r'ParentName="([^"]+)"', attr) else None}
            # (?<!Parent) matters: ParentName="X" CONTAINS Name="X", so a naive search
            # registers every child under its parent's name and clobbers the abstract.
            # That is what hid AncientGarrison/Warehouse/ChemfuelRefinery, which all
            # inherit World/Landmarks/AncientLaunchSite and share one icon.
            nm = re.search(r'(?<!Parent)Name="([^"]+)"', attr)
            dn = re.search(r"<defName>(.*?)</defName>", blk)
            if nm:
                named[nm.group(1)] = rec
            if dn:
                raw[dn.group(1)] = rec

    def inherit(rec, key):
        seen = 0
        while rec and rec.get(key) is None and rec.get("parent") and seen < 6:
            rec = named.get(rec["parent"]); seen += 1
        return rec.get(key) if rec else None

    out = {}
    for d, rec in raw.items():
        out[d] = {"icon": inherit(rec, "icon") or f"World/Landmarks/{d}",
                  "atlas": inherit(rec, "atlas") or (1, 1)}
    return out


def texture_index():
    """texPath-ish key -> file, for loose mod PNGs and the extracted bundle cache."""
    idx = {}
    # ONE level only.  Measured 2026-08-25 over 1254 workshop mods: the root-level
    # glob finds all 43 landmark PNGs in 4.4 s; going one level deeper costs 18 s and
    # two levels 49 s and both find NOTHING.  A recursive walk never finishes at all.
    # Alpha Biomes files its landmark icons under Textures/UI/Icons/AB_Landmarks/, NOT
    # under World/Landmarks -- the iconTexturePath is the only thing that knows.
    for root in (WORKSHOP, f"{GAME}/Mods"):
        for sub in ("World/Landmarks", "UI/Icons/AB_Landmarks", "UI/Icons/AB_MutatorIcons"):
            for p in glob.glob(f"{root}/*/Textures/{sub}/*.png"):
                idx.setdefault(p.split("/Textures/", 1)[1][:-4].lower(), p)
    ic = f"{BUNDLE}/index.csv"
    if os.path.exists(ic):
        for r in csv.DictReader(open(ic)):
            cont = (r["container"] or "").lower()
            key = cont.split("/textures/", 1)[1][:-4] if "/textures/" in cont else \
                  f"world/landmarks/{r['m_Name'].lower()}"
            idx.setdefault(key, f"{BUNDLE}/{r['file']}")
    return idx


def measure(path):
    a = np.array(Image.open(path).convert("RGBA"))
    m = a[..., 3] > 96
    if m.sum() < 50:
        return None
    return {"colours": len(np.unique(a[..., :3][m].reshape(-1, 3), axis=0)),
            "coverage": 100 * m.mean(), "size": a.shape[0]}


def build(out_png):
    defs, idx = landmark_defs(), texture_index()
    counts = Counter(r["landmark"] for r in
                     csv.DictReader(open(os.path.join(REPO, "world/ASHKARR_WORLDMAP_landmarks.csv"))))
    rows = []
    for d, n in counts.most_common():
        rp = f"{REPAINT}/{d}.png"
        if os.path.exists(rp):
            path, where = rp, "REPAINTED"
        else:
            key = defs.get(d, {}).get("icon", f"World/Landmarks/{d}").lower()
            path = idx.get(key)
            where = "vanilla" if path and BUNDLE in path else "mod"
        st = measure(path) if path else None
        if st is None:
            rows.append((n, d, None, None, "icon not found")); continue
        if where == "REPAINTED":
            verdict = "REPAINTED"
        elif st["colours"] <= FLAT_COLOURS and st["coverage"] >= SOLID_COVERAGE:
            verdict = "FLAT STAMP"
        elif st["colours"] <= FLAT_COLOURS:
            verdict = "line art, ok"
        else:
            verdict = "painted, ok"
        rows.append((n, d, path, st, verdict))

    terr = Image.open(os.path.join(REPO, "world/_landmark_sheet_bg.png")).convert("RGB") \
        if os.path.exists(os.path.join(REPO, "world/_landmark_sheet_bg.png")) else None
    C, LBL, COLS = 132, 40, 8
    pad = 8
    r_n = (len(rows) + COLS - 1) // COLS
    W = COLS * (C + pad) + pad
    H = r_n * (C + LBL + pad) + pad + 34
    sheet = Image.new("RGBA", (W, H), (188, 176, 148, 255))
    if terr:
        sheet.paste(terr.resize((W, H)).convert("RGBA"))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    except OSError:
        f = fb = ImageFont.load_default()
    d.text((pad, 8), f"Ash'karr landmark icons — {sum(counts.values())} placements, "
                     f"{len(rows)} defs, shown at 128 px", font=fb, fill=(20, 20, 20))
    COL = {"FLAT STAMP": (168, 24, 24), "REPAINTED": (16, 110, 40),
           "line art, ok": (60, 60, 60), "painted, ok": (60, 60, 60), "icon not found": (150, 90, 0)}
    for i, (n, name, path, st, verdict) in enumerate(rows):
        r, c = divmod(i, COLS)
        x, y = pad + c * (C + pad), 34 + pad + r * (C + LBL + pad)
        if path:
            im = Image.open(path).convert("RGBA")
            s = im.size[0] // 2                       # every landmark atlas is 2x2
            sheet.alpha_composite(im.crop((0, 0, s, s)).resize((C, C), Image.LANCZOS), (x, y))
        d.text((x, y + C + 1), f"{name[:22]}", font=f, fill=(15, 15, 15))
        d.text((x, y + C + 14), f"{n} tiles · {st['colours'] if st else '?'} col", font=f,
               fill=(15, 15, 15))
        d.text((x, y + C + 27), verdict, font=f, fill=COL[verdict])
    sheet.convert("RGB").save(out_png)
    return out_png, rows


if __name__ == "__main__":
    import sys
    p, rows = build(sys.argv[1] if len(sys.argv) > 1 else "TRANSIENT_ashkarr_landmarks.png")
    flat = [r for r in rows if r[4] == "FLAT STAMP"]
    print(p)
    print(f"{len(flat)} flat stamps, {sum(r[0] for r in flat)} placements:",
          ", ".join(f"{r[1]}({r[0]})" for r in flat))
    nf = [r for r in rows if r[4] == "icon not found"]
    if nf:
        print("icon not found:", ", ".join(r[1] for r in nf))
