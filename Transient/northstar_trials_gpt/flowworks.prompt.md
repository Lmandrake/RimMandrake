You are reviewing a validation TRIAL PLAN for a RimWorld 1.6 mod ("FlowWorks": dug canals on a depth/fill grid, liquid stock with limited/limitless bodies, rain fill, recession, superdeep pits that capture pawns, burning flammable liquids). The trial drives a live game through a bridge (step ticks, paint terrain, set fill, take screenshots) and an LLM vision judge grades one screenshot per visual bar.

Attack the plan. Specifically:
1. SITE PREPARATION: what precondition is missing, under-specified, or unverifiable as written? Think about RimWorld specifics: weather/rain, freezing, temperature, roofs, fog, snow, plants/fire spread, pawns pathing through plots, storyteller incidents, time-of-day lighting, map generation randomness, save/load state, mod settings persistence, stale deployed DLLs, duplicate mods, camera/zoom/UI overlays, game speed and tick determinism.
2. FALSE-PASS risks: ways a bar could pass while the mod is actually broken (vacuous checks, wrong frame, wrong cell, judge leniency, state carried from a previous bar).
3. FALSE-FAIL risks: ways a bar could fail while the mod is fine (settle timing, pulse phase, RNG, blank screenshots, contamination).
4. Isolation between bars and between runs.
5. Anything in the run sequence or wall-clock that is unrealistic.

Answer as a numbered list of concrete findings, each with: severity (high/med/low), the plan section it concerns, the problem, and the specific fix. Be terse. No preamble. Max ~40 findings.

=== PLAN ===
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
| DRAFT → VALIDATED | **VALIDATED, hash matches** — 13 must-show + 3 cannot-show | MEASURED: `modcheck.cli status` prints `FlowWorks STALE checklist VALIDATED (13 lines) [stored: GREEN]`; `northstar.parse()` gives 13/3; `floor --all` row reads `VALIDATED 13`. |
| …but the bar is **incomplete** | **0 pit bars.** The 11+1 pit bars live in `design/validation_walks/RimMandrake/Pits.md`, which no `modcheck run FlowWorks` reads: `runner.northstar_for()` resolves `find_walk(ROOT, "FlowWorks")` → `FlowWorks.md` only. | MEASURED (read `runner.py`, `northstar.py`). The `feature:` key (`WALK_FEATURE_KEY_1`) has landed in `doctor.py` (`parse_feature`) — `Pits.md` already carries `subject: src/RimMandrake/FlowWorks` + `feature: pit-dig-trap-and-cell` — but **only `doctor` reads `feature:`; the runner, floor and judge do not.** So a per-feature walk is lint-clean and still binds nothing. |
| Pits walk | `modcheck status` → `Pits ORPHANED (no such mod folder) checklist VALIDATED (11 lines) [stored: GREEN]` | MEASURED. Its `## north star` section also still opens with a **false** "⚠️ DRAFT — not a bar until the owner validates it" banner under `state: VALIDATED`. It is moot once the bars move (§2.3) and `Pits.md` is deleted, so it is not edited here (editing would revert his hash). |
| STALE | The stored `GREEN` is from run `FluidCanals@1789295363` — a pre-north-star, pre-rename, pre-ruling-24 run against a deleted comp. It certifies nothing about today's mod. | MEASURED: `infrastructure/state/modcheck_status.json` `FlowWorks.run_id`, `renamed_from: FluidCanals`. |
| VALIDATED → WIRED | **0 of 13 must-show lines claimed.** `floor --all`: `FlowWorks … VALIDATED 13 0 13 REFUSED (uncovered)`; Pits row `11 0 11 REFUSED (uncovered)`. | MEASURED. |
| validation.py | 🔴 **`src/RimMandrake/FlowWorks/validation.py` is the old Pits suite moved in unchanged**: docstring says "suite for RimMandrake Pits (mandrake.rm.pits)", `suite = Suite("Pits")`, toggles are `PitsSettings`' four, both chains drive the BUILDING pit (`RM_OpenPit_Bare`). **No canal, depth, fill, stock or superdeep component exists.** | MEASURED (read file, 133 lines). |
| Mod Settings toggle floor | FlowWorks ships **27 boolean toggles** (22 in `RimMandrakeFlowWorksSettings`, 4 in `PitsSettings`, 1 in `RiverSteamSettings`) plus 18 numeric tunables. The suite declares 4. | MEASURED (grep of `public static bool` in the three settings classes). |
| GREEN-minimal / GREEN-full | **Never run against the current mod.** | MEASURED (status store). |
| Deploy | `deploy_custom_mods.py --mod FlowWorks` (dry run, from origin/main worktree): `in sync (68 files)`. Deployed `RimMandrakeFlowWorks.dll` and `.srchash` byte-identical to repo (sha1 `ca7e954fd522…` / `98c569bdb880…`). | MEASURED 2026-09-30. Re-measure at run time — this decays. |
| 🔴 Stale **Pits** mod still deployed **and active** | Game `Mods/Pits/` (packageId `mandrake.rm.pits`, `RimMandrakePits.dll`, About.xml dated 2026-08-30) is on the live list beside FlowWorks. **All 22 of its defNames collide with FlowWorks' defs** (`RM_OpenPit_Bare`, `RM_PinnedInPit`, `RM_DigPitDeeper`, …). | MEASURED: parsed live `ModsConfig.xml` (612 active, read-only) — contains both `mandrake.rm.flowworks` and `mandrake.rm.pits`; defName set intersection 22/22. This is a site-prep blocker for GREEN-full and a live-game defect in its own right — filed as `PITS_STALE_DEPLOY_COLLISION_1`. |
| Code review | **117 CLEAN / 12 DIRTY** of 129 tracked `.cs/.py/.xml` under `src/RimMandrake/FlowWorks`. DIRTY: `RM_LiquidDrill.xml`, `RM_LiquidBodyRegistry.xml`, `RM_Propane.xml`, `RM_TarGlass.xml`, `RM_WaterBoiling.xml`, `RM_LiquidTank.xml`, `RM_DeepSand.xml`, `RM_LiquidShores_MapGenPatch.xml`, `RM_LiquidBodyDef.cs`, `RM_NoRecreationalSwimExtension.cs`, `RM_Patch_NoRecreationalSandSwim.cs`, `Tools/generate_liquid_suite.py`. | MEASURED: `code_review_status.py check` over `git ls-files`. |
| Art | **7 textures ship** (tank, 3 tar filth, barrel, bottle, bucket). Every channel depth (`RM_Channel_Empty/Mid/Deep/Superdeep`) borrows `Terrain/Surfaces/Gravel`; fills borrow vanilla water ramps tinted; **3 pit defs still point at `Things/Building/Security/TrapSpikeArmed`**. | MEASURED (find + grep of `texturePath`/`TrapSpikeArmed`). |

**Ruled vs built for the features the bars cover** (MEASURED by grep of `Source/` and `Defs/` unless marked):

| feature | ruled | built? |
|---|---|---|
| Depth/fill primitive, pulse flow, confinement | yes | **yes** — `RM_MapComponent_Excavation`, pulse every `pulseIntervalTicks` = 250, `flowPerPulse` = 1 |
| Stock, limited/limitless (sticky), recession, refill, rain fill (roof blocks it), edge sinks | yes | **yes** — `RM_LiquidStock`, `RM_LiquidBody`; a body is classified ONCE on first contact and never re-argued |
| Per-fluid viscosity in the depth engine | yes ("water almost at once, tar creeping") | **no** — `RM_MapComponent_Excavation` has no viscosity/`ticksPerTile` read; viscosity exists only on the legacy `Flood_FlowWorks` release |
| Per-body fluid type | yes (item `[F]`) | **no** — `ActiveFluid` is ONE `FluidDef` per map, defaulting to water, with no UI and no bridge setter |
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
  back from settings (default 250, clamped ≥ 60). A plot is **settled** when the F vector over every
  excavated cell in the plot is identical across **3 consecutive pulse boundaries** (750 ticks at
  default) AND the plot's reservoir stock reading is unchanged over the same window. **Budget** per
  bar is stated; exceeding it is FAIL with reason `NOT_SETTLED`, never a pass. Every step is
  `rimworld/step_game_ticks` from a paused game — never real-time speed.
- **Conservation check** (used by stock bars): Σ(F over channel cells) × `volumePerTile` + Δ(limited
  body stock) + `sinkTransferredTotal` delta + `overflowDestroyedTotal` delta = 0 within ±1 unit.
- **Shot** — `driver.shot(plot, cells, zoom="play"|"max", hide_labels=True)`: clear selection + UI,
  pin time to noon, frame the cell rect with a 3-cell margin, set zoom, capture via
  `rimworld/screenshot_cell_rect` (fallback `rimworld/take_screenshot`, then
  `system_screenshot.py`), then **read the PNG back and refuse a black/blank/menu frame**
  (mean-luma and variance gate) before handing it to the judge.

### 2.3 The canal bars (13 must + 3 cannot, VALIDATED, ids frozen)

| bar | asserts | setup → state predicates (state half) | shot | live/offline | expected today |
|---|---|---|---|---|---|
| `canal_reads_as_dug_channel` | dug channel reads as excavated ground with walls | Plot A: dig a 1×8 run at D=1 on Soil. Expect report `D=1`, `isExcavated=true`, terrain `RM_Channel_Empty`, F=0. | play zoom, run + 3-cell margin | live | **NO** (Gravel texture) |
| `canal_dry_reads_as_obstacle` | unfilled channel legible as impeding crossing | Same plot as above (shared component allowed: one shot, two `shows`). State: `pathCost` of the cell (def read-back) > open soil — ⚠️ build program Phase 5 says the dry-trench cost should be 30 and today is 6: **assert the def value and report it**, do not gate the visual on it. | same shot | live + `[D]` def read | NO |
| `canal_partial_fill_distinct` | partly filled vs full distinguishable | Plot B: two parallel 1×6 runs at D=3; fill run 1 to F=1, run 2 to F=3 via `setFill`; set `depthEngineEnabled=false` **for this component only** so the pulse cannot equalise them, read back F per cell, restore setting after. | play zoom, both runs in frame | live | NO/UNCERTAIN (tinted ramps may differ) |
| `canal_fill_spreads_along_itself` | liquid spreads through the channel, not pooled at entry | Plot C: limitless reservoir strip on the map edge; dig a 1×10 D=1 channel from it. Step pulses until settled (budget 20 pulses = 5,000 ticks). Predicate: every channel cell F≥1 OR, when the limited budget runs out first, F is monotone non-increasing away from the mouth with no isolated wet cell. | play zoom, after settle | live | state PASS; visual UNCERTAIN |
| `canal_fill_front_watchable` (change) | visible fill front; water near-instant, tar creeping | Plot C, frames at pulse 1 and pulse 3 → diptych. For the tar half, requires per-map `ActiveFluid=RM_Fluid_Tar` (driver needs a setter, §6) on a **second map or after a full plot reset**, because ActiveFluid is map-wide. | diptych | live | **BLOCKED** — depth engine has no viscosity (MEASURED), so tar fills at water's rate; expected NO |
| `canal_holds_only_the_channel` | liquid inside the channel, not on open ground beside it | Plot C after settle. Predicate: every cell in the 1-cell ring around the channel has `D=0`, `tempTerrain=none`, terrain unchanged from the pre-dig snapshot. Toggle `channelConfinementEnabled` (default true). | play zoom | live | state PASS expected (MEASURED built) |
| `canal_reads_as_same_liquid_as_reservoir` | filled canal reads as the same substance as its body | Plot C after settle, reservoir + mouth + channel in one frame. | play zoom | live | UNCERTAIN |
| `reservoir_fill_visibly_drops` (change) | reservoir visibly less full after supplying; small pond shrinks at far edge | Plot D: **limited** pond, 5×5 natural `WaterShallow`, ≥10 cells from every edge and every other plot. Snapshot body stock + pond cells. Dig a 1×12 D=3 channel from it; step until settled (budget 40 pulses). Predicates: stock decreased by Σ F × volumePerTile (conservation ±1); `recessionEnabled` → ≥1 pond cell now dry (`underneath` = original, `isSourceCell=false`). Frames before/after → diptych. | diptych | live | state PASS likely; visual NO (no reduced-pond art) |
| `canal_burning_reads_as_burning_liquid` | lit flammable canal reads as liquid surface alight | Plot E on a **separate map or post-reset** with `ActiveFluid=RM_Fluid_Tar`, `liquidIgnitionEnabled=true` (non-default). Fill 1×8 D=1 channel from a limited tar pond; ignite mouth cell (driver: `ignite_cell`). Step 600 ticks. Predicate: ≥3 channel cells carry Fire. Fire-safety isolation: 8-cell non-flammable (bare Soil, plants wiped) moat round the plot; `jawa/clear_area` of plants first. | play zoom | live | UNCERTAIN (ignition premise UNMEASURED — build program Phase 6 flags `About.xml`'s "vanilla ignition already works" as unverified prose) |
| `canal_fire_reaches_reservoir` | fire present at the reservoir, not only the channel | Plot E continued, step until a reservoir cell has Fire (budget 6,000 ticks). | play zoom incl. pond | live | UNCERTAIN |
| `canal_spent_after_burn` | burned-out channel reads scorched and empty, not merely dry | Plot E, step until no Fire in plot (budget 60,000 ticks — burn is "one canal tier per day"). Predicate: F=0 on burned cells. | play zoom | live | NO (no third channel state art) |
| `slime_reads_as_viscous_not_water` | slime opaque and viscous, never tinted water | Plot F, `ActiveFluid=RM_Fluid_SlimeGreen` (map-wide, so separate map/reset), fill a 1×6 D=1 channel by `setFill`. Water control channel would need a second fluid on the same map — impossible today; the control is a stored reference PNG of the water fill from Plot C. | play zoom | live | UNCERTAIN |
| `slime_occupant_below_surface` | pawn in a slime canal not drawn standing on the surface | Plot F, D=3 slime run; spawn a colonist, order into the middle cell, step 300 ticks; predicate pawn position is in the run. | play zoom, pawn centred | live | **NO** (no depth draw offset) |
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
| `pit_depth_ladder_legible` | 🆕 approved + strengthened by his depth ruling | Plot H: five adjacent 2×3 pads at D=0..4 in one row; then a colonist walked across all five (frames at D=1 and D=4 → diptych for "rises and lowers") | **NO** (one Gravel texture for every depth; no draw offset) |
| `pit_occupant_below_floor` | kept; absorbs `pitcell_occupant_visible` (merge, flag) | Plot G: hostile-faction pawn spawned beyond, walked/ordered in; predicate superdeep capture (`superdeepCaptureEnabled`) — pawn despawned into the hidden `RM_SuperdeepPit` holder OR present below the lip, whichever the shipping model does | NO |
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

⚠️ A bar that cannot be evaluated must not be filed as a binding bar (the spec's own rule). The
BLOCKED rows above go to him **marked as blocked**, with the choice: validate now and accept REFUSED
until built, or park them as `### candidate lines` until their feature lands. That is his call, so it
is a question in the re-validation item, not a decision here.

### 2.5 State-only components (no `shows`), needed for the toggle floor

The floor refuses a run while any Mod Settings toggle has no covering component. 27 toggles,
MEASURED. Each gets one component, toggle named, with a positive predicate (on) and — where the
setting can flip live via `jawa/mod_settings_field` (static fields, `RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings`
/ `RimMandrake.FlowWorks.Pits.PitsSettings` / `…ManyWaters.RiverSteamSettings`) — a negative
predicate (off). Grouped:

- **Engine:** `depthEngineEnabled` (off ⇒ F frozen across 4 pulses), `channelConfinementEnabled`,
  `digToDepthEnabled`, `edgeSinksEnabled` (channel reaching edge ⇒ `sinkTransferredTotal` rises),
  `fillInEnabled` + `fillInDisplacementEnabled` (fill-in returns liquid to neighbours, Σ conserved).
- **Stock:** `sourceBudgetEnabled` (limited pond stops supplying at 5 cells per source cell × multiplier),
  `stickyLimitlessEnabled`, `recessionEnabled`, `refillEnabled` (limited pond stock rises over N pulses
  with no draw), `rainFillsExcavationsEnabled` (**only component that turns rain ON**: unroofed D=1 cell
  gains F under forced rain; roofed twin stays F=0 — the roof rule).
- **Fire / corrosion:** `liquidIgnitionEnabled`, `liquidCorrosionEnabled` (both default false).
- **Superdeep:** `superdeepCaptureEnabled`, `superdeepCapturesOwnFaction` (default false: colonist
  crosses unharmed), `ladderRequiredToExitEnabled`, `superdeepShootingRuleEnabled` (occupant invalid
  ranged target except from 8-adjacent lip).
- **Containers / drilling / shores:** `bottleLoopEnabled`, `bottleDirtyStageEnabled`, `tankLoopEnabled`,
  `liquidDrillingEnabled`, `typedLiquidShoresEnabled` (mapgen — **worldgen-affecting, needs a fresh
  map**; mark it so in the suite).
- **Pits (building-era, still shipping):** `trapTriggerEnabled`, `fallDamageEnabled`, `escapeEnabled`,
  `pitCellExposureEnabled` — the existing two chains, rewritten to the new plot scheme.
- **RiverSteam:** `riverSteamEnabled` — needs a river map; a quicktest map may have none ⇒ that
  component runs on its own map (§4).

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
  holding the bridge runs it, and `restore_full()` restores `ModsConfig.FULL.LATEST.xml` — confirm
  that file is current (it must contain the same mods as the live list, minus `mandrake.rm.pits`)
  **before** the swap, or the restore silently changes his list.
- `modset_builder.py --apply` refuses while `Player.log` was touched in the last 3 minutes ⇒ kill
  first, then swap.

### 3.2 Deploy freshness
- `deploy_custom_mods.py --mod FlowWorks` dry run reports `in sync` (MEASURED in sync today).
- Deployed `Assemblies/RimMandrakeFlowWorks.dll` sha == repo sha, and `.srchash` == repo `.srchash`,
  and `dll_source_stamp.py` agrees the srchash matches `Source/` at HEAD (a DLL stale against its own
  source is the classic false-fail).
- JawaBench companion deployed DLL carries `JawaBenchFlowWorksTools` (assert the three tools below
  register — §3.9 P-B3).
- The DLL can't be written while the game runs: deploy before launch.

### 3.3 Mod Settings state
- Read every field of the three settings classes via `jawa/mod_settings_field get` and compare to the
  **shipped defaults** table (§2.5). Any drift ⇒ refuse (a previous session's live toggle persists in
  `ModSettings.xml` only if written; static writes do not persist — but a hand-edited settings file
  does). Record the full snapshot into the run sheet.
- Components that need a non-default value set it, read it back, and **restore it in a `finally`** —
  the next component must start from defaults.

### 3.4 Save, map, plots
- **Map:** a dedicated, saved **trial site**, built once by `prep_site.py` and reloaded per run
  (`rimworld/load_game_ready`) — not a fresh quicktest every run, because quicktest biome, terrain,
  water and rivers are random. Built from `rimworld/start_debug_game_ready` on the `flowworks` tier.
  Size ≥ 200×200 (MEASURED once: a quicktest map was 174×174 — record the real size). Save name
  `NS_FlowWorks_TrialSite_v1`; back up the Saves folder first and stat it after save (the
  `save_game` wrong-slot trap).
- **Ground:** every plot cell and its buffer painted `Soil` with `jawa/set_terrain_batch`; assert
  via `jawa/get_terrain_batch` that 100% of plot+buffer cells read `Soil`, **base AND temp layer**
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
- **Bodies:** authored reservoirs painted at prep, before any dig — then **never touched by another
  bar**. Body classification is sticky and stock is saved, so a body debited by one bar is wrong for
  the next. Each stock bar gets its own pond; the run reloads the save rather than reusing a body.
- **Fog:** `jawa/set_fog` off for plots only (⚠️ CAI's unfogAll wedges the game — never unfog the
  whole map).
- **Home area/zones:** none over plots (colonists would haul/clean there).

### 3.5 Temperature and freezing
- Biome temperate (TemperateForest or AridShrubland), season **mid-summer**: `jawa/time_set_ticks`
  to a summer quadrum day.
- Assert `jawa/cell_temperature` ≥ **+10 °C** at every plot centre at prep **and again before every
  liquid bar** (vanilla freezing turns water terrain to ice and would read as a fill that vanished
  or a channel that reads as ice). Refuse below.
- Assert ≤ +45 °C as well (heatstroke on test pawns; boiling-water terrain exists in this mod).
- No `GameCondition` that moves temperature (cold snap, heat wave, volcanic winter, toxic fallout):
  `jawa/game_condition` list = empty; remove any found.

### 3.6 Weather, rain, incidents
- 🔴 **Rain adds liquid** (`rainFillsExcavationsEnabled` default TRUE, `rainFillPerPulse` 0.1 per pulse
  on unroofed excavations). Force `Clear` with `jawa/weather_set`, zero the buildup
  (`jawa/set_weather_buildup`), and assert `jawa/weather_get` = Clear **before each liquid bar and
  after its settle** (a weather roll mid-bar invalidates it — FAIL with `WEATHER_CHANGED`, re-run).
  Rain is turned on in exactly one component, deliberately.
- Incidents off: `jawa/incident_queue_clear`, storyteller to a no-incident setting or god mode
  `rimworld/set_god_mode` — a raid, manhunter pack, flashstorm (fire!) or infestation would wreck a plot.
- No lightning near Plot E's moat.

### 3.7 Time, light, speed, RNG
- Paused at all times; advance only with `rimworld/step_game_ticks` in pulse multiples.
- **Screenshots at noon** — `jawa/time_set_ticks` to hour 12 before each shot (dark frames have
  failed review shots before). Read back the clock (`jawa/time_clock`). Ticks stepped for a settle
  move the clock, so re-pin after stepping.
- `jawa/time_perf` sanity: the step rate is measured at preflight; a bar's tick budget is converted
  to a wall-clock timeout from that measurement, not guessed.
- **Pulse phase:** read `nextPulseTick` relationship by stepping to a pulse boundary first (step until
  an F change is observed on a sentinel cell, or step `PULSE` ticks from a known state) so "pulse 1"
  means the same thing every run.
- **RNG:** flow and stock are deterministic; capture, escape, fire spread and weather are not.
  Stochastic predicates run **N=3 independent spawns** (memory: "spawn many — one pawn's result can
  be pure RNG") and pass on a stated threshold, never on one roll.

### 3.8 Pawns, modals, camera, UI
- Exactly the pawns the bar spawns. Colonists from the quicktest start are moved into a walled,
  roofed holding room ≥ 30 cells from any plot, drafted, so they never path through a plot.
  `superdeepCapturesOwnFaction` defaults false — a colonist test pawn is NOT captured; capture bars
  use a **hostile-faction** pawn, steered with `jawa/order_pawn` (MEASURED earlier: hostile steering
  is unreliable ⇒ the driver needs a "force job / place pawn at cell" call, §6).
- Pawn needs: no mental break mid-test — god mode or full needs on spawn.
- Stale modals block every later call: `jawa/clear_ui` + assert no open window before each bar.
- `jawa/screenshot_mode` / labels off, selection cleared, hover cleared before each shot.
- Camera zoom: "play zoom" and "max zoom" are fixed numbers recorded at prep from `get_camera_state`,
  not "whatever it was".
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
| P-S1 | plots: terrain Soil (base), temp none, D=0, F=0, roof none, things none | dirty cell |
| P-S2 | authored reservoirs present, cell counts match sidecar, `isSourceCell` true, untouched (no body yet, or stock == capacity) | otherwise |
| P-S3 | map-wide: `excavatedCellCount`=0, no `RM_FluidCanalFlood`, `sinkTransferredTotal`=0, `overflowDestroyedTotal`=0 | nonzero |
| P-E1 | weather Clear, buildup 0, no temperature-moving GameCondition, incident queue empty | otherwise |
| P-E2 | every plot centre 10–45 °C; season summer; clock pinnable | otherwise |
| P-E3 | game paused; step rate measured; no open window; dev mode on; god mode as designed | otherwise |
| P-E4 | holding room: all start colonists inside, drafted | otherwise |
| P-E5 | a calibration shot at a fixed empty plot passes the luma/variance gate and is not the menu | blank/black |

Between bars the driver runs **`isolate(plot)`**: assert the previous plot's state is confined to its
rect (ring scan = clean), restore settings to defaults, re-run P-E1/P-E2/P-E3. On any isolation
failure: reload the trial-site save rather than continue (contamination is never "probably fine").

---

## 4. Run sequence and wall-clock

All times UNMEASURED estimates except where marked; the first run records real ones into the sheet.

| # | step | where | est. |
|---|---|---|---|
| 0 | Offline preflight P-O1..O4; `run_selftests.py` green | WSL | 1 min |
| 1 | `rimflow bridge take`; kill game; `modset_builder --tier flowworks --apply`; launch via Steam | Desktop | load: minimal list with 5 DLCs UNMEASURED (22 s was MEASURED on a 13-mod no-DLC list; the DLCs add real load) — budget 3 min |
| 2 | `load_game_ready NS_FlowWorks_TrialSite_v1` (first time: `prep_site.py` builds + saves it, ~5 min) | bridge | 1–2 min |
| 3 | Live preflight P-L/P-B/P-S/P-E | bridge | ≤ 30 s with the fast driver |
| 4 | Toggle-floor components (27), mostly state-only, ≤ 8 pulses each | bridge | ~10 min (ticks dominate: ~27 × 2,000 ticks) |
| 5 | Canal visual bars (Plots A–D), water map | bridge | ~10 min; `reservoir_fill_visibly_drops` 40-pulse budget = 10,000 ticks |
| 6 | Reload save → set `ActiveFluid` tar → Plot E fire bars (burn-out budget 60,000 ticks) | bridge | ~15 min, dominated by step rate |
| 7 | Reload → slime → Plot F | bridge | ~5 min |
| 8 | Reload → superdeep / pit Plots G, H (N=3 captures) | bridge | ~8 min |
| 9 | RiverSteam component on a river quicktest map | bridge | ~4 min |
| 10 | `release` bridge; restore FULL list (unconditional `finally`) | — | 1 min |
| 11 | Judge: ~30 shots × `claude -p` vision, **run in parallel, off the bridge** | WSL | ~5 min parallel (30–60 s each serial) |
| 12 | Sheet → owner's one review → `rimflow verify FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1 …` | — | his time |

**GREEN-minimal pass ≈ 70–80 min wall-clock** end to end, most of it in ticks for fire and stock.
**GREEN-full** repeats 2–11 on the full list after a **~15 min cold load** (MEASURED 2026-09-07 on 599
mods) and with `mandrake.rm.pits` gone; on the full list the full-list risks are other mods'
weather/incidents/temperature and terrain patches — preflight catches them.

---

## 5. Gaps that block SHIPPED

1. **Bar roster incomplete** — pit bars not in FlowWorks.md; re-validation owed (§7).
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
   `set_active_fluid(map, defName)` (**new JawaBench tool needed**: `ActiveFluid` setter via reflection),
   `ignite_cell(cell)`, `body_report(cell)` (stock, capacity, limitless, cell count — **new tool**:
   no bridge read of `RM_LiquidBody` exists).
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

---

## 7. Proposed bar-text changes — need his re-validation (not applied here)

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

Filed for FOUNDRY (§ items list in the rung table below — see the ledger for live state):

| item | rung | acceptance |
|---|---|---|
| `FLOWWORKS_NORTHSTAR_TRIAL_1` | parent | every child closed; `modcheck status FlowWorks` = GREEN on full list; SHIPPED criteria in §5 met |
| `FLOWWORKS_NORTHSTAR_REVALIDATE_1` | VALIDATED (re) | owner validates the merged section (§7) in a sitting; `northstar.parse` VALIDATED with new hash; `Pits.md` deleted; `Pits` status key forgotten |
| `FLOWWORKS_NORTHSTAR_WIRE_1` | WIRED | `validation.py` rewritten (§2.3–2.5); `floor --all` FlowWorks row: 0 uncovered, 0 orphans, 27/27 toggles; diptych + framed shot used; walk steps 4–6 rewritten; selftests green |
| `FLOWWORKS_NORTHSTAR_SITE_PREP_1` | site | `prep_site.py` builds + saves the trial site; `preflight_flowworks.py` implements §3.9 and has refused a deliberately dirtied site at least once (proof it can fail) |
| `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` | GREEN-minimal | one full run on the `flowworks` tier with preflight clean; sheet produced; `rimflow verify` recorded (pass or fail — a RED run is a valid first result); owner reviewed the sheet once |
| `FLOWWORKS_NORTHSTAR_GREEN_FULL_1` | GREEN-full | same on the full list after `PITS_STALE_DEPLOY_COLLISION_1` |
| `FLOWWORKS_NORTHSTAR_SHIP_1` | SHIPPED | 0 DIRTY files; Mod Settings superb checklist (§5.7); art for every visual bar; deploy in sync; doors and pit collapse closed or their bars parked by his word |
| `PITS_STALE_DEPLOY_COLLISION_1` | blocker | `mandrake.rm.pits` absent from live + FULL.LATEST list; `Mods/Pits/` retired; Player.log has no duplicate pit defNames |

---

## 9. GPT review

(filled after the review ran — see below)
