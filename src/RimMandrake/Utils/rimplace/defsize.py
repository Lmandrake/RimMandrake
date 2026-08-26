"""rimplace.defsize - how many cells a ThingDef actually occupies.

WHY THIS FILE EXISTS
====================
The dwelling template laid every piece of furniture on a 1-cell grid regardless
of `ThingDef.size`, so a 1x2 table swallowed the chair beside it and a run of
shelves ate itself: 3 of 81 planned things were not on the map afterwards, and
`rimplace lint` reported 0 findings (TEMPLATE_FOOTPRINT_IGNORES_SIZE_1).

🔴 THE DEF DUMP CANNOT ANSWER THIS. `defs.sqlite` has no size column - checked,
`def_flags` for Shelf carries weapon/apparel/category flags and nothing
dimensional. So "absent from the dump" here is a COVERAGE hole, not a fact about
the game, and the only offline source of truth left is the XML the game loads.

WHAT IT READS
=============
The active mod set, in load order, via rimworld_loadset - the same resolver
refresh.py uses, so versioned and conditional loadFolders are handled rather
than guessed. A later mod redefining a defName wins, which is what the game
does.

⚠️ WHAT IT CANNOT SEE, stated because a size that is wrong is worse than a size
that is missing:
  * PatchOperations. A patch that rewrites <size> after load is invisible here;
    this reads defs as authored, not as patched.
  * C# that sets size at runtime.
  * Anything whose size is inherited from a def in a mod that is not ACTIVE.
Each of those returns UNKNOWN rather than a guess, and lint reports unknown as
UNMEASURED - never as 1x1, which is the assumption that caused the bug.
"""
from __future__ import annotations

import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

CACHE = _HERE.parents[3] / "observed" / "def_sizes.json"
_SIZE = re.compile(r"^\s*\(?\s*(-?\d+)\s*,\s*(-?\d+)\s*\)?\s*$")


def _parse_size(text: str | None):
    if not text:
        return None
    m = _SIZE.match(text)
    if not m:
        return None
    w, h = int(m.group(1)), int(m.group(2))
    return (w, h) if w > 0 and h > 0 else None


def scan(verbose: bool = False) -> dict:
    """{defName: [w, h]} for every active ThingDef whose size resolves.

    Returns {} if the load set cannot be read - the caller must treat that as
    UNMEASURED.
    """
    try:
        import rimworld_loadset as RL
        from game_paths import GAME_DATA, LOCAL_MODS, WORKSHOP
    except ImportError:
        return {}
    try:
        mods, missing, version = RL.build_load_set(
            RL.DEFAULT_MODS_CONFIG, [WORKSHOP, LOCAL_MODS, GAME_DATA])
    except Exception:
        return {}
    if not mods:
        return {}
    if verbose:
        print(f"  load set: {len(mods)} mod(s) resolved for {version}, "
              f"{len(missing)} missing", file=sys.stderr)
    declared: dict[str, tuple] = {}     # key (defName or Name) -> (size, parent)
    t0 = time.time()
    files = 0
    for mod in mods:
        for d in RL.def_dirs(mod, "Defs"):
            for xml in sorted(Path(d).rglob("*.xml")):
                files += 1
                try:
                    root = ET.parse(xml).getroot()
                except (ET.ParseError, OSError):
                    continue
                for node in root:
                    if not isinstance(node.tag, str) or "ThingDef" not in node.tag:
                        continue
                    name = node.get("Name")
                    dn = node.findtext("defName")
                    key = dn or name
                    if not key:
                        continue
                    declared[key] = (_parse_size(node.findtext("size")),
                                     node.get("ParentName"))
                    if dn and name:
                        declared[name] = declared[key]
    if verbose:
        print(f"  {files} def file(s), {len(declared)} ThingDef key(s), "
              f"{time.time() - t0:.1f}s", file=sys.stderr)

    # 🔑 EVERY key that was seen goes in, including the ones that declare no
    # size at all - because ThingDef.size DEFAULTS to (1,1) in the engine, so a
    # def we found and that declares nothing really is 1x1. Only a def that is
    # ABSENT from this index is unmeasured, and the difference decides whether a
    # caller may reason about it: present -> a fact, absent -> say UNMEASURED.
    out: dict[str, list] = {}
    for key, (size, parent) in declared.items():
        seen = set()
        s, p = size, parent
        while s is None and p and p not in seen:
            seen.add(p)
            nxt = declared.get(p)
            if not nxt:
                break
            s, p = nxt
        out[key] = [s[0], s[1]] if s else [1, 1]
    return out


def load(refresh: bool = False, verbose: bool = False) -> dict:
    """The size index, from cache unless refresh is asked for.

    🔑 The cache is DERIVED and regenerable; it is not committed. An empty dict
    means UNMEASURED, and every caller must say so rather than assuming 1x1.
    """
    if not refresh and CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    idx = scan(verbose=verbose)
    if idx:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE.with_suffix(".tmp")
        tmp.write_text(json.dumps(idx, indent=0, sort_keys=True), encoding="utf-8")
        tmp.replace(CACHE)
    return idx


def footprint(defName: str, x: int, z: int, rot: int, sizes: dict):
    """The cells this thing occupies, or None if its size is unknown.

    RimWorld rotates the footprint on odd rotations (1 = east, 3 = west), and
    the origin cell is the one the game is given: for even sizes the extra cell
    extends north/east, matching GenAdj.OccupiedRect.
    """
    s = sizes.get(defName)
    if not s:
        return None
    w, h = (s[1], s[0]) if rot in (1, 3) else (s[0], s[1])
    x0 = x - (w - 1) // 2
    z0 = z - (h - 1) // 2
    return {(x0 + dx, z0 + dz) for dx in range(w) for dz in range(h)}


if __name__ == "__main__":
    idx = load(refresh="--refresh" in sys.argv, verbose=True)
    big = sum(1 for v in idx.values() if v != [1, 1])
    print(f"{len(idx)} ThingDef(s) indexed, {big} bigger than 1x1 -> {CACHE}")
    for d in ("Shelf", "Table1x2c", "DiningChair", "Wall", "Bedroll", "ElectricStove"):
        print(f"  {d:<16} {idx.get(d, 'UNKNOWN')}")
