#!/usr/bin/env python3
"""modaudit/diskfacts.py - static, on-disk facts per mod (About.xml + folder walk + assembly flags). Resumable.

    python3 src/RimMandrake/Utils/modaudit/diskfacts.py --budget 240     # process mods until 240 s spent; re-run to resume
    python3 src/RimMandrake/Utils/modaudit/diskfacts.py --status         # how many cached / remaining
    python3 src/RimMandrake/Utils/modaudit/diskfacts.py --redo <pid>     # drop one mod's cache entry

Per mod, cached as one JSON file under ~/.cache/rm_modaudit/disk/<packageId>.json (derived; outside git):
  about      every About.xml field the audit uses, parsed (never grepped): name, author(s), url, supportedVersions,
             description, modVersion, modDependencies (+ByVersion), loadBefore/After (+force), incompatibleWith
  workshop   PublishedFileId.txt or the workshop folder name
  disk       total bytes/files and a split by kind (textures, sounds, assemblies, xml, assetbundles, source, other)
  textures   png/dds pixel census from headers: count and decoded-RGBA MB estimate (an INFERRED VRAM/RAM proxy,
             w*h*4*1.33 for mips; RimWorld compresses some textures so this is an upper-ish estimate, not a measurement)
  dlls       every .dll: relative path, bytes, and FLAGS from a byte search of the file (string presence in the
             assembly's metadata/string heaps; a FLAG, never a count): HarmonyLib, settings screen
             (DoSettingsWindowContents), MapComponentTick, GameComponentTick, WorldComponentTick, CompTick,
             CompTickRare, Prepatcher
  source     ships C# source (.cs/.csproj/.sln), .git, .github, README files, and the folder's Source/ dir
  layout     files under Defs/ Patches/ Languages/ (any version folder); defs_dirs = {"<path>/Defs": xml files}
  textures   decoded_mb_est counts ONLY images under a Textures/ segment and under no source-like segment
             (Source, src, .vs, obj, bin, packages, About) - RimWorld loads textures only from <contentDir>/Textures;
             decoded_mb_est_all_images keeps every png/dds for comparison
  dlls       + "types": top-level type names from the .NET metadata TypeDef table (dotnetmeta.py), for class_ref edges

SCHEMA bumps whenever a record's shape changes; a cached record with another schema is re-collected.
"""
import argparse
import json
import os
import re
import struct
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import dotnetmeta  # noqa: E402

CACHE = os.path.expanduser("~/.cache/rm_modaudit/disk")
SCHEMA = 2
SOURCE_SEGS = {"source", "src", ".vs", "obj", "bin", "packages", "about"}
KIND = {}
for e in (".png", ".dds", ".jpg", ".jpeg", ".psd", ".tga", ".bmp"):
    KIND[e] = "textures"
for e in (".ogg", ".wav", ".mp3", ".flac"):
    KIND[e] = "sounds"
KIND[".dll"] = "assemblies"
KIND[".pdb"] = "assemblies"
KIND[".xml"] = "xml"
for e in (".cs", ".csproj", ".sln", ".props", ".targets"):
    KIND[e] = "source"
DLL_FLAGS = {
    "harmony": b"HarmonyLib",
    "settings_screen": b"DoSettingsWindowContents",
    "map_component_tick": b"MapComponentTick",
    "game_component_tick": b"GameComponentTick",
    "world_component_tick": b"WorldComponentTick",
    "comp_tick": b"CompTick",
    "comp_tick_rare": b"CompTickRare",
    "prepatcher": b"Prepatcher",
}
BYVERSION_FIELDS = ("loadAfterByVersion", "loadBeforeByVersion", "forceLoadAfterByVersion", "forceLoadBeforeByVersion")
LIST_FIELDS = ("loadBefore", "loadAfter", "forceLoadBefore", "forceLoadAfter", "incompatibleWith", "supportedVersions",
               "authors")


def _lis(node):
    return [(li.text or "").strip() for li in node.findall("li") if (li.text or "").strip()] if node is not None else []


def parse_about(path):
    """About.xml -> dict. Pure over a path; selftested. Direct children of <ModMetaData> only."""
    root = ET.parse(path).getroot()

    def t(tag):
        n = root.find(tag)
        return (n.text or "").strip() if n is not None and n.text else None
    out = {k: t(k) for k in ("packageId", "name", "author", "url", "description", "modVersion", "shortName")}
    for f in LIST_FIELDS:
        out[f] = _lis(root.find(f))
    deps = []
    for li in (root.find("modDependencies").findall("li") if root.find("modDependencies") is not None else []):
        d = {k: ((li.find(k).text or "").strip() if li.find(k) is not None and li.find(k).text else None)
             for k in ("packageId", "displayName", "steamWorkshopUrl", "downloadUrl")}
        deps.append(d)
    out["modDependencies"] = deps
    byv = {}
    mdbv = root.find("modDependenciesByVersion")
    if mdbv is not None:
        for v in mdbv:
            byv[v.tag] = [((li.find("packageId").text or "").strip().lower() if li.find("packageId") is not None
                           and li.find("packageId").text else None) for li in v.findall("li")]
    out["modDependenciesByVersion"] = byv
    for f in BYVERSION_FIELDS:
        node = root.find(f)
        out[f] = {v.tag: [x.lower() for x in _lis(v)] for v in node} if node is not None else {}
    out["supports_1_6"] = "1.6" in out["supportedVersions"]
    return out


def image_dims(path):
    """(w, h) from a PNG IHDR or DDS header, else None. Reads <= 32 bytes."""
    try:
        with open(path, "rb") as fh:
            b = fh.read(32)
    except OSError:
        return None
    if b[:8] == b"\x89PNG\r\n\x1a\n" and len(b) >= 24:
        return struct.unpack(">II", b[16:24])
    if b[:4] == b"DDS " and len(b) >= 20:
        h, w = struct.unpack("<II", b[12:20])
        return (w, h)
    return None


def texture_is_loaded(rel_dir):
    """True when an image in this folder (relative to the mod root) is one RimWorld loads as a texture: some path
    segment is Textures and none is source-like. Pure; selftested."""
    segs = [x.lower() for x in rel_dir.replace("\\", "/").split("/") if x and x != "."]
    return "textures" in segs and not (set(segs) & SOURCE_SEGS)


def defs_dir_key(rel_dir):
    """'1.6/Mods/X/Defs/Things' -> '1.6/Mods/X/Defs' (the folder up to the first Defs segment), else None."""
    segs = [x for x in rel_dir.replace("\\", "/").split("/") if x and x != "."]
    return "/".join(segs[:segs.index("Defs") + 1]) if "Defs" in segs else None


def walk_mod(folder):
    disk = {"bytes": 0, "files": 0, "by_kind": {}}
    tex = {"images": 0, "images_loaded": 0, "decoded_mb_est": 0.0, "decoded_mb_est_all_images": 0.0,
           "unreadable_headers": 0, "largest": [], "largest_not_loaded": []}
    dlls, source, layout = [], {"cs": 0, "csproj": 0, "sln": 0, "git": False, "github": False, "readme": [],
                                "source_dir": False}, {"Defs": 0, "Patches": 0, "Languages": 0, "defs_dirs": {}}
    big, big_out = [], []
    for dp, dns, fns in os.walk(folder):
        rel = os.path.relpath(dp, folder)
        parts = set(rel.replace("\\", "/").split("/"))
        tex_loaded = texture_is_loaded(rel)
        dkey = defs_dir_key(rel)
        if ".git" in dns:
            source["git"] = True
            dns.remove(".git")
        if ".github" in dns:
            source["github"] = True
        if rel == "." and any(d.lower() == "source" for d in dns):
            source["source_dir"] = True
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            ext = os.path.splitext(fn)[1].lower()
            kind = KIND.get(ext)
            if kind is None:
                kind = "assetbundles" if "AssetBundles" in parts or ext == "" and "Assets" in parts else "other"
            disk["bytes"] += sz
            disk["files"] += 1
            k = disk["by_kind"].setdefault(kind, [0, 0])
            k[0] += 1
            k[1] += sz
            for seg in ("Defs", "Patches", "Languages"):
                if seg in parts and ext == ".xml":
                    layout[seg] += 1
            if dkey and ext == ".xml":
                layout["defs_dirs"][dkey] = layout["defs_dirs"].get(dkey, 0) + 1
            if ext in (".png", ".dds"):
                tex["images"] += 1
                d = image_dims(p)
                if d is None:
                    tex["unreadable_headers"] += 1
                else:
                    mb = d[0] * d[1] * 4 * 1.33 / 1048576.0
                    tex["decoded_mb_est_all_images"] += mb
                    row = (round(mb, 1), os.path.relpath(p, folder), d[0], d[1])
                    if tex_loaded:
                        tex["images_loaded"] += 1
                        tex["decoded_mb_est"] += mb
                        big.append(row)
                    else:
                        big_out.append(row)
            elif ext == ".dll":
                try:
                    with open(p, "rb") as fh:
                        blob = fh.read()
                except OSError:
                    blob = b""
                dlls.append({"path": os.path.relpath(p, folder), "bytes": sz,
                             "flags": sorted(f for f, needle in DLL_FLAGS.items() if needle in blob),
                             "types": dotnetmeta.type_names(blob)})
            elif ext == ".cs":
                source["cs"] += 1
            elif ext == ".csproj":
                source["csproj"] += 1
            elif ext == ".sln":
                source["sln"] += 1
            if fn.lower().startswith("readme") and len(source["readme"]) < 5:
                source["readme"].append(os.path.relpath(p, folder))
    big.sort(reverse=True)
    big_out.sort(reverse=True)
    tex["largest"] = big[:5]
    tex["largest_not_loaded"] = big_out[:5]
    tex["decoded_mb_est"] = round(tex["decoded_mb_est"], 1)
    tex["decoded_mb_est_all_images"] = round(tex["decoded_mb_est_all_images"], 1)
    return disk, tex, dlls, source, layout


def collect_one(row):
    folder = row.get("folder")
    rec = {"packageId": row["packageId"], "schema": SCHEMA, "folder": folder, "collected": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if not folder or not os.path.isdir(folder):
        rec["error"] = "UNRESOLVED (no folder)"
        return rec
    about = os.path.join(folder, "About", "About.xml")
    try:
        rec["about"] = parse_about(about)
    except (OSError, ET.ParseError) as e:
        rec["about_error"] = str(e)
    pf = os.path.join(folder, "About", "PublishedFileId.txt")
    wid = None
    if os.path.isfile(pf):
        wid = open(pf, errors="replace").read().strip() or None
    if not wid and row.get("resolution") == "workshop":
        wid = os.path.basename(folder.rstrip("/"))
    rec["workshop_id"] = wid if wid and re.fullmatch(r"\d{6,12}", wid) else None
    t0 = time.time()
    rec["disk"], rec["textures"], rec["dlls"], rec["source"], rec["layout"] = walk_mod(folder)
    rec["walk_seconds"] = round(time.time() - t0, 1)
    return rec


def _cache_path(pid):
    return os.path.join(CACHE, re.sub(r"[^A-Za-z0-9._-]", "_", pid) + ".json")


def _current(p):
    """True when a cache file exists and carries this SCHEMA."""
    if not os.path.isfile(p):
        return False
    try:
        return json.load(open(p)).get("schema") == SCHEMA
    except (OSError, ValueError):
        return False


def load_all(rows, any_schema=False):
    """{packageId: record} for every cached record of the CURRENT schema (stale ones are absent -> missing)."""
    out = {}
    for r in rows:
        p = _cache_path(r["packageId"])
        if os.path.isfile(p):
            rec = json.load(open(p))
            if any_schema or rec.get("schema") == SCHEMA:
                out[r["packageId"]] = rec
    return out


def main(argv=None):
    from universe import UNIVERSE_JSON
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=240.0)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--redo", default=None)
    a = ap.parse_args(argv)
    rows = json.load(open(UNIVERSE_JSON))["rows"]
    os.makedirs(CACHE, exist_ok=True)
    if a.redo:
        p = _cache_path(a.redo.lower())
        if os.path.exists(p):
            os.remove(p)
    todo = [r for r in rows if not _current(_cache_path(r["packageId"]))]
    if a.status:
        print("diskfacts: %d cached, %d remaining of %d" % (len(rows) - len(todo), len(todo), len(rows)))
        return
    t0, n = time.time(), 0
    for r in todo:
        if time.time() - t0 > a.budget:
            break
        rec = collect_one(r)
        with open(_cache_path(r["packageId"]), "w") as fh:
            json.dump(rec, fh)
        n += 1
        if n % 25 == 0:
            print("  diskfacts: %d done this run (%.0fs), last %s" % (n, time.time() - t0, r["packageId"]), flush=True)
    left = len(todo) - n
    print("diskfacts: collected %d this run in %.0fs; %d remaining%s"
          % (n, time.time() - t0, left, " - re-run to resume" if left else " - DONE"))


if __name__ == "__main__":
    main()
