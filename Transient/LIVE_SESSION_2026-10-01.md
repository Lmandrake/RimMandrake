# FOUNDRY live session 2026-10-01 (owner AFK, authorized "Yes, tonight" by card)

Deployed commit: `cc4bc992243` (clean worktree `D:\Luke\dev\RimMandrake-wt-livedeploy`).
Before launch, the unified `RimMandrake.Biomes` compose was 148 files behind that commit
(Stillsand, CreatureBehaviors, TerminalBiomes, Contagion included); deployed with
`deploy_custom_mods.py --compose biomes --apply`, re-plan "Everything in sync".
Not deployed / not in `cc4bc992243`: `136c287f5` (event creatures), `6236731d6` (precious caves).
Game copy of SWBestiary carries 4 files not in the repo (`RSW_SandSwimmer_Items.xml`, 3 `RM_Qorrax` textures), left in place.

## Decision strings (written before launch)

| check | string / read | pass | fail |
|---|---|---|---|
| load alive | `Bridge token:` in Player.log | present | `Recovered from incompatible or corrupted mods`, `Caught exception while loading play data`, `Resetting mods config` |
| first error | first `Exception` line after `Initializing new game with mods` / during load | none of ours | names RimMandrake.Stillsand / CreatureBehaviors / TerminalBiomes / Contagion |
| defs smoke | `jawa/get_defs` ThingDef/RM_ChillCryoponicsVat, RM_ChillFloorBed, RM_PillarArm, RM_PillarArmItem, RM_Lash, RM_LashItem; HediffDef/RM_PillarArm, RM_Lash; RecipeDef/RM_InstallPillarArm, RM_InstallLash | foundCount = asked, success true | any notFound; `Config error in RM_Chill*/RM_PillarArm*/RM_Lash*`; `Could not resolve cross-reference` naming them |
| sand-swim types | log `Could not find type named RM_CompSandSwim` / `RM_SandSwimExtension` / `RM_MapComponent_Zuurrik` | absent | present |
| Stillsand map | `jawa/map_info.mapBiome` after tile set + regen | `RM_Stillsand` | anything else |
| submerged | `jawa/pawn_health` on RM_Vekka on Sand/SoftSand/RM_DeepSand | hediff `RM_SandSubmerged` present | absent |
| surfaced | same vekka moved to rock/floor, or damaged | `RM_SandSubmerged` gone | still present |
| mech immunity | no `RM_SandSubmerged` vekka attack on mechanoid | mech HP unchanged | mech damaged by submerged swimmer |
| zuurrik | 8+ `Filth_Blood` cells in r8 on sand, step ~600 ticks | `RM_Zuurrik` pawns appear | none |
| sun | no state-read surface for `RM_MapComponent_ShadeGrid` fields (no bridge tool) | — | UNMEASURABLE by state read |

## Results

(filled progressively)

### Load (cold, full list, 611 active mods per ModsConfig) — 01:03 launch via Steam, `Bridge token:` at ~01:26
- No load abort. Our load-time defects (log copy: `Transient\livesession_20261001\Player.load.log`, paired list `ours_errors.txt`):
  - `RM_Stillsand_FilloutFlora.xml`: `TreeCategory "Standard"` is not a valid value -> **`RM_KneelOllim` discarded** (get_defs notFound; `RM_Stillsand` BiomePlantRecord cross-ref fails).
  - `RM_Loomma` startingHediffs `<severityRange>` is not a field of StartingHediff -> sunstruck start severity ignored.
  - Config errors: `RM_Loomma`, `RM_Vaalok` trainability null; `RM_Zuurrik`, `RM_Liikka`, `RM_Veessa` meat from Megascarab (which uses Megaspider meat).
  - Contagion: `No textures found at path Things/Plant/RM_Lashgrass/RM_Lashgrass` (plant, not the Lash limb).
- Defs smoke (`jawa/get_defs`, success true, foundCount 15/16): RM_ChillCryoponicsVat, RM_ChillFloorBed, RM_PillarArmItem, RM_LashItem, HediffDef RM_PillarArm/RM_Lash, RecipeDef RM_InstallPillarArm/RM_InstallLash, RM_Vekka, RM_Zuurrik, RM_SandSubmerged, RM_SandSwimmer, BiomeDef RM_Stillsand, RM_Loomma, RM_Soorrak all found; no config error names a Chill/PillarArm/Lash def. **Smoke PROVEN.**

### Quicktest map
- `start_debug_game_ready` worked on the full list (01:27 -> Playing 01:29). Tile 97517, lat 37.87. `world_tile_set biome=RM_Stillsand temperature=48` + Regenerate Current Map -> `mapBiome RM_Stillsand`, outdoor 51.5 C. 3 colonists planted. A hostile insect group spawned at the map centre (Megaspider/Megascarab/Spelopede/Locust, faction Hive) and was removed with `Destroy hostile pawns`. Wild RM_Vekka x2 spawned naturally.

### Sand-swim (STILLSAND_SAND_SWIM_KIT_1 criteria, state reads via `jawa/pawn_get` hediffs) — `st_sandswim.json`, `st2.json`
- Submerged on sand: natural and spawned vekkas on Sand carry `RM_SandSubmerged`; a vekka on Gravel does not. PROVEN.
- Surfaces when struck: `jawa/damage` Blunt 1 -> `RM_SandSubmerged` gone 5 ticks later; back under after 1500 ticks. PROVEN.
- Mech immunity: submerged vekka given `AttackMelee` on a Mech_Militor six times over 600 ticks stayed submerged, mech uninjured; controls on the same sand (vekka -> hare, vekka -> player chicken) surfaced and killed. PROVEN (forced job; manhunter vekkas ignore mechs and go for colonists, so the manhunter route says nothing).
- Take signs: player chicken killed on sand -> letter `Taken under: Pilot` (tick 7088). PROVEN for the letter. **FAILED for the funnel:** no `RM_Filth_DisturbedSand` anywhere (list_things: 0 of 14,387 things). Masks measured with get_defs; that this is why the placement is refused is inferred from vanilla FilthMaker: Sand, SoftSand and RM_DeepSand have `filthAcceptanceMask = Unnatural`, and `RM_Filth_DisturbedSand` / `RM_Filth_DragMark` use `placementMask Terrain`, so `FilthMaker.TryMakeFilth` refuses on every swim terrain. The corpse also stays on the surface though the letter says the body was pulled down.
- Wild kill (hare): no message check possible by state read; no funnel (same cause).

### Stillsand content (STILLSAND_CONTENT_LIVE_PROOF_1) — `st3.json`, `zt.out`
- Atlas: 20 of 21 `RM_` Stillsand kinds spawn. **`RM_Oorrik` throws a NullReferenceException in pawn generation** (OORRIK_PAWNGEN_NRE_1). `jawa/texture_audit` lists 137 dead texPaths, none of them a Stillsand def. Magenta was not checked by eye.
- Zuurrik: woke on blood on sand twice (swarm of 3 each time), and stripped blood at its site (42 to 36 cells in 2,400 ticks; a 12-cell control pad stayed at 12). Toggle off: no wake over 3 polls. Toggle on: woke within 600 ticks. The unwounded-pawn rule is inconclusive (3 unhurt hares beside the swarm vanished with no corpse). Re-bury was not observed (the swarm always had blood near it). The wake message cannot be state-read.
- Loomma: `RM_LoommaSunstruck` rises in the open (0.01 to 0.14 in 600 ticks); loommas walk into roofed shade, and there it decays to 0.
- Soorrak: flight state report only: canEverFly true, MaxFlightTime 30, flightStartChanceOnJobStart 0.3. No flight was attempted. **It logged 59 NREs in `Pawn_FlightTracker.Notify_JobStarted`** (SOORRAK_FLIGHT_JOBSTART_NRE_1).
- Not live work: the placeholder art swap and the hourbloom incident decision.

### Sun (STILLSAND_SUN_LIVE_VERIFY_1)
- No bridge surface reads `RM_MapComponent_ShadeGrid` or `RM_MapComponent_PinnedSun` (SHADEGRID_BRIDGE_READER_1).
- On this standard-planet quicktest, a SolarGenerator gave 1700 W from tick 20,400 to 24,436, then 1672, 1563 and 1446 W by tick 26,872, so sky glow was not constant. Whether the map counts as a pinned map is unknown.

### Other session-time errors (`livesession_20261001\Player.session.log`)
- `GenStep_RimplacePlan.Generate` NRE during the Stillsand regen (RIMPLACE_GENSTEP_NRE_1).

## Verdicts
| item | verdict |
|---|---|
| Chill vat/bed + Contagion Pillar Arm/Lash defs smoke | PROVEN (all resolved; no config error names them) |
| STILLSAND_SAND_SWIM_KIT_1 / _REMAINDER_1 live criteria | PARTIAL: submerge, surface, mech immunity and take letter PROVEN; funnel FAILED (SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1); thumper and fishing NOT BUILT |
| STILLSAND_CONTENT_LIVE_PROOF_1 | PARTIAL: zuurrik wake/strip/toggle and loomma clock PROVEN; Oorrik NRE, soorrak NRE, KneelOllim discarded; art swap not live work |
| STILLSAND_SUN_LIVE_VERIFY_1 | NOT PROVABLE yet (no reader tool; solar not constant on this quicktest) |
| STILLSAND_EVENT_CREATURES_LIVE_1 | SKIPPED: `136c287f5` not in deployed `cc4bc992243` |
| STILLSAND_PRECIOUS_CAVES_LIVE_1 | SKIPPED: `6236731d6` not in deployed `cc4bc992243` |

Filed: SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1, STILLSAND_LOAD_DEF_ERRORS_1, OORRIK_PAWNGEN_NRE_1, SHADEGRID_BRIDGE_READER_1, SOORRAK_FLIGHT_JOBSTART_NRE_1, RIMPLACE_GENSTEP_NRE_1.
Game closed at the end (it was down at the start). Bridge released.
