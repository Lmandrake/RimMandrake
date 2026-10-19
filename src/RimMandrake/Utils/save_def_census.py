#!/usr/bin/env python3
"""save_def_census.py -- list every defName a savegame names in <def>NAME</def> that the CURRENT mod list does not define.

    python3 save_def_census.py <save.rws>... [--modsconfig PATH] [--src] [--json OUT] [--top N]
    python3 save_def_census.py <save.rws> --strip-things OUT.rws [--def NAME ...]   # copy without those plant/item things

Why (2026-10-19, Transient/live_testing_2026-10-19b.md): a cauldron test-site save kept 1528 `RM_TreeMartyr`
plants, a def cut the day before (9a8fc0edf). Scribe logged 'Could not load reference' x1534, then 100 'Exception
spawning loaded thing null' and the map load went bad. save_donor_census.py only knows the RETIRED-DONOR list, so a
def WE removed is invisible to it. Any def removal needs a save thing census first; this is that census.

Def set: every `<defName>` in the XML files of every mod of the ModsConfig list (the folders the game reads:
the Steam Mods/workshop dirs and Data/<DLC>), excluding Languages/Textures/Sounds/Assemblies/About and version
folders older than 1.6 (over-inclusive otherwise, so a miss is real). Implied defs the game builds in code resolve
through their base (Frame_/Blueprint_/Install_/Corpse_/Techprint_/Neurotrainer_). `--src` also reads src/ and marks
defs that exist ONLY there as 'src-only' (written but not deployed yet): they still count unresolved for the live game.
A probe refuses to report when the set cannot see ThingDef Human or a known-absent def is present.

Grading, by element: a THING is an element with BOTH <def> and <id> children (Plant, Building, Pawn, item ...), the
kind that can throw at spawn; (b) everything else (terrain, hediffs, thoughts, mutators, factions) is a reference that
Scribe drops with one log line.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_class_census as K  # noqa: E402

SRC = Path(__file__).resolve().parents[1]  # .../src
SKIP_DIRS = {"languages", "textures", "sounds", "assemblies", "about", "source", "news"}
IMPLIED = ("Frame_", "Blueprint_", "Install_", "Corpse_", "Techprint_", "Neurotrainer_")
DEFNAME = re.compile(rb"<defName>\s*([^<\s][^<]*?)\s*</defName>")
CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "rm_save_def_census_defs.v1.json"


def _old_version_dir(name: str) -> bool:
    m = re.fullmatch(r"v?(\d+)\.(\d+)", name)
    return bool(m) and (int(m[1]), int(m[2])) < (1, 6)


def defs_in(root: Path) -> set[str]:
    out: set[str] = set()
    if not root.is_dir():
        return out
    for a, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d.lower() not in SKIP_DIRS and not _old_version_dir(d)]
        for f in fs:
            if f.lower().endswith(".xml"):
                try:
                    out.update(m.decode("utf-8", "replace") for m in DEFNAME.findall((Path(a) / f).read_bytes()))
                except OSError:
                    pass
    return out


def live_defs(modsconfig: Path) -> tuple[set[str], int, list[str]]:
    active = [li.text.strip().lower() for li in ET.parse(modsconfig).getroot().find("activeMods")]
    idx = K.mod_index()
    missing = [p for p in active if p not in idx]
    cache = {}
    try:
        cache = json.loads(CACHE.read_text())
    except (OSError, ValueError):
        pass
    out: set[str] = set()
    dirty = False
    for p in active:
        d = idx.get(p)
        if d is None or not d.is_dir():
            continue
        try:
            sig = max((x.stat().st_mtime for x in [d, d / "Defs", d / "Patches"] if x.exists()), default=0)
        except OSError:
            sig = 0
        key = f"{d}|{int(sig)}"
        if key not in cache:
            cache[key] = sorted(defs_in(d))
            dirty = True
        out.update(cache[key])
    if dirty:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache))
    return out, len(active), missing


def resolves(name: str, known: set[str]) -> bool:
    if name in known:
        return True
    return any(name.startswith(p) and name[len(p):] in known for p in IMPLIED)


def save_defs(save: Path) -> list[tuple[str, str, str]]:
    """(defName, kind, parentTag) for every <def>: kind is the Class= of a THING, else ''."""
    out = []
    for _, el in ET.iterparse(save, events=("end",)):
        d = el.find("def")
        if d is not None and d.text and d.text.strip():
            is_thing = el.find("id") is not None
            out.append((d.text.strip(), (el.get("Class") or el.tag) if is_thing else "", el.tag))
    return out


def census(save: Path, known: set[str], src_only: set[str] | None = None) -> dict:
    things, refs = Counter(), Counter()
    total_things = 0
    for name, kind, tag in save_defs(save):
        if kind:
            total_things += 1
        if resolves(name, known):
            continue
        (things if kind else refs)[(name, kind or tag)] += 1
    return {"things_total": total_things,
            "things": [{"def": n, "kind": k, "count": c, "src_only": bool(src_only and n in src_only)}
                       for (n, k), c in things.most_common()],
            "refs": [{"def": n, "tag": k, "count": c, "src_only": bool(src_only and n in src_only)}
                     for (n, k), c in refs.most_common()]}


def strip_things(src: Path, dst: Path, defs: list[str]) -> tuple[int, list[str]]:
    """Byte-level balanced removal of every <thing Class=..> block whose <def> is in defs. CRLF kept, never in place.
    SAFE: a block that nests another <thing, or whose id text occurs anywhere else in the file (a reference from a
    list, lord, designation ...), is kept and returned in the skipped list (def:id:why). Returns (removed, skipped)."""
    if dst.resolve() == src.resolve() or dst.exists():
        raise SystemExit(f"refusing to write {dst}: in place or exists")
    d = src.read_bytes()
    pat = re.compile(rb"(?:" + b"|".join(re.escape(x.encode()) for x in sorted(defs, key=len, reverse=True)) + rb")\d+")
    seen = Counter(m.decode() for m in pat.findall(d))
    removed, skipped = 0, []
    for name in defs:
        needle = f"<def>{name}</def>".encode()
        pos = 0
        while (i := d.find(needle, pos)) >= 0:
            s = d.rfind(b"<thing ", 0, i)
            between = d[s:i]
            if s < 0 or b"</thing>" in between or between.count(b"<") != 1:
                pos = i + 1  # not the first child of a thing block: a plain reference, keep
                continue
            end = d.find(b"</thing>", i)
            block = d[s:end]
            m = re.search(rb"<id>([^<]+)</id>", block)
            tid = m[1].decode() if m else "?"
            if b"<thing " in block[1:]:
                skipped.append(f"{name}:{tid}:nested")
                pos = end
                continue
            if seen[tid] > 1:
                skipped.append(f"{name}:{tid}:referenced x{seen[tid] - 1}")
                pos = end
                continue
            end += len(b"</thing>")
            start = s
            while start > 0 and d[start - 1:start] in (b"\t", b" "):
                start -= 1
            if d[start - 2:start] == b"\r\n":
                start -= 2
            d = d[:start] + d[end:]
            removed += 1
            pos = start
    dst.write_bytes(d)
    return removed, skipped


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("saves", nargs="+", type=Path)
    ap.add_argument("--modsconfig", type=Path, default=K.MODSCONFIG)
    ap.add_argument("--src", action="store_true", help="also index src/ to mark src-only defs")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--strip-things", type=Path, metavar="OUT")
    ap.add_argument("--def", dest="defs", action="append", help="def to strip (default: all unresolved plain things)")
    a = ap.parse_args(argv)

    known, n_active, missing = live_defs(a.modsconfig)
    probe = "Human" in known and "RM_ZZZ_NoSuchDef_Probe" not in known
    print(f"# index: {n_active} active mods ({len(missing)} not on disk), {len(known)} defNames; probe {'OK' if probe else 'FAILED'}")
    if not probe:
        print("# PROBE FAILED: UNMEASURED")
        return 2
    src_only = (defs_in(SRC) - known) if a.src else None
    report, bad = {}, False
    for s in a.saves:
        r = census(s, known, src_only)
        report[str(s)] = r
        bad |= bool(r["things"])
        print(f"{s.name}: {r['things_total']} things; unresolved THING defs {sum(x['count'] for x in r['things'])} "
              f"({len(r['things'])} defs), other refs {sum(x['count'] for x in r['refs'])} ({len(r['refs'])} defs)")
        for x in r["things"][:a.top]:
            print(f"  THING {x['count']:6} {x['kind']:12} {x['def']}{'  [src-only]' if x['src_only'] else ''}")
        for x in r["refs"][:a.top]:
            print(f"  ref   {x['count']:6} {x['tag']:12} {x['def']}")
    if a.json:
        a.json.write_text(json.dumps(report, indent=1))
    if a.strip_things:
        if len(a.saves) != 1:
            raise SystemExit("--strip-things takes exactly one save")
        r = report[str(a.saves[0])]
        defs = a.defs or [x["def"] for x in r["things"] if x["kind"] in ("Plant", "Building", "Mineable", "Thing", "ThingWithComps")]
        n, skipped = strip_things(a.saves[0], a.strip_things, defs)
        print(f"# removed {n} thing block(s) of {defs} -> {a.strip_things}; kept {len(skipped)}: {skipped[:20]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
