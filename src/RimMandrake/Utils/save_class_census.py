#!/usr/bin/env python3
"""save_class_census.py -- list every C# class a savegame names in Class="..." that no active mod provides.

    python3 save_class_census.py <save.rws> [...] [--modsconfig PATH] [--no-assemblies] [--json OUT]
    python3 save_class_census.py <save.rws> --strip-fatal OUT.rws     # copy with FATAL area entries removed
    python3 save_class_census.py <save.rws> --mods-from-save --strip-dead OUT.rws [--strip-ref DEFNAME ...]

Why (2026-10-19, Transient/vf_nre_rootcause_2026-10-19.md): saves kept `<li Class="VFEInsectoids.Area_Hive">`
after VFE Insectoids 2 was retired. An unknown Area class leaves a null in <areaManager><areas>, the WHOLE
AreaManager is discarded, Vehicle Framework NREs, and the map never finishes loading. save_donor_census.py reads
defNames in element TEXT only, so C# type names in Class= attributes were a blind spot.

Resolution: types are read from the DLLs (ECMA-335 TypeDef table, via dnfile) of every mod in the live
ModsConfig.xml activeMods list, plus the game's Managed folder. A save writes a type's name with the
Verse/RimWorld namespaces stripped (GenTypes ignored namespaces), so a bare name is resolved against those too.
All DLLs under an active mod folder count (every version folder): over-inclusive, so a miss is real.
--no-assemblies skips the DLL index and flags only RETIRED_NS namespaces (fast; used by the selftest).

--mods-from-save resolves against the mod list the SAVE records (<meta><modIds>), not the live ModsConfig: the question
"does this save load clean on the list it was made for" (WALK_SAVE_SILENCE_ABSENT_BIOME_OBJECTS, 2026-11-01: the
fw walkthrough saves d/e were made on 14 mods while the live list was another tier).

Severity of an unresolved class, by where it sits:
  FATAL     under <areaManager><areas>: one null area discards the whole AreaManager (map never loads)
  WORLDOBJ  under <worldObjects><worldObjects>: SaveableFromNode NREs in WorldObject.InitializeComps on load
            (seen 2026-10-23 on save e: RimMandrake.Pyrelands.WorldObject_RM_FurnaceHerd, cut in 84cc81013d)
  SKIPPED   a map/world/game component: the engine drops it and goes on, with an error line
  OTHER     anything else (thing comps, hediffs, needs...): that object loads wrong; review
--strip-fatal removes FATAL elements only; --strip-dead removes every FATAL, WORLDOBJ and SKIPPED element (a class
that also sits in an OTHER context is left whole and named). Both are balanced <li>..</li> or <li ... />, byte-level,
CRLF kept, never in place, and the copy must re-parse. A world object's own deep-saved contents go with it; a
reference to its ID from elsewhere would dangle, so --strip-dead refuses one whose WorldObject_<ID> is named anywhere.
--strip-ref DEFNAME also drops by-name references to a def the same mod list does not define: a leaf <li>NAME</li>
(ThingFilter allowedDefs) and an <li> whose only element child is <animal>NAME</animal> (autoSlaughter configs).
It refuses a name the def index resolves. Other def-by-name references are save_def_census.py's business.
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


def modsconfig_active(modsconfig: Path) -> list[str]:
    return [li.text.strip().lower() for li in ET.parse(modsconfig).getroot().find("activeMods")]


def save_active(saves: list[Path]) -> list[str]:
    """The <modIds> every save records; refuses saves made on different lists (one index answers for all)."""
    import modsconfig_from_save as MS
    lists = {tuple(x.strip().lower() for x in MS.mod_list(s)["modIds"]) for s in saves}
    if len(lists) != 1 or not next(iter(lists)):
        raise SystemExit("--mods-from-save: the saves record different (or no) mod lists; run them one at a time")
    return list(next(iter(lists)))


def active_types(modsconfig: Path | None = None, active: list[str] | None = None) -> tuple[set[str], int, list[str]]:
    if active is None:
        active = modsconfig_active(modsconfig)
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
    if parts[-2:] == ["worldObjects", "worldObjects"]:
        return "WORLDOBJ"
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
STRIP_DEAD = ("FATAL", "WORLDOBJ", "SKIPPED")


def _li_end(d: bytes, i: int) -> int:
    """End offset of the <li ...> element opening at i: self-closing, or balanced against nested <li> (a nested
    self-closing <li .../> opens nothing; <lifeStage> and the like are not <li>)."""
    gt = d.find(b">", i)
    if d[gt - 1:gt] == b"/":
        return gt + 1
    depth, k = 0, gt
    while True:
        o, e = d.find(b"<li", k + 1), d.find(b"</li>", k + 1)
        if e < 0:
            raise SystemExit(f"unbalanced <li> at byte {i}")
        if o != -1 and o < e:
            k = o
            if d[o + 3:o + 4] not in (b">", b" "):
                continue
            g = d.find(b">", o)
            if d[g - 1:g] != b"/":
                depth += 1
        elif depth:
            depth, k = depth - 1, e
        else:
            return e + len(b"</li>")


def _cut(d: bytes, start: int, end: int) -> tuple[bytes, bytes]:
    """Remove [start,end) plus the indentation and line break before it."""
    while start > 0 and d[start - 1:start] in (b"\t", b" "):
        start -= 1
    if d[start - 2:start] == b"\r\n":
        start -= 2
    elif d[start - 1:start] == b"\n":
        start -= 1
    return d[:start] + d[end:], d[start:end]


def _strip_li_classes(d: bytes, classes: list[str], check=None) -> tuple[bytes, list[str]]:
    removed = []
    for c in classes:
        pat = re.compile(rb'<li Class="' + re.escape(c.encode()) + rb'"[ />]')
        while (m := pat.search(d)):
            i = m.start()
            if check:
                check(d, i, c)
            d, seg = _cut(d, i, _li_end(d, i))
            removed.append(seg.decode("utf-8", "replace"))
    return d, removed


def _write_checked(src: Path, dst: Path, d: bytes) -> None:
    if dst.resolve() == src.resolve() or dst.exists():
        raise SystemExit(f"refusing to write {dst}: in place or exists")
    try:
        ET.fromstring(d)
    except ET.ParseError as e:
        raise SystemExit(f"stripped copy does not parse ({e}); nothing written")
    dst.write_bytes(d)


def strip_fatal(src: Path, dst: Path, classes: list[str]) -> list[str]:
    """Byte-level balanced removal of <li Class="X">..</li> inside <areas>; CRLF untouched; never in place."""
    if dst.resolve() == src.resolve() or dst.exists():
        raise SystemExit(f"refusing to write {dst}: in place or exists")

    def inside_areas(d, i, c):
        if d.rfind(b"<areas>", 0, i) < d.rfind(b"</areas>", 0, i):
            raise SystemExit(f"{c} at byte {i} is not inside <areas>")
    d, removed = _strip_li_classes(src.read_bytes(), classes, inside_areas)
    _write_checked(src, dst, d)
    return removed


def strip_dead(src: Path, dst: Path, rows: list[dict], refs: list[str] = ()) -> dict:
    """Remove every FATAL/WORLDOBJ/SKIPPED dead-class element, and the by-name references in `refs` (already
    checked absent by the caller). Returns what went and what was left."""
    if dst.resolve() == src.resolve() or dst.exists():
        raise SystemExit(f"refusing to write {dst}: in place or exists")
    sev = defaultdict(set)
    for r in rows:
        sev[r["class"]].add(r["severity"])
    take = sorted(c for c, ss in sev.items() if ss <= set(STRIP_DEAD))
    left = sorted(c for c in sev if c not in take)
    d = orig = src.read_bytes()

    def no_dangling_id(dd, i, c):
        # world objects only (a component's nested <ID>s are not world-object IDs); judged on the ORIGINAL bytes,
        # so a reference does not vanish just because a sibling strip removed it first
        if "WORLDOBJ" not in sev[c]:
            return
        m = re.search(rb"<ID>(\d+)</ID>", dd[i:_li_end(dd, i)])
        if m and b"WorldObject_" + m.group(1) + b"<" in orig:
            raise SystemExit(f"{c} world object ID {m.group(1).decode()} is referenced elsewhere; strip it by hand")
    d, removed = _strip_li_classes(d, take, no_dangling_id)
    ref_cuts = Counter()
    for name in refs:
        n = re.escape(name.encode())
        leaf = re.compile(rb"<li>" + n + rb"</li>")
        while (m := leaf.search(d)):
            d, _ = _cut(d, m.start(), m.end())
            ref_cuts[name] += 1
        animal = re.compile(rb"<li>\s*<animal>" + n + rb"</animal>\s*</li>")
        while (m := animal.search(d)):
            d, _ = _cut(d, m.start(), m.end())
            ref_cuts[name] += 1
    _write_checked(src, dst, d)
    return {"classes": take, "elements": len(removed), "left_other": left, "refs": dict(ref_cuts)}


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("saves", nargs="+", type=Path)
    ap.add_argument("--modsconfig", type=Path, default=MODSCONFIG)
    ap.add_argument("--mods-from-save", action="store_true",
                    help="resolve against the mod list the save records, not the live ModsConfig")
    ap.add_argument("--no-assemblies", action="store_true", help="flag RETIRED_NS namespaces only; no DLL index")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--strip-fatal", type=Path, metavar="OUT", help="write a copy with FATAL classes removed")
    ap.add_argument("--strip-dead", type=Path, metavar="OUT",
                    help="write a copy with every FATAL, WORLDOBJ and SKIPPED dead class removed")
    ap.add_argument("--strip-ref", action="append", default=[], metavar="DEFNAME",
                    help="with --strip-dead: also drop by-name references to this absent def (repeatable)")
    a = ap.parse_args(argv)
    if (a.strip_fatal or a.strip_dead) and len(a.saves) != 1:
        raise SystemExit("--strip-fatal/--strip-dead take exactly one save")
    if a.strip_ref and not a.strip_dead:
        raise SystemExit("--strip-ref needs --strip-dead")
    if a.strip_dead and a.no_assemblies:
        raise SystemExit("--strip-dead needs the DLL index (drop --no-assemblies)")
    active = save_active(a.saves) if a.mods_from_save else None

    known = None
    retired = set()
    if not a.no_assemblies:
        known, n_active, missing = active_types(a.modsconfig, active)
        retired = retired_types()
        # sanity probe: the instrument must see a type we know is loaded, and must not see the retired one
        probe_ok = "RimWorld.Area_Home" in known and "Verse.Area" in known and "VFEInsectoids.Area_Hive" not in known \
            and ("VFEInsectoids.Area_Hive" in retired or not retired)
        if UNREADABLE:
            print(f"# WARNING {len(UNREADABLE)} DLL(s) unreadable or empty, their types invisible: "
                  + "; ".join(UNREADABLE[:5]))
        print(f"# index ({'save modIds' if active else a.modsconfig}): {n_active} active mods ({len(missing)} not found on disk), {len(known)} types; "
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
        fatal = sorted({r["class"] for r in report[str(a.saves[0])] if r["severity"] == "FATAL"})
        gone = strip_fatal(a.saves[0], a.strip_fatal, fatal)
        print(f"# stripped {len(gone)} FATAL element(s) {fatal} -> {a.strip_fatal}")
    if a.strip_dead:
        if a.strip_ref:
            import save_def_census as D
            defs, _, _ = D.live_defs(a.modsconfig, active)
            if "Human" not in defs:
                raise SystemExit("--strip-ref: the def index cannot see Human; UNMEASURED, nothing written")
            live = [n for n in a.strip_ref if D.resolves(n, defs)]
            if live:
                raise SystemExit(f"--strip-ref refused: {live} resolve on this mod list; nothing written")
        res = strip_dead(a.saves[0], a.strip_dead, report[str(a.saves[0])], a.strip_ref)
        print(f"# stripped {res['elements']} element(s) of {len(res['classes'])} dead class(es) {res['classes']}"
              f"; refs {res['refs']} -> {a.strip_dead}")
        if res["left_other"]:
            print(f"# LEFT (also in an OTHER context, review by hand): {res['left_other']}")
    bad = ("FATAL", "WORLDOBJ")
    return 1 if any(r["severity"] in bad for rows in report.values() for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
