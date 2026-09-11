# Per-biome inconsistency/opportunity review — post-move casts (round 2)

Derived 2026-09-10 from `decisions_propagated.json` (828 rows) + `move_mapping_v2.md`
(with the 2026-09-10 rulings: ninth faction-fauna roster, both-jungles trio, injectables,
placement-rule creatures) + each biome sheet's own admission tests and hard bans.
Standing rulings applied (insect ruling 2026-09-10: base-game/Black Hive insects are faction-only — infestation/raid events, never biome residents; VFEI2_* de-selected everywhere); boom family (15) CUT — including GR_Boomsnake's "Pyrelands" move;
VQE_IceCrawler/VQE_Megamidge out; VQEA Splice x4 → dungeon-guardians; fliers extracted to
their roster; injectables (Bulwark, Squall, Prowler, Megaphorid) not counted as residents.
Duplicate arrival rows (a creature both staying and "arriving", or one move splitting into
two combined-sheet targets) are deduped here; the census script's raw output overcounts them.
Ordered by churn (arrivals+departures+cuts+flier extractions), highest first.

---

## the_miasma — churn 22 (cast 30 → 23) · NURSERY (ruled 2026-09-10)
Arrivals (7): Dianoga, RSW_SandoAquaMonster, BMT_PodWorm, Blarth, Blixus, JRWBeelzebufo, MarshHaunt. Flier→roster arriving: Bogwing.
Departures (12 moves): entire aquatic cast to the seas (RSW_Faa/Laa/Mee/OpeeSeaKiller/SiltLamprey, Yobshrimp) + AA_BloodShrimp, AA_Helixien, AA_Plasmorph, AA_Slurrypede, BMT_Gembug, Kreetle. Insect ruling: VFEI2_Swarmling + VFEI2_BlackSwarmling out (faction-only).

NURSERY RULING (owner, 2026-09-10): the sea creatures use the Miasma as a young-raising ground — juvenile-only spawns via per-species young PawnKindDefs (same race, maxGenerationAge capped below adulthood, reduced combatPower) in the Miasma wildAnimals list. Engine-verified: PawnKindDef.minGenerationAge/maxGenerationAge. Build filed for FOUNDRY.

INCONSISTENCIES:
1. JRWBeelzebufo reads as "giant frog" — collides with ban 7 (no vanilla-Earth fauna) and the recognizability rule; rename/reskin owed.
2. SandoAquaMonster is an open-ocean titan routed into brine channels; sheet's rings-of-refuge fiction needs a line justifying it.
3. Blarth ("Hutt pets") carries faction-territory language — overlaps the new ninth roster; owner said Miasma, but dual-list it deliberately.

OPPORTUNITIES:
1. Losing six fish leaves the surge-channel scavenger niche open — Dianoga's "tentacle pulling like lasso" note is the star; build it.
2. MarshHaunt + Dianoga + SandoAquaMonster gives a three-tier water-menace ladder; say so in §4's rings.

## the_rot — churn 19 (cast 15 → 20)
Arrivals (11): ShiroTrap, pustule hornet family x5 (Queen, ColonyQueen, Spawned, Colony, plain), AA_AnimaColossus, BMT_Thrumbungus, BMT_Yooka, MA_Sporemole, Snoruuk. Fliers→roster arriving: AA_AngelMoth, BMT_SmogMoth. Flier extracted: BMT_GlowBat.
Departures (5 out): BMT_CaveSpider, BMT_ChemSnail, BMT_GiantSlug, BMT_GiantSnail, BMT_Pillbug.

INCONSISTENCIES:
1. Ban 2: residents must be fungus/animal hybrids. Pustule hornets, ShiroTrap, Snoruuk, BMT_Yooka arrive un-hybridized — each needs the hybrid treatment or the sitting rejects it.
2. Five pustule-hornet defs are one organism; count them as one admission, not five.

OPPORTUNITIES:
1. Thrumbungus ("partially digesting itself") and Sporemole pass ban 2 cleanly — flagship arrivals; feature both in §4's cast table.
2. AnimaColossus near the anima-analog (§7) makes a natural undefended-prize guardian (ban 8); wire them together.

## the_greentide — churn 19 (cast 27 → 17)
Arrivals (3): GiantAnt_Race (event-only, by ruling), Tach + Rikknit (both-jungles ruling). Flier→roster arriving: BMT_FacetMoth. Fliers extracted: Convor, Hawkbat.
Departures (9 moves): AA_BloodShrimp, AA_Razorjack, Beldon, Dalgo, Dianoga, Falumpaset, Hssiss, Lylek, ShiroTrap. Insect ruling: VFEI2_Swarmling out (faction-only). Sitting 2026-09-10: AA_Wildpawn arrives from arid (the steaming jungle); BMT_Diggerpede to reserve; AA_Needlepost OUT; Fambaa + Dragonsnake TOTAL art redo + web research (SW, no rename).

INCONSISTENCIES:
1. GiantAnt_Race is event-only ("only the raiding events") — belongs on the event roster, not wildAnimals; keep it off the sheet's resident cast.
2. Losing Lylek, Hssiss, Dianoga strips three of four big predators; §4's "open free-for-all, no truce" now rests on Kinrath + Dragonsnake alone.

OPPORTUNITIES:
1. Rikknit's ovum-sac cuisine note is a whole §7 Uniquely-available entry (ji rikknit, egg delicacy) — write it.
2. Tach the Greatbole-canopy thief pairs with §7b's living towers; a steal-from-camps mechanic fits the register.

## the_scarlands — churn 11 (cast 9 → 15)
Arrivals (6, deduped): AA_AcanthamoebaGiganteaSmall, BMT_CrystalFairyMole, BMT_MegaphoridLarva, BMT_Stoneback, RSW_ShaleGorger, SW_Electricfish, SW_Grenadierworm (insect ruling: VFEI2_Acidspitter + VFEI2_RoyalSpelopede arrivals VOIDED — faction-only). Sitting 2026-09-10: AA_Terramorph arrives (dayside lurker, shared range with wasteland). (SW_Electrictick already resident — its wasteland row is consolidation, not arrival).
Departures (2): AA_Helixien, AA_SpinedGow. Cut: VFEI2_Boomtick (boom family).

INCONSISTENCIES:
1. SW_Electricfish needs a water body; the sheet's only liquids are rainbow acid pools — either it lives IN acid (say so) or it misroutes.
2. Nine arrivals nearly double a biome whose §4 is "what life REMAINS" — sparse-wound register; thin or justify density.

OPPORTUNITIES:
1. Electro-cluster (Electrictick, Electricfish, Electricgryllotalpa, Grenadierworm) is now a coherent "the ground still discharges" fauna story — name it in §4.
2. MegaphoridLarva resident + Megaphorid adult as injectable hive = a life-cycle hook no other biome has.

## terminator_sea + the_grey_deep — churn 11 (cast 2 → 7) — CAP RELEASED 2026-09-10
Arrivals (5): RSW_SiltLamprey, RSW_ElderSando, BMT_Polluwog, Blixus, TetnissCrab (insect ruling: VFEI2_Silverfish arrival VOIDED — faction-only). Ruled 2026-09-10: the sheet's "three, and no more" cap is RELEASED (sheet amended); schooling fish retargeted to the Twilight Deep — BMT_Megakrill (still a fishing result, never a spawn) + BMT_MutatingTumorfish x3. Flier: AA_ColossalAerofleet arriving→roster; AA_Aerofleet extracted.

INCONSISTENCIES:
1. RESOLVED by the 2026-09-10 ruling: schools/swarms ban stands in the Grey — the schooling set now lives in the Twilight.
2. Tumorfish x3 is one organism's life cycle — one admission (now in the Twilight); Megakrill stays a *fishing result*, off wildAnimals, twilight waters.

OPPORTUNITIES:
1. If the cap is to survive: ElderSando (apex), SiltLamprey (parasite), Blixus (horror) honor "three, and no more" — the rest become fishing results/set-pieces.
2. TetnissCrab (0.5 cells) as the preserved-in-tar scavenger fits the preservation register (§3) perfectly.

## the_scald — churn 10 (cast 2 → 8; zero holdovers)
Arrivals (8): RSW_Faa, RSW_Mee, AA_Atispec, AA_LarvalAtispec, AA_RayHound, JOE_Nautilant, RSW_ColoClawFish, RSW_ThornbackColo.
Departures (2): RSW_ElderSando, RSW_SandoAquaMonster.

INCONSISTENCIES:
1. Ban 4: no macro-life in the boil's surface layer — every arrival must be written as depth-dweller; ColoClawFish/ThornbackColo need that line.
2. Ban 3: no native land predator hunts the water — AA_RayHound ("Scald beast") must be aquatic, not a shore hound, or it violates.
3. Entire cast replaced in one wave; §4's "roiling wonder" text still describes nobody now present — sheet fauna prose is stale.

OPPORTUNITIES:
1. Faa (0.2) + Mee (0.3) give the boil its prey base — the temperature-banded rainbow mats (§4) as their grazing story writes itself.
2. Atispec + LarvalAtispec life cycle at the vents = the biome's first native breeding fiction.

## terminator_sea + the_twilight_deep — churn 12 (cast 2 → 12) — receives the Grey's schooling set (2026-09-10)
Arrivals (11): RSW_Laa, RSW_OpeeSeaKiller, Yobshrimp, RSW_AbyssalColo, RSW_CrimsonOpee, RSW_Starmaw, RSW_StormSando, StoneCrab + from the Grey's cap ruling: BMT_MutatingTumorfish x3 (one organism); BMT_Megakrill arrives as a FISHING RESULT only. Flier: ColossalAerofleet→roster; AA_Aerofleet extracted.

INCONSISTENCIES:
1. Predator stack: OpeeSeaKiller (5 sq), CrimsonOpee (9 sq), Starmaw, StormSando, AbyssalColo — five mega-predators over prey of Laa, Yobshrimp, StoneCrab; chain is inverted.
2. Two Opee variants (SeaKiller + CrimsonOpee) do the same lurker job at two sizes — merge or differentiate (river-bank vs light-column).
3. Surface ban still holds (nothing schools above the roof) — Yobshrimp's placement must be bank/channel, sheet §4's river-fauna slot.

OPPORTUNITIES:
1. "Rich and varied as the land, by ruling" — this cast finally delivers it; distribute across §4's three habitats (columns, banks, dark between) explicitly.
2. StoneCrab (0.3) on the lamplit banks is the Compact's harvest animal — a tended-fishery hook for §8.

## wasteland — churn 11 (cast 21 → 12) · Terramorph DAYSIDE
Arrivals (1): BMT_Stoneback. Departures (7 moves): AcanthamoebaSmall, Eyeling, pustule hornets x3, SW_Electrictick, Toxalope; (1 out): AA_FissionMouse. Insect ruling: VFEI2_Swarmling + VFEI2_BlackSwarmling out (faction-only).
Sitting 2026-09-10: AA_Terramorph ENFORCED dayside-only — resident here + the_scarlands, cut from nightside_ice and desert; terrain-matching color change noted as MAYBE.

INCONSISTENCIES:
1. None structural — losses are all correct routings; ban 3 ("wildlife never the headline threat") is easier to honor at 14.

OPPORTUNITIES:
1. The wretched-many register (§4) has room for 2-3 of the 103 unrouted homeless needs-owner rows (sick, cornered, scavenging body plans).

## the_slime — churn 9 (cast 9 → 6)
Arrivals (3): AA_AcanthamoebaGiganteaHuge, AA_OvergrownColossus ("slime trees"), AA_TeratogenicOriginator ("tint green"). Departures (6): DecayDrake, Helixien, Mime→dungeon, Plasmorph, Thunderbeast→blue_desert, GR_Manbear→ninth roster.

INCONSISTENCIES:
1. All three arrivals carry explicit slimification notes — admission test ("part of the flow, or being transformed") honored; ban 5 needs each to get a resistance-or-transformation state written.
2. GR_Chickenrabbit survives as a resident; "chicken+rabbit" name fails recognizability — rename with the slimified art pass.

OPPORTUNITIES:
1. Six residents is thin for a flagship biome; the Unfinished-adjacent transformation states of visitors could carry ambient density instead of new species.

## desert — churn 14 (cast 45 → 47)
Arrivals (8): AA_GreatDevourer, AA_Groundrunner, AA_MatureFleshbeast, AA_SandLion, BMT_Stoneback, BMT_TruffleMole, JOE_Cephalope, JOE_Landopus.
Sitting 2026-09-10: OUT Skalder, Jakobeast (ice predator — routing owed), AA_Terramorph (dayside range is wasteland+scarlands); to RESERVE: Kwi, AA_Gigantelope. Horax TOTAL art redo (SW references). Desert-wide art posture (owner): most of this cast needs new art except pieces already generated — rides the art-template ticket.

INCONSISTENCIES:
1. 53 residents is the planet's biggest cast — spawn dilution; nobody will ever see the rare ones. Thin toward the reserve pool.
2. GreatDevourer + MatureFleshbeast are BOTH "sarlacc relatives", atop SandSquid/MammothWorm/SandLion/TruffleMole/Cephalope — seven subsurface ambushers, one niche.
3. JOE_Landopus "desert water defender" — the desert sheet has no water; its home is the oasis register (weeping_stones) or a placement rule.
4. Ban 3 (no pursuit predators): Groundrunner's name promises pursuit; verify its hunt is ambush/scavenge before admitting.

OPPORTUNITIES:
1. A sarlacc growth ladder (MatureFleshbeast → GreatDevourer → offmap Sarlacc) told as one organism turns niche-duplication into the biome's deepest lore hook.

## the_contagion — churn 7 (cast 11 → 16) · RedGoo → TITAN (ruled bigger)
Arrivals (5, deduped — AA_BloodShrimp already resident): AA_Eyeling, AA_FungalHusk, AA_OcularNightling, AG_OcularSlinger, GR_Fleshling. Flier extracted: AA_InfectedAerofleet.

INCONSISTENCIES:
1. weeping_stones:AA_Eyeling is an unresolved propagation conflict — its untouched row still holds Eyeling there while "ocular" routes it here; resolve at the sitting.
2. Each arrival needs the §4 admission line written: UV-shy or UV-armored — the ocular family plausibly dives at the Burn; say it.

OPPORTUNITIES:
1. The ocular cluster (Eyeling, OcularJelly, OcularNightling, OcularSlinger, FungalHusk) is now a coherent "the weapon grows eyes" cast — name the family in §4's table.
2. GR_Fleshling beside the Unfinished: make it a *survived* bud — the one form the goo didn't reabsorb.

## the_pyrelands — churn 5 (cast 9 → 8)
Arrivals (2): AA_Razorjack, Dalgo (GR_Boomsnake's "Pyrelands" move is voided by the boom-family cut). Departures (2): Boomalope→dungeon commission, Gizka. Flier extracted: AA_FireWasp.

INCONSISTENCIES:
1. The fire food-web (§4 — heat-banking furnace-beasts, boom-and-bust) now has NO creature expressing it: the boom cut removed the entire fire-linked fauna and the replacement goo-sack lives in dungeons.
2. Desert ban 4 explicitly assigns boom-and-bust populations to the Pyrelands — the mechanic is now assigned to nobody.

RULED (owner card, 2026-09-10) — fire-web repopulation:
1. COMMISSIONED: the fire-hawk (flier roster — carries burning twigs, flushes prey) and the furnace-beast (heat-banking migratory megafauna) — the two irreplaceable igniters.
2. RECAST: Razorjack arrives as the fire-follower (flame-edge hunter); Barbslinger routed here as the ash-grazer.
3. The burrower family slot fills from the homeless pool or a third commission — FOUNDRY's pick at build.

## nightside_ice — churn 10 (cast 6 → 9: 6 native + 3 visitors) — VISITOR LAW RULED 2026-09-10
Natives: AA_ShockGoat (refashion ruled) + BMT_CaveLemming (rename ruled) arrive as natives — all natives get the thermal-only sensing line. VISITORS-AND-DYING (never native, low commonality, riding the sheet's own "visitor, a machine, or dying" clause): Tauntaun (margin herds straying in), Wampa (follows the herds), Jakobeast (rerouted from desert). Visitors hunt by starlight/aurora (real, cold light), exempt from thermal-only; every straying herd is a walking thermal beacon that ends as a tunneler-warren event. NEEDS-MORE fills from the sheet's own unbuilt natives, COMMISSIONED: tunneler warren creature, inclusion-insect swarm, aurora-current feeder. Injectable, not resident: Bulwark. AA_Terramorph out (dayside won the either-or).

REMAINING:
1. CaveLemming and ShockGoat renames/refashions are ruled but not yet done — they enter the cast only after (with the thermal-only sensing line).

OPPORTUNITIES:
1. ShockGoat's "pale blue aura" is the biome's first visible-from-distance creature cue — a legible hazard in a sensor-dead biome.

## dune_sea + deep_desert — churn 7 (cast 12 → 15) — sitting 2026-09-10: AA_TetraSlug out (cathedral-only), AA_Dunealisk CUT from game; GIANTS VERY RARE here (owner: giant creatures at trace commonality)
Arrivals (5, deduped across the combined sheets): AA_SpinedGow, AA_SandLion, BMT_TruffleMole (0.4 cells), JOE_Cephalope, GR_ParagonThrumbo ("Great Thrumbo", 7 sq, very rare).

INCONSISTENCIES:
1. Dune-sea ban: no medium fauna — giant or grain-scale only. SandLion, SpinedGow, Cephalope must land in a size bin that honors it; verify before deploy.
2. Sand-burrower niche now five deep (Dunealisk, SandLion, TruffleMole, Cephalope + Krayt ambush) — differentiate by depth/prey or thin.
3. "Recognizable giant is the worst offence" — Great Thrumbo is a renamed vanilla Thrumbo; its art must alienize, not just rename.

OPPORTUNITIES:
1. Great Thrumbo as the deep-desert white whale (very rare, very dangerous) fills the sheet's legend slot beside the Krayts.

## poison_forest — churn 9 (cast 17 → 20)
Arrivals (5): Lylek, AA_Plasmorph, AA_LuciferBug, AA_Radyak, AA_RipperHound. Flier extracted: AA_InfectedAerofleet. Horror ruling: Visceral out (injected dark-side art only). Sitting 2026-09-10: Skalder arrives from arid; AA_Wildpod OUT.

INCONSISTENCIES:
1. Ban: "Nothing fast. No sprinters, no pursuit predators" — Lylek and RipperHound are both pursuit-built; admit only with a rewritten slow/ambush hunting story.
2. Ban: "No open grazing herbivore body plans — nothing to graze" — Radyak (yak-analog) violates on silhouette; refashion as fungivore/vent-licker or reroute.
3. AA_Helixien kept here after being "not here"-ed out of three biomes — deliberate? Confirm at the sitting.

OPPORTUNITIES:
1. LuciferBug among the cold vents and black/purple phototrophs — the biome's light-lure predator; a natural fit, feature it.

## the_forge — churn 4 (cast 7 → 9)
Arrivals (2, deduped — Beldon already resident): AA_CrescendoAnole, Tibidee. Flier arriving→roster: AA_ColossalAerofleet; extracted: AA_Aerofleet.

INCONSISTENCIES:
1. Tibidee is canonically a flying ray — flier-roster candidate that slipped the extraction; decide roster vs resident before it lands.
2. Ban 5: beldons are the only tibanna source — greentide's Beldon move consolidates the herd here correctly; keep one def, one biome. Sitting 2026-09-10: ONLY ONE beldon entry on the slide — resident+arrival of the same def must render once (per-biome dedup ruling, all biomes).

OPPORTUNITIES:
1. CrescendoAnole as the machine-watcher (basks on cooling flows near the lava-machines) ties fauna to the biome's central mystery without revealing it (ban 2).

## fall_line — churn 4 (cast 13 → 15)
Arrivals (3): BMT_BunkerBug, BMT_Megapleura, Squall (injectable — "injectable wreck creatures", not resident). Insect ruling: VFEI2_Fuelmite out (faction-only).

INCONSISTENCIES:
1. Vanilla "Rat" survives in the cast — direct violation of ban 7 (no instantly-nameable terrestrial referent); cut or reskin (Scavrat already covers the niche).
2. Ban 6: nothing defends a fixed range — BunkerBug's name/story implies a held bunker; write it nomadic-between-wrecks or it violates.
3. Rat + Scavrat + WompRat = three rats; one niche, keep two at most.

OPPORTUNITIES:
1. Eight OuterRim feral droids + Megapleura is the planet's only machine-ecology (Fuelmite went faction-only with the insect ruling — the fuel-parasite niche is now vacant; commission or leave).

## the_lantern_deeps — churn 4 (cast 0 → 3)
Arrivals (3): BMT_Gembug, BMT_CrystalCrab, BMT_Glowtail. Flier arriving→roster: BMT_FacetMothLarvae (larvae — likely NOT a flier; restore to cast if so).

INCONSISTENCIES:
1. Ban 3: no crystal-studded animals — crystal life must BE crystal. CrystalCrab and Gembug read as animals wearing crystals; art/lore must commit them to true crystal biology.
2. FacetMothLarvae got swept out with the flier family; larvae don't fly — probable wrong extraction, and the caverns are its ruled home.

OPPORTUNITIES:
1. Glowtail vs the no-free-light law (ban 6): make its glow a light-draw *cost* mechanic — the creature that eats your lamplight.

## arid_shrubland — churn 9 (cast 42 → 38)
Arrivals (2, deduped — Kreetle already resident): BMT_Stoneback, VAEWaste_Hydra ("venomvine patch predator"). Insect ruling: VFEI2_Macrofly arrival VOIDED (faction-only). Horror ruling: Terrorworm out (injected dark-side art only). Flier extracted: Convor. Sitting 2026-09-10: Skalder→poison_forest, AA_Wildpawn→the_greentide, Cannok+Vulptex→reserve; Kreetle art REDO (SW: no rename).

INCONSISTENCIES:
1. Ban 4: no resident LARGE-band creature (large only as juvenile of huge) — the register bins Wildpod, Bantha, Corinathoth, Mudhorn, Ronto, Skalder LARGE. Six standing violations; rebin as juveniles-of-huge or move.
2. 43 residents is the second-biggest cast — same dilution problem as desert.

OPPORTUNITIES:
1. VAEWaste_Hydra inside venomvine patches is a perfect ban-6 synergy (the one dense flora gets a guardian) — flagship placement.

## the_cracked_lands — churn 3 (cast 11 → 12)
Arrivals (2): BMT_SandPillar, DA_RockTroll. Flier extracted: Convor.
1. Clean wave. RockTroll/SandPillar fit the stone register; ban 4 (no flier nests) satisfied by Convor's extraction. Woolamander/Gornt icons protected.

## the_sump — churn 2 (cast 3 → 5)
Arrivals (2): Hssiss, AA_BumbledroneQueen (rejoins its drones — good).

INCONSISTENCIES:
1. Hssiss routed on "the swamp biome only" — but the Miasma is the swamp; the Sump is cold tar with chemotrophic flora. Probable misroute; confirm which biome the owner meant.

OPPORTUNITIES:
1. If Hssiss stays: a dark-side dragon sleeping in preserved tar suits ban 1's partial-remains register better than a wetland story.

## the_rust_cathedral — churn 3 (cast 1 → 4) — sitting 2026-09-10: AA_TetraSlug arrives (sole home). COMMISSIONS ruled: mechanical cockroach + the little gear-like dancing creatures (to be made); organic cockroach already resident (Ling_Cockroach)
Arrivals (2): GR_Mechachicken, GR_Mecharat.
1. Ban 7 (nothing organic outside §4's short list): both are mech-analog — add them to §4's list explicitly or the linter flags them.
2. "Mechachicken" fails recognizability on name; rename with the pass (Mecharat borderline, WompRat precedent).

## the_webwork — churn 2 (cast 4 → 6)
Arrivals (2): AA_Feralisk (ruled: reskin/merge INTO Wysokk), GR_Chickenspider ("baby evil spider" — juvenile Wyyyschokk).
1. Feralisk is a merge, not a new species — implement as Wysokk art/def work, cast stays 5.
2. Resident Kreetle carries the owner's "arid type only" note — the webwork copy should depart; unpropagated leftover.
3. OPPORTUNITY: Chickenspider-as-juvenile gives the Wyyyschokk a brood ecology — eggs in the dark cells (ban 6 synergy). Rename owed (chicken).

## forsaken_crags — churn 4 (cast 14 → 14) — sitting 2026-09-10: AA_SandProwler + AA_Frostling OUT
Arrivals (2): AA_Behemoth (16 sq — distinct from trader-beast "Behemoth"), GR_Nighthrumbo.
1. Both fit the dark register (ban 6: no sun-dependent life). Watch the name collision AA_Behemoth vs homeless:Behemoth (trader pack animal) — two rosters, one word.
2. OPPORTUNITY: 16-square Behemoth as the thing you hear in the gust-dark — the cryptid register (§8) made flesh without showing the Forsakens.

## the_propane_lakes — churn 5 (cast 4 → 2) ⚠ NEAR-EMPTY
Arrivals (1): AA_AuroraSylph ("perfect Propane Lake creature"). Flier→roster: AA_Skyeel. Departures (3): FrostboundBehemoth (OPEN — "needs to totally alien life"), Slurrypede, Terramorph.
1. Two residents for the "most alien life in the cast" biome — the showcase is empty; FrostboundBehemoth's alien redesign is the only pipeline and it's OPEN.
2. OPPORTUNITY: admission test is strict (solvent-tolerant, ignition-safe) — commission 2-3 natives around AuroraSylph's aurora register rather than importing.

## the_blue_desert — churn 1 (cast 0 → 1) ⚠ NEAR-EMPTY
Arrivals (1): AA_Thunderbeast (electric — fits the detonation register).
1. One creature. The hydrocarbon-flora biome has no herbivore eating that flora (warm-detonation ban makes this a genuinely novel niche) — commission or route from the hot-biome OPEN pool (Barbslinger, ysalamir).

## weeping_stones — churn 1 (cast 10 → 9) — sitting 2026-09-10: ColossusToad OUT
1. AA_Eyeling's row here is the unresolved propagation conflict — "ocular" routes it to the Contagion; this copy likely departs. Decide at the sitting.
2. Dactillion is canonically a flying mount — flier-roster candidate never extracted.
3. OPPORTUNITY: Rycrit ("herd animal near oases") and Gullipud ("oases and pets") placement rules land here first — the oasis register is their obvious anchor.

## terminator_sea (standalone) — churn 0 (cast 0)
By design: the solitary-handful law lives in the two Deep sheets; only ColossalAerofleet (roster) passes over. Nothing owed.

## the_fever_wood — churn 5 (cast 11 → 12)
Arrivals (2): Tach, Rikknit (both-jungles ruling). Flier arriving→roster: BMT_FacetMoth. Flier extracted: Convor. Insect ruling: VFEI2_Megathrips out (faction-only).
1. Ban 3 (no native chase predators) holds — Tach steals, doesn't chase; Rikknit nests in crowns. Clean.
2. FacetMoth tension: the both-jungles ruling places it here, the flier extraction removes it — the flier roster needs a per-biome presence field to honor both.

## Skipped (zero fauna rows, no arrivals): wreck_fields, and the non-biome sheets (assailant_weapon_remnants, rosters/, gene lists).

---

## Cross-biome notes
- Flier-extraction stragglers not in the fliers list but flying by canon: Tibidee (forge), Dactillion (weeping_stones), Shyrack (desert — cave bat), VFEI2_Macrofly (arid), Neebray + Mynock (poison_forest/scarlands/fall_line — icons, appear in 3+ casts). One sweep against defs owed.
- 103 homeless needs-owner rows and the 22+ ninth-roster rows are not in any cast above; the near-empty biomes (propane_lakes, blue_desert, slime) should get first pick at those sittings.
- Size-bin data is the register's, unverified against defs; the arid LARGE-ban and dune-sea no-medium findings depend on it.
