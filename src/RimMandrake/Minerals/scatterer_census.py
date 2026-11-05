#!/usr/bin/env python3
"""Census of mineable scatterers outside GenStep_RocksFromGrid (MINERAL_SCATTERERS_AUDIT_OUTSIDE_ROCKS).

The minerals policy zeroes a governed mineable's mineableScatterCommonality; anything else that draws a mineable by that
weight (a GenStep_ScatterLumpsMineable with no forcedDefToScatter, a subclass, or code reading the field) then loses the
def with no per-biome replacement. This scans mod roots for the two places such a scatterer can hide:

  xml  - a def node whose Class names a ScatterLumpsMineable/PreciousLump step, with or without forcedDefToScatter
  dll  - an assembly whose metadata names one of DLL_TOKENS (the field, the lump/precious steps, MineralRich, the
         meteorite maker; string heap bytes)

A hit is a CANDIDATE, classified by hand in design/RimMandrake/mineral_scatterers_census_2026-11-05.md; a mod with
no hit cannot hold one (the field and the type are reached by name in metadata or XML) - unless the scan says it could
not look: an unreadable file or folder is an `error` row, an XML file that names a step but does not parse is a
`parse_error` row. Output: TSV on stdout or --out.

  python3 src/RimMandrake/Minerals/scatterer_census.py --root <dir> [--root <dir> ...] [--modsconfig <ModsConfig.xml>] [--shard i/n]
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

DLL_TOKENS = (b"mineableScatterCommonality", b"GenStep_ScatterLumpsMineable", b"GenStep_PreciousLump",
              b"TileMutatorWorker_MineralRich", b"ThingSetMaker_Meteorite")
CLASS_RX = re.compile(r"ScatterLumpsMineable|PreciousLump", re.I)


def package_id(mod_dir):
    p = os.path.join(mod_dir, "About", "About.xml")
    try:
        r = ET.parse(p).getroot()
        e = r.find("packageId")
        return (e.text or "").strip().lower() if e is not None else ""
    except (OSError, ET.ParseError):
        return ""


def active_ids(modsconfig):
    if not modsconfig:
        return None
    r = ET.parse(modsconfig).getroot().find("activeMods")
    if r is None:
        return None  # no list read is "unknown" (?), never "every mod off"
    return {re.sub(r"_(steam|copy)$", "", (li.text or "").strip().lower()) for li in r.findall("li")}


def dll_hits(data):
    return [t.decode() for t in DLL_TOKENS if t in data]


def xml_hits(text):
    """(class, forced) for each node whose Class attribute names a lump-scatter step; None when the XML does not parse."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None
    out = []
    for el in root.iter():
        cls = el.attrib.get("Class", "")
        if cls and CLASS_RX.search(cls):
            forced = el.find("forcedDefToScatter")
            out.append((cls, (forced.text or "").strip() if forced is not None else ""))
    return out


def _clean(v):
    return re.sub(r"\s+", " ", v)


def mod_dirs(root):
    """A root is one mod (About/, Defs/ or Assemblies/ in it) or a folder of mods (Mods/, workshop, Data/)."""
    if any(os.path.isdir(os.path.join(root, d)) for d in ("About", "Defs", "Assemblies")):
        return [root]
    return sorted(os.path.join(root, d) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))


def scan(roots, active=None, shard=(0, 1)):
    rows = []

    def add(*r):
        rows.append(tuple(_clean(str(v)) for v in r))

    for root in roots:
        try:
            mods = mod_dirs(root)[shard[0]::shard[1]]
        except OSError as e:
            add("error", "", "?", root, "root unreadable: %s" % e, "")
            continue
        for mod in mods:
            pid = package_id(mod)
            on = "?" if active is None or not pid else ("yes" if pid in active else "no")

            def walk_err(e, mod=mod, pid=pid, on=on):
                add("error", pid, on, os.path.relpath(getattr(e, "filename", "") or mod, mod), "unreadable: %s" % e, "")

            for dp, _dn, fns in os.walk(mod, onerror=walk_err):
                for fn in fns:
                    p = os.path.join(dp, fn)
                    rel = os.path.relpath(p, mod)
                    low = fn.lower()
                    if not (low.endswith(".dll") or low.endswith(".xml")):
                        continue
                    try:
                        with open(p, "rb") as f:
                            raw = f.read()
                    except OSError as e:
                        add("error", pid, on, rel, "unreadable: %s" % e, "")
                        continue
                    if low.endswith(".dll"):
                        hits = dll_hits(raw)
                        if hits:
                            add("dll", pid, on, rel, ",".join(hits), "")
                        continue
                    probe = raw.decode("utf-16", "ignore") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "ignore")
                    if not CLASS_RX.search(probe):
                        continue
                    found = xml_hits(raw)
                    if found is None:
                        add("parse_error", pid, on, rel, "names a lump step but does not parse", "")
                    for cls, forced in found or ():
                        add("xml", pid, on, rel, cls, forced)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", action="append", required=True)
    ap.add_argument("--modsconfig")
    ap.add_argument("--out")
    ap.add_argument("--shard", default="0/1", help="i/n: scan every n-th mod folder from the i-th (parallel runs over a slow mount)")
    a = ap.parse_args(argv)
    try:
        i, n = (int(x) for x in a.shard.split("/"))
    except ValueError:
        i, n = -1, 0
    if not 0 <= i < n:
        ap.error("--shard wants i/n with 0 <= i < n, got %r" % a.shard)
    rows = scan(a.root, active_ids(a.modsconfig), (i, n))
    lines = ["kind\tpackageId\tactive\tpath\twhat\tforcedDefToScatter"] + ["\t".join(r) for r in rows]
    out = "\n".join(lines) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"{len(rows)} candidate rows -> {a.out}")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
