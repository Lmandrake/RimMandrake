#!/usr/bin/env python3
"""Offline portrait of a planet region the way the 1.6 world map layers it, for judging hill decals.

Layers, in the game's order (RM_WorldLook / vanilla lifts): biome faces (+ our soft border blend, approximated by a
blur at biome edges) < hills (+0.005, WorldDrawLayer_Hills: one quad per hilly tile without a landmark, 0.9-1.1 x tile
size, random rotation, centre jitter, random 2x2 atlas cell) < rivers (+0.01, dark bank + azure water, RM_WorldPaths)
< landmarks (drawAboveRoads ones at +0.025, Odyssey icons). Faces are sampled with uv = position x 0.1 (the
pollution/blend layers' mapping; the WorldTerrain shader's own span is UNMEASURED), so face grain is indicative.

usage: python3 world_hill_preview.py --region "Rust Cathedral" --hills DIR --out PNG [--landmarks DIR] [--tiles 26]
  DIR holds SmallHills/LargeHills/Mountains/Impassable.png (a 2x2 atlas each). Save: world/ASHKARR_DEV_START_2026-10-20.rws
  with both 2026-10-20 mountain plans applied (the live hilliness after MOUNTAINS and MOUNTAINS2).
"""
import argparse, glob, json, os, re, sys
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
sys.path.insert(0, os.path.dirname(HERE))
import worldview  # noqa: E402

SAVE = os.path.join(REPO, "world", "ASHKARR_DEV_START_2026-10-20.rws")
PLANS = [os.path.join(REPO, "world", p) for p in ("ASHKARR_MOUNTAINS_2026-10-20_plan.json", "ASHKARR_MOUNTAINS2_2026-10-20_plan.json")]
HILL = {2: ("SmallHills", 0.37), 3: ("LargeHills", 0.2), 4: ("Mountains", 0.08), 5: ("Impassable", 0.08)}
RIVER_W = {"Creek": 0.32, "River": 0.46, "LargeRiver": 0.62, "HugeRiver": 0.82}
GAME = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"


def face_paths():
    tex = {}
    for f in glob.glob(os.path.join(REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        t = open(f, encoding="utf-8", errors="replace").read()
        if "<BiomeDef" not in t: continue
        try: r = ET.fromstring(t)
        except ET.ParseError: continue
        root = f.split(os.sep + "Defs" + os.sep)[0]
        for d in r.iter("BiomeDef"):
            n, p = d.findtext("defName"), d.findtext("texture")
            if n and p:
                cand = os.path.join(root, "Textures", p + ".png")
                if os.path.exists(cand): tex[n] = cand
    return tex


def landmark_defs():
    m, nm = {}, {}
    for f in glob.glob(GAME + "/*/Defs/**/*.xml", recursive=True) + glob.glob(os.path.join(REPO, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        t = open(f, encoding="utf-8", errors="replace").read()
        if "LandmarkDef" not in t: continue
        try: r = ET.fromstring(t)
        except ET.ParseError: continue
        for d in r.iter("LandmarkDef"):
            k = d.findtext("defName") or "@" + (d.get("Name") or "")
            if d.get("Name"): nm[d.get("Name")] = k
            m[k] = (d.findtext("iconTexturePath"), d.findtext("atlasSize"), d.findtext("drawScale"), d.get("ParentName"), d.findtext("drawType"))
    def res(k, i, depth=0):
        v = m[k]
        if v[i] is None and v[3] in nm and depth < 6: return res(nm[v[3]], i, depth + 1)
        return v[i]
    return {k: (res(k, 0), res(k, 1), res(k, 2), res(k, 4)) for k in m if not k.startswith("@")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", required=True); ap.add_argument("--hills", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--landmarks"); ap.add_argument("--tiles", type=float, default=26.0)
    ap.add_argument("--width", type=int, default=1100); ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--title", default="")
    a = ap.parse_args()

    pv = worldview.PlanetView(SAVE)
    hilly = pv.hilly.astype(int).copy()
    for p in PLANS:
        for t, h in json.load(open(p))["hilliness"].items(): hilly[int(t)] = int(h)
    g = pv.geom; V = g.vec
    names = {f["index"]: f["name"] for f in pv.features}
    region = [t for t in range(pv.n) if names.get(int(pv.feature_idx[t])) == a.region]
    if not region: sys.exit("no tiles in region " + a.region)
    c = V[region].mean(0); c /= np.linalg.norm(c)
    up = np.array([0, 1.0, 0]); east = np.cross(up, c); east /= np.linalg.norm(east); north = np.cross(c, east)
    spacing = np.mean([np.linalg.norm(V[t] - V[g.neighbours(t)[0]]) for t in range(0, pv.n, 97)])   # unit sphere
    W, H = a.width, a.height
    ppu = W / (a.tiles * spacing)                       # pixels per unit-sphere length
    def proj(v): return (W / 2 + ppu * (v @ east), H / 2 - ppu * (v @ north))

    # nearest tile per pixel, among tiles near the window
    xs, ys = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    pe = (xs - W / 2) / ppu; pn = -(ys - H / 2) / ppu
    pz = np.sqrt(np.clip(1 - pe ** 2 - pn ** 2, 0, 1))
    P = pe[..., None] * east + pn[..., None] * north + pz[..., None] * c
    near = np.where(V @ c > np.cos(np.radians(max(W, H) / ppu * 60)))[0]
    Pf = P.reshape(-1, 3); owner = np.empty(len(Pf), np.int32)
    for i in range(0, len(Pf), 20000):
        owner[i:i + 20000] = near[np.argmax(Pf[i:i + 20000] @ V[near].T, axis=1)]
    owner = owner.reshape(H, W)

    # faces: uv = position (radius 100) x 0.1 in the local tangent plane
    tex = face_paths(); cache = {}
    U = (pe * 100 * 0.1); Vv = (pn * 100 * 0.1)
    img = np.zeros((H, W, 3))
    for b in set(pv.biome[t] for t in np.unique(owner)):
        m = np.isin(owner, [t for t in np.unique(owner) if pv.biome[t] == b])
        if b in tex:
            if b not in cache: cache[b] = np.asarray(Image.open(tex[b]).convert("RGB"), float)
            T = cache[b]; th, tw = T.shape[:2]
            img[m] = T[(Vv[m] * th).astype(int) % th, (U[m] * tw).astype(int) % tw]
        else:
            col = worldview.biome_color(b).lstrip("#"); img[m] = [int(col[i:i + 2], 16) for i in (0, 2, 4)]
    water = np.array([pv.is_water[t] for t in owner.ravel()]).reshape(H, W)
    img[water] = img[water] * 0.5 + np.array([0.05, 0.09, 0.20]) * 255 * 0.5      # RM_WorldLook deep film
    # soft borders: blur, used only where the biome changes within ~0.5 tile
    bid = np.vectorize(lambda t: hash(pv.biome[t]) % 100000)(owner)
    edge = np.zeros((H, W), bool)
    edge[:, 1:] |= bid[:, 1:] != bid[:, :-1]; edge[1:] |= bid[1:] != bid[:-1]
    r = max(2, int(0.45 * spacing * ppu))
    ew = np.asarray(Image.fromarray((edge * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * (r // 2) + 1))
                    .filter(ImageFilter.GaussianBlur(r / 2)), float) / 255
    bl = np.asarray(Image.fromarray(img.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r / 1.5)), float)
    ew = np.clip(ew * 2.5, 0, 1)[..., None] * (~water)[..., None]
    img = img * (1 - ew) + bl * ew
    canvas = Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")

    # hills
    lmk = {int(l["tile"]): l["def"] for l in pv.landmarks if int(l.get("layer", 0)) == 0}
    atl = {k: Image.open(os.path.join(a.hills, k + ".png")).convert("RGBA") for k, _ in HILL.values()}
    rng = np.random.default_rng(7)
    vis = [t for t in near if V[t] @ c > 0.5]
    tsz = spacing * ppu
    for t in vis:
        h = hilly[t]
        if h not in HILL or t in lmk: continue
        k, off = HILL[h]
        x, y = proj(V[t])
        ang = rng.uniform(0, 2 * np.pi); d = rng.uniform(0, off) * tsz
        x += d * np.cos(ang); y += d * np.sin(ang)
        s = max(2, int(rng.uniform(0.9, 1.1) * tsz))
        A = atl[k]; cw = A.width // 2
        ci, cj = rng.integers(0, 2), rng.integers(0, 2)
        q = A.crop((ci * cw, cj * cw, ci * cw + cw, cj * cw + cw)).resize((s, s), Image.LANCZOS).rotate(rng.uniform(0, 360), Image.BICUBIC)
        canvas.alpha_composite(q, (int(x - s / 2), int(y - s / 2))) if 0 <= int(x - s / 2) and 0 <= int(y - s / 2) and int(x + s / 2) < W and int(y + s / 2) < H else None

    # rivers: dark bank, azure water 0.2 narrower (RM_WorldPaths)
    dr = ImageDraw.Draw(canvas)
    for lay, (col, dw) in enumerate((((5, 13, 46, 255), 0.0), ((15, 84, 217, 255), 0.2))):
        for (ta, tb, dn, _) in pv.rivers:
            if V[ta] @ c < 0.5: continue
            w = max(1, int((RIVER_W.get(dn, 0.4) - dw) * tsz * 0.5))
            dr.line([proj(V[ta]), proj(V[tb])], fill=col, width=w, joint="curve")

    # landmarks
    if a.landmarks:
        ld = landmark_defs(); miss = set()
        for t, dn in lmk.items():
            if V[t] @ c < 0.5: continue
            p, atls, sc, dt = ld.get(dn, (None, None, None, None))
            if dt not in (None, "Standard"): continue          # only Standard landmarks print a quad (WorldDrawLayer_Landmarks)
            f = os.path.join(a.landmarks, os.path.basename(p) + ".png") if p else None
            if p and not os.path.exists(f):
                f = next(iter(glob.glob(os.path.join(REPO, "src", "*", "*", "Textures", p + ".png"))), f)
            if not f or not os.path.exists(f): miss.add(dn); continue
            L = Image.open(f).convert("RGBA")
            ax, az = (int(x) for x in re.findall(r"\d+", atls or "(1,1)")[:2]) if atls else (1, 1)
            cw, chh = L.width // ax, L.height // az
            ci, cj = rng.integers(0, ax), rng.integers(0, az)
            s = max(2, int(tsz * float(sc or 1)))
            q = L.crop((ci * cw, cj * chh, ci * cw + cw, cj * chh + chh)).resize((s, s), Image.LANCZOS).rotate(rng.uniform(0, 360), Image.BICUBIC)
            x, y = proj(V[t])
            if 0 <= x - s / 2 and 0 <= y - s / 2 and x + s / 2 < W and y + s / 2 < H: canvas.alpha_composite(q, (int(x - s / 2), int(y - s / 2)))
        if miss: print("landmarks with no icon offline (not drawn):", ", ".join(sorted(miss)))
    if a.title:
        ImageDraw.Draw(canvas).rectangle((0, 0, W, 30), fill=(0, 0, 0, 170)); ImageDraw.Draw(canvas).text((10, 8), a.title, fill=(255, 255, 255, 255))
    canvas.convert("RGB").save(a.out)
    print("wrote", a.out, "tiles", len(region), "tile px %.1f" % tsz)


if __name__ == "__main__":
    main()
