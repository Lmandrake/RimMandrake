#!/usr/bin/env python3
"""icon_outline_census.py — which item icons still carry a drawn near-black outline, and why each one may.

    python3 src/RimMandrake/Utils/art/icon_outline_census.py [--check] [--out FILE.json]

ICON_OUTLINE_REPAINT_1. Scope and metric are the 2026-10-10 census: every PNG under src/**/Textures/Things/**
whose path holds Item, Resource or Food. Opaque = alpha > 128; an edge pixel is opaque with a transparent
4-neighbour; the EDGE share is the fraction of edge pixels with luminance < 45. An icon reading >= 0.90 is
OUTLINED. The metric cannot tell a drawn rim from a near-black MATERIAL (soot, bitumen, black loam: batch-2
review), so a repaint over 0.30 is still clean when its interior (pixels >= 3 px inside the edge) is about as dark
(edge share - interior share <= 0.25, the rule the batch-3 report set).

Every OUTLINED icon must be accounted for, else it is OPEN:
  KEPT        its picture is under an owner keep in the art ledger (sheet picks of IN GAME art land as keeps)
  PICKED      its picture is the column he picked on picks_icons_sheet_2026-10-19
  HELD        that sheet's row for it is `hold`, or its pick was assigned `not_needed`
  TWIN        a RUT_ Utinni copy whose RM_ twin's row he decided keep-in-game
  MASK        a `_m` colour mask (black/white by design, not an icon)
  DARK        a near-black material, not a rim: edge share - interior share <= 0.25
  ORPHAN      no texPath in any src/**/*.xml reads it (exact, its variant stem, or its folder); dead art
  QUEUED      a job of this item for its stem waits in the artpipe pending/active dir (not done: --check fails)
Every no-outline render of this item that is installed (sha = a `*_nooutline` column on that sheet) must read
EDGE < 0.30 or pass the dark-material rule; else it is BAD.

--check exits 0 when OPEN and BAD are both empty, 1 otherwise; 2 when an input it needs cannot be read.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SHEET = "Transient/biome_ffar/picks_icons_sheet_2026-10-19.decisions.json"
SNAPSHOT = "infrastructure/state/art/sheets/picks_icons_sheet_2026-10-19.snapshot.json"
SCOPE = ("Item", "Resource", "Food")
OUTLINED, REPAINT_MAX, DARK_GAP = 0.90, 0.30, 0.25
VARIANT = re.compile(r"_(a|b|c|d|e|A|B|C|D|E|east|north|south|west)$")


def shares(rgba: np.ndarray):
    """(edge share, interior share) of luminance < 45, or None when nothing is opaque."""
    a = rgba[..., 3] > 128
    if not a.any():
        return None
    pad = np.pad(a, 1)
    edge = a & (~pad[:-2, 1:-1] | ~pad[2:, 1:-1] | ~pad[1:-1, :-2] | ~pad[1:-1, 2:])
    inner = a.copy()
    for _ in range(3):                                 # erode 3 px: interior = >= 3 px inside the edge
        p = np.pad(inner, 1)
        inner = inner & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    lum = 0.299 * rgba[..., 0] + 0.587 * rgba[..., 1] + 0.114 * rgba[..., 2]
    dark = lum < 45
    e = float((dark & edge).sum() / edge.sum())
    i = float((dark & inner).sum() / inner.sum()) if inner.any() else e
    return e, i


def measure(path):
    return shares(np.asarray(Image.open(path).convert("RGBA")).astype(float))


def stem(path):
    return VARIANT.sub("", os.path.basename(path)[:-4])


def load_sheet(root):
    d = json.load(open(os.path.join(root, SHEET)))["decisions"]
    rows = json.load(open(os.path.join(root, SNAPSHOT)))["rows"]
    return d, rows


def row_for(path, keys):
    """Sheet row of an icon file: its stem (variant suffix stripped), RUT_ read as RM_, a bare fish stem read as its
    Catch; else the longest row key the path contains."""
    s = stem(path)
    tries = {s.lower(), re.sub(r"^rut_", "rm_", s.lower()), "rsw_" + s.lower(), "rm_" + s.lower()}
    tries |= {t + "catch" for t in tries}
    for k in keys:
        if k.lower() in tries:
            return k
    hits = [k for k in keys if k.lower() in path.lower()]
    return max(hits, key=len) if hits else None


def xml_texpaths(root):
    tps = set()
    for x in glob.glob(os.path.join(root, "src/**/*.xml"), recursive=True):
        try:
            tps.update(t.strip() for t in re.findall(r"<\w*[tT]exPath>([^<]+)</", open(x, errors="replace").read()))
        except OSError:
            pass
    return tps


def read_by(rel, tps):
    t = rel.split("/Textures/", 1)[1][:-4]
    return t in tps or VARIANT.sub("", t) in tps or os.path.dirname(t) in tps


def queued_stems(state):
    """Stems of this item's waiting (pending/active) jobs. Another item's job, or a failed one, excuses nothing."""
    mine = set()
    for d in ("pending", "active"):
        for f in glob.glob(os.path.join(state, d, "*.json")):
            if f.endswith(".manifest.json"):
                continue
            try:
                j = json.load(open(f))
            except (OSError, json.JSONDecodeError):
                continue
            tp = j.get("target_texpath")
            if not tp:
                continue
            if j.get("rimflow_item_id") == "ICON_OUTLINE_REPAINT_1":
                mine.add(os.path.basename(tp).lower())
    return mine


def artpipe_state():
    """The artpipe state dir (state_dir.py's resolution), or None: QUEUED is then unmeasured and nothing is QUEUED."""
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "artpipe"))
        import state_dir
        p = state_dir.resolve()
        return str(p) if p.is_dir() else None
    except Exception:
        return None


def census(root=".", state=None):
    import artledger as L
    dec, rows = load_sheet(root)
    keys = sorted(rows, key=len, reverse=True)
    nooutline = {}                                     # sha -> row, every *_nooutline render shown on the sheet
    for k, r in rows.items():
        for col, lab in r.get("labels", {}).items():
            if "_nooutline" in (lab or ""):
                for sha in r["columns"].get(col, {}).values():
                    nooutline[sha] = k
    idx = L.Index()
    tps = xml_texpaths(root)
    queued = queued_stems(state) if state else set()
    out = []
    for p in sorted(glob.glob(os.path.join(root, "src/**/Textures/Things/**/*.png"), recursive=True)):
        rel = os.path.relpath(p, root)
        if not any(x in rel for x in SCOPE):
            continue
        try:
            m = measure(p)
        except OSError:
            continue
        if m is None:
            continue
        edge, inner = m
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        row = row_for(rel, keys)
        rec = {"path": rel, "edge": round(edge, 3), "interior": round(inner, 3), "sha": sha[:12], "row": row}
        if sha in nooutline:
            ok = edge < REPAINT_MAX or edge - inner <= DARK_GAP
            rec["repaint"] = "ok" if ok else "BAD"
        if edge >= OUTLINED:
            rd = dec.get(row, {}) if row else {}
            picked = rd.get("decision")
            pcol = rows.get(row, {}).get("columns", {}).get(picked, {}) if row else {}
            if idx.protected(sha):
                c = "KEPT"
            elif sha in pcol.values():
                c = "PICKED"
            elif picked == "hold" or "not_needed" in (rd.get("assign") or {}).values():
                c = "HELD"
            elif os.path.basename(rel).startswith("RUT_") and row and row.startswith("RM_") and picked \
                    and (rows[row]["labels"].get(picked) or "").startswith("IN GAME"):
                c = "TWIN"
            elif stem(rel).endswith("_m") or os.path.basename(rel)[:-4].endswith("_m"):
                c = "MASK"
            elif edge - inner <= DARK_GAP:
                c = "DARK"
            elif not read_by(rel, tps):
                c = "ORPHAN"
            elif stem(rel).lower() in queued or os.path.basename(rel)[:-4].lower() in queued:
                c = "QUEUED"
            else:
                c = "OPEN"
            rec["class"] = c
        out.append(rec)
    return out


def selftest():
    def img(rim, fill):
        a = np.zeros((32, 32, 4))
        a[4:28, 4:28] = (*fill, 255)
        if rim is not None:
            a[4:28, 4] = a[4:28, 27] = a[4, 4:28] = a[27, 4:28] = (*rim, 255)
        return a
    e, i = shares(img((0, 0, 0), (200, 150, 90)))
    assert e == 1.0 and i == 0.0, (e, i)               # drawn rim on a light subject: outlined, not dark material
    e, i = shares(img(None, (200, 150, 90)))
    assert e == 0.0, e                                 # painted edge
    e, i = shares(img(None, (20, 20, 20)))
    assert e == 1.0 and i == 1.0 and e - i <= DARK_GAP  # black material: edge as dark as the interior
    assert shares(np.zeros((8, 8, 4))) is None
    assert stem("x/RM_Foo_a.png") == "RM_Foo" and stem("x/Kit_east.png") == "Kit"
    keys = ["RM_DossCatch", "Pyrinth"]
    assert row_for("src/U/Textures/Things/Item/Fish/RUT_Doss.png", keys) == "RM_DossCatch"
    assert read_by("src/T/Textures/Things/Item/Resource/Pyrinth/Pyrinth_b.png", {"Things/Item/Resource/Pyrinth"})
    assert not read_by("src/T/Textures/Things/Item/Resource/RM_Saal/RM_Saal_a.png", {"Things/Item/Fish/RM_Saal"})
    assert row_for("src/P/Textures/Things/Item/Resource/Pyrinth/Pyrinth_b.png", keys) == "Pyrinth"
    import tempfile
    with tempfile.TemporaryDirectory() as t:           # only THIS item's pending/active jobs excuse an icon
        for d, name, item in (("pending", "Mine", "ICON_OUTLINE_REPAINT_1"), ("active", "Act", "ICON_OUTLINE_REPAINT_1"),
                              ("failed", "Dead", "ICON_OUTLINE_REPAINT_1"), ("pending", "Other", "SOME_OTHER_ITEM"),
                              ("failed", "OtherDead", "SOME_OTHER_ITEM")):
            os.makedirs(os.path.join(t, d), exist_ok=True)
            json.dump({"target_texpath": "Things/Item/" + name, "rimflow_item_id": item},
                      open(os.path.join(t, d, name + ".json"), "w"))
        assert queued_stems(t) == {"mine", "act"}, queued_stems(t)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--state", help="artpipe state dir (default: artpipe_state.py's resolution)")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    try:
        recs = census(state=a.state or artpipe_state())
    except (OSError, KeyError, json.JSONDecodeError) as e:
        print(f"UNMEASURED: cannot read an input ({e})")
        return 2
    if a.out:
        json.dump(recs, open(a.out, "w"), indent=1)
    cls = Counter(r["class"] for r in recs if "class" in r)
    rep = Counter(r["repaint"] for r in recs if "repaint" in r)
    print(f"{len(recs)} icons measured; outlined (edge >= {OUTLINED}): {sum(cls.values())} "
          f"{dict(sorted(cls.items()))}; installed no-outline repaints: {dict(rep)}")
    bad = [r for r in recs if r.get("class") in ("OPEN", "QUEUED") or r.get("repaint") == "BAD"]
    for r in bad:
        print(f"  {r['class'] if r.get('class') in ('OPEN', 'QUEUED') else 'BAD'}  edge {r['edge']:.2f} "
              f"interior {r['interior']:.2f}  {r['path']}")
    if a.check:
        print("PASS" if not bad else f"FAIL: {len(bad)} open or bad")
        return 0 if not bad else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
