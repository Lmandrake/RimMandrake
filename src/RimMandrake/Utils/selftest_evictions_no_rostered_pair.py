#!/usr/bin/env python3
"""selftest_evictions_no_rostered_pair.py -- the generated BiomeCastEvictions_WildBiomes.xml never
evicts a pair a roster admits (EVICTIONS_RAZORJACK_FIX_STALE_ROW: AA_Razorjack x ZBiome_Grasslands
was shipped though rostered), and the generator's exemption covers a race's Corpse_ twin.

Offline, no capture needed: reads the roster JSONs and the shipped evictions XML."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "design", "Jawa", "fauna"))
import biome_wildbiomes_evictions as E  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


roster = E.rostered()
# Positive control: the instrument can see the very pair the item named.
check("AA_Razorjack" in roster.get("ZBiome_Grasslands", set()),
      "control: the ZBiome_Grasslands roster admits AA_Razorjack")
check(sum(len(v) for v in roster.values()) > 100,
      "control: rosters read (%d admissions)" % sum(len(v) for v in roster.values()))

# Generator unit: race, kind and corpse twin are all exempt; an unrostered race is not.
r = {"B": {"KindX", "RaceY"}}
k = {"RaceX": ["KindX"]}
check(E.is_rostered("RaceY", "B", r, k), "is_rostered: race named directly")
check(E.is_rostered("RaceX", "B", r, k), "is_rostered: race via its kind")
check(E.is_rostered("Corpse_RaceX", "B", r, k), "is_rostered: corpse twin via its race's kind")
check(E.is_rostered("Corpse_RaceY", "B", r, k), "is_rostered: corpse twin of a named race")
check(not E.is_rostered("RaceZ", "B", r, k), "is_rostered: unrostered race is evictable")
check(not E.is_rostered("RaceY", "Other", r, k), "is_rostered: scoped to the biome")

xml = os.path.join(E.REPO, "src", "RimUtinni", "UtinniPatches", "Patches",
                   "BiomeCastEvictions_WildBiomes.xml")
pairs = set(E.PAIR_RE.findall(open(xml, encoding="utf-8").read()))
check(len(pairs) > 100, "control: shipped file parsed (%d pairs)" % len(pairs))
# Kinds are capture-only; offline, a race counts as rostered by its own name or its corpse's race.
bad = sorted((a, b) for a, b in pairs if E.is_rostered(a, b, roster, {}))
check(not bad, "shipped evictions hold no rostered pair: %s" % bad[:5])
check(("AA_Razorjack", "ZBiome_Grasslands") not in pairs,
      "the named pair AA_Razorjack x ZBiome_Grasslands is not evicted")

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
