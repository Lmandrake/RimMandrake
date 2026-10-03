# FlowWorks north-star interrogation (2026-10-02)

I wrote this as a helper to the FOUNDRY seat. It is offline only: the game was down, I did not
take the bridge, and I edited no code, walk or `validation.py`.

**Subject:**
- `src/RimMandrake/FlowWorks/validation.py`: 1,103 lines, 86 components, 33 of which carry `shows=`.
- `design/validation_walks/RimMandrake/FlowWorks.md`: 38 must-show and 5 cannot-show bars, `state: VALIDATED`.

I checked both against the C# in `Source/`, the defs in `Defs/`, the JawaBench tools, and the one
recorded live run.

**Counts come from a script, not a tally.** The verdict table lives in
`scratchpad/verdicts.py`, and `scratchpad/count.py` parses the walk and `validation.py` with
`ast`. Sanity probe: the script must find the known bar `pit_reads_as_hole` and must not find
the fake `zz_fake`. It reports 38 + 5 bars, 86 components and 0 uncovered ids. That agrees with
`flowworks_shows_wiring_2026-10-01.md`'s 38/38.

## 1. Sources read

**Library:**
- `debug_process.md`
- `northstar_time_ledger_2026-10-01.md`
- `northstar_pilot_scoping_2026-10-02.md`
- `flowworks_shows_wiring_2026-10-01.md`
- `Transient/northstar_live_pass2_2026-10-01.md`
- `northstar_helpers_plan.md`: the bland-map sections §4 and §10.7, "checkpoint beats sanitising"
- `modcheck/{saved_base,bland_world,clockgate}.py`: their docstrings
- `FlowWorks/northstar/{site_spec,prep_site,preflight_flowworks,fakegame}.py`: their docstrings and constants

**Code:**
- `Source/RM_MapComponent_Excavation.cs`, read in full over its engine region (l.36-455 and l.730-1222)
- `RimMandrakeFlowWorksMod.cs`, the settings
- `RM_LiquidStock.cs`, the classification lines
- `Superdeep/{Building_SuperdeepPit,RM_SuperdeepCapture,RM_LadderUtility}.cs`
- `LiquidTypes/LiquidIgnition.cs`
- `Flood_FlowWorks.cs`, its expiry and temp-terrain lines
- `bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorks{,Northstar}Tools.cs`

**Defs:** all 49 XML files, parsed. They hold 191 defNames, and the parser found `RM_Channel_Empty`, which it must.

**The one recorded live run:** `D:\Luke\dev\wt_live2\Transient\modcheck\live_queue\situational_rerun\FlowWorks_summary.json`.
- It is situational_rerun `--bland-world` #2, 2026-10-01 ~21:41. It ran 85 components: **PASS 28, FAIL 21, UNMEASURED 36**.
- The time ledger measures 112,921 ticks and 21.4 min for it, at 33 ticks/s, with 799 report polls.
- This run is the strongest evidence below, because it shows each predicate meeting the real game.

The two items below come from a helper agent's audit of the 27 toggle chains, recorded in §3b:
- the toggle table
- the bridge-tool parameter check

## 2. What FlowWorks actually is (code + defs)

**The engine**
- One `RM_MapComponent_Excavation` per map holds a byte grid `D` (0..4) and `F` (0..D).
- It pulses every `PulseIntervalTicks`. That is the `pulseIntervalTicks` slider, default 250 and clamped to at least 60.
- Each recipient cell with F<D takes up to `FlowPerPulse` units from a donor. That is the `flowPerPulse` slider, default 1 and clamped to 1..4.
- The donor is the neighbour with the best score. A natural water cell scores 1000. Otherwise the score is `F*10+D`, and a non-brimming donor may give only to a recipient deeper than itself (GRAVITY). A brimming donor may give to any cell with room (OVERFLOW).
- Recipients are sorted deepest-first, with a **cell-index tiebreak**.
- **There is no viscosity anywhere in the engine.** `FlowPerPulse` is global. `FluidDef.ticksPerTile` is read only by the legacy `Flood_FlowWorks`. `RM_LiquidProperties.viscosityClass` is documentation (`RimMandrakeFlowWorks_DefOf.cs:32`: "not yet wired").

**D only ever increases** (`Deepen`, "LAW 1"). Two things lower it:
- `FillIn`, a colonist job behind the `RM_FillInCanal` designation;
- natural recession.

There is **no bridge tool that resets a cell's D or F to 0 on undug ground**. Repainting Soil
(`set_terrain_batch`) leaves the grid untouched.

**One `ActiveFluid` per map.**
- `jawa/flowworks_set_active_fluid` refuses once any body is classified or any cell holds fill.
- So tar, slime and water each need their own map or their own load of a save.

**Sources and sinks**
- **A source** is any natural `IsWater` base terrain, WaterShallow included. `DepthAt` reads it through as D=4, F=4.
- **Limitless** requires *edge contact AND ≥ `minLimitlessBodyCells` (50)* (`RM_LiquidStock.cs:152`). Classification is sticky.
- **A limited body's budget** is `canalCellsPerSourceCell` = 5 levels per source cell (`FlowWorks_Fluids.xml`). So a 5×5 pond holds 125 fill-levels.
- **A sink** is *any excavated cell within 10 cells of the edge* (`IsSinkCell`, `GenGrid.NoBuildEdgeWidth`). It drains `FlowPerPulse` every pulse.

**🔴 A channel running east or north of its source never fills. It oscillates forever.**
This is a MOD defect candidate. The live log measures it, and an independent port of the
pulse reproduces it exactly. (Item suggestion: `FLOWWORKS_CHANNEL_OSCILLATION_1`.)

*The mechanism:*
- The recipient list is snapshotted at the start of the pulse and sorted deepest-first, with ties broken by cell index.
- `PickDonor`'s OVERFLOW clause lets a brimming cell give to an *equal-depth* neighbour.
- In a channel whose cell index rises away from the source (east or north), the mouth fills and then hands its unit on within the same pulse.
- Once the mouth starts a pulse full, it is no longer a recipient, so it never draws from the source again.
- The fill units already in the channel then shuttle between neighbours with a period of 2, and the channel never reaches full.
- West- and south-running channels fill normally.

*The evidence:*
- A pure-Python port of `DoPulse`/`PickDonor`/`CompareDeepestFirst` (this pass) predicts the following for a channel off a limitless source:
  - an east-running 3-cell D=1 channel: `[1,0,1]↔[1,1,0]`;
  - a 6-cell one: `[1,1,1,0,0,1]↔[1,1,0,1,1,0]`;
  - north-running channels: identical;
  - west- and south-running channels fill. The pulse count is length-dependent: 3 cells by pulse 5, 4 by pulse 7, 6 by pulse 11 (an earlier "≤ 8" here was wrong; the GPT review caught it).
- The port is a scratch file this pass and is not committed. The draft's `PulseOracle` class is the committed form of the same algorithm (§3 O5 of the plan).
- **The live 2026-10-01 log matches.** `pond_drawn_down` (plot D: a 5×5 pond and a 12-cell D=3 channel running east) alternated over its last 8 recorded pulses (ticks 538,130→539,880) between exactly `[3,3,2,3,3,2,2,3,3,2,2,3]` and `[3,3,3,2,2,3,3,2,2,3,3,2]`.
- The port, given the same geometry and a 125-level stock, produces **both of those vectors exactly**. The pond stock stalls at 94, so 31 of 36 levels are delivered.
- `confinement_on` (a 6-cell east channel) also oscillated live. Its exact states are contaminated by plot reuse.

*The same clause has a second symptom (port only, UNMEASURED live).* A **partly filled**
equal-depth run never comes to rest, in any direction:
- A 1-cell limited pond (5 levels) feeding an 8-cell south-running D=1 channel delivers exactly 5 levels.
- The vector then keeps alternating (period 2) once the stock is spent. Brimming cells keep handing a unit to an empty neighbour.
- On screen, a partly filled canal would **flicker every pulse**. That bears on `canal_partial_fill_distinct` and `canal_fill_spreads_along_itself`.
- The sum is conserved, so the conservation ledger is silent about it.

*What this means for the script:*
- The two live `NOT_SETTLED` FAILs were **the mod's behaviour**, not budget arithmetic.
- The old suite read them as a harness budget problem.
- This finding also validates the port as a v2 oracle.

**Throughput**
- A single-mouth channel gains at most 1 level per pulse from its source, at FlowPerPulse=1.
- So a 12-cell channel at D=3 needs at least 36 pulses (9,000 ticks) to fill, and the `_settle` 3-pulse stability rule adds more.

**Capture**
- `Building_SuperdeepPit` is an invisible holder (`drawerType None`) that `Deepen` spawns on every D=4 cell.
- Its `Tick` captures any pawn standing on the cell whose faction qualifies. That covers a pawn that is **spawned directly on it**, so no pathing is needed.
- The ladder only counts **in the pit cell itself** (`RM_LadderUtility.HasLadder(map, Position)`, plus `PlaceWorker_LadderOnExcavation`).
- The ladder has **no raised/lowered state**. It is present or absent, and its art is the vanilla `TrapSpikeArmed` placeholder.

**Art**
- All four channel depths use `Terrain/Surfaces/Gravel`.
- Fill tiers have their own defs (`RM_Fill_Water_Trace/Half/Brim/Superdeep`, parented to WaterShallow).
- No code offsets a pawn's draw position by depth. A grep for DrawPos/DrawOffset/PawnRenderer in `Source/` hits only the legacy building pit and terrain-mimic cover.

**Cheap invariants the engine already announces.** The script checks none of them today:
- The `Log.Warning "conservation ledger does not balance"` (DevMode, `RM_MapComponent_Excavation.cs:938`).
- `overflowDestroyedTotal`.
- `jawa/flowworks_engine_state`, `jawa/flowworks_body_report` (stock, capacity, limitless, recededCount) and `jawa/type_probe` identity. All three exist since `d83c40a9f`, and `validation.py` calls none of them.

## 3. validation.py assertions, classified

The verdict is about the component's **state predicate** against the mechanism the bar names.
What the judge sees is separate. The live outcome is from the 2026-10-01 run.

### 3a. Bar-claiming components (43 bars; script count)

**BAR VERDICTS: PROVES 4 · VACUOUS 15 · WRONG ASSUMPTION 7 · UNREACHABLE 17 · STALE ID 0** (total 43).
**Built state of the bar's feature:** BUILT 20 · BUILT but sharing Gravel art 7 · UNBUILT 12 · UNMEASURED 4 (liquid burning).

**The site (one finding that covers every plot).**
- The plots come from `t.anchor` with no bounds or edge check (`_plot`, l.88). Live:
  - plot C dug at (250,170) on a 250×250 map, out of bounds;
  - so did `toggle_sticky_limitless`;
  - plots near x≥240 became **sink cells**.
- Every toggle chain re-preps plots A-T that the bar chains already dug. D never resets, so they inherit depth and fill:
  - `excavatedCellCount` read **348** at the first component;
  - `depth_engine_off` read D=3 F=1 on a "fresh" D=1 channel.
- The map was the shared situational map, at tick 529,880, with 39 colonists restored and 12 corpses afterwards.
- Classification: **SITE defect, the dominant one.**

| bar(s) | component | verdict | why (evidence) | live 10-01 |
|---|---|---|---|---|
| canal_reads_as_dug_channel, never_gravel_path | canal_dug_channel_look | PROVES (dig) | reads D=1,F=0 and terrain RM_Channel_Empty (substring check, fragile). The visual half will fail: the texture IS Gravel | PASS |
| canal_dry_reads_as_obstacle | canal_dry_obstacle_look | WRONG | `'"pathCost":30' in str(r)` runs on a Python dict repr (single quotes), so **it can never match**. `get_defs` was called with no `fields`, and `fieldsAsked: []`. The source XML has `pathCost 30`, which is the ruled value. HARNESS | FAIL (harness) |
| filled_excavation_reads_as_obstacle | filled_excavation_obstacle_look | VACUOUS | reads back its own `setFill`; never reads the fill terrain's pathCost | UNMEASURED |
| canal_partial_fill_distinct, fill_tier_legible | plot B | VACUOUS (staging) | the engine is frozen, it writes F and reads F back. It proves the scene, not the mod | PASS |
| depth_and_fill_jointly_legible | depth_and_fill_joint_look | WRONG | the pads are D1F0, D2F1, D3F1, D4F2. The framed rect holds **no same-depth/different-fill pair**, so the bar's second clause is not staged | PASS (wrongly) |
| canal_fill_spreads_along_itself | canal_fill_spreads | UNREACHABLE | plot C is out of bounds. The "limitless" strip is interior, so it is **LIMITED** (needs edge + ≥50 cells) | UNMEASURED |
| canal_fill_front_watchable | canal_fill_front | WRONG | it asserts only mouth F≥1 after 3 pulses, which says nothing about a front moving. Plot C runs east, so per §2 the channel would oscillate and never fill. The diptych would show a flickering gap, not a front | UNMEASURED |
| tar_fill_front_lags_water | tar_front_lags_water | VACUOUS + UNBUILT | `wet < 10 after 3 pulses` is also true for **water** (≤1 level/pulse), so it passes with zero viscosity. Viscosity is unbuilt | UNMEASURED (fluid refused) |
| canal_holds_only_the_channel, never_liquid_on_open_ground | canal_holds_only_channel | PROVES (invariant) | the D=0,F=0 dry ring is a valid regression guard. But `toggle=channelConfinementEnabled` is **misattributed**: that toggle gates only the legacy `Flood_FlowWorks` (`Flood_FlowWorks.cs:238`), and the engine structurally never fills undug cells | UNMEASURED |
| canal_reads_as_same_liquid_as_reservoir | canal_same_liquid_look | VACUOUS | no predicate; judge only | UNMEASURED |
| fill_fluid_distinct | two_fluids_side_by_side | UNREACHABLE + UNBUILT | unconditional `BLOCKED` (one ActiveFluid per map) | UNMEASURED |
| reservoir_fill_visibly_drops, never_full_reservoir_after_heavy_draw | pond_drawn_down | VACUOUS | `any channel F>0` is not the reservoir's stock. `flowworks_body_report.stock` exists and is unused. It failed NOT_SETTLED **because the mod oscillates** (§2): the live vectors match the port exactly | FAIL (MOD: oscillation) |
| reservoir_shoreline_recedes | pond_shoreline_recedes | WRONG | proxies with one corner cell's `isSourceCell`. The recession order is engine-chosen, so the right read is `body.recededCount` | UNMEASURED |
| empty_reservoir_stops_flow | pond_empty_stops_flow | UNREACHABLE | 125-level pond vs a 36-level channel, so it **never empties**. The "no-op re-dig" is not a no-op: `deepenLevels:3` on D=3 deepens to **D=4** and spawns capture holders | UNMEASURED |
| reservoir_recharge_progress_visible | pond_recharge_visible | VACUOUS | no predicate. Refill is per day (ooze), so 20 pulses (~0.08 day) cannot show it | UNMEASURED |
| canal_burning…, canal_fire_reaches…, canal_fire_persists, canal_spent_after_burn | plot E | UNREACHABLE | plot E **never sets tar**, so it runs on water. `LiquidIgnition` needs `RM_LiquidProperties.flammable` terrain next to an existing Fire, and live there were 0 Fire things. `burned_channel_spent` alone waits **60,000 ticks** | FAIL / UNMEASURED |
| slime_reads_as_viscous_not_water | slime_viscous_look | UNREACHABLE (shared map) | fluid set refused live. Otherwise a staging read-back | UNMEASURED |
| slime_occupant_below_surface | slime_occupant_look | UNREACHABLE + UNBUILT | no draw offset exists | UNMEASURED |
| pit_depth_ladder_legible | depth_ladder_look | VACUOUS (staging) | D=0..4 read-back. All depths share the Gravel texture | PASS |
| pawn_height_ladder_legible, pawn_lowers_on_deeper_cell, pawn_rises_on_shallower_cell | plot H | VACUOUS + UNBUILT | no predicate (frames only). No depth draw offset in `Source/`. Live, the frame call timed out at 30 s | FAIL (bridge timeout) |
| pit_reads_as_hole, pit_walls_have_visible_depth, pit_reads_at_size | pit_hole_look | VACUOUS (staging) | D=4 read-back. RM_Channel_Superdeep is Gravel, and the holder is invisible | PASS |
| pit_not_vanilla_trap, never_reads_as_building | pit_not_vanilla_trap | WRONG | the scan of Defs for `TrapSpikeArmed` hits **RM_Ladder's placeholder** and the **legacy RM_OpenPitBase / dig-site / pit-cell family**, not the superdeep excavation (its holder `RM_SuperdeepPit` is `drawerType None`). Red for the wrong reason | FAIL |
| pit_occupant_below_floor, pit_occupied_distinguishable, never_snared_standing | pit_captures_hostile | UNREACHABLE | a hostile pawn **ignores `order_pawn`** (live: "no drafter…ordered undrafted", 0/1 arrived). "Absent from list_pawns" also counts a dead pawn as captured. Fix: spawn **on** the D=4 cell and read the holder | UNMEASURED |
| pit_trapped_reads_as_trapped | same | UNREACHABLE + UNBUILT | walls-above-head needs a draw offset | UNMEASURED |
| pit_covered_invisible, pit_covered_seam_at_max_zoom | pit_cover_invisible | UNREACHABLE + UNBUILT | unconditional BLOCKED | UNMEASURED |
| ladder_state_legible | ladder_state_look | WRONG + UNBUILT | the ladder is placed **beside** the pit, not in it, so it does nothing. No raised/lowered state exists | UNMEASURED |
| sluice_gate_state_legible | sluice_state_look | UNREACHABLE + UNBUILT | BLOCKED (`FLOWWORKS_DOOR_FAMILY_1`) | UNMEASURED |
| spikes_read_distinct | spikes_look | UNREACHABLE + UNBUILT | BLOCKED | UNMEASURED |

**Smaller defects:**
- `canal_dug_channel_look` substring-matches `"RM_Channel_Empty" in str(r)`. This breaks debug_process §2.2 ("never substring a payload").
- The `_expect(x if t._guard() else None, …)` idiom is sound live. It means the offline `--mock` pass proves nothing about any of these predicates.

### 3b. Toggle components (27 toggles, 49 toggle-only components)

**Merged from the helper audit, a static read of every toggle's C# gate.** The setup holds:
- all 27 fields exist as `public static bool` in exactly the classes `validation.py` names
  (22 FW, 4 Pits, 1 River);
- each initializer equals its `Scribe_Values` default;
- `DEFAULTS` matches both.

**TOGGLE VERDICTS: PROVES 4 · VACUOUS 16 · WRONG ASSUMPTION 5 · STALE ID 1 · UNREACHABLE 1** (27). The audit said PROVES 5; sourceBudget moved to VACUOUS after the GPT review, confirmed by the port.
Only `fillInEnabled`'s OFF half is a clean proof. The other four PROVES are partial or
contaminated:
- sourceBudget and recession run on a stale body from an earlier chain;
- superdeepCapture's OFF half is weak;
- ownFaction asserts only its default half.

| toggle | verdict | the decisive reason |
|---|---|---|
| depthEngineEnabled | WRONG (as staged) | ON proves. OFF re-digs plot A and inherits F, so it fails on a working toggle |
| channelConfinementEnabled | WRONG | gates only the legacy flood. The ON ring even includes a source-strip cell (D=4/F=4), so ON can never pass |
| digToDepthEnabled | WRONG | the drive tool bypasses the designator gate |
| liquidCorrosionEnabled | VACUOUS | no `_expect`. The code damages pawns/apparel, never the Wall the test spawns |
| liquidIgnitionEnabled | VACUOUS | water map. `n<=1` is true at 0 fires. The ON half asserts nothing |
| fillInEnabled | PROVES | ShouldSkip gate. Depends on the spawned colonist doing the job |
| fillInDisplacementEnabled | VACUOUS | no colonist in that chain, so the fill-in never runs and the sums stay trivially equal. Live it read "3→0". Explained: the cells were in the sink band (`isSinkCell: true`, x=240-242), so SITE |
| sourceBudgetEnabled | **VACUOUS** (corrected after the GPT review; was PROVES) | the 30-cell east channel off the 2×2 pond (budget 20) oscillates and saturates at **16 wet with 4 stock left** (port), so the budget never binds. ON `wet<=20` passes regardless, and OFF `wet>20` can never pass. Live OFF read 16 |
| stickyLimitlessEnabled | VACUOUS | interior strip, so limited either way |
| recessionEnabled | PROVES (contaminated) | corner-cell proxy, stale body |
| refillEnabled | VACUOUS | 0.13 units/cell/day over 0.083 day |
| rainFillsExcavationsEnabled | **STALE ID** | `set_roof_batch ThickStoneRoof`: no such RoofDef (vanilla `RoofRockThick`). The result is unchecked, and the cell was also in the sink band |
| edgeSinksEnabled | UNREACHABLE | plots are interior. ⚠️ Live `edge_sinks_on` **PASSed vacuously**: `sinkTransferredTotal` is a **map-wide** counter, and it rose from other chains' sink cells |
| superdeepCaptureEnabled | PROVES (ON) | OFF half weak (pathing detour). Live it timed out |
| superdeepCapturesOwnFaction | PROVES (default half) | the True half asserts nothing |
| ladderRequiredToExitEnabled | VACUOUS | ladder outside the pit cell |
| superdeepShootingRuleEnabled | VACUOUS | no shooters |
| bottleLoopEnabled | VACUOUS | spawns an already-filled bottle |
| bottleDirtyStageEnabled | VACUOUS | nobody drinks |
| tankLoopEnabled | WRONG | the tank never touches the excavation grid. Live, OFF "drew": the F change came from the engine pulse, not the tank |
| liquidDrillingEnabled | VACUOUS | no outlet, survey, power or fluid match |
| typedLiquidShoresEnabled | VACUOUS | worldgen. A field read-back only |
| trapTriggerEnabled | WRONG | the superdeep holder never reads it (`CompPitCoverTrigger` is the legacy covered building pit) |
| fallDamageEnabled | VACUOUS | reachable through superdeep capture plus a hediff read |
| escapeEnabled | VACUOUS | reachable through ladder plus `EscapeBlocked` |
| pitCellExposureEnabled | VACUOUS | needs a legacy `Building_PitCell` |
| riverSteamEnabled | VACUOUS | setter echo |

**Bridge tools:** all 19 called tools exist in `JawaBench.BridgeTools/*.cs`, and every
parameter name and response key matches. The exceptions are the stale roof def above and the
pathCost repr. Note that `spawn_pawn`'s `success` is never checked, so a `None` id flows into
`order_pawn`. (Full audit: the helper's scratch file. Its essentials are here.)

Two kinds of finding from my own source read agree with the audit:

**Gates that `validation.py` misattributes:**

| toggle | real gate (file:line) | what validation.py assumes | verdict |
|---|---|---|---|
| digToDepthEnabled | `WorkGiver_DigCanal.cs:53`, `Designator_DigCanal.cs:95`: the **player designation/job path** | that `flowworks_excavation_drive` (which calls `Deepen` directly) clamps to D=1 | WRONG. Live it FAILed with D=3, which is correct engine behaviour |
| channelConfinementEnabled | `Flood_FlowWorks.cs:238`: the **legacy release path only** | that the depth engine leaks with it OFF | WRONG. The engine cannot fill an undug cell |
| tankLoopEnabled | `WorkGiver_FillBottleFromTank.cs:22`, `WorkGiver_EmptyBottleIntoTank.cs:24`: the **bottle WorkGivers** | that a tank draws from an adjacent excavation | WRONG. Live, OFF still "drew", so something else moved F |
| trapTriggerEnabled | `Pits/Trigger/CompPitCoverTrigger.cs:46`: the **legacy building-pit cover** | that it gates superdeep capture | WRONG. Superdeep capture is `superdeepCaptureEnabled` |
| ladderRequiredToExitEnabled | `Building_SuperdeepPit.cs:61`: a ladder **in the pit cell** | a ladder beside the pit | WRONG (placement) |

**VACUOUS (no predicate: wait-only or flip-only):**
- fill_in_displacement_off
- sticky_limitless_off
- liquid_corrosion (both)
- superdeep_own_faction ON branch
- ladder_required_off
- superdeep_shooting (both)
- bottle_loop_off
- bottle_dirty (both)
- liquid_drilling (both)
- typed_shores (it reads the field only)
- trap_trigger_off
- fall_damage (both)
- escape (both)
- pit_exposure (both)
- river_steam, which writes and reads back the setting. That **is the setter's echo**, which the suite's own header forbids.

These all PASSed live, and **a PASS here is noise**: 15 of the 28 live PASSes are wait-only components.

## 4. Walk `## must be true` and `## the walk` lines, classified

| line | verdict | evidence |
|---|---|---|
| MBT1: `RM_DigCanal` drives a colonist to dig (`JobDriver_DigCanal`, `WorkGiver_DigCanal`) | **MISSING** | the defs exist (`FlowWorks_Designations.xml`, `_JobDefs.xml`, `_WorkGivers.xml`), but **no component ever designates a dig**. Every dig is `excavation_drive` → `Deepen`, so the player's own path is untested. This is the single largest functional gap |
| MBT2: flooded cell's underlying terrain recoverable (temp terrain) | MISSING | it applies to legacy `Flood_FlowWorks`, which is reachable via `jawa/flowworks_spawn_flood`, and no component calls it |
| MBT3: walled flood self-destroys at `ExpiryTick = spawnedTick + 2*FloodingTicks` | MISSING | `Flood_FlowWorks.cs:107,201` holds as written. No check covers it |
| MBT4: `RM_Channel_Empty` … "is what `canal_dig` sets a cell to" | **STALE ID** | `canal_dig` is a stub (`JawaBenchFlowWorksTools.cs:54-75`). `Deepen` sets `DryTerrainFor(d)` |
| MBT5: spread channel-constrained via `CanLiquidEnter` behind `channelConfinementEnabled` (default true) | PROVES as prose (true for the legacy flood), but the script tests it on the engine: WRONG there | `Flood_FlowWorks.cs:238` |
| step 1 [L] no Config error naming the three def files | PROVES as written; **MISSING from validation.py** | no log gate exists in the suite |
| step 2 [D] `RM_Fluid_Water floodTerrain = ShallowFloodwater` | **STALE ID** | the XML says `RM_Fill_Water_Trace`. volumePerTile 1, ticksPerTile 60 and floodedTicks 300000 are correct |
| step 3 [D] `RM_Channel_Empty` Diggable, natural=true | PROVES as written; MISSING from the suite | XML: affordances Walkable/Light/Diggable, natural true, pathCost 30 |
| steps 4-6 [B] drive / report / fill | PROVES | the tools match. Step 6's "fill=1 after one pulse" holds only for an isolated cell |
| step 7 [S] look | n/a (owner layer) | |
| `→ chain.component` arrows on MBT lines | **MISSING** | 0 of 5 lines carry one. debug_process §2.3 counts an unarrowed line as uncovered |

## 5. The "6 by-design failures", checked

`flowworks_shows_wiring_2026-10-01.md` says "four components claim six bars and raise BLOCKED
unconditionally". **A script count finds 4 components claiming 5 bars:**
- `fill_fluid_distinct`
- `pit_covered_invisible`
- `pit_covered_seam_at_max_zoom`
- `sluice_gate_state_legible`
- `spikes_read_distinct`

So "6" is off by one. The sixth bar that the "6" figure most plausibly counted is
`ladder_state_legible`. It is not BLOCKED in code, but its feature (a raised/lowered ladder
state) is unbuilt.

**The true by-design (UNBUILT) set is larger: 12 bars.** Each is checked against source.

| # | bar | missing feature (source evidence) |
|---|---|---|
| 1 | fill_fluid_distinct | per-body fluid. `activeFluid` is one field per map component |
| 2-3 | pit_covered_invisible, pit_covered_seam_at_max_zoom | superdeep cover. Only the legacy `Building_TerrainMimicCover` exists |
| 4 | sluice_gate_state_legible | door family (`FLOWWORKS_DOOR_FAMILY_1`) |
| 5 | spikes_read_distinct | per-cell spikes |
| 6 | ladder_state_legible | ladder raised/lowered state. `RM_Ladder` is `thingClass Building` and only present or absent |
| 7 | tar_fill_front_lags_water | viscosity. `FlowPerPulse` is global, and `viscosityClass` is unwired |
| 8-10 | pawn_height_ladder_legible, pawn_lowers_on_deeper_cell, pawn_rises_on_shallower_cell | a depth draw offset. Nothing in `Source/` offsets pawn drawing by D |
| 11 | pit_trapped_reads_as_trapped | the same draw offset (walls above head) |
| 12 | slime_occupant_below_surface | the same draw offset |

**Seven more bars share one art defect:** every channel depth uses `Terrain/Surfaces/Gravel`.
- So `never_gravel_path` and the depth, hole, wall and size bars will fail on the judge even though their state is right.
- That is an ART gap, not an unbuilt mechanic.
- Four fire bars are **UNMEASURED** for built-state. `LiquidIgnition` exists but is OFF by default, never live-proven, and staged on water.

## 6. MISSING coverage: what the code does that nothing checks

**Player path**
1. **The player dig path:** designate `RM_DigCanal`, a colonist digs, D increases. Also `digToDepthEnabled` OFF clamping that path.
2. **Fill-in displacement arithmetic:** `F-(D-1)` is credited to neighbours, and overflow goes to `overflowDestroyedTotal` (OFF goes to `ReportOverflow`). The live "3 → 0" was sink drainage (SITE), so the arithmetic itself has never been checked.

**Conservation and invariants**

3. The conservation ledger, read from the log (`conservation ledger does not balance`) and from `overflowDestroyedTotal`.
4. The limited-body budget, read directly as `body.stock`, `capacity` and `limitless` via `flowworks_body_report`, and limitless requiring edge contact plus 50 cells.
5. Sinks within 10 cells of the edge, read through `isSinkCell` and `sinkTransferredTotal`, with a negative control at 11 cells.

**Engine behaviour**

6. **Engine cadence:** `engine_state.pulseIntervalTicks` = 250 at default, with `nextPulseTick` advancing by exactly that.
7. **Determinism:** the same staged scene twice must give the same F vector. The engine claims index-tiebreak determinism (`CompareDeepestFirst`).
8. Index-order fill direction (§2): an east channel vs a west channel.
9. Rain filling **roofed vs unroofed** cells off the sink band. Live "unroofed cell took no rain" was a cell at x=240, which is a sink cell (SITE).

**Persistence and the legacy flood**

10. Save→load persistence of D/F/activeFluid/bodies (`ExposeData`).
11. The legacy flood: temp terrain, recovery, `ExpiryTick`, and the confinement toggle (`flowworks_spawn_flood`).
12. The Player.log / `rimbridge/list_logs` gate on config errors.

## 7. Counts (script-derived, with sanity probe)

| set | PROVES | VACUOUS | WRONG | STALE | UNREACHABLE | MISSING |
|---|---|---|---|---|---|---|
| 43 north-star bars (claiming components) | 4 | 15 | 7 | 0 | 17 | 0 (all claimed) |
| walk must-be-true + walk steps (12 lines incl. arrows) | 4 | 0 | 1 | 2 | 0 | 5 |
| 27 toggles (49 components) | 4 (1 clean) | 16 | 5 | 1 | 1 | 0 |
| behaviours with no check at all | | | | | | 12 (§6) |

**Live 2026-10-01, re-read by component.**
- 28 PASS, made up of:
  - **4 PROVES-grade:** canal_dug_channel_look, dig_to_depth_on, edge_sinks_on, fill_in_on;
  - **9 staging read-backs;**
  - **15 wait-only toggles.**
- 21 FAIL. The causes trace as follows:
  - **2 are a MOD defect:** the two `NOT_SETTLED` (pond_drawn_down, confinement_on) are the east/north channel oscillation (§2). It is measured in the live log and reproduced exactly by the port. The fill-in displacement "3→0" is **SITE, not MOD**: its three cells (x=240-242 on a 250-wide map) read `isSinkCell: true` in the live evidence, so the sinks drained them over the 10-pulse wait. tank_loop_off "drawing" was the engine pulse, not the tank (§3b).
  - **≥10** are SITE (out of bounds, sink band, plot reuse);
  - **≥6** are HARNESS or WRONG assumption (pathCost repr, digToDepth, trap_trigger, hostile order, 30 s timeouts ×4);
  - (The NOT_SETTLED pair is counted above as MOD, not budget.)
