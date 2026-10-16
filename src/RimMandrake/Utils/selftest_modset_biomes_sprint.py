#!/usr/bin/env python3
"""biomes_sprint tier: a superset of ratchet_pilot's wants and guards, Phase 0 donors forbidden,
and the ExplosiveGrowth fold guard flips standalone want -> forbid (offline; no ModsConfig touched)."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modset_builder as mb

fails = []
def check(name, cond):
    if not cond:
        fails.append(name)

t, p = mb.TIERS["biomes_sprint"], mb.TIERS["ratchet_pilot"]
check("dlc on", t["dlc"] is True)
check("pilot wants kept", set(p["want"]) <= set(t["want"]))
check("pilot guards kept", set(p["forbid"]) <= set(t["forbid"]) and set(p["forbid_substr"]) <= set(t["forbid_substr"]))
for d in ("mlie.starwarsanimalcollection", "sarg.alphaanimals", "daria40k.alphaanimalspatchoutposts"):
    check("donor forbidden " + d, d in t["forbid"])
eg = "mandrake.rm.explosivegrowth"
check("EG exactly one of want/forbid", (eg in t["want"]) != (eg in t["forbid"]))
check("EG matches compose file", (eg in t["forbid"]) == mb._composed_in_biomes("ExplosiveGrowth"))

# the guard reader itself, on a fixture compose file
real_root = mb.ROOT
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "src", "RimMandrake"))
    f = os.path.join(d, "src", "RimMandrake", "Biomes.compose.json")
    mb.ROOT = d
    try:
        json.dump({"compose_wave": 2, "entries": [{"key": "ExplosiveGrowth", "wave": 2}]}, open(f, "w"))
        check("composed at wave<=compose_wave", mb._composed_in_biomes("ExplosiveGrowth"))
        json.dump({"compose_wave": 2, "entries": [{"key": "ExplosiveGrowth", "wave": 3}]}, open(f, "w"))
        check("not composed at a later wave", not mb._composed_in_biomes("ExplosiveGrowth"))
        os.remove(f)
        check("missing compose file -> not composed", not mb._composed_in_biomes("ExplosiveGrowth"))
    finally:
        mb.ROOT = real_root

print("FAIL: " + ", ".join(fails) if fails else "OK selftest_modset_biomes_sprint")
sys.exit(1 if fails else 0)
