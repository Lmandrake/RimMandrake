#!/usr/bin/env python3
"""modaudit/defscan.py - offline def + patch census per mod, for the mod audit (stage 0).

    python3 src/RimMandrake/Utils/modaudit/defscan.py        # ~minutes over /mnt/c; writes the cache below

Builds def_inventory's DefSet (load folders resolved by rimworld_loadset, version folders + LoadFolders.xml honoured,
<ParentName> resolved) over a SYNTHETIC ModsConfig holding the whole audit universe (FULL.LATEST + our absent mods,
from facts/universe.json), then for every mod:
  * def counts by type (non-abstract nodes it declares; abstract count separately),
  * its Patches/: operation count (root-level <Operation> elements + nested op nodes), the def types and defNames
    its xpaths name, PatchOperationFindMod <mods> names, MayRequire ids,
  * cross-reference: which mods DECLARE the defNames it patches (edges mod -> owner).

Caveats carried into every record: base XML only, PatchOperations NOT run, MayRequire NOT evaluated, so a def
count is "declared in its own XML", not "present in the running game". An xpath that names no defName (e.g. a
//li or @Name selector) contributes to op_count but to no edge: edges are a LOWER bound.

Cache (derived, regenerable, outside git): ~/.cache/rm_modaudit/defscan.json
"""
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
sys.path.insert(0, UTILS)
sys.path.insert(0, HERE)

CACHE_DIR = os.path.expanduser("~/.cache/rm_modaudit")
CACHE = os.path.join(CACHE_DIR, "defscan.json")

XP_DEFTYPE = re.compile(r"Defs/([A-Za-z_][\w.]*)")
XP_DEFNAME = re.compile(r"defName\s*=\s*[\"']([^\"']+)[\"']")
XP_DEFNAME_TEXT = re.compile(r"defName\s*\[\s*text\(\)\s*=\s*[\"']([^\"']+)[\"']\s*\]")


def xpath_targets(xp):
    """(def types, defNames) an xpath names. Pure; selftested. Ignores Name/@Name selectors (abstract parents)."""
    xp = xp or ""
    types = [t for t in XP_DEFTYPE.findall(xp) if t != "li"]
    names = XP_DEFNAME.findall(xp) + XP_DEFNAME_TEXT.findall(xp)
    return sorted(set(types)), sorted(set(names))


def _is_op(el):
    if el.tag == "Operation":
        return True
    c = el.get("Class") or ""
    # nested ops live in <li Class=..> (sequences) AND in <match>/<nomatch> (FindMod, Conditional)
    return bool(c) and ("PatchOperation" in c or "Operation" in c)


def patch_file_census(root):
    """Census one parsed Patch XML root -> dict. Pure; selftested."""
    out = {"ops_root": 0, "ops_all": 0, "classes": Counter(), "def_types": Counter(), "def_names": Counter(),
           "findmod_names": Counter(), "mayrequire": Counter(), "xpaths": 0}
    if root is None:
        return out
    for child in list(root):
        if child.tag == "Operation":
            out["ops_root"] += 1
    for el in root.iter():
        if _is_op(el):
            out["ops_all"] += 1
            out["classes"][el.get("Class") or "?"] += 1
            mr = el.get("MayRequire") or el.get("MayRequireAnyOf")
            if mr:
                for m in re.split(r"[,\s]+", mr.strip()):
                    if m:
                        out["mayrequire"][m.lower()] += 1
            if "FindMod" in (el.get("Class") or ""):
                mods = el.find("mods")
                if mods is not None:
                    for li in mods.findall("li"):
                        if (li.text or "").strip():
                            out["findmod_names"][li.text.strip()] += 1
        if el.tag == "xpath" and (el.text or "").strip():
            out["xpaths"] += 1
            t, n = xpath_targets(el.text)
            for x in t:
                out["def_types"][x] += 1
            for x in n:
                out["def_names"][x] += 1
    return out


def _merge(acc, one):
    for k, v in one.items():
        if isinstance(v, Counter):
            acc.setdefault(k, Counter()).update(v)
        else:
            acc[k] = acc.get(k, 0) + v


def _patch_dirs(mod):
    out = []
    for base in mod.get("contentDirs") or [mod["folder"]]:
        p = os.path.join(base, "Patches")
        if os.path.isdir(p) and p not in out:
            out.append(p)
    return out


def write_config(universe, path):
    """A ModsConfig.xml holding the universe in order (version copied from FULL.LATEST)."""
    full = ET.parse(universe["_full_path"]).getroot()
    ver = full.find("version")
    root = ET.Element("ModsConfigData")
    v = ET.SubElement(root, "version")
    v.text = ver.text if ver is not None else "1.6"
    am = ET.SubElement(root, "activeMods")
    for r in universe["rows"]:
        li = ET.SubElement(am, "li")
        li.text = r["packageId"]
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def run():
    import def_inventory
    from game_paths import LOCAL_MODS, WORKSHOP, GAME_DATA
    from universe import UNIVERSE_JSON, ROOT
    u = json.load(open(UNIVERSE_JSON))
    u["_full_path"] = os.path.join(ROOT, u["full_latest"])
    os.makedirs(CACHE_DIR, exist_ok=True)
    cfg = os.path.join(CACHE_DIR, "ModsConfig.UNIVERSE.xml")
    write_config(u, cfg)
    t0 = time.time()
    ds = def_inventory.build(config=cfg, workshop=WORKSHOP, local=LOCAL_MODS, data=GAME_DATA, quiet=False)
    t_build = time.time() - t0
    per = defaultdict(lambda: {"defs_by_type": Counter(), "abstract": 0, "def_names": []})
    owners = defaultdict(set)
    for r in ds.records:
        m = per[r.packageId]
        if r.isAbstract:
            m["abstract"] += 1
            continue
        m["defs_by_type"][r.defType] += 1
        if r.defName:
            owners[r.defName].add(r.packageId)
    patches = {}
    for mod in ds.mods:
        acc = {}
        files = 0
        bad = 0
        for d in _patch_dirs(mod):
            for dp, _, fns in os.walk(d):
                for fn in fns:
                    if not fn.lower().endswith(".xml"):
                        continue
                    files += 1
                    try:
                        root = ET.parse(os.path.join(dp, fn)).getroot()
                    except (ET.ParseError, OSError):
                        bad += 1
                        root = None
                    _merge(acc, patch_file_census(root))
        acc["files"] = files
        acc["unparseable"] = bad
        edges = Counter()
        for dn, n in acc.get("def_names", Counter()).items():
            for o in owners.get(dn, ()):
                if o != mod["packageId"]:
                    edges[o] += n
        acc["targets_owner_mods"] = edges
        unowned = [dn for dn in acc.get("def_names", {}) if dn not in owners]
        acc["def_names_unowned"] = len(unowned)
        patches[mod["packageId"]] = acc
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "instrument": "def_inventory.build over ModsConfig.UNIVERSE.xml + patch_file_census",
        "build_seconds": round(t_build, 1),
        "missing": ds.missing,
        "gameVersion": ds.gameVersion,
        "defNodes": ds.defNodeCount,
        "mods": {m["packageId"]: {"order": m["order"], "contentDirs": m["contentDirs"], "folder": m["folder"]}
                 for m in ds.mods},
        "defs": {k: {"defs_by_type": dict(v["defs_by_type"]), "abstract": v["abstract"]} for k, v in per.items()},
        "owners": {k: sorted(v) for k, v in owners.items()},
        "patches": {k: {kk: (dict(vv) if isinstance(vv, Counter) else vv) for kk, vv in v.items()}
                    for k, v in patches.items()},
    }
    with open(CACHE, "w") as fh:
        json.dump(out, fh)
    nd = sum(sum(v["defs_by_type"].values()) for v in out["defs"].values())
    print("defscan: %d mods, %d def nodes (%d non-abstract counted), missing %s, build %.0fs -> %s"
          % (len(ds.mods), ds.defNodeCount, nd, ds.missing, t_build, CACHE))


if __name__ == "__main__":
    run()
