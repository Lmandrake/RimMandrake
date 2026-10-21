#!/usr/bin/env python3
"""save_class_census.py -- list every C# class a savegame names in Class="..." that no active mod provides.

    python3 save_class_census.py <save.rws> [...] [--modsconfig PATH] [--no-assemblies] [--json OUT]
    python3 save_class_census.py <save.rws> --strip-fatal OUT.rws     # copy with FATAL area entries removed

Why (2026-10-19, Transient/vf_nre_rootcause_2026-10-19.md): saves kept `<li Class="VFEInsectoids.Area_Hive">`
after VFE Insectoids 2 was retired. An unknown Area class leaves a null in <areaManager><areas>, the WHOLE
AreaManager is discarded, Vehicle Framework NREs, and the map never finishes loading. save_donor_census.py reads
defNames in element TEXT only, so C# type names in Class= attributes were a blind spot.

Resolution: types are read from the DLLs (ECMA-335 TypeDef table, via dnfile) of every mod in the live
ModsConfig.xml activeMods list, plus the game's Managed folder. A save writes a type's name with the
Verse/RimWorld namespaces stripped (GenTypes ignored namespaces), so a bare name is resolved against those too.
All DLLs under an active mod folder count (every version folder): over-inclusive, so a miss is real.
--no-assemblies skips the DLL index and flags only RETIRED_NS namespaces (fast; used by the selftest).

Severity of an unresolved class, by where it sits:
  FATAL     under <areaManager><areas>: one null area discards the whole AreaManager (map never loads)
  SKIPPED   a map/world/game component: the engine drops it and goes on
  OTHER     anything else (thing comps, hediffs, needs...): that object loads wrong; review
--strip-fatal removes FATAL elements only (balanced <li>..</li>, byte-level, CRLF kept), never in place.
Defs-by-name references are NOT this tool's business (Scribe logs 'Could not load reference' and carries on).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

STEAM = Path("/mnt/c/Program Files (x86)/Steam/steamapps")
ROOTS = [STEAM / "common/RimWorld/Mods", STEAM / "workshop/content/294100"]
GAME_DATA = STEAM / "common/RimWorld/Data"
MANAGED = STEAM / "common/RimWorld/RimWorldWin64_Data/Managed"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_paths  # noqa: E402  the one path seam
MODSCONFIG = Path(game_paths.MODS_CONFIG)
CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "rm_save_class_census_types.v2.json"
UNREADABLE: list[str] = []  # DLLs dnfile could not read: their types are invisible, so "unknown" may be false

# Retired donors (2026-10-19 donor-free list). Namespaces measured from their 1.6 DLLs with dnfile, plus
# AlphaBiomes (sarg.alphabiomes, no longer on disk). A class in one of these namespaces is RETIRED.
RETIRED_PIDS = ["grimterra.biomesmod", "lingluo.cockroach", "mlie.horrors", "oskarpotocki.vfe.insectoid2",
                "regrowth.botr.core", "sarg.alphagenes", "who.vfee.isopodageneline", "sarg.alphabiomes",
                "mlie.starwarsanimalcollection"]
RETIRED_NS = ["VFEInsectoids", "AlphaBiomes", "ReGrowthCore", "Ling_Cockroach", "Horrors", "Isopoda_Geneline",
              "Isopoda_Geneline_Insector", "Isopoda_Geneline_AlienRacePatch", "AlphaGenes", "SWAC"]
IGNORED_NS = ["Verse", "Verse.AI", "Verse.AI.Group", "Verse.Sound", "Verse.Grammar", "RimWorld", "RimWorld.Planet",
              "RimWorld.BaseGen", "RimWorld.QuestGen", "RimWorld.SketchGen", "RimWorld.Utility", "System"]
COMPONENT_LISTS = {"components"}


# ---------------------------------------------------------------- type index
def _dll_types(path: Path) -> list[str]:
    import dnfile
    pe = dnfile.dnPE(str(path), fast_load=False)
    try:
        md = pe.net.mdtables if pe.net else None
        if md is None or md.TypeDef is None:
            return []
        rows = list(md.TypeDef.rows)
        full = {}
        for i, r in enumerate(rows, 1):
            ns, nm = str(r.TypeNamespace or ""), str(r.TypeName or "")
            full[i] = f"{ns}.{nm}" if ns else nm
        if md.NestedClass is not None:
            for _ in range(4):  # nesting depth
                for r in md.NestedClass.rows:
                    if r.NestedClass is None or r.EnclosingClass is None:  # dnfile cannot resolve some rows
                        continue
                    inner, outer = r.NestedClass.row_index, r.EnclosingClass.row_index
                    full[inner] = f"{full.get(outer, '?')}+{rows[inner - 1].TypeName}"
        return list(full.values())
    finally:
        pe.close()


def _about_pid(d: Path) -> str | None:
    # the TOP-LEVEL packageId: a regex for the first <packageId> hits <modDependencies> first (53 of 535 missed)
    try:
        root = ET.parse(d / "About/About.xml").getroot()
    except (OSError, ET.ParseError):
        return None
    for ch in root:
        if ch.tag.lower() == "packageid" and (ch.text or "").strip():
            return ch.text.strip().lower()
    return None


def mod_index() -> dict[str, Path]:
    idx: dict[str, Path] = {}
    for r in ROOTS:
        if not r.is_dir():
            continue
        for d in sorted(r.iterdir()):
            pid = _about_pid(d)
            if pid and pid not in idx:
                idx[pid] = d
    for dl in ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]:
        idx["ludeon.rimworld" if dl == "Core" else "ludeon.rimworld." + dl.lower()] = GAME_DATA / dl
    return idx


def types_of(dirs: list[Path]) -> set[str]:
    cache = {}
    try:
        cache = json.loads(CACHE.read_text())
    except (OSError, ValueError):
        pass
    out, dirty = set(), False
    for d in dirs:
        if not d.is_dir():
            continue
        for a, _, fs in os.walk(d):
            for f in fs:
                if not f.lower().endswith(".dll"):
                    continue
                p = Path(a) / f
                st = p.stat()
                key = f"{p}|{st.st_size}|{int(st.st_mtime)}"
                if key not in cache:
                    try:
                        cache[key] = _dll_types(p)
                    except Exception:
                        cache[key] = None
                    dirty = True
                if not cache[key]:
                    UNREADABLE.append(str(p))
                out.update(cache[key] or [])
    if dirty:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache))
    return out


def active_types(modsconfig: Path) -> tuple[set[str], int, list[str]]:
    active = [li.text.strip().lower() for li in ET.parse(modsconfig).getroot().find("activeMods")]
    idx = mod_index()
    missing = [p for p in active if p not in idx]
    dirs = [idx[p] for p in active if p in idx] + [MANAGED]
    return types_of(dirs), len(active), missing


def retired_types() -> set[str]:
    idx = mod_index()
    return types_of([idx[p] for p in RETIRED_PIDS if p in idx])


# ---------------------------------------------------------------- save scan
def class_sites(save: Path) -> list[tuple[str, str]]:
    """(class, context path of the two enclosing tags) for every element carrying Class=."""
    out, stack = [], []
    for ev, el in ET.iterparse(save, events=("start", "end")):
        if ev == "start":
            stack.append(el.tag)
            c = el.get("Class")
            if c:
                out.append((c, "/".join(stack[-3:-1])))
        else:
            stack.pop()
            if len(stack) <= 2:
                el.clear()
    return out


def severity(ctx: str) -> str:
    parts = ctx.split("/")
    if parts[-2:] == ["areaManager", "areas"]:
        return "FATAL"
    if parts and parts[-1] in COMPONENT_LISTS:
        return "SKIPPED"
    return "OTHER"


def _ns_root(c: str) -> str:
    return c.split("`")[0].rsplit(".", 1)[0] if "." in c else ""


def is_retired(c: str, retired: set[str]) -> bool:
    base = c.split("`")[0]
    ns = _ns_root(c)
    return base in retired or any(ns == r or ns.startswith(r + ".") for r in RETIRED_NS)


def resolves(c: str, known: set[str]) -> bool:
    base = c.split("[")[0]
    if base in known:
        return True
    return "." not in base.split("`")[0] and any(f"{ns}.{base}" in known for ns in IGNORED_NS)


def census(save: Path, known: set[str] | None, retired: set[str]) -> list[dict]:
    rows = Counter()
    for c, ctx in class_sites(save):
        ok = resolves(c, known) if known is not None else not is_retired(c, retired)
        if ok:
            continue
        rows[(c, ctx)] += 1
    out = []
    for (c, ctx), n in sorted(rows.items()):
        out.append({"class": c, "count": n, "context": ctx, "severity": severity(ctx),
                    "retired_donor": is_retired(c, retired)})
    return out


# ---------------------------------------------------------------- strip
def strip_fatal(src: Path, dst: Path, classes: list[str]) -> list[str]:
    """Byte-level balanced removal of <li Class="X">..</li> inside <areas>; CRLF untouched; never in place."""
    if dst.resolve() == src.resolve() or dst.exists():
        raise SystemExit(f"refusing to write {dst}: in place or exists")
    d = src.read_bytes()
    removed = []
    for c in classes:
        open_tag = f'<li Class="{c}">'.encode()
        while (i := d.find(open_tag)) >= 0:
            if d.rfind(b"<areas>", 0, i) < d.rfind(b"</areas>", 0, i):
                raise SystemExit(f"{c} at byte {i} is not inside <areas>")
            depth, k = 0, i
            while True:
                o, e = d.find(b"<li", k + 1), d.find(b"</li>", k + 1)
                if o != -1 and o < e:
                    depth, k = depth + 1, o
                elif depth:
                    depth, k = depth - 1, e
                else:
                    end = e + len(b"</li>")
                    break
            start = i
            while start > 0 and d[start - 1:start] in (b"\t", b" "):
                start -= 1
            if d[start - 2:start] == b"\r\n":
                start -= 2
            removed.append(d[start:end].decode("utf-8", "replace"))
            d = d[:start] + d[end:]
    dst.write_bytes(d)
    return removed


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("saves", nargs="+", type=Path)
    ap.add_argument("--modsconfig", type=Path, default=MODSCONFIG)
    ap.add_argument("--no-assemblies", action="store_true", help="flag RETIRED_NS namespaces only; no DLL index")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--strip-fatal", type=Path, metavar="OUT", help="write a copy with FATAL classes removed")
    a = ap.parse_args(argv)

    known = None
    retired = set()
    if not a.no_assemblies:
        known, n_active, missing = active_types(a.modsconfig)
        retired = retired_types()
        # sanity probe: the instrument must see a type we know is loaded, and must not see the retired one
        probe_ok = "RimWorld.Area_Home" in known and "Verse.Area" in known and "VFEInsectoids.Area_Hive" not in known \
            and ("VFEInsectoids.Area_Hive" in retired or not retired)
        if UNREADABLE:
            print(f"# WARNING {len(UNREADABLE)} DLL(s) unreadable or empty, their types invisible: "
                  + "; ".join(UNREADABLE[:5]))
        print(f"# index: {n_active} active mods ({len(missing)} not found on disk), {len(known)} types; "
              f"retired donors: {len(retired)} types; probe {'OK' if probe_ok else 'FAILED'}")
        if not probe_ok:
            print("# PROBE FAILED: the type index cannot see RimWorld.Area_Home or sees Area_Hive; results UNMEASURED")
            return 2
    report = {}
    for s in a.saves:
        rows = census(s, known, retired)
        report[str(s)] = rows
        print(f"{s.name}: {len(rows)} unresolved class sites")
        for r in rows:
            print(f"  {r['severity']:7} {'RETIRED' if r['retired_donor'] else 'unknown':7} "
                  f"{r['count']:5}  {r['class']}  @ {r['context']}")
    if a.json:
        a.json.write_text(json.dumps(report, indent=1))
    if a.strip_fatal:
        if len(a.saves) != 1:
            raise SystemExit("--strip-fatal takes exactly one save")
        fatal = sorted({r["class"] for r in report[str(a.saves[0])] if r["severity"] == "FATAL"})
        gone = strip_fatal(a.saves[0], a.strip_fatal, fatal)
        print(f"# stripped {len(gone)} FATAL element(s) {fatal} -> {a.strip_fatal}")
    return 1 if any(r["severity"] == "FATAL" for rows in report.values() for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
