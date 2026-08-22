#!/usr/bin/env python3
r"""gen_pawnkind_roster.py - the 48 faction pawn kinds, from design/…/pawnkind_roster.md.

WHY THIS IS GENERATED. The roster is a design table: twelve factions x four roles, with
weaponMoney, apparelMoney and a quality clamp per kind. Keeping the table here means the
numbers can be re-tuned in one place and the 48 defs re-emitted, instead of 48 XML blocks
drifting apart. The design lives in the doc; the STRINGS are the build.

🔴 WHY IT EXISTS AT ALL. Measured 2026-08-19: four factions field combat groups made of
SPECIES SAMPLERS - `isFighter: false`, `combatPower: 40`, `weaponMoney: 0~0` and no
`weaponTags` - so their raids arrive UNARMED. These 48 kinds are the fix (roster R20),
not a refinement.

🔑 EVERY TAG BELOW WAS RESOLVED AGAINST SURVIVING WEAPONS, never invented. The roster
deliberately gives weapon CLASSES and refuses to guess tag strings. Re-check them with
`weapon_tag_audit.py`, which lists every tag the cherrypick emptied - a tag with no
surviving carrier hands the pawn nothing, silently.

⛔ The Predator/Yautja mod is GONE (owner, 2026-08-20). Nothing here may reference it.

⚠️ EVERY defName HERE WAS LOOKED UP, NOT GUESSED. Two apparel names in the first draft
were plausible inventions - `OuterRim_ImperialArmourStormtrooper` and
`guy762_HvyArmor_mandalorian` - and neither existed. `apparelRequired` naming a def that
does not exist is a load-time cross-reference error, so a guess here is loud rather than
silent; the weapon tags above are the opposite and fail in silence. Check both.
"""
from __future__ import annotations
import sys
from pathlib import Path

OUT = Path("src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml")

# (faction, role) -> (race ThingDef, owning packageId for MayRequire)
#
# 🔴 A KIND WITH NO ENTRY HERE IS `Human` AND `useFactionXenotypes true`, which is the
# roster's whole design: one kind spawns the faction's species MIX. An entry here opts a
# kind OUT of that, and is only correct when the kind is not a person.
#
# DROID_RACES_APPLIED_TO_KINDS_1, executing DECIDE's ruling in DROID_KINDS_NEED_A_RACE_1.
# The four Jawa_Droid_* kinds declared <race>Human</race> against Jawa_FreeDroidEnclaves'
# deliberately EMPTY xenotypeSet, so the faction fielded Baseliner 4-of-4 - baseline humans
# walking out of an enclave of freed droids.
#
# ⛔ `useFactionXenotypes` is forced FALSE for these. A xenotype is a Human-race concept;
# with a droid race the field asks the faction for something the race cannot wear.
#
# ⛔ NO BATTLE DROIDS. B1, B2, BX Commando and MagnaGuard read as *Separatist army*; this
# faction is an enclave of FREED droids and its roster reads as what its members were built
# for and escaped from. Two of the four are already fielded by the faction's Trader group.
#
# ⚠️ Jawa_Droid_Specialist is labelled "medical droid" and gets a PROTOCOL chassis because
# there is no medical droid in the Humanlike set - 2-1B and FX have no Humanlike ThingDef in
# this stack. Protocol is the nearest attendant silhouette. Flagged, not buried.
#
# All four measured present in OFFICIAL-2026-08-21 (defs.sqlite, 578 mods): intelligence
# Humanlike, race.body OuterRim_HumanoidDroid, thinkTreeMain Humanlike, one lifeStageAges
# entry each - a single adult stage, so no droid children. That is correct, not a defect.
# 🔴 KINDS THE TABLE CANNOT EXPRESS, CARRIED VERBATIM. Emitted after the 48.
#
# ⚠️ THIS EXISTS BECAUSE REGENERATING SILENTLY DELETED ONE. Measured 2026-08-21: the
# committed XML held 49 PawnKindDefs and this generator emits 48. The odd one out was
# `Jawa_Homestead_DesertRanger` — hand-added to the OUTPUT after an owner ruling, with
# thirty lines of provenance the table has nowhere to put. Re-running the generator
# removed it and its comment, and nothing said so: `wrote … 48 pawn kinds` reads
# identically whether or not a def just died. A count is not a roster.
#
# ⇒ Anything hand-added to the output goes HERE, verbatim, or the next regeneration
# eats it. ⛔ Do not "clean this up" into the table: the table cannot carry a comment,
# and its combat_power() formula does not reproduce this kind's 62 from its own money
# values (200+240 gives 55/60/63 across the role multipliers). The number was chosen by
# a person. Rebuilding it from the formula would be a silent re-tune.
EXTRAS = """\
  <!-- ⭐ THE DESERT TROOPER — owner, 2026-08-20: "the Homestead Defense League
       absolutely would dress like the desert naturally."

       It began as `OuterRim_RebelDesertTrooper`, asserted as an inventory fact in
       desert_world_design.md:448 and absent from the dump. The Rebel Alliance holds
       none of the 72 settlements, so it could never have spawned there. The Homestead
       Defense League is the right home: 13 settlements, the most on the map, sited on
       "the arable margin of the terminator".

       ⚠️ DRESSED EXPLICITLY, unlike its four siblings, and that is the point of it.
       They leave apparel to `apparelMoney` and take whatever the roll gives; this one
       names duster + headwrap because LOOKING like the desert is the whole brief.
       Both are vanilla `Core` items, so no mod can take them away.

       ⚠️ Outer Rim's own "snow trooper" wears the FOREST set — `RebelForestFatigues`,
       forest poncho, forest helmet. Its biome troopers are name-and-tag reskins, not
       new art, which is the licence to do the same here rather than commission a set.

       ✅ IT SPAWNS AS OF 2026-08-21 === OUTLANDER_GROUPMAKER_PATCH_1, owner:
       "Approved abstract patch." This paragraph used to read "IT DOES NOT SPAWN YET",
       and that is now wrong. `pawnGroupMakers` for this faction does live on the
       ABSTRACT parent `OutlanderFactionBase` and not on `OutlanderCivil` — which is
       exactly why every earlier xpath at `FactionDef[defName="OutlanderCivil"]/
       pawnGroupMakers` matched nothing and logged nothing. The parent is now patched
       ADDITIVELY, by its `Name` attribute, at the end of
       `Patches/HomesteadDefenseLeague.xml`: four new group makers (Combat, Peaceful,
       Trader, Settlement) at commonality 5, which is 4.8% of Outlander groups of each
       kind. All five Homestead kinds are in them; the ranger carries the joint-highest
       weight. If it still never appears, the weight is wrong, not the def. -->
  <PawnKindDef>
    <defName>Jawa_Homestead_DesertRanger</defName>
    <label>dune ranger</label>
    <race>Human</race>
    <defaultFactionDef>OutlanderCivil</defaultFactionDef>
    <combatPower>62</combatPower>
    <isFighter>true</isFighter>
    <useFactionXenotypes>true</useFactionXenotypes>
    <weaponMoney>200~260</weaponMoney>
    <apparelMoney>240~300</apparelMoney>
    <initialResistanceRange>10~16</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>SimpleGun</li>
      <li>KotORRanged_mid</li>
    </weaponTags>
    <apparelRequired>
      <li>Apparel_Duster</li>
      <li>Apparel_Headwrap</li>
    </apparelRequired>
    <apparelAllowHeadgearChance>1</apparelAllowHeadgearChance>
    <maxApparelQuality>Good</maxApparelQuality>
  </PawnKindDef>
"""

DROID_DEPOT = "Neronix17.OuterRim.DroidDepot"
RACES = {
    ("Droid", "Grunt"):      ("OuterRim_ImperialLaborDroid", DROID_DEPOT),
    ("Droid", "Heavy"):      ("OuterRim_KXSecurityDroid",    DROID_DEPOT),
    ("Droid", "Specialist"): ("OuterRim_ProtocolDroid",      DROID_DEPOT),
    ("Droid", "Leader"):     ("OuterRim_SuperTacticalDroid", DROID_DEPOT),
}

# faction -> (FactionDef defName, xenotype-driven?)
FACTIONS = {
    "Empire":     "Empire",
    "Hutt":       "Jawa_HuttCartel",
    "Homestead":  "OutlanderCivil",
    "DeepDesert": "TribeCivil",
    "Droid":      "Jawa_FreeDroidEnclaves",
    "Wildsteam":  "Jawa_WildsteamClan",
    "Deepwater":  "Jawa_DeepwaterCompact",
    "Geonosian":  "Jawa_GeonosianFoundryHive",
    "Helix":      "Jawa_AscendantHelix",
    "Blackstar":  "Pirate",
    "TradeMoot":  "Jawa_IndigenousTribes",
    "Junkers":    "Jawa_Junkers",
}

# 🔴 weaponMoney IS A CEILING, AND A CEILING BELOW THE CHEAPEST WEAPON IN THE POOL ARMS
# NOBODY. RimWorld picks from the tag pool filtered by value <= weaponMoney, so a kind
# whose pool starts at 1,250 and whose money is 200 is as unarmed as one with no tags at
# all - and just as silent about it. Measured 2026-08-20: five kinds were in that state,
# including the Jawa scavenger, whose ion weapons all cost 800+ against a budget of 120.
# ⇒ Every number below has been checked against the CHEAPEST member of its own pool.
#
# 🔴 AND "CEILING" IS ONLY HALF THE RULE. weaponMoney is rolled ONCE and every weapon
# priced at or below that roll is eligible, so:
#     max >= cheapest  ->  the kind CAN arm
#     min >= cheapest  ->  the kind ALWAYS arms
# The roster's acceptance criterion is 5 spawns out of 5 armed, so the bar is the
# SECOND one. The number in each row below IS the min - this file emits `wm ~ wm*1.2` -
# so every wm must sit at or above its pool's cheapest member, with headroom.
# ⚠️ Headroom is not padding: the engine prices a ThingStuffPair, which includes STUFF
# cost, while the audit reads an unstuffed value. The real price is higher, never lower.
#
# ✅ THE AFFORDABILITY PASS NOW EXISTS - it did not when the line below was written:
#     python3 src/RimMandrake/Utils/weapon_affordability.py
# Run it after ANY change to a tag or a number here. It reports every kind as always /
# sometimes / never arming, and it PRICES the Outer Rim weapons, which declare no
# MarketValue at all and are computed by the engine from their recipe.
# (faction, role, label, weaponMoney, apparelMoney, quality, [weaponTags], [apparelRequired])
# quality: ("force",) | ("max", Q) | ("min", Q) | ("item", Q) | None
R = [
 ("Empire","Grunt","stormtrooper",650,500,("force",),["ORImperialStandard","ORImperialLight"],["OuterRim_StormtrooperCuirass","OuterRim_StormtrooperHelmet"]),
 ("Empire","Heavy","heavy trooper",1000,700,("force",),["ORImperialHeavy","ORHeavyWeapon"],["OuterRim_ImperialArmyCuirass","OuterRim_ImperialArmyHelmet","OuterRim_ImperialArmyPauldrons"]),
 ("Empire","Specialist","Imperial officer",900,700,("force",),["ORPistol","ORImperialLight"],["OuterRim_ImperialOfficerUniform","OuterRim_ImperialOfficerCap"]),
 ("Empire","Leader","Emperor Palpatine",1600,1200,("item","Excellent"),["ORImperialSniper","ORPistol"],["OuterRim_ImperialOfficerUniform_Black","OuterRim_ImperialOfficerCap_Black"]),

 ("Hutt","Grunt","Cartel enforcer",200,250,None,["KotORRanged_weak","SWKotORWeaponCategoryTag_pistol"],[]),
 ("Hutt","Heavy","Cartel bodyguard",550,400,None,["KotORRanged_mid","SWKotORWeaponCategoryTag_heavyranged"],[]),
 ("Hutt","Specialist","Cartel factor",800,600,None,["KotORRanged_mid","SWKotORWeaponCategoryTag_pistol"],[]),
 ("Hutt","Leader","Lord Gorga the Immense",13000,2000,("item","Masterwork"),["KotORRanged_legendary","KotORRanged_rare"],[]),

 ("Homestead","Grunt","homestead militia",130,180,("max","Good"),["SimpleGun","KotORRanged_weak"],[]),
 ("Homestead","Heavy","well-guard",300,250,("max","Good"),["AssaultRifle","KotORRanged_mid"],[]),
 ("Homestead","Specialist","water warden",450,300,("max","Good"),["SniperRifle","ORSniper"],[]),
 ("Homestead","Leader","High Marshal Taren Voss",700,500,("max","Excellent"),["ORPistol","SWKotORWeaponCategoryTag_pistol"],[]),

 ("DeepDesert","Grunt","Tusken raider",150,100,("max","Normal"),["ORTuskenMelee","ORMeleeBlunt","NeolithicMeleeAdvanced"],[]),
 ("DeepDesert","Heavy","Tusken brute",200,150,("max","Normal"),["ORMeleeBlunt","NeolithicMeleeAdvanced"],[]),
 ("DeepDesert","Specialist","Tusken marksman",2000,200,("max","Normal"),["SaV_tusken"],[]),
 ("DeepDesert","Leader","War Chief Torr'gan",500,350,("max","Good"),["ORTuskenMelee","NeolithicMeleeAdvanced"],[]),

 ("Droid","Grunt","labour droid",1100,120,None,["ORDroidWeapon"],[]),
 ("Droid","Heavy","security droid",1400,200,None,["ORDroidWeapon"],[]),
 ("Droid","Specialist","medical droid",1200,180,None,["ORDroidWeapon"],[]),
 ("Droid","Leader","First Speaker R-41 Rell",1800,400,("item","Excellent"),["ORDroidWeapon"],[]),

 ("Wildsteam","Grunt","Wildsteam hunter",1300,150,("min","Good"),["KotORBowcaster"],[]),
 ("Wildsteam","Heavy","pod-warden",900,200,("min","Good"),["KotORBowcaster","SWKotORWeaponCategoryTag_heavyranged"],[]),
 ("Wildsteam","Specialist","beast-handler",620,250,("min","Good"),["ORMeleeSharp","ORVibroweapon"],[]),
 ("Wildsteam","Leader","Elder Rroowaak",2100,400,("min","Excellent"),["KotORBowcaster"],[]),

 ("Deepwater","Grunt","shore guard",300,400,("min","Good"),["KotORRanged_mid","SWKotORWeaponCategoryTag_rifle"],[]),
 ("Deepwater","Heavy","pressure trooper",600,550,("min","Good"),["SWKotORWeaponCategoryTag_heavyranged","KotORRanged_strong"],[]),
 ("Deepwater","Specialist","Quarren shipwright",750,650,("min","Good"),["ORVibroweapon","ORMeleeSharp"],[]),
 ("Deepwater","Leader","High Warden Neris Cal",1400,1100,("item","Excellent"),["ORMeleeSharp","KotORRanged_rare"],[]),

 ("Geonosian","Grunt","Geonosian drone",400,60,None,["KotORRanged_sonic"],[]),
 ("Geonosian","Heavy","soldier drone",800,80,None,["KotORRanged_sonic","SWKotORWeaponCategoryTag_heavyranged"],[]),
 ("Geonosian","Specialist","hive overseer",1000,100,None,["KotORRanged_sonic","KotORRanged_rare"],[]),
 ("Geonosian","Leader","Archduke Korrik the Shaper",1500,200,("item","Excellent"),["KotORRanged_sonic","KotORRanged_legendary"],[]),

 ("Helix","Grunt","retrieval agent",600,700,("min","Excellent"),["SWKotORWeaponCategoryTag_pistol","KotORRanged_strong"],[]),
 ("Helix","Heavy","brute-stock labourer",1100,900,("min","Excellent"),["SWKotORWeaponCategoryTag_heavyranged","KotORRanged_strong"],[]),
 ("Helix","Specialist","Helix curator",1400,1100,("min","Excellent"),["KotORRanged_rare","ORSniper"],[]),
 ("Helix","Leader","Director Ko Saiyan",12500,1800,("item","Masterwork"),["KotORRanged_legendary","KotORRanged_rare"],[]),

 ("Blackstar","Grunt","hired gun",400,350,None,["SWKotORWeaponCategoryTag_rifle","SimpleGun"],[]),
 ("Blackstar","Heavy","Mandalorian",700,500,None,["SWKotORWeaponCategoryTag_heavyranged","KotORRanged_strong"],["guy762_MandoArmor_battle","guy762_MandoHelmet_supercom"]),
 ("Blackstar","Specialist","Blackstar hunter",1100,800,None,["ORSniper","KotORRanged_rare"],[]),
 ("Blackstar","Leader","Captain Jaxen Marr",1800,1500,None,["KotORRanged_legendary","ORPistol"],[]),

# 🔑 IONBLASTER_INTO_THE_GENERATOR_1. `JawaIon_Damage` is the campaign's signature weapon
# tag and it is declared HERE on Heavy/Specialist/Leader, not in a patch. It replaced
# `Patches/JawaIon_FieldOurOwnGun.xml`, which was a stopgap and is deleted - a patch that
# adds a tag the generator does not know about drifts the moment this table is re-emitted.
# ⛔ The GRUNT is excluded on purpose: `JawaIon_Blaster` costs 420 against his 250 ceiling,
# so the tag there would be a silent no-op. Same reason his `Jawa_IonWeaponLight` is dead
# weight today - it resolves to `IW_Gun_IonPistol` (800) and `IW_Gun_IonPDW` (1000), both
# far above 250. It is KEPT rather than dropped because it costs nothing at spawn time and
# is the hook a cheap light ion weapon would arrive on; the Jawa's lowest-on-the-map budget
# is a design feature (design/Jawa/mods/required_mods.md), so the ceiling does not move.
# His live pool is `KotORRanged_ion` -> `guy762_ionpistol` at 200, which always arms.
 ("TradeMoot","Grunt","Jawa scavenger",250,100,("max","Poor"),["KotORRanged_ion","SaV_jawaheavy","Jawa_IonWeaponLight"],["guy762_Robes_jawa"]),
 ("TradeMoot","Heavy","crawler guard",450,130,("max","Normal"),["KotORRanged_ion","Jawa_IonWeapon","JawaIon_Damage","KotORRanged_weak"],["guy762_Robes_jawa"]),
 ("TradeMoot","Specialist","Scrap-Singer",900,160,("max","Normal"),["Jawa_IonWeapon","JawaIon_Damage","KotORRanged_ion"],["guy762_Robes_jawa"]),
 ("TradeMoot","Leader","First Bargainer Kiknik the Wealthy",900,250,("max","Good"),["KotORRanged_ion","Jawa_IonWeapon","JawaIon_Damage"],["guy762_Robes_jawa"]),

 ("Junkers","Grunt","Junker scrapper",60,400,("max","Awful"),["ORMeleeBlunt","NeolithicMeleeBasic"],[]),
 ("Junkers","Heavy","warcasket Junker",140,700,None,["SimpleGun","KotORRanged_weak"],["VFEP_WarcasketHelmet_Warcasket"]),
 ("Junkers","Specialist","claim-jumper",200,900,("max","Poor"),["AssaultRifle","KotORRanged_mid"],[]),
 ("Junkers","Leader","Scraplord Tarn Vox the Brutal",350,1400,("item","Masterwork"),["ORMeleeBlunt"],[]),
]

# combatPower FOLLOWS THE MONEY, per the roster's own instruction - a kind is dangerous
# in proportion to what it is carrying. Anchored on vanilla: a Mercenary_Gunner is 90
# at roughly 600 of gear, a Grunt-tier tribal 40 at nearly none.
# 🔴 THE WARCASKET IS THE PAWN, and until 2026-08-20 the Junker heavy asked for no
# apparel at all - no `apparelRequired`, no `apparelTags` - so it drew generic gear and
# the encounter the whole Junker design rests on never happened. The armour existed (55
# surviving pieces), the counter existed (19 vibro weapons), and the two never met.
# `apparelRequired` pins the helmet; the tag brings the matching body plate, because a
# casket is a SET and requiring every piece by name would break the moment VFEP renames one.
# 🔴 THE SILHOUETTE IS THE FACTION, and without this the pool is the whole load set.
# Measured live 2026-08-22 (IMPERIAL_APPAREL_ON_ALL_KINDS_1): `Jawa_Empire_Heavy` and
# `_Specialist` carried neither `apparelRequired` nor any `apparelTags`, so
# PawnApparelGenerator dressed them from all 723 usable apparel defs on a 578-mod list.
# What arrived: `guy762_Clothing_RebelCamoII` and a rebel cap on the heavy, `GS_SandP_Hood`
# (Sandpeople) and `guy762_SithMask_marauder` on the specialist. The faction the guidance
# doc calls "uniform, mass-produced, no personality - you are fighting a supply chain" was
# fielding troops in REBEL CAMOUFLAGE and a TUSKEN HOOD.
# 🔑 Three tags, not one: Outer Rim does NOT put `ImperialApparel` on everything Imperial.
# The army set carries only `ImperialArmy` and the officer set only `ImperialOfficer`, so a
# single-tag pool would silently exclude two of the four kinds' own uniforms.
# ⚠️ `apparelRequired` is generated regardless of this filter and regardless of
# `apparelMoney` - that is why the Grunt's stormtrooper plate has always landed on 4 of 4.
# These tags govern the OTHER slots, which is where the rebel camo was coming from.
APPAREL_TAGS = {
    "Junkers": ["WarcasketAll"],
    "Empire":  ["ImperialApparel", "ImperialArmy", "ImperialOfficer"],
}

RESIST = {"Grunt": (8, 14), "Heavy": (12, 18), "Specialist": (14, 22), "Leader": (20, 30)}
WILL   = {"Grunt": (1, 3),  "Heavy": (2, 4),   "Specialist": (2, 5),   "Leader": (4, 7)}


def combat_power(wm, am, role):
    base = 35 + (wm + am) / 22.0
    return int(round(base * {"Grunt": 1.0, "Heavy": 1.15, "Specialist": 1.1, "Leader": 1.3}[role]))


def emit():
    L = ['<?xml version="1.0" encoding="utf-8"?>', "<!--", __doc__.strip().replace("--", "="),
         "-->", "<Defs>", ""]
    for fac, role, label, wm, am, q, wt, req in R:
        race, pkg = RACES.get((fac, role), ("Human", None))
        # 🔑 MayRequire rides the whole PawnKindDef, not the <race> line. If the race's mod
        # is absent the def must vanish WHOLE - a kind whose <race> node was stripped has no
        # race at all, which is a louder failure than the one being guarded against. The
        # matching guard on the faction's group makers is in JawaFreeDroidEnclaves.xml and
        # the two must move together.
        L += ["  <PawnKindDef%s>" % ('' if pkg is None else ' MayRequire="%s"' % pkg),
              "    <defName>Jawa_%s_%s</defName>" % (fac, role),
              "    <label>%s</label>" % label,
              "    <race>%s</race>" % race,
              "    <defaultFactionDef>%s</defaultFactionDef>" % FACTIONS[fac],
              "    <combatPower>%d</combatPower>" % combat_power(wm, am, role),
              "    <isFighter>%s</isFighter>" % ("false" if not wt else "true"),
              # 🔑 The whole point of the roster: ONE kind spawns the faction's whole
              # species mix wearing that faction's gear, so species never appear in a
              # kind's name and a faction's look is edited in one place.
              "    <useFactionXenotypes>%s</useFactionXenotypes>" % ("true" if race == "Human" else "false"),
              "    <weaponMoney>%d~%d</weaponMoney>" % (wm, int(wm * 1.2)),
              "    <apparelMoney>%d~%d</apparelMoney>" % (am, int(am * 1.2)),
              # 🔴 REQUIRED ON EVERY HUMANLIKE KIND. Omitting them is not fatal but the
              # game logs `initial resistance range is undefined for humanlike pawn kind`
              # and `initial will range is undefined` for EACH one, every load - measured
              # 2026-08-20 as 108 red lines from this file alone. They are what recruiting
              # and enslaving a captured pawn cost, so a kind without them is also
              # meaningless to capture. Scaled by role: a leader is harder to turn.
              "    <initialResistanceRange>%d~%d</initialResistanceRange>" % RESIST[role],
              "    <initialWillRange>%d~%d</initialWillRange>" % WILL[role]]
        if wt:
            L.append("    <weaponTags>")
            L += ["      <li>%s</li>" % t for t in wt]
            L.append("    </weaponTags>")
        if req:
            L.append("    <apparelRequired>")
            L += ["      <li>%s</li>" % r for r in req]
            L.append("    </apparelRequired>")
        if fac in APPAREL_TAGS:
            L.append("    <apparelTags>")
            L += ["      <li>%s</li>" % t for t in APPAREL_TAGS[fac]]
            L.append("    </apparelTags>")
        if q:
            if q[0] == "force":
                L.append("    <forceNormalGearQuality>true</forceNormalGearQuality>")
            elif q[0] == "max":
                L.append("    <maxApparelQuality>%s</maxApparelQuality>" % q[1])
            elif q[0] == "min":
                L.append("    <minApparelQuality>%s</minApparelQuality>" % q[1])
            else:
                L.append("    <itemQuality>%s</itemQuality>" % q[1])
        L += ["  </PawnKindDef>", ""]
    L += [EXTRAS, ""]
    L += ["</Defs>", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    return len(R) + EXTRAS.count("<PawnKindDef")


if __name__ == "__main__":
    n = emit()
    print("wrote %s - %d pawn kinds" % (OUT, n))
    sys.exit(0)
