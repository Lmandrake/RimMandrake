# FlowWorks north-star trial plan

**Subject:** `src/RimMandrake/FlowWorks` (packageId `mandrake.rm.flowworks`) — canals, the depth/fill
primitive, liquid stock, superdeep pits (Pits merged in at `cade628c1`), the liquids registry.
**Commissioned by the owner, 2026-09-30 (typed):** *"Write out comprehensive northatar plans for all
three and ticket them out as trials for full completion. Use gpt reviews for their validation plan
especially site preparation that's often overlooked before a proper test setup. I'd like this to go
very well. Then use ultra fast python to drive the bridge to validate. Make it happen!"*
**Parent item:** `FLOWWORKS_NORTHSTAR_TRIAL_1` (FOUNDRY). Rung items are listed in §8.
**Written offline 2026-09-30 by a BENCH design subagent. Nothing here touched the live game, the
bridge or `ModsConfig.xml`.** Every number carries MEASURED (read this session, with the instrument
named) or UNMEASURED.

The ladder every trial climbs:
**DRAFT → VALIDATED** (owner's word) **→ WIRED** (every bar has `shows=`) **→ GREEN-minimal → GREEN-full
→ SHIPPED** (deployed, Mod Settings superb per the 2026-09-12 ruling, art complete, code review CLEAN).

---

## 1. Current state, rung by rung

| rung | state | evidence |
|---|---|---|
| DRAFT → VALIDATED | **VALIDATED 2026-10-01 — 38 must-show + 5 cannot-show**, pit bars included | Re-validated on his typed word *"Again write the comprehensive one and have gpt review it"* after the GPT checklist review (§9b). The 13+3 / 0-pit-bar state this row used to describe is gone. |
| Pits walk | **deleted 2026-10-01** | Its still-valid bars were rewritten and folded into FlowWorks.md (§2.4); `modcheck forget-key Pits` run. |
| STALE | The stored `GREEN` is from run `FluidCanals@1789295363` — a pre-north-star, pre-rename, pre-ruling-24 run against a deleted comp. It certifies nothing about today's mod. | MEASURED: `infrastructure/state/modcheck_status.json` `FlowWorks.run_id`, `renamed_from: FluidCanals`. |
| VALIDATED → WIRED | **0 of 38 must-show lines claimed** (no `shows=` in `validation.py`). | MEASURED 2026-10-01 by `northstar.parse`; the earlier 13-line `floor` reading predates the re-validation. |
| validation.py | 🔴 **`src/RimMandrake/FlowWorks/validation.py` is the old Pits suite moved in unchanged**: docstring says "suite for RimMandrake Pits (mandrake.rm.pits)", `suite = Suite("Pits")`, toggles are `PitsSettings`' four, both chains drive the BUILDING pit (`RM_OpenPit_Bare`). **No canal, depth, fill, stock or superdeep component exists.** | MEASURED (read file, 133 lines). |
| Mod Settings toggle floor | FlowWorks ships **27 boolean toggles** (22 in `RimMandrakeFlowWorksSettings`, 4 in `PitsSettings`, 1 in `RiverSteamSettings`) plus 18 numeric tunables. The suite declares 4. | MEASURED (grep of `public static bool` in the three settings classes). |
| GREEN-minimal / GREEN-full | **Never run against the current mod.** | MEASURED (status store). |
| Deploy | `deploy_custom_mods.py --mod FlowWorks` (dry run, from origin/main worktree): `in sync (68 files)`. Deployed `RimMandrakeFlowWorks.dll` and `.srchash` byte-identical to repo (sha1 `ca7e954fd522…` / `98c569bdb880…`). | MEASURED 2026-09-30. Re-measure at run time — this decays. |
| 🔴 Stale **Pits** mod still deployed | **Off the live list since 2026-09-30 23:58** (backup `infrastructure/state/modlists/ModsConfig_before_pits_off_2026-09-30T235855.xml`); the game folder `Mods/Pits/` is still on disk and `ModsConfig.FULL.LATEST.xml` still lists `mandrake.rm.pits`. Its 22 defNames all collide with FlowWorks'. | MEASURED 2026-10-01: parsed live `ModsConfig.xml` (611 active, no `mandrake.rm.pits`); parsed FULL.LATEST (612, contains it); `Mods/Pits/` present. Remaining work: `PITS_STALE_DEPLOY_COLLISION_1`. |
| Code review | **117 CLEAN / 12 DIRTY** of 129 tracked `.cs/.py/.xml` under `src/RimMandrake/FlowWorks`. DIRTY: `RM_LiquidDrill.xml`, `RM_LiquidBodyRegistry.xml`, `RM_Propane.xml`, `RM_TarGlass.xml`, `RM_WaterBoiling.xml`, `RM_LiquidTank.xml`, `RM_DeepSand.xml`, `RM_LiquidShores_MapGenPatch.xml`, `RM_LiquidBodyDef.cs`, `RM_NoRecreationalSwimExtension.cs`, `RM_Patch_NoRecreationalSandSwim.cs`, `Tools/generate_liquid_suite.py`. | MEASURED: `code_review_status.py check` over `git ls-files`. |
| Art | **7 textures ship** (tank, 3 tar filth, barrel, bottle, bucket). Every channel depth (`RM_Channel_Empty/Mid/Deep/Superdeep`) borrows `Terrain/Surfaces/Gravel`; fills borrow vanilla water ramps tinted; **3 pit defs still point at `Things/Building/Security/TrapSpikeArmed`**. | MEASURED (find + grep of `texturePath`/`TrapSpikeArmed`). |

**Ruled vs built for the features the bars cover** (MEASURED by grep of `Source/` and `Defs/` unless marked):

| feature | ruled | built? |
|---|---|---|
| Depth/fill primitive, pulse flow, confinement | yes | **yes** — `RM_MapComponent_Excavation`, pulse every `pulseIntervalTicks` = 250, `flowPerPulse` = 1 |
| Stock, limited/limitless (sticky), recession, refill, rain fill (roof blocks it), edge sinks | yes | **yes** — `RM_LiquidStock`, `RM_LiquidBody`; a body is classified ONCE on first contact and never re-argued |
| Per-fluid viscosity in the depth engine | yes ("water almost at once, tar creeping") | **no** — `RM_MapComponent_Excavation` has no viscosity/`ticksPerTile` read; viscosity exists only on the legacy `Flood_FlowWorks` release |
| Per-body fluid type | yes (item `[F]`) | **no** — `ActiveFluid` is ONE `FluidDef` per map, defaulting to water, with no UI; the bridge setter `jawa/flowworks_set_active_fluid` changes the whole map's fluid, never one body's |
| Ignition / burning canals | yes | partial — `LiquidIgnition.cs` exists; `liquidIgnitionEnabled` **defaults false**, so the defense bars test a non-default setting |
| Superdeep capture, ladder | yes | **yes** — `Building_SuperdeepPit` (inherits `Building_OpenPit` despawn-into-container), `RM_Ladder` |
| Pawn draw offset by depth, walls 20% over head | yes (third card round) | **no** |
| Superdeep cover (terrain-mimic) | yes | building-pit only (`Building_TerrainMimicCover`) |
| Sluice / SecurityGrateDoor | yes (`FLOWWORKS_DOOR_FAMILY_1`) | **no** — zero hits for `Sluice`/`SecurityGrate` |
| Per-cell spikes | yes | building-pit fitting only (`RM_OpenPit_Spiked`) |
| Bespoke channel / pit / fill art | yes (rulings 19, 33) | **no** |

⇒ **Honest expectation:** WIRED is reachable now. GREEN is not: about two-thirds of the bars are
expected to come back NO from the judge until art and the unbuilt mechanics above land. That RED
run is still worth having — it is the first live proof that the visual floor catches a mod whose
state assertions pass (`north_star_validation_spec.md` §9's falsification test).

---

## 2. Bars and their bindings

### 2.1 How a bar binds today (MEASURED from `src/RimMandrake/Utils/modcheck/`)

- A bar is claimed by a component in `validation.py`: `with t.component("<name>", toggle=…, shows=["<bar_id>"]):`.
- The **judge** (`judge.py`) grades **only the LAST screenshot** the component captured, by
  `claude -p` vision, YES/NO/UNJUDGEABLE. A must-show passes on YES; a cannot-show passes on NO.
  A claimed bar with no screenshot is UNJUDGEABLE = fail.
- The **state half** is every `expect_*` inside the component. GREEN needs both halves AND the
  owner's one review of the sheet (`status.verdict_for`).
- `t.screenshot()` today: `jawa/clear_ui` → `rimworld/jump_camera_to_cell(anchor)` →
  `rimworld/take_screenshot`. **It frames the suite ANCHOR, not the cells under test, and sets no
  zoom.** Every bar below that says "at play zoom" or "at max zoom" therefore needs the driver's
  framed-shot call (§6), or the judge is looking at the wrong thing.
- ⚠️ **Three bars are declared `(change)`** — `canal_fill_front_watchable`,
  `reservoir_fill_visibly_drops`, `never_full_reservoir_after_heavy_draw` — and are judgeable only
  from TWO frames. The judge sees one. Resolution adopted here, so the judge stays unchanged: **the
  driver composes a labelled before|after diptych into one PNG** and the component's last screenshot
  is that diptych. Judge prompt text stays the bar text.

### 2.2 Conventions used in every binding

- **Plot** — every bar owns a disjoint rectangle on the trial map (§3.4). Coordinates are plot-relative
  `(px, pz)`; the driver adds the plot origin.
- **Dig** — `jawa/flowworks_excavation_drive {x,z,deepenLevels:N,setFill:-1}` (calls the engine's own
  `Deepen()`; LAW 1 clamps). **Fill** — same tool with `deepenLevels:0, setFill:F` (calls
  `TrySetDriverFill`, clamped 0≤F≤D). **Read** — `jawa/flowworks_excavation_report {x,z}` (D, F,
  isExcavated, isSourceCell, isSinkCell, sink/overflow totals, ticksGame) and
  `jawa/canal_cell_report {x,z}` (terrain, tempTerrain, underneath, things).
  ⚠️ Both `flowworks_excavation_*` tools exist in `JawaBenchFlowWorksTools.cs` but are **absent from
  `Transient/bench_tools_dump.json` (dumped 2026-09-08, before they were written)** — their live
  registration is UNMEASURED and is the preflight's first bridge check (§3.9 P-B3).
  `jawa/canal_dig` is a **stub that always fails** (ruling 24) and must never be called.
- **Reservoir** — a natural liquid body: base terrain with `IsWater`, depth grid 0 (`IsSourceCell`).
  Painted with `jawa/set_terrain_batch` **before** any excavation touches it, because classification
  happens once on first contact. **Limitless** = touches the map edge AND ≥ `minLimitlessBodyCells`
  (50); **limited** = a pond inside the map.
- **Settle** (liquids are time-dependent): step in whole pulses. `PULSE = PulseIntervalTicks` read
  back from settings (default 250, clamped ≥ 60). **Pulse phase is read, never inferred** — the driver
  reads the component's `nextPulseTick` (reflection; new tool, §6) and steps to it exactly, so "pulse 1"
  means the same tick every run (GPT #21). A plot is **settled** when, across **3 consecutive pulse
  boundaries** (750 ticks at default), ALL of these are unchanged: the F vector over the plot's
  excavated cells, the plot body's stock, `sinkTransferredTotal`, `overflowDestroyedTotal`, and the
  rain accumulator (GPT #36 — constant F with a rising sink total is a flowing state, not a settled one).
  For that reason **every stock bar switches OFF the stock modifiers it is not about** (`refillEnabled`,
  `rainFillsExcavationsEnabled`, `edgeSinksEnabled`, and `recessionEnabled` except in the recession
  bar) and restores them in `finally`. **Budget** per bar is stated; exceeding it is FAIL with reason
  `NOT_SETTLED`, never a pass. Every step is `rimworld/step_game_ticks` from a paused game, and the
  driver asserts after each one: start/end tick, exact delta, still paused, no long event pending, same
  map id, pulse count advanced as expected (GPT #22).
- **Conservation ledger** (stock bars): Σ(ΔF over plot cells) × `volumePerTile` = −Δ(body stock)
  − Δ`sinkTransferredTotal` − Δ`overflowDestroyedTotal` + Σ(driver `setFill` injections) + refill +
  rain + displacement − burn, each term read or logged, the disabled ones asserted 0, within ±1 unit
  (GPT #37).
- **Shot** — `driver.shot(plot, cells, zoom="play"|"max", hide_labels=True)`: clear selection + UI,
  freeze the engine (`depthEngineEnabled=false`, read back) and advance **forward** to the next noon
  (never set the clock backwards — GPT #20), frame the cell rect with a 3-cell margin, set the recorded
  zoom, capture via `rimworld/screenshot_cell_rect` (fallback `rimworld/take_screenshot`, then
  `system_screenshot.py`), restore the engine. The PNG is accepted only if: its mtime is after the
  call, its hash is new, its dimensions match the pinned resolution, it passes the luma/variance gate,
  and the call returned the expected map id / tick / camera rect (GPT #28). The accepted path is
  **nominated** as the bar's evidence and its hash recorded in the result — diagnostics and
  calibration shots are written outside the component so they can never become "the last screenshot"
  the judge reads (GPT #29).
- **Cannot-show scope** — a cannot-show bar is judged on the staged footprint + buffer only and is
  always paired with an exhaustive state scan of that same rect (e.g. `never_liquid_on_open_ground`:
  every un-dug cell in footprint+buffer has F=0, tempTerrain none). A crop cannot prove "never"
  map-wide, and the plan does not claim it does (GPT #33).
- **Judge rubric** — each visual component passes the judge a positive and a negative reference
  image where one exists (e.g. the Gravel road as the negative for `canal_reads_as_dug_channel`),
  and any UNCERTAIN/borderline verdict is routed to the owner's sheet review rather than retried
  until it says YES (GPT #32; the owner's one review is already a GREEN requirement).

### 2.3 The canal bars (13 must + 3 cannot, VALIDATED, ids frozen)

| bar | asserts | setup → state predicates (state half) | shot | live/offline | expected today |
|---|---|---|---|---|---|
| `canal_reads_as_dug_channel` | dug channel reads as excavated ground with walls | Plot A: dig a 1×8 run at D=1 on Soil. Expect report `D=1`, `isExcavated=true`, terrain `RM_Channel_Empty`, F=0. | play zoom, run + 3-cell margin | live | **NO** (Gravel texture) |
| `canal_dry_reads_as_obstacle` | unfilled channel legible as impeding crossing | Same plot as above (shared component allowed: one shot, two `shows`). State: the effective `pathCost` of a D=1 dry cell **equals the ruled 30** (build program Phase 5) — not merely "more than soil" (GPT #34) — plus a timed traversal: a colonist ordered across 8 dug cells takes measurably longer than across 8 soil cells. Expected FAIL today (shipped 6). | same shot | live + `[D]` def read | NO |
| `canal_partial_fill_distinct` | partly filled vs full distinguishable | Plot B: two parallel 1×6 runs at D=3; fill run 1 to F=1, run 2 to F=3 via `setFill`; set `depthEngineEnabled=false` **for this component only** so the pulse cannot equalise them, read back F per cell, restore setting after. | play zoom, both runs in frame | live | NO/UNCERTAIN (tinted ramps may differ) |
| `canal_fill_spreads_along_itself` | liquid spreads through the channel, not pooled at entry | Plot C: limitless reservoir strip on the map edge; dig a 1×10 D=1 channel from it. Step pulses until settled (budget 20 pulses = 5,000 ticks). Predicate: mouth cell F≥1, every channel cell F≥1, no dry gap between wet cells, and settled inside budget — the old "monotone" fallback is struck because an all-dry channel satisfies it (GPT #35). The source is limitless, so no budget can legitimately run out. | play zoom, after settle | live | state PASS; visual UNCERTAIN |
| `canal_fill_front_watchable` (change) | visible fill front; water near-instant, tar creeping | Plot C, frames at pulse 1 and pulse 3 → diptych. For the tar half: a four-panel composite water/tar × pulse 1/pulse 3 from two working copies of the golden save with identical geometry, `ActiveFluid` set and verified **before first classification**, plus a machine-checked state delta: tar's wet front at pulse 3 is strictly shorter than water's (GPT #31). | diptych | live | **BLOCKED** — depth engine has no viscosity (MEASURED), so tar fills at water's rate; expected NO |
| `canal_holds_only_the_channel` | liquid inside the channel, not on open ground beside it | Plot C after settle. Predicate: every cell in the 1-cell ring around the channel has `D=0`, `tempTerrain=none`, terrain unchanged from the pre-dig snapshot. Toggle `channelConfinementEnabled` (default true). | play zoom | live | state PASS expected (MEASURED built) |
| `canal_reads_as_same_liquid_as_reservoir` | filled canal reads as the same substance as its body | Plot C after settle, reservoir + mouth + channel in one frame. | play zoom | live | UNCERTAIN |
| `reservoir_fill_visibly_drops` (change) | reservoir visibly less full after supplying; small pond shrinks at far edge | Plot D: **limited** pond, 5×5 natural `WaterShallow`, ≥10 cells from every edge and every other plot. Snapshot body stock + pond cells. Dig a 1×12 D=3 channel from it; step until settled (budget 40 pulses). Predicates: stock decreased by Σ F × volumePerTile (conservation ±1); `recessionEnabled` → ≥1 pond cell now dry (`underneath` = original, `isSourceCell=false`). Frames before/after → diptych. | diptych | live | state PASS likely; visual NO (no reduced-pond art) |
| `canal_burning_reads_as_burning_liquid` | lit flammable canal reads as liquid surface alight | Plot E on a **fresh working copy** with `ActiveFluid=RM_Fluid_Tar` set before first classification, `liquidIgnitionEnabled=true` (non-default). Fill 1×8 D=1 channel from a limited tar pond; ignite the mouth cell (driver: `ignite_cell`). Poll every 60 ticks up to 1,200. Predicate: the recorded ignited-cell set grows to ≥3 channel cells, N=3 repetitions with distinct ignition cells, pass on 3/3 (GPT #39). Which cells are *eligible* to hold Fire (channel fill terrain vs natural pond terrain) is read from `LiquidIgnition.cs` before wiring, not assumed. Fire-safety isolation: 8-cell non-flammable (bare Soil, plants wiped) moat round the plot; `jawa/clear_area` of plants first. | play zoom | live | UNCERTAIN (ignition premise UNMEASURED — build program Phase 6 flags `About.xml`'s "vanilla ignition already works" as unverified prose) |
| `canal_fire_reaches_reservoir` | fire present at the reservoir, not only the channel | Plot E continued, poll until a reservoir cell has Fire (budget 6,000 ticks), 3/3. | play zoom incl. pond | live | UNCERTAIN |
| `canal_spent_after_burn` | burned-out channel reads scorched and empty, not merely dry | Plot E, poll until no Fire in plot (budget 60,000 ticks — burn is "one canal tier per day"). "Burned cell" = a cell in the recorded ignited set. Predicate: every burned cell F=0 and still excavated (D unchanged). | play zoom | live | NO (no third channel state art) |
| `slime_reads_as_viscous_not_water` | slime opaque and viscous, never tinted water | Plot F, fresh working copy, `ActiveFluid=RM_Fluid_SlimeGreen` set and read back before any fill, fill terrain asserted to be the slime fill def (not the water ramp) after a forced redraw (GPT #38), then fill a 1×6 D=1 channel by `setFill`. Water control channel would need a second fluid on the same map — impossible today; the control is a stored reference PNG of the water fill from Plot C. | play zoom | live | UNCERTAIN |
| `slime_occupant_below_surface` | pawn in a slime canal not drawn standing on the surface | Plot F, D=3 slime run; spawn a colonist ADJACENT and order it into the middle cell so it makes a real cell transition (no teleport — GPT #24); step ≤300 ticks; predicate pawn position is in the run. | play zoom, pawn centred | live | **NO** (no depth draw offset) |
| `never_liquid_on_open_ground` (cannot) | no liquid standing on undug ground | Claimed by the Plot C component (photographing exactly where the defect would appear). | same as Plot C | live | PASS expected |
| `never_gravel_path` (cannot) | channel never reads as a gravel road | Claimed by Plot A. | Plot A shot | live | **FAIL expected** (it IS Gravel) |
| `never_full_reservoir_after_heavy_draw` (change, cannot) | reservoir fill never looks untouched after a long canal | Plot D diptych. | diptych | live | FAIL likely (no reduced art) |

### 2.4 The pit bars — the Pits-walk fold

🔴 **Do not move the 11+1 Pits bars as they stand** (`PIT_SUPERDEEP_COLLAPSE_1`, the item is
authority over the spec): several are claims about a Building, and the pit is now a SUPERDEEP cell.
The item records his third-card-round rulings, which change the roster. What goes to him for
re-validation, as **proposed text** (§7) inside FlowWorks.md's `## north star` under a new
`**The pit — a superdeep excavation**` group:

| proposed id | source | binding | expected today |
|---|---|---|---|
| `pit_reads_as_hole` | kept, re-subjected ("approved in substance") | Plot G: dig a 3×3 D=4 area; shot at play zoom, labels hidden | NO (Gravel) |
| `pit_not_vanilla_trap` | rewritten — drop "own texture path", keep the claim | Plot G shot; plus `[D]` offline: no FlowWorks def `texPath` = `Things/Building/Security/TrapSpikeArmed` (today 3 → FAIL) | FAIL |
| `pit_reads_at_size` | kept, strengthened (flag to him) | Plot G | NO |
| `pit_depth_ladder_legible` | 🆕 approved + strengthened by his depth ruling | Plot H: five adjacent 2×3 pads at D=0..4 in one row; then a colonist walked across all five with `superdeepCaptureEnabled=false` for this component only, so it is not captured on D=4 before the frame (GPT #25); frames at D=1 and D=4 → diptych for "rises and lowers". Capture is tested separately in Plot G at defaults. | **NO** (one Gravel texture for every depth; no draw offset) |
| `pit_occupant_below_floor` | kept; absorbs `pitcell_occupant_visible` (merge, flag) | Plot G: hostile-faction pawn spawned 3 cells off the lip and force-moved across it (a real cell transition — placing a pawn ON the cell may bypass the entry detector, GPT #24); predicate superdeep capture (`superdeepCaptureEnabled`) — pawn despawned into the hidden `RM_SuperdeepPit` holder. Ruling: superdeep traps *absolutely*, so the threshold is **3/3** over three spawns, never "most" | NO |
| `pit_occupied_distinguishable` | kept | Plot G occupied vs Plot G′ empty in one frame | NO |
| `pit_trapped_reads_as_trapped` | 🆕 approved, worded against the walls | Plot G occupied | NO |
| `pit_covered_invisible` / `pit_covered_seam_at_max_zoom` | kept | **BLOCKED** — no superdeep cover exists | UNJUDGEABLE until built |
| `ladder_state_legible` | rehoused from `pitcell_gate_state_legible` (split, flag) | Plot G with/without `RM_Ladder` | UNCERTAIN |
| `sluice_gate_state_legible` | rehoused (split, flag) | **BLOCKED** — `FLOWWORKS_DOOR_FAMILY_1` unbuilt | — |
| `fill_tier_legible` | 🆕 approved — strengthens `canal_partial_fill_distinct` (4 states vs 2) | Plot B extended to four runs F=0..3 at D=3 | NO/UNCERTAIN |
| `fill_fluid_distinct` | 🆕 approved — generalises `slime_reads_as_viscous_not_water` | **BLOCKED** — fluid is per-MAP today; the bar compares two fluids side by side, which cannot be staged on one map | — |
| `spikes_read_distinct` | 🆕 approved, with his camera constraint | **BLOCKED** — per-cell spikes unbuilt | — |
| `never_snared_standing` (cannot) | kept verbatim | Plot G occupied shot | FAIL likely |
| `never_reads_as_building` (cannot) | 🆕 approved | Plot G | FAIL likely while 3 defs use TrapSpikeArmed |

**Deleted, not carried:** `digsite_stage_legible` (its referent, the `RM_PitDigSite_*` chain, retires).
`fitting_reads_distinct` splits into `fill_fluid_distinct` + `spikes_read_distinct`.

✅ **Ruled 2026-10-01 — comprehensive:** the BLOCKED rows are bound, not parked. A bar for an
unbuilt feature fails until the feature is built, which is the bar doing its job. The validated
section (FlowWorks.md) also reworded several bars and added ten after the GPT review — §9b is the
list; bind against the walk file, not the ids in this table.

### 2.5 State-only components (no `shows`), needed for the toggle floor

The floor refuses a run while any Mod Settings toggle has no covering component. 27 toggles,
MEASURED. Each gets one component, toggle named, with a positive predicate (on) and — where the
setting can flip live via `jawa/mod_settings_field` (static fields, `RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings`
/ `RimMandrake.FlowWorks.Pits.PitsSettings` / `…ManyWaters.RiverSteamSettings`) — a negative
predicate (off). Grouped:

Each row is executable: ON = shipped default, OFF = flipped for that component and restored in
`finally`. A component that merely declares `toggle=` with no predicate is a floor cheat and is
refused in review (GPT #15). Ticks are budgets; every check reads state through the driver, never
the setter's echo.

| toggle (default) | plot / setup | ON predicate | OFF predicate | ticks |
|---|---|---|---|---|
| `depthEngineEnabled` (T) | limitless body + 1×6 D=1 channel | F rises at mouth within 2 pulses | F vector identical over 4 pulses | 1,000 |
| `channelConfinementEnabled` (T) | Plot C ring | ring cells F=0, tempTerrain none after settle | (OFF = old leak behaviour) ≥1 ring cell gets liquid — proves the toggle is live | 5,000 |
| `digToDepthEnabled` (T) | one cell, `dig(levels=3)` | D=3 | D clamps to 1 (or digging refuses past shallow — read the code before wiring) | 0 |
| `edgeSinksEnabled` (T) | channel from a limited pond to the map edge | `sinkTransferredTotal` rises; pond stock falls by the same amount (ledger) | sink total unchanged | 5,000 |
| `fillInEnabled` (T) | filled D=1 cell, fill-in designation, colonist | cell D=0, original terrain restored | designation refused | 2,500 |
| `fillInDisplacementEnabled` (T) | as above, with wet neighbours | Σ F conserved (liquid moved, not deleted) | liquid deleted: ledger shows the loss | 2,500 |
| `sourceBudgetEnabled` (T) | limited 2×2 pond, 30-cell channel | channel stops at 5 × 4 × multiplier cells | channel keeps filling past that | 10,000 |
| `stickyLimitlessEnabled` (T) | edge body ≥80 cells, draw it down by recession | `limitless` stays true | reclassifies | 5,000 |
| `recessionEnabled` (T) | limited pond drawn from | ≥1 far-edge pond cell dries, `underneath` restored | no pond cell dries | 10,000 |
| `refillEnabled` (T) | limited pond partly drawn, no draw after | stock rises over 20 pulses | stock flat | 5,000 |
| `rainFillsExcavationsEnabled` (T) | two D=1 cells, one roofed, forced rain | unroofed F rises, roofed F=0 | both F=0 | 5,000 |
| `liquidIgnitionEnabled` (F) | Plot E | ignition spreads (§2.3) | ignite call produces no liquid fire | 1,200 |
| `liquidCorrosionEnabled` (F) | corrosive fluid fill under a steel wall/item (read `LiquidCorrosion.cs` for the contract first) | HP falls | HP unchanged | 2,500 |
| `superdeepCaptureEnabled` (T) | Plot G | hostile captured 3/3 | hostile crosses 3/3 | 600 |
| `superdeepCapturesOwnFaction` (F) | Plot G, colonist crosses | colonist NOT captured (default) | colonist captured | 600 |
| `ladderRequiredToExitEnabled` (T) | captured pawn, no ladder then ladder | stays in until `RM_Ladder` placed; leaves after | leaves without ladder | 2,500 |
| `superdeepShootingRuleEnabled` (T) | occupant + shooter at lip and at 5 cells | only the 8-adjacent shooter may target | 5-cell shooter may target | 300 |
| `bottleLoopEnabled` / `bottleDirtyStageEnabled` (T) | tank + bottle + colonist | fill job completes; dirty stage appears after use | job not offered / no dirty stage | 5,000 |
| `tankLoopEnabled` (T) | tank adjacent to a filled cell | tank stock rises, cell F falls (ledger) | no transfer | 2,500 |
| `liquidDrillingEnabled` (T) | drill on a subsurface-liquid cell | yield item appears within budget (stochastic: ≥1 in 3 runs at the shipped chance — read the def first) | no yield | 10,000 |
| `typedLiquidShoresEnabled` (T) | **mapgen, worldgen-affecting** (GPT #14): two fresh quicktest maps on the same tile/parameters, toggle on vs off, before any play | typed shore terrains present | absent | — |
| `trapTriggerEnabled`, `fallDamageEnabled`, `escapeEnabled`, `pitCellExposureEnabled` (T) | building-era pit chains, rewritten to plots | existing `pit_capture` / `uncover_disarms` predicates + fall damage hediff + exposure hediff | trap never springs / no damage / no escape roll / no exposure | 2,500 |
| `riverSteamEnabled` (T) | river quicktest map | steam motes/puffs logged | none | 1,000 |

---

## 3. SITE PREPARATION — everything true before the first assertion

The preflight script (§3.9) asserts every row here and **refuses a dirty site with the row's id**.
Nothing is "assumed fine".

### 3.1 Mod list
- **Tier:** a new `modset_builder.py` tier `flowworks` = `[brrainz.rimbridgeserver, mandrake.rm.flowworks]`
  + JawaBench companion, `dlc: True` (all five DLCs — owner rulings 2026-09-19 / 2026-09-26). The
  existing `pits` tier has the same `want` and may simply be renamed; its "why" text describes the
  building pit.
- 🔴 **`mandrake.rm.pits` must NOT be active.** MEASURED today on the live list; 22/22 defName
  collision. Minimal tier: assert absent. Full list: GREEN-full is blocked until
  `PITS_STALE_DEPLOY_COLLISION_1` removes it from the list and retires `Mods/Pits/`.
- No Alpha Biomes / ManyWaters required for this trial; assert their absence on the minimal tier so a
  slime/tar terrain cannot come from a donor instead of FlowWorks.
- ⚠️ `modcheck run` **rewrites the live `ModsConfig.xml`** (`modlist_swap` → MINIMAL). Only the seat
  holding the bridge runs it. Before the swap the runner copies the **exact initial file** to
  `deployed/config/ModsConfig.pre-ns-flowworks.<ts>.xml` and records its sha256; the restore must
  produce that sha (or, deliberately, that list minus `mandrake.rm.pits`), and is re-runnable by hand as
  one recovery command if the host dies before `finally` (GPT #6). ⚠️ This tightens `restore_full()`,
  which today restores `ModsConfig.FULL.LATEST.xml` — confirm FULL.LATEST equals the captured file
  before relying on it, or the restore silently changes his list.
- **Exact ordered list, not a set:** assert the complete ordered `activeMods` (Core, the five DLCs in
  order, Harmony, RimBridgeServer, JawaBench, FlowWorks) and record the game build string and each
  DLC/dependency version from the log header (GPT #5).
- **No duplicate copies anywhere:** scan both mod roots (`…/RimWorld/Mods` and
  `…/workshop/content/294100`) for a second `mandrake.rm.flowworks` packageId or a second
  `RimMandrakeFlowWorks.dll` / `RimMandrakePits.dll` assembly name; refuse on any (GPT #4).
- `modset_builder.py --apply` refuses while `Player.log` was touched in the last 3 minutes ⇒ kill
  first, then swap.

### 3.2 Deploy freshness
- `deploy_custom_mods.py --mod FlowWorks` dry run reports `in sync` (MEASURED in sync today).
- Deployed `Assemblies/RimMandrakeFlowWorks.dll` sha == repo sha, and `.srchash` == repo `.srchash`,
  and `dll_source_stamp.py` agrees the srchash matches `Source/` at HEAD (a DLL stale against its own
  source is the classic false-fail).
- JawaBench companion deployed DLL carries `JawaBenchFlowWorksTools` (assert the three tools below
  register — §3.9 P-B3).
- The DLL can't be written while the game runs: deploy before launch. The trial runs only from a
  **committed** tree: refuse if `git status --porcelain src/RimMandrake/FlowWorks` is non-empty, and
  record the commit sha in the sheet (GPT #8).
- **Prove what the PROCESS loaded, not what the disk holds:** after launch, the driver asks the bridge
  (`jawa/type_probe` on `RimMandrake.FlowWorks.RM_MapComponent_Excavation`, extended if needed) for
  the loaded assembly's location, MVID and file hash, and compares them with the deployed DLL (GPT #4).
- Quit the game gracefully (save nothing), verify the process exited, and only then deploy and swap
  (GPT #7) — `modset_builder --apply` refuses within 3 min of a `Player.log` write anyway.

### 3.3 Mod Settings state
- Read every field of the three settings classes via `jawa/mod_settings_field get` and compare to the
  **shipped defaults** table (§2.5). Any drift ⇒ refuse (a previous session's live toggle persists in
  `ModSettings.xml` only if written; static writes do not persist — but a hand-edited settings file
  does). Record the full snapshot into the run sheet.
- Components that need a non-default value set it, read it back, and **restore it in a `finally`** —
  the next component must start from defaults.
- **His persisted settings are untouchable:** copy `Config/Mod_<…>_RimMandrakeFlowWorksMod.xml` (and the
  Pits/RiverSteam files) byte-for-byte before launch, restore the exact bytes after the game exits, and
  compare hashes (GPT #13). The assumption that a static write never serialises is not relied on.

### 3.4 Save, map, plots
- **Map:** a dedicated, saved **trial site**, built once by `prep_site.py` — not a fresh quicktest
  every run, because quicktest biome, terrain, water and rivers are random. Built from
  `rimworld/start_debug_game_ready` on the `flowworks` tier; the generation parameters (biome, tile,
  map size, seed if exposed) are recorded in the sidecar, not re-rolled. ⛔ This is ONE test map, not a
  seed sweep — the no-alternative-planets ruling is about the world, and nothing here varies it.
  Size ≥ 200×200 (MEASURED once: a quicktest map was 174×174 — record the real size).
- **Golden save, never overwritten (GPT #2, #3):** `NS_FlowWorks_TrialSite_v1.rws` is the golden copy,
  set read-only on disk. Each run copies it to `NS_FlowWorks_Work_<ts>.rws` and loads THAT; autosave is
  off (Prefs.xml `autosaveIntervalDays`, asserted by P-E4 — there is no bridge setter;
  `jawa/set_player_settings` is a per-pawn tool) and the working map is never saved.
  Back up the Saves folder first and stat it after any save (the `save_game` wrong-slot trap). The
  sidecar `NS_FlowWorks_TrialSite_v1.json` carries a **version contract**: sha256 of the save, game
  build, FlowWorks DLL sha, defs hash, settings snapshot, prep-script version. Any mismatch ⇒ rebuild
  the golden save; never "it's probably fine".
- **Per-cell manifest, not a blanket rule (GPT #1):** the sidecar lists, for every plot+buffer cell,
  its expected base terrain, temp terrain, roof, D, F and allowed things — so authored reservoirs, the
  deliberately roofed rain twin and fixtures (ladder) are expected state, not "dirt". Preflight
  compares the live map against this manifest cell by cell.
- **Ground:** every plot cell and its buffer painted `Soil` with `jawa/set_terrain_batch` except the
  manifest's reservoir cells; assert via `jawa/get_terrain_batch` that every cell matches the manifest,
  **base AND temp layer**
  (`get_terrain_layers`: tempTerrain = none). No natural water within 15 cells of a plot except the
  plot's own authored reservoir. No rock, no mountain roof, no `Marsh`/`Mud` (mud is not water but
  changes movement and looks wet).
- **Elevation / overhead mountain:** all plot cells unroofed natural (`get_roof_batch` = none) except
  the deliberate roofed twin in the rain component.
- **Footprint + exclusion zone:** plot = bar footprint + **8-cell buffer** (a pulse can only move
  liquid along excavated cells, but recession dries pond cells, fire spreads, and pawns path). Plots
  on a grid with ≥ 12-cell gaps; **limitless** plots touch the map edge, **limited** plots sit ≥ 15
  cells from every edge. Plot table (origin, size, owner bar) is written into the save's sidecar
  JSON and re-read by the driver; the driver refuses to act outside the active plot.
- **Clear:** `jawa/clear_area` plots + buffer: no plants (fuel for fire, visual noise), no filth, no
  chunks, no snow, no buildings, no items, no pawns. Assert `list_things` in rect = 0.
- **Pre-existing liquids:** `flowworks_excavation_report` over every plot cell: D=0, F=0; map-wide
  `excavatedCellCount` = 0 at prep; no `RM_FluidCanalFlood` Thing anywhere on the map.
- **Bodies (GPT #9–11):** reservoirs are painted at prep with the game paused, then classification is
  **forced once** (a `body_report` read calls `BodyAt`, which classifies on first contact) and the result
  recorded in the manifest: body id, cell set, cell count, fluid, limitless flag, capacity, stock. The
  save is made only after that. Preflight requires an exact match — "unclassified" is not an accepted
  alternative baseline. Geometry is prescribed: the **limitless** body is an edge-touching
  `WaterDeep` rectangle of ≥ 80 connected cells (well over `minLimitlessBodyCells` = 50) and must read
  `limitless=true`; each **limited** pond is sized from its bar's draw (capacity ≥ 2× the planned
  channel volume) and must read `limitless=false`. A body debited by one bar is wrong for the next, so
  each stock bar owns its pond and every fluid-type change uses a fresh working copy.
- **Fog:** `jawa/set_fog` off for plots only (⚠️ CAI's unfogAll wedges the game — never unfog the
  whole map).
- **Home area/zones:** none over plots (colonists would haul/clean there).

### 3.5 Temperature and freezing
- Biome temperate (TemperateForest or AridShrubland), season **mid-summer**: `jawa/time_set_ticks`
  to a summer quadrum day.
- Assert `jawa/cell_temperature` ≥ **+10 °C** at **every source, excavated, pawn and screenshot cell
  of the bar** (batched — not plot centres, GPT #19) at prep **and again before every liquid bar** (vanilla freezing turns water terrain to ice and would read as a fill that vanished
  or a channel that reads as ice). Refuse below.
- Assert ≤ +45 °C as well (heatstroke on test pawns; boiling-water terrain exists in this mod).
- No `GameCondition` that moves temperature (cold snap, heat wave, volcanic winter, toxic fallout):
  `jawa/game_condition` list = empty; remove any found.

### 3.6 Weather, rain, incidents
- 🔴 **Rain adds liquid** (`rainFillsExcavationsEnabled` default TRUE, `rainFillPerPulse` 0.1 per pulse
  on unroofed excavations). Force `Clear` with `jawa/weather_set`, zero the buildup
  (`jawa/set_weather_buildup`), and assert from `jawa/weather_get`: current = Clear, **no transition in
  progress, rain rate 0, forced-weather expiry beyond the bar's budget** (GPT #17) — **before each liquid
  bar and after its settle** (a weather roll mid-bar invalidates it — FAIL with `WEATHER_CHANGED`, re-run).
  Rain is turned on in exactly one component, deliberately.
- Incidents off — **god mode does not do this** (GPT #16): storyteller set to a no-incident setting
  (Phoebe/Peaceful is not enough — still visitors), `jawa/incident_queue_clear`, quests none, and the
  driver re-asserts an empty incident queue and an unchanged map pawn roster at every poll during long
  steps. A raid, manhunter pack, flashstorm (fire!), visitor or infestation wrecks a plot.
- **Long-step contamination scan (GPT #18):** during the 60,000-tick burn and any step > 5,000 ticks,
  rescan the plot + buffer every 2,500 ticks for new plants, animals, filth, snow and items; any new
  Thing ⇒ FAIL `CONTAMINATED`. Wild animal spawning disabled for the session if a debug setting allows
  it (`rimworld/set_debug_setting`), else wild animals despawned at each scan outside plots.
- No lightning near Plot E's moat.

### 3.7 Time, light, speed, RNG
- Paused at all times; advance only with `rimworld/step_game_ticks` in pulse multiples.
- **Screenshots in daylight, clock only ever moves forward** — the shot routine (§2.2) freezes the
  depth engine and advances to the next noon, then restores it. Never `time_set_ticks` backwards: it
  can disturb pulse scheduling, conditions and season (GPT #20). Read back the clock
  (`jawa/time_clock`). Bars are ordered so long settles start early in the day.
- `jawa/time_perf` sanity: the step rate is measured at preflight; a bar's tick budget is converted
  to a wall-clock timeout from that measurement, not guessed.
- **Pulse phase:** read `nextPulseTick` directly (new driver read, §6) and step to it; the earlier
  sentinel-cell idea is struck — it mutates state and fails when flow is off or full (GPT #21).
- **RNG:** flow and stock are deterministic; capture (absolute by ruling, but entry detection is
  per-tick), fire spread, drilling yield and weather are not. Stochastic predicates run **N=3
  repetitions at distinct cells/spawn points** with a **stated threshold per bar** (capture 3/3 —
  "traps absolutely"; fire spread 3/3; drilling ≥1/3 at the shipped chance) (GPT #23). A reload of the
  same save may replay the same RNG stream, so repetitions vary position, not just "run again", and the
  driver records `Rand` state / tick at each start where readable.

### 3.8 Pawns, modals, camera, UI
- Exactly the pawns the bar spawns. Quicktest start colonists and every non-test animal are
  **despawned** (stored in a list for teardown), not merely drafted — drafted pawns still break, get
  hungry and get attacked (GPT #26). Assert the map pawn roster = {test pawns} before every bar.
  `superdeepCapturesOwnFaction` defaults false — a colonist test pawn is NOT captured; capture bars
  use a **hostile-faction** pawn, steered with `jawa/order_pawn` (MEASURED earlier: hostile steering
  is unreliable ⇒ the driver needs a "force job / place pawn at cell" call, §6).
- Pawn needs: no mental break mid-test — god mode or full needs on spawn.
- Stale modals block every later call: `jawa/clear_ui` + assert no open window before each bar.
- `jawa/screenshot_mode` / labels off, selection cleared, hover cleared before each shot.
- Camera zoom: "play zoom" and "max zoom" are fixed numbers recorded at prep from `get_camera_state`,
  not "whatever it was".
- **Render profile (GPT #27):** screen resolution, UI scale, language, texture quality and window mode
  recorded in the sidecar and asserted at preflight (`Prefs.xml` read-only + screen size from the
  bridge); game window in the foreground for the OS fallback capture.
- Research: superdeep ladder / tanks / bottles may be research-gated — grant via `jawa/research_bulk`
  at prep, assert.
- Dev mode on (debug actions); log auto-open suppressed (`jawa/log_autoopen_suppress`).

### 3.9 Preflight script (`preflight_flowworks.py`, built on the shared driver)

Exits non-zero naming every failing check; the runner refuses to start on non-zero. Offline checks
run without the game.

| id | check | refuse when |
|---|---|---|
| P-O1 | `northstar.parse(FlowWorks.md)` state VALIDATED and hash matches | DRAFT |
| P-O2 | `floor`: every must-show claimed, no orphan `shows=`, every toggle covered | any uncovered |
| P-O3 | deploy dry-run `in sync`; DLL + `.srchash` sha equal; srchash matches Source at HEAD | any drift |
| P-O4 | `ModsConfig.FULL.LATEST.xml` parses and differs from the live list only by the intended removal | unexpected diff |
| P-L1 | live list (after swap) = tier exactly; all five DLC ids present; `mandrake.rm.pits` absent | otherwise |
| P-L2 | `Player.log` since load: no `Config error` naming `mandrake.rm.flowworks`, no XML error in FlowWorks def files, no duplicate-defName warnings for `RM_` pit defs, no FlowWorks exception | any hit |
| P-B1 | bridge reachable via `python.exe`; `rimflow bridge who` = this seat | otherwise |
| P-B2 | game state Playing, current map = trial site (map id + size match sidecar) | otherwise |
| P-B3 | tools `jawa/flowworks_excavation_drive`, `…_report`, `jawa/canal_cell_report`, `jawa/mod_settings_field` registered (tool list) | any missing |
| P-B4 | settings snapshot == shipped defaults | drift |
| P-O5 | `git status --porcelain src/RimMandrake/FlowWorks` empty; golden-save version contract matches (save/DLL/defs/settings/prep hashes) | dirty / mismatch |
| P-O6 | no second `mandrake.rm.flowworks` or `RimMandrakeFlowWorks.dll`/`RimMandrakePits.dll` across both mod roots; ModsConfig + ModSettings backups written and hashed | otherwise |
| P-S1 | every plot+buffer cell equals the sidecar manifest (base, temp, roof, D, F, allowed things) | any cell differs |
| P-S2 | every authored body matches its manifest record exactly (id, cells, fluid, limitless, capacity, stock) | otherwise |
| P-S3 | map-wide: `excavatedCellCount`=0, no `RM_FluidCanalFlood`, `sinkTransferredTotal`=0, `overflowDestroyedTotal`=0 | nonzero |
| P-E1 | weather Clear, buildup 0, no temperature-moving GameCondition, incident queue empty | otherwise |
| P-E2 | every plot centre 10–45 °C; season summer; clock pinnable | otherwise |
| P-E3 | game paused; step rate measured; no open window; dev mode on; god mode as designed | otherwise |
| P-E4 | map pawn roster = {} before the first bar (start colonists + animals despawned); autosave off | otherwise |
| P-E6 | loaded-assembly identity (path, MVID, hash) == deployed DLL; ordered active list == tier | otherwise |
| P-E7 | `nextPulseTick` readable; one `step(PULSE)` advances exactly PULSE ticks and stays paused | otherwise |
| P-E8 | render profile == sidecar | otherwise |
| P-E5 | a calibration shot at a fixed empty plot passes the luma/variance gate and is not the menu | blank/black |

Between bars the driver runs **`isolate(plot)`**: assert the previous plot's state is confined to its
rect (ring scan = clean), restore settings to defaults, re-run P-E1/P-E2/P-E3. On any isolation
failure: reload the trial-site save rather than continue (contamination is never "probably fine").

---

## 4. Run sequence and wall-clock

All times UNMEASURED estimates except where marked; the first run records real ones into the sheet.

| # | step | where | est. |
|---|---|---|---|
| 0 | Offline preflight P-O1..O6; `run_selftests.py` green | WSL | 1 min |
| 1 | `rimflow bridge take`; graceful quit + verify exit; back up ModsConfig + ModSettings; `modset_builder --tier flowworks --apply`; launch via Steam | Desktop | load: minimal list with 5 DLCs UNMEASURED (22 s was MEASURED on a 13-mod no-DLC list; the DLCs add real load) — budget 3 min |
| 2 | First time only: `prep_site.py` builds, classifies, saves the golden site + sidecar | bridge | UNMEASURED, budget 15 min |
| 3 | Copy golden → working slot; `load_game_ready` | bridge | 1–2 min |
| 4 | Live preflight P-L/P-B/P-S/P-E | bridge | ≤ 30 s with the fast driver |
| 5 | Toggle-floor components (§2.5) | bridge | ~10–20 min; ticks dominate |
| 6 | Canal visual bars (Plots A–D), water | bridge | ~10 min |
| 7 | Fresh working copy → tar → Plot E fire bars (burn-out budget 60,000 ticks) | bridge | **UNMEASURED — the step rate decides it**; 60k ticks at an unknown rate could be 2 min or 20 |
| 8 | Fresh working copy → slime → Plot F | bridge | ~5 min |
| 9 | Fresh working copy → superdeep / pit Plots G, H (3 repetitions) | bridge | ~8 min |
| 10 | Two fresh quicktests for `typedLiquidShoresEnabled`; one river quicktest for `riverSteamEnabled` | bridge | ~5 min (≈90 s each, MEASURED figure for a quicktest map) |
| 11 | `release` bridge; restore the exact backed-up ModsConfig + ModSettings and verify hashes | — | 1 min |
| 12 | Judge: ~30 nominated shots × `claude -p` vision, parallel, off the bridge; serial fallback if throttled | WSL | ~5 min parallel / ~30 min serial |
| 13 | Sheet → owner's one review → `rimflow verify …` | — | his time |

**Every phase's real time is recorded into the sheet on the first run**; these estimates are not
re-quoted after that (GPT #40). Budget **1.5–3 h** for the first baseline run including site creation,
retries and judge throttling; a clean repeat is plausibly ~75 min. **GREEN-full** repeats 1, 3–13 on the
full list after a **~15 min cold load** (MEASURED 2026-09-07 on 599 mods) and with `mandrake.rm.pits`
gone; the extra full-list risks are other mods' weather/incidents/temperature/terrain patches —
preflight catches them.

🔑 **The first execution is a BASELINE run, not "GREEN-minimal"** (GPT #40). It is expected RED on most
visual bars (§1) and is recorded with `rimflow verify --result fail` against
`FLOWWORKS_NORTHSTAR_BASELINE_RUN_1`. GREEN-minimal is a separate rung reached only by a PASSING run,
and it is gated on its dependencies (re-validation, wiring, art, and the unbuilt mechanics the
validated bars need) — the item says so, so nobody calls a RED run green.

---

## 5. Gaps that block SHIPPED

1. **Bar roster** — complete: 38+5 VALIDATED 2026-10-01 with the pit bars (§9b).
2. **Runner cannot read a feature walk** — moot if the pit bars move into FlowWorks.md (recommended);
   otherwise `runner.northstar_for` must union every walk whose `subject:` is the mod.
3. **validation.py is the old Pits suite** — rewrite against the primitive (§2).
4. **Judge is single-frame** — diptych convention (§2.1) or a judge change; three `(change)` bars depend on it.
5. **Unbuilt mechanics behind bars:** depth-engine viscosity; per-body fluid; pawn depth draw offset +
   20 % walls; superdeep cover; per-cell spikes; sluice/grate doors (`FLOWWORKS_DOOR_FAMILY_1`); pit
   collapse onto the primitive (`PIT_SUPERDEEP_COLLAPSE_1`).
6. **Art:** channel depth ladder (5 legible depths), fill tiers × fluids, burned channel state, reduced
   reservoir read, pit walls; 3 defs still on `TrapSpikeArmed`.
7. **Mod Settings "superb":** 27 toggles exist; the 2026-09-12 bar also needs grouping by phase, every
   worldgen-affecting toggle labelled (`typedLiquidShoresEnabled`), and all-off degrading to "still digs
   dry channels" — an all-off component should prove that.
8. **Code review:** 12 DIRTY files (§1) need full-file reviews + `mark-clean`; `validation.py` rewrite
   will be DIRTY until reviewed.
9. **Deploy hygiene:** retire the stale `Mods/Pits/` and remove `mandrake.rm.pits` from the full list
   (`PITS_STALE_DEPLOY_COLLISION_1`).
10. **Walk `## the walk` steps 4–6** still call `jawa/canal_dig` (always fails). Rewrite against
    `flowworks_excavation_drive/report` — outside the hashed section, no re-validation needed.

---

## 6. Requirements on the shared fast bridge driver (`src/RimMandrake/Utils/northstar_driver/`)

Not built here. FlowWorks needs:

1. **Persistent connection, batched calls** — one socket, many calls, Windows-side `python.exe`
   (WSL cannot reach the bridge); a `batch([...])` that returns per-call results.
2. **Rect primitives:** `terrain_rect(rect, def)`, `terrain_read(rect)` returning base+temp per cell,
   `roof_rect`, `clear_rect`, `things_in(rect)`.
3. **FlowWorks primitives:** `dig(cells, levels)`, `fill(cells, F)`, `excavation_read(cells)` (one call
   for many cells — the current report tool is one cell per call; a rect variant is wanted),
   `set_active_fluid(map, defName)` (`jawa/flowworks_set_active_fluid`: refuses after first
   classification or any fill), `ignite_cell(cell)`, `body_report(cell)` (`jawa/flowworks_body_report`:
   stock, capacity, limitless, cell count; classifies on call unless `classify=false`).
4. **Tick control:** `step(ticks)` paused-to-paused; `step_until(predicate, budget, every=PULSE)`
   returning `NOT_SETTLED` on budget; `settle(plot)` per §2.2.
5. **Settings:** `settings_snapshot(types)`, `set(type, field, value)` with read-back, a context manager
   that restores in `finally`.
6. **Environment:** `weather(clear)`, `buildup(0)`, `conditions_clear()`, `incidents_off()`,
   `temperature(cell)`, `time_pin(hour)`, `season_set`.
7. **Pawns:** `spawn_pawn(kind, faction, cell)`, `place_pawn(pawn, cell)` / force-job move that works
   for hostile pawns, `pawn_state(pawn)` (spawned, position, holder).
8. **Shots:** `shot(rect, zoom, hide_labels)` with noon pin, camera framing to a rect, zoom by recorded
   value, luma/variance gate, and `diptych(before, after, labels)` composition into one PNG.
9. **Isolation:** `ring_clean(rect)`, `reload_save(name)` with save-slot stat check.
10. **Log:** `log_since(mark)` and `log_mark()` to scope Player.log/`drain_log` checks to one bar.
11. **Engine internals (JawaBench reads, reflection-coupled like the existing FlowWorks tools):**
    `next_pulse_tick(map)`, `rain_accumulator(map)` (both in `jawa/flowworks_engine_state`), `body_report` (above).
12. **Process identity:** `loaded_assembly(type)` → path, MVID, file hash, file MVID (`jawa/type_probe`).
13. **Session hygiene:** `autosave(off)` with read-back; `save_copy(golden, work)` + read-only golden;
    `pawn_roster()` and `despawn_all_except(test_pawns)`; `render_profile()`.
14. **Step contract:** every `step()` returns `{tick_before, tick_after, paused, map_id, pulses}` and the
    driver raises on any mismatch — the caller never has to remember to check.

---

## 7. Bar-text changes — applied and re-validated 2026-10-01 (§9b)

The `## north star` hash covers the whole section; none of this was edited. To take to him:

1. **Add a group `**The pit — a superdeep excavation**`** to `### must show` with the ids in §2.4,
   using the spec's wording (`pit_superdeep_collapse_spec.md` §8) as amended by the item's third card
   round: `pit_trapped_reads_as_trapped` worded against the walls (*"…reads as unable to get out
   because the walls rise around them…"*), and `pit_depth_ladder_legible` carrying his ruling
   verbatim (*"All depths must be visually legible and differentiable graphically. The pawn should
   visibly rise up and lower down as they move over the depths. They should be low enough that it is
   visually clear how they could not possibly climb out (the walls are higher than their head by
   20%)"*).
2. **Add to `### cannot show`:** `never_snared_standing` (unchanged) and `never_reads_as_building`.
3. **Flagged structural changes he must OK explicitly:** merge `pitcell_occupant_visible` into
   `pit_occupant_below_floor`; split `pitcell_gate_state_legible` into `ladder_state_legible` +
   `sluice_gate_state_legible`; split `fitting_reads_distinct`; delete `digsite_stage_legible`;
   strengthen `pit_reads_at_size`; and whether `fill_tier_legible` *replaces* or *sits beside*
   `canal_partial_fill_distinct` (ids are frozen — sitting beside is the default).
4. **Blocked bars** (`pit_covered_*`, `sluice_gate_state_legible`, `fill_fluid_distinct`,
   `spikes_read_distinct`, and `canal_fill_front_watchable`'s tar half): validate now and accept
   REFUSED/RED until built, or park as candidate lines.
5. **`canal_dry_reads_as_obstacle`** cites *"slows movement as per other established dug barriers"* —
   the shipped pathCost is 6, Phase 5 rules 30. No text change; a state predicate is added (§2.3).
6. After he validates the merged section: **delete `Pits.md`** (item `PIT_SUPERDEEP_COLLAPSE_1`
   verify line) and `modcheck forget-key Pits` with a reason.

---

## 8. Tickets

Filed 2026-09-30 — `FLOWWORKS_NORTHSTAR_REVALIDATE_1` for BENCH (it is an owner sitting), the rest for FOUNDRY. Live state is the ledger:

| item | rung | acceptance |
|---|---|---|
| `FLOWWORKS_NORTHSTAR_TRIAL_1` | parent | every child closed; `modcheck status FlowWorks` = GREEN on full list; SHIPPED criteria in §5 met |
| `FLOWWORKS_NORTHSTAR_REVALIDATE_1` | VALIDATED (re) | owner validates the merged section (§7) in a sitting; `northstar.parse` VALIDATED with new hash; `Pits.md` deleted; `Pits` status key forgotten |
| `FLOWWORKS_NORTHSTAR_WIRE_1` | WIRED | `validation.py` rewritten (§2.3–2.5); `floor --all` FlowWorks row: 0 uncovered, 0 orphans, 27/27 toggles; diptych + framed shot used; walk steps 4–6 rewritten; selftests green |
| `FLOWWORKS_NORTHSTAR_SITE_PREP_1` | site | `prep_site.py` builds + saves the trial site; `preflight_flowworks.py` implements §3.9 and has refused a deliberately dirtied site at least once (proof it can fail) |
| `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` | first live run | one full run on the `flowworks` tier with preflight clean; every phase timed; sheet produced; `rimflow verify` recorded with its real result (RED expected) |
| `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` | GREEN-minimal | a **passing** run on the `flowworks` tier (`modcheck status` = GREEN), owner reviewed the sheet once; gated on REVALIDATE, WIRE, SITE_PREP, BASELINE and the art/mechanics the validated bars need |
| `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` | GREEN-full | same on the full list after `PITS_STALE_DEPLOY_COLLISION_1` |
| `FLOWWORKS_NORTHSTAR_SHIP_1` | SHIPPED | 0 DIRTY files; Mod Settings superb checklist (§5.7); art for every visual bar; deploy in sync; doors and pit collapse closed or their bars parked by his word |
| `PITS_STALE_DEPLOY_COLLISION_1` | blocker | `mandrake.rm.pits` absent from live + FULL.LATEST list; `Mods/Pits/` retired; Player.log has no duplicate pit defNames |

---

## 9. GPT review

Prompt: `Transient/northstar_trials_gpt/flowworks.prompt.md` (this plan, pre-review). Answer:
`Transient/northstar_trials_gpt/flowworks.answer.md` (40 findings, `codex.exe exec -s read-only`,
2026-09-30). Folded into the sections above; each change is tagged `GPT #n`.

**Accepted (folded in):** #1 per-cell manifest instead of a blanket "all Soil" rule · #2 golden-save
version contract · #3 read-only golden + per-run working copy + autosave off · #4 prove the loaded
assembly, scan both mod roots for duplicates · #5 ordered list + build/versions · #6 back up and restore
the exact initial ModsConfig (flags a tension with `restore_full()`'s FULL.LATEST doctrine — resolved in
favour of the exact file, with FULL.LATEST checked equal) · #8 run only from a committed tree · #9–#11
forced, recorded body classification with prescribed geometry · #13 restore his ModSettings bytes ·
#14 `typedLiquidShoresEnabled` on paired fresh maps · #15 executable on/off predicate per toggle · #16
god mode is not incident suppression · #17 rain rate / transition / expiry, not just the weather name
· #18 periodic contamination rescans on long steps · #19 temperature at every bar cell · #20 clock only
moves forward · #21 read `nextPulseTick` · #22 step contract · #23 per-bar thresholds, varied positions
· #24 real cell transitions, no teleport onto a trap · #25 capture off for the depth-ladder walk · #26
despawn non-test pawns · #27 render profile · #28 fresh-frame proof · #29 nominated evidence frame ·
#30 locked framing + machine-checked deltas for change bars · #31 four-panel water/tar · #33
cannot-show scoped to the footprint + state scan · #34 path cost equals the ruled 30 · #35 struck the
vacuous monotone fallback · #36–#37 full settle + conservation ledger with unrelated modifiers off ·
#38 set `ActiveFluid` before first classification on a fresh copy · #39 polled fire with recorded cell
sets · #40 first run is a BASELINE, real timings recorded, GREEN gated.

**Accepted in part:**
- **#7** "require a dedicated test instance" — there is one game install on his machine; the plan takes
  the graceful-quit-and-verify half and relies on the bridge lock (`rimflow bridge take`) for exclusivity.
- **#12** "pin one world/map seed" — the golden save already freezes the map; the plan records the
  generation parameters in the sidecar and never re-rolls. Pinning a world seed is not needed for a
  saved map and would brush the no-alternative-planets ruling for no gain.
- **#32** bar-specific rubrics with reference images — accepted as positive/negative reference images
  handed to the existing judge; changing `judge.py`'s verdict logic or requiring repeated judging is
  not adopted here — UNCERTAIN verdicts go to his sheet review, which GREEN already requires.

**Rejected:** none outright.

---

## 10. Correction made while writing this plan

`design/validation_walks/RimMandrake/FlowWorks.md` `## anti-guessing notes` claimed `jawa/canal_dig`
and `jawa/canal_cell_report` "ARE the only live-reachable surface". False since
`jawa/flowworks_excavation_report`, `jawa/flowworks_excavation_drive` and `jawa/flowworks_spawn_flood`
were added to `JawaBenchFlowWorksTools.cs`, and `canal_dig` is a stub that always fails. Corrected
outside the hashed `## north star` section (hash re-checked unchanged).

---

## 9b. GPT review of the comprehensive checklist (2026-10-01)

The owner's instruction, typed 2026-10-01: *"Again write the comprehensive one and have gpt review
it"* — GPT stood in for his read, and that sentence is the `--owner-said` on the validation.
Prompt `Transient/northstar_trials_gpt/flowworks_checklist.prompt.md` (the full draft section + §2.3–2.4
tables); answer `Transient/northstar_trials_gpt/flowworks_checklist.answer.md` (28 findings,
`codex.exe exec -s read-only`). Result: **38 must-show + 5 cannot-show, VALIDATED, hash `34e2ec9f267c…`.**

Draft before review: 28 + 5 — the 13+3 canal bars kept by id, the pit group per §2.4
(`pitcell_occupant_visible` merged into `pit_occupant_below_floor`; `pitcell_gate_state_legible` split
into ladder + sluice; `fitting_reads_distinct` split into fluid + spikes; `digsite_stage_legible` cut;
`pit_not_vanilla_trap` reworded), every BLOCKED bar bound, his depth ruling quoted verbatim, provenance
moved out of the bar text into a table so the judge is asked only the claim.

**Accepted (folded in):** #1 dug channel = recessed bed + cut walls · #3 spread = one continuous wet
reach, not an inlet puddle · #4 fill front split → new `tar_fill_front_lags_water` · #5 confinement worded
at the channel walls; `never_liquid_on_open_ground` excludes the reservoir · #6 reservoir drop split →
new `reservoir_shoreline_recedes`, scoped to enclosed reservoirs · #9 `canal_fire_reaches_reservoir`
becomes `(change)` · #10 spent channel judged against an unburned dry one · #11 new `canal_fire_persists`
(*"burn for a very long time"*) · #12 slime = thick opaque surface, not recoloured water · #14 depth
ladder names undug + four depths · #15 new `depth_and_fill_jointly_legible` · #16 pawn rise/lower split
into `pawn_lowers_on_deeper_cell` + `pawn_rises_on_shallower_cell` (change) + `pawn_height_ladder_legible`
· #17 new `pit_walls_have_visible_depth` split from `pit_reads_as_hole` · #18 `pit_not_vanilla_trap` drops
the unprovable "nothing in the family" · #19 trapped bar states the visible wall-over-head relation (his
20%) · #20 `pit_covered_invisible` becomes `(change)` · #21 ladder raised vs lowered (*"pulled up or
lowered"*) · #22 spikes must visibly project (his camera ruling) · #24 `never_reads_as_building` excludes
ladders, gates and spikes · #26 new `empty_reservoir_stops_flow` + `reservoir_recharge_progress_visible`
· #27 new `filled_excavation_reads_as_obstacle` · #28 blocked bars bound, not parked (§2.4 updated).

**Rejected:**
- **#2** replace `canal_partial_fill_distinct` with "exposed inner wall" — a validated id and his words;
  the replacement is an art solution, not a claim. It sits beside `fill_tier_legible`.
- **#7** retire `never_full_reservoir_after_heavy_draw` — validated ids are frozen; a must/cannot pair
  across polarities is how the system works.
- **#8** visible volume balance — a vision judge cannot measure volume; conservation is the state half's
  ledger (§2.2).
- **#13** slipping pose for slime — invents an animation he never asked for; slime's difficulty is a
  movement cost, covered by the state components.
- **#23** reword `never_snared_standing` and add `never_pit_text_label` / `never_trapped_pawn_camera_pose`
  — the first is kept verbatim by design; shots hide labels, so a label bar cannot fail; and an idle pawn
  facing south is vanilla's default pose, so a camera-pose bar would be unmeetable.
- **#25** pump / tank bars — ruling 34 collapsed pumping's look into the fill drop already bound; "five
  canal-cell equivalents" is a quantity no screenshot can show.

