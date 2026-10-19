## spec
Plan P5 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`).
Design: `design/RimMandrake/flowworks_elevation_feasibility_2026-10-17.md` §1.3 and §4 T1. Owner R5 (card 2026-10-17):
default max colonist dig 8 m, setting 2 to 20 m; 0.5 m step stays; lakes keep their own floors.
ESTIMATE 3 to 5 agent-days. Starts after the level-surface solver (`WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`) lands.
**Must not ship before `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` passes.** Land together with
`PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` (fall damage divides by the dig cap today, so a cap raise alone softens falls).

## cap sites (re-grepped at `9196261f3`, `src/RimMandrake/FlowWorks/Source/`)
| site | today | change |
|---|---|---|
| `RM_ExcavationDepth.cs:38` `Superdeep = 4`, `:40` `MaxDepth = Superdeep` | trap depth = dig cap | split `PitDepth` (4) and `MaxDigDepth` (setting, default 16, range 4..40) |
| `RM_FlowKernel.cs:130` `Superdeep = 4`; `:686` `b < 5`; `:719` `tb < 5` | depth 0..4 | gone with the solver; else derive from the deepest floor |
| `RM_PitDrawMath.cs:28` `MaxDepth = 4` | absolute sink, capped 2 m | sink by drop below the near lip (`ClampSinkToLip` exists) |
| `RM_PitTrapMath.cs:20` `Superdeep = 4`; `:503` `FallDropScale(drop, maxDepth = Superdeep)`; caller `Superdeep/RM_SuperdeepTrap.cs:381` passes `MaxDepth` | falls scale by drop ÷ cap | by metres fallen (P7) |
| `Superdeep/RM_PocketGrid.cs:129` `new Labels[MaxDepth]` (and `MaxDepth` at `:57`); `Superdeep/RM_CliffMask.cs` band array `[MaxDepth]`; `RM_PocketGridMath.cs` band lookup | bands 1..MaxDepth-1; "K ≥ MaxDepth climbs everything" | size by the largest climb limit (4 + climber + leaper = 6); drop the shortcut |
| `WorkGiver_DigCanal.cs:52`, `Designator_DigCanal.cs:79`, `JobDriver_DigCanal.cs:30`, `JobDriver_FillInCanal.cs:32`, `RM_MapComponent_Excavation.cs:808, :1348, :1570` via `RM_ExcavationDepth.DepthOfDryTerrain` (`:97`) | depth read from the TERRAIN def (4 looks) | read the grid. **The real bug class:** past 2 m every cell is Superdeep terrain, so it would refuse to dig deeper and price work wrong |
| `RM_WallFaceMath.cs:230` `depth >= 4 ? 0.34f : …` and the face arrays | a 4 m and a 2 m cliff draw alike | arrays to ~8 notches, saturating (his look first) |
| `Superdeep/RM_Spikes.cs:50` `depth >= 4` | absolute | P7: sheer drop ≥ 2 m to a neighbour |
| `Superdeep/RM_PitRooms.cs:65, :67` `IsSuperdeepRaw` (`RM_MapComponent_Excavation.cs:241`) | absolute 2 m | P7: person-band pocket |
| rain loop `levels < MaxDepth` (`RM_MapComponent_Excavation.cs`, ~:2200 at `664f8dd1a`) | 4 notches | the cell's own depth |
| `RM_ExcavationDepth.WorkToDeepen` | 3,200 × notch | kept (`DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT`) |
| designator text "shallow, mid, deep, then SUPERDEEP" (`Designator_DigCanal.cs`), settings and Keyed strings | four names | metres; add "dig to N m" |

## verify
- L1 selftests: a 4/7/7/4 square digs (16 designations with dig-to-N), holds by band, renders distinct ledge and core
  walls, and reloads identically; lowering the cap never shallows a dug cell.
- L1: Mod Setting "max colonist dig depth" defaults to 8 m, settable 2 to 20 m in 0.5 m steps; `Superdeep` (4) is a
  separate constant from `MaxDigDepth`; no dig code reads the terrain for depth.
- L1: the filled 4/7/7/4 square is one body with one surface (the P3 diagnostic under 1 cm).
- L2 (P10 walk): a colonist digs one square to 8 m by "dig to N m" in game; the readout shows the hole depth.
- Ships only after `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` passes and together with `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE`.

## criteria
- A1 L0: offline built cb8194587 — SelfTest DeepDig_* (4/7/7/4 square 16 orders/152 cuts, 152,000 L, one surface; cap 2/8/20; never shallows; no terrain depth reads; bands K1..6). Report `Transient/fw_scenes/p5_build_log.md`.
- A2 L2: P10 walk — a colonist digs one square to 8 m by "Dig to depth" in game; the readout shows the hole depth; the 4/7/7/4 square staged in the P10 savegame.
- A3 L2: a save with digs past 2 m reloads identically (depth grid, dig-to orders, pocket bands).
- A4 L4: deeper wall faces, pawn sink by drop and floor tint past 2 m: P9 art review (his look first), not built here.
