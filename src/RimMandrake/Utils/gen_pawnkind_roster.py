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
      <!-- settlers and salvagers - modest, practical, a little cash -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>6~15</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>15~45</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Good'. Settlers keep decent kit but nothing exquisite. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>
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
 # 🔴 BUDGETS RAISED 2026-08-23 on the owner's ruling. MEASURED: these two kinds could
 # afford NOTHING their tags named — Specialist 1320 against KotORRanged_rare whose
 # cheapest survivor is 12799, Leader 2160 against KotORRanged_legendary at 12000. Nothing
 # was cut; the tiers are simply ~10x a mid-tier budget, so the pool resolved empty and the
 # pawn rolled bare. Asked whether to repoint the tags or raise the budgets, the owner
 # chose RAISE. ⚠️ combatPower is derived from these numbers, so raiding difficulty and
 # drop value both go up deliberately. BLACKSTAR_DEEPDESERT_POOLS_EMPTY_1.
 ("Blackstar","Specialist","Blackstar hunter",12800,800,None,["ORSniper","KotORRanged_rare"],[]),
 ("Blackstar","Leader","Captain Jaxen Marr",14600,1500,None,["KotORRanged_legendary","ORPistol"],[]),

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
# 🔴 `PrestigeCombatGear` REMOVED from all four Ascendant Helix kinds, 2026-08-27, BUILD.
# It is the one apparel tag in this file whose pool contains NO Star Wars content at all.
# Measured against the live 582-mod capture, all 22 carriers:
#     AG_Forsaken* (7, Alpha Genes)  ·  AM_*Mechlord/MechBreaker/MechCommander* (6, Alpha
#     Mechs)  ·  BMT_Apparel_Armor*phractPrestige (5, Biomes! Caverns beetle chitin)  ·
#     VQE_Crypto* (4, Vanilla Quests Cryptoforge)
# ⇒ It dressed an Arkanian ultratech faction in beetle chitin and Forsaken cloaks. This is
# `faction_equipment_clusters.md` R4, which measured it on 2026-08-22 and was never acted on.
# ✅ No kind is stranded: every Helix kind keeps `KotORArmor_mid` (20 carriers) and/or
# `KotORArmor_heavy` (16), which is the "merc composite, top tier" the design asked for.
# 🔑 The rule this enforces is the design's own: pick a tag by WHAT CARRIES IT, never by
# what its name sounds like.

APPAREL_TAGS = {
    "Junkers": ["WarcasketAll"],
    "Empire":  ["ImperialApparel", "ImperialArmy", "ImperialOfficer"],
}

# 🔴 EMPIRE_BLACKSTAR_ALWAYS_WILLING_1. DECIDE ruled 2026-08-22 that a pacifist pawn is
# acceptable from ten of the twelve factions and unacceptable from these two: the Empire is
# a supply chain and Blackstar is a contract house, and neither sends someone who will not
# fight. ⛔ The other ten keep their pacifist rolls - DECIDE called that wanted texture and
# narrowing it a regression.
#
# 🔑 `requiredWorkTags` is the VANILLA mechanism and not an invention: 143 kinds in the live
# 578-mod set already carry it, including Core's own `AncientSoldier`, `Tribal_Archer` and
# `Tribal_Warrior`. `PawnGenerator` rejects and re-rolls a pawn whose disabled work tags
# intersect it - "Generated pawn with disabled requiredWorkTags" - which is a harder
# guarantee than a backstory filter, because it catches a trait or a gene that disables
# violence as well as a backstory.
# ⚠️ It is also NOT redundant with the raid path. `PawnGroupKindWorker_Normal` already
# passes `mustBeCapableOfViolence: true`, so a pawn arriving in a RAID was already covered;
# what was not covered is every other route these kinds reach the map by - a dev spawn, a
# quest, a settlement roster, an inhabited map - and that is where the 5-in-20 was measured.
REQUIRE_VIOLENT = {"Empire", "Blackstar"}

RESIST = {"Grunt": (8, 14), "Heavy": (12, 18), "Specialist": (14, 22), "Leader": (20, 30)}
WILL   = {"Grunt": (1, 3),  "Heavy": (2, 4),   "Specialist": (2, 5),   "Leader": (4, 7)}


# ⭐ combatPower is DERIVED from weaponMoney and STAYS derived — owner's ruling
# 2026-08-23, made with the numbers in front of him.
#
# BUILD clamped these two by hand first, on the reasoning that a 12,800-silver KotOR
# pistol is RARE rather than ten times deadlier, and that RimWorld sizes a raid by
# summing combatPower — so the derived 718/997 would make Blackstar arrive as one or
# two pawns instead of a syndicate. That reasoning was put to the owner and he chose
# THE DIFFICULTY JUMP: Blackstar becomes a small elite strike force with legendary
# weapons and a much richer drop, not a crowd.
#
# ⇒ The clamp is GONE. If Blackstar raids start arriving as a duo, that is the
# intended shape and not a regression — do not "fix" it back.
COMBAT_POWER_OVERRIDE = {}


def combat_power(wm, am, role, fac=None):
    if (fac, role) in COMBAT_POWER_OVERRIDE:
        return COMBAT_POWER_OVERRIDE[(fac, role)]
    base = 35 + (wm + am) / 22.0
    return int(round(base * {"Grunt": 1.0, "Heavy": 1.15, "Specialist": 1.1, "Leader": 1.3}[role]))



# ============================================================================
# THE CURATED KIT — PAWNKIND_GENERATOR_DIVERGED_1, reconciled 2026-08-23
# ============================================================================
#
# 🔴 WHY THIS TABLE EXISTS. This generator wrote JawaFactionRoster.xml on
# 2026-08-20 and the file was then HAND-EDITED for three days — the whole
# faction equipment layer: apparel clusters, wealth tiers, quality clamps, item
# kits, faction colours, cross-faction taboos, and the stormtrooper lockdown.
# The generator never heard of any of it. MEASURED 2026-08-23: running it
# reverted weaponMoney 950~1150 -> 650~780 (below the 906 that every
# ORImperialStandard rifle costs, so stormtroopers silently went back to
# PISTOLS), widened apparelTags from 3 carriers to 21, and deleted
# forceNormalGearQuality, inventoryOptions and apparelDisallowTags outright.
# It reported success. Nothing warned.
#
# ⭐ OWNER'S RULING, 2026-08-23: GENERATOR WINS. So the curation was ported in
# here rather than the header being softened or the write path retired.
#
# 🔑 THE SPLIT, and it is the point:
#     the GENERATOR computes  — defName, label, race, defaultFactionDef,
#                               combatPower, isFighter, useFactionXenotypes.
#                               Mechanical, derivable, and safe to recompute.
#     this TABLE carries      — everything from <weaponMoney> onward, verbatim,
#                               plus each kind's explanatory comment block.
#                               Curated, argued-over, and NOT derivable.
#
# ⇒ Regenerating is now a NO-OP DIFF, which is the only definition of "the
# header is true" that survives contact with anyone. Verify it that way:
#     python3 src/RimMandrake/Utils/gen_pawnkind_roster.py
#     git diff --stat src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml
# Empty means true. Anything else means this table has drifted again.
#
# ⚠️ EDIT THE KIT HERE, not in the XML. An edit to the XML is reverted by the
# next run, exactly as before — the trap is fixed, not removed.
# ============================================================================

KIT_PRE = {
 'Jawa_DeepDesert_Specialist': """  <!-- 🔴 REVERTED 2026-08-23. I cut this to 400~500 as 'a Tusken outspending a stormtrooper'.
         Wrong: SaV_tusken holds exactly 2 weapons, both the Tusken slugrifle at 1977.
         The budget was sized to the signature weapon; below it the kind is bare-handed. -->
""",
 'Jawa_Empire_Grunt': """  <!-- STORMTROOPER, and the owner's hard requirement: shiny new stormtrooper armour and
         NOTHING else, with a proper blaster.
         🔴 weaponMoney was 650~780 and EVERY rifle in ORImperialStandard costs 906 -
         E-11, DLT-20A and E-22 alike - so the roll could never afford one and always
         fell back to ORImperialLight, which is PISTOLS. Stormtroopers were carrying
         sidearms. Raised to 950~1150 and ORImperialLight dropped: the three rifles
         left are all canon-correct and all now reachable.
         🔴 apparelTags was ImperialApparel, which has 21 carriers including SNOWTROOPER,
         SCOUT, RANGE, DEATH TROOPER and ISB pieces. The required cuirass and helmet
         fill Torso and FullHead, but Shoulders was free, so a stormtrooper could take
         the field in Scout Trooper pauldrons. Narrowed to ImperialStormtrooper (3
         carriers: cuirass, helmet, pauldrons) and the rest hard-refused below. -->
""",
 'Jawa_Empire_Heavy': """  <!-- Imperial ARMY trooper - army plate only, never stormtrooper white or an officer's cap. -->
""",
 'Jawa_Empire_Leader': """  <!-- senior officer, black uniform. Officer wardrobe only. -->
""",
 'Jawa_Empire_Specialist': """  <!-- Imperial officer - uniform and cap only. -->
""",
 'Jawa_Helix_Leader': """  <!-- 🔴 REVERTED 2026-08-23. Cut to 4000~5000; KotORRanged_legendary/rare start at 12000, so
         the cut left the Helix boss unarmed. Owner: Helix are VERY wealthy - this is what
         very wealthy costs in this stack. -->
""",
 'Jawa_Homestead_DesertRanger': """  <!-- ⭐ THE DESERT TROOPER — owner, 2026-08-20: "the Homestead Defense League
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
""",
 'Jawa_Hutt_Leader': """  <!-- 🔴 REVERTED 2026-08-23. Cut to 3000~3600 as 'not intermediate'; the legendary tier starts
         at 12000 and the cut disarmed him. The FACTION is intermediate - its Grunts run
         200~240 - but a Hutt crime boss carrying one ostentatious 12000-credit blaster is
         the character, not a contradiction. -->
""",
 'Jawa_Junkers_Heavy': """  <!-- owner 2026-08-23: 'Heavy junkers should be required to be in warcaskets of course.'
         🔴 This required the HELMET ONLY - a warcasket head over ordinary clothes.
         Body (341) and shoulders (81) added, so the suit is a suit. Base Warcasket
         tier, which is the scrapper's own, not a veteran suit. -->
""",
 'Jawa_Junkers_Leader': """  <!-- the Junker boss is also cased. Same base tier - Junkers are not rich, they are
         merely armoured, which is the whole character of the faction. -->
""",
 'Jawa_Wildsteam_Grunt': """  <!-- 🔴 REVERTED 2026-08-23. Cut to 500~600; the bowcaster costs 1250 and KotORBowcaster is
         this kind's only tag. The Grunt/Heavy inversion is real but the fix is to raise
         the HEAVY, not to strand the Grunt below its own weapon. -->
""",
 'Jawa_Wildsteam_Heavy': """  <!-- raised above the Grunt to restore the ladder - and 2000 reaches the war bowcaster. -->
""",
}

KIT = {
 'Jawa_Empire_Grunt': """    <weaponMoney>950~1150</weaponMoney>
    <apparelMoney>900~1100</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>ORImperialStandard</li>
    </weaponTags>
    <apparelRequired>
      <li>OuterRim_StormtrooperCuirass</li>
      <li>OuterRim_StormtrooperHelmet</li>
    </apparelRequired>
    <requiredWorkTags>Violent</requiredWorkTags>
    <apparelTags>
      <li>ImperialStormtrooper</li>
    </apparelTags>
    <forceNormalGearQuality>true</forceNormalGearQuality>
      <!-- issued kit only. An imperial trooper carries what the quartermaster gave him -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <apparelDisallowTags>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialSpecialist</li>
      <li>ImperialScout</li>
      <li>ImperialDeathTrooper</li>
      <li>ImperialArmyFatigues</li>
      <li>ImperialJumpsuit</li>
    </apparelDisallowTags>
    <minApparelQuality>Normal</minApparelQuality>
    <!-- 🔑 PURE WHITE IS THE ENGINE'S 'DO NOT TINT' SENTINEL, and that is why it is exact.
         PawnApparelGenerator.cs:828 reads `if (pawn.kindDef.apparelColor != Color.white)`
         before calling SetColor - so (255,255,255) skips tinting ENTIRELY and every piece
         keeps its own painted texture. Stormtrooper plate is white because the ART is
         white, not because we dyed it. Owner, 2026-08-23: 'make the stormtrooper armor
         not colorable (fixed at white)'. This is that, without removing a comp.
         ⚠️ It was (250,250,250), which is NOT Color.white and therefore DID tint. -->
    <apparelColor>(255,255,255)</apparelColor>""",
 'Jawa_Empire_Heavy': """    <weaponMoney>1000~1200</weaponMoney>
    <apparelMoney>1100~1300</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>ORImperialHeavy</li>
      <li>ORHeavyWeapon</li>
    </weaponTags>
    <apparelRequired>
      <li>OuterRim_ImperialArmyCuirass</li>
      <li>OuterRim_ImperialArmyHelmet</li>
      <li>OuterRim_ImperialArmyPauldrons</li>
    </apparelRequired>
    <requiredWorkTags>Violent</requiredWorkTags>
    <apparelTags>
      <li>ImperialArmy</li>
    </apparelTags>
    <forceNormalGearQuality>true</forceNormalGearQuality>
      <!-- issued kit only. An imperial trooper carries what the quartermaster gave him -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <apparelDisallowTags>
      <li>ImperialStormtrooper</li>
      <li>ImperialOfficer</li>
      <li>ImperialSpecialist</li>
      <li>ImperialScout</li>
      <li>ImperialDeathTrooper</li>
    </apparelDisallowTags>
    <minApparelQuality>Normal</minApparelQuality>
    <!-- dark grey-olive - owner: 'the favored color the dark grey-olive or near black for
         everything else. That's the closest match to lore.' Imperial Army, not stormtrooper. -->
    <apparelColor>(86,90,78)</apparelColor>""",
 'Jawa_Empire_Specialist': """    <weaponMoney>900~1080</weaponMoney>
    <apparelMoney>1000~1200</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>ORPistol</li>
      <li>ORImperialLight</li>
    </weaponTags>
    <apparelRequired>
      <li>OuterRim_ImperialOfficerUniform</li>
      <li>OuterRim_ImperialOfficerCap</li>
    </apparelRequired>
    <requiredWorkTags>Violent</requiredWorkTags>
    <apparelTags>
      <li>ImperialOfficer</li>
    </apparelTags>
    <forceNormalGearQuality>true</forceNormalGearQuality>
      <!-- issued kit only. An imperial trooper carries what the quartermaster gave him -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <apparelDisallowTags>
      <li>ImperialStormtrooper</li>
      <li>ImperialArmy</li>
      <li>ImperialScout</li>
      <li>ImperialDeathTrooper</li>
    </apparelDisallowTags>
    <minApparelQuality>Normal</minApparelQuality>
    <!-- dark grey-olive - the Imperial officer's uniform colour. -->
    <apparelColor>(86,90,78)</apparelColor>""",
 'Jawa_Empire_Leader': """    <weaponMoney>1600~1920</weaponMoney>
    <apparelMoney>2000~2400</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>ORImperialSniper</li>
      <li>ORPistol</li>
    </weaponTags>
    <apparelRequired>
      <li>OuterRim_ImperialOfficerUniform_Black</li>
      <li>OuterRim_ImperialOfficerCap_Black</li>
    </apparelRequired>
    <requiredWorkTags>Violent</requiredWorkTags>
    <apparelTags>
      <li>ImperialOfficer</li>
    </apparelTags>
    <itemQuality>Excellent</itemQuality>
      <!-- issued kit only. An imperial trooper carries what the quartermaster gave him -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <apparelDisallowTags>
      <li>ImperialStormtrooper</li>
      <li>ImperialArmy</li>
      <li>ImperialScout</li>
      <li>ImperialDeathTrooper</li>
    </apparelDisallowTags>
    <minApparelQuality>Excellent</minApparelQuality>
    <!-- near-black - the senior officer already wears the _Black uniform and cap; the tint
         deepens it rather than fighting it. -->
    <apparelColor>(42,44,40)</apparelColor>""",
 'Jawa_Hutt_Grunt': """    <weaponMoney>200~240</weaponMoney>
    <apparelMoney>250~300</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>KotORRanged_weak</li>
      <li>SWKotORWeaponCategoryTag_pistol</li>
    </weaponTags>
      <apparelTags>
      <li>SaV_apparel_huttgoon</li>
      <li>KotORArmor_mid</li>
      <li>SaV_apparel_thug</li>
    </apparelTags>
      <!-- cartel vice and portable wealth - the richest and least disciplined roster -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>SmokeleafJoint</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Yayo</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Flake</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Ambrosia</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>40~120</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>2~8</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Hutt_Heavy': """    <weaponMoney>550~660</weaponMoney>
    <apparelMoney>400~480</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>KotORRanged_mid</li>
      <li>SWKotORWeaponCategoryTag_heavyranged</li>
    </weaponTags>
      <apparelTags>
      <li>SaV_apparel_huttgoon</li>
      <li>KotORArmor_mid</li>
      <li>SaV_apparel_thug</li>
    </apparelTags>
      <!-- cartel vice and portable wealth - the richest and least disciplined roster -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>SmokeleafJoint</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Yayo</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Flake</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Ambrosia</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>40~120</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>2~8</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Hutt_Specialist': """    <weaponMoney>800~960</weaponMoney>
    <apparelMoney>600~720</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>KotORRanged_mid</li>
      <li>SWKotORWeaponCategoryTag_pistol</li>
    </weaponTags>
      <apparelTags>
      <li>SaV_apparel_huttgoon</li>
      <li>KotORArmor_mid</li>
      <li>SaV_apparel_thug</li>
    </apparelTags>
      <!-- cartel vice and portable wealth - the richest and least disciplined roster -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>SmokeleafJoint</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Yayo</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Flake</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Ambrosia</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>40~120</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>2~8</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Hutt_Leader': """    <weaponMoney>12000~15600</weaponMoney>
    <apparelMoney>2000~2400</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>KotORRanged_legendary</li>
      <li>KotORRanged_rare</li>
    </weaponTags>
    <itemQuality>Masterwork</itemQuality>
      <apparelTags>
      <li>SaV_apparel_huttgoon</li>
      <li>KotORArmor_mid</li>
      <li>Royal</li>
    </apparelTags>
      <!-- cartel vice and portable wealth - the richest and least disciplined roster -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>SmokeleafJoint</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Yayo</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Flake</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>Ambrosia</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>40~120</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>2~8</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>10~30</countRange></li>
        <li><thingDef>Luciferium</thingDef><countRange>1~3</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Homestead_Grunt': """    <weaponMoney>130~156</weaponMoney>
    <apparelMoney>180~216</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>SimpleGun</li>
      <li>KotORRanged_weak</li>
    </weaponTags>
    <maxApparelQuality>Good</maxApparelQuality>
      <apparelTags>
      <li>Outlander</li>
      <li>Western</li>
      <li>ORScrapper</li>
      <li>KotORClothing_civilian_villager</li>
    </apparelTags>
      <!-- settlers and salvagers - modest, practical, a little cash -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>6~15</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>15~45</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Good'. Settlers keep decent kit but nothing exquisite. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Homestead_Heavy': """    <weaponMoney>300~360</weaponMoney>
    <apparelMoney>250~300</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>AssaultRifle</li>
      <li>KotORRanged_mid</li>
    </weaponTags>
    <maxApparelQuality>Good</maxApparelQuality>
      <apparelTags>
      <li>Outlander</li>
      <li>Western</li>
      <li>ORScrapper</li>
      <li>KotORClothing_civilian_villager</li>
    </apparelTags>
      <!-- settlers and salvagers - modest, practical, a little cash -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>6~15</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>15~45</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Good'. Settlers keep decent kit but nothing exquisite. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Homestead_Specialist': """    <weaponMoney>450~540</weaponMoney>
    <apparelMoney>300~360</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>SniperRifle</li>
      <li>ORSniper</li>
    </weaponTags>
    <maxApparelQuality>Good</maxApparelQuality>
      <apparelTags>
      <li>Outlander</li>
      <li>Western</li>
      <li>ORScrapper</li>
      <li>KotORClothing_civilian_villager</li>
    </apparelTags>
      <!-- settlers and salvagers - modest, practical, a little cash -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>6~15</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>15~45</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Good'. Settlers keep decent kit but nothing exquisite. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Homestead_Leader': """    <weaponMoney>700~840</weaponMoney>
    <apparelMoney>500~600</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>ORPistol</li>
      <li>SWKotORWeaponCategoryTag_pistol</li>
    </weaponTags>
    <maxApparelQuality>Excellent</maxApparelQuality>
      <apparelTags>
      <li>Outlander</li>
      <li>Western</li>
      <li>ORScrapper</li>
      <li>KotORClothing_civilian_villager</li>
    </apparelTags>
      <!-- settlers and salvagers - modest, practical, a little cash -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>6~15</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>15~45</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Good'. Settlers keep decent kit but nothing exquisite. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_DeepDesert_Grunt': """    <weaponMoney>150~180</weaponMoney>
    <apparelMoney>100~120</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>ORTuskenMelee</li>
      <li>ORMeleeBlunt</li>
      <li>NeolithicMeleeAdvanced</li>
    </weaponTags>
    <maxApparelQuality>Normal</maxApparelQuality>
      <apparelTags>
      <li>ORTusken</li>
      <li>SaV_apparel_tusken</li>
    </apparelTags>
      <!-- Tusken: no industry, herbal medicine and dried meat, jade as portable wealth -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>10~25</countRange></li>
        <li><thingDef>Jade</thingDef><countRange>1~4</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty sandy tan — owner. Tusken, sand-coloured by living in it -->
    <apparelColor>(186,163,122)</apparelColor>
      <!-- design: 'max Normal'. No quality clamp on the weapon itself - a scavenged rifle is
         whatever it was when they found it. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_DeepDesert_Heavy': """    <weaponMoney>200~240</weaponMoney>
    <apparelMoney>150~180</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>ORMeleeBlunt</li>
      <li>NeolithicMeleeAdvanced</li>
    </weaponTags>
    <maxApparelQuality>Normal</maxApparelQuality>
      <apparelTags>
      <li>ORTusken</li>
      <li>SaV_apparel_tusken</li>
    </apparelTags>
      <!-- Tusken: no industry, herbal medicine and dried meat, jade as portable wealth -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>10~25</countRange></li>
        <li><thingDef>Jade</thingDef><countRange>1~4</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty sandy tan — owner. Tusken, sand-coloured by living in it -->
    <apparelColor>(186,163,122)</apparelColor>
      <!-- design: 'max Normal'. No quality clamp on the weapon itself - a scavenged rifle is
         whatever it was when they found it. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_DeepDesert_Specialist': """    <weaponMoney>2000~2400</weaponMoney>
    <apparelMoney>200~240</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>SaV_tusken</li>
    </weaponTags>
    <maxApparelQuality>Normal</maxApparelQuality>
      <apparelTags>
      <li>ORTusken</li>
      <li>SaV_apparel_tusken</li>
    </apparelTags>
      <!-- Tusken: no industry, herbal medicine and dried meat, jade as portable wealth -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>10~25</countRange></li>
        <li><thingDef>Jade</thingDef><countRange>1~4</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty sandy tan — owner. Tusken, sand-coloured by living in it -->
    <apparelColor>(186,163,122)</apparelColor>
      <!-- design: 'max Normal'. No quality clamp on the weapon itself - a scavenged rifle is
         whatever it was when they found it. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_DeepDesert_Leader': """    <weaponMoney>500~600</weaponMoney>
    <apparelMoney>350~420</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>ORTuskenMelee</li>
      <li>NeolithicMeleeAdvanced</li>
    </weaponTags>
    <maxApparelQuality>Good</maxApparelQuality>
      <apparelTags>
      <li>ORTusken</li>
      <li>SaV_apparel_tusken</li>
    </apparelTags>
      <!-- Tusken: no industry, herbal medicine and dried meat, jade as portable wealth -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>10~25</countRange></li>
        <li><thingDef>Jade</thingDef><countRange>1~4</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty sandy tan — owner. Tusken, sand-coloured by living in it -->
    <apparelColor>(186,163,122)</apparelColor>
      <!-- design: 'max Normal'. No quality clamp on the weapon itself - a scavenged rifle is
         whatever it was when they found it. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Droid_Grunt': """    <weaponMoney>1100~1320</weaponMoney>
    <apparelMoney>180~216</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>ORDroidWeapon</li>
    </weaponTags>
      <apparelTags>
      <li>KotORDroidArmorT1</li>
      <li>DroidArmor</li>
    </apparelTags>
      <!-- droids need parts and fuel, never food or medicine -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>10~30</countRange></li>
        <li><thingDef>OuterRim_ComponentHypertech</thingDef><countRange>1~1</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- oxidised bronze — owner. Droids should read as MADE, not dressed; bronze also keeps them distinct from the Junkers' rust -->
    <apparelColor>(122,110,84)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Droid_Heavy': """    <weaponMoney>1400~1680</weaponMoney>
    <apparelMoney>200~240</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>ORDroidWeapon</li>
    </weaponTags>
      <apparelTags>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT1</li>
      <li>DroidArmor</li>
    </apparelTags>
      <!-- droids need parts and fuel, never food or medicine -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>10~30</countRange></li>
        <li><thingDef>OuterRim_ComponentHypertech</thingDef><countRange>1~1</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- oxidised bronze — owner. Droids should read as MADE, not dressed; bronze also keeps them distinct from the Junkers' rust -->
    <apparelColor>(122,110,84)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Droid_Specialist': """    <weaponMoney>1200~1440</weaponMoney>
    <apparelMoney>180~216</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>ORDroidWeapon</li>
    </weaponTags>
      <apparelTags>
      <li>KotORDroidArmorT1</li>
      <li>DroidArmor</li>
    </apparelTags>
      <!-- droids need parts and fuel, never food or medicine -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>10~30</countRange></li>
        <li><thingDef>OuterRim_ComponentHypertech</thingDef><countRange>1~1</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- oxidised bronze — owner. Droids should read as MADE, not dressed; bronze also keeps them distinct from the Junkers' rust -->
    <apparelColor>(122,110,84)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Droid_Leader': """    <weaponMoney>1800~2160</weaponMoney>
    <apparelMoney>600~720</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>ORDroidWeapon</li>
    </weaponTags>
    <itemQuality>Excellent</itemQuality>
      <apparelTags>
      <li>KotORDroidArmorT3</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT1</li>
      <li>DroidArmor</li>
    </apparelTags>
      <!-- droids need parts and fuel, never food or medicine -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>10~30</countRange></li>
        <li><thingDef>OuterRim_ComponentHypertech</thingDef><countRange>1~1</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- oxidised bronze — owner. Droids should read as MADE, not dressed; bronze also keeps them distinct from the Junkers' rust -->
    <apparelColor>(122,110,84)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Wildsteam_Grunt': """    <weaponMoney>1300~1560</weaponMoney>
    <apparelMoney>150~180</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>KotORBowcaster</li>
    </weaponTags>
    <minApparelQuality>Good</minApparelQuality>
      <apparelTags>
      <li>ORBoneArmour</li>
      <li>ORChitinArmour</li>
      <li>Neolithic</li>
    </apparelTags>
      <!-- tribal steam-tech: hides and herbs, plus fuel for the boilers -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>WoodLog</thingDef><countRange>10~25</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark green — owner. Tribal hides and boiler grime -->
    <apparelColor>(52,72,45)</apparelColor>
      <!-- design: 'min Good - few weapons, each old and well-made'. A forged culture keeps a
         small number of good things rather than many poor ones. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <itemQuality>Good</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Wildsteam_Heavy': """    <weaponMoney>1700~2000</weaponMoney>
    <apparelMoney>200~240</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>KotORBowcaster</li>
      <li>SWKotORWeaponCategoryTag_heavyranged</li>
    </weaponTags>
    <minApparelQuality>Good</minApparelQuality>
      <apparelTags>
      <li>ORBoneArmour</li>
      <li>ORChitinArmour</li>
      <li>Neolithic</li>
    </apparelTags>
      <!-- tribal steam-tech: hides and herbs, plus fuel for the boilers -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>WoodLog</thingDef><countRange>10~25</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark green — owner. Tribal hides and boiler grime -->
    <apparelColor>(52,72,45)</apparelColor>
      <!-- design: 'min Good - few weapons, each old and well-made'. A forged culture keeps a
         small number of good things rather than many poor ones. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <itemQuality>Good</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Wildsteam_Specialist': """    <weaponMoney>620~744</weaponMoney>
    <apparelMoney>250~300</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>ORMeleeSharp</li>
      <li>ORVibroweapon</li>
    </weaponTags>
    <minApparelQuality>Good</minApparelQuality>
      <apparelTags>
      <li>ORBoneArmour</li>
      <li>ORChitinArmour</li>
      <li>Neolithic</li>
    </apparelTags>
      <!-- tribal steam-tech: hides and herbs, plus fuel for the boilers -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>WoodLog</thingDef><countRange>10~25</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark green — owner. Tribal hides and boiler grime -->
    <apparelColor>(52,72,45)</apparelColor>
      <!-- design: 'min Good - few weapons, each old and well-made'. A forged culture keeps a
         small number of good things rather than many poor ones. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <itemQuality>Good</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Wildsteam_Leader': """    <weaponMoney>1600~1920</weaponMoney>
    <apparelMoney>400~480</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>KotORBowcaster</li>
    </weaponTags>
    <minApparelQuality>Excellent</minApparelQuality>
      <apparelTags>
      <li>ORBoneArmour</li>
      <li>ORChitinArmour</li>
      <li>Neolithic</li>
    </apparelTags>
      <!-- tribal steam-tech: hides and herbs, plus fuel for the boilers -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>Chemfuel</thingDef><countRange>8~20</countRange></li>
        <li><thingDef>WoodLog</thingDef><countRange>10~25</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark green — owner. Tribal hides and boiler grime -->
    <apparelColor>(52,72,45)</apparelColor>
      <!-- design: 'min Good - few weapons, each old and well-made'. A forged culture keeps a
         small number of good things rather than many poor ones. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <itemQuality>Good</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Deepwater_Grunt': """    <weaponMoney>300~360</weaponMoney>
    <apparelMoney>400~480</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>KotORRanged_mid</li>
      <li>SWKotORWeaponCategoryTag_rifle</li>
    </weaponTags>
    <minApparelQuality>Good</minApparelQuality>
      <apparelTags>
      <li>EVA</li>
      <li>Vacsuit</li>
      <li>KotORHeadband_gasmask</li>
    </apparelTags>
      <!-- sealed-suit divers carry rations and real medicine, not herbs -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark teal — owner. Deep water, sealed suits -->
    <apparelColor>(38,74,74)</apparelColor>
      <!-- design: 'min Good'. Sealed-suit divers maintain their kit because failure drowns them. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <itemQuality>Good</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Deepwater_Heavy': """    <weaponMoney>600~720</weaponMoney>
    <apparelMoney>550~660</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>SWKotORWeaponCategoryTag_heavyranged</li>
      <li>KotORRanged_strong</li>
    </weaponTags>
    <minApparelQuality>Good</minApparelQuality>
      <apparelTags>
      <li>EVA</li>
      <li>Vacsuit</li>
      <li>KotORHeadband_gasmask</li>
    </apparelTags>
      <!-- sealed-suit divers carry rations and real medicine, not herbs -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark teal — owner. Deep water, sealed suits -->
    <apparelColor>(38,74,74)</apparelColor>
      <!-- design: 'min Good'. Sealed-suit divers maintain their kit because failure drowns them. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <itemQuality>Good</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Deepwater_Specialist': """    <weaponMoney>750~900</weaponMoney>
    <apparelMoney>650~780</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>ORVibroweapon</li>
      <li>ORMeleeSharp</li>
    </weaponTags>
    <minApparelQuality>Good</minApparelQuality>
      <apparelTags>
      <li>EVA</li>
      <li>Vacsuit</li>
      <li>KotORHeadband_gasmask</li>
    </apparelTags>
      <!-- sealed-suit divers carry rations and real medicine, not herbs -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark teal — owner. Deep water, sealed suits -->
    <apparelColor>(38,74,74)</apparelColor>
      <!-- design: 'min Good'. Sealed-suit divers maintain their kit because failure drowns them. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <itemQuality>Good</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Deepwater_Leader': """    <weaponMoney>1400~1680</weaponMoney>
    <apparelMoney>1100~1320</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>ORMeleeSharp</li>
      <li>KotORRanged_rare</li>
    </weaponTags>
    <itemQuality>Excellent</itemQuality>
      <apparelTags>
      <li>EVA</li>
      <li>Vacsuit</li>
      <li>KotORHeadband_gasmask</li>
    </apparelTags>
      <!-- sealed-suit divers carry rations and real medicine, not herbs -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dull dark teal — owner. Deep water, sealed suits -->
    <apparelColor>(38,74,74)</apparelColor>
      <!-- design: 'min Good'. Sealed-suit divers maintain their kit because failure drowns them. -->
    <forceWeaponQuality>Good</forceWeaponQuality>
    <minApparelQuality>Good</minApparelQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Geonosian_Grunt': """    <weaponMoney>400~480</weaponMoney>
    <apparelMoney>60~72</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>KotORRanged_sonic</li>
    </weaponTags>
      <apparelTags>
      <li>ORChitinArmour</li>
      <li>KotORClothing_civilian_prole</li>
    </apparelTags>
      <!-- hive insectoids: insect jelly is food AND identity; foundry stock beside it -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>InsectJelly</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>10~30</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- chitin red-brown — owner. Matches the carapace the hive already wears -->
    <apparelColor>(104,62,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Geonosian_Heavy': """    <weaponMoney>800~960</weaponMoney>
    <apparelMoney>80~96</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>KotORRanged_sonic</li>
      <li>SWKotORWeaponCategoryTag_heavyranged</li>
    </weaponTags>
      <apparelTags>
      <li>ORChitinArmour</li>
      <li>KotORClothing_civilian_prole</li>
    </apparelTags>
      <!-- hive insectoids: insect jelly is food AND identity; foundry stock beside it -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>InsectJelly</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>10~30</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- chitin red-brown — owner. Matches the carapace the hive already wears -->
    <apparelColor>(104,62,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Geonosian_Specialist': """    <weaponMoney>1000~1200</weaponMoney>
    <apparelMoney>100~120</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>KotORRanged_sonic</li>
      <li>KotORRanged_rare</li>
    </weaponTags>
      <apparelTags>
      <li>ORChitinArmour</li>
      <li>KotORClothing_civilian_prole</li>
    </apparelTags>
      <!-- hive insectoids: insect jelly is food AND identity; foundry stock beside it -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>InsectJelly</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>10~30</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- chitin red-brown — owner. Matches the carapace the hive already wears -->
    <apparelColor>(104,62,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Geonosian_Leader': """    <weaponMoney>1500~1800</weaponMoney>
    <apparelMoney>200~240</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>KotORRanged_sonic</li>
      <li>KotORRanged_legendary</li>
    </weaponTags>
    <itemQuality>Excellent</itemQuality>
      <apparelTags>
      <li>ORChitinArmour</li>
      <li>KotORClothing_civilian_prole</li>
    </apparelTags>
      <!-- hive insectoids: insect jelly is food AND identity; foundry stock beside it -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>InsectJelly</thingDef><countRange>2~6</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>10~30</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- chitin red-brown — owner. Matches the carapace the hive already wears -->
    <apparelColor>(104,62,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Helix_Grunt': """    <weaponMoney>1400~1700</weaponMoney>
    <apparelMoney>700~840</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>SWKotORWeaponCategoryTag_pistol</li>
      <li>KotORRanged_strong</li>
    </weaponTags>
    <minApparelQuality>Excellent</minApparelQuality>
      <apparelTags>
      <li>KotORArmor_mid</li>
    </apparelTags>
      <!-- Arkanian geneticists: glitterworld medicine and lab stock, never street drugs -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineUltratech</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>3~8</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>3~10</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- very pale baby blue — owner. Clinical, expensive, Arkanian -->
    <apparelColor>(208,226,240)</apparelColor>
      <!-- design: 'min Excellent - few and perfect'. forceWeaponQuality is an EXACT value, not
         a floor, so Excellent here means every Helix weapon is Excellent - which is
         exactly the stated character: no waste, no spares, nothing improvised. -->
    <forceWeaponQuality>Excellent</forceWeaponQuality>
    <itemQuality>Excellent</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Helix_Heavy': """    <weaponMoney>2000~2400</weaponMoney>
    <apparelMoney>900~1080</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>SWKotORWeaponCategoryTag_heavyranged</li>
      <li>KotORRanged_strong</li>
    </weaponTags>
    <minApparelQuality>Excellent</minApparelQuality>
      <apparelTags>
      <li>KotORArmor_mid</li>
    </apparelTags>
      <!-- Arkanian geneticists: glitterworld medicine and lab stock, never street drugs -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineUltratech</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>3~8</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>3~10</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- very pale baby blue — owner. Clinical, expensive, Arkanian -->
    <apparelColor>(208,226,240)</apparelColor>
      <!-- design: 'min Excellent - few and perfect'. forceWeaponQuality is an EXACT value, not
         a floor, so Excellent here means every Helix weapon is Excellent - which is
         exactly the stated character: no waste, no spares, nothing improvised. -->
    <forceWeaponQuality>Excellent</forceWeaponQuality>
    <itemQuality>Excellent</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Helix_Specialist': """    <weaponMoney>2600~3100</weaponMoney>
    <apparelMoney>1100~1320</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>KotORRanged_rare</li>
      <li>ORSniper</li>
    </weaponTags>
    <minApparelQuality>Excellent</minApparelQuality>
      <apparelTags>
      <li>KotORArmor_heavy</li>
      <li>KotORArmor_mid</li>
    </apparelTags>
      <!-- Arkanian geneticists: glitterworld medicine and lab stock, never street drugs -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineUltratech</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>3~8</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>3~10</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- very pale baby blue — owner. Clinical, expensive, Arkanian -->
    <apparelColor>(208,226,240)</apparelColor>
      <!-- design: 'min Excellent - few and perfect'. forceWeaponQuality is an EXACT value, not
         a floor, so Excellent here means every Helix weapon is Excellent - which is
         exactly the stated character: no waste, no spares, nothing improvised. -->
    <forceWeaponQuality>Excellent</forceWeaponQuality>
    <itemQuality>Excellent</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Helix_Leader': """    <weaponMoney>12500~15000</weaponMoney>
    <apparelMoney>1800~2160</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>KotORRanged_legendary</li>
      <li>KotORRanged_rare</li>
    </weaponTags>
    <itemQuality>Masterwork</itemQuality>
      <apparelTags>
      <li>KotORArmor_heavy</li>
    </apparelTags>
      <!-- Arkanian geneticists: glitterworld medicine and lab stock, never street drugs -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineUltratech</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Neutroamine</thingDef><countRange>3~8</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Gold</thingDef><countRange>3~10</countRange></li>
        <li><thingDef>MedicineUltratech</thingDef><countRange>2~4</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>2~4</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- very pale baby blue — owner. Clinical, expensive, Arkanian -->
    <apparelColor>(208,226,240)</apparelColor>
      <!-- design: 'min Excellent - few and perfect'. forceWeaponQuality is an EXACT value, not
         a floor, so Excellent here means every Helix weapon is Excellent - which is
         exactly the stated character: no waste, no spares, nothing improvised. -->
    <forceWeaponQuality>Excellent</forceWeaponQuality>
    <minApparelQuality>Excellent</minApparelQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Blackstar_Grunt': """    <weaponMoney>400~480</weaponMoney>
    <apparelMoney>350~420</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>SWKotORWeaponCategoryTag_rifle</li>
      <li>SimpleGun</li>
    </weaponTags>
    <requiredWorkTags>Violent</requiredWorkTags>
      <apparelTags>
      <li>SaV_outfit_merc</li>
      <li>KotORArmor_mid</li>
      <li>KotORClothing_undersuit</li>
    </apparelTags>
      <!-- professional mercenaries: combat drugs, real medicine, and paid in silver -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>2~4</countRange></li>
        <li><thingDef>GoJuice</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>50~150</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- near-black — owner. It is in the name, and it makes them read instantly against white stormtroopers and brown Jawa -->
    <apparelColor>(38,38,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Blackstar_Heavy': """    <weaponMoney>700~840</weaponMoney>
    <apparelMoney>500~600</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>SWKotORWeaponCategoryTag_heavyranged</li>
      <li>KotORRanged_strong</li>
    </weaponTags>
    <apparelRequired>
      <li>guy762_MandoArmor_battle</li>
      <li>guy762_MandoHelmet_supercom</li>
    </apparelRequired>
    <requiredWorkTags>Violent</requiredWorkTags>
      <!-- professional mercenaries: combat drugs, real medicine, and paid in silver -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>2~4</countRange></li>
        <li><thingDef>GoJuice</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>50~150</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- near-black — owner. It is in the name, and it makes them read instantly against white stormtroopers and brown Jawa -->
    <apparelColor>(38,38,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Blackstar_Specialist': """    <weaponMoney>12800~16500</weaponMoney>
    <apparelMoney>800~960</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>ORSniper</li>
      <li>KotORRanged_rare</li>
    </weaponTags>
    <requiredWorkTags>Violent</requiredWorkTags>
      <apparelTags>
      <li>SaV_outfit_merc</li>
      <li>KotORArmor_mid</li>
      <li>KotORClothing_undersuit</li>
    </apparelTags>
      <!-- professional mercenaries: combat drugs, real medicine, and paid in silver -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>2~4</countRange></li>
        <li><thingDef>GoJuice</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>50~150</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- near-black — owner. It is in the name, and it makes them read instantly against white stormtroopers and brown Jawa -->
    <apparelColor>(38,38,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Blackstar_Leader': """    <weaponMoney>14600~26000</weaponMoney>
    <apparelMoney>1500~1800</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>KotORRanged_legendary</li>
      <li>ORPistol</li>
    </weaponTags>
    <requiredWorkTags>Violent</requiredWorkTags>
      <apparelTags>
      <li>SaV_outfit_merc</li>
      <li>MNCFactionArmor</li>
      <li>KotORArmor_mid</li>
    </apparelTags>
      <!-- professional mercenaries: combat drugs, real medicine, and paid in silver -->
    <inventoryOptions>
      <skipChance>0.35</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineIndustrial</thingDef><countRange>2~4</countRange></li>
        <li><thingDef>GoJuice</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>MealSurvivalPack</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>50~150</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>150~400</countRange></li>
        <li><thingDef>GoJuice</thingDef><countRange>2~4</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- near-black — owner. It is in the name, and it makes them read instantly against white stormtroopers and brown Jawa -->
    <apparelColor>(38,38,42)</apparelColor>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_TradeMoot_Grunt': """    <weaponMoney>250~300</weaponMoney>
    <apparelMoney>100~120</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>KotORRanged_ion</li>
      <li>SaV_jawaheavy</li>
      <li>Jawa_IonWeaponLight</li>
    </weaponTags>
    <maxApparelQuality>Poor</maxApparelQuality>
      <apparelRequired>
      <li>guy762_Robes_jawa</li>
      <li>guy762_JawaHood</li>
    </apparelRequired>
    <apparelTags>
      <li>SaV_apparel_jawa</li>
      <li>ORHermit</li>
      <li>KotORClothing_civilian_hooded</li>
    </apparelTags>
      <!-- the clan trades in salvage; a Jawa carries stock, not supplies -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>20~60</countRange></li>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~15</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty dark brown — owner, the Jawa colour -->
    <apparelColor>(77,58,42)</apparelColor>
      <!-- design: 'max Poor->Normal', the tightest clamp of any faction, paired with the widest
         variety - because everything a Jawa carries came off something else. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
    <itemQuality>Poor</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_TradeMoot_Heavy': """    <weaponMoney>450~540</weaponMoney>
    <apparelMoney>130~156</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>KotORRanged_ion</li>
      <li>Jawa_IonWeapon</li>
      <li>JawaIon_Damage</li>
      <li>KotORRanged_weak</li>
    </weaponTags>
    <maxApparelQuality>Normal</maxApparelQuality>
      <apparelRequired>
      <li>guy762_Robes_jawa</li>
      <li>guy762_JawaHood</li>
    </apparelRequired>
    <apparelTags>
      <li>SaV_apparel_jawa</li>
      <li>ORHermit</li>
      <li>KotORClothing_civilian_hooded</li>
    </apparelTags>
      <!-- the clan trades in salvage; a Jawa carries stock, not supplies -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>20~60</countRange></li>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~15</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty dark brown — owner, the Jawa colour -->
    <apparelColor>(77,58,42)</apparelColor>
      <!-- design: 'max Poor->Normal', the tightest clamp of any faction, paired with the widest
         variety - because everything a Jawa carries came off something else. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
    <itemQuality>Poor</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_TradeMoot_Specialist': """    <weaponMoney>900~1080</weaponMoney>
    <apparelMoney>160~192</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>Jawa_IonWeapon</li>
      <li>JawaIon_Damage</li>
      <li>KotORRanged_ion</li>
    </weaponTags>
    <maxApparelQuality>Normal</maxApparelQuality>
      <apparelRequired>
      <li>guy762_Robes_jawa</li>
      <li>guy762_JawaHood</li>
    </apparelRequired>
    <apparelTags>
      <li>SaV_apparel_jawa</li>
      <li>ORHermit</li>
      <li>KotORClothing_civilian_hooded</li>
    </apparelTags>
      <!-- the clan trades in salvage; a Jawa carries stock, not supplies -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>20~60</countRange></li>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~15</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty dark brown — owner, the Jawa colour -->
    <apparelColor>(77,58,42)</apparelColor>
      <!-- design: 'max Poor->Normal', the tightest clamp of any faction, paired with the widest
         variety - because everything a Jawa carries came off something else. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
    <itemQuality>Poor</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_TradeMoot_Leader': """    <weaponMoney>900~1080</weaponMoney>
    <apparelMoney>250~300</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>KotORRanged_ion</li>
      <li>Jawa_IonWeapon</li>
      <li>JawaIon_Damage</li>
    </weaponTags>
    <maxApparelQuality>Good</maxApparelQuality>
      <apparelRequired>
      <li>guy762_Robes_jawa</li>
      <li>guy762_JawaHood</li>
    </apparelRequired>
    <apparelTags>
      <li>SaV_apparel_jawa</li>
      <li>ORHermit</li>
      <li>KotORClothing_civilian_hooded</li>
    </apparelTags>
      <!-- the clan trades in salvage; a Jawa carries stock, not supplies -->
    <inventoryOptions>
      <skipChance>0.25</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~3</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>20~60</countRange></li>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~15</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>60~150</countRange></li>
        <li><thingDef>ComponentSpacer</thingDef><countRange>1~1</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- dusty dark brown — owner, the Jawa colour -->
    <apparelColor>(77,58,42)</apparelColor>
      <!-- design: 'max Poor->Normal', the tightest clamp of any faction, paired with the widest
         variety - because everything a Jawa carries came off something else. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
    <itemQuality>Poor</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
 'Jawa_Junkers_Grunt': """    <weaponMoney>60~72</weaponMoney>
    <apparelMoney>250~300</apparelMoney>
    <initialResistanceRange>8~14</initialResistanceRange>
    <initialWillRange>1~3</initialWillRange>
    <weaponTags>
      <li>ORMeleeBlunt</li>
      <li>NeolithicMeleeBasic</li>
    </weaponTags>
    <apparelTags>
      <li>WarcasketAll</li>
    </apparelTags>
    <maxApparelQuality>Awful</maxApparelQuality>
      <!-- warcasket scrappers run on chemfuel and carry what they stripped -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>Chemfuel</thingDef><countRange>10~35</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~20</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Awful->Poor on WEAPONS; armour UNCLAMPED'. That asymmetry is the faction:
         the armour was cut off a body and the gun was not. Apparel is deliberately left
         without a clamp - do not 'finish' it by adding one. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
    <itemQuality>Poor</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
    </apparelDisallowTags>""",
 'Jawa_Junkers_Heavy': """    <weaponMoney>140~168</weaponMoney>
    <apparelMoney>600~720</apparelMoney>
    <initialResistanceRange>12~18</initialResistanceRange>
    <initialWillRange>2~4</initialWillRange>
    <weaponTags>
      <li>SimpleGun</li>
      <li>KotORRanged_weak</li>
    </weaponTags>
    <apparelRequired>
      <li>VFEP_WarcasketHelmet_Warcasket</li>
      <li>VFEP_Warcasket_Warcasket</li>
      <li>VFEP_WarcasketShoulders_Warcasket</li>
    </apparelRequired>
    <apparelTags>
      <li>WarcasketAll</li>
    </apparelTags>
      <!-- warcasket scrappers run on chemfuel and carry what they stripped -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>Chemfuel</thingDef><countRange>10~35</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~20</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Awful->Poor on WEAPONS; armour UNCLAMPED'. That asymmetry is the faction:
         the armour was cut off a body and the gun was not. Apparel is deliberately left
         without a clamp - do not 'finish' it by adding one. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
    <itemQuality>Poor</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
    </apparelDisallowTags>""",
 'Jawa_Junkers_Specialist': """    <weaponMoney>200~240</weaponMoney>
    <apparelMoney>700~850</apparelMoney>
    <initialResistanceRange>14~22</initialResistanceRange>
    <initialWillRange>2~5</initialWillRange>
    <weaponTags>
      <li>AssaultRifle</li>
      <li>KotORRanged_mid</li>
    </weaponTags>
    <apparelTags>
      <li>WarcasketAll</li>
    </apparelTags>
    <maxApparelQuality>Poor</maxApparelQuality>
      <!-- warcasket scrappers run on chemfuel and carry what they stripped -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>Chemfuel</thingDef><countRange>10~35</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~20</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Awful->Poor on WEAPONS; armour UNCLAMPED'. That asymmetry is the faction:
         the armour was cut off a body and the gun was not. Apparel is deliberately left
         without a clamp - do not 'finish' it by adding one. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
    <itemQuality>Poor</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
    </apparelDisallowTags>""",
 'Jawa_Junkers_Leader': """    <weaponMoney>350~420</weaponMoney>
    <apparelMoney>1000~1200</apparelMoney>
    <initialResistanceRange>20~30</initialResistanceRange>
    <initialWillRange>4~7</initialWillRange>
    <weaponTags>
      <li>ORMeleeBlunt</li>
    </weaponTags>
    <apparelTags>
      <li>WarcasketAll</li>
    </apparelTags>
    <itemQuality>Masterwork</itemQuality>
      <!-- warcasket scrappers run on chemfuel and carry what they stripped -->
    <inventoryOptions>
      <skipChance>0.3</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>Chemfuel</thingDef><countRange>10~35</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~4</countRange></li>
        <li><thingDef>OuterRim_Durasteel</thingDef><countRange>5~20</countRange></li>
        <li><thingDef>Steel</thingDef><countRange>15~40</countRange></li>
        <li><thingDef>OuterRim_ComponentHypertech</thingDef><countRange>1~2</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <apparelRequired>
      <li>VFEP_Warcasket_Warcasket</li>
      <li>VFEP_WarcasketShoulders_Warcasket</li>
      <li>VFEP_WarcasketHelmet_Warcasket</li>
    </apparelRequired>
      <!-- design: 'max Awful->Poor on WEAPONS; armour UNCLAMPED'. That asymmetry is the faction:
         the armour was cut off a body and the gun was not. Apparel is deliberately left
         without a clamp - do not 'finish' it by adding one. -->
    <forceWeaponQuality>Poor</forceWeaponQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
    </apparelDisallowTags>""",
 'Jawa_Homestead_DesertRanger': """    <weaponMoney>200~260</weaponMoney>
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
      <!-- settlers and salvagers - modest, practical, a little cash -->
    <inventoryOptions>
      <skipChance>0.4</skipChance>
      <subOptionsChooseOne>
        <li><thingDef>MedicineHerbal</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Pemmican</thingDef><countRange>6~15</countRange></li>
        <li><thingDef>ComponentIndustrial</thingDef><countRange>1~2</countRange></li>
        <li><thingDef>Silver</thingDef><countRange>15~45</countRange></li>
      </subOptionsChooseOne>
    </inventoryOptions>
      <!-- design: 'max Good'. Settlers keep decent kit but nothing exquisite. -->
    <itemQuality>Normal</itemQuality>
      <!-- TABOO: a culture must never turn up in another culture's uniform. Only
         families this kind does not use itself are listed - its own apparelTags and
         every tag its apparelRequired items carry are excluded, so a disallow can
         never strand it. -->
    <apparelDisallowTags>
      <li>DroidArmor</li>
      <li>ImperialApparel</li>
      <li>ImperialArmy</li>
      <li>ImperialOfficer</li>
      <li>ImperialStormtrooper</li>
      <li>KotORDroidArmorT1</li>
      <li>KotORDroidArmorT2</li>
      <li>KotORDroidArmorT3</li>
      <li>MNCFactionArmor</li>
      <li>ORTusken</li>
      <li>Royal</li>
      <li>SaV_apparel_jawa</li>
      <li>SaV_apparel_tusken</li>
      <li>Warcasket</li>
      <li>WarcasketAll</li>
      <li>WarcasketVeteran</li>
    </apparelDisallowTags>""",
}


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
        name = "Jawa_%s_%s" % (fac, role)
        if name in KIT_PRE:
            L.append(KIT_PRE[name].rstrip("\n"))
        L += ["  <PawnKindDef%s>" % ('' if pkg is None else ' MayRequire="%s"' % pkg),
              "    <defName>%s</defName>" % name,
              "    <label>%s</label>" % label,
              "    <race>%s</race>" % race,
              "    <defaultFactionDef>%s</defaultFactionDef>" % FACTIONS[fac],
              "    <combatPower>%d</combatPower>" % combat_power(wm, am, role, fac),
              "    <isFighter>%s</isFighter>" % ("false" if not wt else "true"),
              # 🔑 The whole point of the roster: ONE kind spawns the faction's whole
              # species mix wearing that faction's gear, so species never appear in a
              # kind's name and a faction's look is edited in one place.
              "    <useFactionXenotypes>%s</useFactionXenotypes>" % ("true" if race == "Human" else "false")]
        # 🔑 Everything from <weaponMoney> on is CURATED, not computed. See KIT above.
        # The generator used to derive these from its R table and that derivation is
        # what silently reverted the equipment layer, so it is gone rather than kept
        # alongside as a second opinion.
        L.append(KIT[name].rstrip("\n"))
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
