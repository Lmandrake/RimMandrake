#!/usr/bin/env python3
"""
Offline check of the VEHICLE_FUEL_ACCEPTS_VEGETABLES_1 acceptance predicate.

WHAT THIS PROVES AND WHAT IT DOES NOT.  It re-states the rule in
VegetableFuel.cs and runs it over every ThingDef in a real def dump, so it
proves the RULE admits and excludes the right defs against the owner's actual
578-mod def set.  It does NOT execute the compiled C# and it does NOT prove the
Harmony patches attach - only a game load does that.

  python3 check_fuel_predicate.py [path/to/DefDump/defs/ThingDef.json]

Default dump: the frozen OFFICIAL-2026-08-20 one named in
infrastructure/state/dumps/REGISTRY.jsonl.
"""

import json
import sys

DEFAULT_DUMP = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
                "RimWorld by Ludeon Studios/DefDump/defs/ThingDef.json")

# RimWorld.FoodTypeFlags, read out of
# C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll
# by reflection on 2026-08-21.  Do not retype these from memory - the values are
# NOT the obvious powers of two in source order, and two of them are composites
# that decide this whole check:
#   Fungus = 4097 = 4096 | VegetableOrFruit, so RawFungus IS a vegetable food.
#   OvivoreAnimal = 2848 = Kibble | Processed | Meal | AnimalProduct, so an
#   unfertilised egg is excluded by the AnimalProduct bit it hides inside.
# A name-set test instead of flag arithmetic gets both of those backwards.
FLAG_VALUES = {
    "None": 0, "VegetableOrFruit": 1, "Meat": 2, "Fluid": 4, "Corpse": 8,
    "Seed": 16, "AnimalProduct": 32, "Plant": 64, "Tree": 128, "Meal": 256,
    "Processed": 512, "Liquor": 1024, "Kibble": 2048, "Fungus": 4097,
    "VegetarianAnimal": 7953, "VegetarianRoughAnimal": 8017,
    "CarnivoreAnimal": 2826, "CarnivoreAnimalStrict": 10,
    "OmnivoreAnimal": 7963, "OmnivoreRoughAnimal": 8027,
    "DendrovoreAnimal": 6801, "OvivoreAnimal": 2848, "OmnivoreHuman": 7999,
}

# Seed added 2026-08-21 on the owner's ruling: RawRice's foodType is the standalone
# Seed flag (16), so the rule rejected a crop the item's own roster said should fuel.
ACCEPTED = (FLAG_VALUES["Plant"] | FLAG_VALUES["VegetableOrFruit"]
            | FLAG_VALUES["Meal"] | FLAG_VALUES["Seed"])
REJECTED = FLAG_VALUES["Meat"] | FLAG_VALUES["AnimalProduct"]

# The verify line from the item.  RawMeat is not a vanilla defName - meat is
# per-species - so the real meat defs stand in for it.
MUST_ACCEPT = ["Hay", "RawPotatoes", "RawCorn", "RawBerries", "RawFungus", "RawRice"]
MUST_REJECT = ["Beer", "Meat_Cow", "Meat_Human", "Milk", "Ambrosia",
               "MA_RaptorkhanEggUnfertilized"]

# Defs the item's spec claims the rule admits, that it measurably does not.
# Reported, never quietly fixed: the predicate is DECIDE's ruling verbatim.
SPEC_CLAIMS_NOT_MET = ["RawRice"]

def iter_thingdefs(path):
    """Yield one ThingDef dict at a time.  The dump is a single 300MB+ line, so
    it is decoded object by object off a sliding buffer rather than parsed
    whole - json.load on this file wants several GB."""
    decoder = json.JSONDecoder()
    marker = '"defs":['
    buffer = ""
    with open(path, "r", encoding="utf-8") as handle:
        while marker not in buffer:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                raise ValueError("%s has no \"defs\" array" % path)
            buffer += chunk
        pos = buffer.index(marker) + len(marker)

        while True:
            while pos < len(buffer) and buffer[pos] in " \t\r\n,":
                pos += 1
            if pos < len(buffer) and buffer[pos] == "]":
                return
            if pos >= len(buffer):
                chunk = handle.read(4 * 1024 * 1024)
                if not chunk:
                    return
                buffer += chunk
                continue
            try:
                obj, pos = decoder.raw_decode(buffer, pos)
            except ValueError:
                chunk = handle.read(4 * 1024 * 1024)
                if not chunk:
                    return
                buffer += chunk
                continue
            yield obj
            if pos > 4 * 1024 * 1024:
                buffer = buffer[pos:]
                pos = 0


def food_flags(raw, unknown_sink):
    """Turn "Fluid, Processed, Liquor" into the int the game would hold."""
    value = 0
    for part in (raw or "").split(","):
        name = part.strip()
        if not name:
            continue
        if name not in FLAG_VALUES:
            unknown_sink.add(name)
            continue
        value |= FLAG_VALUES[name]
    return value


def nutrition_of(fields, ingestible):
    """What ThingDef.IsNutritionGivingIngestible reads, reconstructed offline.

    TRAP: IngestibleProperties.cachedNutrition is a LAZY cache, and the dump
    catches most defs before anything asked for their nutrition - Hay,
    RawPotatoes, RawBerries and MealSimple all dump as -1 while MealFine and
    Kibble dump as their real value.  Reading cachedNutrition alone rejects
    every raw crop and makes this check say the exact opposite of the truth.
    The Nutrition statBase is the value the cache is computed FROM, and the dump
    has it already resolved through def inheritance."""
    cached = float(ingestible.get("cachedNutrition") or 0.0)
    if cached > 0.0:
        return cached
    for modifier in fields.get("statBases") or []:
        if isinstance(modifier, dict) and modifier.get("stat") == "Nutrition":
            return float(modifier.get("value") or 0.0)
    return 0.0


def accepts(fields, unknown_sink):
    """VegetableFuel.IsVegetableFood, restated."""
    ingestible = fields.get("ingestible")
    if not isinstance(ingestible, dict):
        return False
    # ThingDef.IsNutritionGivingIngestible == ingestible != null && nutrition > 0
    if nutrition_of(fields, ingestible) <= 0.0:
        return False
    if (ingestible.get("drugCategory") or "None") != "None":
        return False
    food_type = food_flags(ingestible.get("foodType"), unknown_sink)
    if food_type & REJECTED:
        return False
    return bool(food_type & ACCEPTED)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DUMP
    unknown = set()
    accepted = []
    verdicts = {}
    seen = 0
    watched = set(MUST_ACCEPT) | set(MUST_REJECT) | set(SPEC_CLAIMS_NOT_MET) | {"Kibble"}

    for thing in iter_thingdefs(path):
        if thing.get("defType") != "ThingDef":
            continue
        seen += 1
        name = thing.get("defName")
        ok = accepts(thing.get("fields", {}), unknown)
        if ok:
            accepted.append(name)
        if name in watched:
            verdicts[name] = ok

    print("dump: %s" % path)
    print("ThingDefs scanned: %d" % seen)
    print("accepted by the vegetable rule: %d" % len(accepted))
    print("  sample: %s" % ", ".join(sorted(accepted)[:25]))

    failures = []
    print("\nverify line:")
    print("  count >= 6                      : %s" % ("PASS" if len(accepted) >= 6 else "FAIL"))
    if len(accepted) < 6:
        failures.append("fewer than 6 accepted defs")
    for name in MUST_ACCEPT:
        got = verdicts.get(name)
        state = "ABSENT FROM DUMP" if got is None else ("PASS" if got else "FAIL")
        print("  accepts %-24s: %s" % (name, state))
        if got is False:
            failures.append("%s rejected but must be accepted" % name)
    for name in MUST_REJECT:
        got = verdicts.get(name)
        state = "ABSENT FROM DUMP" if got is None else ("PASS" if not got else "FAIL")
        print("  rejects %-24s: %s" % (name, state))
        if got is True:
            failures.append("%s accepted but must be rejected" % name)

    print("\nthe Seed ruling, owner 2026-08-21 - these were rejected until Seed was added:")
    for name in SPEC_CLAIMS_NOT_MET:
        got = verdicts.get(name)
        print("  %-24s: accepted=%s  (foodType is the standalone Seed flag (16),"
              % (name, got))
        print("  %-24s   not VegetableOrFruit. The item's roster always said it"
              % "")
        print("  %-24s   should fuel; the rule now matches the roster.)" % "")
        if got is not True:
            failures.append("%s must be accepted since the Seed ruling" % name)

    kibble = verdicts.get("Kibble")
    print("\nKibble by the rule alone: %s" % kibble)
    print("  (the item's spec calls Kibble 'part-plant'; its foodType is the")
    print("   standalone Kibble flag, so the rule REJECTS it and DogSled keeps")
    print("   working only because VegetableFuel.Accepts always admits the")
    print("   comp's own declared fuelType.)")

    if unknown:
        print("\nUNKNOWN FoodTypeFlags names, decision NOT trustworthy: %s"
              % ", ".join(sorted(unknown)))
        failures.append("unknown foodType flag names")

    print("\n%s" % ("ALL CHECKS PASS" if not failures else "FAILURES: " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
