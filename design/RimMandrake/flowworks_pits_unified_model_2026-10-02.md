# FlowWorks + Pits — one model (2026-10-02)

> Owner, 2026-10-02: *"We absorbed a mod called Pits into FlowWorks. I have this weird feeling that
> now there's a 'pit' building floating around inside Flowworks canals... even though a pit is just a
> 1 square canal. There's no 'pit' as a special thing, it's just a channel/canal dig. Right?"*

## 1. Verdict

**He is right, and the "floating building" is real.** MEASURED 2026-10-02 from source:

- `RM_SuperdeepCapture.EnsureHolder` spawns one hidden **`RM_SuperdeepPit`** Thing (label
  "superdeep excavation", `thingClass Building_SuperdeepPit`, in
  `src/RimMandrake/FlowWorks/Defs/Canals/ThingDefs/FlowWorks_ThingDefs.xml`) on **every** D=4 cell,
  on dig, load and settings flip. `Building_SuperdeepPit : Building_OpenPit` — the old Pits
  building — and on capture it **despawns the pawn into a container** (`innerContainer`) and runs
  the old struggle-escape clock. That is the "pit building floating around inside the canal".
- It was built in FlowWorks Phase 5 (`52e312a15`, 2026-09-17), hours **before** his collapse ruling
  that same day, under the older ruling-26 argument ("reuse Pits' capture machinery"). The collapse
  ruling (`PIT_SUPERDEEP_COLLAPSE_1`) removed that premise; nothing has been rebuilt since.
- Alongside it the whole old Pits mod still ships in FlowWorks: **21 pit ThingDefs/abstracts**
  (`Defs/Pits/`), 3 hediffs, the `RM_DigPitDeeper` designation/job/workgiver, a second `Mod`
  subclass with its own settings screen (`PitsMod.cs`), and **20 `.cs` files** in `Source/Pits/`
  of which exactly one reads the canal depth grid.

**So the unified answer is: a pit is any canal cell dug to SUPERDEEP (D=4). Nothing else.** No pit
Thing, no holder Thing, no pit dig chain. What a player *adds* to that cell — spikes, a ladder, a
cover, a sluice/grate door at its mouth, a prisoner bed in the enclosed room — is ordinary
buildable stuff on a canal bottom. What *fills* it is a FluidDef. Everything below hangs off that.

His words today, 2026-10-02, are treated as the ruling on the one question the 2026-09-17 spec left
open (§9, "does a per-D=4-cell holder Thing survive at all?"): *"There's no 'pit' as a special
thing, it's just a channel/canal dig."* ⇒ **No holder Thing.** The fall/trap state is a grid fact.

## 2. Sources read and their current state

States are from `rimflow show` on 2026-10-02 (items decay; re-check before acting).

| Source | State | Role in this model |
|---|---|---|
| `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md` | proposed, BENCH, needs offline | **The authority.** Rulings of 2026-09-17, three card rounds, all ten spec §9 questions answered. Unbuilt. |
| `design/RimMandrake/pit_superdeep_collapse_spec.md` | design doc | Predates the three card rounds; its §2 file-by-file table is still the best inventory and is adopted below with the item's corrections. |
| `infrastructure/state/items/FLOWWORKS_DOOR_FAMILY_1.md` | proposed, BENCH | Two stuffable doors (`Sluice`, `SecurityGrateDoor`). Kept; folded into the build order. |
| `infrastructure/state/items/FLOWWORKS_BUILD_PROGRAM_1.md` | doing, FOUNDRY | Phases 0-9. Phase 5 and Phase 9 and two Watch-out lines described the pre-collapse pit; corrected in place (§5). |
| `infrastructure/state/items/NORTH_STAR_PIT_PILOT_1.md` | proposed, BENCH, needs owner | Its spec steps targeted the deleted `Pits.md` walk and the non-existent `src/RimMandrake/Pits/validation.py`. Superseded (§5). |
| `FLOWWORKS_NORTHSTAR_{TRIAL,SITE_PREP,BASELINE_RUN,GREEN_MINIMAL,GREEN_FULL,SHIP}_1` | proposed | The FlowWorks north-star ladder. Unchanged in shape; the pit bars ride it. GREEN_FULL/TRIAL cite `PITS_STALE_DEPLOY_COLLISION_1` as a blocker, which closed at `bd8d58dbb`. |
| `FLOWWORKS_CHANNEL_OSCILLATION_1` | open (another helper is on it) | Flow never fills east/north. Everything that needs liquid in a pit waits on it (§6). |
| `HUTT_SLAVE_PIT_TEST_SITE_1` | proposed, FOUNDRY | Its "oubliette" is a sealed map feature at a Hutt site, **not** the cut oubliette fitting. Under this model it is simply an enclosed superdeep room with no ladder — noted in the item. |
| `SARLACC_HABITAT_BUILD_1` | doing, blocked | A sarlacc "pit" is a creature's lair, not a FlowWorks pit. Out of scope; not touched. |
| Closed: `RIMMANDRAKE_PITS_BUILD_1`, `PITCELL_PRISONER_BED_BRIDGE_GAP_1`, `PIT_TRAP_VISUAL_REDESIGN_1`, `MOD_VALIDATION_PIT_PILOT_1`, `PITS_STALE_DEPLOY_COLLISION_1`, `FLOWWORKS_NORTHSTAR_REVALIDATE_1` | terminal | Read for provenance. The 12 pit bars are already rewritten and VALIDATED inside FlowWorks' walk (2026-10-01). |
| `design/RimMandrake/flowworks_mod_definition.md`, `flowworks_liquid_matrix.md` | design | Rulings 17-29 (D/F primitive = 18, four depths = 19, shooting = 23, source = 24, rain = 25, superdeep captures as if dry = 26, fill-in destroys = 29). |

**Savegame exposure — MEASURED 2026-10-02:** of the **41** `.rws` files in the owner's Saves folder,
**0** contain any of `RM_OpenPit_*`, `RM_PitDigSite_*`, `RM_PitCell_*`, `RM_SuperdeepPit`,
`RM_Ladder`, `RM_PinnedInPit`, `RM_PitExposure`, `RM_PitDrowning` (searched as `<def>NAME`;
sanity probe: `<def>Wall</def>` found in 41 of 41, `<def>RM_` in 36). So **retiring every pit Thing
breaks no existing save**, and the world-remake-is-last ruling makes future saves cheap anyway.
The canal *terrains* are shortHash-encoded in saves and were not measured; they are all KEPT, so it
does not matter.

## 3. The unified model

Every line here is one of his rulings (item `PIT_SUPERDEEP_COLLAPSE_1` unless noted) or is marked
**DEFAULT** — a gap filled by this pass, reversible, listed in §7.

### 3.1 The primitive — one cell, two numbers, one per-depth field

- **D** = depth 0-4 (surface, shallow, mid, deep, SUPERDEEP). Set only by digging and filling in.
  We dig down, never build up (LAW 1). `RM_ExcavationDepth` owns it.
- **F** = fill, `0 ≤ F ≤ D`, of a **FluidDef**. The fluid's identity is held **per liquid body**, not
  per cell or per map ([F]); the per-map `ActiveFluid` field retires.
- **Max body size per depth** ([J]): a field on the depth, so a shallow cut cannot hold what a
  superdeep one can. The same `BodySize` also scales spike damage ([G]) — a deliberate pairing.
  ⚠️ Since only D=4 holds anything (answer 2), the field matters only at D=4. **DEFAULT: no limit at
  D=4**, which makes [J] inert in play until he says otherwise — Q4.
- **LAW 2** (depth reads only movement and liquid) carries **two** stated, narrow exceptions:
  ruling 23 (a D=4 occupant trades fire only with its 8 neighbours — already built, reads the grid)
  and [D] (depth may bound a room). Worded so it is not a precedent for anything else.

### 3.2 What "a pit" is

**A pit is any connected set of D=4 cells.** "Pit" is a player's word for a shape, like "moat" or
"terrace". There is no pit def, no pit Thing, no pit holder, no pit dig job: you designate
"dig canal" until the cell reads SUPERDEEP. A one-cell pit is a one-cell canal dug to 4.

| Depth | Holds a pawn? | Movement |
|---|---|---|
| D 1-3 | **No.** Movement cost only. | dry cost rising with depth; **flooded strictly costlier than dry at the same depth** — the depth × fill-tier matrix [E] |
| D 4 | **Yes, absolutely.** No climb-out, no roll, no skill check. | walking in is allowed (that is how you fall in); walking out is vetoed |

**The trap rule, as a grid fact (not a container):** a *spawned* pawn on a D=4 cell may not step to
any cell with lower D, unless (a) a **lowered ladder** stands in its cell, or (b) it leaves through a
**door/sluice opened from outside**. The pawn stays spawned, standing on terrain — which is what lets
it be in a room, feel temperature, be shot at from its lip, and be captured from above. Seam:
reachability veto (no job is ever taken that needs leaving) plus a hard per-move floor
(`RM_SuperdeepTrapUtility`, proposed in spec §3); the patch seam is measured on the Desktop first.

### 3.3 Getting in

All four routes are a **descent** (previous cell's D < this cell's D) and all fire the same entry
event: mass-scaled blunt fall damage (existing `fallDamageEnabled`/`fallDamageMultiplier`), then
spikes if the cell has them.

1. **Walking in** over the lip. Own-faction carve-out stays a Mod Setting
   (`superdeepCapturesOwnFaction`, default off) so a builder can place the ladder.
2. **Through a cover** that gives way under mass — the existing cover tiers (40/120/220 kg, his
   220) are kept unchanged.
3. **Pushed or blasted in** — anything that moves a pawn against its will (weapon blowback).
4. **"Jump into pit"** gizmo — voluntary, warns and confirms, strands the jumper too.

### 3.4 Things built on the canal bottom (or at its mouth)

All are ordinary buildables with a placeworker that requires an excavated cell. None is "a pit".

| Thing | Where | Rule |
|---|---|---|
| **Spikes** (`RM_Spikes`, new) | ON a D=4 cell | Per-cell. Fire on **any descent** into that cell, never on walking up to them or moving along a spiked floor between D=4 cells. Massive **Sharp** damage through the normal pipeline (armour applies, no instant death), scaled with `BodySize` [G]. The number is proposed with reasoning for his word — never presented as his. The art must show *some* spike at the pit's viewing angle. |
| **Ladder** (`RM_Ladder`, exists) | ON a D=4 cell | Lowered = exit open; **raised = exit shut** — "like opening a prison door". Today it is presence-only (build/deconstruct); a raise/lower toggle is owed. Still wears the vanilla spike-trap texture — art owed. |
| **Cover** (rehoused terrain-mimic + mass trigger) | OVER D=4 cells, multi-cell | Hides the hole; gives way under mass so pawns fall in involuntarily. |
| **Sluice** (`FLOWWORKS_DOOR_FAMILY_1`) | at a canal mouth | Stuffable door. Passes liquid while closed. Holds small creatures only. Openable from outside or above, never from inside a D=4 cell. Releases a held mech when you choose [C]. |
| **SecurityGrateDoor** (same item) | at a canal mouth | Stuffable door. Passes liquid while closed. Holds a real prisoner. Same open-from-outside rule. Stuff decides armour and fire survival — a wooden one burns, by design. |
| **Prisoner bed** (vanilla) | inside an enclosed D=4 area | Turns the room into a prison room on vanilla's terms. |

### 3.5 What fills it — fluids, never fittings

Water, oil, poison, tar, slime and the rest are **FluidDefs**, entering by flow (a sluice, a breach,
rain on an unroofed cut). There is no "water pit", "oiled pit" or "poison pit".

- **F > 0 at D=4 drowns** a non-swimmer — `RM_PitDrowning`, keyed to fill; its `CanSwim` check
  (swimming graphic, not an "aquatic" substring) moves with it.
- **Oil** stays ignitable; fire on a body with an occupant must know the occupant is there.
  Oil + ignition is a real kill route, separate from the capture route.
- **Poison**: its toxin is keyed to fill, not to a comp.
- 🔴 Every liquid-in-a-pit behaviour waits on `FLOWWORKS_CHANNEL_OSCILLATION_1` (east/north canals
  never fill). Nothing liquid can be proven until flow fills in every direction.

### 3.6 Rooms, prisoners, capture

- An **enclosed D=4 area is a room** [D]. Bare, it holds **trapped enemies**, not prisoners. With a
  **prisoner bed** it is a **prison room**.
- **Capture down** and **convert down** are done **from the lip**, warden **adjacent** [B-item].
  Nobody ever has to enter. The accepted risk: an armed occupant can shoot an adjacent warden
  (ruling 23 permits exactly that exchange).
- A trapped hostile **mech** is a stored asset — killable from the lip, or released through a
  sluice when wanted [C]. No anti-mech fitting replaces the cut oubliette.

### 3.7 Temperature — the softening mechanism

- Pit cells couple to outdoor temperature **harder** than a roofed room: desert sun heats an open
  pit fast; a cold night chills it.
- Two independent dials [H]: vanilla **Heatstroke/Hypothermia** do the physical harm;
  **`RM_PitExposure`** is the accumulator that drives resistance (recruitment first, then will) down.
- It is cruel and reads as cruel: an **"Exposed Prisoner"** thought that compassionate pawns feel
  and psychopaths and hard-morality cultures do not, **copying vanilla's beggar-rejection
  structure** — no new moral axis [A-item]. Numbers and exact def shape return to him.

### 3.8 Filling in

`Designator_FillInCanal` lowers D. On a D=4 cell that removes the pit by definition (ruling 29's
"fill destroys the pit" becomes trivially true — there is nothing else to destroy). **DEFAULT:**
spikes and ladders on a cell being filled are uninstalled to their materials first, like vanilla
deconstruction; fill-in on a cell with a pawn standing in it is refused until the pawn is out.

### 3.9 Cut, and stays cut

The oubliette / ion charge; the water, oiled and poison "fittings"; the rival
Shallow/Deep/Chasm dig ladder; `RM_OpenPit_*` and `RM_PitCell_*` as buildings; the pit's own dig
chain; the hidden per-cell `RM_SuperdeepPit` holder; the struggle-to-escape roll; pawns despawned
into a container; any def on `Things/Building/Security/TrapSpikeArmed`.

## 4. Every old pit def / class / hediff / job / test: KEEP / REWIRE / RETIRE

KEEP = stays as is. REWIRE = the behaviour survives and moves onto the canal-bottom model.
RETIRE = deleted. **Save impact for every RETIRE row: none measured** — 0 of 41 saves hold any of
these defs (§2). A save that did hold one would log "Could not load reference" and drop the Thing
(and any pawn inside a holder's container would be lost with it); with no world shipped yet and the
remake last, that is accepted.

### 4.1 C# — `src/RimMandrake/FlowWorks/Source/Pits/` (20 files) and neighbours

| File | Verdict | Reason |
|---|---|---|
| `Pits/Holding/Building_OpenPit.cs` | RETIRE | The building-that-holds-a-pawn model, with its container, struggle clock and single drawn pawn. |
| `Pits/Holding/Building_PitCell.cs` | RETIRE | Replaced by a real room + vanilla prisoner bed; vanilla wardens feed and tend. |
| `Pits/Escape/PitEscapeUtility.cs` | RETIRE | "You can't climb out. Period." — no roll exists at any depth. |
| `Pits/DigStage/` — `Building_PitDigSite`, `CompPitDigStage`, `CompProperties_PitDigStage`, `JobDriver_DigPitDeeper`, `WorkGiver_DigPitDeeper` | RETIRE (5) | The pit's own dig chain. FlowWorks' `JobDriver_DigCanal` already digs and is already `MiningSpeed`-scaled (MEASURED, line 37), so nothing is re-priced. |
| `Pits/DigStage/PitDepthTier.cs` | RETIRE | The rival ladder. Its `MaxBodySize` idea REWIRES onto `RM_ExcavationDepth` as the per-depth field [J]. |
| `Pits/Fitting/CompPitFitting.cs` | RETIRE | Fittings collapse to spikes alone. Its `OccupyingLiquid()` query is lifted into the drowning-on-fill code; its `Stab` hit and `spikeDamage = 25f` default are the starting point for `RM_Spikes` (to be re-tuned: Sharp, BodySize-scaled). |
| `Pits/Fitting/CompProperties_PitFitting.cs`, `PitFittingType.cs` | RETIRE (2) | Tuning for cut fittings; a one-member enum is not a model. |
| `Pits/PitsMod.cs` | RETIRE | A second `Mod` and settings screen inside FlowWorks. Survivors REWIRE into `RimMandrakeFlowWorksSettings`: `trapTriggerEnabled`, `trapSensitivityMultiplier`, `fallDamageEnabled`, `fallDamageMultiplier`. The rest die with their mechanics. |
| `Pits/RimMandrakePits_DefOf.cs` | REWIRE | Shrinks to the surviving hediffs and merges into `RimMandrakeFlowWorks_DefOf`. |
| `Pits/Debug/PitDebugActions.cs` | RETIRE | Debug actions on retired buildings. Replaced by cell-level debug actions (spawn pawn on D=4, force fall, toggle ladder) in `FlowWorksDebugActions.cs`. |
| `Pits/SelfTest/Program.cs` + `RimMandrakePits.SelfTest.csproj` | RETIRE | Tests the retired ladder's arithmetic. A new selftest covers the trap predicate and descent rule. |
| `Pits/TerrainMimic/Building_TerrainMimicCover.cs` | REWIRE | Keep `TerrainMimicPrinter` (already per-cell); drop the self-declared dead `Building_TerrainMimicCover` class. |
| `Pits/Trigger/CompPitCoverTrigger.cs`, `CompProperties_PitCoverTrigger.cs` | REWIRE (2) | The cover's mass trigger. Fires a fall instead of a despawn; its cells are the cover's own. |
| `Pits/Trigger/PitCoverTier.cs` | KEEP | 40/120/220 kg; 220 is his number. |
| `Superdeep/Building_SuperdeepPit.cs` | RETIRE | **The floating building.** Its entry detector REWIRES into a map component over the depth grid (descent event → fall damage → spikes). |
| `Superdeep/RM_SuperdeepCapture.cs` | RETIRE | Holder lifecycle (`EnsureHolder`/`HolderAt`/`SyncMap`). Its "why a building" header is the argument today's words overturn. |
| `Superdeep/RM_LadderUtility.cs` | REWIRE | `HasLadder` + placeworker stay; gains a raised/lowered state ("like a prison door"). |
| `RM_Patch_SuperdeepShooting.cs` | KEEP | Ruling 23. MEASURED: it reads `IsSuperdeepExcavation` on the grid, not the holder, so deleting the holder leaves it intact. |
| `RM_MapComponent_Excavation.cs`, `Designator_FillInCanal.cs`, `RimMandrakeFlowWorksMod.cs` | REWIRE (3) | Each calls into the holder or pit classes (`SyncMap` at lines 253/755, `EnsureHolder` at 399). The calls are removed; the trap/descent hooks are added here. The settings text "Falling in, ladders and shooting" is re-worded. |

### 4.2 Defs

| Def | Verdict | Reason |
|---|---|---|
| `RM_OpenPit_{Bare,Spiked,Oiled,Poison,Water,Oubliette}` (6) | RETIRE | Pits as buildings. Spikes return as `RM_Spikes`; the rest are fluids or cut. |
| `RM_PitDigSite_{Shallow_Bare,_Spiked,_Oiled,_Poison,_Water,_Oubliette, Deep_Bare, Chasm_Bare}` (8) | RETIRE | Rival dig ladder. |
| `RM_PitDigSite_Cell{Single,Double}` (2), `RM_PitCell_{Single,Double}` (2) | RETIRE (4) | Prisoner pit cell → room + bed. |
| `RM_PitDigSiteBase`, `RM_OpenPitBase`, `RM_PitCellBase` (abstract, 3) | RETIRE | The three `TrapSpikeArmed` texPath lines die here. |
| `RM_DigPitDeeper` Designation / Job / WorkGiver (3) | RETIRE | Dig chain. |
| `RM_SuperdeepPit` ThingDef | RETIRE | The holder. |
| `RM_Ladder` ThingDef | REWIRE | Kept; gains raise/lower; **art owed** (still `TrapSpikeArmed`, MEASURED line 103). |
| `RM_PitDrowning` HediffDef | REWIRE | Keyed to fill at D=4 instead of the Water fitting. |
| `RM_PitExposure` HediffDef | REWIRE | Kept by [H]; its writer becomes the temperature accumulator, its effect becomes lowered resistance. |
| `RM_PinnedInPit` HediffDef | RETIRE (**DEFAULT**) | It meant "you are inside the container". The terrain now says you are held; the fall injury is ordinary damage. |
| Canal terrains `RM_Channel_*`, `RM_Fill_*` | KEEP | The primitive. (`RM_Fill_Tar_Superdeep`'s old Impassable defect is already fixed — MEASURED Standable.) |

### 4.3 Tests, walks, tools

| Thing | Verdict | Reason |
|---|---|---|
| FlowWorks walk `design/validation_walks/RimMandrake/FlowWorks.md` `## north star` (pit groups) | KEEP | Already rewritten against the superdeep model and VALIDATED 2026-10-01. Not touched. |
| `src/RimMandrake/FlowWorks/validation.py` + `northstar/` plan rows that assert the holder (script plan S1 "holder exists", S7 "spawned=false, in the holder", S8 holder shed/regrown, O1 `RM_SuperdeepPit drawerType None`) | REWIRE (when the collapse lands) | True of today's code, so the first script may record them now; each **inverts** when the holder retires (S7 becomes "pawn stays spawned, cannot path out"). Owned by the collapse items, not changed in this pass. |
| Bridge tool `jawa/flowworks_pit_report` (script plan §bridge #3, reads the holder's `innerContainer`) | REWIRE | Should read the grid: D, F, fluid, HasLadder/raised, HasSpikes, room/prison status, occupants by position. |
| `bridgetools/JawaBench.BridgeTools/JawaBenchBedTools.cs` PitCell intake notes | REWIRE | Mentions PitCell gizmos that retire. |

**Counts.** C# (28 files incl. neighbours and the selftest csproj): **KEEP 2, REWIRE 8, RETIRE 18**
(the 20 under `Pits/` split RETIRE 15 / REWIRE 4 / KEEP 1; `Superdeep/` + shooting patch RETIRE 2 /
REWIRE 1 / KEEP 1; three core files REWIRE; the selftest csproj RETIRE). Defs (29): **KEEP 0 (+ the canal terrains), REWIRE 3,
RETIRE 26.** Tests/tools: **KEEP 1, REWIRE 3.**

## 5. Item hygiene done (2026-10-02)

| Item | Action | Proof |
|---|---|---|
| `NORTH_STAR_PIT_PILOT_1` | **superseded** by `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1` | Its spec validated the deleted `Pits.md` walk and wired `src/RimMandrake/Pits/validation.py`, which does not exist (`src/RimMandrake/Pits/` holds only `__pycache__`). The 12 bars are already in FlowWorks' VALIDATED north star; the falsification run it carried is the baseline run's stated value. |
| `FLOWWORKS_BUILD_PROGRAM_1` | **corrected** | Phase 5 said superdeep capture reuses `Building_OpenPit`'s container and struggle-escape clock — contradicted by the collapse ruling; Phase 9 told readers to `modcheck validate Pits` (walk deleted) and pointed at the superseded `PIT_TRAP_VISUAL_REDESIGN_1`; two Watch-out lines assumed pit *buildings* on canal cells; the design-doc filename `fluid_canals_mod_definition.md` no longer exists (it is `flowworks_mod_definition.md`). |
| `FLOWWORKS_NORTHSTAR_GREEN_FULL_1`, `FLOWWORKS_NORTHSTAR_TRIAL_1` | **corrected** | Both named `PITS_STALE_DEPLOY_COLLISION_1` as a blocker; it closed `done` at `bd8d58dbb`. |
| `PIT_SUPERDEEP_COLLAPSE_1` | **kept as the rulings record**; `## children` added | It is the cited authority (CLAUDE.md) — moving it to `closed/` would break that pointer. |
| `FLOWWORKS_DOOR_FAMILY_1` | kept; `## depends` added | Needs the grid trap rule and the oscillation fix. |
| `HUTT_SLAVE_PIT_TEST_SITE_1` | kept; one Watch-out line | Its "oubliette" is a map feature, not the cut fitting. |

**Left for FOUNDRY (not mine to edit):**
- `CLAUDE.md` says *"`NORTH_STAR_PIT_PILOT_1` is the falsification test and has never run"*. That item
  is now superseded; the line should name `FLOWWORKS_NORTHSTAR_BASELINE_RUN_1`.
- The script plan `design/RimMandrake/flowworks_northstar_script_plan_2026-10-02.md` rows S1, S7, S8, O1
  and bridge tool #3 (`jawa/flowworks_pit_report` reading the holder's `innerContainer`) describe the
  holder. They are true of today's code, so the first script may record them; they invert when
  `SUPERDEEP_HOLDER_RETIRE_1` lands. Whoever builds `flowworks_pit_report` now should read the grid
  (D, F, fluid, ladder, spikes, room, occupants by position) so it survives the retirement.

## 6. New work, in dependency order

All filed 2026-10-02 for FOUNDRY, `proposed`, `needs offline`, spec = this file. Each item file has
`## spec / ## verify / ## criteria / ## depends / ## northstar`. Model ladder per
`infrastructure/agents/Agent_Policy.md`.

| # | Item | What | Depends on | Waits on oscillation fix? | Changes if owner answers differently |
|---|---|---|---|---|---|
| 1 | `SUPERDEEP_SEAM_MEASURE_1` | Desktop RimSage reads: exit veto seam, room/region builder, door permission, room temperature, beggar thought, Prisoner Realism | — | no | — |
| 2 | `SUPERDEEP_HOLDER_RETIRE_1` | Delete the hidden holder; pawn stays spawned; grid trap rule; descent event; jump gizmo; per-depth body size | 1 | no (dry pits) | Q4 |
| 3 | `PIT_LEGACY_CODE_RETIRE_1` | Delete 26 pit defs + `Source/Pits/` building model; rehouse 4 toggles | 2 | no | — |
| 4 | `CANAL_BOTTOM_SPIKES_1` | `RM_Spikes` per-cell on the canal bottom, Sharp × BodySize on descent | 2 | no | Q2 |
| 5 | `LADDER_PRISON_DOOR_1` | Raise/lower from the lip; who may climb; ladder art | 2 | no | Q1 |
| 6 | `PIT_COVER_FALL_REWIRE_1` | Multi-cell cover; mass trigger drops pawns in | 2, 3 | no | — |
| 7 | `SUPERDEEP_PRISON_ROOM_1` | Enclosed D=4 = room; bed = prison; capture/convert down from the lip | 1, 2 | no | Q1 (who exits) |
| 8 | `PIT_TEMPERATURE_SOFTENING_1` | Hard ambient coupling; `RM_PitExposure` → resistance; Exposed Prisoner thought | 7 | no | — |
| 9 | `PIT_DEPTH_DRAW_OFFSET_1` | Pawn sinks/rises with D; D=4 walls 20% above head | 2 | no | — |
| 10 | `EXCAVATION_WALL_ART_1` | Wall faces for 4 depths, spikes, ladder (search artpipe first) | none to start | no | Q2 (spike art at shallow depths) |
| 11 | `DEPTH_FILL_COST_MATRIX_1` | Flooded always slower than dry at the same depth | — | no (defs) | — |
| 12 | `LIQUID_BODY_FLUID_IDENTITY_1` | Fluid per liquid body; merge rule | — | **yes** | Q3 |
| 13 | `PIT_FILL_EFFECTS_1` | Drowning at D=4, poison by fill, burning oil with an occupant | 2, 12 | **yes** | Q3 |
| — | `FLOWWORKS_DOOR_FAMILY_1` (existing) | Sluice + SecurityGrateDoor, stuffable | 2 | **yes** (liquid pass) | — |

**Northstar angle, in one line each** (full rows in each item's `## northstar`): every item's first
script is a **state** component on the minimal `flowworks` tier per `debug_process.md` §2 — the
pawn's spawned flag and reachability (2, 5), injuries by damage def after a forced descent (4, 6),
room id/role and warden position (7), temperature/exposure/resistance deltas against a roofed twin
(8), the draw offset read by a companion tool (9), a def-census inequality (11), fluid per body (12),
hediff severity by fluid (13). Frame-judged bars (art) stay with the owner-validated `## north star`;
none of these items edits that section.

## 7. Questions for the owner

Each has a recommended default; the work above proceeds on the defaults, and the last column of §6
says which item changes if he picks otherwise.

**Q1. When the ladder into a pit is let down, who can climb out?**
- **Like a prison door (recommended).** Your own people climb up and down freely; trapped enemies and
  prisoners cannot use it unless they stage a prison break. Pulling the ladder up locks everyone in,
  your own people too. *Trade-off:* matches "works like a prison cell" and lets you send a warden down
  safely; less literal, since an enemy standing at the foot of a ladder will not climb it.
- **Anyone below can climb while it is down.** *Trade-off:* simple and physical; but rescuing a
  colonist who fell in also lets every enemy in that pit out.
- **You choose per ladder who may use it**, like door permissions. *Trade-off:* most control; one more
  setting on every ladder to explain and manage.

**Q2. Can spikes go in any dug canal, or only in the deepest pits?**
- **Only in the deepest pits (recommended).** Spikes stay a pit feature; shallower canals are just
  slow ground. *Trade-off:* no cheap "spiked trench" defence line.
- **Any depth, and stepping down into a spiked canal of any depth hurts, more the deeper it is.**
  *Trade-off:* a strong new defence line of shallow spiked trenches; it competes with vanilla spike
  traps and makes your own canals risky for colonists.
- **Any depth, but shallow spikes only wound lightly; only the deepest pits kill.** *Trade-off:* a
  middle ground; one more damage rule to tune and explain.

**Q3. When you dig a channel joining a pit of water to a pit of oil, what should happen?**
- **They don't mix (recommended).** The joining channel stays dry until one pit is drained.
  *Trade-off:* simple and predictable; can feel like the game refusing what you dug.
- **The bigger pool wins.** The smaller pit's liquid is replaced by the bigger one's. *Trade-off:* easy
  to read; you can lose an oil trap by one careless dig.
- **They mix into a murky sludge** with weaker versions of both. *Trade-off:* realistic and messy; one
  more liquid to draw and balance.

**Q4. Should anything be too big to be held by a deepest pit?**
- **No — a deepest pit holds anything that falls in (recommended).** Size only decides how hard spikes
  hit. *Trade-off:* a thrumbo or a mech in a pit is completely stuck, which is very strong.
- **The very largest creatures (thrumbo-sized and up) can climb out.** *Trade-off:* keeps megafauna
  dangerous; breaks "you can't climb out, period" for them and adds a size limit to tune.
- **Big creatures are held only by a pit at least two cells wide.** *Trade-off:* realistic and rewards
  digging bigger pits; adds a footprint rule players must learn.
