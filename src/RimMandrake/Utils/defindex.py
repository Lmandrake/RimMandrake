#!/usr/bin/env python3
"""defindex.py -- every def of a RimDefDump capture as (type, defName, shortHash, packageId), fast and cached,
and the question "does mod list X provide def N?" answered offline.

    python3 src/RimMandrake/Utils/defindex.py [--capture DIR] [--modlist ModsConfig.xml] [--name N ...]

WHY: the dump's defs/*.json is ~720 MB (ThingDef.json alone ~400 MB). json.load on it is gigabytes; def_diff's
streaming raw_decode is correct but slow. Every def RECORD in the dump opens with the same flat header
    {"defName":..,"defType":..,"defTypeFull":..,"label":..,"shortHash":N,"modName":..,"packageId":..
so one regex over the bytes finds them all. Measured 2026-10-18 on the 2026-10-16T09-47-54Z capture: 82,703
records, equal to sum(manifest.defCounts) -- the count check below REFUSES the index when it is not, so a header
change in RimDefDump cannot make this silently see fewer defs. ~16 s cold, then cached as gzip JSON under
~/.cache/rimmandrake/defindex/ (a program reads it: never the repo).

A MOD LIST'S DEFS, OFFLINE (`ModSetDefs`): the dump was captured on a DIFFERENT mod list than the one asked about,
so "provided" = a dump def whose packageId is on the list, + a dump def with no packageId (engine-generated:
Corpse_/Meat_/Blueprint_/Frame_ ...) whose stripped base is provided, + a src/ def (any def file under a src mod
whose packageId, composed-biome folds resolved, is on the list -- catches ports added after the capture).
What this CANNOT see, said on every report: defs a mod makes at runtime that the dump did not capture, defs a
non-src mod added since the capture, and the shortHash table the NEW list will assign (collisions resolve per
load order, so a hash decoded through this table is INFERRED for any list but the dump's own).
"""
import argparse
import collections
import gzip
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "src")
if HERE not in sys.path:
    sys.path.insert(0, HERE)

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "rimmandrake", "defindex")
HEADER = re.compile(rb'\{"defName":"((?:[^"\\]|\\.)*)","defType":"([^"]*)","defTypeFull":"[^"]*",'
                    rb'"label":(?:null|"(?:[^"\\]|\\.)*"),"shortHash":(\d+),'
                    rb'"modName":(?:null|"(?:[^"\\]|\\.)*"),"packageId":(?:null|"([^"]*)")')
ENGINE_PREFIX = ("Blueprint_Install_", "Blueprint_", "Frame_", "Corpse_", "Meat_", "Leather_", "Egg_")
CHUNK = 32 << 20


def default_capture():
    from game_paths import DEF_DUMP
    return DEF_DUMP


def capture_with(packages, newest_first=True):
    """The newest capture whose manifest lists any of `packages` (e.g. a pre-retirement dump that still holds the
    donors' defs), or None. Reads manifests only."""
    from game_paths import CAPTURES
    packages = {p.lower() for p in packages}
    try:
        names = sorted(os.listdir(CAPTURES), reverse=newest_first)
    except OSError:
        return None
    for n in names:
        mp = os.path.join(CAPTURES, n, "manifest.json")
        try:
            man = json.load(open(mp, encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if packages & {m.get("packageId", "").lower() for m in man.get("mods", [])}:
            return os.path.join(CAPTURES, n)
    return None


def _scan_file(path):
    out = []
    with open(path, "rb") as fh:
        tail = b""
        while True:
            b = fh.read(CHUNK)
            if not b:
                break
            buf = tail + b
            last = 0
            for m in HEADER.finditer(buf):
                pkg = m.group(4)
                out.append((m.group(2).decode(), json.loads(b'"' + m.group(1) + b'"'), int(m.group(3)),
                            pkg.decode().lower() if pkg else None))
                last = m.end()
            tail = buf[max(last, len(buf) - 4096):]       # a header is < 4 KB; a straddling one is re-read
    return out


def build(capture):
    man = json.load(open(os.path.join(capture, "manifest.json"), encoding="utf-8-sig"))
    rows = []
    ddir = os.path.join(capture, "defs")
    for fn in sorted(os.listdir(ddir)):
        if fn.endswith(".json"):
            rows += _scan_file(os.path.join(ddir, fn))
    want = sum((man.get("defCounts") or {}).values())
    if want and len(rows) != want:
        raise ValueError("defindex: %d def headers found but the manifest counts %d -- the RimDefDump header "
                         "format changed; this index would be blind to %d defs. Fix HEADER." % (len(rows), want,
                                                                                               want - len(rows)))
    return {"capture": os.path.basename(capture.rstrip("/\\")), "capturedUtc": man.get("capturedUtc"),
            "modCount": man.get("modCount"), "mods": [m.get("packageId", "").lower() for m in man.get("mods", [])],
            "defs": rows}


def load_raw(capture=None, cache=CACHE, rebuild=False):
    capture = capture or default_capture()
    cid = os.path.basename(capture.rstrip("/\\")) or "capture"
    cp = os.path.join(cache, cid + ".json.gz")
    mp = os.path.join(capture, "manifest.json")
    if not rebuild and os.path.isfile(cp) and os.path.getmtime(cp) >= os.path.getmtime(mp):
        with gzip.open(cp, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    t = time.time()
    raw = build(capture)
    os.makedirs(cache, exist_ok=True)
    with gzip.open(cp + ".tmp", "wt", encoding="utf-8") as fh:
        json.dump(raw, fh)
    os.replace(cp + ".tmp", cp)
    sys.stderr.write("defindex: built %d defs from %s in %.0fs (cached %s)\n" % (len(raw["defs"]), cid,
                                                                               time.time() - t, cp))
    return raw


class Index(object):
    def __init__(self, raw):
        self.raw = raw
        self.capture = raw.get("capture")
        self.mods = raw.get("mods", [])
        self.by_name = collections.defaultdict(list)          # name -> [(type, hash, pkg)]
        for t, n, h, p in raw["defs"]:
            self.by_name[n].append((t, h, p))

    def hash_table(self, def_type):
        """{shortHash: defName} for one def type (ShortHashGiver namespaces are per type)."""
        return {h: n for n, rows in self.by_name.items() for t, h, p in rows if norm_type(t) == def_type}

    def names_of(self, packages):
        packages = {p.lower() for p in packages}
        return {n for n, rows in self.by_name.items() if any(p in packages for t, h, p in rows)}


def modlist_packages(path):
    root = ET.fromstring(open(path, "rb").read().decode("utf-8-sig"))
    node = root.find("activeMods")
    return [(li.text or "").strip().lower() for li in node.findall("li")] if node is not None else []


def src_defs():
    """{defName: {(type, packageId)}} for every def file under src/ (composed folds resolved)."""
    sys.path.insert(0, os.path.join(HERE, "modcheck"))
    import l1_donor_off_round as L                            # its src walker and packageId fold, not a copy
    pids = L._package_ids()
    out = collections.defaultdict(set)
    for p in L._def_xml_files("Defs"):
        root = L._parse(p)
        if root is None:
            continue
        pid = pids.get(L._mod_folder(p))
        for el in root:
            if isinstance(el.tag, str):
                n = (el.findtext("defName") or "").strip()
                if n:
                    out[n].add((el.tag, pid))
    return out


class ModSetDefs(object):
    """Which defNames a mod list provides, from a dump of another list + src/. See the module docstring."""

    def __init__(self, index, packages, src=None, extra_absent=()):
        self.ix = index
        self.packages = {p.lower() for p in packages}
        self.removed = sorted(set(index.mods) - self.packages)   # in the dump, not on this list
        self.added = sorted(self.packages - set(index.mods))     # on this list, never dumped: UNMEASURED
        self.src = src if src is not None else {}
        self.extra_absent = set(extra_absent)                    # e.g. a retired donor's workshop defNames

    def types(self, name):
        t = {norm_type(r[0]) for r in self.ix.by_name.get(name, ())}
        t |= {norm_type(r[0]) for r in self.src.get(name, ())}
        return t

    def known(self, name):
        return name in self.ix.by_name or name in self.src or name in self.extra_absent

    def provided(self, name, def_type=None):
        """True / False, or None when no offline source knows the name at all."""
        hit = False
        for t, h, p in self.ix.by_name.get(name, ()):
            if def_type and norm_type(t) != def_type:
                continue
            if p is None:
                base = _strip_engine(name)
                if base != name:
                    if self.provided(base) is True:
                        return True
                    continue
                if name not in self.extra_absent:
                    return True                                  # generated, unattributed, still in the dump
                continue
            hit = True
            if p in self.packages:
                return True
        for t, p in self.src.get(name, ()):
            if def_type and norm_type(t) != def_type:
                continue
            hit = True
            if p in self.packages:
                return True
        if hit or self.known(name):
            return False
        base = _strip_engine(name)
        if base != name and self.known(base):
            return self.provided(base)
        return None

    def owner(self, name):
        pk = sorted({p for t, h, p in self.ix.by_name.get(name, ()) if p} | {p for t, p in self.src.get(name, ()) if p})
        return pk


def norm_type(t):
    """'ThingDef_AlienRace' -> 'ThingDef', 'AbilityUser.AbilityDef' -> 'AbilityDef' (the dump names the runtime class)."""
    t = (t or "").rsplit(".", 1)[-1]
    m = re.match(r"^([A-Za-z]+Def)(?:_|$)", t)
    return m.group(1) if m else t


def _strip_engine(name):
    for pre in ENGINE_PREFIX:
        if name.startswith(pre) and len(name) > len(pre):
            return name[len(pre):]
    return name


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--capture")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--modlist", help="ModsConfig-shaped list to answer 'provided?' against")
    ap.add_argument("--name", nargs="*", default=[])
    a = ap.parse_args(argv)
    ix = Index(load_raw(a.capture, rebuild=a.rebuild))
    print("capture %s: %d defs, %d mods" % (ix.capture, len(ix.raw["defs"]), len(ix.mods)))
    if a.modlist:
        ms = ModSetDefs(ix, modlist_packages(a.modlist), src_defs())
        print("list %s: %d mods; dump-only (treated absent): %s; never dumped (UNMEASURED): %s"
              % (os.path.basename(a.modlist), len(ms.packages), ms.removed or "none", ms.added or "none"))
        for n in a.name:
            print("  %-40s provided=%s types=%s owners=%s" % (n, ms.provided(n), sorted(ms.types(n)), ms.owner(n)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
