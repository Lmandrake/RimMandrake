#!/usr/bin/env python3
"""
animal_live_diff.py — diff the offline animal inventory against a live def dump.

VERSION 1.0  (2026-08-10)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Docs/manifest: src/RimMandrake/Utils/README.md  ("animal_live_diff.py" section)
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

THE POINT
---------
`animal_inventory.py` reads Defs on disk: it knows which mod and which xpath to
target, which is what you need to WRITE a patch. `src/RimMandrake/RimDefDump` dumps the
def database from inside the running game after every PatchOperation has
applied: it knows what actually resulted, which is what you need to TRUST one.

Neither is the truth on its own. This tool is the join, and the join is the
deliverable — it turns "I think this xpath hits the right thing" into a verified
statement, and it retires three documented limitations of the offline scan:

  * PatchOperation results       -> visible as field deltas on matched defs
  * mod-vs-mod override winners  -> visible as modName disagreements
  * shortHashCandidate is a guess-> checked against the real shortHash

INPUTS
  --live     a DefDump folder (animals.json + manifest.json), written by
             src/RimMandrake/RimDefDump. See that mod's README for how to arm it.
  --offline  a folder holding animals.csv + biome_animals.csv
             (default: observed/2026-08-13/inventory)

OUTPUTS
  divergence.csv       one row per animal, with a status and any field deltas
  biome_divergence.csv one row per (biome, animal) pair that disagrees
  console              the summary you actually read

HOW TO READ THE STATUS COLUMN
  both          present in both. Check the delta columns.
  live_only     the game has it, the file scan does not. Expect: created by a
                PatchOperation, or a def whose <race> is purely inherited (the
                offline tool selects animals on the def's OWN <race>).
  offline_only  the file scan has it, the game does not. Expect: removed by a
                PatchOperation, lost to a mod-vs-mod override, or gated off by
                MayRequire — which the offline scan does not evaluate.

Neither live_only nor offline_only is automatically a bug. They are the list of
things worth explaining.

SELF-TEST
  python animal_live_diff.py --selftest
Builds a synthetic dump exercising every classification and asserts the result,
so the tool is verifiable without paying a ~23 minute game load.
"""

import argparse
import csv
import io
import json
import os
import sys
import tempfile

# Offline CSV column  ->  where the same quantity lives in the live dump.
# "stats.X"  reads animals[].stats.X          (resolved via GetStatValueAbstract)
# "race.X"   reads animals[].race.X           (resolved RaceProperties field)
FIELD_MAP = [
    ("moveSpeed", "stats.MoveSpeed"),
    ("marketValue", "stats.MarketValue"),
    ("mass", "stats.Mass"),
    ("comfyTempMin", "stats.ComfyTemperatureMin"),
    ("comfyTempMax", "stats.ComfyTemperatureMax"),
    ("wildness", "stats.Wildness"),
    ("leatherAmount", "stats.LeatherAmount"),
    ("meatAmount", "stats.MeatAmount"),
    ("carryingCapacity", "stats.CarryingCapacity"),
    ("toxicResistance", "stats.ToxicResistance"),
    ("psychicSensitivity", "stats.PsychicSensitivity"),
    ("minimumHandlingSkill", "stats.MinimumHandlingSkill"),
    ("armorSharp", "stats.ArmorRating_Sharp"),
    ("armorBlunt", "stats.ArmorRating_Blunt"),
    ("armorHeat", "stats.ArmorRating_Heat"),
    ("baseBodySize", "race.baseBodySize"),
    ("baseHealthScale", "race.baseHealthScale"),
    ("baseHungerRate", "race.baseHungerRate"),
    ("lifeExpectancy", "race.lifeExpectancy"),
    ("gestationPeriodDays", "race.gestationPeriodDays"),
    ("nuzzleMtbHours", "race.nuzzleMtbHours"),
    ("roamMtbDays", "race.roamMtbDays"),
    ("manhunterOnDamageChance", "race.manhunterOnDamageChance"),
    ("manhunterOnTameFailChance", "race.manhunterOnTameFailChance"),
    ("maxPreyBodySize", "race.maxPreyBodySize"),
    ("trainability", "race.trainability"),
    ("petness", "race.petness"),
    ("predator", "race.predator"),
    ("herdAnimal", "race.herdAnimal"),
    ("packAnimal", "race.packAnimal"),
    ("hasGenders", "race.hasGenders"),
    ("fleshType", "race.fleshType"),
    ("bloodDef", "race.bloodDef"),
    ("body", "race.body"),
    ("leatherDef", "race.leatherDef"),
    ("useMeatFrom", "race.useMeatFrom"),
]

# Relative tolerance for float comparison. Stat values go through a float
# pipeline in the game and a text pipeline on disk; exact equality would report
# thousands of meaningless deltas.
REL_TOL = 1e-3
ABS_TOL = 1e-6


def fnum(s):
    try:
        return float(str(s).strip())
    except Exception:
        return None


def norm_bool(s):
    t = str(s).strip().lower()
    if t in ("true", "1"):
        return "true"
    if t in ("false", "0"):
        return "false"
    return None


def values_agree(offline, live):
    """
    True when the two representations mean the same thing.

    Deliberately lenient in three specific ways, each of which would otherwise
    generate pure noise:
      * numbers compared with a relative tolerance
      * booleans normalised across True/true/1
      * an empty offline value is 'no opinion', not a disagreement — the offline
        scan legitimately cannot see plenty of fields
    """
    o = "" if offline is None else str(offline).strip()
    l = "" if live is None else str(live).strip()

    if o == "":
        return True          # offline had nothing to say
    if o == l:
        return True

    ob, lb = norm_bool(o), norm_bool(l)
    if ob is not None and lb is not None:
        return ob == lb

    of, lf = fnum(o), fnum(l)
    if of is not None and lf is not None:
        if abs(of - lf) <= ABS_TOL:
            return True
        denom = max(abs(of), abs(lf))
        return denom > 0 and abs(of - lf) / denom <= REL_TOL

    return o.lower() == l.lower()


def dig(obj, path):
    """Fetch a dotted path, returning None if any hop is missing."""
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        if part not in cur:
            return None
        cur = cur[part]
    return cur


def load_live(live_dir):
    ap = os.path.join(live_dir, "animals.json")
    if not os.path.isfile(ap):
        sys.exit("no animals.json in %s — is that a DefDump folder? "
                 "See src/RimMandrake/RimDefDump/README.md for how to produce one."
                 % live_dir)
    with io.open(ap, encoding="utf-8") as f:
        data = json.load(f)

    manifest = {}
    mp = os.path.join(live_dir, "manifest.json")
    if os.path.isfile(mp):
        with io.open(mp, encoding="utf-8") as f:
            manifest = json.load(f)
    return data, manifest


def load_offline(off_dir):
    ap = os.path.join(off_dir, "animals.csv")
    if not os.path.isfile(ap):
        sys.exit("no animals.csv in %s — run animal_inventory.py first." % off_dir)
    with io.open(ap, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    pairs = set()
    bp = os.path.join(off_dir, "biome_animals.csv")
    if os.path.isfile(bp):
        with io.open(bp, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                pairs.add((r["biome"], r["animal"]))
    return rows, pairs


def diff(live_data, offline_rows, offline_pairs):
    live_by_name = {}
    for a in live_data.get("animals", []):
        dn = a.get("defName")
        if dn:
            live_by_name[dn] = a

    # The offline scan can carry duplicate defNames (mods redefining each
    # other). Keep the last, which is the load-order winner it also reports.
    off_by_name = {}
    for r in offline_rows:
        dn = (r.get("defName") or "").strip()
        if dn:
            off_by_name[dn] = r

    rows = []
    stats = {"both": 0, "live_only": 0, "offline_only": 0,
             "hash_mismatch": 0, "mod_mismatch": 0, "field_deltas": 0,
             "defs_with_deltas": 0}

    for dn in sorted(set(live_by_name) | set(off_by_name)):
        lv, off = live_by_name.get(dn), off_by_name.get(dn)

        if lv is not None and off is None:
            stats["live_only"] += 1
            rows.append({"defName": dn, "status": "live_only",
                         "liveMod": lv.get("modName", ""),
                         "offlineMod": "",
                         "liveShortHash": lv.get("shortHash", ""),
                         "offlineShortHashCandidate": "",
                         "hashMatch": "", "modMatch": "",
                         "deltaCount": "", "deltas": ""})
            continue

        if lv is None:
            stats["offline_only"] += 1
            rows.append({"defName": dn, "status": "offline_only",
                         "liveMod": "", "offlineMod": off.get("modName", ""),
                         "liveShortHash": "",
                         "offlineShortHashCandidate": off.get("shortHashCandidate", ""),
                         "hashMatch": "", "modMatch": "",
                         "deltaCount": "", "deltas": ""})
            continue

        stats["both"] += 1

        # shortHash: the offline value is a candidate because the game bumps
        # collisions across the whole loaded set. This is where we find out.
        lh = str(lv.get("shortHash", "")).strip()
        oh = str(off.get("shortHashCandidate", "")).strip()
        hash_match = "" if not oh or not lh else ("yes" if oh == lh else "NO")
        if hash_match == "NO":
            stats["hash_mismatch"] += 1

        # Mod attribution: disagreement means an override the offline scan
        # flagged but could not resolve.
        lm = (lv.get("modName") or "").strip()
        om = (off.get("modName") or "").strip()
        mod_match = "" if not lm or not om else ("yes" if lm == om else "NO")
        if mod_match == "NO":
            stats["mod_mismatch"] += 1

        deltas = []
        for col, path in FIELD_MAP:
            if col not in off:
                continue
            live_val = dig(lv, path)
            if live_val is None:
                continue
            if not values_agree(off.get(col), live_val):
                deltas.append("%s: %s -> %s" % (col, off.get(col), live_val))

        if deltas:
            stats["field_deltas"] += len(deltas)
            stats["defs_with_deltas"] += 1

        rows.append({"defName": dn, "status": "both",
                     "liveMod": lm, "offlineMod": om,
                     "liveShortHash": lh, "offlineShortHashCandidate": oh,
                     "hashMatch": hash_match, "modMatch": mod_match,
                     "deltaCount": len(deltas), "deltas": " | ".join(deltas)[:600]})

    # biome x animal, keyed on race defName so it lines up with the offline
    # pairs, which are (biome, animal-defName) not (biome, pawnkind).
    live_pairs = set()
    for p in live_data.get("biomeAnimals", []):
        race = p.get("race")
        if race:
            live_pairs.add((p.get("biome"), race))

    bio_rows = []
    for key in sorted(live_pairs - offline_pairs):
        bio_rows.append({"biome": key[0], "animal": key[1], "status": "live_only"})
    for key in sorted(offline_pairs - live_pairs):
        bio_rows.append({"biome": key[0], "animal": key[1], "status": "offline_only"})

    stats["biome_live_only"] = len(live_pairs - offline_pairs)
    stats["biome_offline_only"] = len(offline_pairs - live_pairs)
    stats["biome_both"] = len(live_pairs & offline_pairs)
    return rows, bio_rows, stats


DIV_COLUMNS = ["defName", "status", "liveMod", "offlineMod",
               "liveShortHash", "offlineShortHashCandidate", "hashMatch",
               "modMatch", "deltaCount", "deltas"]


def write_csv(path, cols, rows):
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)


def report(rows, bio_rows, stats, manifest, out_dir):
    print("\n=== offline vs live ===")
    if manifest:
        print("live dump: %s, %s mods, captured %s"
              % (manifest.get("gameVersion", "?"),
                 manifest.get("modCount", "?"),
                 manifest.get("capturedUtc", "?")))
    print("  matched (both)        %5d" % stats["both"])
    print("  live only             %5d   <- patch-created, or race purely inherited"
          % stats["live_only"])
    print("  offline only          %5d   <- patch-removed, overridden, or MayRequire-gated"
          % stats["offline_only"])
    print("  shortHash mismatches  %5d   <- offline value was a candidate; these were wrong"
          % stats["hash_mismatch"])
    print("  mod attribution diffs %5d   <- override winners the offline scan could not resolve"
          % stats["mod_mismatch"])
    print("  defs with field deltas%5d   (%d deltas total)  <- PatchOperation results"
          % (stats["defs_with_deltas"], stats["field_deltas"]))
    print("  biome pairs: both %d, live only %d, offline only %d"
          % (stats["biome_both"], stats["biome_live_only"], stats["biome_offline_only"]))

    worst = sorted((r for r in rows if r["status"] == "both" and r["deltaCount"]),
                   key=lambda r: -r["deltaCount"])[:10]
    if worst:
        print("\nmost-patched animals:")
        for r in worst:
            print("   %-26s %2d  %s" % (r["defName"], r["deltaCount"], r["deltas"][:110]))

    print("\nwrote divergence.csv and biome_divergence.csv to %s" % os.path.abspath(out_dir))


# ---------------------------------------------------------------- self-test
def selftest():
    """
    Build a synthetic live dump in the exact shape RimDefDump emits, plus a
    matching offline CSV, and assert every classification. This is what makes
    the tool trustworthy before a real dump exists.
    """
    tmp = tempfile.mkdtemp(prefix="livediff_selftest_")
    live_dir = os.path.join(tmp, "live")
    off_dir = os.path.join(tmp, "offline")
    os.makedirs(live_dir)
    os.makedirs(off_dir)

    live = {
        "animals": [
            {   # clean match, nothing changed
                "defName": "Muffalo", "shortHash": 1111, "modName": "Core",
                "stats": {"MoveSpeed": 4.5, "MarketValue": 300.0},
                "race": {"baseBodySize": 2.4, "trainability": "None",
                         "predator": False, "gestationPeriodDays": 6.66},
            },
            {   # a PatchOperation moved MoveSpeed and body size
                "defName": "Thrumbo", "shortHash": 2222, "modName": "Core",
                "stats": {"MoveSpeed": 5.6, "MarketValue": 4000.0},
                "race": {"baseBodySize": 4.0, "trainability": "Advanced",
                         "predator": True},
            },
            {   # offline guessed the hash wrong (collision bumped in game)
                "defName": "Alphabeaver", "shortHash": 3333, "modName": "Core",
                "stats": {"MoveSpeed": 3.2},
                "race": {"baseBodySize": 0.5},
            },
            {   # another mod won the override
                "defName": "Armadillo", "shortHash": 4444,
                "modName": "Beasts of the Rim (Continued)",
                "stats": {"MoveSpeed": 3.0},
                "race": {"baseBodySize": 0.6},
            },
            {   # created by a patch; offline cannot see it
                "defName": "PatchBornBeast", "shortHash": 5555, "modName": "SomeMod",
                "stats": {"MoveSpeed": 2.0},
                "race": {"baseBodySize": 1.0},
            },
        ],
        "biomeAnimals": [
            {"biome": "Desert", "pawnKind": "Muffalo", "race": "Muffalo", "commonality": 1.0},
            {"biome": "Tundra", "pawnKind": "PatchBornBeast", "race": "PatchBornBeast",
             "commonality": 0.5},
        ],
    }
    with io.open(os.path.join(live_dir, "animals.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(live))
    with io.open(os.path.join(live_dir, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"gameVersion": "1.6.4871", "modCount": 562,
                            "capturedUtc": "2026-08-10T00:00:00Z"}))

    cols = ["defName", "modName", "shortHashCandidate", "moveSpeed", "marketValue",
            "baseBodySize", "trainability", "predator", "gestationPeriodDays"]
    off_rows = [
        # matches live exactly
        dict(defName="Muffalo", modName="Core", shortHashCandidate="1111",
             moveSpeed="4.5", marketValue="300", baseBodySize="2.4",
             trainability="None", predator="False", gestationPeriodDays="6.66"),
        # two fields differ -> patch deltas
        dict(defName="Thrumbo", modName="Core", shortHashCandidate="2222",
             moveSpeed="5.0", marketValue="4000", baseBodySize="3.5",
             trainability="Advanced", predator="True", gestationPeriodDays=""),
        # hash guess wrong
        dict(defName="Alphabeaver", modName="Core", shortHashCandidate="9999",
             moveSpeed="3.2", marketValue="", baseBodySize="0.5",
             trainability="", predator="", gestationPeriodDays=""),
        # offline attributed to the loser of an override
        dict(defName="Armadillo", modName="Odyssey", shortHashCandidate="4444",
             moveSpeed="3.0", marketValue="", baseBodySize="0.6",
             trainability="", predator="", gestationPeriodDays=""),
        # gone at runtime
        dict(defName="GhostAnimal", modName="DeadMod", shortHashCandidate="7777",
             moveSpeed="1.0", marketValue="", baseBodySize="0.2",
             trainability="", predator="", gestationPeriodDays=""),
    ]
    write_csv(os.path.join(off_dir, "animals.csv"), cols, off_rows)
    with io.open(os.path.join(off_dir, "biome_animals.csv"), "w",
                 encoding="utf-8-sig", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["biome", "animal", "sources", "direction", "commonality", "mod", "file"])
        wr.writerow(["Desert", "Muffalo", 1, "biome.wildAnimals", "1.0", "Core", "x.xml"])
        wr.writerow(["Boreal", "GhostAnimal", 1, "biome.wildAnimals", "1.0", "DeadMod", "y.xml"])

    live_data, manifest = load_live(live_dir)
    offline_rows, offline_pairs = load_offline(off_dir)
    rows, bio_rows, stats = diff(live_data, offline_rows, offline_pairs)
    by = dict((r["defName"], r) for r in rows)

    checks = [
        ("both counted", stats["both"] == 4),
        ("live_only counted", stats["live_only"] == 1),
        ("offline_only counted", stats["offline_only"] == 1),
        ("PatchBornBeast is live_only", by["PatchBornBeast"]["status"] == "live_only"),
        ("GhostAnimal is offline_only", by["GhostAnimal"]["status"] == "offline_only"),
        ("Muffalo has no deltas", by["Muffalo"]["deltaCount"] == 0),
        ("Thrumbo has 2 deltas", by["Thrumbo"]["deltaCount"] == 2),
        ("delta text names the field", "moveSpeed" in by["Thrumbo"]["deltas"]),
        ("hash mismatch found", stats["hash_mismatch"] == 1),
        ("Alphabeaver flagged", by["Alphabeaver"]["hashMatch"] == "NO"),
        ("Muffalo hash ok", by["Muffalo"]["hashMatch"] == "yes"),
        ("mod mismatch found", stats["mod_mismatch"] == 1),
        ("Armadillo override flagged", by["Armadillo"]["modMatch"] == "NO"),
        ("empty offline field is not a delta",
         "gestationPeriodDays" not in by["Thrumbo"]["deltas"]),
        ("bool True/true agrees", "predator" not in by["Thrumbo"]["deltas"]),
        ("float tolerance holds", "marketValue" not in by["Thrumbo"]["deltas"]),
        ("biome live_only", stats["biome_live_only"] == 1),
        ("biome offline_only", stats["biome_offline_only"] == 1),
        ("biome both", stats["biome_both"] == 1),
    ]

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("ok   " if ok else "FAIL ") + n)
    print()
    if bad:
        print("%d FAILURES" % len(bad))
        return 1
    print("ALL PASS (%d checks)" % len(checks))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", help="DefDump folder (animals.json + manifest.json)")
    ap.add_argument("--offline", default=os.path.join("observed", "2026-08-13", "inventory"),
                    help="folder with animals.csv (default: observed/2026-08-13/inventory)")
    ap.add_argument("--out", default=".")
    ap.add_argument("--selftest", action="store_true",
                    help="verify the differ against a synthetic dump and exit")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(selftest())
    if not a.live:
        sys.exit("--live is required (or use --selftest). "
                 "Produce a dump with src/RimMandrake/RimDefDump.")

    live_data, manifest = load_live(a.live)
    offline_rows, offline_pairs = load_offline(a.offline)
    rows, bio_rows, stats = diff(live_data, offline_rows, offline_pairs)

    os.makedirs(a.out, exist_ok=True)
    write_csv(os.path.join(a.out, "divergence.csv"), DIV_COLUMNS, rows)
    write_csv(os.path.join(a.out, "biome_divergence.csv"),
              ["biome", "animal", "status"], bio_rows)
    report(rows, bio_rows, stats, manifest, a.out)


if __name__ == "__main__":
    main()
