#!/usr/bin/env python3
"""modaudit/universe.py - the mod universe for the once-and-for-all mod audit (stage 0).

    python3 src/RimMandrake/Utils/modaudit/universe.py            # write facts/universe.json, print summary

The universe is:
  * every packageId in infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml (the canonical full list), in
    its order, and
  * every mod WE build under src/<RimMandrake|RimStarWars|RimUtinni>/ that is absent from it
    (modmanifest.shipping_ids / shipping_gap; members folded into the composed mandrake.rm.biomes excluded,
    they load inside it).

Each id is resolved to EVERY on-disk root that carries it, by parsing About/About.xml (never grep) across the
game's Mods folder, the Steam workshop (294100) and the game's Data folder (Core + DLC). Duplicates are kept
(all roots listed; the one the game would load is the Mods/Data copy before workshop - RimWorld prefers a local
copy; we record both and flag DUPLICATE). An id of ours that is not installed falls back to its src/ folder
(resolution "repo-src"). Anything else unresolved is reported, never dropped.

Classes:  OURS        mandrake.rm.* / mandrake.rsw.* / mandrake.rut.* (the three tiers) or any src/ About id
          CORE_DLC    ludeon.rimworld[.*]
          THIRD_PARTY everything else (donors, frameworks, libraries, Harmony)
"""
import json
import os
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(UTILS)))
sys.path.insert(0, UTILS)

FULL_LATEST = os.path.join(ROOT, "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
AUDIT_DIR = os.path.join(ROOT, "design", "RimMandrake", "mod_audit")
FACTS_DIR = os.path.join(AUDIT_DIR, "facts")
UNIVERSE_JSON = os.path.join(FACTS_DIR, "universe.json")
OUR_PREFIXES = ("mandrake.rm.", "mandrake.rsw.", "mandrake.rut.")


def classify(pid, src_ids=()):
    p = pid.lower()
    if p == "ludeon.rimworld" or p.startswith("ludeon.rimworld."):
        return "CORE_DLC"
    if p.startswith(OUR_PREFIXES) or p in src_ids:
        return "OURS"
    return "THIRD_PARTY"


def about_id(folder):
    """packageId (lowercased) as a DIRECT child of <ModMetaData>; a recursive find() would read a dependency's."""
    try:
        n = ET.parse(os.path.join(folder, "About", "About.xml")).getroot().find("packageId")
    except (OSError, ET.ParseError):
        return None
    return (n.text or "").strip().lower() if n is not None and (n.text or "").strip() else None


def scan_roots(roots):
    """{packageId: [{"folder", "root_kind"}]} for every immediate child of each (kind, base) root with an About.xml.
    Raises if a root cannot be listed: an unlistable root must never read as 'nothing installed'."""
    out = {}
    for kind, base in roots:
        names = sorted(os.listdir(base))
        for n in names:
            f = os.path.join(base, n)
            if not os.path.isdir(f):
                continue
            pid = about_id(f)
            if pid:
                out.setdefault(pid, []).append({"folder": f, "root_kind": kind})
    return out


def resolve(ordered_ids, installed, src_map, src_ids=()):
    """-> list of universe rows. Pure (selftested). ordered_ids: [(id, membership)] in universe order."""
    rows, seen = [], set()
    for i, (pid, membership) in enumerate(ordered_ids, 1):
        key = pid.lower()
        if key in seen:
            continue                     # a duplicate id in a list is reported by modmanifest, not doubled here
        seen.add(key)
        hits = installed.get(key, [])
        # the copy the game loads: Data (Core/DLC) > Mods (local) > workshop
        rank = {"data": 0, "mods": 1, "workshop": 2}
        hits = sorted(hits, key=lambda h: rank.get(h["root_kind"], 9))
        row = {"packageId": key, "id_as_listed": pid, "universe_order": i, "membership": membership,
               "class": classify(key, src_ids), "roots": hits, "duplicate": len(hits) > 1,
               "src": src_map.get(key)}
        if hits:
            row["resolution"] = hits[0]["root_kind"]
            row["folder"] = hits[0]["folder"]
        elif src_map.get(key):
            row["resolution"] = "repo-src"
            row["folder"] = os.path.join(ROOT, src_map[key])
        else:
            row["resolution"] = "UNRESOLVED"
            row["folder"] = None
        rows.append(row)
    return rows


def build():
    import modmanifest
    from game_paths import LOCAL_MODS, WORKSHOP, GAME_DATA
    full = modmanifest.read_modsconfig(FULL_LATEST)
    ours, folded = modmanifest.shipping_ids()
    gap = modmanifest.shipping_gap(full, ours, folded)["absent"]
    installed = scan_roots([("data", GAME_DATA), ("mods", LOCAL_MODS), ("workshop", WORKSHOP)])
    ordered = [(p, "FULL.LATEST") for p in full]
    for p in gap:
        ordered.append((p, "OURS_ABSENT_INSTALLED" if p in installed else "OURS_ABSENT_SRC_ONLY"))
    rows = resolve(ordered, installed, ours, set(ours))
    full_pos = {p.lower(): n for n, p in enumerate(full, 1)}
    for r in rows:
        r["full_latest_position"] = full_pos.get(r["packageId"])
    return {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "instrument": "modaudit/universe.py (About.xml parse over Data + Mods + workshop/294100; modmanifest.shipping_ids)",
        "full_latest": os.path.relpath(FULL_LATEST, ROOT),
        "full_latest_count": len(full),
        "installed_ids_on_disk": len(installed),
        "sanity_probe": {p: (p in installed) for p in ("brrainz.harmony", "ludeon.rimworld", "ludeon.rimworld.odyssey",
                                                       "mandrake.rm.flowworks")},
        "folded_into_biomes": sorted(folded),
        "rows": rows,
    }


def summary(u):
    rows = u["rows"]
    from collections import Counter
    c = Counter(r["class"] for r in rows)
    res = Counter(r["resolution"] for r in rows)
    mem = Counter(r["membership"] for r in rows)
    return ("universe %d (FULL.LATEST %d) | classes %s | resolution %s | membership %s | duplicates %d | probe %s"
            % (len(rows), u["full_latest_count"], dict(c), dict(res), dict(mem),
               sum(1 for r in rows if r["duplicate"]), u["sanity_probe"]))


def main():
    u = build()
    if not all(u["sanity_probe"].values()):
        raise SystemExit("SANITY PROBE FAILED %s - the root scan cannot see known mods; refusing to write" % u["sanity_probe"])
    os.makedirs(FACTS_DIR, exist_ok=True)
    with open(UNIVERSE_JSON, "w") as fh:
        json.dump(u, fh, indent=1)
    print(summary(u))
    unres = [r["packageId"] for r in u["rows"] if r["resolution"] == "UNRESOLVED"]
    print("UNRESOLVED:", unres)
    print("wrote", os.path.relpath(UNIVERSE_JSON, ROOT))


if __name__ == "__main__":
    main()
