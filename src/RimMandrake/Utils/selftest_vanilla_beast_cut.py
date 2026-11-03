#!/usr/bin/env python3
"""selftest for vanilla_beast_cut.py (VANILLA_BEAST_EXCISION_1 wave 4) — fixtures for the pure classifier, then the
shipped Cherry Picker list against the live def dump.

    python3 src/RimMandrake/Utils/selftest_vanilla_beast_cut.py

The dump half asserts the wave's contract: every official animal no uncut roster, faction carrier or family rule
holds back is cut in CherryPicker.SHIP.xml (nothing eligible is left open), the wave-4 keys resolve with the right
def type (cherrypick_build.check), and none of them strips a roster or a carrier. A future dump that frees an
animal (its biome's sitting cut it from the roster) fails the "nothing open" check on purpose: that is the next wave.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vanilla_beast_cut as v  # noqa: E402

FAILS = []

WAVE4 = v.WAVES[4]


def check(name, cond, detail=""):
    print("%s  %s%s" % ("ok  " if cond else "FAIL", name, ("  — " + detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def fixtures():
    A = lambda **k: dict(dict(pkg="ludeon.rimworld", official=True, dryad=False, insect=False), **k)  # noqa: E731
    animals = {"Cow": A(), "Hare": A(), "Muffalo": A(), "Dryad_Basic": A(dryad=True), "Megaspider": A(insect=True),
               "Chimera": A(pkg="ludeon.rimworld.anomaly"), "Gone": A(), "Ghostcow": A(), "Zero": A(),
               "Thrumbo": A(), "RSW_Bantha": A(pkg="mandrake.rsw.bestiary", official=False)}
    kinds = {"Hare": {"HareKind"}, "Ghostcow": {"Ghostcow"}}
    biomes = {"Arid": {"wildAnimals": [("HareKind", 1.0), ("Zero", 0)]},
              "CutBiome": {"wildAnimals": [("Ghostcow", 2.0)]}}
    factions = {"Traders": {"Muffalo"}}
    namers = {("TileMutatorDef", "Escapees"): {"Cow"}, ("RecipeDef", "Cook"): {"Thrumbo"},
              ("IncidentDef", "CutInc"): {"Zero"}}
    cut = {"ThingDef/Gone", "BiomeDef/CutBiome", "IncidentDef/CutInc"}
    res, leaks = v.classify(animals, kinds, biomes, factions, namers, cut)
    check("fx: already-cut race is not open", "Gone" not in res)
    check("fx: ours never listed", "RSW_Bantha" not in res)
    check("fx: roster member via its kind name waits", res.get("Hare", "").startswith("roster"))
    check("fx: commonality-0 roster entry does not hold", res.get("Zero") == "cut")
    check("fx: a CUT biome's roster does not hold", res.get("Ghostcow") == "cut")
    check("fx: carrier waits", res.get("Muffalo", "").startswith("carrier"))
    check("fx: dryad / insect / anomaly are family", all(res.get(n, "").startswith("family")
                                                         for n in ("Dryad_Basic", "Megaspider", "Chimera")))
    check("fx: a route def naming it is a leak, not a block", res.get("Cow") == "cut" and leaks.get("Cow") == ["TileMutatorDef/Escapees"])
    check("fx: a RecipeDef mention is no route", "Thrumbo" not in leaks and res.get("Thrumbo") == "cut")
    check("fx: a cut route def is no leak", "Zero" not in leaks)
    ks = v.keys_for(["Thrumbo", "Cow"], {"ThingDef/Cow"})
    check("fx: keys_for adds the C# companion and skips present keys", ks == ["ThingDef/Thrumbo", "IncidentDef/ThrumboPasses"], str(ks))


def live():
    if not os.path.exists(v.DB):
        check("dump present at %s" % v.DB, False, "UNMEASURED: no def dump; run src/RimMandrake/Utils/refresh.py")
        return
    cap, animals, kinds_of, biomes, factions, namers = v.load(v.DB)
    cut = v.ship_keys(v.SHIP)
    off = [n for n, a in animals.items() if a["official"]]
    check("sanity: the dump sees >100 official animals (%d)" % len(off), len(off) > 100)
    check("sanity: Muffalo is a faction carrier", "Muffalo" in {k for ks in factions.values() for k in ks})
    check("sanity: SHIP list parses to >1000 keys (%d)" % len(cut), len(cut) > 1000)
    res, leaks = v.classify(animals, kinds_of, biomes, factions, namers, cut)
    owed = v.keys_for([n for n, r in res.items() if r == "cut"], cut)
    check("contract: no eligible official animal left uncut (dump %s)" % cap, not owed, "owed: %s" % owed)
    check("wave 4: every key is in SHIP", all(k in cut for k in WAVE4), str([k for k in WAVE4 if k not in cut]))
    # Re-classify as though wave 4 were not cut: none of its races may be roster- or carrier-bound.
    pre, _ = v.classify(animals, kinds_of, biomes, factions, namers, cut - set(WAVE4))
    bad = {n: pre.get(n) for n in (k.split("/")[1] for k in WAVE4 if k.startswith("ThingDef/")) if pre.get(n) != "cut"}
    check("wave 4: no key strips a roster, a carrier or a family", not bad, str(bad))
    import cherrypick_build as cb
    probs = cb.check(WAVE4)
    check("wave 4: every key resolves with its def type (cherrypick_build.check)", not probs, str(probs))


def main():
    fixtures()
    live()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
