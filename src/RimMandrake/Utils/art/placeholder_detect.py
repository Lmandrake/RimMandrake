#!/usr/bin/env python3
"""placeholder_detect.py — which census rows are drawn with PLACEHOLDER art (owner, 2026-10-05).

The Grey Sea sheet showed flat ellipses, cubes and vanilla cactus photos, and every gate counted them as "art of ours".
A row's live art is PLACEHOLDER when either holds:

  (a) FLAT   the texture is script-drawn: <= FLAT_MAX_COLOURS distinct colours (5-bit quantised, opaque pixels),
             >= FLAT_MIN_SMOOTH of neighbouring opaque pixels equal within 6/765, and >= FLAT_MIN_PIXELS opaque pixels.
  (b) BORROWED  the texPath depicts something else: a non-plant row (creature / fish / catch item) on a Things/Plant/*
             path, or an RM_/RSW_/RUT_ def whose texPath tail does not contain its own subject name AND the same
             texture is shared by 2+ distinct subjects, or sits under a vanilla-plant / vanilla-item folder.

    python3 src/RimMandrake/Utils/art/placeholder_detect.py sweep [--census PATH] [--out JSON]
    python3 src/RimMandrake/Utils/art/placeholder_detect.py file <png>...
    python3 src/RimMandrake/Utils/art/placeholder_detect.py selftest

Library: classify_row(row, kind, shared) -> {"verdict": PLACEHOLDER|REAL|NONE|UNMEASURED, "reasons": [...]}.
A row with several body resources is PLACEHOLDER only when EVERY body resource is. UNMEASURED = the file could not
be found and the texPath rule did not fire; that is never read as REAL by sweep totals (printed separately).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SRC = REPO / "src"
CENSUS = REPO / "Transient/biome_ffar/census.json"

# thresholds, calibrated 2026-10-05: Grey Sea script-drawn shapes read 1-3 colours / flat 0.91-1.00;
# 400 random real artpipe renders read min 12 colours, 1st percentile 74, flat <= 0.87, median 607 colours.
FLAT_MAX_COLOURS = 8
FLAT_MIN_SMOOTH = 0.85
FLAT_MIN_PIXELS = 300

VANILLA_FOLDERS = ("Things/Plant/", "Things/Item/ToxicMeat", "Things/Item/Resource/", "Things/Item/Special/")
OWN_TREE = re.compile(r"(^|/)(RM|RSW|RUT)_")
OWN_PREFIX = re.compile(r"^(RM|RSW|RUT)_")


def pixel_metrics(path):
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGBA")).astype(int)
    m = a[..., 3] > 200
    n = int(m.sum())
    if n == 0:
        return {"n": 0, "ncol": 0, "smooth": 1.0}
    q = a[..., :3][m] >> 3
    ncol = len(np.unique(q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2]))
    g = a[..., :3].sum(-1)
    h = np.abs(g[:, 1:] - g[:, :-1])[m[:, 1:] & m[:, :-1]]
    v = np.abs(g[1:] - g[:-1])[m[1:] & m[:-1]]
    d = np.concatenate([h, v])
    smooth = float((d <= 6).mean()) if len(d) else 1.0
    return {"n": n, "ncol": int(ncol), "smooth": round(smooth, 3)}


def is_flat(m) -> bool:
    return m["n"] >= FLAT_MIN_PIXELS and m["ncol"] <= FLAT_MAX_COLOURS and m["smooth"] >= FLAT_MIN_SMOOTH


def find_png(mod: str | None, res: str):
    """The picture the game draws for res: prefer _south, then bare, then any non-mask facing."""
    roots = [SRC / mod / "Textures"] if mod else []
    for r in roots + [p for p in SRC.glob("*/*/Textures")]:
        base = r / res
        if base.is_dir():  # Graphic_Random / Graphic_Collection: the folder is the texPath
            pngs = sorted(q for q in base.glob("*.png") if not q.stem.endswith("m"))
            if pngs:
                return pngs[0]
        for suf in ("_south", "", "_east", "_north", "_a", "A", "_0"):
            p = Path(str(base) + suf + ".png")
            if p.is_file():
                return p
    return None


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def subject_stem(defname: str) -> str:
    s = re.sub(r"^[A-Z]{2,4}_", "", defname)
    s = re.sub(r"(Catch|Fish|Item|Juv|Plant)$", "", s)
    s = re.sub(r"^Plant_", "", s)
    return norm(s)


def borrowed_reason(defname: str, kind: str, res: str, shared: dict):
    """(b). shared: res -> set of distinct subject stems drawing it across the census."""
    low = res
    if kind in ("fauna", "fish") and low.startswith("Things/Plant/"):
        return f"{kind} row on plant texPath {res}"
    if not OWN_PREFIX.match(defname):
        return None
    stem = subject_stem(defname)
    tail = norm(res.rsplit("/", 1)[-1])
    if stem and (stem in norm(res) or (len(tail) >= 4 and tail in stem)):
        return None
    if OWN_TREE.search(res) or not res.startswith("Things/"):
        return None  # our own folder (a deliberate family) or a donor mod's own tree: not a vanilla picture of something else
    if len(shared.get(res, ())) >= 2:
        return f"{defname} shares {res} with {len(shared[res]) - 1} other subject(s)"
    if any(res.startswith(v) for v in VANILLA_FOLDERS):
        return f"{defname} draws vanilla {res}"
    return None


def classify_row(row: dict, shared: dict) -> dict:
    kind = row.get("kind")
    dn = (row.get("defNames") or [row.get("key")])[0]
    bodies = [x for x in row["art"]["resources"] if x.get("role") == "body"] or row["art"]["resources"]
    if not bodies:
        return {"verdict": "NONE", "reasons": ["no body texPath"], "def": dn}
    per, reasons = [], []
    for x in bodies:
        res = x["res"]
        mod = ((x.get("live") or {}).get("mod"))
        why = []
        b = borrowed_reason(dn, kind, res, shared)
        if b:
            why.append("BORROWED: " + b)
        p = find_png(mod, res)
        met = pixel_metrics(p) if p else None
        if met and is_flat(met):
            why.append(f"FLAT: {met['ncol']} colours, smooth {met['smooth']}")
        per.append("PLACEHOLDER" if why else ("REAL" if met else "UNMEASURED"))
        reasons += [f"{res}: {w}" for w in why] or ([f"{res}: {met}"] if met else [f"{res}: file not found"])
    if all(v == "PLACEHOLDER" for v in per):
        v = "PLACEHOLDER"
    elif "REAL" in per:
        v = "REAL"
    else:
        v = "UNMEASURED"
    return {"verdict": v, "reasons": reasons, "def": dn}


def shared_map(census: dict) -> dict:
    sh = defaultdict(set)
    for b in census["biomes"].values():
        for r in b["rows"]:
            for x in r["art"]["resources"]:
                if x.get("role") == "body":
                    dn = (r.get("defNames") or [r["key"]])[0]
                    sh[x["res"]].add(subject_stem(dn))
    return sh


def sweep(census_path=CENSUS):
    census = json.load(open(census_path))
    sh = shared_map(census)
    out = {}
    for bd in census["biome_order"]:
        for r in census["biomes"][bd]["rows"]:
            c = classify_row(r, sh)
            c.update(kind=r.get("kind"), label=r.get("label"), biome=bd)
            out.setdefault(bd, []).append(c)
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "file":
        for p in argv[1:]:
            m = pixel_metrics(p)
            print(p, m, "FLAT" if is_flat(m) else "real")
        return 0
    if cmd == "calibrate":
        import numpy as np
        res = sweep()
        pl, rl = [], []
        for rows in res.values():
            for x in rows:
                for rs in x["reasons"]:
                    pass
        census = json.load(open(CENSUS))
        for bd in census["biome_order"]:
            for r in census["biomes"][bd]["rows"]:
                for x in r["art"]["resources"]:
                    f = find_png((x.get("live") or {}).get("mod"), x["res"])
                    if f:
                        m = pixel_metrics(f)
                        (pl if is_flat(m) else rl).append(m)
        import glob
        art = [pixel_metrics(f) for f in glob.glob("/mnt/d/Luke/dev/_artpipe/_artsrc/*/*.png")[::6]]
        for name, ms in (("FLAT (live census)", pl), ("live census not flat", rl), ("artpipe real renders", art)):
            for k in ("ncol", "smooth"):
                v = np.array([m[k] for m in ms if m["n"] >= FLAT_MIN_PIXELS], float)
                if len(v):
                    print(f"{name:22} n={len(v):4} {k:6} min {v.min():8.3f} p5 {np.percentile(v,5):8.3f} median {np.median(v):8.3f} p95 {np.percentile(v,95):8.3f} max {v.max():8.3f}")
        return 0
    if cmd == "selftest":
        import selftest_placeholder_detect as T
        return T.run()
    if cmd == "sweep":
        cp = CENSUS
        outp = None
        if "--census" in argv:
            cp = Path(argv[argv.index("--census") + 1])
        if "--out" in argv:
            outp = Path(argv[argv.index("--out") + 1])
        res = sweep(cp)
        print(f"{'biome':26} rows  PLACEHOLDER  REAL  UNMEAS  NONE")
        for bd, rows in sorted(res.items(), key=lambda kv: -sum(r['verdict'] == 'PLACEHOLDER' for r in kv[1])):
            cnt = lambda v: sum(r["verdict"] == v for r in rows)
            print(f"{bd:26} {len(rows):4} {cnt('PLACEHOLDER'):8} {cnt('REAL'):9} {cnt('UNMEASURED'):6} {cnt('NONE'):6}")
        if outp:
            outp.write_text(json.dumps(res, indent=1))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
