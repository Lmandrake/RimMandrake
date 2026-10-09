# Live acceptance plan, 2026-10-09 (prepared by a FOUNDRY helper; NOT run)

Source: `rimflow next --acceptance --seat FOUNDRY`, 235 built/validated items owing 572 criteria
(L1 53, L2 304, L3 42, L4 54, GREEN-MIN 110, GREEN-FULL 9). Nothing here was run: no bridge call, no game launch,
no `modset_builder --apply`. The scene-harness agent holds the bridge; take it with `rimflow bridge take --for "acceptance 10-09"` first.
Per-criterion rows (section 3) are generated from the live queue and the item prose; criteria text is copied verbatim, truncated at 170 chars.
Counts decay: re-run `rimflow next --acceptance --seat FOUNDRY` at the start of the sitting and diff the ID list against section 3.

## 0. Rules for the sitting
- Write each check BEFORE launching (section 3 holds it). A check not written is UNMEASURED, not passed.
- One bridge driver; python.exe for every bridge call (WSL cannot reach the loopback bridge). Read the tool's own `success`/`foundCount`/`notFound`
  fields; `get_defs` takes `defs` as a STRING "DefType/DefName". Pipe python.exe output through `tr -d '\r\n'` before comparing.
- NEVER live-test flyer flight (state read only), never fullscreen/focus the game, kill hostiles on review maps.
- `modcheck run <Mod>` REWRITES the live ModsConfig (swaps to MINIMAL): only inside the GREEN-MIN step, never during L1/L2.
- Do not call `modset_builder --apply` while `Player.log` was touched in the last 3 min (kill first). Back up Saves keepers before any `save_game`.
- Record each outcome: `rimflow verify <ID> --criterion <C> --result pass|fail --config <min-13|full-...> --evidence <path>`. L4 criteria are the owner's; do not verify them.
- All five DLCs are in every tier (`dlc: True`; `tier_guard` refuses a list missing royalty/ideology/biotech/anomaly/odyssey). Confirm by parsing ModsConfig (`ET.parse(p).find("activeMods")`), never `grep -c '<li>'`.

## 1. Order, cheapest first
| # | Sitting | List | Cost | Covers |
|---|---|---|---|---|
| 1 | Smoke + all L1 reads | proposed tier `acc_20261009` (below) | ~1 min load on a ~43-mod list | Section 2 smoke, then 53 L1 criteria (def reads, log strings) |
| 2 | L2 on ONE quicktest map | same load as 1, no relaunch | ~90 s map | 304 L2 criteria, grouped by scene/biome in section 3; scene-harness items go through its runner |
| 3 | GREEN-MIN | `acc_green_min`, then `acc_green_min2` (existing tiers, see section 4) | one swap each, `modcheck run` per mod | 110 criteria (north-star driver runs on the minimal list) |
| 4 | GREEN-FULL, one cold load | the owner's full list (~630 mods; read ModsConfig snapshot in `infrastructure/state/modlists/`) | ~15 min cold load | 9 criteria + harvest of Player.log for patch failures |
| 5 | L3 | Opus evaluator over the screenshots/art from 2 | offline | 42 criteria |
| - | L4 | owner | - | 54 criteria; list them for him, never self-verify |

Stop rules: if the smoke fails (section 2), stop and file the mod before spending L1/L2; if sitting 1 shows a red error from our mods, the load was not clean and L2 results from it are suspect.

## 2. Smoke step: every converted mod's PatchApplier path loaded, no failed patches

What `PatchApplier` (`src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs`) writes, MEASURED from its source:
- success census, `Log.Message`: `[<logTag>] Harmony: patched N, missing 0` (logTag = third argument of `PatchApplier.Apply`, `RimMandrake.<Mod>`);
- partial failure, `Log.Warning`: the same line with `missing X: <feature> (<patchClass>)...` and the sentence "Those features are switched off for this session";
- per-feature `Log.Error`: `[<logTag>] Harmony patch failed, feature switched off: <feature> (...)`.
Sanity probe (run it first; a search must prove it can find something): in the 2026-10-08 `Player.log`, `\[RimMandrake[^]]*\] Harmony: patched [0-9]+, missing [0-9]+` finds 1 line
(`[RimMandrake.FlowWorks] Harmony: patched 31, missing 0`) and `Patch operation .* failed` finds 38 lines. A smoke that reports 0 hits for both is a broken instrument.

Pass = (a) one census line per converted mod that is ACTIVE in the sitting-1 list, every one `missing 0`; (b) 0 lines matching `Harmony patch failed`;
(c) 0 lines matching `Harmony: patched [0-9]+, missing [1-9]`; (d) the count of `Patch operation .* failed` lines is no higher than the pre-sitting baseline
(copy the old log to `Transient/` before launch; the 10-08 log holds 38, mostly `PatchOperationConditional` no-match logs from `RimUtinni Patches`).
A converted mod that is NOT in the list prints no census line; that is expected-absent, not a failure. A converted mod that IS active and prints nothing is UNMEASURED-bad:
its `Apply` never ran (assembly not loaded, `<Compile Include>` missing, or DLL not deployed) and must be chased before anything else.

Command, run from WSL after the load reaches the main menu (read-only on the log, no bridge):
```
python3 - <<'PY'
import re
L="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
t=open(L,errors="ignore").read()
cen=re.findall(r"\[(RimMandrake[^\]]*)\] Harmony: patched (\d+), missing (\d+)",t)
print("census lines:",len(cen)); [print(" ",c) for c in cen]
print("Harmony patch failed:",len(re.findall(r"Harmony patch failed",t)))
print("missing>0:",len(re.findall(r"Harmony: patched \d+, missing [1-9]",t)))
print("Patch operation failed:",len(re.findall(r"Patch operation .* failed",t)))
PY
```
Expected census tags (36 mods call `PatchApplier.Apply`; the packageId column is blank where the mod ships inside a composed mod, such as `mandrake.rm.biomes` or `mandrake.rut.patches`, and loads with it):

| src dir | packageId of its own About | expected tag |
|---|---|---|
| Abyss | mandrake.rm.abyss | RimMandrake.Abyss |
| Aftermath | mandrake.rm.aftermath | RimMandrake.Aftermath |
| CathedralPass | (no About: folded?) | RimMandrake.CathedralPass |
| Cauldron | mandrake.rm.cauldron | RimMandrake.Cauldron |
| DivingInteraction | mandrake.rm.divinginteraction | RimMandrake.DivingInteraction |
| EmpirePursuit | (no About: folded?) | RimMandrake.EmpirePursuit |
| ExplosiveGrowth | mandrake.rm.explosivegrowth | RimMandrake.ExplosiveGrowth |
| ExplosiveKnockback | mandrake.rm.explosiveknockback | RimMandrake.ExplosiveKnockback |
| FallLineArrivals | (no About: folded?) | RimMandrake.FallLineArrivals |
| FeverWood | mandrake.rm.feverwood | RimMandrake.FeverWood |
| FloodedCanyon | mandrake.rm.floodedcanyon | RimMandrake.FloodedCanyon |
| FlowWorks | mandrake.rm.flowworks | RimMandrake.FlowWorks |
| FungalSoilTrade | (no About: folded?) | RimMandrake.FungalSoilTrade |
| GizkaStowaway | (no About: folded?) | RimMandrake.GizkaStowaway |
| GravshipLanding | mandrake.rm.gravshiplanding | RimMandrake.GravshipLanding |
| Inhabited | mandrake.rm.inhabited | RimMandrake.Inhabited |
| KeelHoist | mandrake.rm.keelhoist | RimMandrake.KeelHoist |
| KineticArms | mandrake.rm.kineticarms | RimMandrake.KineticArms |
| LanternDeeps | mandrake.rm.lanterndeeps | RimMandrake.LanternDeeps |
| LuminousPigment | mandrake.rm.luminouspigment | RimMandrake.LuminousPigment |
| Ninefold | mandrake.rm.ninefold | RimMandrake.Ninefold |
| PlanetPresetPrime | mandrake.rm.planetpresetprime | RimMandrake.PlanetPresetPrime |
| PlantGrowth | (no About: folded?) | RimMandrake.PlantGrowth |
| PropaneLakeMechanics | (no About: folded?) | RimMandrake.PropaneLakeMechanics |
| RaidRedesigner | mandrake.rm.raidredesigner | RimMandrake.RaidRedesigner |
| RiverColors | (no About: folded?) | RimMandrake.RiverColors |
| RustCathedral | mandrake.rm.rustcathedral | RimMandrake.RustCathedral |
| SWBestiary | (no About: folded?) | RimMandrake.SWBestiary |
| Scarlands | mandrake.rm.warscar | RimMandrake.Scarlands |
| SeaShores | mandrake.rm.seashores | RimMandrake.SeaShores |
| ShipShields | (no About: folded?) | RimMandrake.ShipShields |
| SolarMirrors | mandrake.rm.solarmirrors | RimMandrake.SolarMirrors |
| TerminalBiomes | mandrake.rm.terminalbiomes | RimMandrake.TerminalBiomes |
| TheForge | mandrake.rm.theforge | RimMandrake.TheForge |
| UnfinishedLine | (no About: folded?) | RimMandrake.UnfinishedLine |
| Wreckage | mandrake.rm.wreckage | RimMandrake.Wreckage |

Decide expected-present by the mod being in the active list (ModsConfig parsed) or its DLL being under an active mod's `Assemblies/`; the unmatched rest are expected-absent.
Also read, same log: first exception of any kind from `RimMandrake.` or `RimUtinni`/`RimStarWars` namespaces (the first exception, not the loudest), and `Could not resolve cross-reference` counts versus baseline.

## 3. Per-criterion checks (generated from the live queue)

Columns: item.criterion, state, text (verbatim, 170 chars), instrument family, item-named instruments (backticked tool calls or log strings found in the item prose), extra mods beyond `acc_20261009` the criterion text names.
Item-named instrument `-` means the item prose names none: the check is then the family template below, and the exact call (def names, tool args) MUST be written into the item row before launch. Until written, that row is UNMEASURED, not planned.

Family templates:
- **LOG**: read Player.log (WSL path above) after the step; the string/count named in the criterion; baseline count taken before the step
- **DEFREAD**: python.exe bridge call jawa/get_defs defs="DefType/DefName" (string); pass = success true, foundCount = asked, notFound empty, no ConfigError for the def in Player.log
- **CHAIN**: modcheck status/floor for the named mod, or the validation chain named in the item; read the result JSON, not exit code
- **SCENE**: scene-harness runner (src/RimMandrake/Utils/scenes); pass = the named scenes PASS in its result file
- **OBSERVE**: state read via a [Tool] on a quicktest spawn (list_pawns/list_things/get_pawn); no screenshot hunts; flyers: Pawn_FlightTracker state only

### 3.a L1 (sitting 1, after smoke) (53 criteria)

| item.crit | st | criterion | fam | named instrument | + mods |
|---|---|---|---|---|---|
| BAZAAR_PRICE_ENGINE_1.A1 | bui | minimal-list read finds the price store, seed rules, intel gates and columns, 7 settings loading clean | OBSERVE | - | rm.bazaar |
| BLOWER_ROOM_COOLER_1.A2 | bui | on a load, Player.log has no config error or cross-reference error naming RM_DryAirBlower, CompProperties_Blow | LOG | - |  |
| CATHEDRAL_MECHANOID_PASS_VERBS_1.A1 | bui | minimal-list read finds the CathedralPass mod, pass hediff and scoped Hostility patch loading clean | OBSERVE | - | rut.cathedralpass |
| CRACKEDLANDS_PEAKSTORM_DUST_REVERSAL_1.A2 | bui | under Peakstorm Light ProofState samples show both reversed=True and reversed=False | OBSERVE | - |  |
| CRUST_NEVER_STRANDS_1.A2 | bui | on a Grey Sea floor map with crust, ProofTearFree clears crust, gate=accepted, tearFreeOffered=True | OBSERVE | - |  |
| DECOY_SHADE_TARP_1.A1 | bui | decoyShadeEnabled wired and gated (mechanic_toggles.decoyShade_wired_and_gated); tarp def and research resolve | DEFREAD | - |  |
| DEEPFIRE_WORLD_LIGHT_1.A1 | bui | a grey-sea "drawn" creature (or the suulk) on a map with a deepfire-painted floor and no player lamp walks to  | OBSERVE | - |  |
| DEEPFIRE_WORLD_LIGHT_1.A2 | bui | in the Abyss Dark a deepfire floor proxy and the glow tank keep their full GlowRadius while a vanilla lamp bes | OBSERVE | - |  |
| DEEPFIRE_WORLD_LIGHT_1.A3 | bui | with the Visibility mod active, an hour of darkness on a home map with N lit deepfire lights raises shipVisibi | OBSERVE | - |  |
| DEEPFIRE_WORLD_LIGHT_1.A4 | bui | a pawn wearing a lacquered cloak and carrying deepfire glow (worn coat or Cuisine hediff) never gains the invi | OBSERVE | - |  |
| DUST_DEVIL_ITEM_LOSS_FIX_1.A1 | bui | with a dust devil lifting an item whose landing spot and devil cell both refuse placement, the item is back at | OBSERVE | - |  |
| ELDER_TREASURE_TAG_TABLE_1.A1 | bui | DefDatabase lists RM_ElderSealedRelic and RM_ElderUnknownWeapon as Elder treasures and an Elder offer can stil | OBSERVE | - |  |
| EMPIRE_ESCALATION_LADDER_1.A4 | bui | all six RUT_EmpireRungDef load with rungIndex/kind (validation chain ladder_rungs_resolve) and no ConfigErrors | LOG | - | rut.empirepursuit |
| FEVERWOOD_LIMB_LINGER_CAP_1.A1 | bui | on a Fever Wood map with the bestiary on, a spawned feeler despawns after the linger time with no pool cooldow | OBSERVE | - |  |
| FEVERWOOD_LIMB_LINGER_CAP_1.A2 | bui | with the cap at 1 and one limb standing, an ordinary emergence spawns nothing and encounter pressure still ris | OBSERVE | - |  |
| FEVERWOOD_LIMB_LINGER_CAP_1.A3 | bui | a sentinel sinking on linger restores the biome ambient (ChorusSilenced reads false) | OBSERVE | - |  |
| FORCE_DISTURBANCE_REFLAVOR_1.A1 | bui | after deploy, the patched psychic event defs resolve live with Force-flavoured label and letter text and no va | DEFREAD | - | rsw.patches |
| GLOOMCAST_WAKE_RIDERS_1.A2 | bui | spawned follower within 60 cells of a gloomcast gets the follow job (state read) | OBSERVE | - |  |
| GLOW_TANK_LIQUID_FEED_1.A1 | val | with FlowWorks and LuminousPigment loaded, a seeded GlowTank on no net reads "Dry: growth paused" | OBSERVE | - |  |
| GRAVSHIP_WIRES_SURVIVE_LAUNCH_1.A2 | bui | a minimal-list load with the new DLL shows no GimmeSomeSlack errors in Player.log and the Mod Settings page sh | LOG | - |  |
| GREYSEA_FLOOR_WALKABLE_CHECK_1.A1 | bui | on a generated Grey Sea floor, flooding from the map centre reaches a cell beside every Brine Elder and grey-f | OBSERVE | - |  |
| HARMONY_PATCH_RESILIENCE_1.A1 | bui | on the live list Player.log carries `[RimMandrake.FlowWorks] Harmony: patched 30, missing 0`, with no FlowWork | LOG | [HarmonyPatch]; [<mod>] Harmony: patched N, missing X; [PatchFeature("label", typeof(Settings), "field")] |  |
| HARMONY_PATCH_RESILIENCE_1.A2 | bui | a test build with one patch target deliberately renamed logs exactly that feature as switched off, every other | OBSERVE | [HarmonyPatch]; [<mod>] Harmony: patched N, missing X; [PatchFeature("label", typeof(Settings), "field")] |  |
| JAWA_SWIM_HOOD_KEEP_1.A1 | bui | the deployed JawaRules DLL state-read shows Apparel_Head.CanDrawNow true for a swimming Jawa wearing a hood | OBSERVE | - |  |
| KINETIC_BLAST_WEAPONS_1.EK.load | bui | explosiveknockback tier loads with no red error from this mod; Harmony patches applied | LOG | - |  |
| LASSO_CHERRYPICKER_REMOVAL_1.A1 | bui | The live CherryPicker config is reconciled (2133 unrecognised cuts) and cherrypicker_swap --ship --apply succe | OBSERVE | - |  |
| LASSO_CHERRYPICKER_REMOVAL_1.A2 | bui | Melee Animation LassoSpawnChance is set to 0. | OBSERVE | - |  |
| LAUNCH_HELD_COLONIST_WARNING_1.A2 | bui | on a load, Player.log has no "[RM EnvironmentalHazards] launch held-colonist warning" error (the patch armed) | LOG | - |  |
| LIGHT_LEDGER_ONE_1.A2 | val | a suulk grazing a mature sun-sphere: the sphere's GlowRadius stays reduced across 60-tick culture steps and ac | OBSERVE | - |  |
| LIGHT_LEDGER_ONE_1.A3 | val | on a Twilight floor map, SetLidDarkDimming(true) holds every open well at 0.1 through a waning step, a well op | OBSERVE | - |  |
| LIGHT_LEDGER_ONE_1.A4 | val | in the Abyss Dark a lamp a krizzak is feeding on is shrunk by BOTH (radius = base x dark share x krizzak share | OBSERVE | - |  |
| LIGHT_LEDGER_ONE_1.A5 | val | a lanternstone under the aurora with sippers on it reads def x 1.75 x sipper share, and returns to def x 1.75  | DEFREAD | - |  |
| LIVE_ROUND2_FIXES_PROOF_1.A3 | bui | Player.log after the WhisperSarlaccSign genstep shows 0 MakeThing stuff=null errors. | LOG | jawa/pawn_use_verb action=cast verb="mirror crest"; jawa/list_pawns includeHealth; jawa/run_genstep RSW_GenStep_WhisperSarlaccSign |  |
| MOD_OPTIONS_RETROFIT_1.A1 | bui | On a full-list load Mod Settings opens for each of our mods with no red errors. | LOG | [StaticConstructorOnStartup] |  |
| MOVING_DUNES_BUILD_1.A3 | bui | the shader tint gate (MaterialColor vs VertexColor) is resolved by a live load | DEFREAD | - |  |
| NINEFOLD_FAVOUR_ODDS_BUILD_1.A1 | bui | minimal-list read finds the favour tilt def and table, offerings and Nine Faults rite defs loading clean | DEFREAD | - | rut.rites |
| PARENTAL_ENRAGE_FACTION_GUARD_1.A1 | bui | three calves, one wild adult, one intruder: exactly one adult enrages; a tame adult never guards a wild calf n | OBSERVE | - |  |
| RAKATAN_ARCHOTECH_MACHINES_1.A1 | bui | minimal-list read finds the grade ladder, Refurbished smelter, mobile power cell and emanator (3 grades), comp | OBSERVE | - |  |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A4 | val | with mandrake.rsw.swbestiary loaded RM_RustCathedral merged wildAnimals contains RSW_Mynock (read as elements) | OBSERVE | jawa/get_defs | rsw.swbestiary |
| SALVAGE_WRECKAGE_EVERYWHERE_1.A1 | bui | minimal-list read finds the wreck families, wreck fields for steps 3-4 and 6, jackets, Forge cache loot and Fa | OBSERVE | - |  |
| SCREEN_STOPS_SPORES_1.A1 | bui | screenStopsSporesEnabled readable and Gas_Damaging branches on it (map_mechanics.gas_screened_by_aerosol_scree | OBSERVE | - |  |
| SHIPVERMIN_FREE_TIER_BEASTS_1.A2 | bui | on the free-tier list ShipVermin loads with no red errors and its four beasts resolve via get_defs | LOG | - | rsw.swbestiary |
| SHIP_TOW_LINE_1.A2 | bui | salvageWinchEnabled wired and gated; RM_SalvageWinch def and research resolve (mechanic_toggles.salvageWinch_w | DEFREAD | - |  |
| SOLAR_MIRRORS_BUILD_1.A2 | bui | every SolarMirrors def loads with its comps and no error names the mod on a minimal list (CreatureBehaviors +  | LOG | jawa/shade_probe |  |
| SURFACE_HOME_MAP_HELPER_1.A1 | bui | with a sea-floor map open as a player home, a gale/swept-away/condenser/navigator return lands on a surface ho | OBSERVE | - |  |
| TAKEN_BY_LAND_SERVICE_1.A2 | bui | taken_by_land.service_has_river_policy_and_trace_setting reads river policy registered and the trace setting;  | OBSERVE | - | rm.traces |
| TICKER_NEVER_FIRES_FIX_1.A1 | val | a spawned RUT_DyingCreep spreads and then dies into RUT_DeadCreep filth within its lifetime hours | OBSERVE | - |  |
| TICKER_NEVER_FIRES_FIX_1.A4 | val | a powered, fuelled RM_DryAirBlower registers its room in RM_MapComponent_DryRooms | OBSERVE | - |  |
| VERMIN_EAT_BREEDING_FOOD_1.A2 | bui | verminBreedingEatsFood wired and gated (mechanic_toggles.verminBreedingEatsFood_wired_and_gated) | OBSERVE | - |  |
| VEXXITH_CLOSED_LOOP_BUILD_1.A2 | bui | log shows Harmony census patched TakeDamage for RimMandrake.Cauldron and vexxith door ignores AcidBurn | LOG | - |  |
| WARCASKET_DEPENDENCY_DOWNLOAD_URL_1.A2 | bui | Player.log shows no "needs to have <downloadUrl>" line for any of our mods | LOG | - | rm.warcasket |
| WARSCAR_AEROSOL_SCREEN_1.A1 | bui | minimal-list read finds the pollution sense, aerosol screen comp and toxic-buildup patches loading clean | OBSERVE | - |  |
| WEEPINGSTONES_CONDENSER_QUESTS_1.C6 | bui | free mod alone shows no Hutt/Blackstar/canon string; campaign loaded, the slots resolve to the Hutt Cartel, Ho | DEFREAD | - |  |

### 3.b L2 (sitting 2, one quicktest map from the same load) (304 criteria)

| item.crit | st | criterion | fam | named instrument | + mods |
|---|---|---|---|---|---|
| ABYSS_LIGHTFALL_BROOD_WRECK_1.A10 | val | a salvage bill completes at the wreck, spends stock and raises the meter; a refused part's fit gizmo shows the | OBSERVE | - |  |
| ABYSS_LIGHTFALL_BROOD_WRECK_1.A11 | val | an egg hatched with a great bone aboard the gravship bonds; without one it hatches wild; a stolen egg calls a  | OBSERVE | - |  |
| ABYSS_LIGHTFALL_BROOD_WRECK_1.A12 | val | past the line she wakes as RM_SummAllRender, manhunter, taking ~3% damage | OBSERVE | - |  |
| ABYSS_LIGHTFALL_BROOD_WRECK_1.A9 | val | a generated map on an RM_BroodLair/Lightfall tile holds the sleeping brood-mother, eggs, bone field and wreck | OBSERVE | - |  |
| ARMOURY_JUMPPACK_INVALID_IL_1.A1 | bui | On a live quicktest map the Player.log contains no InvalidProgramException from the jump pack code. | LOG | - |  |
| ARMOURY_JUMPPACK_INVALID_IL_1.A2 | bui | Harmony's patch list shows the jump pack patch applied. | OBSERVE | - |  |
| ARMOURY_JUMPPACK_INVALID_IL_1.A3 | bui | Raiders with jump packs are seen to jump, with ranged timing treated as provisional. | OBSERVE | - |  |
| ARMOURY_JUMPPACK_INVALID_IL_1.A4 | bui | The Armoury belt recheck that previously failed now passes. | OBSERVE | - |  |
| BACTA_REVIVAL_MECHANIC_1.A1 | bui | On a quicktest map the revival WorkGiver fires automatically on a suitable corpse rather than only when forced | OBSERVE | jawa/pawn_health; jawa/prioritized_work; [Errno 22] Invalid argument | rsw.bacta |
| BACTA_REVIVAL_MECHANIC_1.A2 | bui | A corpse that died of vital-organ loss is revived and then dies again, and the outcome matches the owner desig | OBSERVE | jawa/pawn_health; jawa/prioritized_work; [Errno 22] Invalid argument | rsw.bacta |
| BACTA_REVIVAL_MECHANIC_1.A3 | bui | After TryResurrect clears wounds, the tank does not eject the patient with a 'nothing to heal' result. | OBSERVE | jawa/pawn_health; jawa/prioritized_work; [Errno 22] Invalid argument | rsw.bacta |
| BACTA_TANK_CORE_1.A1 | bui | On a quicktest map a pawn missing an organ (kidney) and a pawn with a brain injury are not restored by the tan | OBSERVE | rimworld/load_game; rimworld/start_debug_game_ready; rimworld/go_to_main_menu | rsw.bacta |
| BACTA_TANK_CORE_1.A2 | bui | A pawn with an infected wound in the tank gets the infection-assist effect at the tuned rate. | OBSERVE | rimworld/load_game; rimworld/start_debug_game_ready; rimworld/go_to_main_menu | rsw.bacta |
| BACTA_TANK_CORE_1.A3 | bui | A scarred pawn's old scar erases after the tuned immersion time. | OBSERVE | rimworld/load_game; rimworld/start_debug_game_ready; rimworld/go_to_main_menu | rsw.bacta |
| BACTA_TANK_CORE_1.A4 | bui | Tank fluid level drains with use and blocks further use at zero. | OBSERVE | rimworld/load_game; rimworld/start_debug_game_ready; rimworld/go_to_main_menu | rsw.bacta |
| BACTA_TANK_CORE_1.A5 | bui | Each of the 6 Mod Settings toggles, when switched off, disables exactly its effect. | OBSERVE | rimworld/load_game; rimworld/start_debug_game_ready; rimworld/go_to_main_menu | rsw.bacta |
| BAZAAR_PRICE_ENGINE_1.A2 | bui | Tradeable.GetPriceFor postfix is inert outside a Bazaar window and shifts prices inside one (needs BAZAAR_WIND | OBSERVE | - | rm.bazaar |
| BELT_WATER_HARNESS_1.A1 | bui | A live run of SUITE_WATER on Miasma proves the return behaviour passes with a painted pond. | OBSERVE | - |  |
| BELT_WATER_HARNESS_1.A2 | bui | A live run of SUITE_WATER on Greentide proves the vurrak chains pass with a painted pond. | OBSERVE | - |  |
| BELT_WATER_HARNESS_1.A3 | bui | After the run the pond is restored to the original bland world state. | OBSERVE | - |  |
| BILEWORM_CORPSE_ROT_1.A2 | bui | on a quicktest map a fresh corpse beside a spawned bileworm dissolves into corpse bile within a day; a nearby  | OBSERVE | - |  |
| BIOME_ARRIVAL_LETTERS_ALL_1.A2 | val | a gravship landing on a Fever Wood map raises the letter once; a second landing does not | OBSERVE | - |  |
| BLOWER_ROOM_COOLER_1.A3 | bui | live, a powered fuelled blower built into the wall of an enclosed room, front facing out, lowers that room tow | OBSERVE | - |  |
| BLOWER_ROOM_COOLER_1.A4 | bui | live, changing the strength and power settings changes the cooling rate and the power draw shown on the power  | OBSERVE | - |  |
| BRIDGE_KILL_HOSTILES_TOOL_1.A1 | bui | jawa/kill_hostiles on a quicktest map kills spawned hostiles, a colonist and a tamed animal survive, count ret | OBSERVE | jawa/kill_hostiles; jawa/get_defs |  |
| BRIDGE_KILL_HOSTILES_TOOL_1.A2 | bui | jawa/get_defs DesignationCategoryDef specialDesignatorClasses returns class names, not RuntimeType | DEFREAD | jawa/kill_hostiles; jawa/get_defs |  |
| BRIDGE_LOCK_CROSS_CLONE_RACE_1.A3 | bui | next real two-window session: a BENCH take blocks a FOUNDRY take without a push in between | OBSERVE | - |  |
| CATHEDRAL_MECHANOID_PASS_VERBS_1.A2 | bui | with the pass hediff mechanoids on a Cathedral map are not hostile, and nothing changes off Cathedral maps (GM | OBSERVE | - | rut.cathedralpass |
| CATHEDRAL_REGARD_BLACKBOARD_1.A2 | bui | live shadow logs show Regard moves in the stated direction for manners band, Assailant missions, restore choic | OBSERVE | jawa/trade_price_probe; jawa/trade_execute; jawa/biome_attitude_get |  |
| CATHEDRAL_REGARD_BLACKBOARD_1.A3 | bui | a crafting consumption of kyber moves no sale counter, resolving the sold-versus-crafted ambiguity | OBSERVE | jawa/trade_price_probe; jawa/trade_execute; jawa/biome_attitude_get |  |
| CATHEDRAL_STAGE_HUM_BRIDGE_1.A1 | bui | On a quicktest map, setting the cathedral stage to WARY or TOLERATED holds the hum band ceiling and shows reco | OBSERVE | - |  |
| CATHEDRAL_STAGE_HUM_BRIDGE_1.A2 | bui | After save and load the baseline hum state persists unchanged. | DEFREAD | - |  |
| CAULDRON_ENRICHMENT_LIVE_PROOF_1.A4 | val | With all three toggles off none of the assay string, letter or nettle spawning happens. | OBSERVE | - |  |
| CAULDRON_VENT_ENRICHMENT_HOOKS_1.A3 | val | Vent-keyed flowers appear around vents on the Cauldron map. | OBSERVE | - |  |
| CAULDRON_VENT_ENRICHMENT_HOOKS_1.A4 | val | The ventsEnabled, ventGardensEnabled and vexxissDrinksVentsEnabled settings toggles each disable their feature | OBSERVE | - |  |
| CHILL_AIR_PUMP_1.A2 | val | on a Chill floor map, a fuelled stove in a sealed roofed room with a powered pump lights; with the pump switch | OBSERVE | - |  |
| CHILL_AIR_PUMP_1.A3 | val | two pumps in one room; switching one off keeps the room lit, switching both off ends it | OBSERVE | - |  |
| CHILL_AIR_PUMP_1.A4 | val | a pump in an unroofed or edge-touching room oxygenates nothing and says so in its inspect line | OBSERVE | - |  |
| CHILL_DIVE_DENSITY_SAMPLER_1.A1 | bui | A generated Chill sea-floor map reads exactly 3 native animals by live state read. | OBSERVE | - |  |
| CRACKEDLANDS_ENRICHMENT_QUICKTEST_1.A1 | bui | On an RM_FloodedCanyon quicktest map the five beats, peakstorm, recede feast and salvage run through the behav | OBSERVE | - |  |
| CRACKEDLANDS_ENRICHMENT_QUICKTEST_1.A2 | bui | Four proofs triggered via dev actions each show their expected result (including RM_IrqitFloodBorn and tarruqS | OBSERVE | - |  |
| CRACKEDLANDS_FIVE_BEATS_AUDIO_1.A1 | bui | DebugStateReport shows tarruqSilenced=True from beat 3 until the recede. | OBSERVE | - |  |
| CREATURE_ALARM_ORIGIN_SHARE_1.A1 | bui | disturbed Kurreth rallies even when neighbours would exhaust the budget (live check owed) | OBSERVE | - |  |
| DANGER_CLOCK_ALERTS_1.A1 | bui | live check owed (see ## verify) | OBSERVE | - |  |
| DEAD_OR_INERT_SETTINGS_1.A2 | bui | Warscar cross-biome opt-in seeds wreck-lichen on an opted-in biome map; rarity 0 leaves no RM_Warscar tile on  | OBSERVE | - |  |
| DECOY_SHADE_TARP_1.A2 | bui | a shade-seeking animal paths to a placed decoy tarp and the shade grid reads 0 under it (art owed: tent textur | OBSERVE | - |  |
| DEEPS_FAUNA_MECHANICS_1.A1 | bui | The grapple comp is observed landing a hit on a live target in a quicktest. | OBSERVE | jawa/get_defs; jawa/ordered_job AttackMelee; rimworld/step_game_ticks |  |
| DEEPS_FAUNA_MECHANICS_1.A2 | bui | The drinker sac comps are observed firing live. | OBSERVE | jawa/get_defs; jawa/ordered_job AttackMelee; rimworld/step_game_ticks |  |
| DEEPS_FAUNA_MECHANICS_1.A3 | bui | The soulchime stun and soothe comps and shard armor are observed taking effect live. | OBSERVE | jawa/get_defs; jawa/ordered_job AttackMelee; rimworld/step_game_ticks |  |
| DEEPS_FAUNA_MECHANICS_2.A1 | bui | A bovine beetle spawned beside a colonist applies RM_Grappled and a torso injury, and a hit from a third pawn  | OBSERVE | - |  |
| DEEPS_FAUNA_MECHANICS_2.A2 | bui | A soulchime in line of sight stuns a pawn, and a deaf pawn is immune. | OBSERVE | - |  |
| DEEPS_FAUNA_MECHANICS_2.A3 | bui | A drinker feeding on a gembug gains RM_FluidSacks with observed severity and yield. | OBSERVE | - |  |
| DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1.A1 | bui | A live-spawned G2 droid shows no human face with useFactionXenotypes=false. | OBSERVE | - |  |
| DROIDWORKS_FACE_RENDER_DEFAULT_HUMAN_1.A2 | bui | Other Droidworks races are spawned live and none gain or lose a face unexpectedly (blast radius of the fix). | OBSERVE | - |  |
| DROIDWORKS_FORMAT_TIERS_1.A1 | bui | A mindless droid formatted to the Power tier is mindless with only the Power behaviour (box 2). | OBSERVE | jawa/pawn_health; jawa/list_pawns; jawa/pawn_need |  |
| DROIDWORKS_FORMAT_TIERS_1.A2 | bui | Formatting a sapient droid down breaks it as the sapient-break case specifies (box 3). | OBSERVE | jawa/pawn_health; jawa/list_pawns; jawa/pawn_need |  |
| DROIDWORKS_FORMAT_TIERS_1.A3 | bui | A blank-tier droid is inert (box 4). | OBSERVE | jawa/pawn_health; jawa/list_pawns; jawa/pawn_need |  |
| DROIDWORKS_FORMAT_TIERS_1.A4 | bui | CompDWFormatTier applies the tier hediff correctly on spawn or format (box 5). | OBSERVE | jawa/pawn_health; jawa/list_pawns; jawa/pawn_need |  |
| DROIDWORKS_FORMAT_TIERS_1.A5 | bui | The three format recipes are gated to the correct droid tiers (box 6). | OBSERVE | jawa/pawn_health; jawa/list_pawns; jawa/pawn_need |  |
| DROIDWORKS_FORMAT_TIERS_1.A6 | bui | Deformatting a sapient droid applies the deformat goodwill penalty and thought (box 7). | OBSERVE | jawa/pawn_health; jawa/list_pawns; jawa/pawn_need |  |
| DROIDWORKS_WIPE_SEVERITY_1.A2 | val | On a quicktest map a wiped droid stumbles across the seven days of the hediff. | OBSERVE | jawa/pawn_health; jawa/bill_add; jawa/ordered_job |  |
| DROIDWORKS_WIPE_SEVERITY_1.A3 | val | After the hediff ends the droid still carries its quirk, and a second wipe adds a second quirk rather than rep | OBSERVE | jawa/pawn_health; jawa/bill_add; jawa/ordered_job |  |
| DUNG_HATCH_WILDLIFE_CAP_1.A1 | bui | on a full-ecosystem map a shade whale dung trail spawns no young (live check owed) | OBSERVE | - |  |
| DUST_SETTLED_LETTER_1.A2 | bui | horizon.horizon_dust_settled_letter on a Stillsand map (a never-arriving warned group gets the letter, an arri | OBSERVE | - |  |
| EMPIRE_ESCALATION_LADDER_1.A5 | bui | quicktest probe rung: a probe drops >=40 cells out, transmits after ~2h LOS (ladder climbs to spotter), self-d | OBSERVE | - | rut.empirepursuit |
| EMPIRE_ESCALATION_LADDER_1.A6 | bui | quicktest spotter/strike/breach: spotter call completes on 6h LOS and fails when downed; repelled strike holds | OBSERVE | - | rut.empirepursuit |
| EMPIRE_ESCALATION_LADDER_1.A7 | bui | quicktest cordon: Empire siege camp builds despite canSiege=false, ion volley EMPs the engine and pushes coold | OBSERVE | - | rut.empirepursuit |
| EMPIRE_ESCALATION_LADDER_1.A8 | bui | quicktest bombardment: 24h telegraph ring drawn, Bombardment lands on the marked area, endless waves follow; l | OBSERVE | - | rut.empirepursuit |
| EMPIRE_ESCALATION_LADDER_1.A9 | bui | storyteller spacing: an unforced Empire raid inside 2 days of a ladder contact is refused; launch resets the n | OBSERVE | - | rut.empirepursuit |
| FALLEN_WIRE_SHOCK_1.A5 | val | live, a live end lying in a chemfuel puddle starts a fire within a few sweeps; with FlowWorks, one lying in ca | OBSERVE | - |  |
| FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1.A3 | val | A captured-to-slave feral survivor keeps the scar and a memwipe cannot remove it. | OBSERVE | - |  |
| FEVERWOOD_BOUGH_SOIL_TERRAIN_1.A2 | val | the eight crown flora roster rows actually root and grow on RUT_BoughSoil in a quicktest map | OBSERVE | - |  |
| FEVERWOOD_BROOD_RANSOM_1.A3 | val | tally - quicktest map with 2 occupied tanks + 1 cask reads 3 (+1 Sporefall while unfreed); after Return to the | OBSERVE | jawa/get_defs |  |
| FEVERWOOD_BROOD_RANSOM_1.A4 | val | gift - young released into a Fever Wood pool gives exactly one RM_DeepGiftLoot thing within 6 cells in 2,500 t | OBSERVE | jawa/get_defs |  |
| FEVERWOOD_BROOD_RANSOM_1.A6 | val | Sporefall - visiting Sporefall places RUT_SporefallDisplayTank owned by the Wildsteam; Free the young drops Wi | OBSERVE | jawa/get_defs |  |
| FEVERWOOD_BROOD_RANSOM_1.A7 | val | Wildsteam settlement/caravan trader stock can carry RM_SekkulaathYoungCask at Expensive; non-Wildsteam outland | OBSERVE | jawa/get_defs |  |
| FEVERWOOD_RM_CAST_COMPLETION_1.A4 | val | With the Shokk brood absent a live read of the TwoFrontLure second-wave faction returns RM_FactionDef_SkrethBr | OBSERVE | jawa/get_defs |  |
| FEVERWOOD_RM_CAST_COMPLETION_1.A5 | val | A live Faction.HostileTo read shows the skreth brood and kurreth swarm factions hostile to each other. | OBSERVE | jawa/get_defs |  |
| FEVERWOOD_RM_CAST_COMPLETION_1.A6 | val | Each of the seven texPaths resolves so a spawned pawn's graphic is not the error material. | LOG | jawa/get_defs |  |
| FLOWWORKS_BUILD_PROGRAM_1.A1 | bui | each of phases 1-8 quicktests alone on the minimal list, including a terraced run filling bottom-up from a nat | OBSERVE | jawa/canal_dig; [MayRequireOdyssey] |  |
| FLOWWORKS_BUILD_PROGRAM_1.A2 | bui | no flood leaves the channel, no source fails to run down, and conservation leaks only through a disclosed over | OBSERVE | jawa/canal_dig; [MayRequireOdyssey] |  |
| FLOWWORKS_CONTAINER_MATERIALS_1.A2 | val | material survives fill, wash and pour into a tank; metal and wood containers refuse acid, plasteel holds it; s | OBSERVE | rimworld/spawn_thing |  |
| FLOWWORKS_LADDER_RAISE_LOWER_1.A1 | bui | the toggle, haul and raised_hold runner scenes pass again on the flowworks tier (passed live 2026-10-06 per co | SCENE | - |  |
| FLOWWORKS_PIT_FALL_ONLY_FORCED_1.A1 | bui | On a quicktest map a forced or blown colonist falls into a pit via OnForcedDescent. | OBSERVE | - |  |
| FLOWWORKS_PIT_FALL_ONLY_FORCED_1.A2 | bui | An enemy under concealed pit cover falls in per the gauntlet expectations. | OBSERVE | - |  |
| FLOWWORKS_VISUAL_PRINCIPLES_1.A2 | val | State-read rows confirm the visual-principle components (wall face depth, face material, liquid surface, pit s | OBSERVE | - |  |
| FOOTPRINT_TRACK_GRID_1.A3 | val | On a Stillsand map the track_grid chain shows the writer recording prints, the invisible flag honoured, and to | OBSERVE | jawa/mod_settings_field action=list |  |
| FORCE_DISTURBANCE_REFLAVOR_1.A2 | bui | a live quicktest of each surveyed psychic storm or condition event shows Force-flavoured label and letter text | OBSERVE | - | rsw.patches |
| FORGE_DHOKKUR_WAYS_1.A2 | val | on a quicktest map a waking dhokkur plays the stone groan, leaves a polished trail that persists across cycles | OBSERVE | - |  |
| FORGE_ENRICHMENT_QUICKTEST_1.A3 | val | Forge voice stingers play for each phase. | OBSERVE | - |  |
| FORGE_ENRICHMENT_QUICKTEST_1.A4 | val | The dhuvvox run clock and seal count are unchanged by the slowing effect. | OBSERVE | - |  |
| FORGE_KEELWORK_REMAINDER_1.A1 | bui | The keel ring sound plays once per linked brace at launch on a quicktest map. | OBSERVE | - |  |
| FORGE_MECHANICS_1.A2 | bui | scald gear-gate quicktest shows damage when unroofed and ungeared and none when geared or roofed | OBSERVE | [MayRequireOdyssey]; [RUT_TheForge] |  |
| FORGE_MECHANICS_1.A3 | bui | F4 portal-chaining quicktest chains portals as designed | OBSERVE | [MayRequireOdyssey]; [RUT_TheForge] |  |
| FORGE_SPUNSTONE_SOURCES_1.A2 | val | On a quicktest map studying the salvage cache unlocks the floatstone door and spunstone hull. | OBSERVE | - |  |
| FORGE_WHITE_PLUME_FRONTS_1.A3 | val | A plume front moves off crusted cells on a quicktest map. | OBSERVE | - |  |
| FORGE_WHITE_PLUME_FRONTS_1.A4 | val | A plume front obscures ranged attacks. | OBSERVE | - |  |
| FORGE_WHITE_PLUME_FRONTS_1.A5 | val | RM_CompVaporDrifter creatures are unharmed by the fronts. | OBSERVE | - |  |
| GELATINOUSSLIME_TITAN_CHUNK_BOMB_1.A2 | val | a thrown titanoslime chunk drenches a test pawn into slimification on a quicktest map | OBSERVE | jawa/get_defs |  |
| GELATINOUSSLIME_TITAN_CHUNK_BOMB_1.A3 | val | an unused titanoslime chunk shrinks to nothing within its shelf time | OBSERVE | jawa/get_defs |  |
| GLOW_TANK_LIQUID_FEED_1.A2 | val | a salt-water tank beside it is drawn down one unit at a time and the crop grows; switching the setting off rem | OBSERVE | - |  |
| GM_BLACKBOARD_SHADOW_M4_1.A1 | bui | a live kyber sale raises Heat in the gm_blackboard_shadow log | LOG | rimworld/get_game_info; jawa/map_info; jawa/list_factions |  |
| GM_BLACKBOARD_SHADOW_M4_1.A2 | bui | the Cathedral-ground signal appears in the shadow log in a live run | LOG | rimworld/get_game_info; jawa/map_info; jawa/list_factions |  |
| GRAFFITI_NORTHSTAR_TRIAL_1.A3 | bui | The SHIP_1 rung is complete with art, stamp and deploy done. | OBSERVE | - | rm.graffiti |
| GRAVSHIP_ACOUSTIC_SCANNER_1.A2 | val | a landed gravship's pulse works on a Cracked Lands map and on a Stillsand map and the reading is always banded | OBSERVE | - |  |
| GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1.A2 | val | on a quicktest map a planted seed grows only when watered, and the greatbole core now ticks so the harvest lad | OBSERVE | - |  |
| GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1.A3 | val | with the dryad servants setting on, the crossover works; with it off (default) nothing changes | OBSERVE | - |  |
| GREENTIDE_BASE_PORT_BUILD_1.A4 | val | a Greentide quicktest map loads with the save aliases, steam devil and toxin sealed floor working | DEFREAD | jawa/get_defs |  |
| GREENTIDE_HUMMING_GROVE_1.A1 | bui | A deterministic state read shows the ProximitySoundscape layer count tracks the player's proximity to Thalquit | OBSERVE | - |  |
| GREENTIDE_STELLOCK_LACE_BUILD_1.A2 | val | Felling a roster tree drops the Stellock branch via the drop comp. | OBSERVE | jawa/get_defs |  |
| GREENTIDE_STELLOCK_LACE_BUILD_1.A3 | val | Study of the found tech unhides the research as expected via RM_CompFoundTechStudy. | OBSERVE | jawa/get_defs |  |
| GREENTIDE_STELLOCK_LACE_BUILD_1.A4 | val | The bleed factor reads 0 in the Laced stage and then greater than 0 afterwards. | OBSERVE | jawa/get_defs |  |
| GREENTIDE_STELLOCK_LACE_BUILD_1.A5 | val | The mechanism works outside Greentide on a non-Greentide use. | OBSERVE | jawa/get_defs |  |
| GREENTIDE_STELLOCK_LACE_BUILD_1.A6 | val | Each of the mod settings toggles disables its feature live. | OBSERVE | jawa/get_defs |  |
| GREENTIDE_THURROCK_HERD_BUILD_1.A3 | val | A spawned Thurrock keeps its hediff across save and load. | DEFREAD | jawa/get_defs |  |
| GREENTIDE_THURROCK_HERD_BUILD_1.A4 | val | A Thurrock fells trees and the toggle disables the behaviour. | OBSERVE | jawa/get_defs |  |
| GREENTIDE_THURROCK_HERD_BUILD_1.A5 | val | Aura wall damage differs between resting and manhunter Thurrocks. | OBSERVE | jawa/get_defs |  |
| HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1.A1 | bui | live check owed (see ## verify) | OBSERVE | - |  |
| HOSTILE_FLORA_FIRST_SCRIPT_1.A2 | bui | a live northstar_driver run of HostileFlora, including the reaction_cluster chain with a mental-state reader,  | CHAIN | modcheck floor | rm.hostileflora |
| HUTT_SLAVE_PIT_TEST_SITE_1.A1 | bui | A peaceful landing at the Hutt slave pit site succeeds on a quicktest map (blocked while GRAVSHIP_PEACEFUL_SET | OBSERVE | - |  |
| HUTT_SLAVE_PIT_TEST_SITE_1.A2 | bui | A slave, prisoner or downed beast can be sold for silver to the pit buyer. | OBSERVE | - |  |
| HUTT_SLAVE_PIT_TEST_SITE_1.A3 | bui | The oubliette is unreachable until conquest, after which the hoist lift works. | OBSERVE | - |  |
| JAWA_SWIM_HOOD_KEEP_1.A2 | bui | the swim gauntlet shows the hood kept while the Jawa swims | OBSERVE | - |  |
| KINETIC_BLAST_WEAPONS_1.EK.config | bui | lookup_projectile, lookup_zero_wins, impact_factor, body_override PASS | OBSERVE | - |  |
| KINETIC_BLAST_WEAPONS_1.EK.guards | bui | immunity_window and shield_counter PASS | OBSERVE | - |  |
| KINETIC_BLAST_WEAPONS_1.EK.reload | bui | recovery-window stamps survive a save/reload (no scene yet) | DEFREAD | - |  |
| KINETIC_BLAST_WEAPONS_1.EK.scenes18 | bui | the 18 v1 scenes still PASS after the 2026-10-06 config/guard/shield change | SCENE | - |  |
| LASSO_CHERRYPICKER_REMOVAL_1.A3 | bui | On a full-list load no lasso is craftable and none appears on pawns. | DEFREAD | - |  |
| LASSO_CHERRYPICKER_REMOVAL_1.A4 | bui | On a full-list load no MeleeAnimation errors appear in Player.log. | LOG | - |  |
| LAUNCH_HELD_COLONIST_WARNING_1.A3 | bui | live, a colonist sealed in a brine jacket (or swallowed by a Hwelgrue) is named in the gravship launch confirm | OBSERVE | - |  |
| LAUNCH_HELD_COLONIST_WARNING_1.A4 | bui | live, with the setting off the dialog is vanilla | OBSERVE | - |  |
| LEANINGSCRUB_ENRICHMENT_QUICKTEST_1.A2 | val | Checks 1 to 5 pass by state read on a quicktest map, including the stall and gale chains that were UNMEASURED. | OBSERVE | - |  |
| LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1.A2 | val | a state read of scavenger jobs shows an arm on the ground draws the ruled scavengers | OBSERVE | - |  |
| LIQUID_BOTTLE_LOOP_1.A1 | bui | On a quicktest map a bottle is filled from a shore, drunk, becomes dirty and is washed back to empty, confirmi | OBSERVE | - |  |
| LIQUID_BOTTLE_LOOP_1.A2 | bui | A boiling bottle becomes fresh and a blood bottle rots on schedule with the hemopack recipe beating the clock. | OBSERVE | - |  |
| LIQUID_BOTTLE_LOOP_1.A3 | bui | With settings off no dirty bottles appear anywhere and the loop remains whole. | OBSERVE | - |  |
| LIQUID_HEAT_PUSH_1.A3 | val | an open boiling patch identifies hot but reads outdoor, and the outdoor temperature beside it is unchanged | OBSERVE | - |  |
| LIQUID_INDUSTRY_SETPIECES_1.A2 | val | forced set-piece spawns place each ruin set piece near liquid on a quicktest map | OBSERVE | - |  |
| LIQUID_INDUSTRY_SETPIECES_1.A3 | val | each wrecked piece repairs and converts as designed and none appears in the build menu | OBSERVE | - |  |
| LIQUID_INDUSTRY_SETPIECES_1.A4 | val | jawa/list_things per slot confirms every set piece is present | OBSERVE | - |  |
| LIVE_ROUND2_FIXES_PROOF_1.A1 | bui | On a Stillsand quicktest a muffalo targeted by the MirrorBeam gets Burn after the cast, its currentJob is UseV | OBSERVE | jawa/pawn_use_verb action=cast verb="mirror crest"; jawa/list_pawns includeHealth; jawa/run_genstep RSW_GenStep_WhisperSarlaccSign |  |
| LIVE_ROUND2_FIXES_PROOF_1.A2 | bui | A soorrak captured over 2500 ticks yields an [RM CreatureBehaviors] instant job loop log line recorded into SO | LOG | jawa/pawn_use_verb action=cast verb="mirror crest"; jawa/list_pawns includeHealth; jawa/run_genstep RSW_GenStep_WhisperSarlaccSign |  |
| LONGSHADE_BEDAZZLE_CONTENT_1.A3 | bui | After compose deploy the LongShade atlas shows no magenta in game. | OBSERVE | - |  |
| LONGSHADE_ENRICHMENT_QUICKTEST_1.A1 | bui | The gloomcast moving shade layer moves live on a quicktest map. | OBSERVE | - |  |
| LONGSHADE_ENRICHMENT_QUICKTEST_1.A2 | bui | The Shipfall Commons ladder works live and survives save and load. | DEFREAD | - |  |
| LONGSHADE_ENRICHMENT_QUICKTEST_1.A3 | bui | The Greentide grove layers work live. | OBSERVE | - |  |
| LONGSHADE_ENRICHMENT_QUICKTEST_1.A4 | bui | Player.log shows no red errors from these features during the run. | LOG | - |  |
| LONGSHADE_MIDDENS_SPENT_BUILD_1.A1 | bui | new Long Shade map has 2-5 midden heaps at the down-sun end of small rocks; searching one yields vanilla items | OBSERVE | - |  |
| LONGSHADE_MIDDENS_SPENT_BUILD_1.A2 | bui | mirrak/gulloth shade patches show an "Unnaturally clean." inspect line on a ground marker | OBSERVE | - |  |
| MESSYCONDUIT_CABLE_PILE_LOOK_1.A2 | bui | on a quicktest map with two hose reels where the newer hose's free end rests on the older hose's body, the hos | OBSERVE | - |  |
| MESSYCONDUIT_CABLE_PILE_LOOK_1.A3 | bui | a hose crossing another at a bend draws no joiner on the crossing (probe joints vs drawn count), and a joiner  | OBSERVE | - |  |
| MESSYCONDUIT_REVIEW_ROUND1_1.A1 | bui | Live, bracket placement, pileArt and poleTex behave correctly in GimmeSomeSlack. | OBSERVE | - |  |
| MIASMA_MECHANICS_1.A1 | bui | M2 surge and salt-line movement is observed moving on a quicktest map in the Miasma biome | OBSERVE | [StaticConstructorOnStartup]; [0.04, 2.0] | rm.liquidtypes, rsw.swbestiary |
| MIASMA_MECHANICS_1.A2 | bui | M3 stranding pools appear and persist after the miasma recedes | OBSERVE | [StaticConstructorOnStartup]; [0.04, 2.0] | rm.liquidtypes, rsw.swbestiary |
| MIASMA_MECHANICS_1.A3 | bui | M6 the warden (RM_WardenMother) never leaves its anchor | OBSERVE | [StaticConstructorOnStartup]; [0.04, 2.0] | rm.liquidtypes, rsw.swbestiary |
| MINDSTONE_MATRIX_KINDLED_BUILD_1.A2 | val | The gauntlet of mine, recipes, assemble, then wipe refusal passes on a quicktest map. | OBSERVE | - |  |
| MOD_OPTIONS_RETROFIT_1.A2 | bui | For each mod toggling a feature off provably disables it live or at next map-gen on a quicktest map with no er | OBSERVE | [StaticConstructorOnStartup] |  |
| MOD_OPTIONS_RETROFIT_1.A3 | bui | The Greentide churnmud feature works in a non-Greentide biome when opted in. | OBSERVE | [StaticConstructorOnStartup] |  |
| MOVINGDUNES_WATER_BANKS_SAND_1.A2 | bui | on a dune map with a lake downwind, sand piles on the shore and the lake cells stay at depth 0 over a storm | OBSERVE | - |  |
| MOVING_DUNES_BUILD_1.A1 | bui | sand persists and moves downwind on a live map | OBSERVE | - |  |
| MOVING_DUNES_BUILD_1.A2 | bui | a burial cache is revealed as a dune moves off it | OBSERVE | - |  |
| MYCOID_COLOSSUS_LIVE_LOOK_1.A2 | bui | The colossus size changes as expected on north-height when it turns. | OBSERVE | - |  |
| NINEFOLD_FAVOUR_ODDS_BUILD_1.A2 | bui | on a quicktest map an offering shifts the favour odds and the Nine Faults rite runs (satiation-bank payment an | OBSERVE | - | rut.rites |
| NINEFOLD_LOUDNESS_FRONT_1.A1 | bui | A scripted gravship landing returns the correct front. | OBSERVE | - |  |
| NINEFOLD_LOUDNESS_FRONT_1.A2 | bui | A Large event flips the front mid-map. | OBSERVE | - |  |
| NINEFOLD_LOUDNESS_FRONT_1.A3 | bui | The front is kept across save and reload. | DEFREAD | - |  |
| NORTHSTAR_COMPANION_GAPS_1.A2 | val | each of the six tools is proven live on the minimal list returning correct data | OBSERVE | - |  |
| PIT_LIP_OCCLUDES_OUTSIDE_1.A1 | bui | a depth-4 pawn on a pit south row stays inside the opening and the muffalo lip cover spans the real sprite | OBSERVE | - |  |
| PIT_TEMPERATURE_SOFTENING_1.A2 | val | At desert noon an unroofed pit's temperature moves faster than a roofed twin. | OBSERVE | - |  |
| PIT_TEMPERATURE_SOFTENING_1.A3 | val | An occupant's resistance falls faster in the pit than in a normal prison cell. | OBSERVE | - |  |
| PIT_TEMPERATURE_SOFTENING_1.A4 | val | A compassionate colonist gets the RM_ExposedPrisoner thought and a psychopath does not. | OBSERVE | - |  |
| POLE_OWNER_CHANGE_DROPS_WIRES_1.A1 | bui | live check owed (see ## verify) | OBSERVE | - |  |
| PROMISED_GIFT_NEVER_LOST_1.A1 | bui | live check owed (see ## verify) | OBSERVE | - |  |
| RAKATAN_ARCHOTECH_MACHINES_1.A2 | bui | dev-spawned machines run, degrade gracefully and heal per grade on a quicktest map | OBSERVE | - |  |
| RIVER_STEAM_ANIMATION_1.A1 | bui | On a live Pyrelands-biome map steam puffs rise near river cells at a non-spammy rate with the reworked shape a | OBSERVE | jawa/map_info; jawa/world_links_set; jawa/get_terrain_batch | rsw.cuisine |
| RIVER_STEAM_ANIMATION_1.A2 | bui | On a non-Pyrelands map rivers stay silent so the biome gate holds. | OBSERVE | jawa/map_info; jawa/world_links_set; jawa/get_terrain_batch | rsw.cuisine |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A5 | val | on a Cathedral test map firing RM_LineCycle lowers the attitude band by one where band 1-3 (worst unchanged, b | OBSERVE | jawa/get_defs | rsw.swbestiary |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A6 | val | hum reading: a colonist with RM_HumReader makes RM_HumReading.Readout non-empty, removing it empties it; RM_Ga | OBSERVE | jawa/get_defs | rsw.swbestiary |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A7 | val | eels: on a canal-water Cathedral map RM_CoolantEel count > 0 and every eel stands on water after 5000 ticks; n | OBSERVE | jawa/get_defs | rsw.swbestiary |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A8 | val | strays: dessicated corpses within 8 cells of the edge > 0 with the toggle on, 0 off; no live pawn from the Gen | OBSERVE | jawa/get_defs | rsw.swbestiary |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1.A9 | val | each new Mod Settings toggle off removes exactly its effect | OBSERVE | jawa/get_defs | rsw.swbestiary |
| RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.A3 | val | chance 1 -> exactly one borehulk on a Rust Cathedral map on a non-sacred cell; chance 0 -> none; other biome - | OBSERVE | jawa/get_defs |  |
| RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.A4 | val | spawned borehulk reads comp Worn, faction null; harmed 2500 ticks it never starts an attack job, mental state  | OBSERVE | jawa/get_defs |  |
| RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.A5 | val | lowest hum band -> wait/freeze job; band restored -> moves within 2500 ticks | OBSERVE | jawa/get_defs |  |
| RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.A6 | val | 30000 ticks Worn -> 0 mined cells, RM_BorehulkGrind played >= 1 (comp counter); each Mod Settings toggle off r | OBSERVE | jawa/get_defs |  |
| RUSTCATHEDRAL_GOODWILL_FLOOR_1.A2 | val | calm_bands_reachable PASSES live; the worst-band drain, eel catch cost and drill response move the standing va | OBSERVE | - |  |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1.A2 | val | launch from a Rust Cathedral test map with living bolts within 4 cells, count forced 2: exactly 2 RM_HullBolt  | OBSERVE | jawa/get_defs | rut.rites |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1.A3 | val | -80C and +90C for 10,000 ticks each: no Hypothermia/Heatstroke/ToxicBuildup on any hull bolt; Flame and EMP da | OBSERVE | jawa/get_defs | rut.rites |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1.A4 | val | with a hull bolt aboard, selling one RM_BoltShedCuriosity adds one ledger entry at the configured weight and e | OBSERVE | jawa/get_defs | rut.rites |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1.A5 | val | landing on a Rust Cathedral map with ledger T raises starting irritation by min(T, cap) and the ledger reads e | OBSERVE | jawa/get_defs | rut.rites |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1.A6 | val | at hullBoltRealiseDays the mark set covers each hull bolt's cell and its inspect string carries the cold line | OBSERVE | jawa/get_defs | rut.rites |
| RUSTCATHEDRAL_HULL_BOLTS_BUILD_1.A7 | val | free tier: the dilemma letter fires once, only after a hum reader is on the map and a tell occurs | OBSERVE | jawa/get_defs | rut.rites |
| RUST_CATHEDRAL_MECHANICS_1.A2 | val | A whole-kit quicktest shows the Harmony patches bind, the coolant eel fishing interval scan runs, and the cath | OBSERVE | jawa/spawn_pawn; jawa/spawn_batch; jawa/list_pawns | rut.rustcathedralroaches |
| SALT_TRAVELS_WITH_DOOR_1.A1 | bui | live check owed (see ## verify) | OBSERVE | - |  |
| SALVAGE_WRECKAGE_EVERYWHERE_1.A2 | bui | on a quicktest map wreck fields scatter by density class per biome, careful deconstruct pays tiered loot, and  | OBSERVE | - |  |
| SALVAGE_WRECKAGE_EVERYWHERE_1.A3 | bui | the wreck-fall incident (step 5) fires from debug and drops a wreck | OBSERVE | - |  |
| SCALD_WATER_AGITATION_FLECKS_1.A2 | val | Light and heavy ripples appear and the water margin stays calm on a quicktest map. | OBSERVE | - |  |
| SCARLANDS_MECHANICS_2.A2 | val | On a Scarlands quicktest map the mark severity floor holds. | OBSERVE | - |  |
| SCARLANDS_MECHANICS_2.A3 | val | Scaria incubation onset occurs as designed. | OBSERVE | - |  |
| SCARLANDS_MECHANICS_2.A4 | val | A sentinel never pursues beyond its defended perimeter. | OBSERVE | - |  |
| SCARLANDS_MECHANICS_2.A5 | val | Pre-sprung hazards are present on the map. | OBSERVE | - |  |
| SCREEN_STOPS_SPORES_1.A2 | bui | a spore cloud next to a built Scarlands aerosol screen does nothing inside the dome and still hurts outside it | OBSERVE | - |  |
| SEA_DIVE_FLOOR_TERRAIN_1.A1 | bui | Scald sea-floor plants spawn from a real Scald-temperature tile, shown by rerunning prove_sea_dive_floor.py. | OBSERVE | - |  |
| SEA_DIVE_FLOOR_TERRAIN_1.A2 | bui | Chill sea-floor plants spawn from a real Chill-temperature tile, shown by rerunning prove_sea_dive_floor.py. | OBSERVE | - |  |
| SEA_FISHABLES_ALIVE_IN_DEPTHS_1.A3 | val | A floor census shows every fishable alive on the sea floor. | OBSERVE | - |  |
| SHIELD_MODS_LEVERAGE_1.A2 | val | a shield gauntlet on a quicktest map shows bubble, thermal veil, particulate and cryo fields each working | OBSERVE | [0.05, 0.98] |  |
| SHIPVERMIN_FREE_TIER_BEASTS_1.A3 | bui | with swbestiary loaded the canon creatures take the same four nest slots | OBSERVE | - | rsw.swbestiary |
| SHIP_TOW_LINE_1.A3 | bui | a placed winch drags a wreck chunk home one cell per reel interval (art owed: capstan base placeholder; KeelHo | OBSERVE | - |  |
| SOLAR_HEAT_EXPOSURE_1.A2 | bui | On a quicktest map sun exposure feeds vanilla heatstroke and each biome's heat kind behaves as declared. | OBSERVE | - |  |
| SOLAR_MIRRORS_BUILD_1.A3 | bui | a mirror aimed at a shaded cell lowers ShadeAt and raises ExposureAt there (read by `jawa/shade_probe`); a wal | OBSERVE | jawa/shade_probe |  |
| SOLAR_MIRRORS_BUILD_1.A4 | bui | a generated Long Shade map carries an ancient field whose solver report reads solvable with an unsolved start; | OBSERVE | jawa/shade_probe |  |
| SOLAR_MIRRORS_BUILD_1.A5 | bui | dust from a sandstorm lowers a mirror's delivered light; a cleaning job restores it. | OBSERVE | jawa/shade_probe |  |
| SOLAR_MIRRORS_BUILD_1.A6 | bui | a beam through a glazed aperture into a roofed room warms it; the furnace lit indoors warms its room. | OBSERVE | jawa/shade_probe |  |
| SOLAR_MIRRORS_BUILD_1.A7 | bui | the heliograph opens comms with a friendly faction in range by day and refuses at night. | OBSERVE | jawa/shade_probe |  |
| SPECIMEN_CABINET_DISPLAY_1.A2 | bui | a placed cabinet holding two distinct corpses reads Beauty +4 and the colony gets RM_SpecimenMuseum stage 0 (a | OBSERVE | - |  |
| STILLSAND_CAVE_AS_PLACE_1.A2 | val | A corpse placed in a Stillsand cave does not rot. | OBSERVE | - |  |
| STILLSAND_CAVE_AS_PLACE_1.A3 | val | The lens-grotto walls are mineable and yield RM_Biosilica. | OBSERVE | - |  |
| STILLSAND_EVENT_CREATURES_LIVE_1.A1 | bui | a wild krayt still spawns on a Stillsand map | OBSERVE | - |  |
| STILLSAND_EVENT_CREATURES_LIVE_1.A2 | bui | RUT_KraytAttack and RM_MuurrokEmergence fire by dev action on a Stillsand quicktest, a pawn of the kind appear | OBSERVE | - |  |
| STILLSAND_EVENT_CREATURES_LIVE_1.A3 | bui | the muurrok beam damages a target with no exception in Player.log and does nothing at night or in a Sandstorm | LOG | - |  |
| STILLSAND_EVENT_CREATURES_LIVE_1.A4 | bui | a take on sand leaves RM_Filth_DisturbedSand, a drag-mark line and a letter naming the taken, then the leviath | OBSERVE | - |  |
| STILLSAND_EVENT_CREATURES_LIVE_1.A5 | bui | the settings panel Stillsand: event creatures lists both incidents | OBSERVE | - |  |
| STILLSAND_EVENT_CREATURES_LIVE_1.A6 | bui | The Long Hunger is live-fired once on a Stillsand map | OBSERVE | - |  |
| STILLSAND_GEOPHONE_1.A2 | val | a submerged swimmer within the geophone radius shows the bearing and size-class marker | OBSERVE | - |  |
| STILLSAND_PRECIOUS_CAVES_LIVE_1.A2 | val | Across ten RM_Stillsand quicktest maps with rock at least eight carry a shade-mouth cave facing away from the  | OBSERVE | [Stillsand] precious cave:; [Stillsand] precious cave roll: |  |
| STILLSAND_PRECIOUS_CAVES_LIVE_1.A3 | val | A guzzka lair spawns the guzzka on its clutch. | OBSERVE | [Stillsand] precious cave:; [Stillsand] precious cave roll: |  |
| STILLSAND_PRECIOUS_CAVES_LIVE_1.A4 | val | No cave is generated outside rock. | OBSERVE | [Stillsand] precious cave:; [Stillsand] precious cave roll: |  |
| STILLSAND_PRECIOUS_CAVES_LIVE_1.A5 | val | The Rock island letter fires once on the home map and names the outcrop and bearing. | OBSERVE | [Stillsand] precious cave:; [Stillsand] precious cave roll: |  |
| STILLSAND_SAND_SIEVE_CHORE_1.A2 | val | A pawn carrying a sieve sifts sand without being ordered. | OBSERVE | - |  |
| STILLSAND_SAND_SIEVE_CHORE_1.A3 | val | A pawn without a sieve is never offered the sift job. | OBSERVE | - |  |
| STILLSAND_SKELETONS_REMAINDER_1.A3 | val | on a Stillsand quicktest, sandGrid.SetDepth 0.7 over a skeleton footprint then UpdateBurial() reads Buried, ha | OBSERVE | [ThreadStatic] |  |
| STILLSAND_SKELETONS_REMAINDER_1.A4 | val | a dev herd migration on a Stillsand map raises "Dust on the horizon", is delayed by horizonWarningHours, and P | OBSERVE | [ThreadStatic] |  |
| STILLSAND_SUN_LANCE_1.A2 | val | The sun lance damages a target and starts no fire. | OBSERVE | - |  |
| STILLSAND_SUN_LANCE_1.A3 | val | The sun lance does nothing to targets in shade or during a gale. | OBSERVE | - |  |
| STILLSAND_SUN_LIVE_VERIFY_1.A1 | bui | There is no night and shadow length varies by latitude. | OBSERVE | - |  |
| STILLSAND_SUN_LIVE_VERIFY_1.A2 | bui | A roof protects only above 55 degrees. | OBSERVE | - |  |
| STILLSAND_SUN_LIVE_VERIFY_1.A3 | bui | Shade exposure reads 0.35 and lee reads 0. | OBSERVE | - |  |
| STILLSAND_SUN_LIVE_VERIFY_1.A4 | bui | Far-ring pawns suffer heatstroke. | OBSERVE | - |  |
| STILLSAND_SUN_LIVE_VERIFY_1.A5 | bui | Solar panels produce at full output. | OBSERVE | - |  |
| STILLSAND_SUN_LIVE_VERIFY_1.A6 | bui | Glare, mirage, wind lock and cooling draught each work live. | OBSERVE | - |  |
| SUMP_TAR_NASTINESS_1.A2 | val | tar can be applied to a non-tar terrain and cleaned off it on a quicktest map | OBSERVE | - |  |
| SUMP_TAR_NASTINESS_1.A3 | val | a pawn crossing tar picks up the Tarred hediff | OBSERVE | - |  |
| SUMP_TAR_NASTINESS_1.A4 | val | the ScrubTarred surgery and a weak solvent remove the Tarred hediff | OBSERVE | - |  |
| SUMP_TAR_NASTINESS_1.A5 | val | the weak solvent is craftable from in-biome materials only and the Bitumen reward loop yields something a colo | OBSERVE | - |  |
| SUMP_TAR_NASTINESS_1.A6 | val | all four tar features toggle in Mod Settings | OBSERVE | - |  |
| SUMP_WALKWAYS_1.A2 | bui | Duckboards foul and slow pawns walking on them. | OBSERVE | - |  |
| SUMP_WALKWAYS_1.A3 | bui | Glasswalk caps speed near 80 percent and causes slip stagger. | OBSERVE | - |  |
| SUMP_WALKWAYS_1.A4 | bui | Both floors are placeable and glasswalk works aboard a gravship. | OBSERVE | - |  |
| SURFACE_RIVER_WEIRS_1.A2 | val | The live proof rows for current, fords, flood surge, wash-off, weir, levee, silt trap, ferry and drift pass on | OBSERVE | - |  |
| TAKEN_BY_LAND_SERVICE_1.A3 | bui | a pawn swept off the river edge and a pawn carried off by a gale each get a letter, a drag mark where they sto | OBSERVE | - | rm.traces |
| TERMINALBIOMES_REVIEW_FIXES_1.A2 | bui | the lure springs in a live quicktest | OBSERVE | - |  |
| TERMINALBIOMES_REVIEW_FIXES_1.A3 | bui | the mobile glower moves in a live quicktest | OBSERVE | - |  |
| THICK_LIQUID_CREEP_1.A2 | bui | a tar channel on a bridge map fills at the stated speed in game | OBSERVE | - |  |
| TILE_STRUCTURE_DESIGNS_1.A1 | bui | A quicktest shows the live terrain and roof ordering of injected structures is correct (sole closure bar). | OBSERVE | - | rm.injections, rsw.injections, rut.injections |
| TILE_TEMP_CACHE_RESET_TOOL_1.A1 | bui | after a temperature retile, jawa/world_cache_audit includeTemps shows stale caches, jawa/world_tile_cache_rese | OBSERVE | - |  |
| TREE_GRAPHICS_OWNERSHIP_1.A1 | bui | RUT_SweetlineTree spawns and the BetterTrees-immunity log check passes | LOG | jawa/spawn_thing; [0,0,0,0] | rut.ashkarrflora |
| TWILIGHT_WELL_AVOIDS_CURRENT_1.A1 | bui | live check owed (see ## verify) | OBSERVE | - |  |
| UNFINISHED_LINE_TITHE_BEAT_1.A2 | bui | The tithe beat gauntlet passes: tithe is taken, a lent colonist returns after 10 days, and a lent colonist's d | OBSERVE | - |  |
| UNFINISHED_LINE_WORLD_FOUNDRY_1.A4 | val | modcheck chain 'world' on a save with the Enclaves allied: stand -> runs=True; volunteer offered; Enclave trad | CHAIN | - |  |
| UNFINISHED_LINE_WORLD_FOUNDRY_1.A5 | val | accept the volunteer: one droid joins the player with no bolt/wipe hediff; bolting it flips betrayed=True, cos | OBSERVE | - |  |
| UNFINISHED_LINE_WORLD_FOUNDRY_1.A6 | val | settlement regrowth: an Enclave settlement map generated while the line runs gets more defenders than baseline | OBSERVE | - |  |
| VAULT_DUNGEON_BUILD_1.A1 | bui | type 2 vault proof is run with the third-party symbol mods on the tier | OBSERVE | jawa/kcsg_place; rimworld/get_cell_info | rm.injections, rut.injections |
| VAULT_DUNGEON_BUILD_1.A2 | bui | the LARGE size check of each vault template is run on a quicktest map | OBSERVE | jawa/kcsg_place; rimworld/get_cell_info | rm.injections, rut.injections |
| VAULT_THAW_QUEST_FAMILY_1.A2 | val | The V6 quest runs on a quicktest map. | OBSERVE | [symbol] | rm.injections, rut.injections |
| VAULT_THAW_QUEST_FAMILY_1.A3 | val | The V1 garrison appears as designed. | OBSERVE | [symbol] | rm.injections, rut.injections |
| VAULT_THAW_QUEST_FAMILY_1.A4 | val | Quest gating works and the vault is inert on arrival. | OBSERVE | [symbol] | rm.injections, rut.injections |
| VAULT_THAW_QUEST_FAMILY_1.A5 | val | The Reclamation quest runs through. | OBSERVE | [symbol] | rm.injections, rut.injections |
| VERMIN_EAT_BREEDING_FOOD_1.A3 | bui | a grub litter shrinks the fruit pile by the setting and a walled-off pile starves the breeder (tune verminLitt | OBSERVE | - |  |
| WARSCAR_AEROSOL_SCREEN_1.A2 | bui | inside a dome no toxic buildup occurs in fallout, ToxRain, RM_Settling or Wasteland ash (needs a building that | OBSERVE | - |  |
| WARSCAR_CHOTRIX_SIGNS_1.A2 | val | on a quicktest map a walking chotrix leaves chotrix print tracks and a kill leaves a drag mark that a colonist | OBSERVE | - |  |
| WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1.A2 | bui | cataloguing the Pilgrim journal once advances the Scarlands ladder live | OBSERVE | - |  |
| WARSCAR_RAINBOW_POOLS_1.A2 | val | A quicktest Warscar map holds 1 to 3 reaction pools. | OBSERVE | - |  |
| WARSCAR_RAINBOW_POOLS_1.A3 | val | Drawing from each phase yields its reagent, and drawing the bloom phase injures the drawer. | OBSERVE | - |  |
| WARSCAR_RAINBOW_POOLS_1.A4 | val | With glower crust the phase holds and yield doubles, and without it the phase cycles. | OBSERVE | - |  |
| WARSCAR_TOTCHAK_WAKES_1.A2 | val | A totchak placed in a wall run wakes within 12 cells and a letter fires. | OBSERVE | - |  |
| WARSCAR_TOTCHAK_WAKES_1.A3 | val | The totchak gnaws ruin before player structures. | OBSERVE | - |  |
| WARSCAR_TOTCHAK_WAKES_1.A4 | val | The totchak returns to dormancy after waking. | OBSERVE | - |  |
| WARSCAR_TURRETS_TRACK_1.A2 | val | A state read on a quicktest map shows the RM_CompTurretAim aim angle changes as designed. | OBSERVE | - |  |
| WARSCAR_TURRETS_TRACK_1.A3 | val | The Refit gizmo yields a turret that fires. | OBSERVE | - |  |
| WAR_LAB_CRATER_HOOK_1.A1 | bui | Igniting the reactor core flips the derived tiles to the crater biome. | OBSERVE | jawa/world_tile_set; jawa/world_commit |  |
| WAR_LAB_CRATER_HOOK_1.A2 | bui | The crater mutation persists across save and load. | DEFREAD | jawa/world_tile_set; jawa/world_commit |  |
| WAR_LAB_CRATER_HOOK_1.A3 | bui | The crater fires only once. | OBSERVE | jawa/world_tile_set; jawa/world_commit |  |
| WAR_LAB_CRATER_HOOK_1.A4 | bui | The hook works while the map is unloaded. | OBSERVE | jawa/world_tile_set; jawa/world_commit |  |
| WASTELAND_GPT_ENRICHMENT_1.A1 | val | Named storms fire on a quicktest map. | OBSERVE | - |  |
| WASTELAND_GPT_ENRICHMENT_1.A4 | val | The Rite of Tipping runs through. | OBSERVE | - |  |
| WASTELAND_MECHANICS_BUILD_1.A3 | val | A penned Sloghog on polluted ground produces a bezoar. | OBSERVE | - |  |
| WASTELAND_MECHANICS_BUILD_1.A4 | val | A Smolderback heats and doses a closed room. | OBSERVE | - |  |
| WASTELAND_MECHANICS_BUILD_1.A5 | val | When an ash storm ends cinderfelt appears on the fresh fall and the exhumation re-deal fires via the MovingDun | OBSERVE | - |  |
| WEBWORK_DEAD_GIANT_BUILD_1.A2 | bui | all RM_Urraveth_Remains pieces spawn, can be read, and the creak gauntlet runs | OBSERVE | - |  |
| WEBWORK_TRACTION_LANCE_BUILD_1.A3 | val | The gauntlet passes for pull, wall, friendly, ollathrix-shade, stuff, research and settings behaviour. | OBSERVE | - |  |
| WEEPINGSTONES_CONDENSER_QUESTS_1.C3 | bui | each quest fires from the dev quest menu on a quicktest with a debug-spawned condenser crab | OBSERVE | - |  |
| WEEPINGSTONES_CONDENSER_QUESTS_1.C4 | bui | capture branch removes the crab with a letter and ends the walking condenser's world state | OBSERVE | - |  |
| WEEPINGSTONES_CONDENSER_QUESTS_1.C5 | bui | keep-free branch spawns hunters; a strike at the pool triggers retribution; success letter and goodwill | OBSERVE | - |  |
| WEEPINGSTONES_STOCK_JOB_LOOP_1.A1 | bui | The job_net, job_stock, job_stock_outside_pen and job_cull checks pass on rerun after the driver fixes. | OBSERVE | - |  |
| WEEPINGSTONES_STOCK_JOB_LOOP_1.A2 | bui | The feed and harvest job chains complete live. | OBSERVE | - |  |
| WETBULB_FOLD_INTO_HEAT_1.A2 | bui | on the live full tier, Player.log has no cross-reference or config error naming the deleted defs after deployi | LOG | - |  |
| WETBULB_FOLD_INTO_HEAT_1.A3 | bui | live, an unprotected colonist outdoors on a Greentide map gains vanilla Heatstroke, and one in an enclosed roo | OBSERVE | - |  |
| WETBULB_FOLD_INTO_HEAT_1.A4 | bui | live, the sealed suit raises the wearer's ComfyTemperatureMax by roughly 1.4x the stuff's heat insulation | OBSERVE | - |  |
| WIRE_DOWN_ALERT_1.A1 | bui | probe alert lists the anchors of a cut span (down>=2, enabled) and is empty after restring; wireDownAlert=fals | OBSERVE | - |  |
| WORLDMAP_LIQUID_TAGS_1.A1 | bui | On a landing quicktest of the canonical Ash'karr save, each of the four biomes' shores is repainted to its tag | OBSERVE | jawa/world_tile_set; jawa/world_tile_export; jawa/world_stats |  |
| WRECKED_DISTILLATION_MODULE_1.A2 | val | salt water converts to fresh, tar is refused, and tier rates differ | OBSERVE | - |  |
| WYYYSCHOKK_FANG_PENDANT_1.A2 | val | Butchering a wyyyschokk (RM_Ollathrix) yields fangs and the pendant can be crafted. | OBSERVE | - |  |
| WYYYSCHOKK_FANG_PENDANT_1.A3 | val | Observers of a listed faction show an opinion delta from the pendant and observers of an unlisted faction do n | OBSERVE | - |  |
| WYYYSCHOKK_FANG_PENDANT_1.A4 | val | The pendant sells to a vanilla trader and coexists with other neck-slot apparel. | OBSERVE | - |  |

### 3.c GREEN-MIN (sitting 3) (110 criteria)

| item.crit | st | criterion | fam | named instrument | + mods |
|---|---|---|---|---|---|
| ABYSS_FIRST_SCRIPT_1.A1 | val | A live northstar_driver run of the Abyss validation script on the smallest tier that loads the mod completes a | DEFREAD | modcheck floor |  |
| ASSAILANT_SALVAGE_FIRST_SCRIPT_1.A1 | bui | one live northstar run of the AssailantSalvage validation script on the smallest mod list that loads it is rec | DEFREAD | modcheck floor | rut.assailantsalvage |
| ASSAILANT_SALVAGE_FIRST_SCRIPT_1.A2 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor | rut.assailantsalvage |
| BACTA_FIRST_SCRIPT_1.A2 | bui | one live northstar_driver run of Bacta on the smallest tier that loads it is recorded with its results JSON in | DEFREAD | modcheck floor |  |
| BACTA_FIRST_SCRIPT_1.A3 | bui | every non-pass in the Bacta run is classified as harness, site, mod or unmeasured and none is hidden | SCENE | modcheck floor |  |
| BLUE_DESERT_FIRST_SCRIPT_1.A2 | bui | One live driver run of BlueDesert validation.py on the minimal list produces a results JSON. | CHAIN | modcheck floor |  |
| BLUE_DESERT_FIRST_SCRIPT_1.A3 | bui | Every FAIL in that results JSON is classified as harness, site, mod or unmeasured. | SCENE | modcheck floor |  |
| BRAIN_WORMS_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the BrainWorms validation script on the smallest mod list that loads it is recorded  | DEFREAD | modcheck floor |  |
| BRAIN_WORMS_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| CONTAGION_FIRST_SCRIPT_1.A2 | bui | one live northstar_driver run of Contagion on the smallest tier that loads it is recorded with its results JSO | DEFREAD | modcheck floor |  |
| CONTAGION_FIRST_SCRIPT_1.A3 | bui | every non-pass in the Contagion run is classified as harness, site, mod or unmeasured and none is hidden | SCENE | modcheck floor |  |
| CREATURE_BEHAVIORS_FIRST_SCRIPT_1.A3 | val | the CreatureBehaviors validation script passes on the minimal list with every non-pass classified | OBSERVE | modcheck floor |  |
| DIVING_INTERACTION_FIRST_SCRIPT_1.A2 | bui | a live northstar_driver run of DivingInteraction via the driver (beyond the Grey-floor run) is recorded with i | CHAIN | modcheck floor |  |
| DIVING_INTERACTION_FIRST_SCRIPT_1.A3 | bui | every non-pass in the DivingInteraction run is classified as harness, site, mod or unmeasured | SCENE | modcheck floor |  |
| DROIDWORKS_WIPE_SEVERITY_1.A4 | val | The Droidworks north-star bars covering wipe severity pass on the minimal list. | CHAIN | jawa/pawn_health; jawa/bill_add; jawa/ordered_job |  |
| ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the EnvironmentalHazards validation script on the smallest mod list that loads it is | DEFREAD | modcheck floor |  |
| ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| EXPLOSIVE_GROWTH_FIRST_SCRIPT_1.A2 | bui | one live northstar_driver run of ExplosiveGrowth on the smallest tier that loads it is recorded with its resul | DEFREAD | modcheck floor | rm.explosivegrowth |
| EXPLOSIVE_GROWTH_FIRST_SCRIPT_1.A3 | bui | every non-pass in the ExplosiveGrowth run is classified as harness, site, mod or unmeasured and none is hidden | SCENE | modcheck floor | rm.explosivegrowth |
| FEVER_WOOD_FIRST_SCRIPT_1.A1 | bui | A fresh live run of the FeverWood validation script on the minimal list leaves modcheck status no longer RED w | CHAIN | modcheck floor |  |
| FEVER_WOOD_FIRST_SCRIPT_1.A2 | bui | Every FAIL from that run is classified. | OBSERVE | modcheck floor |  |
| FLOODED_CANYON_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the FloodedCanyon validation script on the smallest mod list that loads it is record | DEFREAD | modcheck floor |  |
| FLOODED_CANYON_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| FLOWWORKS_BUILD_PROGRAM_1.A3 | bui | the FlowWorks north-star baseline run (FLOWWORKS_NORTHSTAR_BASELINE_RUN_1) is recorded on the minimal list | CHAIN | jawa/canal_dig; [MayRequireOdyssey] |  |
| FLOWWORKS_NORTHSTAR_BASELINE_RUN_1.A2 | bui | Each failed component from the FlowWorks baseline run has a recorded finding. | OBSERVE | - |  |
| FLOWWORKS_NORTHSTAR_BASELINE_RUN_1.A3 | bui | The committed live run results are confirmed to match the item's acceptance. | OBSERVE | - |  |
| FLOWWORKS_NORTHSTAR_TRIAL_1.A1 | bui | BASELINE_RUN_1 and GREEN_MINIMAL_1 pass live on the minimal list for FlowWorks. | OBSERVE | modcheck run |  |
| FLOWWORKS_NORTHSTAR_TRIAL_1.A4 | bui | The six bars that fail by design for unbuilt features are recorded as classified findings rather than hidden. | OBSERVE | modcheck run |  |
| FLOWWORKS_PIT_FALL_ONLY_FORCED_1.A3 | bui | The FlowWorks pit north-star bars pass on the minimal list. | CHAIN | - |  |
| FORGE_SPUNSTONE_SOURCES_1.A4 | val | The TheForge north-star bars for these sources pass on the minimal list. | CHAIN | - |  |
| FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the FungalSoilTrade validation script on the smallest mod list that loads it is reco | DEFREAD | modcheck floor |  |
| FUNGAL_SOIL_TRADE_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| GELATINOUS_SLIME_FIRST_SCRIPT_1.A2 | bui | A recorded live driver run of the GelatinousSlime north star on the minimal list produced a results JSON, and  | CHAIN | modcheck floor |  |
| GIZKA_STOWAWAY_FIRST_SCRIPT_1.A1 | val | A live northstar_driver run of the GizkaStowaway validation script on the smallest tier that loads the mod com | DEFREAD | modcheck floor |  |
| GIZKA_STOWAWAY_FIRST_SCRIPT_1.A3 | val | modcheck status for GizkaStowaway reads GREEN with a current hash after the re-run. | CHAIN | modcheck floor |  |
| GRAFFITI_IMPERIAL_FIRST_SCRIPT_1.A2 | bui | One live northstar driver run of GraffitiImperial on the minimal list completes with a results JSON, proving t | CHAIN | modcheck floor | rm.graffiti |
| GRAFFITI_IMPERIAL_FIRST_SCRIPT_1.A3 | bui | Every FAIL in that run is classified as harness, site, mod or unmeasured. | SCENE | modcheck floor | rm.graffiti |
| GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1.A2 | val | The Graffiti north-star trial runs using these tools. | CHAIN | - | rm.graffiti |
| GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1.A1 | bui | The Graffiti north-star run on the minimal list plus Graffiti only passes. | CHAIN | modcheck status; modcheck review Graffiti --owner-said … | rm.graffiti |
| GRAFFITI_NORTHSTAR_TRIAL_1.A1 | bui | The Graffiti northstar passes on the minimal list. | CHAIN | - | rm.graffiti |
| GRAVSHIP_LANDING_FIRST_SCRIPT_1.A2 | bui | A recorded live driver run of the GravshipLanding north star on the minimal list produced a results JSON, and  | CHAIN | modcheck floor |  |
| GREENTIDE_RAID_ANT_FIRST_SCRIPT_1.A2 | bui | One live run of the validation script on the minimal list produces a results JSON. | OBSERVE | modcheck floor |  |
| GREENTIDE_RAID_ANT_FIRST_SCRIPT_1.A3 | bui | Every non-passing bar, including directed assault, faction hidden and butchery, is classified. | OBSERVE | modcheck floor |  |
| GREENTIDE_STELLOCK_LACE_BUILD_1.A7 | val | The Greentide north-star bars pass on the minimal list. | CHAIN | jawa/get_defs |  |
| HOSTILE_FLORA_FIRST_SCRIPT_1.A3 | bui | every non-pass in the HostileFlora run is classified as harness, site, mod or unmeasured | SCENE | modcheck floor | rm.hostileflora |
| KYBER_TRADE_PLOT_FIRST_SCRIPT_1.A2 | bui | One live northstar run of KyberTradePlot on the minimal list completes with a results JSON, settling quest gen | CHAIN | modcheck floor |  |
| KYBER_TRADE_PLOT_FIRST_SCRIPT_1.A3 | bui | Every FAIL in that run is classified as harness, site, mod or unmeasured. | SCENE | modcheck floor |  |
| LEANINGSCRUB_ENRICHMENT_QUICKTEST_1.A3 | val | The LeaningScrub north-star rerun on the minimal list passes. | CHAIN | - |  |
| LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1.A3 | val | the LeaningScrub north-star bar covering the arm and scavengers passes on the minimal list | CHAIN | - |  |
| LEANING_SCRUB_FIRST_SCRIPT_1.A2 | bui | A recorded live driver run of the LeaningScrub north star on the minimal list produced a results JSON, and eac | CHAIN | modcheck floor |  |
| LONG_SHADE_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the LongShade validation script on the smallest mod list that loads it is recorded w | DEFREAD | modcheck floor |  |
| LONG_SHADE_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| LORE_STAGES_FIRST_SCRIPT_1.A2 | bui | one live northstar_driver run of LoreStages (offline_mechanism chain only, as no bridge tool drives SetStage)  | CHAIN | modcheck floor | rm.lorestages |
| LORE_STAGES_FIRST_SCRIPT_1.A3 | bui | every non-pass in the LoreStages run is classified as harness, site, mod or unmeasured | SCENE | modcheck floor | rm.lorestages |
| MESSYCONDUIT_REVIEW_ROUND1_1.A2 | bui | modcheck for GimmeSomeSlack moves from DRAFT-CHECKLIST to a passing run. | CHAIN | - |  |
| MIASMA_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the Miasma validation script on the smallest mod list that loads it is recorded with | DEFREAD | modcheck floor |  |
| MIASMA_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| MINDSTONE_MATRIX_KINDLED_BUILD_1.A3 | val | The mindstone north star bars pass on the minimal list. | CHAIN | - |  |
| MOVING_DUNES_FIRST_SCRIPT_1.A2 | bui | One live northstar run of MovingDunes on the minimal list completes with a results JSON, settling the debug-ac | CHAIN | modcheck floor |  |
| MOVING_DUNES_FIRST_SCRIPT_1.A3 | bui | Every FAIL in that run is classified as harness, site, mod or unmeasured. | SCENE | modcheck floor |  |
| OASIS_MAKER_FIRST_SCRIPT_1.A2 | bui | a live run of the OasisMaker validation script on a staged pad produces a results JSON in Transient/northstar | CHAIN | modcheck floor | rm.oasismaker |
| OASIS_MAKER_FIRST_SCRIPT_1.A3 | bui | the debug-action path and Granite_Rough pad assumptions are confirmed or classified in the results | OBSERVE | modcheck floor | rm.oasismaker |
| PIT_TEMPERATURE_SOFTENING_1.A5 | val | The FlowWorks north-star bars for pit exposure pass on the minimal list. | CHAIN | - |  |
| PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1.A2 | bui | One live north-star run on the minimal list produces a results JSON. | CHAIN | modcheck floor |  |
| PROPANE_LAKE_MECHANICS_FIRST_SCRIPT_1.A3 | bui | Every non-passing bar from that run is classified. | OBSERVE | modcheck floor |  |
| PYRELANDS_GREEN_MINIMAL_1.A1 | bui | a live Pyrelands run on the pyrelands tier passes every bar at its plan predicate with evidence HTML and summa | OBSERVE | modcheck run |  |
| PYRELANDS_GREEN_MINIMAL_1.A2 | bui | the 30 C control site run is recorded alongside the 50 C sites | OBSERVE | modcheck run |  |
| PYRELANDS_GREEN_MINIMAL_1.A3 | bui | rimflow verify PYRELANDS_GREEN_MINIMAL_1 is recorded with result and config pyrelands-tier and the evidence pa | OBSERVE | modcheck run |  |
| PYRINTH_FIRST_SCRIPT_1.A3 | val | A live northstar_driver run of the Pyrinth validation script on the smallest tier that loads the mod completes | DEFREAD | modcheck floor | rm.pyrinth |
| RIVER_COLORS_FIRST_SCRIPT_1.A2 | val | one live driver run of the RiverColors validation script on the minimal list produces a results JSON in Transi | CHAIN | modcheck floor |  |
| RUST_CATHEDRAL_MECHANICS_1.A3 | val | The RustCathedral north-star bars pass on the minimal list. | CHAIN | jawa/spawn_pawn; jawa/spawn_batch; jawa/list_pawns | rut.rustcathedralroaches |
| RUST_CATHEDRAL_ROACHES_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the RustCathedral validation script on the smallest mod list that loads it is record | DEFREAD | modcheck floor |  |
| RUST_CATHEDRAL_ROACHES_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| SARLACC_FIRST_SCRIPT_1.A3 | bui | one live northstar_driver run of Sarlacc is recorded with its results JSON | CHAIN | modcheck floor |  |
| SARLACC_FIRST_SCRIPT_1.A4 | bui | every FAIL in the Sarlacc run is classified as harness, site, mod or unmeasured | SCENE | modcheck floor |  |
| SCARLANDS_FIRST_SCRIPT_1.A2 | val | A live northstar_driver run of the Scarlands validation script on the smallest tier that loads the mod complet | DEFREAD | modcheck floor |  |
| SCARLANDS_LADDER_FIRST_SCRIPT_1.A2 | val | one live driver run of the ScarlandsLadder validation script on the minimal list produces a results JSON in Tr | CHAIN | modcheck floor |  |
| SCAVENGER_EVENTS_FIRST_SCRIPT_1.A2 | bui | One live run of the validation script on the minimal list produces a results JSON. | OBSERVE | modcheck floor |  |
| SCAVENGER_EVENTS_FIRST_SCRIPT_1.A3 | bui | Every non-pass from that run is classified. | OBSERVE | modcheck floor |  |
| SHIELD_MODS_LEVERAGE_1.A3 | val | the ShipShields north-star bars pass on the minimal list | CHAIN | [0.05, 0.98] |  |
| SHIP_VERMIN_FIRST_SCRIPT_1.A2 | val | A live northstar_driver run of the ShipVermin validation script on the smallest tier that loads the mod comple | DEFREAD | modcheck floor |  |
| SHOKKWEAVE_ECONOMY_FIRST_SCRIPT_1.A2 | val | one live driver run of the ShokkweaveEconomy validation script on the minimal list produces a results JSON in  | CHAIN | modcheck floor |  |
| SHOKK_FIRST_SCRIPT_1.A3 | bui | One live northstar run of Shokk completes with a results JSON. | CHAIN | modcheck floor |  |
| SHOKK_FIRST_SCRIPT_1.A4 | bui | Every FAIL in that run is classified as harness, site, mod or unmeasured. | SCENE | modcheck floor |  |
| STILLSAND_FIRST_SCRIPT_1.A2 | bui | A recorded live driver run of the Stillsand north star on the minimal list produced a results JSON, and each F | CHAIN | modcheck floor |  |
| SUMP_TAR_NASTINESS_1.A7 | val | the TheSump north-star bars covering tar nastiness pass on the minimal list | CHAIN | - |  |
| SURFACE_RIVER_WEIRS_1.A3 | val | The RiverWorks walk passes on the minimal list. | OBSERVE | - |  |
| TERMINAL_BIOMES_FIRST_SCRIPT_1.A2 | bui | One live northstar run of TerminalBiomes completes with a results JSON in Transient/northstar. | CHAIN | modcheck floor |  |
| TERMINAL_BIOMES_FIRST_SCRIPT_1.A3 | bui | Every FAIL in that run is classified as harness, site, mod or unmeasured. | SCENE | modcheck floor |  |
| THE_BAZAAR_FIRST_SCRIPT_1.A2 | bui | One live run of the TheBazaar validation script on the minimal list is performed. | OBSERVE | modcheck floor | rm.bazaar |
| THE_FORGE_FIRST_SCRIPT_1.A1 | bui | One live run of TheForge validation.py on the minimal list is recorded as a results JSON. | OBSERVE | modcheck floor |  |
| THE_FORGE_FIRST_SCRIPT_1.A2 | bui | Every finding in that run is classified. | OBSERVE | modcheck floor |  |
| THE_ROT_FIRST_SCRIPT_1.A2 | bui | one live northstar run of the TheRot validation script on the smallest mod list that loads it is recorded with | DEFREAD | modcheck floor |  |
| THE_ROT_FIRST_SCRIPT_1.A3 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| THE_SUMP_FIRST_SCRIPT_1.A3 | val | one live northstar_driver run of TheSump is recorded with its results JSON | CHAIN | - |  |
| THE_SUMP_FIRST_SCRIPT_1.A4 | val | every FAIL in the TheSump run is classified as harness, site, mod or unmeasured | SCENE | - |  |
| TITANIC_CREATURES_FIRST_SCRIPT_1.A2 | val | A live northstar_driver run of the TitanicCreatures validation script on the smallest tier that loads the mod  | DEFREAD | modcheck floor |  |
| UTINNI_DISCOVERY_ACHIEVEMENTS_1.A2 | bui | The first live run of the Atlas north-star validation on the minimal list passes, beyond the mock green. | CHAIN | - | rut.atlas |
| WARCASKET_FIRST_SCRIPT_1.A2 | val | A live northstar_driver run of the Warcasket validation script on the smallest tier that loads the mod complet | DEFREAD | modcheck floor | rm.warcasket |
| WASTELAND_FIRST_SCRIPT_1.A1 | bui | a live northstar_driver run of Wasteland via a composed route that can find the biome is recorded with its res | CHAIN | modcheck floor |  |
| WASTELAND_FIRST_SCRIPT_1.A2 | bui | every FAIL in the Wasteland run is classified as harness, site, mod or unmeasured | SCENE | modcheck floor |  |
| WASTELAND_FIRST_SCRIPT_1.A3 | bui | the 154 components never run live are each measured in the run or marked unmeasured | OBSERVE | modcheck floor |  |
| WEBWORK_DEAD_GIANT_BUILD_1.A3 | bui | the Webwork north-star bars pass on the minimal list | CHAIN | - |  |
| WEBWORK_FIRST_SCRIPT_1.A3 | val | The one FAIL from the earlier 21P/1F retile run is classified as harness, site, mod or unmeasured. | SCENE | modcheck floor |  |
| WEEPINGSTONES_STOCK_JOB_LOOP_1.A3 | bui | The WeepingStones north-star rerun improves on the previous 55 PASS and 7 FAIL. | CHAIN | - |  |
| WEEPING_STONES_FIRST_SCRIPT_1.A1 | bui | one live northstar run of the WeepingStones validation script on the smallest mod list that loads it is record | DEFREAD | modcheck floor |  |
| WEEPING_STONES_FIRST_SCRIPT_1.A2 | bui | every non-passing step in that run is classified as harness, site, mod or unmeasured, with none hidden. | SCENE | modcheck floor |  |
| WILDSTEAM_EGG_BOUNTY_FIRST_SCRIPT_1.A2 | bui | one live northstar_driver run of WildsteamEggBounty on the smallest tier that loads it is recorded with its re | DEFREAD | modcheck floor |  |
| WILDSTEAM_EGG_BOUNTY_FIRST_SCRIPT_1.A3 | bui | every non-pass in the WildsteamEggBounty run is classified as harness, site, mod or unmeasured and none is hid | SCENE | modcheck floor |  |
| WYYYSCHOKK_FANG_PENDANT_1.A5 | val | The TrophyCraft north-star bars for the pendant pass on the minimal list. | CHAIN | - |  |

### 3.d GREEN-FULL (sitting 4, one cold load) (9 criteria)

| item.crit | st | criterion | fam | named instrument | + mods |
|---|---|---|---|---|---|
| ARMOURY_PROJECTILE_DAMAGE_TOOL_1.A2 | val | The ranged_ladder_landed north-star bar passes live on the full mod list. | CHAIN | jawa/get_defs; jawa/projectile_damage |  |
| CUT_FALLOUT_GENERATED_DATA_1.A1 | bui | A cold load of the full list shows the patch-failure count in Player.log dropped compared with before the cut. | LOG | - |  |
| FLOWWORKS_NORTHSTAR_GREEN_FULL_1.A1 | bui | After a cold load on the full mod list, modcheck status for FlowWorks reads GREEN, with GREEN-MIN passed first | DEFREAD | modcheck status FlowWorks |  |
| FLOWWORKS_NORTHSTAR_GREEN_FULL_1.A2 | bui | The mod list is restored to its prior state after the full-list run. | OBSERVE | modcheck status FlowWorks |  |
| FLOWWORKS_NORTHSTAR_TRIAL_1.A2 | bui | GREEN_FULL_1 runs on the full list and modcheck status FlowWorks prints GREEN re-derived, after the stale hash | CHAIN | modcheck run |  |
| FULL_LOAD_RESIDUE_TRIAGE_1.A1 | bui | A fresh full-list cold load harvest shows zero patch failures and a reduced config-error count versus the prio | LOG | [RimStarWars Patches] .../BMT_*/weaponTags failed |  |
| GRAFFITI_NORTHSTAR_TRIAL_1.A2 | bui | The Graffiti northstar passes on the full list. | CHAIN | - | rm.graffiti |
| PYRELANDS_GREEN_FULL_1.A1 | bui | A scratch full-list save with fresh mapgen passes census bars 1, 2 and 4. | OBSERVE | rimflow verify … --config full-latest |  |
| PYRELANDS_GREEN_FULL_1.A2 | bui | rimflow verify --config full-latest passes for Pyrelands. | OBSERVE | rimflow verify … --config full-latest |  |

### 3.e L3 (Opus evaluator over art captured in sitting 2) (42 criteria)

| item.crit | st | criterion | fam | named instrument | + mods |
|---|---|---|---|---|---|
| ABYSS_LIGHTFALL_BROOD_WRECK_1.A13 | val | joint session with the owner judges landscape scale, alien-beast feel and where the greed line sits | OBSERVE | - |  |
| ABYSS_SHEET_DONOR_PORT_1.A5 | val | art draws on a quicktest spawn, all facings | OBSERVE | - |  |
| BACTA_TANK_CORE_1.A6 | bui | The tank art showing the pawn suspended in the tank is evaluated and accepted alongside BACTA_TANK_ART_1. | OBSERVE | rimworld/load_game; rimworld/start_debug_game_ready; rimworld/go_to_main_menu | rsw.bacta |
| CAULDRON_ENRICHMENT_VISUALS_1.A2 | val | Opus evaluation finds the Cauldron enrichment visuals consistent with the ruled art colour law | OBSERVE | - |  |
| FLOWWORKS_BUILD_PROGRAM_1.A4 | bui | the excavation wall and pit art (EXCAVATION_WALL_ART_1) is evaluated and reads as shipping quality | OBSERVE | jawa/canal_dig; [MayRequireOdyssey] |  |
| FLOWWORKS_VISUAL_PRINCIPLES_1.A3 | val | An Opus evaluation of captured FlowWorks visuals judges them against the visual principles. | OBSERVE | - |  |
| FOOTPRINT_TRACK_GRID_1.A4 | val | The real print art is judged acceptable in style. | OBSERVE | jawa/mod_settings_field action=list |  |
| FORGE_KEELWORK_REMAINDER_1.A2 | bui | The keel brace and ring art is evaluated for style fit. | OBSERVE | - |  |
| FORGE_SPUNSTONE_SOURCES_1.A3 | val | Art for the door, hull and salvage cache is evaluated by Opus and fits the style, noting RUT_FoundrySalvageCac | OBSERVE | - |  |
| GELATINOUSSLIME_TITAN_CHUNK_BOMB_1.A4 | val | the chunk art is evaluated against the gelatinousslime_turn1_2026-10-02.csv brief | OBSERVE | jawa/get_defs |  |
| GRAVSHIP_WIRES_SURVIVE_LAUNCH_1.A3 | bui | joint live flight with the owner watching: two masts linked on the ship land with the span still drawn and bot | OBSERVE | - |  |
| GREENTIDE_THURROCK_HERD_BUILD_1.A6 | val | Thurrock art is judged acceptable in style. | OBSERVE | jawa/get_defs |  |
| LANTERNDEEPS_SHEET_ART_REDO_1.A3 | bui | eye-repaint creatures draw without eyes on a quicktest spawn | OBSERVE | - |  |
| LEANINGSCRUB_SWEETLINE_VISITORS_1.A2 | val | RM_SweetlineToken art exists and is judged acceptable in style. | OBSERVE | - |  |
| LIQUID_INDUSTRY_SETPIECES_1.A5 | val | Opus evaluation of the set-piece art once textures exist | OBSERVE | - |  |
| LONGSHADE_BEDAZZLE_CONTENT_1.A1 | bui | The shadespire art is redone as RM_Shadespire_c and evaluated. | OBSERVE | - |  |
| LONGSHADE_BEDAZZLE_CONTENT_1.A2 | bui | Gloomcast_Dessicated art is replaced (no longer a Horax copy) and evaluated. | OBSERVE | - |  |
| LONGSHADE_MIDDENS_SPENT_BUILD_1.A3 | bui | midden and clean-patch art installed from artpipe (RM_LongShadeMidden, RM_LongShadeCleanPatch) | OBSERVE | - |  |
| MESSYCONDUIT_REVIEW_ROUND1_1.A3 | bui | Wall-bracket art is produced per the look and evaluated. | OBSERVE | - |  |
| MOVING_DUNES_BUILD_1.A4 | bui | cache art PNG is delivered and evaluated | OBSERVE | - |  |
| MYCOID_COLOSSUS_LIVE_LOOK_1.A1 | bui | AA_MycoidColossus spawned live is read at all three facings by facing name, with no bare-path fallback masking | OBSERVE | - |  |
| NIGHTSIDEICE_SHEET_ART_REDO_1.A2 | bui | lemming, shock goat and tauntaun draw the new art on a quicktest spawn | OBSERVE | - |  |
| RUSTCATHEDRAL_SHEET_ART_REDO_1.A2 | bui | redo bolt draws on a quicktest spawn, all facings | OBSERVE | - |  |
| RUST_CATHEDRAL_MECHANICS_1.A4 | val | An Opus evaluation judges the living bolt dance look. | OBSERVE | jawa/spawn_pawn; jawa/spawn_batch; jawa/list_pawns | rut.rustcathedralroaches |
| SCARLANDS_MECHANICS_2.A6 | val | The placeholder Mech_Pikeman kind and prefab art are evaluated by Opus and replaced as owed. | OBSERVE | - |  |
| SEA_FISHABLES_ALIVE_IN_DEPTHS_1.A4 | val | The aluun three-view art is wired and judged acceptable. | OBSERVE | - |  |
| SHIELD_MODS_LEVERAGE_1.A4 | val | the shield art and placeholder textures are evaluated | OBSERVE | [0.05, 0.98] |  |
| STILLSAND_CAVE_AS_PLACE_1.A4 | val | An Opus evaluation judges the wall and glyph art, currently placeholders. | OBSERVE | - |  |
| STILLSAND_GEOPHONE_1.A3 | val | Opus evaluation of the geophone art once the registered art job lands | OBSERVE | - |  |
| STILLSAND_SAND_SIEVE_CHORE_1.A4 | val | RM_SandSieve art has landed from the artpipe job and is evaluated. | OBSERVE | - |  |
| STILLSAND_SKELETONS_REMAINDER_1.A5 | val | a buried skeleton reads sand-tinted to the eye (provisional 0.6/0.3 thresholds judged against real dune drift) | OBSERVE | [ThreadStatic] |  |
| STILLSAND_SUN_LANCE_1.A4 | val | An Opus evaluation judges the sun lance art. | OBSERVE | - |  |
| TREE_GRAPHICS_OWNERSHIP_1.A2 | bui | Opus evaluation of the 14-variant rotation scale and look | OBSERVE | jawa/spawn_thing; [0,0,0,0] | rut.ashkarrflora |
| UTINNI_DISCOVERY_ACHIEVEMENTS_1.A3 | bui | An Opus evaluation judges the Atlas plate and lamp art. | OBSERVE | - | rut.atlas |
| UTINNI_WORLDMAP_FLIGHT_ICON_1.A2 | val | The icon style is judged acceptable. | OBSERVE | - |  |
| WARSCAR_SHEET_DONOR_PORT_1.A3 | val | each draws its ruled art on a quicktest spawn | OBSERVE | - |  |
| WARSCAR_TOTCHAK_WAKES_1.A5 | val | Totchak creature art is produced and evaluated. | OBSERVE | - |  |
| WAR_LAB_CRATER_HOOK_1.A5 | bui | A world-map before and after screenshot is judged acceptable. | OBSERVE | jawa/world_tile_set; jawa/world_commit |  |
| WEBWORK_DEAD_GIANT_BUILD_1.A4 | bui | Opus evaluation of the Urraveth remains art | OBSERVE | - |  |
| WEBWORK_TRACTION_LANCE_BUILD_1.A4 | val | The traction lance art installs are produced and evaluated. | OBSERVE | - |  |
| WRECKED_DISTILLATION_MODULE_1.A3 | val | Opus evaluation of the replacement art for the placeholders | OBSERVE | - |  |
| WYYYSCHOKK_FANG_PENDANT_1.A6 | val | The fang and pendant art is evaluated by Opus. | OBSERVE | - |  |

### 3.f L4 (owner only; listed so he can be offered them in one batch) (54 criteria)

| item.crit | st | criterion | fam | named instrument | + mods |
|---|---|---|---|---|---|
| BIOME_ARRIVAL_LETTERS_ALL_1.H1 | val | the owner reviews and edits the ten placeholder texts | OBSERVE | - |  |
| BLOWER_ROOM_COOLER_1.H1 | bui | the owner judges strength 14 and draw 250 W in a sitting (PROVISIONAL until then) | OBSERVE | - |  |
| CAULDRON_ENRICHMENT_VISUALS_1.A3 | val | owner looks at the Cauldron enrichment visuals in game and accepts them | OBSERVE | - |  |
| CHILL_AIR_PUMP_1.H1 | val | the owner judges power cost and room capacity (PROVISIONAL until then) | OBSERVE | - |  |
| CHILL_DIVE_DENSITY_SAMPLER_1.A2 | bui | The owner tunes the provisional chillDiveAnimalCount on a live walk. | OBSERVE | - |  |
| CRACKEDLANDS_FIVE_BEATS_AUDIO_1.A2 | bui | In a joint session with the owner each of the five beats is audibly distinct and the tarruq calls on an ordina | OBSERVE | - |  |
| CUT_FALLOUT_GENERATED_DATA_1.A2 | bui | The owner or a keyboard session confirms the live Windows DeepStorage settings config file (c) is cleaned. | OBSERVE | - |  |
| FALLEN_WIRE_SHOCK_1.H1 | val | the owner judges the knockback, knock-out length and ignition chance in a sitting (PROVISIONAL until then) | OBSERVE | - |  |
| FEVERWOOD_BOUGH_SOIL_TERRAIN_1.A3 | val | owner confirms the provisional fertility 1.4 and the footprint | OBSERVE | - |  |
| FEVERWOOD_LIMB_LINGER_CAP_1.H1 | bui | the owner judges the linger time and cap in a sitting (PROVISIONAL until then) | OBSERVE | - |  |
| FLOWWORKS_BUILD_PROGRAM_1.A5 | bui | the owner has looked at the FlowWorks result in game and accepts it | OBSERVE | jawa/canal_dig; [MayRequireOdyssey] |  |
| FLOWWORKS_CONTAINER_MATERIALS_1.A3 | val | owner judges the stuff-tinted container art (greyscale renders queued) | OBSERVE | rimworld/spawn_thing |  |
| FLOWWORKS_LADDER_RAISE_LOWER_1.A2 | bui | owner confirms the raised and lowered ladder art (raised variant owed) | OBSERVE | - |  |
| FLOWWORKS_NORTHSTAR_TRIAL_1.A3 | bui | SHIP_1 shipped gaps are each closed or parked by the owner's word. | OBSERVE | modcheck run |  |
| FLOWWORKS_VISUAL_PRINCIPLES_1.A4 | val | The owner judges the FlowWorks look on a live map. | OBSERVE | - |  |
| FORCE_DISTURBANCE_REFLAVOR_1.A3 | bui | the owner has seen and approved the replacement wording | OBSERVE | - | rsw.patches |
| FORGE_DHOKKUR_WAYS_1.A3 | val | owner rules the two open questions (shove behaviour, whether tracks fade) and judges bespoke trail and gutter  | OBSERVE | - |  |
| FORGE_KEELWORK_REMAINDER_1.A3 | bui | The owner confirms or vetoes the ruling that the payload gives no SubstructureSupport. | DEFREAD | - |  |
| FORGE_WHITE_PLUME_FRONTS_1.A7 | val | The owner reviews and accepts or overrides the four builder-chosen answers. | OBSERVE | - |  |
| GLOW_TANK_LIQUID_FEED_1.H1 | val | the owner judges the drink rate (PROVISIONAL until then) | OBSERVE | - |  |
| GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1.A2 | bui | The owner reviews the result via modcheck review. | CHAIN | modcheck status; modcheck review Graffiti --owner-said … | rm.graffiti |
| GRAFFITI_NORTHSTAR_TRIAL_1.A4 | bui | The owner reviews the sheet and gives his word on the hashed-prose correction. | OBSERVE | - | rm.graffiti |
| GRAVSHIP_ACOUSTIC_SCANNER_1.A3 | val | the owner judges the per-biome payload feel across the 62 biome payloads | DEFREAD | - |  |
| GREENTIDE_HUMMING_GROVE_1.A2 | bui | The owner hears the grove hum change as he walks through it, with no obtrusive pop when layers change, in a sa | OBSERVE | - |  |
| JAWA_SWIM_HOOD_KEEP_1.A3 | bui | owner decides whether the fallback hood tint is acceptable | OBSERVE | - |  |
| KINETIC_BLAST_WEAPONS_1.EK.feel | bui | owner watches a blast and a shield belt: reads right | OBSERVE | - |  |
| LEANINGSCRUB_SWEETLINE_VISITORS_1.A3 | val | The owner vetoes or accepts the open design calls. | OBSERVE | - |  |
| LONGSHADE_BEDAZZLE_CONTENT_1.A4 | bui | The owner looks at the LongShade content and re-tints as desired. | OBSERVE | - |  |
| LONGSHADE_ENRICHMENT_QUICKTEST_1.A5 | bui | The owner listens to the heat soundscape (placeholder audio) and approves. | OBSERVE | - |  |
| MESSYCONDUIT_CABLE_PILE_LOOK_1.A4 | bui | owner looks at a junction pile, a Modern strip pile and two crossing hoses on a review map and rules the look  | OBSERVE | - |  |
| MESSYCONDUIT_REVIEW_ROUND1_1.A4 | bui | The owner re-reviews round 2. | OBSERVE | - |  |
| MYCOID_COLOSSUS_LIVE_LOOK_1.A3 | bui | The owner looks at the colossus in game. | OBSERVE | - |  |
| PIT_TEMPERATURE_SOFTENING_1.A6 | val | The owner judges the provisional mood number reads as cruel at the right strength. | OBSERVE | - |  |
| RAKATAN_ARCHOTECH_MACHINES_1.A3 | bui | owner reviews the Rakatan design (component source, ruin wrecks, turrets and art are not built yet) | OBSERVE | - |  |
| RIVER_STEAM_ANIMATION_1.A3 | bui | The owner judges the steam shape and motion against the reference photo. | OBSERVE | jawa/map_info; jawa/world_links_set; jawa/get_terrain_batch | rsw.cuisine |
| RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1.A7 | val | Worn art installed (south failed in artpipe) and Unbitted/Restored edits swap the body graphic per comp state | OBSERVE | jawa/get_defs |  |
| RUST_CATHEDRAL_MECHANICS_1.A5 | val | The owner looks at the bolt dance. | OBSERVE | jawa/spawn_pawn; jawa/spawn_batch; jawa/list_pawns | rut.rustcathedralroaches |
| SALVAGE_WRECKAGE_EVERYWHERE_1.A4 | bui | owner reviews wreck art in game (wave-2 renders queued, not all installed) | OBSERVE | - |  |
| SCALD_WATER_AGITATION_FLECKS_1.A3 | val | The owner looks at the wreck shadows and the agitation and approves them. | OBSERVE | - |  |
| SHIPVERMIN_FREE_TIER_BEASTS_1.A4 | bui | owner approves the free-tier beast list and the art | OBSERVE | - | rsw.swbestiary |
| SOLAR_HEAT_EXPOSURE_1.A3 | bui | The owner watches and tunes the rest-dash behaviour. | OBSERVE | - |  |
| STILLSAND_CAVE_AS_PLACE_1.A5 | val | The owner hears the cave drip and approves. | OBSERVE | - |  |
| STILLSAND_PRECIOUS_CAVES_LIVE_1.A6 | val | The owner looks at the caves in game. | OBSERVE | [Stillsand] precious cave:; [Stillsand] precious cave roll: |  |
| TREE_GRAPHICS_OWNERSHIP_1.A3 | bui | owner looks at the sweetline tree variants in game | OBSERVE | jawa/spawn_thing; [0,0,0,0] | rut.ashkarrflora |
| UTINNI_DISCOVERY_ACHIEVEMENTS_1.A4 | bui | The owner reviews the Atlas tab, the riddles and the lore leaves. | OBSERVE | - | rut.atlas |
| UTINNI_WORLDMAP_FLIGHT_ICON_1.A3 | val | The owner looks at the globe in flight and approves the icon. | OBSERVE | - |  |
| VAULT_DUNGEON_BUILD_1.A3 | bui | the owner hand-finishes the six sites and world_commit lands them | OBSERVE | jawa/kcsg_place; rimworld/get_cell_info | rm.injections, rut.injections |
| VAULT_DUNGEON_BUILD_1.A4 | bui | the owner reads the V6 wake, loot and leave text and letters and accepts them as plainly brutal with the ship- | OBSERVE | jawa/kcsg_place; rimworld/get_cell_info | rm.injections, rut.injections |
| VAULT_THAW_QUEST_FAMILY_1.A6 | val | The owner reviews the design row and the letters. | OBSERVE | [symbol] | rm.injections, rut.injections |
| WARSCAR_CHOTRIX_SIGNS_1.A3 | val | owner judges the chotrix print art (currently a placeholder copy; real art owed) | OBSERVE | - |  |
| WARSCAR_PILGRIM_JOURNAL_ANTIQUITY_1.A3 | bui | owner answers the three open questions on the journal | OBSERVE | - |  |
| WARSCAR_RAINBOW_POOLS_1.A5 | val | The owner looks at the pool tint and icons. | OBSERVE | - |  |
| WAR_LAB_CRATER_HOOK_1.A6 | bui | The owner looks at the world-map before and after. | OBSERVE | jawa/world_tile_set; jawa/world_commit |  |
| WETBULB_FOLD_INTO_HEAT_1.H1 | bui | the owner judges the 12 C offset and the gear values in a sitting (PROVISIONAL until then) | OBSERVE | - |  |

## 4. Tiers and mod lists

All `modset_builder.py` tiers set `dlc: True`; `tier_guard` refuses a resolved list missing any of the five DLCs, and resolving the proposed list below
(read-only, in-process, nothing written) returned 0 refusals, 0 missing, all five `ludeon.rimworld.*` present.

**Proposed new tier `acc_20261009`** (does not exist yet; add to `TIERS` in `src/RimMandrake/Utils/modset_builder.py` before the sitting, then `--tier acc_20261009 --list` to confirm, `--apply` only when the bridge is yours and the game is down).
It is the union of `acc_l1x`, `acc_harness`, `acc_biomes`, `live_20261008b`, `kineticarms`, `explosiveknockback`, `flowworks` plus every converted mod that has its own packageId and is installed. Resolved closure: 43 packageIds.
```
"want": ["brrainz.rimbridgeserver", "mandrake.rm.acousticscanner", "mandrake.rm.aftermath", "mandrake.rm.biomes", "mandrake.rm.explosiveknockback", "mandrake.rm.flowworks", "mandrake.rm.gimmesomeslack", "mandrake.rm.gravshiplanding", "mandrake.rm.hugethings", "mandrake.rm.inhabited", "mandrake.rm.keelhoist", "mandrake.rm.kineticarms", "mandrake.rm.luminouspigment", "mandrake.rm.ninefold", "mandrake.rm.planetpresetprime", "mandrake.rm.proximityhatch", "mandrake.rm.raidredesigner", "mandrake.rm.shipvermin", "mandrake.rm.solarmirrors", "mandrake.rm.visibility", "mandrake.rm.watchers", "mandrake.rm.wreckedmachines", "mandrake.rsw.droidworks", "mandrake.rsw.trophycraft", "mandrake.rut.eggreckoning", "mandrake.rut.falllinearrivals", "mandrake.rut.patches", "mandrake.rut.shipshields", "mandrake.rut.unfinishedline"]
```
Known wart: the builder prints `forcing mandrake.rm.biomes into place with unmet ordering constraint(s) on ['mandrake.rut.patches']` for this list, the same as the existing `live_20261008b` and `acc_*` tiers use; not new, but record it beside the sitting.
`mandrake.rm.explosivegrowth` is left out on purpose: with it the same warning also names it. Run it in its own `explosivegrowth` / `explosivegrowth_solo` tier if its criteria are wanted.

Existing tiers to reuse unchanged: `acc_green_min`, `acc_green_min2` (GREEN-MIN batches; run `acc_green_min2` second), `kineticarms`/`explosiveknockback` (KINETIC_BLAST_WEAPONS_1 scenes), `weepingstones_solo`, `pyrelands`, `graffiti_solo`, `leaningscrub`, `shrublandfauna`, `xenotypes` for item families that name them.
The "+ mods" column in section 3 shows mods a criterion's own text names that are not in the proposed list; for each, either add to the sitting-1 list (preferred, one more load is dearer than ~5 more mods) or move that criterion to the tier owning it.
Items whose subject mod has no packageId of its own ship inside `mandrake.rm.biomes` or `mandrake.rut.patches`, both in the list.
GREEN-FULL uses the owner's live full list: do not rebuild it with a tier; restore the prior ModsConfig after (criterion FLOWWORKS_NORTHSTAR_GREEN_FULL_1.A2 asks for it).

## 5. What UNMEASURED looks like

- The bridge tool returns `success: false`, times out, or the reply has no `foundCount`: UNMEASURED, never "absent". Zero hits from a Player.log grep without the section 2 sanity probe finding its known lines: UNMEASURED.
- A census of the "queue is empty" kind that came from `ls | wc -l`: prove the path first. A count that is conveniently or alarmingly round is a query bug until proven otherwise.
- `game_loaded` true but the map never ticks, a stale modal, or the load aborted midway (zombie state): UNMEASURED; check the first exception in Player.log.
- Log taken from the wrong session: confirm the log's start time is after the launch and the Mod list in its header matches `acc_20261009` (parse ModsConfig; a stale list is a false root cause).
- A DLL deployed before tonight's rebuild: compare the deployed DLL's `.srchash` with the repo copy for every converted mod before launch (`deploy_custom_mods.py --mod <name>` dry run lists `-`/diff lines; do not `--apply` without the bridge).
- A screenshot without a state read, or any flyer judged by sight: not a measurement. L3/L4 rows are never closed by this plan.
- `rimflow verify` needs `--config` (min-13 for sitting 1/2/3, full-... for 4); evidence path must be a committed file or one under `Transient/`.
- A criterion text that names mods or tools the sitting did not load is UNMEASURED for that sitting, not failed; rows with a non-blank "+ mods" cell are the first suspects.
