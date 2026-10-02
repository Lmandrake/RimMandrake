# FlowWorks functional script v2: plan (2026-10-02)

I designed this offline as a helper to FOUNDRY. The game was down and I did not take the bridge.

- **The evidence** is `design/RimMandrake/flowworks_northstar_interrogation_2026-10-02.md` (call it "INT").
- **The script** is `src/RimMandrake/FlowWorks/northstar/validation_v2.py` (the `_DRAFT` was promoted
  after its first green live run, 2026-10-02; its docstring records what the live runs taught). It is
  not wired into modcheck, and it does not replace `validation.py` or touch the walk.

## 0. What changes, in one paragraph

The current suite costs **112,921 game ticks and 21-35 min**. On the one recorded run it reached
only **4 PROVES-grade PASSes** out of 85 components (INT §7), and most of its reds were SITE or
HARNESS defects. The causes:
- plots derived from an anchor that fell off the map and into the 10-cell sink band;
- plots reused across chains on a grid where depth never resets;
- one ActiveFluid per map;
- hostile pawns that ignore `order_pawn`;
- settle loops sized below the engine's own 1-level-per-pulse throughput.

v2 inverts this. Most of what the mod does is decidable **with the clock stopped**:
- dig, clamp, classification, limitless and limited, sinks, capture-holder spawn;
- defs, settings and identity.

Those run first, at 0 ticks. What needs time is measured **in pulses**, at a pinned 60-tick pulse,
against a **pure-Python port of the engine's pulse** that predicts the exact F vector. A live
reading either equals the prediction or names the first cell that differs.

The site is **one pristine bland save, loaded once per fluid**. Every scene gets **never-used
cells**, so no state is inherited.

**Headline from this pass.** The pulse port that v2 uses as its oracle reproduced the live run's
F vectors **exactly**. Those vectors expose a MOD defect: a channel dug **east or north** of its
source never fills and oscillates forever (INT §2). E2 below is built to show it red-before-green.

**Estimated cost: ~6,700 ticks and ~3-5 min wall, against 112,921 ticks and 21-35 min (~17×
fewer ticks).** That is a planning estimate, not yet measured.

## 1. Design rules (each traces to a measured failure)

| rule | the failure it prevents (INT ref) |
|---|---|
| R1 **Static plots, never anchor-derived.** Absolute coordinates are validated offline: inside the map, ≥ 11 cells from every edge unless the scene IS the sink band, and ≥ 4 cells apart. | (250,170) out of bounds; x≥240 rain/fill cells were sinks (INT §3a site) |
| R2 **A cell is used by exactly one scene per load.** An offline allocator asserts it. `D` never decreases and no tool resets it. | `excavatedCellCount` 348 at the first component; `depth_engine_off` D=3 F=1 on a "fresh" channel |
| R3 **One ActiveFluid per load.** The water group runs on load 1, the tar group on load 2 (`set_active_fluid` runs first, before any classification). Slime has no mechanism of its own beyond fill terrain, so it is checked offline (§3 O1). | tar and slime chains REFUSED live |
| R4 **Zero ticks first.** Every check that a stopped clock can decide runs before any tick. | 15 of 28 live PASSes were wait-only noise |
| R5 **Time in pulses, not ticks.** Pin `pulseIntervalTicks`=60 (the clamp floor) and read it back from `jawa/flowworks_engine_state`. Step `ticksUntilNextPulse+1` to land exactly after a pulse. Assert an **exact** predicted F vector, never "settled for 3 pulses". One cadence check runs at the shipped 250. | NOT_SETTLED ×2. The real cause was the mod's oscillation (INT §2), which a "settled for 3 pulses" rule can never see. An exact vector catches it on the first read |
| R6 **Read the quantity, not a proxy.** Body stock, capacity, limitless and `recededCount` come from `flowworks_body_report`. Capture is read from the holder or pawn state, never from "absent from list_pawns". pathCost comes from a typed field read, never `str(r)`. | pathCost repr; corner-cell recession proxy; dead pawn counts as captured |
| R7 **Stimulate without pathing.** A pawn is spawned ON the cell under test. Fire is spawned next to flammable fill. The player path is driven by designation + colonist only where the player path IS the subject (dig, fill-in). | hostile 0/1 arrived (no drafter) |
| R8 **Every positive check has a twin negative control in the same scene** (red-before-green). Each live check states the reading that would make it fail. | debug_process §3 rung 3 "a check never seen red proves nothing" |
| R9 **Unbuilt features are recorded as UNBUILT from a zero-tick source/def fact**, never staged to fail. | 12 UNBUILT bars staged and waited on (INT §5) |
| R10 **Batch reads.** Reads are ≤ 6 cells per scene. A rect read tool is owed (§8), and `rimbridge/run_script` is the fallback (External advice). | 799 report polls at ~48 ms each |

## 2. Environment: the bland static world

**The save.** `NS_FlowWorks_Bland_v2` is built ONCE by a builder in the shape of `prep_site.py`.
It is not run per suite.
- **Tier:** `modset_builder` `flowworks` (BRIDGE + `mandrake.rm.flowworks`, all five DLCs via
  `dlc: True`). It forbids `mandrake.rm.pits`, `sarg.alphabiomes` and anything ManyWaters, so a
  terrain cannot come from a donor. This is the min list. On 2026-10-01 it launched in **36-38 s**
  (time ledger §2).
- **Map:** a `start_debug_game_ready` map ≥ 200×200, then `modcheck.bland_world.setup`'s recipe:
  - a flat dry tile at 15-30 °C, no mutators, rivers or roads;
  - `destroy_bulk nonColonists`, which also removes hostile-faction insects (measured 10-01);
  - ruins destroyed;
  - **the colony named** (`saved_base.induce_and_finish_naming`), because the naming dialog
    re-raises every 1000 ticks.
- **Colonists:** keep 2. The fill-in and dig scenes need a worker. Despawn the rest so the
  watch's food feed stays at 1-2 calls.
- **Terrain:** the plot rect is painted Soil, and the authored water bodies are painted:
  - **W1:** a WaterShallow strip touching the WEST edge, 4×16 = 64 cells, so it is limitless.
  - **W2:** a 1×1 interior pond (WaterShallow), limited, capacity 5.
  - **W3:** a 2×1 interior pond, limited, capacity 10.
  - **W4:** an edge strip of 4×10 = 40 cells. It is the negative control for the 50-cell rule.
  - **W5:** an interior 8×8 = 64-cell pond. It is the negative control for the edge rule.
  - **W6 / W7:** stickyLimitless-OFF twins of W1, two cells apart.
- **What the save does NOT have:** unclassified bodies are **left unclassified** (the reverse of
  `prep_site.py` step 6). Classification IS a check (S3), and the order relative to the
  ActiveFluid set matters (R3).
- **Pre-save gate:** `excavatedCellCount==0` and `bodyCount==0` (via `flowworks_engine_state`).
- **How it is saved:** `saved_base.save_base`, which backs up the keepers and proves a NEW file
  appeared and no other changed size.

**Interference sources and how each is pinned:**

| source | pin | verified by |
|---|---|---|
| weather (rain fills excavations; ruling 25) | `jawa/weather_set Clear lockWeather=true` saved into the save. Only S/E6 sets Rain | `weather_get` at load (preflight) |
| time of day / season / temperature (freezing liquid, heat) | summer, 15-30 °C tile. `cell_temperature` on the plot centre must be in 5-40 °C | preflight |
| game conditions and incidents (raids, cold snap) | conditions ended and the incident queue cleared before the save. Watch detectors stay on (abort policy) | `weather_get.conditions == []`, `queued_incidents == []` |
| wildlife, strangers, hostiles | `destroy_bulk nonColonists` before the save. The detectors abort on any new one | `assert_world` |
| colonists wandering into plots and getting captured | 2 colonists drafted and parked outside the plot rect. Only the dig and fill-in scenes undraft one | list_pawns positions vs the plot rect |
| colonist hunger on a food-less map | the run is ~7k ticks (< 0.2 day), so the feed seldom fires. The watch's `feed_colonists` stays on | watch summary `fed` |
| naming dialog / modal | named before the save. `detectors.modal_open` ignores `Dialog_NamePlayer*` | modal detector |
| fog | the plot rect is unfogged before the save | screenshots only. State reads are fog-independent |
| autosave stalls | `autosaveIntervalDays` raised for the run and restored (time ledger fix 8) | Prefs read-back |
| multiple maps slowing ticks (416→50 t/s) | ONE map in the save. Loading a save replaces the game, so no stale maps survive | `maps` count = 1 at preflight |
| window focus (tick-rate collapse) | `game_focus.focus_game` per scene, and log ticks/s per step | timing jsonl |
| mod settings drift | the 27 toggles plus `pulseIntervalTicks`, `flowPerPulse`, `rainFillPerPulse` and `minLimitlessBodyCells` are read at preflight (L4). Any non-default value REFUSES the run. Only the harness pins (pulse=60, and rainFillPerPulse=1.0 inside E6) are set, read back and restored in `finally` | `mod_settings_field get` |
| deployed copy ≠ repo | `type_probe` identity: the assembly sha must equal the repo DLL. `get_defs` with explicit `fields` | L2/L3 |
| map edge sinks | R1 geometry. S4 measures the band directly | S4 |
| index-order fill direction | every flow scene is predicted by the oracle in its real compass direction, and E2 measures both directions on purpose | E2 |

## 3. The script, with its game-time budget

The ticks are planned. Wall time assumes ~150 ticks/s, the middle of the measured 33-416 range,
and ~50 ms per bridge call (measured median). **Every live row lists the reading that would make
it red.** "Neg" is its in-scene negative control.

### Tier O: offline, 0 ticks, ~5 s, run on every commit (`--offline`)

| id | check | red when |
|---|---|---|
| O1 | Defs, parsed:<br>• RM_Fluid_Water `floodTerrain=RM_Fill_Water_Trace`, volumePerTile 1, canalCellsPerSourceCell 5<br>• channel pathCost ladder 30/45/80/300, affordances, `natural`<br>• every FluidDef's fill terrains resolve; tar fill terrain carries `RM_LiquidProperties flammable=true`; slime fill terrain exists and is not a water-parented recolour<br>• `RM_SuperdeepPit drawerType None`; `RM_Ladder` has `PlaceWorker_LadderOnExcavation`<br>• `RM_DigCanal`/`RM_FillInCanal` designations, jobs, workgivers | any field differs or any def is missing. Sanity probe: the parser must find `RM_Channel_Empty` |
| O2 | Settings defaults in C# (`RimMandrakeFlowWorksMod.cs` initializers AND `Scribe_Values` defaults) equal the script's DEFAULTS for all 27 toggles plus the 4 floats | a mismatch |
| O3 | **UNBUILT register.** For each of the 12 UNBUILT bars (INT §5), a source fact is still true, e.g. `FlowPerPulse` used fluid-independently, no pawn draw offset by D, `activeFluid` a single field, no Sluice def. When a fact flips, the bar is reported **"feature landed: stage it now"** | a fact flips (that is a *promotion*, not a failure) |
| O4 | Geometry: every scene's cells are in bounds, at their declared edge distance, and disjoint (R1/R2) | an overlap, or a cell in the sink band that is not declared a sink |
| O5 | **Pulse oracle selftest:** the Python port reproduces hand-worked cases, including the index-order prediction, and is deterministic over 100 seeds | a mismatch |
| O6 | `lint_calls.py` schema lint of every bridge call against `tool_schemas.json` | an undeclared parameter or a missing tool |

### Tier L: load and preflight, 0 ticks, ~40-60 s wall (the load itself ~20-40 s, UNMEASURED for this save)

| id | check | red when |
|---|---|---|
| L0 | `rimworld/load_game_ready` NS_FlowWorks_Bland_v2 (readiness `mapData`, per the author's doc). Must read paused: `ticksGame` unchanged across two reads | load fails / clock moves |
| L1 | `rimbridge/list_logs`: no error or exception naming `mandrake.rm.flowworks`, `RimMandrake.FlowWorks` or FlowWorks def files. **Sanity probe:** the log is non-empty and contains the RimBridge start line | any hit; or an empty log (UNMEASURED) |
| L2 | `jawa/type_probe` identity: the loaded assembly's sha256 equals the repo `Assemblies/*.dll` | mismatch, meaning the deployed copy is stale |
| L3 | `jawa/get_defs` with explicit `fields` (pathCost, affordances…) for the channel and fill terrains. Read `success`/`foundCount`/`notFound` as typed values | live ≠ O1 |
| L4 | Settings snapshot, all 31 values = defaults. Then pin pulse=60 and read it back via `engine_state.pulseIntervalTicks` | drift; pin not read back |
| L5 | Site pristine: `engine_state` excavatedCellCount=0, bodyCount=0, activeFluidRaw=null; weather Clear, no conditions, maps=1, plot temperature in band, no pawn inside the plot rect. **Neg:** the same predicate run against a deliberately prefilled fakegame site must refuse (offline selftest) | any dirt |

### Tier S: state, clock stopped, 0 ticks, ~25 s wall (≈120 calls)

| id | check (bar / MBT it serves) | neg control in the same scene | red when |
|---|---|---|---|
| S1 | **Dig ladder.** `excavation_drive` deepen 1,2,3,4 on four fresh cells.<br>• D reads 1..4<br>• `canal_cell_report` terrain RM_Channel_Empty/Mid/Deep/Superdeep<br>• `excavatedCellCount` +4, `superdeepCellCount` +1<br>• a `RM_SuperdeepPit` holder exists at the D=4 cell (`list_things`)<br>Serves pit_depth_ladder / canal_reads_as_dug_channel state; MBT4 corrected | deepen the D=4 cell once more: it stays 4; no holder at the D=3 cell | any read differs |
| S2 | **Fill clamp (driver contract).** setFill 9 on D=2 gives F=2; setFill 1 on an undug cell gives `fillSet=false`, F=0 | the undug cell is the neg | clamp broken |
| S3 | **Classification.** `body_report` (classify=true) on W1, W2, W3, W4, W5. Expected limitless: T,F,F,F,F. Capacity: W2=5, W3=10 | W4 (edge but <50 cells) and W5 (≥50 cells but interior) | any flag or capacity differs |
| S4 | **Sink band.** One cell dug at 9 from the edge and one at 11 (a declared sink scene). `isSinkCell` T / F | the 11-cell twin | wrong band |
| S5 | **stickyLimitless toggle (0 ticks).** With it OFF, classify W6 (edge, 64 cells) → limitless F. Restore ON, classify W7 (identical) → T | W7 | W6 is limitless, or W7 is not |
| S6 | **digToDepth on the player path (0 ticks).** With it OFF, `designate_batch add RM_DigCanal` on a D=1 cell. Read the designation count on that cell: refused (0). With it ON, the designation is accepted (1). Then remove it | the ON twin | an OFF designation is accepted |
| S7 | **Capture, holder present.** Spawn a hostile ON a D=4 cell. Step **2 ticks** (the holder is a normal-ticker Building). The pawn must be `spawned=false` AND `dead=false`, and be in the holder (pawn_get / holder inspect). Serves pit_occupant / never_snared_standing state | the colonist twin on a second D=4 cell stays spawned (superdeepCapturesOwnFaction default false). The hostile on a D=3 cell stays spawned | captured ≠ expected |
| S8 | **Capture toggle.** `superdeepCaptureEnabled` OFF, step 1 tick so `SyncMap` runs → the holder count on D=4 cells is 0. A hostile spawned on one stays. Restore ON, step 1 tick → holders return | the ON state is its twin | holders not shed / not regrown |
| S9 | **Ladder in pit.** Spawn `RM_Ladder` IN a D=4 cell. Its inspect reads "ladder present". A twin ladder spawned BESIDE the pit reads "no ladder" | the beside-pit twin | inverted |

S7 and S8 spend 4 ticks in all, counted under E.

### Tier E: engine, pinned pulse 60, ~6,700 ticks, ~45-75 s stepping + ~30 s calls

| id | scene | ticks | prediction (oracle) / red when | neg control |
|---|---|---|---|---|
| E1 | **Cadence.** Restore pulse=250 and read `nextPulseTick`. Step to the boundary+1: `nextPulseTick` advances by exactly 250. Re-pin 60: the next advance is 60 | ~320 | advance ≠ setting | — |
| E2 | **Channel fill + direction + determinism.**<br>• Four D=1 channels of 4 cells off W1: two running east (scenes A and A′ are identical twins) and two running west, as the geometry allows. W1 is on the west edge, so "west-running" means a channel dug from W1's south end running south; the oracle is direction-generic.<br>• Step 6 pulses, reading the F vectors after pulses 1, 3 and 6.<br>Serves canal_fill_spreads / fill_front / holds_only_channel | A vs A′ identical (determinism); a dry ring around each run (`never_liquid_on_open_ground`) | live vector ≠ oracle at any read, or A ≠ A′. ⚠️ The oracle PREDICTS the east and north runs oscillate. The bar-level check (`channel_fills`: every channel full by pulse 8) is therefore **expected RED on the east/north twins until `FLOWWORKS_CHANNEL_OSCILLATION_1` is fixed**, and GREEN on the west/south twins (its negative control) |
| E3 | **Limited budget + exhaustion + recession.**<br>• Scene: a W2 (cap 5) → 1×8 D=1 channel. Step until the oracle says the stock is exhausted (≈8-10 pulses), then 3 more.<br>• Assert: Σ F = 5; `body.stock` < 1; the vector unchanged over the last 3 pulses (`empty_reservoir_stops_flow`); `body.recededCount` = 1 (`reservoir_shoreline_recedes`, read, not a proxy).<br>• Then the neg control: `sourceBudgetEnabled` OFF for 2 pulses → Σ F rises (a spent body supplies again). Restore. | ~840 | any differs | the budget-OFF tail |
| E4 | **Engine off.** On a fresh unfilled channel off W3: set `depthEngineEnabled` OFF. Step 2×60. F stays 0 and `nextPulseTick` is frozen. Set ON, step 61: F at the oracle's cell rises | ~250 | F moves while OFF / stays while ON | the ON half |
| E5 | **Sinks.** A D=1 run from W1 that ends inside the sink band. Over 4 pulses `sinkTransferredTotal` rises by the oracle's amount. With `edgeSinksEnabled` OFF for 2 pulses it is unchanged, and `isSinkCell` reads F | ~360 | total wrong | the OFF half |
| E6 | **Rain, roofed vs unroofed** (ruling 25). Two isolated D=1 cells, one under a `RoofConstructed` patch. Not `ThickStoneRoof`, which the old suite used: no such RoofDef exists (INT §3b). The roof is read back via `get_roof_batch` before stepping. Pin `rainFillPerPulse` 1.0, weather Rain locked. Read the weatherManager RainRate first; it must be > 0.01, otherwise UNMEASURED. Step 2 pulses: unroofed F=1, roofed F=0. Then `rainFillsExcavationsEnabled` OFF on a third cell: F=0. Restore Clear and 0.1 | ~240 | unroofed dry / roofed wet | roofed twin; toggle-OFF twin |
| E7 | **Fill-in displacement (player path, MBT; the live "3→0" was sink drainage, so the arithmetic has never been checked).** A 1×3 D=2 run with F=2,2,2 and the engine paused by toggle so a pulse cannot move it. Designate `RM_FillInCanal` on the middle cell, undraft one colonist next to it, step until D of that cell = 1, capped at 2,000 ticks. Assert Σ F conserved, or `overflowDestroyedTotal` rose by exactly `F-(D-1)` = 1 if the neighbours were full. `fillInDisplacementEnabled` OFF twin: displaced liquid is destroyed, so overflow rises by 1 and Σ F drops by 1 | ≤2,000 | Σ F + Δoverflow ≠ before (a leak) | the OFF twin |
| E8 | **Player dig path (MBT1).** `designate_batch add RM_DigCanal` on 1 fresh cell, undraft colonist 2, step until D=1, capped at 2,500 ticks. Assert the job ran (D=1 and terrain RM_Channel_Empty) | ≤2,500 | D stays 0 within the cap | S6's refused designation |
| E9 | **Conservation gate.** After E2-E8, `list_logs` has no `conservation ledger does not balance` line, and `overflowDestroyedTotal` = Σ of what E7 predicted. **Sanity probe:** the E7 OFF twin must have produced exactly one dev warning `conservation exception` | 0 | an imbalance line | the expected `conservation exception` line |
| E10 | **Save/load persistence.** `save_game` to a work slot (prove the new file), then `load_game_ready`. D, F, activeFluid, `body.stock` and `excavatedCellCount` on 8 sampled cells equal the pre-save reads | 0 (load ~20-40 s wall) | any differs | — |

### Tier T: the tar load, ~400 ticks, + one load (~20-40 s)

| id | check | ticks | red when |
|---|---|---|---|
| T0 | Reload the pristine save. `set_active_fluid RM_Fluid_Tar` BEFORE any classify or fill; `fluidAfter` must read back. **Neg:** a second call with water must REFUSE once a cell holds fill (after T1) | 0 | not set / not refused |
| T1 | A 1×3 D=1 run, setFill 1 (driver). `canal_cell_report`: the terrain is tar fill, and `TerrainDef` has `RM_LiquidProperties.flammable` | 0 | wrong terrain |
| T2 | **Ignition** (liquidIgnition default OFF, so this is a toggle check). With it OFF: `spawn_batch Fire` beside cell 0, step 250 → no Fire ON tar cells (adjacent fire may burn out). With it ON: a twin run, step 2×250 → at least 1 Fire on a tar cell (`list_things` rect = the run). Serves the canal fire bars' state | ~750 | ON yields 0 / OFF yields fire |
| T3 | Viscosity: **not run.** O3 records `tar_fill_front_lags_water` UNBUILT (FlowPerPulse is fluid-independent) | 0 | — |

**Burn-out** (`canal_spent_after_burn`) and **fire persistence for a day** stay out of the
functional budget. A one-day wait is exactly the long run that invites nonsense. Once T2 is
green, they become a *keeper-save* item (§5) the owner fast-forwards himself.

### Budget total

| tier | ticks | wall (est.) |
|---|---|---|
| O offline | 0 | 5 s |
| L load + preflight | 0 | 40-60 s |
| S state | 4 | 25 s |
| E engine | ~6,500 (E7/E8 caps dominate; the oracle scenes are ~2,000) | 75-110 s |
| T tar (load + checks) | ~750 | 40-60 s |
| **total** | **~7,300 worst case (~3,000 typical, if E7/E8 finish early)** | **~3-5 min** |
| *old suite (measured 10-01)* | *112,921* | *21.4 min (J1bw #2); 35 min (first run)* |

## 4. Sanity probe and determinism

- **Sanity probe per instrument:**
  - L1 must find the RimBridge start line before an empty-error result counts.
  - S3 must classify W1 limitless before W4/W5's "limited" counts.
  - S7's "colonist stays" counts only if the hostile twin WAS captured.
  - E4's "unchanged while OFF" counts only if the ON half changed.
  - E9's "no imbalance" counts only if the expected `conservation exception` line was seen.
- **The offline checks can go red (measured this pass, on in-memory mutations; no file edited):**
  - O4 refuses an overlapping cell, an out-of-bounds cell, and a 40-cell edge body declared limitless;
  - O2 refuses a changed float default;
  - O5 is anchored to the live-measured oscillation vectors.

  The draft's `--offline` run returns exit 0. O1-O5 all PASS, and O3 reports 12 UNBUILT bars, none landed.
- **Determinism, three independent ways:**
  1. Twin scenes A/A′ in E2 must give equal vectors.
  2. Every live vector must equal the offline oracle, which is deterministic by construction (O5).
  3. A second full run on a fresh load of the same save must reproduce every recorded reading
     bit-for-bit. `--twice` writes both runs' readings to the summary and diffs them. A
     difference is a finding, a stop per debug_process rung 2.

## 5. What stays for a human: keeper saves, not screenshots

Only what a state read cannot show. The script ends by building ONE keeper save,
`NS_FlowWorks_Review_<date>`, on the water load, with a grid key in the run summary. Per the
owner's 2026-09-02 ruling, options he must look at ship as a savegame. The key's cells:

| grid cell | shows (owner bars) |
|---|---|
| K1 | dry D=1..4 ladder + undug: `pit_depth_ladder_legible`, `canal_reads_as_dug_channel`, `never_gravel_path`, `pit_reads_as_hole`, `pit_walls_have_visible_depth` |
| K2 | D=3 runs at F=0/1/2/3, plus D=1..4 at F=1, so both axes are staged correctly (INT found the old staging wrong): `fill_tier_legible`, `canal_partial_fill_distinct`, `depth_and_fill_jointly_legible` |
| K3 | 3×3 superdeep area with an occupant beside an empty twin: `pit_reads_at_size`, `pit_occupied_distinguishable`, `pit_occupant_below_floor` |
| K4 | a half-filled channel from W1 next to the drawn-down W2/W3: `canal_fill_spreads_along_itself`, `canal_reads_as_same_liquid_as_reservoir`, `reservoir_fill_visibly_drops` |
| K5 (tar save) | a lit tar run: `canal_burning_reads_as_burning_liquid`. He fast-forwards a day himself for `canal_fire_persists`/`canal_spent_after_burn` |

The 12 UNBUILT bars get no keeper cell. O3 tells the seat when each becomes stageable. The
judge/screenshot route (`shows=` + diptychs) is not dropped. It moves to a **separate
`--visual` pass** that reuses the same scenes, so the functional script is never gated on art.
`modcheck floor` keeps its 38/38 coverage by keeping `shows=` on the v2 scene components (see
the draft).

## 6. What each failure means (debug_process §3 classes)

| red at | first suspect | why |
|---|---|---|
| O1-O3 | MOD (def/code changed) or a stale script fact | pure source |
| O4-O6 | HARNESS | geometry, oracle, schema |
| L0, L5 | SITE (bad save, drifted world) | nothing of the mod has run yet |
| L1-L3 | MOD (load/def error) or deploy (L2 sha mismatch is DEPLOY, which is HARNESS-class) | |
| L4 | HARNESS/SITE (settings drift from an earlier run's unrestored `finally`) | |
| S1-S9 | MOD, unless its neg control also failed, in which case it is HARNESS (the instrument is blind) | zero ticks: no environment can intervene |
| E2-E6 | MOD if the oracle and the twin agree with each other but not with live. **HARNESS (oracle port wrong)** if live is internally consistent (A=A′, conservation holds) but ≠ oracle. Re-read the C# before blaming the mod | |
| E7/E8 timeout | **unresolved.** Poll the job identity and failure reason first. Then classify as SITE (colonist unable or unwilling: skills, drafted, needs, reservations) or MOD (WorkGiver/JobDriver) | pawn AI is the noisy part; a timeout alone is evidence of neither (GPT item 16) |
| E9 | MOD (a conservation leak is a bug by the code's own words) | |
| E10 | MOD (`ExposeData`) | |
| T0 | HARNESS/SITE (save not pristine) | |
| T2 | MOD, if O1 confirmed the tar terrain is flammable | |
| any surprise abort | SITE (a detector saw an event) | UNMEASURED, never FAIL |

## 7. Coverage map: old bar to v2

- **4 PROVES:** kept, as S1 and E2-ring.
- **15 VACUOUS:** replaced by S1/S2/S3/E2/E3 reads, or moved to keeper/visual.
- **7 WRONG:**
  - pathCost moves to O1/L3;
  - joint staging moves to K2;
  - fill-front moves to the E2 oracle;
  - recession moves to E3 `recededCount`;
  - the TrapSpikeArmed scan becomes O1 (holder `drawerType None`), with the RM_Ladder placeholder art filed as an ART note, not a pit failure;
  - the ladder moves to S9.
- **17 UNREACHABLE:** made reachable by R1-R3/R7 (S3, S7, S8, E2, E3, T1, T2), or registered UNBUILT (O3).
- **The 5 misattributed toggles:**
  - digToDepth moves to S6 (designator);
  - confinement stays on the legacy flood (§8 owed);
  - tankLoop moves to the bottle WorkGiver;
  - trapTrigger stays on the legacy building pit;
  - ladder moves to S9.
- **Wait-only toggles:** each becomes either a 0-tick setting-gate read where the gate is a WorkGiver/designator (a `designate_batch` acceptance, or a `HasJobOnThing` probe when a tool exists), or is listed **UNCOVERED: <why>** rather than pretending.

## 8. Owed tools and items (not built here; nothing in Source/ or bridgetools was edited)

1. `jawa/flowworks_excavation_rect {rect}`: D/F/sink/source for every cell in one call. It removes ~80% of calls (R10).
2. `jawa/flowworks_pulse {n}`: invoke `DoPulse` n times by reflection with **0 ticks**. With it, E2-E5 cost 0 game ticks. Refill and recession use `PulseIntervalTicks` as their dt, so it is exact.
3. `jawa/flowworks_pit_report {x,z}`: the holder's innerContainer, `EscapeBlocked`, `HasLadder`. It removes the "absent from list_pawns" proxy.
4. Legacy `Flood_FlowWorks`: MBT2/3/5 (temp terrain, `ExpiryTick`, confinement) via the existing `jawa/flowworks_spawn_flood`. Add it as tier F once the owner confirms the legacy release path still ships. It is reachable today but out of v2's first cut.
5. **Walk corrections (agent-owned sections only, never the hashed `## north star`):**
   - step 2 `floodTerrain` should be `RM_Fill_Water_Trace`;
   - MBT4 should replace `canal_dig` with `Deepen`/`DryTerrainFor`;
   - add the `→ chain.component` arrows.
6. `flowworks_shows_wiring_2026-10-01.md`'s "four components claim six bars" is **5 bars**. Correct it.

## 9. External advice

A research helper did this on 2026-10-02. WebFetch of github.com returned 503, so the upstream
files were read through raw.githubusercontent.com and api.github.com.

### 9a. RimBridgeServer's original author

The installed mod:
- path: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3727949765\About\About.xml`
- sanity probe: 1,410 About.xml files scanned, 1 hit
- version: RimBridgeServer **2.1.1**, `brrainz.rimbridgeserver`
- author: **Andreas Pardeike** (the author of Harmony), MIT licence
- repos: https://github.com/pardeike/RimBridgeServer · https://github.com/pardeike/GABP (protocol; conformance tests cover the protocol only) · https://github.com/pardeike/GABS

The workshop copy ships only README and LICENSE.

| advice (quoted or condensed, with source) | actionable for v2? |
|---|---|
| *"For the fastest state-inspection cycle, call `rimworld/start_debug_game_ready` or `rimworld/load_game_ready` with the default `mapData` readiness; use `readiness: "visual"` only when the next step needs visible UI or screenshots."* (`docs/rimworld-mod-debugging-stack.md`) | **YES**. L0 loads with `mapData`; only the `--visual` pass asks for `visual` |
| `rimworld/step_game_ticks`: *"Advance the paused game by an exact number of ticks, one tick per Unity update frame, mirroring Dev_TickOnce"* (README) | **YES, and it explains the cost model.** Stepping is frame-bound, so game time IS wall time. That is the strongest argument for R5, the 60-tick pulse pin, and for owed tool 2 (`flowworks_pulse`, which calls `DoPulse` with 0 ticks) |
| *"Use `ctx.Game.StepTicksAsync` for paused deterministic ticks … Avoid arbitrary sleeps."* (`skills/rimbridge-companion-tools/references/companion-dll-guide.md`) | YES. It matches R5 (exact pulse boundaries, never "wait and hope") |
| Whole test in one call: a companion `[Tool]` that spawns → `RunForTicksAsync(n)` → reads state → returns `{success, stage, error}` (README "Async orchestration example") | YES, for owed tools 1-3. Each scene can become one call |
| `rimbridge/run_script` / `run_lua` (a lowered Lua subset with `rb.call`/`rb.poll`) and `rimbridge/compile_lua` to dry-compile first (README) | **YES, a fallback for R10.** One S-tier block, ~120 calls today, can become one script call. Measure its overhead before relying on it |
| `rimbridge/list_logs`, an in-memory log journal (README; `docs/attention-policy.md`) | **YES**. L1 and E9 read it instead of scraping `Player.log` |
| `RimBridgeEvidenceManifest` / `RimBridgeEvidence.ToolSucceeded(...)`: a stable assertions + captures + errors + environment shape (README) | maybe. Our summary JSON already plays this role |
| Verify the active mod root with `rimworld/get_mod_configuration_status` and the bridge with `rimbridge/get_bridge_status` (companions.diagnostics) before live smoke testing (README/AGENTS.md) | YES, as L2's companion: prove the game loads the dir the build updated |
| README: RimBridge enables `TickManager.UltraSpeedBoost` at startup | context for the 33-416 ticks/s spread. Not acted on |
| No published guidance on minimizing ticks beyond StepTicks | n/a |

### 9b. Web: automated RimWorld mod testing

| source | what | actionable? |
|---|---|---|
| https://github.com/RimWorks/Rimworld-Quickstarts | assertions, a log-error **budget** (`failOnLogError`/`allowedLogErrors`/`ignoredLogErrors`), a watchdog, and JSON/JUnit reports. *"A run also fails when the game logs a red error, even if every assertion holds"* | **YES**. Adopt the log-error budget as L1/E9: any red FlowWorks line fails a run whose state reads are all green |
| https://github.com/mushroomTW/rimworld-mod-mcp | an isolated `-savedatafolder` session; *every Log.Error/Warning deduplicated with occurrence counts*; state polled ~1/s instead of fixed waits | YES. Dedup-with-counts goes in the L1/E9 summary. Polling for "done" is E7/E8's step-until |
| https://rimworldwiki.com/wiki/Modding_Tutorials/Testing_mods | `-quicktest`, `-savedatafolder=<dir>`, `autostart.rws` (load a save at boot, no clicks) | YES, as an option. `autostart.rws` = NS_FlowWorks_Bland_v2 would remove the menu path from L0. Not adopted yet because RimBridge's `load_game_ready` already does it |
| https://github.com/ShugokiFable/RimWorldForge | offline def/patch/texture validation, and decoding Unity `[Ref XXXX] Duplicate stacktrace` storms | YES, for tier O and for reading the first exception |
| https://github.com/RimWorks/Rimworld-Pickle | Gherkin scenarios in a live session, with an "I wait X ticks" step | partly. A vocabulary template only |
| https://github.com/SakuraIsayeki/RimTest (and workshop 2199316917) | in-game C# unit tests | maybe, for the pure engine math (`RM_StockMath`). We already selftest it offline (`Source/SelfTest`). Unverified |
| https://github.com/krafs/RimCI | GH Actions build; tests commented out because there is no headless RimWorld | NO. It confirms that runtime checks need the real game |
| https://github.com/inten-gg/rimworld-ci | CI build plus an XML lint | no (build only) |
| Autotester (workshop 3497629017); botto854 rimworld-modding-skill; RimWorld-Auto-Documentation; HugsLib log publisher | snippets only, not fetched | unknown / marginal |

**Cross-cutting.** Nobody publishes a tick-minimizing method. The shared pattern is:
- offline static checks first;
- one boot into a fixed scenario;
- state plus a log-error budget;
- ticks only inside the assertion step;
- a watchdog and a machine-readable report.

v2 already has that shape. **What v2 takes from outside:**
- the log-error budget;
- deduplicated error counts;
- `mapData` readiness;
- one-call scene tools (`run_lua` or companion `[Tool]`s);
- treating step_game_ticks as frame-bound.

## 10. GPT's recommendation vs mine

- **Model:** `gpt-6.1-sol` at effort `ultra`, the highest in the local `models_cache.json`, via `gpt_consult.py`.
- **Answer:** `design/RimMandrake/flowworks_northstar_gpt_2026-10-02.md`.
- **How it was tested:** every claim I could check offline, I checked with the port in `validation_v2_DRAFT.py` (`PulseOracle`) or against source before adopting it.

| # | GPT point | test I ran | decision |
|---|---|---|---|
| 1 | Run transitions through the **loaded C# pulse** (reflection), and keep a short scheduled replay | none possible offline | **ADOPT** as owed tool 2 (§8). It is now the first item to build. A short real-scheduler replay stays (E1 cadence plus one E2 replay), so reflection never fully replaces ticking |
| 2 | S7 accepted `cap is None`, which is a false pass | read the draft: true | **ADOPT, fixed in the draft.** It now needs the row present, `spawned False` and `dead False`. Holder membership waits on owed tool 3 |
| 3 | The south 4-cell control fills at pulse **7**, so the draft's 6-pulse check would fail its own control. A 6-cell channel needs 11 pulses, not "≤ 8" | port: south-4 first full at 7; south-6 at 11 | **ADOPT.** Draft E2 now runs 8 pulses, and the INT §2 claim is corrected. The smaller discriminator (two 1-cell interior sources, 3-cell east vs west channels, 5 pulses) is **ADOPTED** for the live first run. W1's 64-cell edge body is still needed for S3's limitless check |
| 4 | Old `sourceBudget` ON is vacuous: the 30-cell east channel saturates at 16 and the budget of 20 never binds | port: 16 wet, stock 4 | **ADOPT.** INT §3b moved it from PROVES to VACUOUS (toggle tally now 4/16/5/1/1) |
| 5 | In E3, a spent 1-cell pond recedes, so budget-OFF cannot supply again | source: recession dries the cell, after which `IsSourceCell` is false | **ADOPT.** The draft pins recession OFF for E3's accounting, and recession gets its own scene. Also adopted: E3 uses short multi-outlet geometry (4 separated D=2 recipients) to exhaust in ~2 pulses, not 14 |
| 6 | The draft's E2 claims confinement without reading the surrounding ground, and the old `canal_holds_only_channel` ring included a source cell | the audit had already found this for `confinement_on`; same code path | **ADOPT.** The ring read excludes the authored body footprint. Downgrade `canal_holds_only_channel` from PROVES to "PROVES once fixed". I keep my tally, because the bar verdict is about intent; the ring defect is listed as a WRONG detail in §3a |
| 7 | `PickDonor` lets a non-brimming donor give to a **deeper** recipient, which differs from my prose ("donor deeper or brimming") | C# comment l.958-972 is GRAVITY: a neighbour gives to a deeper cell | **ADOPT.** That was a prose error (corrected in INT §2). The port matches the C#. A two-cell mixed-depth case goes into O5 |
| 8 | An UNBUILT regex flip must never PASS a visual bar | read the draft: `chain_unbuilt` would have passed | **ADOPT, fixed.** It always fails, with either the UNBUILT fact or "FEATURE LANDED: stage a scene" |
| 9 | `fill_fluid_distinct` is not proven UNBUILT by one `activeFluid` field. `allowAfterClassification` keeps old fill terrain on old cells, so two fluids might be *stageable* visually | tool doc: existing fill terrain keeps the old fluid until its next fill write | **PARTIAL ADOPT.** As a visual scene it may be stageable on the tar load (fill one run, switch the fluid with allow=true, fill a fresh run). Its terrain would drift back on the next pulse that touches the old cells. Moved to the keeper-save list (K5) with that caveat. The functional engine still has one fluid per map |
| 10 | Cut the automatic `--twice`, the duplicate east twin, the per-run keeper, and setter-only toggles. Report the setter-only toggles as UNCOVERED | n/a | **ADOPT**, except one: determinism stays as a *canonical-state* comparison (ordered D/F, stock deltas, holder relations) on a later rerun, never a default double run |
| 11 | Tighter budget: **~300-800 non-job ticks plus two measured jobs (≈1,000-2,000 total)**; derive job caps from the work amount, not arbitrary numbers | none (needs live) | **ADOPT as the target**, contingent on owed tool 2. Without it my ~3,000-7,300 stands. E7/E8 caps are derived from the JobDriver work amount plus the approach distance at preflight |
| 12 | E6: `RainRate>0.01` does not guarantee 1 level in 2 pulses. Read rate and roof after the interval too | source: accumulator += RainRate × rainFillPerPulse | **ADOPT.** Predict pulses = ceil(1/(rate×1.0)) from the measured rate, and re-read the roof and rate afterwards |
| 13 | Extra interference sources: Anomaly mode (set Disabled), the storyteller/quest producers, Odyssey terrain layers and ice, worker identity (titles, roles, age, genes), residual designations and reservations, harness feeding as an intervention | none | **ADOPT all** into §2's pin table at build time. The save builder records storyteller, Anomaly mode, worker roster and DLC identity in the sidecar |
| 14 | Save/load should include a **captured occupant**; add a real fill-in to D=0 with terrain and holder cleanup; and MBT2/3/5 legacy flood if it ships | source: `FillIn` to D=0 restores the original terrain and removes the holder | **ADOPT** E10 occupant + fill-in-to-0. The legacy flood stays §8 item 4 (an owner question: does the legacy release path still ship?) |
| 15 | Irrigation still has *functional* claims even with no visual bar | grep `irrig` in `Source/`: not checked this pass | **DEFER, UNMEASURED.** Filed as a question for the next pass. If no yield code exists, it is UNCOVERED with reason "unbuilt" |
| 16 | "A timeout is not automatically SITE" | — | **ADOPT.** §6's E7/E8 row now reads "unresolved; poll job identity and failure reason before classifying" |

**Where GPT and I disagree:**
- **(a)** It prefers labelling staging read-backs "state/driver contract" rather than VACUOUS. I keep VACUOUS *for the bar*, because the bar claims player-visible behaviour. I accept that they are valid driver-contract checks, and v2's S1/S2 keep them as exactly that.
- **(b)** It would cut regex UNBUILT proofs from acceptance entirely. I keep the register, because it is the zero-tick signal that a bar has become stageable, but it can never pass (item 8).
- **(c)** It doubts that "east/north never fills" holds generally. Agreed, and qualified: channels of **length ≥ 3** running index-ascending from a single inlet, initially dry. Lengths 1-2 fill (port confirms).

**Net effect on the headline:**
- The MOD defect claim stands. GPT's hand trace matches the port, and the port reproduced the live vectors.
- The script's target budget drops to **~1,000-2,000 ticks** once `jawa/flowworks_pulse` exists, from ~3,000-7,300 without it, against **112,921** for the old suite.
