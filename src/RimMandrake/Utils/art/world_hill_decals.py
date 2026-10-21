#!/usr/bin/env python3
"""Our own world-map hill decals (owner 2026-10-20: "Let's get it looking great again"). Procedural, no donor bytes.

How 1.6 draws hills (RimSage, WorldDrawLayer_Hills.Regenerate + WorldMaterials static ctor):
  * four shared materials, World/Hills/{SmallHills,LargeHills,Mountains,Impassable}, shader WorldOverlayTransparentLit,
    render queue 3510, material colour white: NO biome tint, NO def (there is no HillsDef);
  * one quad per hilly tile without a landmark, 0.9-1.1 x tile size, lifted 0.005, random rotation 0-360, centre jittered
    by 0-0.37 (small) / 0-0.2 (large) / 0-0.08 (mountains, impassable) x average tile size;
  * each texture is a 2x2 atlas, one random cell per tile.
  Vanilla cells (128 px atlas) are brown blots (mean RGB ~80,57,36, alpha ~0.45) with a hard dark outline: on our faces
  they read as stamped hexes. The Rust Cathedral "white speckle" is NOT hills: it is Odyssey landmark icons (Ruins,
  AncientVents, ...) on 155 of its 236 tiles (landmark tiles draw no hill at all).

Ours: a dark warm-neutral colour whose ALPHA carries the relief, so the face shows through and the hill takes the biome's
own hue (the material is shared by every biome, so a tint cannot come from anywhere else). Because every quad is
rotated at random, the shading is rotation-invariant (height darkens, crests lighten), never a directional light.
Soft edges, zero alpha on every cell border (no outline, no atlas bleed); mountains nearly fill their cell so a range
merges into one massif. Shipped at World/RM_Hills/* and swapped onto the vanilla materials by RM_WorldLook.ApplyHills
(Mod Settings "Planet: soft hill shading", default on; off restores vanilla).

usage:
  python3 world_hill_decals.py gen   [--out DIR]   write the 4 atlases + sheet + stats.json to DIR
  python3 world_hill_decals.py check [--src]       spec check on DIR (default) or on the installed files
  python3 world_hill_decals.py install [--dry-run] art-ledger install (art.py install)
DIR defaults to <agent storage>/rimmandrake/scratch/hilldecals/tex.
"""
import argparse, json, os, subprocess, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
MOD = "RimMandrake/TerminalBiomes"          # a member of the composed RimMandrake.Biomes, always in its LoadFolders
REL = "World/RM_Hills/{}.png"
OWNER = "Let's get it looking great again"
N, CELL = 256, 128
RGB = (36, 28, 21)                          # dark warm neutral; alpha does the work
# name: (seed, max alpha, footprint radius (cell = 1), base, mounds, mound sigma range, ridge weight)
SPEC = {
    "SmallHills": (11, 0.22, 0.70, 0.00, (3, 5), (0.12, 0.20), 0.35),
    "LargeHills": (12, 0.30, 0.80, 0.10, (4, 7), (0.16, 0.26), 0.50),
    "Mountains":  (13, 0.40, 0.92, 0.55, (4, 6), (0.20, 0.32), 0.75),
    "Impassable": (14, 0.50, 0.95, 0.75, (5, 7), (0.22, 0.34), 0.85),
}


def storage_root():
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True, check=True).stdout.strip()
    return os.path.join(r, "rimmandrake", "scratch", "hilldecals", "tex")


def noise(rng, n, octaves=4, k0=4):
    """Smooth value noise in [0,1] on an n x n grid (bicubic-upsampled random lattices)."""
    out = np.zeros((n, n)); amp = 1.0; tot = 0.0
    for o in range(octaves):
        k = k0 * 2 ** o
        g = rng.random((k + 1, k + 1))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        out += amp * np.asarray(img, float) / 255.0; tot += amp; amp *= 0.55
    return out / tot


def cell(name, idx):
    seed, amax, foot, base, (m0, m1), (s0, s1), ridge = SPEC[name]
    rng = np.random.default_rng(seed * 100 + idx)
    y, x = np.mgrid[0:CELL, 0:CELL]
    u = (x + 0.5) / CELL * 2 - 1; v = (y + 0.5) / CELL * 2 - 1
    r = np.hypot(u, v)
    # irregular footprint: radius wobbles with angle so a massif is not a disc
    ang = np.arctan2(v, u)
    wob = 1 + 0.10 * np.sin(3 * ang + rng.uniform(0, 6.3)) + 0.07 * np.sin(5 * ang + rng.uniform(0, 6.3))
    rr = r / (foot * wob)
    env = np.clip((1 - rr) / 0.45, 0, 1); env = env * env * (3 - 2 * env)   # plateau, soft last 45 % to zero
    h = np.full_like(u, base)
    for _ in range(rng.integers(m0, m1 + 1)):
        cr = foot * 0.6 * np.sqrt(rng.random()); ca = rng.uniform(0, 2 * np.pi)
        s = rng.uniform(s0, s1)
        h += np.exp(-(((u - cr * np.cos(ca)) ** 2 + (v - cr * np.sin(ca)) ** 2) / (2 * s * s)))
    h = np.clip(h, 0, None); h /= max(h.max(), 1e-6)
    # ridged detail: crest lines (1 on a crest) at two scales; crests are LIGHTER (less dark), valleys darker
    n1 = noise(rng, CELL, 3, 6); n2 = noise(rng, CELL, 2, 14)
    crest = np.maximum(1 - np.abs(2 * n1 - 1), 0) ** 4 * 0.7 + np.maximum(1 - np.abs(2 * n2 - 1), 0) ** 6 * 0.3
    valley = np.abs(2 * n1 - 1) ** 1.5
    detail = 1 - ridge * (0.55 * crest - 0.35 * valley + 0.10)
    a = amax * np.clip(h * detail, 0, 1) ** 0.85 * env
    # hard guarantee: nothing within 3 px of the cell edge
    edge = np.minimum.reduce([x, y, CELL - 1 - x, CELL - 1 - y])
    a[edge < 3] = 0
    return np.clip(a, 0, amax)


def atlas(name):
    A = np.zeros((N, N))
    for i in range(4):
        cx, cy = (i % 2) * CELL, (i // 2) * CELL
        A[cy:cy + CELL, cx:cx + CELL] = cell(name, i)
    img = np.zeros((N, N, 4), np.uint8)
    img[..., 0], img[..., 1], img[..., 2] = RGB
    img[..., 3] = np.round(A * 255).astype(np.uint8)
    img[img[..., 3] == 0, :3] = 0                                          # clean transparent pixels
    img[img[..., 3] > 0, 0], img[img[..., 3] > 0, 1], img[img[..., 3] > 0, 2] = RGB
    return Image.fromarray(img, "RGBA")


def stats(path, name):
    a = np.asarray(Image.open(path).convert("RGBA"), float)
    al = a[..., 3] / 255; bad = []
    if a.shape[:2] != (N, N): bad.append("size %s" % (a.shape[:2],))
    cov = float((al > 0.02).mean()); amax = float(al.max())
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[al > 0]
    if lum.size and lum.max() > 80: bad.append("bright pixel lum %.0f (no white)" % lum.max())
    if amax > SPEC[name][1] + 0.01: bad.append("alpha max %.2f > %.2f" % (amax, SPEC[name][1]))
    for i in range(4):
        cx, cy = (i % 2) * CELL, (i // 2) * CELL
        c = al[cy:cy + CELL, cx:cx + CELL]
        rim = np.concatenate([c[:3].ravel(), c[-3:].ravel(), c[:, :3].ravel(), c[:, -3:].ravel()])
        if rim.max() > 0: bad.append("cell %d edge alpha %.3f" % (i, rim.max()))
        if (c > 0.02).mean() < 0.02: bad.append("cell %d empty" % i)
    # no outline: the largest one-pixel alpha step stays small (vanilla's outline jumps 0.53-0.75 in one px, 128 px atlas)
    g = max(np.abs(np.diff(al, axis=0)).max(), np.abs(np.diff(al, axis=1)).max())
    if g > 0.12: bad.append("hard edge: alpha step %.3f in one px" % g)
    return {"cov": round(cov, 3), "alpha_max": round(amax, 3), "alpha_mean_on": round(float(al[al > 0.02].mean()), 3),
            "max_step": round(float(g), 3), "bad": bad}


def gen(out):
    os.makedirs(out, exist_ok=True); res = {}
    sheet = Image.new("RGBA", (N * 4 + 30, N + 20), (150, 120, 90, 255))
    for k, name in enumerate(SPEC):
        p = os.path.join(out, name + ".png"); im = atlas(name); im.save(p)
        sheet.alpha_composite(im, (10 + k * (N + 3), 10)); res[name] = stats(p, name)
    sheet.save(os.path.join(out, "sheet.png"))
    json.dump(res, open(os.path.join(out, "stats.json"), "w"), indent=1)
    return res


def check(out, from_src):
    res = {}
    for name in SPEC:
        p = (os.path.join(REPO, "src", MOD, "Textures", REL.format(name)) if from_src else os.path.join(out, name + ".png"))
        res[name] = stats(p, name) if os.path.exists(p) else {"bad": ["missing " + p]}
    return res


def report(res):
    fails = 0
    for k, s in res.items():
        print(("FAIL " if s["bad"] else "ok   ") + k, {x: y for x, y in s.items() if x != "bad"}, "; ".join(s["bad"]))
        fails += bool(s["bad"])
    return fails


def install(out, dry):
    bad = 0
    for name in SPEC:
        stage = os.path.join(REPO, "Transient", "hill_decals_stage", name + ".png")   # art.py wants a file inside the clone
        os.makedirs(os.path.dirname(stage), exist_ok=True)
        open(stage, "wb").write(open(os.path.join(out, name + ".png"), "rb").read())
        cmd = [sys.executable, os.path.join(REPO, "src/RimMandrake/Utils/art/art.py"), "install", MOD, REL.format(name),
               "--file", os.path.relpath(stage, REPO), "--owner-said", OWNER] + (["--dry-run"] if dry else [])
        x = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        o = (x.stdout + x.stderr).strip().splitlines(); bad += x.returncode != 0
        print(x.returncode, MOD, REL.format(name), (o[-1] if o else "")[:120])
    print("install failures", bad); return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["gen", "check", "install"])
    ap.add_argument("--out"); ap.add_argument("--src", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); out = a.out or storage_root()
    if a.cmd == "gen": sys.exit(1 if report(gen(out)) else 0)
    if a.cmd == "check": sys.exit(1 if report(check(out, a.src)) else 0)
    sys.exit(1 if install(out, a.dry_run) else 0)
