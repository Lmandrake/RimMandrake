# Retirement Wave 1: typed save census (2026-10-10)

Save: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\CANONICAL_ASHKARR_START_2026-09-12.rws` (17,483,421 bytes; parsed from a scratch copy, never written). Machine-readable: `/home/mandrake/.seat-tmp/rw1/census/census.json` (instruments in the same folder: `inv.py` inventory, `savepass.py` typed streaming pass, `pass2.py`, `pass3.py`, `providers.py`, `errest.py`).

## Method + probes

- Inventory per packageId (`resolve.py`): top-level `<packageId>` of every About.xml in workshop + Mods roots, all 44 ids installed (41 wave + absorber `mandrake.rm.pyrinth` + `shavius.medieval.flavour` + `sihv.rombonesport`). Defs read across the 1.6 LoadFolders (case-insensitive `loadFolders.xml`, `/` = root); implied `Corpse_/Meat_/Blueprint_/Frame_/Minified/Techprint_` added; DLL types read from the .NET TypeDef table (dnfile), `0Harmony`/`DOTween` excluded.
- Save pass: lxml iterparse. Whole-subtree "units" (map `things/thing`, every world pawn list, factions, ideos, world objects, quests) are scanned with their relative path, so hits are classified by context (placed / worn-carried / hediff / passion / backstory / relic / faction ...). Everything else (components, research, policies, filters, price history) is scanned leaf by leaf with its full path. Matches: element text, element tag (shorthand dict keys), and `Class=` against the mods' DLL types.
- Name collisions: wave defNames that are also vanilla/DLC defNames (11,611 from `Data/*/Defs`) or the enum words None/Minor/Major are split off as `~amb` and excluded (they were the whole VSE `None/Major/Minor` and `Neanderthal` false alarms); names also defined by a surviving installed mod (510 other mods in the save's modIds scanned, `providers.py`) are excluded as non-losses (`AM_Scavenger` and part of `AM_*` price rows via `sarg.alphamemes`, `VWE_TrenchWarfare` via `vanillaexpanded.vfesecurity`).
- Terrain/roof grids decoded with the 2026-10-10T22-31-11Z DefDump capture (550 mods vs the save's 616, so the hash table is approximate; every nonzero hash resolved to a real def and none belongs to the wave): no BoneFloor*, AM_*Tile/AM_RCFloor, VQED_* terrain, no CL_StableRockRoof.

| probe | result |
|---|---|
| Steel / Human / WoodLog text nodes | 925 / 935 / 18 found |
| 11 MinifiedThing(Wall, stuff BlocksSlate) | PASS: 11 found at (x,z) = {40,41} {39,44} {39,46} {44,41} {43,44} {43,46} {46,41} {48,41} {50,41} {52,41} {54,41}; the 12th MinifiedThing is RM_Graffiti_Vandal |
| pawn with backstory SH_MED_MedievalAlchemist | PASS: Rebecca "Rebecca" Rock (see below) |
| SEX_AlwaysAphrodor founders genes | PASS: 9 carriers (Wim Ateeka x2 [dead world copy + map], Griz Utinn, Yeku, Tobb Nkik, Nekko Vok, Sekki Vosh, Exorus Hawke [mothballed], one droid) |
| 5 IdeoRelic precepts with VWE relics | REPRODUCED (3x ChargeLMG_Unique, 2x MarksmanRifle); 34 relic precepts in the save in total, all `generatedRelic=null` |
| futureQuests VQE_AncientLabComplex | REPRODUCED (1, `game/components/li/futureQuests`) |
| Warcasket_Tyrant on dead world pawn | REPRODUCED (Maria Rodriguez, RUT_Jawa_Junkers_Grunt, Junkers) |
| DestinyMod.MapComponent_ExoticsManager | REPRODUCED (1, map component) |
| m_Arc_Injector in drug policies | REPRODUCED (4) |
| Melee_MetalPipe on a dead world pawn | REPRODUCED (Marty Blythe, inventory + rememberedWeapons); plus ONE EXTRA not in the earlier doc: Melee_MetalPipeValved in rememberedWeapons of dead PlayerColony pawn Robert Starling |
| bills | save-wide: 136 `<bills>` elements, all empty (`<bills />`), 0 `Bill_Production`, 0 `<recipe>` - so no instrument can show a positive bill; 0 is true but trivial |

Differences from the earlier oldwhy doc: none contradicted. New: 3 more relic precepts (xmb), the AM_EnemyPirate faction, the 11 minified walls, passions/hediffs from AlphaSkills/VSE, 15 Leather stuffs, and the extra remembered metal pipe.

## Per-mod table (one row per packageId)

| packageId | verdict | specific state |
|---|---|---|
| `gravenwitch.vsrexamined` | CLEAN | nothing in save (5 StatDefs only) |
| `jellypowered.survivaltools` | STATE (minor) | 3 scenario parts (ScenPart starting items SurvivalTools_Axe/Hammer/Pickaxe); SurvivalToolAssignmentDatabase game component (class lost); 104 filter + 44 price-history + 9 work-priority rows |
| `leo.raidprotectionfee` | NOISE-ONLY (component) | WorldComponent_ProtectionFee class lost (its scribed fee state is discarded); nothing else |
| `mlie.beastsoftherim` | STATE (minor, world pawns only) | 15 worn apparel made of Leather_* stuff (Zarander/Jerbal/Megasquid/Giantala/Gigantelope/Yippa/Toraton) on 11 world pawns (7 dead, 2 mothballed, 2 alive, none on a map, none player colonists); 20 auto-slaughter rows; 281 filter + 91 price rows. Neanderthal xenotype hits are vanilla (excluded). |
| `det.epochspyrinth` | NOISE-ONLY | 26 filter/price rows; every DV_* name is also defined by absorber mandrake.rm.pyrinth (donor-only defs: NONE) => zero real loss |
| `chezhou.creature.sandworm` | NOISE-ONLY (components) | 5 component classes lost: SandWormQuestGameComponent, SandWormVisualStateManager, SandWormHudOverlay (game) + SandWormDustStormMapComponent, SandWormPressureMapComponent (map) |
| `chezhou.chezhoulib.lib` | NOISE-ONLY (components) | 13 component classes lost (10 game: DebugTools/ClHair/BossHpBar/Animation/CustomMission levels etc.; 3 map: BuildingAnimation*); 18 work-priority rows (CL_InstallModule); CL_StableRockRoof not in roof grid |
| `sl4vp0wer.weareunited` | CLEAN | nothing found (DLL types and 1 JobDef checked) |
| `mlie.syrmoreslaves` | CLEAN | nothing found (code-only; no defs, no Class= hits) |
| `sarg.alphaskills` | STATE | AS_* passion values in 190 skill-record fields and 151 AS_* hediffs across 73 of 99 pawns: 6 player colonists on map (Wim Ateeka, Griz Utinn, Yeku, Tobb Nkik, Nekko Vok, Sekki Vosh), 7 other map pawns, 3 casketed, 1 inventor record, 5 living world, 33+6 dead, 12 mothballed |
| `vanillaexpanded.skills` | STATE | VSE_Natural/Critical/Apathy passion values in 70 skill fields across 49 pawns: 3 player colonists on map (Wim Ateeka, Tobb Nkik, Sekki Vosh), 7 other map, 1 casketed, 4 living world, 2+21 dead, 11 mothballed. No ExpertiseDef records found. None/Minor/Major hits are vanilla enum values (excluded). |
| `mlie.largefactionbases` | NOISE-ONLY | 2 price-history rows (TrapIED_AntigrainWarhead_Large) |
| `mlie.storytellerenhanced` | CLEAN | nothing found (its storytellers/difficulties are not the save storyteller) |
| `font.rimesis` | NOISE-ONLY (component) | Rimesis.RimesisWorldComponent class lost + 5 filter/price rows |
| `groovytaco.beltextractors` | CLEAN | nothing found (code-only) |
| `reel.turretpipeline` | NOISE-ONLY | 21 filter/price rows; no placed pipe/turret/ammo Thing |
| `erdelf.minifyeverything` | STATE | 11 MinifiedThing holding a Wall (stuff BlocksSlate) at map 0 cells (40,41) (39,44) (39,46) (44,41) (43,44) (43,46) (46,41) (48,41) (50,41) (52,41) (54,41) - these exist only because the mod made walls minifiable; mod defines no defNames, so only the placed state matters |
| `clown.dedicatedturrets` | NOISE-ONLY | research key DedicatedDefenceSystems + 29 filter/price rows; no placed turret |
| `neronix17.shieldgenerators` | NOISE-ONLY | 3 research keys (ShieldGen_*Tech) + 25 filter/price rows; no placed generator |
| `juanlopez2008.lightsout` | CLEAN | nothing found (code-only) |
| `hmc.wall.furniture` | NOISE-ONLY | 86 filter/price rows; no placed wall furniture |
| `kyzy.shipwallenhanced` | NOISE-ONLY (component) | GameComponent_ShipWallTimer class lost + 83 filter/price/food-restriction rows; no placed ShipWall Thing |
| `arcjc007.wallstuff` | NOISE-ONLY | 123 filter/price/work-priority rows + modNames entry; no placed Thing |
| `thumb.bettercremation` | CLEAN | nothing found (code-only) |
| `vanillaexpanded.vwe` | STATE | 5 IdeoRelic precepts (VWE_Gun_ChargeLMG_Unique x3 = Hexlink, Loccorpus, Animal Blaster; VWE_Gun_MarksmanRifle x2 = Strong Rifle, Rifle of Self), all generatedRelic=null; 2 research keys (VWE_HeavyWeapons; VWE_TrenchWarfare is ALSO defined by vanillaexpanded.vfesecurity so only 1 lost); 129 filter + 24 price rows. No placed or carried VWE Thing. |
| `vanillaquestsexpanded.ancients` | STATE | 1 VEF futureQuests entry questDef VQE_AncientLabComplex (third-party null-def behaviour UNMEASURED); 1 ignoredFactions row (VQE_NewVaultPlayerFaction); 8 auto-slaughter rows; 320 price + 70 filter + 63 work-priority rows. No placed Thing, no site, terrain grids hold no VQED_* terrain. |
| `sarg.alphamechs` | STATE (minor) | 2 Big and Small BS_scribedCache rows (BS_OriginalThing AM_Daggersnout, AM_Siegebreaker; third-party code, UNMEASURED) + 4 research keys + 212 filter + 38 price rows. No AM mech pawn (no kindDef hit), no placed Thing. |
| `milkwater.destinymod` | NOISE-ONLY (engine-verified drops) | m_Arc_Injector in 4 drug policies; DestinyMod.MapComponent_ExoticsManager class lost; 40 filter + 20 price + 9 work-priority rows. No Destiny Thing anywhere. |
| `aoba.warcasket` | STATE (minor, harmless) | 1 worn Warcasket_Tyrant on dead world pawn Maria Rodriguez (RUT_Jawa_Junkers_Grunt, Junkers) + 22 outfit/packUp filter rows |
| `flangopink.metalpipe` | STATE (minor, harmless) | Melee_MetalPipe in inventory + rememberedWeapons of dead world pawn Marty Blythe (TribeCivil); Melee_MetalPipeValved in rememberedWeapons of dead world pawn Robert Starling (PlayerColony); + 24 filter/price rows |
| `flangopink.metalpipehorseshoe` | CLEAN | nothing found (1 SoundDef) |
| `kshtantrumsounds.mod` | CLEAN | nothing found (sounds only) |
| `bonible.medievalmeleesounds` | CLEAN | nothing found (patch/sounds only) |
| `armoredampharos.fancyrats` | NOISE-ONLY | 2 auto-slaughter rows (FancyRat) + 21 filter/price rows; no FancyRat pawn |
| `tyrannidae.fancyratsplus` | CLEAN | nothing found (patch only) |
| `van.dacrypts` | NOISE-ONLY | 2 research keys (DA_Catacombs, DA_BloodflameCatacomb) + 67 filter/price rows; no placed tomb Thing |
| `aqued.dredgeaberrations` | NOISE-ONLY | 63 filter/price rows (Fish_*) |
| `xmb.ancienturbanruins.mo` | STATE (major) | see Shells verdict |
| `meteores.ancienturbanruinsalldeconstructible.aurad` | CLEAN | nothing found (patch only; depends on xmb) |
| `meteores.ancienturbanruinsvanillaloot.aurvl` | CLEAN | nothing found (patch only; depends on xmb) |
| `redmattis.bigsmall` | NOISE-ONLY | 6 BS_* faction defs in a world component ignoredFactions list + 13 filter/price rows; no BS pawnkind/xenotype/faction in save |
| `shavius.medieval.flavour` | STAYS - STATE | see Medieval Flavour section |
| `sihv.rombonesport` | STAYS - STATE | see Bones section |
| `mandrake.rm.pyrinth` | STAYS (absorber) | same 26 filter/price rows as donor; all DV_* names defined |

Every one of the 44 ids is present in the save's meta `modIds` (616 entries) => the mod-mismatch dialog fires for all of them.

## Sub-steps required before untick

1. **sarg.alphaskills + vanillaexpanded.skills (the only real pawn-state loss).** 73 of 99 pawns carry AS passions/hediffs, 49 carry VSE passions, incl. 6 player colonists on the map. Either (a) accept: ~260 passion-field parse errors + 151 missing-hediff references, colonists lose their custom passions (they fall back to None) and the hediffs drop; or (b) pre-step: save-edit the 6 colonists (and the 3 casketed pawns) to vanilla passions and remove AS_* hediffs. Decide before unticking; do both mods together (AS needs VSE).
2. **Relics (vanillaexpanded.vwe 5 + xmb 3 = 8 precepts, 6 ideos).** Each logs `Precept_Relic had null thingDef` and is re-rolled to a random relic-eligible def. Pre-step if the specific relic types matter: edit the 8 precepts' `thingDef` to kept defs; otherwise accept the re-roll.
3. **erdelf.minifyeverything.** Install the 11 minified walls at the cells above (or deconstruct) BEFORE unticking; afterwards Wall is no longer minifiable and the held MinifiedThings have no supported way back to a wall (loading behaviour UNMEASURED).
4. **xmb.ancienturbanruins.mo** only if it is actually being removed (see Shells verdict): remove building AM_DamagedEmptyShelves (map 0 cell (140,0,114)), remove faction AM_EnemyPirate "The Ash Crushers" (id Faction_18, 25 relation rows in other factions point at it, no pawns/objects/quests), handle 3 relics (step 2), 56 drug-policy rows.
5. **vanillaquestsexpanded.ancients.** The VEF `futureQuests` entry (VQE_AncientLabComplex) becomes a third-party null questDef; behaviour when VEF fires it is UNMEASURED. Pre-step: delete that one `<li>` from `GameComponent_QuestChains.futureQuests` in a save edit, or measure with a live load.
6. **sarg.alphamechs.** 2 Big and Small `BS_scribedCache` rows hold AM_Daggersnout / AM_Siegebreaker; third-party null handling UNMEASURED; deletable by save edit.
7. **jellypowered.survivaltools.** 3 ScenPart starting-item rows with removed defs; delete from `scenario/parts` in the save if anything ever reads the scenario.
8. No step needed (accept the logged errors): warcasket, metalpipe, beastsoftherim (15 worn Leather stuffs on non-player world pawns), destiny, all component-class losses (25 classes), all filters, price history, work priorities, research keys, auto-slaughter rows.
9. One re-save clears every logged error afterwards.

## Shells verdict (C22)

- `meteores.ancienturbanruinsalldeconstructible.aurad`, `meteores.ancienturbanruinsvanillaloot.aurvl`: CLEAN, save-safe (both are patch-only on top of xmb).
- `redmattis.bigsmall`: NOISE-ONLY, save-safe (6 BS_* faction defs in an ignoredFactions list; no BS pawn kind, xenotype, faction or Thing in the save).
- `xmb.ancienturbanruins.mo`: **NOT save-safe to uninstall as-is.** It holds: 1 placed building (AM_DamagedEmptyShelves, cell (140,0,114)); a live Faction `AM_EnemyPirate` "The Ash Crushers" (Faction_18, referenced by 25 relation rows; empty of pawns); 3 relic precepts (AM_M700A "Rifle of Self", AM_ADAR "Open Heirloom", AM_MK18M "Drug-Rifle") in the ideos the Contract / the Balance / the Reckoning of Debts; 56 drug-policy entries across 4 policies; 2 component classes (`AncientMarket_Libraray.GameComponent_AncientMarket`, `MapComponent_Submap`); ~550 price-history, ~324 filter, 18 work-priority rows. (`AM_Scavenger` style category survives via sarg.alphamemes.) ~1,230 of the wave's first-load errors come from it. Uninstalling it needs sub-step 4; the two meteores patches must go with it or before it.

## Medieval Flavour pawn (`shavius.medieval.flavour`, stays)

Exactly one pawn: **Rebecca "Rebecca" Rock** (`Human933`), kind `Colonist`, adulthood backstory `SH_MED_MedievalAlchemist` (childhood CoreDilettante33), a **living MOTHBALLED world pawn** (pawnsMothballed), faction `RUT_Jawa_AscendantHelix` ("Ascendant Helix"). No other SH_MED_/VA_MED_ backstory is in the save. Not a player colonist.

## Bones (`sihv.rombonesport`, stays)

- Bills: 0 - the save has no production bills at all (136 empty `<bills />`); Make_ChemfuelFromBone / MakeBonePlasteel / MakeBonePlastic / MakeBoneChina occur 0 times (raw check also 0).
- Bone items as Things: none placed or stored. `BoneItem` appears 3 times as a stuff/ref (dead pawns' rememberedWeapons/inventory, one NPC contract); Bonecrete 2 and BonePlastic 2 only in filters/price history.
- BoneChina is STUFF on 195 buildings + 9 doors on map 0 (204 refs) plus 203 `layoutStructureSketches` entities: Bones is load-bearing for that map. 2 research keys (BoneRefine, BoneRefineII), 2 worn ROMB_Apparel_SkullMask on dead world pawns, no BoneFloor terrain in the grid.

## First-load error estimate (wave removed, Pyrinth net zero, Bones and Medieval Flavour kept)

| class | count |
|---|---|
| `Could not load reference to ... named ...` (one per surviving def-text occurrence incl. implied defs, filters, price rows, apparel stuff, hediffs, drug entries, relics' thingDef) | 3295 |
| `Null key while loading dictionary` (price-history keys + research-progress keys + price modifiers; already counted once above as a reference) | 686 |
| missing component classes (`Could not find class`) | 25 |
| `Precept_Relic had null thingDef after loading` | 8 |
| `Some DrugPolicyEntries were null` (4 policies) | 4 |
| auto-slaughter config warnings (rows) | up to 30 |
| passion field values unknown after VSE/AlphaSkills removal (message class UNMEASURED) | 260 |
| `Dialog_ModMismatch` | 1 dialog listing all 44 ids |

**Range: about 3,332 to 4,308 logged messages** (low = references + classes + relics + drug-policy; high = low + null keys + auto-slaughter + passion fields). Without xmb: subtract ~1,230. All far below the 10,000-message log stop. Third-party rows (VTE price history, WorkTab priorities, VEF futureQuests/ignoredFactions, Big and Small cache) tolerate null defs by UNMEASURED behaviour; the engine rows are as in the earlier doc.
