#!/usr/bin/env python3
"""art_override_family.py -- the *ArtOverride family north-star script, STATIC layer.

ART_OVERRIDE_FAMILY_SCRIPT_1 / design/RimMandrake/debug_process.md "The *ArtOverride family".
One parametrized script for every `src/*/*ArtOverride/About/About.xml` mod; the member list is
the glob at run time, never a hand list, so a new override is covered without an edit.

An ArtOverride mod ships NO defs and NO patches: loose PNGs at the donor's own texPath, and the
later-loading loose texture wins (texture binds by texPath, not defName). So per member, per
texture group `<rel>/<base>` this checks, offline:

  binds          some def in the def dump (PawnKindDef life stages, ThingDef graphicData) has
                 texPath == the group's path (case-insensitive, as Unity's resource lookup is).
                 No def binds it -> the art is dead weight (UNBOUND).
  facings        for a Graphic_Multi binding: _north, _south, _east all present (west mirrors
                 east). The colour mask `<base>m_<facing>` / `<base>_<facing>m` is NOT a facing
                 and never counts as one (CLAUDE.md: a `*south*` glob reads the mask as often as
                 the art). For Graphic_Single: `<base>.png` present.
  alpha          each facing PNG is RGBA and has visible pixels (alpha > 16) -- an all-clear or
                 alpha-less PNG renders as nothing or as a box.

What this CANNOT see (the live layer, still owed -- needs bridge): that the game actually
resolved our file over the donor's AssetBundle copy, and that Player.log has no
missing-texture/magenta line for the path. Those are bars 4-5 of the item; see the plan at the
bottom of this docstring.

    python3 src/RimMandrake/Utils/art_override_family.py            table + JSON to Transient/northstar/
    python3 src/RimMandrake/Utils/art_override_family.py --selftest proves every check can go red

Live layer plan (not built): spawn each member's bound PawnKindDef on a bland map via
jawa/spawn_batch, read Player.log delta for "Could not load" / "missing texture" naming the
texPath, and screenshot_cell_rect one frame per member; record under family key
`ArtOverrideFamily`.
"""
import argparse
import glob
import json
import os
import re
import sys
import time
from collections import defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FACINGS_MULTI = ("north", "south", "east")
ALPHA_VISIBLE = 16
_FACING_RE = re.compile(r"^(?P<base>.+?)_(?P<facing>north|south|east|west)(?P<mask>m?)$", re.I)


def members(repo=REPO):
    """Every *ArtOverride mod folder that is a real mod (has About/About.xml)."""
    return sorted(os.path.dirname(os.path.dirname(p))
                  for p in glob.glob(os.path.join(repo, "src", "*", "*ArtOverride", "About", "About.xml")))


def texture_groups(mod_dir):
    """{group_path_lower: {"path": rel/base, "facings": {facing: file}, "single": file|None, "masks": [..]}}"""
    root = os.path.join(mod_dir, "Textures")
    groups = {}
    for f in glob.glob(os.path.join(root, "**", "*.png"), recursive=True):
        rel = os.path.relpath(f, root).replace(os.sep, "/")[:-4]
        d, stem = os.path.split(rel)
        m = _FACING_RE.match(stem)
        if m:
            base = m.group("base")
            mask = bool(m.group("mask"))
            if not mask and base.endswith("m") and glob.glob(
                    os.path.join(glob.escape(os.path.join(root, d)), glob.escape(base[:-1]) + "_*.png")):
                mask = True                      # <base>m_<facing> form
                base = base[:-1]
            key = (d + "/" + base).lstrip("/")
            g = groups.setdefault(key.lower(), {"path": key, "facings": {}, "single": None, "masks": []})
            (g["masks"].append(f) if mask else g["facings"].__setitem__(m.group("facing").lower(), f))
        else:
            key = rel
            g = groups.setdefault(key.lower(), {"path": key, "facings": {}, "single": None, "masks": []})
            g["single"] = f
    return groups


def _walk_texpaths(node, out, owner, graphic_class=None):
    if isinstance(node, dict):
        gc = node.get("graphicClass", graphic_class)
        tp = node.get("texPath")
        if isinstance(tp, str) and tp:
            out[tp.lower()].append((owner, gc or ""))
        for v in node.values():
            if isinstance(v, (dict, list)):
                _walk_texpaths(v, out, owner, gc)
    elif isinstance(node, list):
        for v in node:
            _walk_texpaths(v, out, owner, graphic_class)


def texpath_index(dump_dir, def_types=("PawnKindDef", "ThingDef")):
    """{texPath_lower: [(\"Type/defName\", graphicClass)]} from the def dump; plus per-type counts."""
    idx = defaultdict(list)
    counts = {}
    for t in def_types:
        p = os.path.join(dump_dir, "defs", t + ".json")
        if not os.path.exists(p):
            counts[t] = None                     # UNMEASURED, not zero
            continue
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        rows = data.get("defs") or []
        counts[t] = len(rows)
        for d in rows:
            _walk_texpaths(d.get("fields") or {}, idx, "%s/%s" % (t, d.get("defName")))
    return idx, counts


def _alpha_ok(path):
    try:
        from PIL import Image
    except ImportError:
        return None, "UNMEASURED: Pillow missing"
    im = Image.open(path)
    if im.mode != "RGBA":
        return False, "mode %s, no alpha channel" % im.mode
    hi = im.getchannel("A").point(lambda a: 255 if a > ALPHA_VISIBLE else 0).getbbox()
    return (hi is not None), ("" if hi else "no visible pixels (alpha <= %d everywhere)" % ALPHA_VISIBLE)


def check_member(mod_dir, idx):
    rows = []
    for key, g in sorted(texture_groups(mod_dir).items()):
        binds = idx.get(key, [])
        row = {"group": g["path"], "binds": sorted({b for b, _ in binds})[:6], "findings": []}
        if not binds:
            leaf = key.rsplit("/", 1)[-1]
            moved = sorted({tp for tp in idx if tp.rsplit("/", 1)[-1] == leaf})[:3]
            row["findings"].append("UNBOUND: no PawnKindDef/ThingDef in the dump has texPath %s%s" % (
                g["path"], (" (a def now points at %s -- repointed, so this art is dead)" % moved) if moved
                else " (donor def absent from the dump: mod not in the captured set, or cut)"))
        classes = {gc.rsplit(".", 1)[-1] for _, gc in binds}
        multi = (not classes) or any(c.startswith("Graphic_Multi") or c == "" for c in classes) or bool(g["facings"])
        if multi and not g["single"]:
            missing = [f for f in FACINGS_MULTI if f not in g["facings"]]
            if missing:
                row["findings"].append("MISSING FACING: %s" % ",".join(missing))
            files = [g["facings"][f] for f in FACINGS_MULTI if f in g["facings"]]
        else:
            files = [g["single"]] if g["single"] else []
            if not files:
                row["findings"].append("MISSING: %s.png" % g["path"])
        for f in files:
            ok, why = _alpha_ok(f)
            if ok is False:
                row["findings"].append("ALPHA %s: %s" % (os.path.basename(f), why))
            elif ok is None:
                row["findings"].append(why)
        rows.append(row)
    if not rows:
        rows.append({"group": "(none)", "binds": [], "findings": ["NO TEXTURES: mod ships no PNG"]})
    return rows


def run(dump_dir, repo=REPO):
    idx, counts = texpath_index(dump_dir)
    out = {"dump": dump_dir, "defCounts": counts, "members": {}}
    for m in members(repo):
        out["members"][os.path.basename(m)] = check_member(m, idx)
    return out


def _default_dump():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import refresh  # noqa: E402  (D_DUMP is the current capture)
    return refresh.D_DUMP


def selftest():
    """Each check must be able to go red, and the sanity probe must go green."""
    import tempfile
    from PIL import Image
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "defs"))
        json.dump({"defs": [
            {"defName": "Fake", "fields": {"lifeStages": [{"bodyGraphicData": {
                "texPath": "fx/Fake/Fake", "graphicClass": "Verse.Graphic_Multi"}}]}},
        ]}, open(os.path.join(td, "defs", "PawnKindDef.json"), "w"))
        repo = os.path.join(td, "repo")

        def mk(mod, files):
            for rel, mode, visible in files:
                p = os.path.join(repo, "src", "RimX", mod, "Textures", rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                im = Image.new(mode, (8, 8), (0, 0, 0, 255 if visible else 0) if mode == "RGBA" else (0, 0, 0))
                im.save(p)
            os.makedirs(os.path.join(repo, "src", "RimX", mod, "About"), exist_ok=True)
            open(os.path.join(repo, "src", "RimX", mod, "About", "About.xml"), "w").write("<ModMetaData/>")

        good = [("fx/Fake/Fake_%s.png" % f, "RGBA", True) for f in FACINGS_MULTI]
        mk("GoodArtOverride", good + [("fx/Fake/Fake_southm.png", "RGBA", True)])
        mk("NoNorthArtOverride", [g for g in good if "north" not in g[0]])
        mk("MaskOnlyNorthArtOverride", [g for g in good if "north" not in g[0]] + [("fx/Fake/Fakem_north.png", "RGBA", True)])
        mk("UnboundArtOverride", [("fx/Other/Other_%s.png" % f, "RGBA", True) for f in FACINGS_MULTI])
        mk("ClearArtOverride", good[:2] + [("fx/Fake/Fake_east.png", "RGBA", False)])
        mk("RgbArtOverride", good[:2] + [("fx/Fake/Fake_east.png", "RGB", True)])
        res = run(td, repo)["members"]
        want = {
            "GoodArtOverride": None,
            "NoNorthArtOverride": "MISSING FACING: north",
            "MaskOnlyNorthArtOverride": "MISSING FACING: north",
            "UnboundArtOverride": "UNBOUND",
            "ClearArtOverride": "no visible pixels",
            "RgbArtOverride": "no alpha channel",
        }
        for mod, frag in want.items():
            got = [f for r in res.get(mod, []) for f in r["findings"]]
            ok = (not got) if frag is None else any(frag in f for f in got)
            print("%-4s %-26s %s" % ("PASS" if ok else "FAIL", mod, got or "clean"))
            fails += 0 if ok else 1
    print("%d/%d selftest cases passed" % (len(want) - fails, len(want)))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dump", help="def dump capture dir (default: refresh.D_DUMP)")
    ap.add_argument("--out", default=None, help="JSON path (default Transient/northstar/ArtOverrideFamily_<ts>.json)")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    dump = a.dump or _default_dump()
    res = run(dump)
    if any(v is None for v in res["defCounts"].values()):
        print("UNMEASURED: dump lacks %s" % [k for k, v in res["defCounts"].items() if v is None])
    bad = 0
    for mod, rows in res["members"].items():
        f = [x for r in rows for x in r["findings"]]
        bad += bool(f)
        print("%-4s %-40s %d group(s)%s" % ("RED" if f else "ok", mod, len(rows), ("  " + "; ".join(f)) if f else ""))
    print("%d members, %d red, defs indexed %s" % (len(res["members"]), bad, res["defCounts"]))
    out = a.out or os.path.join(REPO, "Transient", "northstar",
                                "ArtOverrideFamily_static_%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
