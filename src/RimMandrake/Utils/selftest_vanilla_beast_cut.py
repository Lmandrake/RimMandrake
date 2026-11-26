#!/usr/bin/env python3
"""selftest for vanilla_beast_cut.py (VANILLA_BEAST_EXCISION_1 wave 4) — fixtures for the pure classifier, then the
shipped Cherry Picker list against the live def dump.

    python3 src/RimMandrake/Utils/selftest_vanilla_beast_cut.py [--dump]

With no flag it runs the fixtures and the repo-file checks (the page's promises; no def dump needed). --dump adds the
dump half below, which needs the live def dump (Archmagi). --offline is accepted and means the default.

The dump half (--dump) asserts the wave's contract: every official animal no uncut roster, faction carrier or family rule
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

# VANILLA_BEAST_LEAKS_EXCISE_ESCAPEES_AT_LARGE: every (uncut route def, name) pair that still named a cut race, measured
# on Archmagi's dump captured 2026-11-12T08:10:06Z over every race in CherryPicker.SHIP.xml (not only wave 4). The egg
# pairs are read from Odyssey's Defs/Odyssey/ThingSetMakerDefs/ThingSetMakers_Fishing.xml (RimSage), because the dump
# cuts a ThingFilter off at its depth limit. Each must be struck by v.STRIKES, or its route def cut in SHIP.
MEASURED_LEAKS_2026_11_12 = [
    ("GenStepDef/RM_CathedralStrays", "Fox_Fennec"),
    ("ThingSetMakerDef/RareFishingCatches_Cold", "Seal"),
    ("ThingSetMakerDef/RareFishingCatches_Hot", "MonitorLizard"),
    ("ThingSetMakerDef/RareFishingCatches_Temperate", "Crow"),
    ("ThingSetMakerDef/RareFishingCatches_Temperate", "Porcupine"),
    ("ThingSetMakerDef/RareFishingCatches_Temperate", "Sparrow"),
    ("ThingSetMakerDef/RareFishingCatches_Temperate", "Squirrel"),
    ("ThingSetMakerDef/RareFishingCatches_Temperate", "EggDuckFertilized"),
    ("ThingSetMakerDef/RareFishingCatches_Temperate", "EggHeronFertilized"),
    ("ThingSetMakerDef/RareFishingCatches_Tropical", "Capybara"),
    ("ThingSetMakerDef/RareFishingCatches_Tropical", "Cobra"),
    ("ThingSetMakerDef/RareFishingCatches_Tropical", "Flamingo"),
    ("ThingSetMakerDef/RareFishingCatches_Tropical", "Monkey"),
    ("ThingSetMakerDef/RareFishingCatches_Tropical", "EggPeacockFertilized"),
    ("ThingSetMakerDef/RareFishingCatches_Tropical", "EggFlamingoFertilized"),
    ("ThingSetMakerDef/RareFishingCatches_Tropical", "EggCobraFertilized"),
    ("TileMutatorDef/VEE_DomesticatedEscapees", "Chicken"),
    ("TileMutatorDef/VEE_DomesticatedEscapees", "Cow"),
    ("TileMutatorDef/VEE_Megafauna", "Cat_Scimitar"),
    ("TileMutatorDef/VEE_Megafauna", "Mastodon"),
    ("TileMutatorDef/VEE_Megafauna", "Wolf_Great"),
    # C# route: VEE CaravanAnimalWI picks every race.packAnimal; Yak and Mastodon are cut pack animals.
    ("IncidentDef/VEE_CaravanAnimalsWanderIn", "Yak"),
]
# A route def of OURS is fixed at its source, not struck by a patch: the pair is closed when that file no longer
# names the race as a list entry.
OWN_DEF_FILES = {"GenStepDef/RM_CathedralStrays": os.path.join(
    v.REPO, "src", "RimMandrake", "RustCathedral", "Defs", "MapGeneration", "RM_CathedralFinishGenSteps.xml")}


def check(name, cond, detail=""):
    print("%s  %s%s" % ("ok  " if cond else "FAIL", name, ("  — " + detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def t_the_classifier_holds_back_what_waits():
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


def _rl_world():
    A = lambda **k: dict(dict(pkg="ludeon.rimworld", official=True, dryad=False, insect=False, pack=False), **k)  # noqa: E731
    animals = {"Cow": A(), "Mastodon": A(pack=True), "Yak": A(pack=True), "Megasloth": A(), "Duck": A(),
               "RSW_Bantha": A(pkg="mandrake.rsw.swbestiary", official=False, pack=True)}
    kinds = {"Mastodon": {"MastodonKind"}}
    eggs = {"EggDuckFertilized": "Duck"}
    namers = {("TileMutatorDef", "Mega"): {"MastodonKind", "Megasloth"}, ("ThingSetMakerDef", "Rare"): {"EggDuckFertilized"},
              ("RecipeDef", "Cook"): {"Cow"}, ("IncidentDef", "CutInc"): {"Cow"}}
    cut = {"ThingDef/Cow", "ThingDef/Mastodon", "ThingDef/Yak", "ThingDef/Duck", "IncidentDef/CutInc"}
    present = {"IncidentDef/VEE_CaravanAnimalsWanderIn"}
    return animals, kinds, eggs, namers, cut, present


def t_a_cut_race_stays_watched_in_every_wave():
    """A race cut in ANY wave stays watched: an uncut route def naming it, its kind or its egg is a leak."""
    animals, kinds, eggs, namers, cut, present = _rl_world()
    lk = v.route_leaks(animals, kinds, namers, cut, eggs=eggs, present=present)
    check("rl: a race cut in an earlier wave is still watched (kind name)", lk.get("Mastodon") ==
          ["IncidentDef/VEE_CaravanAnimalsWanderIn", "TileMutatorDef/Mega"], str(lk.get("Mastodon")))
    check("rl: an uncut race is no leak", "Megasloth" not in lk)
    check("rl: an egg names its hatcher race", lk.get("Duck") == ["ThingSetMakerDef/Rare"], str(lk.get("Duck")))
    check("rl: a RecipeDef mention and a cut route def are no leak", "Cow" not in lk, str(lk.get("Cow")))
    lk2 = v.route_leaks(animals, kinds, namers, cut, eggs=eggs, present=present,
                        struck={("TileMutatorDef/Mega", "MastodonKind")})
    check("rl: a struck pair closes that leak only", lk2.get("Mastodon") == ["IncidentDef/VEE_CaravanAnimalsWanderIn"],
          str(lk2.get("Mastodon")))


def t_a_cut_pack_animal_leaks_through_the_caravan_route_until_it_is_cut():
    animals, kinds, eggs, namers, cut, present = _rl_world()
    lk = v.route_leaks(animals, kinds, namers, cut, eggs=eggs, present=present)
    check("rl: a cut pack animal leaks through the C# caravan route", lk.get("Yak") == ["IncidentDef/VEE_CaravanAnimalsWanderIn"],
          str(lk.get("Yak")))
    check("rl: an owned pack animal is no leak", "RSW_Bantha" not in lk)
    lk2 = v.route_leaks(animals, kinds, namers, cut | {"IncidentDef/VEE_CaravanAnimalsWanderIn"}, eggs=eggs,
                        present=present)
    check("rl: a cut C# route closes the leak", "Yak" not in lk2, str(lk2.get("Yak")))
    lk3 = v.route_leaks(animals, kinds, namers, cut, eggs=eggs, present=set())
    check("rl: a C# route absent from the dump is no leak", "Yak" not in lk3, str(lk3.get("Yak")))


def t_a_strike_is_counted_only_in_the_shape_it_models():
    patch = """<Patch><Operation Class="PatchOperationConditional">
      <xpath>/Defs/TileMutatorDef[defName="Mega"]/modExtensions/li/forcedPawnKindDefs/li[forcedPawnKindDef="A" or forcedPawnKindDef="B"]</xpath>
      <match Class="PatchOperationRemove"><xpath>/Defs/TileMutatorDef[defName="Mega"]/modExtensions/li/forcedPawnKindDefs/li[forcedPawnKindDef="A" or forcedPawnKindDef="B"]</xpath></match>
    </Operation></Patch>"""
    check("rl: struck_pairs reads a conditional remove", v.struck_pairs_text(patch) ==
          {("TileMutatorDef/Mega", "A"), ("TileMutatorDef/Mega", "B")}, str(v.struck_pairs_text(patch)))
    bad = """<Patch><Operation Class="PatchOperationRemove"><xpath>/Defs/TileMutatorDef[defName="Mega"]//li[x="A"]</xpath></Operation></Patch>"""
    try:
        v.struck_pairs_text(bad)
        check("rl: struck_pairs refuses an op shape it does not model", False)
    except ValueError:
        check("rl: struck_pairs refuses an op shape it does not model", True)


def t_a_dump_newer_than_the_strikes_is_read_raw():
    check("sa: a dump before the strike commit counts the strikes", v.strikes_apply("2026-11-12T08:10:06Z", "2026-11-26T19:40:00-08:00"))
    check("sa: a dump after the strike commit is read raw", not v.strikes_apply("2026-11-27T08:00:00Z", "2026-11-26T19:40:00-08:00"))
    check("sa: an unknown time reads raw", not v.strikes_apply(None, "2026-11-26T19:40:00Z")
          and not v.strikes_apply("2026-11-12T08:10:06Z", None))


def t_every_measured_leak_is_closed():
    """The need, on the repo's own files: every measured leak is struck by the strike patch or its route is cut."""
    cut = v.ship_keys(v.SHIP)
    struck = v.struck_pairs(v.STRIKES) if os.path.exists(v.STRIKES) else set()
    def own_closed(k, n):
        return k in OWN_DEF_FILES and "<li>%s</li>" % n not in open(OWN_DEF_FILES[k], encoding="utf-8").read()
    open_ = [(k, n) for k, n in MEASURED_LEAKS_2026_11_12 if (k, n) not in struck and k not in cut and not own_closed(k, n)]
    check("need: every measured 2026-11-12 leak is struck or its route cut (%d open)" % len(open_), not open_, str(open_))
    check("need: the strike patch strikes nothing unmeasured", not (struck - set(MEASURED_LEAKS_2026_11_12)),
          str(sorted(struck - set(MEASURED_LEAKS_2026_11_12))))


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
    struck = v.struck_pairs(v.STRIKES) if v.strikes_apply(cap, v.strikes_committed_utc(v.STRIKES)) else set()
    lk = v.route_leaks(animals, kinds_of, namers, cut, struck=struck, eggs=v.LAST_EGGS, present=v.LAST_PRESENT)
    check("leaks: no uncut spawn route names a cut race (dump %s)" % cap, not lk, str(lk))


def main(argv):
    t_the_classifier_holds_back_what_waits()
    t_a_cut_race_stays_watched_in_every_wave()
    t_a_cut_pack_animal_leaks_through_the_caravan_route_until_it_is_cut()
    t_a_strike_is_counted_only_in_the_shape_it_models()
    t_a_dump_newer_than_the_strikes_is_read_raw()
    t_every_measured_leak_is_closed()
    if "--dump" in argv:
        live()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
