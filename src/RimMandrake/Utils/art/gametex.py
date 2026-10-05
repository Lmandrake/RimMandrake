#!/usr/bin/env python3
"""gametex.py — which picture does the GAME draw for a texPath, and which def draws which texPath
(ART_SUBJECT_RESOLVER_1 phase 2; design/RimMandrake/art_resolution_rootcause_2026-10-04.md class A2d).

    python3 src/RimMandrake/Utils/art/gametex.py index [--rebuild]       build/refresh the cached indexes, timed
    python3 src/RimMandrake/Utils/art/gametex.py def AA_Thunderox ...     texPaths + the file the game draws
    python3 src/RimMandrake/Utils/art/gametex.py res Things/Pawn/Animal/AA_Thunderox/AA_Thunderox_male

Two read-only indexes, cached OUTSIDE the repo (default /tmp/rm_gametex, env RM_GAMETEX_CACHE) because the trees
are big and live on /mnt/c:

  texture index   every loose PNG under <mod>/<load folder>/Textures/ in BOTH game roots —
                  steamapps/common/RimWorld/Mods/* and steamapps/workshop/content/294100/* — keyed by texPath.
                  Load folders follow LoadFolders.xml (<v1.6>) when present, else root + Common + the newest
                  version folder <= 1.6. Plus the AssetBundle / resources.assets extract cache
                  (observed/inventory/bundle_textures/index.csv) for art that is not loose.
  def texPaths    defName -> body texPaths, from the newest DefDump capture (the LIVE, post-patch, post-inheritance
                  defs): a pawn ThingDef draws its PawnKindDefs' lifeStages[].bodyGraphicData (+female); anything
                  else its own graphicData.

The winner among several mods shipping one texPath is the LAST in load order (ContentFinder walks the running
mods in reverse); the order is ModsConfig.FULL.LATEST.xml when the live list is a swapped-in test list (the same
rule art_sheet.load_order uses), and every answer says which list it was measured against.

A texPath that matches nothing returns the full list of what was searched — never a bare "absent".
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

STEAM = Path(os.environ.get("RM_STEAMAPPS") or "/mnt/c/Program Files (x86)/Steam/steamapps")
ROOTS = {"mods": STEAM / "common" / "RimWorld" / "Mods", "workshop": STEAM / "workshop" / "content" / "294100"}
DATA = STEAM / "common" / "RimWorld" / "Data"
BUNDLES = Path("/mnt/d/Luke/dev/RimMandrake/observed/inventory/bundle_textures")
CACHE = Path(os.environ.get("RM_GAMETEX_CACHE") or "/tmp/rm_gametex")
GAME_VERSION = (1, 6)
FACE_RE = re.compile(r"^(?P<stem>.+?)_(?P<facing>north|east|south|west)(?P<mask>m?)$", re.I)
NONBODY = re.compile(r"dess?icc?ated|_corpse$|skeleton", re.I)


# ───────────────────────────────────────────────────────────── load order ──

def load_order() -> tuple[dict, str]:
    """packageId(lower) -> index, fingerprint. Same rule as art_sheet.load_order (single source there)."""
    import art_sheet
    return art_sheet.load_order()


# ──────────────────────────────────────────────────────────── mod folders ──

def _about(root: Path) -> tuple[str, str]:
    try:
        r = ET.parse(root / "About" / "About.xml").getroot()
        return ((r.findtext("packageId") or "").strip().lower(), (r.findtext("name") or "").strip())
    except (ET.ParseError, OSError):
        return "", ""


def _vkey(name: str):
    m = re.fullmatch(r"v?(\d+)\.(\d+)", name)
    return (int(m.group(1)), int(m.group(2))) if m else None


def load_folders(root: Path, active: set) -> list[Path]:
    """Folders RimWorld loads for this mod, lowest priority first."""
    lf = root / "LoadFolders.xml"
    if lf.is_file():
        try:
            r = ET.parse(lf).getroot()
            vers = sorted(((_vkey(c.tag), c) for c in r if _vkey(c.tag) and _vkey(c.tag) <= GAME_VERSION),
                          key=lambda x: x[0])
            if vers:
                out = []
                for li in vers[-1][1].findall("li"):
                    need = li.get("IfModActive")
                    if need and not any(p.strip().lower() in active for p in need.split(",")):
                        continue
                    nope = li.get("IfModNotActive")
                    if nope and any(p.strip().lower() in active for p in nope.split(",")):
                        continue
                    t = (li.text or "").strip().strip("/")
                    out.append(root / t if t else root)
                return out
        except (ET.ParseError, OSError):
            pass
    out = [root, root / "Common"]
    try:
        vs = sorted((_vkey(p.name), p) for p in root.iterdir() if p.is_dir() and _vkey(p.name)
                    and _vkey(p.name) <= GAME_VERSION)
    except OSError:
        vs = []
    if vs:
        out.append(vs[-1][1])
    return out


# ──────────────────────────────────────────────────────── texture index ──

def _split(rel: str) -> tuple[str, str, bool]:
    base = rel[:-4] if rel.lower().endswith(".png") else rel
    m = FACE_RE.match(base)
    if m:
        return m["stem"], m["facing"].lower(), bool(m["mask"])
    return base, "single", False


def build_index() -> dict:
    t0 = time.time()
    order, fp = load_order()
    active = set(order)
    mods, files = [], {}
    stats = {}
    for rk, rp in ROOTS.items():
        n_mod = n_png = 0
        if not rp.is_dir():
            stats[rk] = f"UNMEASURED: {rp} absent"
            continue
        for root in sorted(p for p in rp.iterdir() if p.is_dir()):
            pid, name = _about(root)
            tex_dirs = [f / "Textures" for f in load_folders(root, active)]
            tex_dirs = [d for d in tex_dirs if d.is_dir()]
            if not tex_dirs:
                continue
            n_mod += 1
            mi = len(mods)
            mods.append({"root": rk, "dir": str(root), "packageId": pid, "name": name,
                         "load_index": order.get(pid, order.get(pid + "_steam", -1)) if rk == "workshop"
                         else order.get(pid, -1)})
            for prio, td in enumerate(tex_dirs):
                r = subprocess.run(["find", str(td), "-type", "f", "-iname", "*.png"], capture_output=True, text=True)
                for line in r.stdout.splitlines():
                    rel = line[len(str(td)) + 1:].replace("\\", "/")
                    stem, facing, mask = _split(rel)
                    if mask:
                        continue
                    n_png += 1
                    files.setdefault(stem.lower(), []).append([mi, prio, facing, line])
        stats[rk] = {"mods_with_textures": n_mod, "pngs": n_png}
    # AssetBundle / resources.assets extracts
    bun = {}
    idx = BUNDLES / "index.csv"
    if idx.is_file():
        for row in csv.DictReader(open(idx, newline="", encoding="utf-8")):
            p = str(BUNDLES / row["file"])
            cont = (row.get("container") or "").replace("\\", "/").lower()
            if cont:
                c = re.sub(r"\.(png|psd|tga|jpg|jpeg)$", "", cont.split("textures/", 1)[-1])
                stem, facing, mask = _split(c)
                if not mask:
                    bun.setdefault(stem, []).append([row["sourceKey"], facing, p, "container"])
            else:
                stem, facing, mask = _split(row["m_Name"].lower())
                if not mask:
                    bun.setdefault("name:" + stem.split("/")[-1], []).append([row["sourceKey"], facing, p, "m_Name"])
        # index.csv is incomplete (mlie.horrors: 0 rows, 117 files extracted) — the extracted tree is the truth
        for pkg in sorted(p for p in BUNDLES.iterdir() if p.is_dir()):
            td = pkg / "textures"
            if not td.is_dir():
                continue
            r = subprocess.run(["find", str(td), "-type", "f", "-iname", "*.png"], capture_output=True, text=True)
            for line in r.stdout.splitlines():
                stem, facing, mask = _split(line[len(str(td)) + 1:].lower())
                if not mask and not any(x[2] == line for x in bun.get(stem, [])):
                    bun.setdefault(stem, []).append([pkg.name, facing, line, "extracted tree"])
        stats["bundles"] = {"rows": sum(len(v) for v in bun.values())}
    else:
        stats["bundles"] = f"UNMEASURED: {idx} absent"
    out = {"built": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "secs": round(time.time() - t0, 1), "load_order": fp,
           "roots": {k: str(v) for k, v in ROOTS.items()}, "bundles_dir": str(BUNDLES), "stats": stats,
           "mods": mods, "files": files, "bundle_files": bun}
    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = CACHE / "texindex.json.tmp"
    tmp.write_text(json.dumps(out))
    os.replace(tmp, CACHE / "texindex.json")
    return out


_IDX = None


def index(rebuild: bool = False) -> dict:
    global _IDX
    if _IDX is not None and not rebuild:
        return _IDX
    p = CACHE / "texindex.json"
    if not rebuild and p.is_file():
        _IDX = json.loads(p.read_text())
        _, fp = load_order()
        if _IDX.get("load_order") == fp:
            return _IDX
        print(f"gametex: load order changed ({_IDX.get('load_order')} -> {fp}); rebuilding", file=sys.stderr)
    _IDX = build_index()
    return _IDX


def searched_text(ix: dict | None = None) -> str:
    ix = ix or index()
    s = ix["stats"]
    parts = []
    for k in ("mods", "workshop"):
        v = s.get(k)
        parts.append(f"{ix['roots'][k]} ({v['mods_with_textures']} mods, {v['pngs']} PNGs)" if isinstance(v, dict) else str(v))
    b = s.get("bundles")
    parts.append(f"AssetBundle + resources.assets extracts ({b['rows']} textures)" if isinstance(b, dict) else str(b))
    return "; ".join(parts) + f"; load order {ix['load_order']}"


def resolve_res(res: str, ix: dict | None = None) -> dict:
    """-> {res, copies: [{mod, packageId, root, load_index, winner, faces: {facing: path}, random_of}],
    bundle: [...], searched}. A Graphic_Random texPath is a FOLDER: its first variant file is shown."""
    ix = ix or index()
    key = res.lower().rstrip("/")
    by_mod = {}
    for mi, prio, facing, path in ix["files"].get(key, []):
        d = by_mod.setdefault(mi, {"faces": {}, "prio": {}})
        if prio >= d["prio"].get(facing, -1):
            d["faces"][facing] = path
            d["prio"][facing] = prio
    random_of = {}
    if not by_mod:                                     # Graphic_Random / Graphic_Collection: a folder
        pre = key + "/"
        for k, lst in ix["files"].items():
            if k.startswith(pre) and "/" not in k[len(pre):]:
                for mi, prio, facing, path in lst:
                    d = by_mod.setdefault(mi, {"faces": {}, "prio": {}, "variants": []})
                    d["variants"].append(path)
        for mi, d in by_mod.items():
            vs = sorted(d["variants"])
            d["faces"] = {"single": vs[0]}
            random_of[mi] = len(vs)
    copies = []
    for mi, d in by_mod.items():
        m = ix["mods"][mi]
        copies.append({"mod": m["name"] or Path(m["dir"]).name, "packageId": m["packageId"], "root": m["root"],
                       "dir": m["dir"], "load_index": m["load_index"], "faces": d["faces"],
                       "random_of": random_of.get(mi)})
    copies.sort(key=lambda c: -c["load_index"])
    if copies and copies[0]["load_index"] >= 0:
        copies[0]["winner"] = True
    bundle = []
    if not copies:
        bf = ix["bundle_files"]
        base = key.split("/")[-1]
        hits = bf.get(key, []) or bf.get("name:" + base, [])
        if not hits:                                   # a Random folder inside a bundle: first variant
            pre = key + "/"
            sub = sorted(k for k in bf if k.startswith(pre) and "/" not in k[len(pre):])
            if not sub:                                # base game: no container, variants named <Base>A / <Base>_a
                sub = sorted(k for k in bf if k.startswith("name:") and re.fullmatch(
                    re.escape("name:" + base) + r"_?[a-z]", k))
            hits = bf[sub[0]] if sub else []
            if sub:
                hits = [[s, "single", p, f"{how}, 1 of {len(sub)} variants"] for s, _f, p, how in hits]
        for src, facing, path, how in hits:
            bundle.append({"source": src, "facing": facing, "path": path, "how": how})
    return {"res": res, "copies": copies, "bundle": bundle, "searched": searched_text(ix)}


# ───────────────────────────────────────────────────────── def texPaths ──

def _dump_dir() -> Path | None:
    from game_paths import DEF_DUMP
    p = Path(DEF_DUMP)
    return p if (p / "defs").is_dir() else None


def _texpaths_of(gd) -> list[str]:
    if not isinstance(gd, dict):
        return []
    t = gd.get("texPath")
    return [t] if isinstance(t, str) and t else []


def build_deftex() -> dict:
    t0 = time.time()
    dd = _dump_dir()
    if dd is None:
        raise SystemExit("gametex: no DefDump capture found — def texPaths UNMEASURED")
    out, kinds = {}, {}
    pk = json.loads((dd / "defs" / "PawnKindDef.json").read_text())
    for d in pk["defs"]:
        f = d.get("fields") or {}
        race = f.get("race")
        tps = []
        for ls in f.get("lifeStages") or []:
            if isinstance(ls, dict):
                tps += _texpaths_of(ls.get("bodyGraphicData")) + _texpaths_of(ls.get("femaleGraphicData"))
        tps = [t for t in dict.fromkeys(tps) if not NONBODY.search(t)]
        if tps:
            kinds[d["defName"]] = {"race": race, "tex": tps}
    td = json.loads((dd / "defs" / "ThingDef.json").read_text())
    for d in td["defs"]:
        f = d.get("fields") or {}
        dn = d["defName"]
        tps = []
        if (d.get("is") or {}).get("pawn"):
            for k, v in kinds.items():
                if v["race"] == dn:
                    tps += v["tex"]
        tps += _texpaths_of(f.get("graphicData"))
        tps = [t for t in dict.fromkeys(tps) if not NONBODY.search(t)]
        if tps:
            out[dn] = {"tex": tps, "mod": d.get("modName"), "packageId": d.get("packageId"), "label": d.get("label")}
    for k, v in kinds.items():
        out.setdefault(k, {"tex": v["tex"], "mod": None, "packageId": None, "label": None, "race": v["race"]})
    res = {"capture": str(dd), "built": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "secs": round(time.time() - t0, 1),
           "defs": out}
    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = CACHE / "deftex.json.tmp"
    tmp.write_text(json.dumps(res))
    os.replace(tmp, CACHE / "deftex.json")
    return res


_DT = None


def deftex(rebuild: bool = False) -> dict:
    global _DT
    if _DT is not None and not rebuild:
        return _DT
    p = CACHE / "deftex.json"
    dd = _dump_dir()
    if not rebuild and p.is_file():
        _DT = json.loads(p.read_text())
        if dd is None or _DT.get("capture") == str(dd):
            return _DT
    _DT = build_deftex()
    return _DT


def def_texpaths(defname: str) -> list[str]:
    return list((deftex()["defs"].get(defname) or {}).get("tex") or [])


def ingest(defnames, dry: bool = False) -> dict:
    """Every game copy of every body texPath the live dump gives DEFNAMES -> art-ledger variant(kind=donor), BOUND
    by texPath (never by name). Our own deployed mods (mandrake.*) are skipped where the ledger already holds that
    texPath as a live repo file — those copies are the repo's, already in the ledger. Idempotent (det ids)."""
    import artledger as L
    import backfill as BF
    idx = L.Index()
    live_res = {L.parse_texfile(rel)["res"] for (_m, rel) in idx.live}
    dt = deftex()
    cap = Path(dt["capture"]).name
    w = L.Writer()
    n0 = len(w.known)
    seen_res, stats = set(), {"defs": 0, "defs_with_tex": 0, "texpaths": 0, "copies": 0, "pngs": 0,
                               "bundle": 0, "unresolved": []}
    for dn in sorted(set(defnames)):
        stats["defs"] += 1
        tps = def_texpaths(dn)
        if tps:
            stats["defs_with_tex"] += 1
        for tp in tps:
            if tp in seen_res:
                continue
            seen_res.add(tp)
            stats["texpaths"] += 1
            r = resolve_res(tp)
            if not r["copies"] and not r["bundle"]:
                stats["unresolved"].append(tp)
            for c in r["copies"]:
                if c["packageId"].startswith("mandrake.") and tp in live_res:
                    continue
                stats["copies"] += 1
                for facing, path in c["faces"].items():
                    if dry:
                        stats["pngs"] += 1
                        continue
                    b = Path(path).read_bytes()
                    sha = L.sha256_bytes(b)
                    L.store_put_bytes(b, sha)
                    rel = tp + ("" if facing == "single" else f"_{facing}") + ".png"
                    BF._variant(w, sha=sha, b=b, kind="donor", loc=f"loose:{path}", rel=rel, idkey=f"gametex|{path}|{tp}",
                                extra={"donor_pkg": c["packageId"], "donor_mod": c["mod"], "how": "loose",
                                       "game_root": c["root"], "random_of": c.get("random_of"),
                                       "bound_by": f"texPath of {dn} in live DefDump capture {cap}"})
                    stats["pngs"] += 1
            for bb in r["bundle"]:
                if dry:
                    stats["bundle"] += 1
                    continue
                p = Path(bb["path"])
                if not p.is_file():
                    continue
                b = p.read_bytes()
                sha = L.sha256_bytes(b)
                L.store_put_bytes(b, sha)
                rel = tp + ("" if bb["facing"] == "single" else f"_{bb['facing']}") + ".png"
                BF._variant(w, sha=sha, b=b, kind="donor", loc=f"bundle:{bb['source']}/{p.name}", rel=rel,
                            idkey=f"gametex|{p}|{tp}",
                            extra={"donor_pkg": bb["source"], "how": "assetbundle-extract", "match": bb["how"],
                                   "bound_by": f"texPath of {dn} in live DefDump capture {cap}"})
                stats["bundle"] += 1
    if not dry:
        w.flush()
        BF._phsave()
    stats["new_events"] = len(w.known) - n0
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("verb", choices=["index", "def", "res", "ingest"])
    ap.add_argument("--census", help="ingest: every defName on every row of this census.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("names", nargs="*")
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args(argv)
    if a.verb == "index":
        ix = index(rebuild=a.rebuild)
        dt = deftex(rebuild=a.rebuild)
        print(f"texture index: {ix['secs']}s when built ({ix['built']}) · {searched_text(ix)}")
        print(f"def texPaths: {len(dt['defs'])} defs from {dt['capture']} ({dt['secs']}s when built)")
        print(f"cache: {CACHE}")
        return 0
    if a.verb == "ingest":
        names = list(a.names)
        if a.census:
            c = json.loads(Path(a.census).read_text())
            names += [d for b in c["biomes"].values() for r in b["rows"] for d in [r["key"]] + list(r.get("defNames") or [])]
        t0 = time.time()
        s = ingest(names, dry=a.dry_run)
        un = s.pop("unresolved")
        print(json.dumps(s), f"{round(time.time() - t0)}s")
        if un:
            print(f"{len(un)} texPath(s) with no copy in any root: " + ", ".join(un[:30]))
        return 0
    for n in a.names:
        tps = def_texpaths(n) if a.verb == "def" else [n]
        if a.verb == "def":
            print(f"{n}: {tps or 'no texPath in the live def dump'}")
        for tp in tps:
            r = resolve_res(tp)
            print(f"  {tp}")
            for c in r["copies"]:
                print(f"    {'IN GAME' if c.get('winner') else 'shadowed' if c['load_index'] >= 0 else 'not loaded'}"
                      f"  [{c['load_index']}] {c['mod']} ({c['packageId']}, {c['root']}) {sorted(c['faces'])}"
                      + (f" random 1 of {c['random_of']}" if c.get("random_of") else ""))
            for b in r["bundle"]:
                print(f"    bundle {b['source']} {b['facing']} ({b['how']})")
            if not r["copies"] and not r["bundle"]:
                print(f"    none — searched {r['searched']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
