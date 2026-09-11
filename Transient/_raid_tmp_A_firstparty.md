# First-party Star Wars proper-noun raid — deployed "mandrake" mods

Source: `/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/` (live deployed copies, the canonical live content per repo doctrine). Compiled 2026-09-11.

Legend:
- **SW-CANON** = a real Star Wars proper noun, per the mod's own label/description/comment text.
- **REIMAGINED** = a donor mod's non-SW-named creature/def relabeled with a new campaign-original name (general kind kept, specific name/character is NOT from Star Wars).
- **CAMPAIGN-ORIGINAL** = invented for this Utinni campaign, never Star Wars.
- **NON-SW DONOR** = absorbed wholesale from a non-Star-Wars donor mod, left as-is (not SW, not reimagined).

---

## Mod coverage summary

| Mod | Content found? |
|---|---|
| AnoobaArtOverride, DewbackArtOverride, DragonsnakeArtOverride, FambaaArtOverride, HoraxArtOverride, InsectomorphArtOverride, KreetleArtOverride, MynockArtOverride, RontoArtOverride, ZakkegArtOverride | Art-only reskins of real SW-canon creatures (no Defs/labels touched) |
| GritheArtOverride, GruttArtOverride, KroffaArtOverride, PuffmiteArtOverride | Art + label reskins of non-SW donor creatures into campaign-original names |
| SpidercatArtOverride | Art-only reskin, no label change at all — donor name untouched |
| LockjawArtOverride | Art-only reskin of a non-SW donor creature (Alpha Animals), partial (one of three variants) |
| RotSporeKit | Content found, but entirely campaign-original (fungal kit) — zero SW proper nouns |
| AshkarrLandmarkArt | Pure icon repaint of 48 existing landmarks, zero new names |
| IshkoDarkLandmarks | Content found, entirely campaign-original (Utinni pantheon) |
| TitanicCreatures | Pure engine mod, zero proper nouns |
| Armoury | **Huge SW-canon content** (KotOR factions/characters/crystals/weapons) |
| Droidworks | **Huge SW-canon droid roster** |
| DroidRepairJobs, ShipShields | Mechanism only, zero proper nouns |
| KotORBandolierNorthFix, MSEDroidFix | Art-fix only, no Defs; name real SW items in About.xml prose only |
| RestrainingBolts | Mechanism, one campaign-original faction reference |
| ShipVermin | References SWBestiary's Mynock only |
| ShipMemory | One flavor item, no SW canon names |
| EmpirePursuit | No proper nouns; references a campaign biome name |
| SWBestiary | **Huge content**, but mixed: real SW creatures + absorbed non-SW dinosaurs (mislabeled inside this mod) + absorbed non-SW cave fauna + campaign-original creatures |
| DesertVehicleReskin | No new creatures; reuses SW creature names as vehicle flavor |
| Shokk | One SW-adjacent species referenced (owned by a third-party mod, not this one) |
| StarWarsRaces | **~47-69 real SW playable species** enumerated |
| JawaIonWeapons | Campaign-original item only |
| JawaVoice | No XML proper nouns; About.xml cites real Ben Burtt Jawa-language phrases |
| JawaRules | Zero content beyond About.xml |
| StarWarsPatches | **Large content**: real SW species dev-stubs, canon food-plant renames, campaign-original factions/deities |
| Antiquities, Rites, PawnFlavor, Doctrine | Small amounts of content, mostly campaign-original; some real SW species/factions referenced in backstory flavor text |
| StrandedQuest, Oracle, RaidRedesigner, RustChrome, ProximityHatch, PlanetPresetPrime | Zero proper-noun content (pure mechanism/C#) |
| UtinniPatches | **Huge content**: campaign faction roster (mostly original leaders), real SW species/factions reused as flavor, real SW criminal syndicates in a name-generator table, Rakata reskin of Ancients |
| StructureInjectionsRUT | Real SW creature reference (Sarlacc) + Rakata/Forsaken quest-site lore, mostly campaign-original |
| StructureInjectionsSW | Not separately itemized by the fork beyond the RUT findings — treat as covered by UtinniPatches fork's structure-injection findings |
| StructureInjections | Empty (About.xml only) |
| MandrakePatches | Zero proper-noun content (bugfixes only) |

---

## Creature / Species

### Real Star Wars canon

| Name | Source | Note |
|---|---|---|
| Anooba | `AnoobaArtOverride/About/About.xml` | Art-only; "lean, hyena-like Jawa hunting/guard beast" |
| Dewback | `DewbackArtOverride/About/About.xml`; also `SWBestiary/Defs/ThingDefs_Races/RSW_Dewback.xml` | "native to the Dune Sea of Tatooine," desert reptile beast of burden |
| Dragonsnake | `DragonsnakeArtOverride/About/About.xml` | Art-only, full regen |
| Fambaa | `FambaaArtOverride/About/About.xml` | Art-only, adult facings only |
| Horax | `HoraxArtOverride/About/About.xml` | Art-only |
| Insectomorph | `InsectomorphArtOverride/About/About.xml` | Art-only; "native to Malastare" |
| Kreetle | `KreetleArtOverride/About/About.xml` | Art-only, adult facings only |
| Mynock | `MynockArtOverride/About/About.xml`; `SWBestiary/Defs/ShipVermin/ThingDefs_Races/RSW_Mynock.xml` | Canon ship-leech vacuum parasite; art redesigned "hideous wet practical-creature-effects," distended eyestalks |
| Ronto | `RontoArtOverride/About/About.xml` | Art-only; "the classic elephantine Jawa pack beast," both calf and adult stages |
| Zakkeg | `ZakkegArtOverride/About/About.xml` | Art-only; directed "lean, boney, and deeply disturbing" |
| Bantha | `SWBestiary/Defs/ThingDefs_Races/RSW_Bantha.xml`; also DesertVehicleReskin (bantha cart) | Canon Tatooine herd animal, Tusken mounts |
| Jerba | `SWBestiary/Defs/ThingDefs_Races/RSW_Jerba.xml` | About.xml notes a prior donor mod's "Jerbal" was NOT the real SW jerba — this is "the real one," Tatooine pack/milk beast |
| Acklay | `SWBestiary/Defs/ThingDefs_Races/RSW_Acklay.xml` | Vendaxa native, gladiatorial beast (Geonosis arena, AOTC) |
| Vulptex | `SWBestiary/.../RSW_Vulptex.xml` | Crait crystalline-coated canid (The Last Jedi) |
| Porg | `SWBestiary/.../RSW_Porg.xml` | Description is literally just "The Porg." (placeholder-quality flavor text) |
| Wampa | `SWBestiary/.../RSW_Wampa.xml` | Hoth predator |
| Nuna | `SWBestiary/.../RSW_Nuna.xml` | Naboo "swamp turkey" gamebird |
| Colo Claw Fish | `SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Colo.xml` | Naboo underworld creature (Episode I); "Abyssal colo"/"Thornback colo" morphs are invented, not canon |
| Opee Sea Killer | `SeaBeasts_Opee.xml` | Naboo (Episode I); "Crimson opee"/"Shale gorger" morphs invented |
| Sando Aqua Monster | `SeaBeasts_Sando.xml` | Naboo apex predator (Episode I); "Elder sando"/"Storm sando" morphs invented |
| Wyyyschokk | Referenced by `Shokk/Patches/RSW_Shokk_Wyyyschokk.xml` | Actual ThingDef lives in third-party `mlie.starwarsanimalcollection`, never absorbed into a first-party mod; Shokk only adds a ranged "spit" ability + hediffs |
| Ysalamiri / Ysalamir | `Armoury/Defs/Absorbed_AdditionalMods/kotorcore/VEF/Absorbed_Kotorcore_VEF_Ysalamiri.xml` | Correctly implements Force-nullification-field lore in its description |
| Sarlacc | Referenced only (not spawned) — `UtinniPatches/Defs/LandmarkDefs/RUT_GapingDoom.xml` | Landmark "the Gaping Doom" = a sarlacc's corpse-pit, now a waste dump |

### Non-canon reskins of donor creatures (campaign-original names)

| Name | Donor defName | Source | Note |
|---|---|---|---|
| Grithe | `GR_ParagonRat` (VanillaExpanded.VGeneticsE) | `GritheArtOverride/Patches/Grithe_LabelPatch.xml` | "Chitin-plated insectoid-rodent scavenger... oversized grasping forepaws." Not a literal rat, not SW. |
| Grutt | `GR_Molebear` (VanillaExpanded.VGeneticsE) | `GruttArtOverride/Patches/Grutt_LabelPatch.xml` | "Tusked, armor-plated burrower... blind but for vestigial eyes." Not SW. |
| Kroffa | `BMT_Maligoat` (BiomesTeam.BiomesPollutedLands) | `KroffaArtOverride/Patches/Kroffa_LabelPatch.xml` | "Six-legged plated desert grazer"; labelFemale "kroffa doe". Not SW. |
| Puffmite | `BMT_FleeceSpider` (BiomesTeam.BiomesCaverns) | `PuffmiteArtOverride/Patches/Puffmite_LabelPatch.xml` | "Filament-tufted, crystalline/bioluminescent tiny arachnid." Not SW. |
| Spidercat | `GR_Spidercat` (vanillaexpanded.vgeneticse) | `SpidercatArtOverride/About/About.xml` | Art-only — no label patch at all, donor's own in-game name is untouched. "Spidercat" is only this mod's dev-facing name. Not SW. |
| (untouched) AA_Lockjaw / brown variant styled a whale-alligator hybrid | `AA_Lockjaw` (sarg.alphaanimals) | `LockjawArtOverride/About/About.xml` | Not SW at all (Alpha Animals donor). Only the brown `AA_Lockjaw3` variant fully art-regenerated; grey `AA_Lockjaw2` south facing deferred (failed validator 5×); bare variant untouched. |

### Absorbed non-SW donor fauna hiding inside SW-named mods (notable divergence)

| Name | Source | Note |
|---|---|---|
| Diplocaulus, Segnosaurus, Platyhystrix, Protovermes, Protosolpuga, Baseopsis, Termitotron, Holcorobeus | `SWBestiary/Defs/ThingDefs_Races/RSW_Absorbed_*.xml` | **NOT Star Wars** — dinosaurs absorbed from "Jurassic Rimworld," with in-game descriptions literally styled as "INGEN INTERNAL CASE FILE"/"BIOSYN" corporate lore. Living inside a mod named "SW Bestiary." |
| ~70 generic cave/biome creatures (Pod Worm, Royal Rhino Beetle, Yooka, Pustule Hornet, Maligoat, Fleece Spider, Thrumbungus, Gastro Toad, Basilisk, Crested Dragon, etc.) | `SWBestiary/Defs/BiomesTeamPort/` | Absorbed from BiomesTeam mods — zero Star Wars content despite living in the Bestiary mod |
| Mee/Faa/Laa scalefish, "faynaa" (Gungan-flavor term) | `SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Scalefish.xml` | Invented Naboo-flavor fish family — NOT real SW canon despite the Naboo theming |
| landopus/cephalope/nautilant | `UtinniPatches/Defs/Absorbed_Cephaloids/` | Non-SW donor mod fauna |
| megatardi | `UtinniPatches/Defs/Absorbed_VAEWasteMegatardi/` | Non-SW donor mod (VAE Waste) |

### Campaign-original creatures (not Star Wars)

Fire-hawk (`RUT_FireHawk`) and furnace-beast (`RUT_FurnaceBeast`) — Ash'karr Pyrelands natives, `UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`. Also Karrask, Onnik, Cindermare, Skarnix, SandStalker, Tellurox, Ikee (SWBestiary scope, exact files not itemized by the fork) — all Utinni-original.

**RotSporeKit** (16 files, `RUT_` prefix): entirely campaign-original fungal-warfare content — drugs (ambrosyx shroom), 19 flora species (skulltop, dewshrooms, nuitae, wrinklecap, arpeau, nogtyl, flakespire fungus, pusmelon, rustpuff, sagecrust, bleeding tooth, crimson cap, Grey Lady, shine cap/glimmerslime, shinebell, violet wimple, mortal morel, moonless stripes, dulcis, blastpod shroom/blast spore sac), weapons (fungal mantis scythe, thrumbungus mushroom). Zero SW proper nouns.

**TitanicCreatures**: pure engine mod (multi-cell footprint/crush/corpse-harvest); no creature wired to it here, zero proper nouns.

---

## Character

| Name | Faction/context | Source | Note |
|---|---|---|---|
| Darth Malak, Darth Revan, Darth Nihilus, Darth Sion, Darth Traya (Kreia), Exar Kun, Darth Malgus | Sith | `Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Apparel/Absorbed_KotorWeapons_Apparel_ImmortalusSithLords.xml` | Named hero apparel sets (tunic/mask/cloak per character) |
| Visas Marr, Jolee Bindo, Bastila Shan, Juhani | Jedi/companions | `Absorbed_KotorWeapons_Apparel_KotORHeroApparel.xml` | Named hero apparel ("Visas' hood/robes", "Jolee's Tunic") |
| Lando Calrissian | — | `Absorbed_KotorWeapons_GadgetApparel_KotORBelts.xml` | "Calrissian's utility belt" |
| Ulic Qel-Droma | Sith/Jedi (Old Republic era) | same | "Qel-Droma belt" |
| HK-47 | Droid/assassin | `Absorbed_KotorWeapons_WeaponRanged_KotORDisruptorRifle.xml` | "HK-47's Assassin Rifle" |
| Mandalore, Cassus Fett, Bendak Starkiller, Freedon Nadd, Jurgan Kalta, Jamoh Hogra, Mira, Mission Vao, Sanasiki, Zaalbar, Yusanis, Ordo, Carth Onasi, Bacca, Luxa | Various KotOR-era | named-weapon labels across `Absorbed_KotorWeapons_WeaponRanged/Melee_KotOR*.xml` | Each is a unique named weapon ("X's [weapon]") |
| G0-T0 (GOTO) | Droid | `Droidworks/Defs/Races_KotOR.xml` (`guy762_DroidRace_GOTO`) | Canon KotOR2 unique character, genericized into a droid kind |
| HK-50/HK-51 series | Droid | `Droidworks/Defs/Races_KotOR.xml`, `PawnKinds_KotOR.xml` | HK-47 lineage, genericized into droid-model lines |
| Emperor Palpatine | Galactic Empire | `UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml`; `Patches/GalacticEmpire.xml` | Leader-kind label; nameType also "He Who Is Rising" |

### Campaign-original faction leaders (not Star Wars, listed for completeness — `UtinniPatches/Defs/PawnKindDefs/JawaFactionRoster.xml`)

Lord Gorga the Immense (Hutt Cartel), High Marshal Taren Voss (Homestead Defense League), War Chief Torr'gan (Deep Desert Tribes), First Speaker R-41 Rell (Free Droid Enclaves), Archduke Korrik the Shaper (Geonosian Foundry Hive), Director Ko Saiyan (Ascendant Helix), Captain Jaxen Marr (Blackstar Company), Elder Rroowaak (Wildsteam Clan), High Warden Neris Cal (Deepwater Compact), First Bargainer Kiknik the Wealthy (Jawa Trade Moot), Scraplord Tarn Vox the Brutal (Junkers).

---

## Faction / Organization

### Real Star Wars canon

| Name | Source | Note |
|---|---|---|
| Jedi Order | `Armoury/.../KotORFactions_Jedi.xml` | Generic apparel line |
| Sith (incl. Apprentice/Assassin/Warrior/Marauder/Trooper/Commando ranks) | `.../KotORFactions_Sith.xml`, `SithMilitary.xml` | Full trooper-rank apparel ladder; "Star Forge" final assault mentioned |
| Mandalorian (Neo-Crusader, Supercommando) | `.../KotORFactions_Mando.xml` | Mandalorian War, Exar Kun war references |
| Galactic Republic (incl. Republic Commando, Civic Security/TSF) | `.../KotORFactions_OldRep.xml` | |
| Czerka Corporation | `.../KotORFactions_Czerka.xml`; also `Droidworks/Items_Droidworks.xml` | Laborer/officer/enforcer apparel; canon droid-armor tier labels |
| Hutt Cartel(s) | `.../KotORFactions_Scum.xml`; `UtinniPatches/Defs/FactionDefs/JawaHuttCartel.xml` | Foot-soldier "Tantel Helmet/Armor," "in use for ten thousand years"; alt name "the Ledger"/"That Which Does Not Forgive" |
| The Exchange | `.../KotORFactions_Scum.xml`, KotORBelts/Gloves/StealthBelts | Criminal syndicate; "Exchange Shadow Caster" stealth unit |
| Rakata / Rakatan | `Armoury/Patches/Turrets_Renames.xml`; `UtinniPatches/Patches/AncientsAreRakata.xml`; `StructureInjectionsRUT` | Ancient precursor race; reskins the game's vanilla "Ancients" faction; "Forsaken" is the campaign's label for their soldiers/vaults |
| GenoHaradan | `Armoury/.../WeaponRanged_KotORBlasterPistol.xml`, StealthBelts | Assassins' guild |
| Tenloss (Syndicated Armaments), Systech, Aratech, Kajidic | `Armoury/.../WeaponRanged_KotOR*.xml` | Arms manufacturers/cartel-adjacent terms, named on weapon labels |
| Galactic Empire | `UtinniPatches/Patches/GalacticEmpire.xml`; `PawnFlavor/Defs/Backstories_Empire_Hutt.xml` | Reskinned vanilla Royalty/Empire faction; leaderTitle Emperor; stormtrooper garrison/deserter backstories |
| OuterRim_RebelAlliance | `UtinniPatches/Patches/RebelAlliance_Suppress.xml` | From donor "OuterRim" mod; this patch suppresses it (not active in campaign) |
| Ohnaka Gang, Crimson Dawn, Black Sun, Kanjiklub | `UtinniPatches/Defs/RulePackDefs/Namer_PirateSyndicates.xml` | Real SW criminal syndicates used as a pirate-name generator's rules strings ("Nova Blades" alongside them appears to be campaign-original) |
| Bounty Hunters' Guild (concept, not the exact name) | `PawnFlavor/Defs/Backstories_Geonosian_Helix_Blackstar.xml` ("the Company"/"the Code") | Flavor text alludes to the real SW guild concept using campaign-original naming |

### Campaign-original factions (not Star Wars — listed for completeness)

Ascendant Helix, Deepwater Compact, Free Droid Enclaves, the Junkers, Jawa Trade Moot, Wildsteam Clan, Homestead Defense League (alt "the Withdrawn"), Deep Desert Tribes, the Forgotten Arsenal, Blackstar Company (vanilla Pirate faction reskin), Geonosian Foundry Hive (uses the real SW species/planet name "Geonosian" but the faction itself is original), the Helix (Geonosian gene-cult flavor name), "Free Droid Enclaves"/"Junker" culture (RestrainingBolts, Droidworks). Deity/pantheon names: Ishko the Unmaskable, Sh'kaar, Ohm (the All-Current) — the campaign's "Nine gods." "The Assailant" — a campaign-original ancient antagonist entity (Antiquities).

---

## Planet / Location

### Real Star Wars canon

| Name | Source | Note |
|---|---|---|
| Kessel | `StarWarsPatches/Patches/PlantNames_CanonSW.xml` (comment) | Source of "kessel grain" (corn) |
| Naboo | same | Source of "shuura" fruit |
| Tatooine | same; `Armoury` weapon/vehicle labels | Source of "pallie berry"; desert beasts (dewback/bantha/ronto) called "Tatooine beasts" |
| Mimban | `PlantNames_CanonSW.xml` | Source of "mimbanese cacao"/"mimbanese sweet" |
| Gamorr | `StarWarsPatches/Defs/XenotypeDefs/GamorreanXenotype.xml` | Named in-text as Gamorreans' homeworld |
| Nar Shaddaa | `Armoury/.../WeaponRanged_KotORMicroRepeater.xml` | "Nar Shaddaa Grinder" |
| Onderon | `Armoury/.../WeaponRanged_KotORLightRepeater.xml` | "Onderon Repeating Carbine" |
| Taris | `Armoury/.../GadgetApparel_KotORGloves.xml` | "Taris survival gloves" |
| Cinnagar | `Armoury/.../WeaponRanged_KotORSlugRifle/Carbine`, `HelmetLgtBattle` | "Cinnagar War Helmet" — an invented KotOR-era world name, not mainline-film canon but part of the Old Republic corpus |

### Campaign-original (not Star Wars, listed for completeness)

Ash'karr (the campaign's fixed world — already documented elsewhere in the repo). Sophiamunda — "techno-feudal culture centered on the planet Sophiamunda," the campaign's own Empire homeworld (`UtinniPatches/Defs/CultureDefs/JawaLeaderTitles.xml`), not a real SW planet. Numerous campaign-original sub-locations/biomes (the Rust Cathedral, the Scorch, the Fall Line, Deadstone, the Slough, the Umbra vault, the dark tower, the ancient war lab, the Rot, the Propane Lakes, the Blue Desert, the Forsaken Crags, the Cracked Lands, the Poison Forest, the Weeping Stones, the Pyrelands, the Greentide, the Contagion, the Webwork, the Slime, the Miasma, the Sump, the Fever Wood, the Forge, the Gaping Doom, Lightfall, the gelatinous breach) — `UtinniPatches`.

---

## Ship

| Name | Source | Note |
|---|---|---|
| YT-1300 transport | `Armoury/Defs/Absorbed_AdditionalMods/kotorcore/BTDKotORGravships/Absorbed_Kotorcore_BTDKotORGravships_Buildings_SWGravshipInteriorPieces.xml` | Real canon ship class (the Millennium Falcon's model); used only for a pilot-console building defName |
| Dynamic-class freighter | `.../Gravship_DynamicFreighter.xml` | Not clearly real SW canon — likely donor-invented ship class |
| KT-400 freighter | `.../Gravship_KT400Freighter.xml` | Not identifiable as real SW canon — likely donor-invented |
| the Kolyska | `UtinniPatches/Defs/FactionDefs/JawaTribes.xml` | The player's own gravship — campaign-original, not Star Wars |
| wrecked landspeeder | `StarWarsPatches/Patches/PodCarIsLandspeeder.xml` | Reskin of Vanilla Expanded Core's `AncientPodCar` — real SW vehicle-class name (landspeeder) applied via label/description/texPath only |

---

## Item / Artifact

### Real Star Wars canon

| Name | Source | Note |
|---|---|---|
| Star Forge (Robes/Mask/Cloak) | `Armoury/.../Absorbed_KotorWeapons_Apparel_ImmortalusSithLords.xml` | Named after the KotOR superweapon/factory |
| Kaiburr Crystal | `.../HiltPartDefs_KotORFocusingCrystals.xml` | Real Force-crystal artifact |
| Krayt Dragon Pearl | `.../HiltPartDefs_KotORPowerCrystals.xml` | Real crystal harvested from a Krayt Dragon corpse |
| Adegan, Rubat, Ruusan, Velmorite, Sigil, Nextor, Kasha, Eralam, Damind, Sapith, Opila, Upari, Lorrdian Gemstone, Ankarres Sapphire | Focusing Crystal list, same file | Real named SW lightsaber-crystal types |
| Jenurax, Luxum, Bondar, Dragite, Firkann, Pontite, Stygium, Ultima Pearl, Barab Ore Ingot, Hurrikaine, Artusian, Qixoni, Solari | Power Crystal list, `HiltPartDefs_KotORPowerCrystals.xml` | Real named SW lightsaber-crystal types |
| Mantle of the Force, Heart of the Guardian | Color Crystal list | Named unique SW lightsaber crystals |
| Bowcaster (incl. "Zaalbar's Bowcaster", "War/Ceremonial/Mercenary Bowcaster") | `.../WeaponRanged_KotORBowcaster.xml` | Real SW Wookiee weapon |
| E-Web (repeating blaster) | `Armoury/Defs/ThingDefs/Absorbed_Eweb.xml` | Real SW heavy weapon |
| Thermal Detonator | `Absorbed_JDSArmory_*` | Real SW grenade type |
| DC-15A/S/x, DC-17/17M/17S, E-5/5C/5S, SE-14, Westar-33/34/35/44/M5, Amban sniper rifle, Z6 Rotary Blaster Cannon | `Absorbed_JDSArmory_Weapons.xml` | Real, correctly-named canon SW blaster model numbers (clone-trooper/bounty-hunter armory) |
| "Whistling Birds" launcher | `Absorbed_KotorWeapons_GadgetApparel_KotORMountedWeapons.xml` | Real named KotOR wrist-launcher (Mandalorian tech, in-universe quoted name) |
| Arg'garok (Gamorrean axe) | `UtinniPatches` GamorreanPawnKinds.xml comment (`guy762_gamorreanaxe`) | Canon-named Gamorrean weapon; **bug noted**: no weapon def actually carries the matching `HC_gamorreanaxe` tag, so it's a naming reference only |
| M'uhk'gfa | same file (`guy762_HvyArmor_gamorrean`) | Canon-named Gamorrean battle harness/armor |
| Kajidic Soldier's Axe | same file (`guy762_vaxe_hutt`) | "Kajidic" = real SW term for a Hutt crime clan |
| kessel grain, kibla grain, koyo tuber(s), pallie berry, muja bramble, ardees, shuura bush, mimbanese sweet, mimbanese cacao, bantha fodder | `StarWarsPatches/Patches/PlantNames_CanonSW.xml` | Canon-tier food renames (owner ruling: inspected/traded food gets canon names) — contrast with the deliberately invented background-flora names (silkstrand, reed-cane, duskspire, bloodleaf, ironbough, fanleaf palm, hardgrain, weepvine) |

### Notable divergence

- **`Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Weapons/Absorbed_KotorWeapons_lightsabernames.xml`** (RulePackDef `NamerWeaponLightsaber`): its entire name list — Terra, Locke, Edgar, Sabin, Shadow, Cyan, Gau, Celes, Setzer, Strago, Relm, Mog, Gogo, Umaro, Gestahl, Kefka, Maduin, Siren, Cait Sith, Kirin, Ramuh, Ifrit, Shiva, Carbuncle, Bismarck, Phantom, Unicorn, Catoblepas, Golem, Zona Seeker, Fenrir, Lakshmi, Quetzalli, Phoenix, Ragnarok, Valigarmanda, Midgarsormr, Alexander, Odin, Raiden, Bahamut, Crusader — **is entirely Final Fantasy VI character/esper names, not Star Wars.** A leftover generic namer table from the donor mod's template, currently wired to generate in-game lightsaber names for this campaign.
- `RSW_RN2SWGun_EWebMounted_GPMG` is labeled "M60" — a real-world (non-SW, non-fictional) weapon name.
- `Armoury/Patches/Turrets_Renames.xml`: SW-flavored engine-only renames of third-party turrets (tesla arc projector, helical charge railgun, ion surge column, "ancient beam cannon" tied to the Rakatan-relic reskin) — relabeling only, not new defs.

### Campaign-original

Jawa Ion Blaster, ion bolt (`JawaIonWeapons`) — Utinni-original, not SW canon despite the "Jawa" name. Shokk mouth-loom, web-silk glob (`Shokk`) — Utinni-original mechanic riding the (real, third-party-owned) Wyyyschokk species.

---

## Other / notable

- **JawaVoice** carries no new proper nouns in XML, but its About.xml quotes real Ben Burtt-created Jawa-language phrases used verbatim: *Utinni!*, *M'um m'aloo*, *Ibana*, *Nyeta*, *Taa baa*.
- **KotORBandolierNorthFix** and **MSEDroidFix** are pure art-fix mods with no Defs, but their About.xml text names real SW items/droids: `bandolier_chewbacca`, `bandolier_traveler` (Chewbacca reference) and the MSE-6 droid.
- **StarWarsRaces** (15 files) enumerates a very large real-SW-species roster (About.xml claims 69 total; ~47 directly confirmed via XenotypeDefs/PawnKindDefs): Abednedo, Anzati, Aqualish, Arkanian, Bith, Bothan, Cathar, Cerean, Chadra-Fan, Chagrian, Chiss, Dathomirian, Defel, Devaronian, Duros, Echani, Ewok, Falleen, Feeorin, Gamorrean, Gand, Geonosian, Gungan, Herglic, Hutt, Iktotchi, Iridonian, Ithorian, Kaleesh, Kaminoan, Kel Dor, Klatoonian, Kubaz, Lasat, Mimbanese, Mirialan, Mon Calamari, Muun, Nagai, Nautolan, Neimoidian, Nelvaanian, Nikto, Ortolan, Pantoran, Pyke, Quarren, Rakata, Rodian, Selkath, Sith Kissai/Massassi/Zugurak (Pureblood), Snivvian, Sullustan, Taung, Togorian, Togruta, Trandoshan, Tusken, Twi'lek, Ugnaught, Umbaran, Weequay, Wookiee, "Yoder" (nicknamed "force gremlin," an unnamed canon species), Zeltron, Zygerrian. Also RSW_MandrakeJawa — the campaign's own authored Jawa xenotype ("clan aboard the Kolyska"), campaign-original despite living in this list. Several entries have placeholder/empty descriptions (Defel, Gand, Hutt="e", Kubaz="e", Lasat="e", Mimbanese="e", Taung=".", Ugnaught=".").
- **StarWarsPatches/Defs/PawnKindDefs/AlienSpawnEnablers.xml** adds real-SW-species dev-spawn stubs (no full faction integration) for: Hutt, Gand, Kubaz, Taung, Mimbanese, Zygerrian, Lasat, Muun, Ortolan, Nelvaanian, Sith (Kissai/Massassi), Yoder. Comments note 81 loaded factions were checked and none matches hutt/cartel/crime/pyke/slaver/black-sun — i.e. no Hutt Cartel faction actually exists in the live stack despite the species stub.
- **Gamorrean** (`StarWarsPatches/Defs/XenotypeDefs/GamorreanXenotype.xml`, `RSW_Jawa_Xeno_Gamorrean`) has a self-admitted canon divergence in its own comments: real Gamorreans are 1.3-1.6m (shorter than human) but the def inherits `guy762_BodySizeGene_big` (taller) — flagged, deliberately unresolved.
- **Rakata** backstory (`PawnFlavor/Defs/Backstories_Rakata_Sleepers.xml`) reimagines them as "the last Rakata," a dying civilization fighting a losing war and terraforming — a divergent invented history layered onto the real species, not from any def, backstory-flavor only.
- **Geonosian** backstory (`PawnFlavor/Defs/Backstories_Geonosian_Helix_Blackstar.xml`) invents hive/brood-warrens, a winged nobility caste, and foundry/droid-builder culture as flavor — again backstory-only extrapolation on a real species, not contradicting canon so much as filling gaps.
- Droid designation prefixes drawn from real canon naming conventions (`Armoury/Defs/Absorbed_AdditionalMods/kotorcore/RulePacks/Absorbed_KotorCore_RulePacks_DroidNameMakers.xml`): R2, R3, R4, R5, B1, DUM, 21B (2-1B medical droid), LOM, 3PO (C-3PO line), TC, RA-7 ("Death Star droid"), CLLM2, ASP7.
- Full canon droid-model roster (all real SW designations, verbatim labels — `Droidworks/Defs/PawnKinds_JDS/KotOR/OuterRim/Primitive.xml`): AQ Battle Droid, B1 Battle Droid, B1 Commander Droid, B1 Security Droid, B1A Battle Droid, B2 HA Super Battle Droid, B2 Super Battle Droid, BX Commando Droid, DSD1 Dwarf Spider Droid, DUM Repair Droid, Destroyer Droid, Droideka Droid, Droideka Sharpshooter Droid, IG-100 MagnaGuard, KX Security Droid, MSE Repair Droid, MagnaGuard Droid, Muckraker Crab Droid, R-Series Droid, ST/T-Series/T1 Tactical Droid, T3 unit, FX-7 medical droid, GNK power droid, protocol droid, LR-57 Combat Droid, Pistoeka Sabotage Droid, KM1-series (mining/excavation), GE3-series, IT-series, R-8009 series, Sentinel-class war droid, Devastator-class assassin/war droid, Municipal Patrol Droid Mk I, Assault Droid Mk I/IV/IV-Type-B, Star Forge Assault Droid.
- Droid-brain manufacturer names (real SW canon): Industrial Automaton, Cybot Galactica, Arakyd (`Droidworks/Defs/ThingDefs/BrainTrio_Droidworks.xml`). Droid armor-plating materials: Agrinium, Desh, Quadranium (`Items_Droidworks.xml`).
- Droid "ownership protocol" flavor text references Empire/Imperial and Hutt factions (`Droidworks/DataSpikes_Droidworks.xml`); "Free Droid Enclaves" and "Junker" are campaign-original factions/cultures referenced in the same droid content.
- Gand, Geonosian, Kaleesh (Grievous's species), Verpine, Arkanian, Gree, Bothan, Trandoshan, Zabrak, Nagai, Dashade appear throughout `Armoury`'s KotOR-weapon files as species-flavored weapon/shield/headgear lines (e.g. "Gand Shockstaff," "Geonosian Electrostaff," "Kaleesh Battle Rifle," "Verpine ocular enhancer," "Gree hypershield") — all real SW species, used as adjectival flavor on items rather than as spawnable pawns in this scope.
- Quarren and Mandalorian and Tusken raider/brute/marksman appear as unit-rank labels inside otherwise campaign-original UtinniPatches factions (Deepwater Compact "Quarren shipwright," Blackstar Company "Mandalorian" heavy trooper, Deep Desert Tribes' Tusken ranks) — real SW names reused as flavor labels on original factions.
