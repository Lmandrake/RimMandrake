# Homeless-row bucketing — reserved groups triage

Source (read-only): `design/Jawa/worldbuilding/review/fauna_assignment_register.decisions.json`. 486 rows keyed `homeless:<def>`. Bucketed against the 8 reserved groups (see `reserved_groups_draft.md`) and the boom-family cut, in that priority order: CLAIMED-BY-GROUP first, then CUT-BOOM, then a 3-way proposal on what's left (cut / reserve-pool / needs-owner). A 4th, non-instructed category — **resolved-by-note** — is reported separately below for honesty: these rows already carry a clear owner placement note (a biome or a general rule) and are neither cut, reserved, nor awaiting an owner call; folding them into needs-owner would overstate how much attention they need.

## Counts

- homeless total: 486
- CLAIMED-BY-GROUP: 36
- CUT-BOOM: 13
- remainder: 437
  - cut (decision=out, no group claim): 206
  - needs-owner (decision in/move, empty note — no signal at all): 103
  - resolved-by-note (decision in/move, note gives a placement — not one of the 3 instructed buckets, listed for completeness, no action needed here): 128
  - reserve-pool (remainder rows newly proposed as reserve-pool): 0 — every explicit reserve-pool hedge among homeless rows was already captured under CLAIMED-BY-GROUP (PoisonButterfly, §8 of reserved_groups_draft.md).

## CLAIMED-BY-GROUP (36)

| creature | claimed by | decision | owner's words |
|---|---|---|---|
| AA_AngelMoth | fliers(inferred) | move | Rot |
| AA_AngelMothLarva | fliers(inferred) | move | Wildsteam biomes |
| AA_ColossalAerofleet | fliers(inferred) | move | rare creature wherever normal aerofleets end up |
| AA_EmpressButterfly | fliers(inferred) | move | Wildsteam areas |
| AA_EmpressButterflyLarva | fliers(inferred) | move | Wildsteam biomes |
| AA_EngorgedTentacularAberration | dungeon-guardians(inferred) | in | Assailant |
| AA_Locusts | fliers(inferred); event-only(explicit) | in | 0.1 cell, smallest critter in huge numbers, eats plants ravenously and won't stop, event |
| AA_Skyeel | fliers(explicit) | move | Electrostatic flyer over Propane Lakes |
| AA_SmallButterfly | fliers(inferred) | in | 0.2 cell, flits around the arid shrubland |
| AA_UnblinkingEye | dungeon-guardians(inferred) | in | assailant |
| Aiwha | fliers(explicit); mounts-and-work-beasts(explicit) | move | HUGE flyer, could appear anywhere, mountable, air, sea, land, Helix territories |
| BMT_BloodropMoth | fliers(inferred) | out |  |
| BMT_FacetMoth | fliers(inferred) | move | Make it brightly colored and put it in the jungle |
| BMT_FacetMothLarvae | fliers(inferred) | move | crystal caverns |
| BMT_FacetMothPupa | fliers(inferred) | in |  |
| BMT_FamineLocust | fliers(inferred) | out |  |
| BMT_Megabat | fliers(inferred) | out |  |
| BMT_SmogMoth | fliers(explicit) | move | Neat flier in the Rot |
| BMT_SmogMothLarvae | fliers(inferred) | out |  |
| BMT_Woollybat | fliers(inferred) | out |  |
| Behemoth | trader-beasts(explicit); mounts-and-work-beasts(explicit) | in | huuuge trader pack animal |
| Bogwing | fliers(explicit) | move | miasma flyer |
| Drone_Wasp | fliers(inferred) | out |  |
| GR_AberrantFleshbeast | dungeon-guardians(inferred) | in | Assailant territory |
| GR_FleshFlies | fliers(inferred) | in |  |
| GR_FleshGrowth | dungeon-guardians(inferred) | in | assailant |
| GR_FleshMonstrosity | dungeon-guardians(inferred) | in | assailant |
| GiantAnt_Race | event-only(explicit) | move | Only the raiding events in the greentide jungles and surrounding area |
| Insectomorph | mounts-and-work-beasts(explicit) | in | ridable mount associated with the Drug, found near Hutt settlements |
| Locust | fliers(inferred) | out |  |
| Maalraas | event-only(explicit) | in | 3 cells, dangerous, ability to cloak and hunt, dangerous event |
| PoisonButterfly | fliers(inferred); reserve-pool(explicit) | in | Maybe a pet for beauty? |
| Stintaril | event-only(explicit) | in | Hideous vermin that can appear literally anywhere, especially injected wrecks, settlements, or attempting to infest the player's ship in events. 1 cell |
| VFEI2_Gigalocust | fliers(inferred) | in |  |
| VFEI2_Megawasp | fliers(inferred) | in |  |
| Vulture | fliers(inferred) | out |  |

## CUT-BOOM (13)

| creature | decision | owner's words |
|---|---|---|
| Boomrat | out |  |
| GR_Bearalope | in | follow the boom beasts |
| GR_Boomabear | out |  |
| GR_Boomalisk | out |  |
| GR_Boombeetle | in | go with the boom |
| GR_Boomcat | in | go with the boom |
| GR_Boomffalo | out |  |
| GR_Boomsnake | move | Pyrelands |
| GR_Boomsquirrel | in | with the boom creatures |
| GR_Chickenlope | in | goes along with the other boom creatures |
| GR_Manalope | in | wherever the boom creatures go |
| GR_ParagonBoomalope | in | with the boom |
| GR_Squirralope | in | with the other boom creatures |

## Remainder — proposed CUT (206, decision=out, unclaimed)

These already carry `decision: out` — posture is blacklist, so out on a homeless row means cut for real. This proposal is a restatement of the register's own posture, not a new call.

| creature | owner's words |
|---|---|
| AA_Animalisk |  |
| AA_ArcticLion |  |
| AA_Bobeene |  |
| AA_ChameleonYak |  |
| AA_ChemfuelMyrmidon |  |
| AA_DunealiskClutchMother |  |
| AA_FeraliskClutchMother |  |
| AA_FissionMouseSecond |  |
| AA_FissionMouseThird |  |
| AA_FrostAve |  |
| AA_GreyCoatedMouflon |  |
| AA_Junglelisk |  |
| AM_UnshackledDryad |  |
| Alpaca |  |
| AlphaThrumbo |  |
| BMT_BarbedPangolin |  |
| BMT_Batbird |  |
| BMT_BeardedYak |  |
| BMT_BiliousVarog |  |
| BMT_CactusCrab |  |
| BMT_CaveCricket |  |
| BMT_CrystalBeetle |  |
| BMT_CrystalMantis |  |
| BMT_Crystalope |  |
| BMT_FenridStoat |  |
| BMT_FireSalamander |  |
| BMT_FreezerFrog |  |
| BMT_FrostweaverSpider |  |
| BMT_FungalFerret |  |
| BMT_GastroToad |  |
| BMT_GoetoTadpole |  |
| BMT_HoarfrostMastodon |  |
| BMT_HungeringHydra |  |
| BMT_MaceDrake |  |
| BMT_Maxolotl |  |
| BMT_Megaroach |  |
| BMT_MetalloSnail |  |
| BMT_Molebear |  |
| BMT_MossyFennec |  |
| BMT_Rimebeak |  |
| BMT_RoyalRhino |  |
| BMT_ShatterjawBeetle |  |
| BMT_ShimmershellSnail |  |
| BMT_SilverSheep |  |
| BMT_SludgeCrawler |  |
| BMT_SmolderstingScorpion |  |
| BMT_Snowstalker |  |
| BMT_Swarmcaller |  |
| BMT_TaintedTurtle |  |
| BMT_TripleSnapper |  |
| BMT_Varmot |  |
| BMT_Xyrion |  |
| Bardelot |  |
| Bear_Grizzly |  |
| Bear_Polar |  |
| Bison |  |
| Boarwolf |  |
| Bullfrog |  |
| Caribou |  |
| Chicken |  |
| Chinchilla |  |
| Cougar |  |
| Cow |  |
| DA_Barog |  |
| DA_Crestel |  |
| DA_DwarvenMuffton |  |
| DA_Goldilox |  |
| DA_ImperialRedhound |  |
| DA_IroncasketBeetle |  |
| DA_Karabal |  |
| DA_LeviathanCrab |  |
| DA_NorthernDrog |  |
| DA_Phrak |  |
| DA_Pilgrim |  |
| DA_RedhornedLarpah |  |
| DA_Snaptoad |  |
| DA_SnowTaraal |  |
| DA_Taraal |  |
| Deer |  |
| Donkey |  |
| Dromedary |  |
| Drone_Hunter |  |
| Drone_Sentry |  |
| Duck |  |
| ERN_Amaro |  |
| Elasmotherium |  |
| Elephant |  |
| Elk |  |
| Fox_Arctic |  |
| Fox_Red |  |
| GR_ArchotechCentipede |  |
| GR_Bearcat |  |
| GR_Bearffalo |  |
| GR_Bearodile |  |
| GR_Catalope |  |
| GR_Catchicken |  |
| GR_Crocorse |  |
| GR_Groundffalo |  |
| GR_Manffalo |  |
| GR_Manwolf |  |
| GR_MeadowLizard |  |
| GR_Mechabear |  |
| GR_Mechahorse |  |
| GR_Mechalope |  |
| GR_Mechamime |  |
| GR_Mechamuffalo |  |
| GR_Mechaspider |  |
| GR_Mechaturtle |  |
| GR_Muffalokomodo |  |
| GR_Muffalope |  |
| GR_Muffalopede |  |
| GR_Muffalorat |  |
| GR_ParagonMuffalo |  |
| GR_Ratffalo |  |
| GR_Spiderhorse |  |
| GR_Thrumbalope |  |
| GR_Thrumbear |  |
| GR_Thrumbocat |  |
| GR_Thrumbochicken |  |
| GR_Thrumbolizard |  |
| GR_Thrumboman |  |
| GR_Thrumborat |  |
| GR_Thrumbospider |  |
| GR_Thrumdraeodon |  |
| GR_Thrumffalo |  |
| GR_Thrumhorse |  |
| GR_Wolfhorse |  |
| GRimBullfrog |  |
| GRimLavaSnail |  |
| GRimStoneCrab |  |
| GRimTortoise |  |
| GiantToad |  |
| Giantala |  |
| Gigantelope |  |
| Goat |  |
| Gomphotaria |  |
| Goose |  |
| GuineaPig |  |
| Hare |  |
| HermitCrab |  |
| Horse |  |
| Ibex |  |
| Iguana |  |
| JRWArchaeopteryx |  |
| JRWArthropleura |  |
| JRWBagaceratops |  |
| JRWBaseopsis |  |
| JRWBernicia |  |
| JRWBrachytrachelopan |  |
| JRWCaihong |  |
| JRWDilophosaurus |  |
| JRWDiplocaulus |  |
| JRWEuoplocephalus |  |
| JRWEuphoberia |  |
| JRWGeosternbergia |  |
| JRWGeralinura |  |
| JRWGorgonops |  |
| JRWHynerpeton |  |
| JRWIschigualastia |  |
| JRWMacrelcana |  |
| JRWManipulator |  |
| JRWMeganeura |  |
| JRWNyctosaurus |  |
| JRWPlatyhystrix |  |
| JRWProtosolpuga |  |
| JRWProtovermes |  |
| JRWPteranodon |  |
| JRWPulmonoscorpius |  |
| JRWQantassaurus |  |
| JRWQuetzalcoatlus |  |
| KingToad | likely retire this mod |
| Larva |  |
| Lynx |  |
| MA_Aminox |  |
| MA_Deermoss |  |
| MA_Gnaut |  |
| Megaloceros |  |
| Megascarab |  |
| Megasloth |  |
| Megasquid |  |
| Megavole |  |
| Monkey |  |
| Muffalo |  |
| Panther |  |
| Pig |  |
| Quail |  |
| Rabbuck |  |
| Raccoon |  |
| Rhinoceros |  |
| Sheep |  |
| Snowhare |  |
| Squirrel |  |
| TYR_Lemming |  |
| ThrumbaToad |  |
| Thrumbo |  |
| Turkey |  |
| VAEWaste_Toxiguana |  |
| VRE_CompanionDryad |  |
| WasteRat |  |
| WildBoar |  |
| Wolf_Arctic |  |
| Wolf_Great |  |
| Wolf_Timber |  |
| Wolverine |  |
| Yak |  |
| Zygolophodon |  |

## Remainder — NEEDS-OWNER (103, decision in/move, no note at all)

No group signal, no placement note, no cut. These are staying in the game (decision in/move) with zero recorded intent about where — the owner's attention is the only way to route them.

| creature | decision |
|---|---|
| AA_BlackScarab | in |
| AA_BlackSpelopede | in |
| AA_BlackSpider | in |
| AA_Gallatross | in |
| AA_GallatrossMoribund | in |
| AA_IronhuskBeetle | in |
| AA_MeadowAve | in |
| AA_MegaLouse | in |
| AA_Ravager | in |
| AA_RoyalAve | in |
| AA_Skiphound | in |
| AA_WindBeast | in |
| Akk | in |
| BI_Queen | in |
| BMT_AaroxisDendoriaLarvae | in |
| BMT_AaroxisDendoriaPupa | in |
| BMT_BloodropLarvae | in |
| BMT_BloodropPupa | in |
| BMT_BovineBeetleLarvae | in |
| BMT_BovineBeetlePupa | in |
| BMT_CrystalBeetleLarvae | in |
| BMT_CrystalBeetlePupa | in |
| BMT_FoundryBeetleLarvae | in |
| BMT_FoundryBeetlePupa | in |
| BMT_GoetoToad | in |
| BMT_JewelBeetleLarvae | in |
| BMT_JewelBeetlePupa | in |
| BMT_MossBeetleLarvae | in |
| BMT_MossBeetlePupa | in |
| BMT_RoyalRhinoLarvae | in |
| BMT_RoyalRhinoPupa | in |
| BMT_Sacapillar | in |
| BMT_ShatterjawBeetleLarvae | in |
| BMT_ShatterjawBeetlePupa | in |
| BMT_SmogPupa | in |
| Bordok | in |
| ChrysalideRancor | in |
| DA_BlackScribe | in |
| Devourers | in |
| Drexl | in |
| GR_BearBug | in |
| GR_Bearhorse | in |
| GR_Bearscarab | in |
| GR_Doedicoon | in |
| GR_Elasmobearium | in |
| GR_Hurseman | in |
| GR_Lizardochs | in |
| GR_Manscarab | in |
| GR_Mechacat | in |
| GR_Mechawolf | in |
| GR_Moleman | in |
| GR_Paraceramuffalo | in |
| GR_ParagonIguana | in |
| GR_ParagonInsectoid | in |
| GR_Wolfscarab | in |
| Gualaar | in |
| HarvesterBeetle | in |
| HiveQueen | in |
| IthorianReek | in |
| Kaadu | in |
| Katarn | in |
| KwazelMaw | in |
| LothWolf | in |
| MO_AbominationRace | in |
| Manka | in |
| MastiffPhalone | in |
| Mastmot | in |
| Mawvorr | in |
| Megaspider | in |
| Narglatch | in |
| Raxshir | in |
| Reek | in |
| SW_Emperorisopod | in |
| Silooth | in |
| Spelopede | in |
| Taozin | in |
| Thranta | in |
| Torton | in |
| Tukata | in |
| TuskCat | in |
| VFEI2_BlackEmpress | in |
| VFEI2_BlackQueen | in |
| VFEI2_Empress | in |
| VFEI2_Gigamite | in |
| VFEI2_Hellbeetle | in |
| VFEI2_Ironclad | in |
| VFEI2_Megapede | in |
| VFEI2_Patriarch | in |
| VFEI2_Queen | in |
| VFEI2_RoyalMegascarab | in |
| VFEI2_RoyalMegaspider | in |
| VFEI2_Tankroach | in |
| VFEI2_Teramantis | in |
| VFEI2_Titantick | in |
| VFEI2_Venomite | in |
| VQEA_Splicefiend | in |
| VQEA_Splicehulk | in |
| VQEA_Spliceling | in |
| VQEA_Splicetoot | in |
| VQE_Megamidge | in |
| Vapaad | in |
| Veermok | in |
| Warbird | in |

## Remainder — resolved-by-note, no bucket action needed (128)

Decision is in/move and the note already gives a placement (a biome name, a faction area, a general rule like "wherever needed"). Not a reserved-group member, not cut, not a hedge — just an ordinary creature the owner has already routed. Left here for completeness only.

| creature | decision | owner's words |
|---|---|---|
| AA_AcanthamoebaGiganteaHuge | move | Slime |
| AA_AnimaColossus | move | Rot |
| AA_AnimusVox | in | sold as a pet by the Helix faction, |
| AA_Atispec | move | Scald |
| AA_AuroraSylph | move | Perfect Propane Lake creature |
| AA_Barbslinger | move | wherever needed in hot biomes |
| AA_Behemoth | move | crag, 16 squares |
| AA_BumbledroneQueen | move | goes with the rest of the bumbledrones |
| AA_CrescendoAnole | move | volcanic biomes |
| AA_Erin | move | Wherever it's needed |
| AA_Feralisk | move | Should be reskinned to the Wysokk of the Web biome. Merge |
| AA_FungalHusk | move | occular |
| AA_GreatDevourer | move | Relative of the Sarlacc wandering the desert |
| AA_Groundrunner | move | desert |
| AA_LarvalAtispec | move | wherever the atispec ends up |
| AA_LuciferBug | move | poison forest |
| AA_MatureFleshbeast | move | desert, immature sarlacc |
| AA_OcularNightling | move | occular |
| AA_OvergrownColossus | move | The Slime (make the trees into slime trees) |
| AA_PebbleMit | move | along any shoreline or oasis |
| AA_PedigreedRaptor | move | TOTALLY Hutt settlements and territories |
| AA_Radyak | move | Poison Forest |
| AA_RayHound | move | Scald beast |
| AA_RipperHound | move | Poison Forest |
| AA_SandLion | move | Sand burrower swimmer deserts |
| AA_ShockGoat | move | Refashion into nightside biomes, your choice of extreme cold area, make pale blue aura around it |
| AA_TeratogenicOriginator | move | Slime, tint green |
| AG_OcularSlinger | move | contagion |
| Acklay | move | Hutt arena fodder and territories |
| BMT_Basilisk | move | any mountain, make it grey |
| BMT_BunkerBug | move | Superb for the Fall wreckage creature |
| BMT_CaveLemming | move | ice sheet, rename |
| BMT_ColonyPustuleHornet | move | the Rot |
| BMT_CrystalCrab | move | crystal caverns |
| BMT_CrystalFairyMole | move | Scarlands, oddly. 1 cell |
| BMT_Glowtail | in | Crystal Caverns |
| BMT_Megakrill | move | Fishing result, the Grey Sea |
| BMT_Megaphorid | move | injectable hives |
| BMT_MegaphoridLarva | move | scarlands |
| BMT_Megapleura | move | wreckage-based creature for the Fall |
| BMT_MutatingTumorfishAdult | move | Grey Sea |
| BMT_MutatingTumorfishFry | move | Grey Sea |
| BMT_MutatingTumorfishSpawn | move | Grey Sea |
| BMT_PodWorm | move | Maisma |
| BMT_Polluwog | move | Grey sea |
| BMT_PustuleHornet | move | the Rot |
| BMT_SandPillar | move | cracked land |
| BMT_Stoneback | move | Anywhere on the dayside where it might be needed. 1.2 cells |
| BMT_Thrumbungus | move | Make multi-hued and with a surface that's partially digesting itself, move it into the Rot |
| BMT_TruffleMole | move | sand burrower, desert & extreme desert, 0.4 cells |
| BMT_Yooka | move | The Rot |
| Blarth | move | Miasma, domesticatable, Hutt pets, 1 cell |
| Blixus | move | The Grey Sea and the Maiasma |
| Blurrg | move | Moisture Farmers territory, domesticated |
| Brezak | move | Hutt areas |
| BroodLord | in | Injectable horror content |
| Bulwark | move | Horror injectibles for the night side |
| Bursa | in | domesticated settlement fodder |
| CorellianHound | in | Used as domesticated dog alternative everywhere... so most settlements |
| DA_BeardedTroll | move | Semi-sentient guardian used by Wildsteam, trainable, sometimes seen wild in their territory, mostly fur with little face |
| DA_RockTroll | move | Cracked biome |
| EnergySpider | in | Hutt spicemines dungeon |
| FrogDog | move | Hutt territories and pet and settlements |
| GR_AnimusHare | in | 0.8 cells, pet, settlements |
| GR_Bearman | in | Helix territory |
| GR_Bearmole | move | wherever needed in any dayside biome |
| GR_Chickenhorse | move | Helix areas |
| GR_Chickenlizard | move | Helix areas |
| GR_Chickenspider | move | Baby evil spider in the Web biome Wysok(sp?) |
| GR_Fleshling | move | Contagion |
| GR_Mancat | move | Helix territories |
| GR_Mechachicken | move | rust cathedral |
| GR_Mecharat | move | rust cathedral and mechanoid dungeons |
| GR_Mechathrumbo | in | might want to reskin and add to Mechanoids |
| GR_Muffaloman | in | Helix area |
| GR_Needlechicken | move | Helix territory |
| GR_Nighthrumbo | move | Crags |
| GR_ParagonThrumbo | in | 7 squares, deep desert, very rare, very dangerous, rename to Great Thrumbo |
| GR_Rabbitchicken | move | sold as pet by the Helix faction |
| GR_Snakecat | move | venomthorn dweller |
| GR_Spidersnake | move | Helix area |
| Grazer | in | only in settlements |
| Gullipud | move | oases and pets |
| Gundark | move | Problemmatic semi-sentient predator of the wildsteam territories, can form small raids, this creature steals. Hutt arena material |
| Harvester | in | injected horror |
| JOE_Cephalope | move | sand burrower & swimmer, absorb & retire mod, anywhere there is deep hot sand |
| JOE_Landopus | move | desert water defender type |
| JOE_Nautilant | move | scald |
| JRWBeelzebufo | move | Maisma |
| JungleRancor | move | wildsteam jungle biom, tree breaker |
| KellDragon | move | Hutt territories and area pits |
| Leaftail | move | wildsteam biomes |
| MA_Sporemole | move | The Rot |
| MarshHaunt | in | Maisma |
| Nexu | move | combat pets of the Wildsteam |
| PaintedSpat | move | Slot in nearly anywhere needed on dayside |
| Prowler | move | injectable horror material |
| RSW_AbyssalColo | move | Twilight |
| RSW_ColoClawFish | move | Scald |
| RSW_CrimsonOpee | move | Twilight Sea 9 squares long |
| RSW_ShaleGorger | move | Scarlands |
| RSW_Starmaw | move | Twilight Sea |
| RSW_StormSando | move | Twilight Sea |
| RSW_ThornbackColo | move | Scald |
| Rancor | in | Hutt arena fodder, some escaped living near Oasis and terrifying locals |
| Rikknit | move | Large tree biomes. "rikknit was a crustacean native to New Plympto. They had eight to twelve legs and lived at the tops of hiakk trees. Rikknit spun webs for nests and storage. Female rikknit had ovum sacs connected to their abdomens. The Nosaurians removed these to harvest their eggs, which were sold offworld as a delicacy. They also harvested ovum sacks from rikknit and processed them into an addictive substance called ji rikknit" So good source for Star Wars Cruisine. 0.4 cells |
| Roggwart | in | definitely look up web art for this, Hutt arena fodder |
| Rycrit | move | herd animal near oases |
| SWPotF_RaceDef_ysalamir | move | Wherever needed in arid and hot zones |
| SW_Electricfish | move | scarlands |
| SW_Grenadierworm | move | scarlands |
| Scuttlebug | in | donor for the Genosian Mind Worm |
| Snoruuk | move | The Rot |
| Squall | move | injectable wreck creatures in the Fall Zone |
| StoneCrab | move | 0.3 squares, Twilight Sea |
| Tach | move | 1 cell, this creature can steal, lives in the Jungle |
| Tauntaun | move | white ice night biome |
| TetnissCrab | move | 0.5 cells, grey sea |
| Tibidee | move | volcanic areas |
| Tooke | in | cute vermin that come in festing numbers anywhere near settlements |
| VAEWaste_Hydra | move | venomvine patch predator |
| VFEI2_Acidspitter | move | Scarlands |
| VFEI2_Durapod | in | Infestation |
| VFEI2_Macrofly | move | 0.9 cells in great numbers, emerging out of hives when disturbed, can appear Inhabited in arid shrubland |
| VFEI2_RoyalSpelopede | move | Scarlands |
| VFEI2_Silverfish | move | Grey Sea and surrounding Salt flats of the dessicated sea bed |
| VQE_IceCrawler | in | We must completely examine |
| Wampa | move | Ice plains |
