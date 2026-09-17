# Pit → Superdeep collapse — design spec

**Status:** DRAFT, complete, awaiting his rulings on §9. **Item:**
`PIT_SUPERDEEP_COLLAPSE_1`. Written 2026-09-17 on the Mac laptop, offline.
**One sentence:** A pit is not a building; it is a SUPERDEEP excavated cell on the
D/F (depth + fill) primitive that FlowWorks already implements — this spec carries
the pit code and defs onto it.

**Evidence discipline:** every factual claim below is tagged CONFIRMED (read in this
repo, path given) or UNCERTAIN or UNMEASURABLE HERE (engine internals — no RimSage and
no def dump on this laptop). Identifiers that do not yet exist are written
`NEW: <name>` and need the owner's sign-off.

## 1. The model

The item's assembled table, restated as a contract and resolved against what the
code can actually do today. Column 3 is the resolution: what exists, what must be
built, what is unmeasurable from this laptop.

CONFIRMED — the primitive, read at
`src/RimMandrake/FlowWorks/Source/RM_ExcavationDepth.cs`:

- `RM_ExcavationDepth` is a `static class` in namespace `RimMandrake.FlowWorks`
  holding `Surface=0`, `Shallow=1`, `Mid=2`, `Deep=3`, `Superdeep=4`,
  `MaxDepth=Superdeep`, `WorkPerLevel=3200`.
- Superdeep's own doc comment already reads: *"Ruling 19: the trapping level"*. So
  this spec adds the mechanic to a slot the primitive already named.
- **LAW 1** is stated in the file: D is *"Set by digging, and by nothing else
  (LAW 1: we dig down, we never build up)"*.
- **LAW 2** is stated in the file: *"depth affects MOVEMENT and LIQUID and nothing
  else. It never affects sight, shooting, cover or projectile arcs — the one stated
  exception (ruling 23, a SUPERDEEP occupant may only trade fire with whoever is at
  their own lip) is a RESTRICTION on an existing check and is program 2's, not built
  here."*
- D becomes behaviour through **terrain**, not through a Harmony patch on the path
  grid: `DryTerrainFor(byte)` maps 1→`RM_Channel_Empty`, 2→`RM_Channel_Mid`,
  3→`RM_Channel_Deep`, 4→`RM_Channel_Superdeep`, and the comment says this is
  *"how an integer becomes a pathCost the vanilla pathfinder already honours
  (ruling 17's 30 at shallow, rising with depth) without a Harmony patch on
  PathGrid."* `DepthOfDryTerrain` is the inverse, used once per map to rehydrate
  old saves.
- `FillTier(fill, depth)` quantises F to ruling 5's three tiers against the cell's
  own D, so a brimming shallow trench and a brimming deep one both read as
  brimming. `0` means dry.
- F is bounded: the header says `0 <= F <= D`. **A surface cell therefore cannot
  hold fill at all**, which matters for the fluids section: oil and poison only
  exist inside excavation.

| Contract line (his) | Requirement | Resolution against the code |
|---|---|---|
| D = 4 traps absolutely | no climbing out, no check, no exception | `Superdeep` exists; the trap does not. Needs the exit rule of §3. Terrain `RM_Channel_Superdeep` exists as the carrier — CONFIRMED it is referenced by `DryTerrainFor`; its def body is read in §2. |
| D = 1-3 movement cost only | they hold nothing | Already true and already terrain-borne. **No work owed** beyond deleting the pit's rival ladder. |
| F > 0 at D = 4 drowns | drowning is the consequence of F rising on an occupant | F exists; a drowning consequence does not (see §6). Note the primitive's own bound: at D=4, F may reach 4. |
| F > 0 at D = 1-3 slows more than dry | a RELATION, not a per-depth constant | ⚠️ Today D→pathCost is a *terrain* lookup with one terrain per dry depth. A wet variant per depth is implied — the wet terrains are inventoried in §2. This is the one line of the table that constrains the *shape* of the terrain set, so it is a real design consequence, not a tuning number. |
| Fluids: water, oil, poison, + his list | fill is typed | `FluidDef` exists (§6). Oil/poison do not. |
| Spikes per-CELL | lethal only on a fall INTO that cell | The unit of hardware becomes the cell, matching D and F. Today it is a whole-building fitting (§7). |
| Cover conceals and enables involuntary entry | falling, pushed, blast/blowback | Cover machinery exists (`Trigger/`, `TerrainMimic/`) and is the strongest rehousing candidate in §2. |
| Sluice gate is a door | not from inside; yes from outside or above | Ruling 20 already names sluice gates as the built half. |
| Ladder raised/lowered | behaves like opening a prison door | NEW mechanism. Ruling 20 already names ladders; ruling 33's Quarry reference draws three of them on the walls. |
| Enclosed superdeep area = a ROOM | occupants are trapped enemies | 🔴 This is the line that strains LAW 2 — see §3. |
| + a prisoner bed = a real prison room | vanilla's own terms | §4. |
| Temperature strongly coupled to ambient | exposure swiftly lowers resistance; cruel | §5. |
| `capture down` / `convert down` | from the lip, never by entering | §4. Hard invariant: **any design requiring a pawn to enter is wrong**, because by ruling nobody who enters can leave. |

**The one-line consequence of the collapse:** a pit stops being a `Thing` with a
`texPath` and an inner `ThingOwner`, and becomes *a region of cells at D=4*. Every
identity question ("is this a pit?", "is this pit occupied?", "is this pit
covered?") stops being a field on a building and becomes a query over cells. That
is the whole of §2's work list and the reason several of the 12 bars in §8 cannot
survive unrewritten.

## 2. What retires, file by file

CONFIRMED by directory listing 2026-09-17: `Source/Pits/` holds **20 `.cs` files**
plus one `.csproj` (`SelfTest/RimMandrakePits.SelfTest.csproj`), and `Defs/Pits/`
holds **7 XML files carrying 24 defs** — 18 `ThingDef`s (which is the item's "all
18 pit defs"), 1 `DesignationDef`, 1 `JobDef`, 3 `HediffDef`s, 1 `WorkGiverDef`.

### 🔴 First, a thing the item does not mention and this spec must not overwrite

CONFIRMED: **`Source/Superdeep/` already exists**, outside `Source/Pits/`, with three
files — `Building_SuperdeepPit.cs`, `RM_SuperdeepCapture.cs`, `RM_LadderUtility.cs`
— plus `Source/RM_Patch_SuperdeepShooting.cs` at the root. FlowWorks Phase 5 already
built **most of today's ruling**, against rulings 26 and 20:

- `Building_SuperdeepPit : Building_OpenPit` (CONFIRMED, `Building_SuperdeepPit.cs`
  line 41) carries a per-tick detector copied in shape from vanilla
  `Building_Trap.cs` with **no `SpringChance`** — its own comment: *"there is no
  SpringChance here, because a four-level hole is not a concealed trap that might be
  spotted. Entering one takes you."* That is his "welcome to your pit" already coded.
- `RM_LadderUtility.HasLadder(map, cell)` + `PlaceWorker_LadderOnExcavation`
  (CONFIRMED) — the ladder is **one boolean**, deliberately: *"A ladder does NOT
  change pathing cost, passability, line of sight or the escape odds — it flips one
  gate, the same gate Building_PitCell's closed door flips."* That is his "ladder
  behaves like opening a prison door", already coded, and already unified with the
  prison-door reading he asked for.
- `RM_SuperdeepCapture.EnsureHolder / HolderAt` (CONFIRMED) — one holder Thing per
  D=4 cell, idempotent, spawned on dig and destroyed when the cell stops being D=4.
- Settings already exist on `RimMandrakeFlowWorksSettings`:
  `superdeepCaptureEnabled`, `superdeepCapturesOwnFaction`,
  `ladderRequiredToExitEnabled` (CONFIRMED by reference from
  `Building_SuperdeepPit.cs`).

🔴 **So this item is smaller than it looks, and its real content is a demotion, not
a build.** The gap is precisely that `RM_SuperdeepCapture`'s own header argues the
opposite of today's ruling:

> *"WHY A BUILDING AND NOT A GRID FLAG. Ruling 26 says FlowWorks writes no new
> capture or escape system, and the one that already exists — Pits'
> `Building_OpenPit` — is a Thing that holds pawns in a `ThingOwner`. […] The cost
> is one Thing per SUPERDEEP cell, which is the same cost vanilla pays per trap."*

Today's ruling removes that argument's premise. His answer 1 — *"It's just a room…
they're just trapped enemies"* — means an occupant is a **spawned pawn standing on
terrain inside a room**, not a Thing inside a `ThingOwner`. A pawn in a
`ThingOwner` is despawned (CONFIRMED: `Building_OpenPit.Spring` calls
`p.DeSpawn(DestroyMode.Vanish)` then `innerContainer.TryAddOrTransfer(p)`), and a
despawned pawn is in no room, has no temperature, and cannot be the target of a
`capture down` from the lip. **The container is the thing that must go**, and it is
the single largest deletion in this item.

⚠️ Consequence to state plainly: `Building_SuperdeepPit`, `RM_SuperdeepCapture`
and `RM_LadderUtility` are **not in the 20** but are all touched, because
`Building_SuperdeepPit`'s base class is being deleted under it. See the second
table.

### The 20 `.cs` files

Legend — **RETIRE**: delete, its behaviour either goes away or is re-expressed
elsewhere. **REHOUSE**: the mechanic survives today's ruling and moves out of
`Pits/` onto the cell model. **UNCHANGED**: stays as it is.

| # | File | Lines | Verdict | Why |
|---|---|---|---|---|
| 1 | `Debug/PitDebugActions.cs` | 442 | **RETIRE** | Debug actions against `Building_OpenPit`/`Building_PitCell` instances. The *pattern* worth keeping is that every mechanic has a method callable from the bridge, not only a gizmo lambda (its own stated reason). Rewrite against cells; nothing in the file survives as-is. |
| 2 | `DigStage/Building_PitDigSite.cs` | 20 | **RETIRE** | The pit's parallel dig chain. FlowWorks already digs: `Designator_DigCanal.cs`, `WorkGiver_DigCanal.cs`, `JobDriver_DigCanal.cs` at `Source/` root (CONFIRMED by listing). A pit is dug by digging to D=4. |
| 3 | `DigStage/CompPitDigStage.cs` | 152 | **RETIRE** | Same. Stage-count-to-depth is the rival ladder. |
| 4 | `DigStage/CompProperties_PitDigStage.cs` | 18 | **RETIRE** | Its `openPitDef` field ("the def to become once the final stage completes") is meaningless when the outcome is a terrain, not a def swap. |
| 5 | `DigStage/JobDriver_DigPitDeeper.cs` | 69 | **RETIRE** | ⚠️ Carry one thing across: this driver is **MiningSpeed-scaled, not ConstructionSpeed-scaled** (CONFIRMED, its own class comment: *"deepening an already-placed pit reads as digging"*), and it names itself the attach point for a future Jawa dig-speed bonus. Whether `JobDriver_DigCanal` scales the same way is **UNCERTAIN — not read in this pass**; check before deleting, or the collapse silently re-prices digging. |
| 6 | `DigStage/PitDepthTier.cs` | 79 | **RETIRE** | 🔴 The rival ladder itself: `Shallow=1, Deep=2, Chasm=3`. The item CUTs it explicitly. ⚠️ It is *load-bearing outside Pits*: `RM_SuperdeepCapture` sets `pit.DepthTier = PitDepthTier.Chasm` and `PitEscapeUtility.EscapeChance` takes it as a parameter (both CONFIRMED). Also carries `MaxBodySize` (1 / 2.5 / ∞) — a body-size gate on what a pit can hold that has **no equivalent in `RM_ExcavationDepth`**, and that today's ruling does not restate. Raised as an open question in §9. |
| 7 | `DigStage/WorkGiver_DigPitDeeper.cs` | 16 | **RETIRE** | Two lines of override; dies with its designation and job. |
| 8 | `Escape/PitEscapeUtility.cs` | 58 | **RETIRE** | 🔴 The biggest behavioural deletion. His words: *"you can't climb out. Period."* and his answer 2 (only superdeep traps; 1-3 hold nothing) leave **no depth at which a struggle roll exists**. So `StruggleIntervalTicks`, `EscapeChance` (bodysize/health/manipulation) and `ApplyFailedAttemptCost` all go, along with the *"a healthy thrumbo in a shallow pit is out in seconds and ANGRY"* feel the file was written for. The only way out is the ladder gate, which `RM_LadderUtility` already provides. |
| 9 | `Fitting/CompPitFitting.cs` | 171 | **RETIRE** | Five of six branches are CUT by his answers 6 and 7 (`Oiled`, `Poison`, `Water`, `Oubliette` leave; `Bare` was the absence of the comp anyway). `Spiked` survives but not here — spikes are per-CELL now, and this is a comp on a building. ⚠️ **REHOUSE one method**: `OccupyingLiquid()` is the only place in all 20 files that reads the primitive (`map.GetComponent<RM_MapComponent_Excavation>()`, `IsExcavated`, `FillAt`, `ActiveFluid` — CONFIRMED), and it is the exact query §6 and §7 need. Keep the query, delete its caller. |
| 10 | `Fitting/CompProperties_PitFitting.cs` | 42 | **RETIRE** | Its fields are the cut fittings' tuning (`oublietteEmpDamage`, `poisonSeverityPerInterval`, `drowningSeverityPerInterval`, `escapeBlockingViscosityTicks`). `spikeDamage` is the one number that must land somewhere in §7. |
| 11 | `Fitting/PitFittingType.cs` | 19 | **RETIRE** | The enum collapses to spikes alone, and a one-member enum is not a model — spike presence is a per-cell fact. ⛔ `Oubliette` is CUT and must not reappear. |
| 12 | `Holding/Building_OpenPit.cs` | 377 | **RETIRE** | The model being replaced. `: Building, IThingHolderWithDrawnPawn, IThingHolder` (CONFIRMED line 43). Dies with: `innerContainer`, `MaxOccupants`, `HeldPawn`, `Spring`, `EjectPawn`, `HeldPawnDrawPos_Y`/`HeldPawnBodyAngle`/`HeldPawnPosture`, the `covered` bool, `DirtyMapMesh`, `Destroy`'s drop-occupants net, the `RunStruggleInterval` clock. 🔑 Per the item's Quarry finding, the `IThingHolderWithDrawnPawn` half may need **no replacement at all** (see §8, `pit_occupant_below_floor`) — a standing spawned pawn reads as below-floor because walls rise around it. ⚠️ Note the file's own scope-cut confession: `IThingHolderWithDrawnPawn` draws exactly **one** pawn, so a 2-occupant pit rendered only the first. Terrain has no such limit — the collapse fixes a defect rather than porting it. |
| 13 | `Holding/Building_PitCell.cs` | 193 | **RETIRE** | Its whole job — assign a prisoner, place them in, feed them, gate them — is replaced by §4: a real room plus a vanilla prisoner bed. Its three self-declared holes (no intake `JobDriver`, a teleporting `RM_PlaceInPitCell` stand-in, an instant-feed stand-in) all **cease to exist as work** rather than being owed, because a pawn on terrain in a room is fed and tended by vanilla wardens. ⚠️ One real thing dies with it: `ApplyExposure`'s reading that *"the COVER is the mercy… a captive left open to the sky degrades fast"* (his ruling 2026-08-30, `RM_PitExposure` accruing only while the gate is open) — §5 replaces it with temperature, which is a *different* mechanism reaching the same intent. Flag that swap to him. |
| 14 | `PitsMod.cs` | 143 | **RETIRE** | A second `Mod` subclass and a second settings screen (`SettingsCategory() => "FlowWorks: Pits"`) inside FlowWorks, alongside `RimMandrakeFlowWorksMod`. ⚠️ **REHOUSE the surviving toggles** into `RimMandrakeFlowWorksSettings` (where `superdeepCaptureEnabled` etc. already live), per the every-mod-ships-superb-Mod-Settings ruling. Survivors: `trapTriggerEnabled`, `trapSensitivityMultiplier`, `fallDamageEnabled`, `fallDamageMultiplier`. Die with their mechanics: `struggleIntervalHours`, `escapeEnabled`, `escapeChanceMultiplier`, `digWorkMultiplier`, `pitCellExposureEnabled`, `pitCellExposureMultiplier`. |
| 15 | `RimMandrakePits_DefOf.cs` | 40 | **REHOUSE** | Three `[DefOf]` holders. `RM_DigPitDeeper` (Designation + Job) dies with the dig chain. The three hediffs need per-hediff rulings — see the def table. |
| 16 | `SelfTest/Program.cs` | 194 | **RETIRE** | Tests `PitDepthTier`/`PitCoverTier` arithmetic against a retired ladder. A rewritten selftest is owed, not this one. ⚠️ `PitDepthTier.cs` is *deliberately dependency-free* so it can compile into this plain `net8.0` project (CONFIRMED, its own comment); whatever replaces it inherits that constraint if a selftest is still wanted. |
| 17 | `TerrainMimic/Building_TerrainMimicCover.cs` | 47 | **REHOUSE** | `TerrainMimicPrinter.PrintTerrainMimic` is the mechanism behind `pit_covered_invisible` and behind his cover ruling, and it already works per-cell (`foreach (IntVec3 cell in rect)`) — so it ports to a multi-cell cover with no reshaping. The second class in the file, `Building_TerrainMimicCover`, is **self-declared dead**: *"Standalone example building kept for compile-shape parity with the spike."* Drop the class, keep the printer. Its three UNPROVEN-until-runtime questions (z-fighting, seam at play zoom, dirty-mesh on terrain change) are still open and now bind `pit_covered_seam_at_max_zoom`. |
| 18 | `Trigger/CompPitCoverTrigger.cs` | 87 | **REHOUSE** | 🔑 This is exactly his *"Covering the pit allows people to fall into it involuntarily"*. Sums `StatDefOf.Mass` over `parent.OccupiedRect()` each 30 ticks and springs. Two changes: `Spring` no longer despawns anyone (§3), and `OccupiedRect()` becomes the cover's cells rather than a pit-building's. Keep its own-faction carve-out — `Building_SuperdeepPit` already depends on the same rule for the same reason (a builder must be able to build the ladder without falling in). |
| 19 | `Trigger/CompProperties_PitCoverTrigger.cs` | 22 | **REHOUSE** | `scanIntervalTicks = 30`. Moves with #18 unchanged. |
| 20 | `Trigger/PitCoverTier.cs` | 36 | **REHOUSE** | The only file whose **content** survives byte-for-byte: `None/WovenScrap/PlankLattice/ReinforcedFrame` at 40/120/220 kg. 220 is **his own ruled number** (2026-08-30, after the quicktest matrix found 400 kg unreachable) — ⛔ do not retune it here. It is a property of the cover, not of the pit, so it is untouched by the collapse. |
| — | `SelfTest/RimMandrakePits.SelfTest.csproj` | 48 | **RETIRE** | Not one of the 20; dies with #16. |

**Counts: RETIRE 15, REHOUSE 5, UNCHANGED 0** of the 20 `.cs` files. Zero unchanged
is the honest number and is the measure of the collapse: every one of the 20 is
written against a `Building`, so none survives in place. Of the five rehoused, only
`PitCoverTier.cs` survives as identical content.

### The three files in `Source/Superdeep/` (not in the 20, all affected)

| File | Verdict | Why |
|---|---|---|
| `Superdeep/Building_SuperdeepPit.cs` | **REHOUSE (heavy)** | Its detector and its two gate overrides are the ruling. But `: Building_OpenPit` dies, so the detector must be re-parented — and its purpose changes from *capture into a container* to *mark as fallen-in / apply fall damage and leave the pawn spawned*. `DepthTier = Chasm` and `EscapeBlocked/EscapeAssisted` as virtual overrides on `Building_OpenPit` all need a new home. **NEW: whether a per-D=4-cell holder Thing survives at all is the central open design call** — see §3 and §9. |
| `Superdeep/RM_LadderUtility.cs` | **UNCHANGED** | 🔑 The one file in the whole pit/superdeep surface that today's ruling leaves completely alone. It already is *"one boolean effect; removing the ladder strands whatever is down there"*, already unified with the prison-door reading, and already refuses placement outside an excavation. |
| `Superdeep/RM_SuperdeepCapture.cs` | **REHOUSE or RETIRE** | Depends entirely on the §9 holder question. Its `EnsureHolder`/`HolderAt` lifecycle is correct *if* a holder Thing remains; if the fall state becomes a grid fact, the whole file goes. Its header's "why a Building" argument is now **wrong and must be deleted, not superseded in place** (per the delete-don't-supersede ruling). |
| `RM_Patch_SuperdeepShooting.cs` (at `Source/` root) | **UNCHANGED, but verify** | Ruling 23's restriction. UNCERTAIN whether it keys off the holder Thing or off the depth grid — **not read in this pass**; read it before touching the holder, because deleting the holder could silently disable ruling 23. |

### The 24 defs in `Defs/Pits/`

CONFIRMED: the 18 concrete `ThingDef`s inherit from just **3 abstract parents** —
`RM_PitDigSiteBase` (10 children), `RM_OpenPitBase` (6), `RM_PitCellBase` (2) — and
`texPath` appears on **3 lines total in the whole `Defs/Pits/` tree**, all on those
abstracts, all `Things/Building/Security/TrapSpikeArmed`. So the item's "all 18 share
one texPath" is CONFIRMED and, usefully, the art defect lives in 3 lines, not 18.

| Def(s) | Count | Verdict | Why |
|---|---|---|---|
| `RM_PitDigSite_{Shallow_Bare, Shallow_Spiked, Shallow_Oiled, Shallow_Poison, Shallow_Water, Shallow_Oubliette, Deep_Bare, Chasm_Bare}` | 8 | **RETIRE** | The rival ladder made flesh, plus four CUT fittings. Digging is FlowWorks'. |
| `RM_PitDigSite_{CellSingle, CellDouble}` | 2 | **RETIRE** | Dig sites for `Building_PitCell`, which retires. |
| `RM_OpenPit_{Bare, Spiked, Oiled, Poison, Water, Oubliette}` | 6 | **RETIRE** | ⛔ `RM_OpenPit_*` as buildings is on the item's CUT list by name. `Spiked` returns as per-cell hardware (§7), not as a pit def. |
| `RM_PitCell_{Single, Double}` | 2 | **RETIRE** | Replaced by room + prisoner bed (§4). |
| `RM_PitDigSiteBase`, `RM_OpenPitBase`, `RM_PitCellBase` (abstract) | 3 | **RETIRE** | The three `texPath` lines die here. |
| `RM_DigPitDeeper` (DesignationDef) | 1 | **RETIRE** | |
| `RM_DigPitDeeper` (JobDef) | 1 | **RETIRE** | |
| `RM_DigPitDeeper` (WorkGiverDef) | 1 | **RETIRE** | |
| `RM_PinnedInPit` (HediffDef) | 1 | ⚠️ **NEEDS A RULING** | It expressed "you are inside a container". Under §3/§4 an occupant is a spawned pawn in a room, so nothing needs a hediff to say they are held — the terrain says it. But it may still be wanted as the *fall injury* marker, and `ApplyFailedAttemptCost` (its other writer) is gone. §9. |
| `RM_PitExposure` (HediffDef) | 1 | ⚠️ **NEEDS A RULING** | Its writer (`Building_PitCell.ApplyExposure`) retires and §5's temperature is the replacement. Whether temperature drives vanilla's own `Heatstroke`/`Hypothermia` instead, or `RM_PitExposure` is retargeted, is a real choice — §5 and §9. |
| `RM_PitDrowning` (HediffDef) | 1 | **REHOUSE** | 🔑 The one def that clearly survives. His answer 3 rules that F>0 at D=4 **drowns**, so the drowning clock moves from the `Water` fitting to the fill dimension. Its `CanSwim` check (CONFIRMED: keys off `ageTracker.CurKindLifeStage.swimmingGraphicData != null`, with a recorded 2026-09-02 finding that the old `"aquatic"` substring matched nothing ever) moves with it and must not be re-broken. |

**Def counts: RETIRE 21, REHOUSE 1, NEEDS A RULING 2, UNCHANGED 0** of 24.

Everything on the item's CUT list is accounted for above: the `Oubliette`/ion
fitting (#11 + 2 defs), the `Water`/`Oiled`/`Poison` fittings (#9/#10/#11 + 6 defs),
the `Shallow/Deep/Chasm` ladder (#6 + 10 defs), `RM_OpenPit_*` as buildings (#12 + 6
defs), and every def pointing at `TrapSpikeArmed` (3 abstract parents).

## 3. The trapping rule

His words, verbatim: *"If you're in a superdeep pit, you can't climb out. Period.
Welcome to your pit."* Answer 2: only D=4; 1-3 are movement cost only. So: absolute,
no roll, no skill check, no partial state.

### What does NOT stop pathing out, CONFIRMED

🔴 **The terrain does not, and deliberately must not.** CONFIRMED at
`Defs/Canals/TerrainDefs/FlowWorks_Terrain.xml` line 119ff, `RM_Channel_Superdeep`
ships `<passability>Standable</passability>` and `<pathCost>300</pathCost>`, with
the reason written in place above it:

> *"🔴 PASSABLE, AND THAT IS THE MECHANIC. […] An Impassable terrain would make the
> pathfinder route around the hole and the capture would never fire —
> `Traversability.Impassable` makes `PathGrid.CalculatedCostAt` return its 10000
> sentinel, VERIFIED against the decompiled PathGrid. `pathCost 300` keeps it a
> place nobody crosses by choice."*

⚠️ That `PathGrid` claim is a **prior agent's recorded decompiler reading, not a
measurement made in this pass** — RimSage is unreachable on this laptop, so it is
UNMEASURABLE HERE. It is cited as repo-recorded and flagged for Desktop
re-verification, not laundered into a fresh measurement.

The consequence is structural and worth stating flatly: **a `TerrainDef`'s
`pathCost` and `passability` are per-CELL and therefore symmetric.** There is no
vanilla terrain field that costs more to leave a cell than to enter it. So the trap
cannot be terrain, however deep the number goes — 300 is a deterrent, and a
deterrent is not "Period."

The same file makes the same choice for fill: `RM_Fill_Water_Superdeep` is
`Standable`/`pathCost 300`, with the note *"ruling 26 IS EXACTLY THIS: SUPERDEEP
captures as if dry — fill changes nothing about whether a pawn falls in, so dry and
flooded must have the same passability or the fill would silently become the barrier
the ruling says it is not."* CONFIRMED and consistent.

🔴 **One live inconsistency found, and it is a real defect, not a design question.**
CONFIRMED: `RM_Fill_Tar_Superdeep` ships `<passability>Impassable</passability>`,
with its comment saying *"this stays Impassable until program 2 ships fall-in
capture and ladders"* and its description reading *"Nothing paths into it until
ladders exist."* But `Building_SuperdeepPit` and `RM_LadderUtility` **exist now** —
so that caveat has outlived its condition. A superdeep cell brimming with tar is
today the one fill state that cannot be fallen into, which contradicts ruling 26 and
contradicts his answer 3 (F>0 at D=4 drowns an occupant — there can be no occupant
if nothing can enter). **Fix: `Impassable` → `Standable`, and delete the stale
comment rather than superseding it.**

### What DOES stop pathing out today, CONFIRMED — and why it must die

CONFIRMED: the current answer is that the pawn is **not on the map at all**.
`Building_OpenPit.Spring` calls `p.DeSpawn(DestroyMode.Vanish)` then
`innerContainer.TryAddOrTransfer(p)`. A despawned pawn has no `Position`, takes no
path, and is fed back into the tick only because `Building_OpenPit.Tick` calls
`innerContainer.DoTick()` explicitly (CONFIRMED, with its own comment naming
`Building_Casket.Tick` as the precedent and *"Without this, a held pawn's
needs/hediffs/health never advance: exposure never reaches heatstroke"* as the
reason). Exit is then `EjectPawn` → `GenSpawn.Spawn` at a `RandomClosewalkCellNear`.

🔴 **The container is the current trapping mechanism, and §4 and §5 both forbid it.**
A pawn in a `ThingOwner` is in no room (so it cannot be *"just a room"*), has no cell
temperature (so the desert sun cannot reach it), and cannot be targeted from the lip
as a spawned pawn. So the trapping rule has to be rebuilt for a pawn who **stays
spawned, standing on `RM_Channel_Superdeep`**.

### Where the new rule lives — the shape, and the honest gap

The rule is: *a spawned pawn standing on a D=4 cell may not move to any cell whose D
is less than 4, unless a ladder stands in the cell (or the exit is a sluice gate/door
opened from outside).* Three properties this needs, and the seam each wants:

1. **Jobs must never be TAKEN that require leaving.** The right layer is
   reachability, not mid-walk abort: a pawn who takes a job and then cannot execute
   it produces stuck-pawn bugs and job spam. **NEW: `RM_SuperdeepTrapUtility`** —
   proposed name, needs sign-off — holding the one predicate
   `IsTrappedAt(Map, IntVec3)`, reusing the exact gate `Building_SuperdeepPit`
   already computes (`!RM_LadderUtility.HasLadder`).
2. **A hard per-move veto as the floor**, so blast/teleport/oddity cannot leak a
   pawn out even if reachability is bypassed.
3. **Pathing INTO the pit must be untouched**, or the capture never fires (see the
   terrain comment above). Whatever patch is written must be asymmetric by
   construction: it reads *the cell being left*, never the cell being entered.

🔴 **UNMEASURABLE HERE — the patch seam cannot be chosen on this laptop.** No
RimSage, no decompiled tree, no def dump. What to check on the Desktop, named
precisely so the run is not wasted:

- `Verse.AI.PathFinder.FindPath` — does it expose the *previous* cell at cost time,
  or only the candidate cell? (If only the candidate, an edge-asymmetric cost is not
  expressible in the path grid at all and the veto must live higher.)
- `Verse.AI.Reachability.CanReach(...)` overloads and `Verse.AI.ReachabilityCache`
  — is a per-start-cell veto cacheable, and does the cache key include the start?
- `Verse.AI.Pawn_PathFollower.TryEnterNextPathCell` and `CostToMoveIntoCell` — the
  natural home for property 2.
- `RegionAndRoomUpdater` / `Region` / `District` — see the LAW 2 question below.
- Vanilla's nearest analogue is **`Building_Door.PawnCanOpen(Pawn)`**, which is
  already a per-pawn permission on a *boundary* rather than a cell cost. If it turns
  out that a door is the only sanctioned boundary permission in the engine, that is a
  strong argument for making the pit's lip literally door-shaped — which is exactly
  what his sluice-gate answer 7 already says. Worth checking first.

### 🔴 LAW 2 verdict — the ruling DOES strain it. Raising it, not widening it.

LAW 2, verbatim from `RM_ExcavationDepth.cs`: *"depth affects MOVEMENT and LIQUID and
nothing else. It never affects sight, shooting, cover or projectile arcs — the one
stated exception (ruling 23 […]) is a RESTRICTION on an existing check."*

Two halves of today's ruling, judged separately:

- ✅ **The trapping half does NOT strain LAW 2.** "You cannot climb out" is a
  statement about **movement**, which is the first thing LAW 2 explicitly permits.
  It is an unusual movement rule (asymmetric where vanilla's are symmetric), but it
  is squarely inside the law.
- 🔴 **"This defines a room if it's enclosed" DOES strain LAW 2.** Room detection is
  neither movement nor liquid. There is a narrow reading under which it survives —
  *rooms are derived from passability, so if depth's only reach is into passability,
  then room detection reads the movement fact and depth never touches rooms
  directly.* **But that reading does not save this ruling**, because
  `RM_Channel_Superdeep` is deliberately `Standable`: it bounds nothing, so an
  enclosed superdeep area is **not** a room by that derivation. To make it one you
  must either put something impassable at the lip, or reach into room detection
  because of D. The second is a widening of LAW 2, and this spec will not do it
  quietly.

⚠️ Also note the *kind* of exception differs. Ruling 23 is a **restriction** on an
existing check — it takes something away and so cannot create new coupling. "An
enclosed superdeep area is a room" is an **addition**: it makes a new system (room
role, temperature, prisoner assignment) read depth. That is a materially bigger step
than ruling 23 was, and it should not inherit ruling 23's precedent by analogy.

**This is raised for his ruling as open question A in §9**, with the two ways out
priced there. Do not treat either as chosen.

⚠️ One further unmeasurable that decides how big the problem is: **does vanilla's
room/region builder consider `TerrainDef` at all, or only edifices?** UNMEASURABLE
HERE. On the Desktop, read `RegionAndRoomUpdater`, `RegionMaker`,
`Region.Room`/`District`, and `RoomGroup`. If regions split only on
`Building.def.Fillage == Full` / edifices and never on terrain, then **no terrain
choice can ever make a pit a room** and option A2 in §9 is the only route.

## 4. Room and prisoner semantics

His answer 1, verbatim: *"It's just a room until you put a prisoner bed in it. So
when people fall into it they aren't prinsoners yet, they're just trapped enemies.
But that should be one of those interactions that is helped by letting them roast in
there: easy prisoner capture once they're in the pit, and no you don't have to go
down and enter the room to capture them. You can 'capture down' and 'convert down'"*

### 🔴 The hard invariant, stated once and load-bearing everywhere below

**No design may require a pawn to enter the pit.** By ruling, anyone who enters
cannot leave. A warden who walks down to feed, capture, convert, arrest, rescue or
haul is trapped, and a colony that loses a warden per capture is a broken mechanic,
not a harsh one. Every interaction is performed **from the lip** — a surface cell
adjacent to (or, per open question B, in some relation to) the superdeep cell.

⚠️ This invalidates by construction the whole of `Building_PitCell`'s unbuilt work
list (a carry-to-holder `JobDriver` modelled on `JobDriver_CarryToEntityHolder`, a
real feed-through-the-gate job). Those jobs must not be revived: they are jobs that
walk a colonist to a holder, and the holder is gone.

### State 1 — a bare enclosed superdeep area: TRAPPED ENEMIES

- The occupants are **spawned pawns**, hostile, un-downed if they walked in
  uninjured, standing on `RM_Channel_Superdeep`. They are **not** prisoners: no
  `Pawn_GuestTracker` prisoner state, no warden jobs, no food/medical duty.
- They are simply unable to path out (§3). They fight — ruling 23 restricts them to
  trading fire with whoever is at their own lip, which is already patched
  (`RM_Patch_SuperdeepShooting.cs`).
- They starve, roast, freeze and bleed on vanilla's own clocks, because they are
  spawned. 🔑 **This is a free win of the collapse**: the container version needed an
  explicit `innerContainer.DoTick()` with a comment about needs never advancing;
  spawned pawns need nothing.
- ⚠️ **What vanilla does with an unreachable hostile is UNMEASURABLE HERE.** On the
  Desktop check: does the raid AI's `LordJob` handle "no path to any objective" by
  routing to `JobGiver_ExitMap` and then jamming? Does the map ever declare the
  threat over (`GenHostility.AnyHostileActiveThreatToPlayer`), or does a pit full of
  live raiders hold the colony in permanent combat state, blocking the
  end-of-raid letter and any quest that waits on it? Read `Lord`, `LordToil_*`,
  `GenHostility`, `RaidStrategyWorker`. **This is the single most likely source of a
  shipping bug in the whole item.**

### State 2 — the same area with a prisoner bed: A REAL PRISON ROOM

His rule is minimal and should be implemented as minimally: **put a vanilla prisoner
bed on a superdeep cell and vanilla's own machinery takes over.** No parallel prison
system, no `Building_PitCell`, no assignment gizmo, no feed gizmo.

- The bed is an ordinary `Building_Bed` with `forPrisoners` set by the player, built
  on a superdeep cell like any furniture on any terrain.
- Vanilla then supplies: prisoner status, warden work (`WorkGiver_Warden_*`), food,
  medical, recruitment/conversion interactions, resistance and will tracking, the
  Prisoner tab, prison break logic.
- ⚠️ **Two vanilla prerequisites that are UNMEASURABLE HERE and decide whether this
  works at all:**
  1. Vanilla's prison-cell room role requires the area to *be a room*. That is
     exactly the LAW 2 question in §3 — if a superdeep area is not a room, a bed on
     it is a bed in the open, and this whole state fails. Check
     `RoomRoleWorker_PrisonCell`, `Room.Role`, `RoomRoleDef`.
  2. Can a `Building_Bed` be placed on `RM_Channel_Superdeep` at all? Its
     `<affordances>` list only `Light` (CONFIRMED, terrain def line 133ff), and beds
     have a `terrainAffordanceNeeded`. **This may be a one-line def fix or a real
     blocker.** Check `TerrainAffordanceDefOf.Light` vs `Building_Bed`'s requirement
     on the Desktop.

### The transition, and what it is NOT

The transition from state 1 to state 2 is **the player building a prisoner bed**, and
his capture interaction. There is no "convert the pit" action and no pit mode flag.
That is the whole point of *"It's just a room until you put a prisoner bed in it"* —
the state is derived from the furniture, exactly as vanilla derives it.

The capture itself is his two new interactions:

- **`capture down`** — a warden at the lip converts a downed (or, per open question
  C, merely trapped) hostile in the pit into a prisoner assigned to a prisoner bed
  in the pit, without pathing in. **NEW: `RM_JobDriver_CaptureDown`** and
  **NEW: `RM_WorkGiver_CaptureDown`** (proposed names, need sign-off).
- **`convert down`** — the same shape for ideoligious conversion, i.e. the
  `InteractionWorker` that normally requires the warden to be adjacent to the
  prisoner runs across the lip boundary instead.
- 🔑 **Being trapped is what makes these cheap.** His words: *"that should be one of
  those interactions that is helped by letting them roast in there: easy prisoner
  capture once they're in the pit."* The discount is delivered by §5's temperature,
  not by a flat bonus on the job.

⚠️ **`legator.prisonerrealism` — UNMEASURABLE HERE, measured 2026-09-17.** No Steam
installation exists on this Mac (`~/Library/Application Support/Steam` does not
exist) and no copy of the mod is anywhere on disk; the string appears only as a
`packageId` inside `ModsConfig` snapshots and as prose in two of our own audit docs.
⛔ Its behaviour is therefore not described here, from memory or otherwise. Our own
doc records it as WS `3760196312`, *"every feature individually toggleable, and
auto-defers to other mods that cover the same feature"* — that is a repo claim about
its packaging, not a reading of its code.

**What to read on the Desktop, and the one question to ask of it:** *how does it
decide whether a prisoner is adequately confined, and what does it do when the answer
is no?* Specifically — its Harmony patches on any confinement/escape check, its
`RoomRoleWorker`/`Room` reads if any, its own settings keys for the confinement
features, and whether it patches the same seam §3's exit veto wants. If it does, the
pit must defer to it or be defeated by it. Its auto-defer behaviour also means **the
pit may want to advertise itself as covering a feature it overlaps** — worth checking
whether that deferral is a public, patchable contract.

⚠️ Also in the same adopted cluster and worth the same check: **Prison Labor**
(forced work, needs warden presence) and **Torture Pod**. A forced-labour system that
sends a prisoner to a work station is a system that needs the prisoner to *leave the
pit*, which the ruling forbids. Flagged, not resolved.

## 5. Temperature as the softening mechanism

His answer 5, verbatim, and the item records this as the answer he most wanted on
record:

> *"but I really meant being in brutal high-temp sun should raise the temperature in
> the pit quickly, just as cold-exposure will wear them down as well, and swiftly
> lower their resistance to much of anything. But it's not something nice colonists
> do…"*

### Why this is nearly free, and why it needs a multiplier anyway

🔑 **A superdeep occupant is now a spawned pawn on an unroofed cell, so vanilla
already gives it outdoor temperature.** In the container model it had no cell at all.
That is the largest single behavioural gain from the collapse, and it arrives with no
new code.

But he asked for something stronger than "it is outdoors": *"raise the temperature in
the pit **quickly**"*, more coupled than an ordinary room. Vanilla's own room
temperature system blends toward outdoor temperature as a function of roof coverage
and room size. So the mechanism is: **a superdeep cell's temperature tracks ambient
faster than roof coverage alone would predict.**

⚠️ **UNMEASURABLE HERE.** What to read on the Desktop, named precisely:
`RoomTempTracker` (its equalisation rate and `thickRoofCoverage` blend),
`GenTemperature.TryGetTemperatureForCell`, `GenTemperature.OutdoorTemp`,
`Room.Temperature`, and `Room.OpenRoofCount`. The question: **is the equalisation
rate reachable, or is a Harmony patch on `RoomTempTracker.EqualizeTemperature`
required?** Also check whether an unroofed room in vanilla is simply pinned to
outdoor temperature, in which case the "faster" is already maximal and the design
should say so instead of adding a knob.

⚠️ Note the asymmetry he described is physically real and worth honouring rather than
flattening: a hole in the ground is *more* thermally coupled to direct sun (it traps
radiation, no airflow) and *less* coupled at night (it retains). If vanilla's model
cannot express "hotter by day and also colder by night", say which one wins rather
than fudging both.

### "Swiftly lower their resistance to much of anything" — which stat

Read against vanilla, "resistance" is two named quantities on the prisoner, and his
"to much of anything" reaches both:

1. **Recruitment resistance** — `Pawn_GuestTracker.resistance`. This is the primary
   reading and the one that delivers his *"easy prisoner capture once they're in the
   pit."*
2. **Will** (Ideology) — `Pawn_GuestTracker.will`, the quantity conversion and
   enslavement reduce. This is what makes `convert down` cheap.

⚠️ **UNCERTAIN on both field names and on whether they are public.** UNMEASURABLE
HERE — verify `Pawn_GuestTracker`'s actual members, and read
`InteractionWorker_RecruitAttempt`, `InteractionWorker_EnslaveAttempt` and
`InteractionWorker_ConvertIdeoAttempt` for where the per-attempt reduction is
computed and what modifies it.

🔴 **A likely finding to prepare for: vanilla may have no environmental → resistance
path at all.** Vanilla reduces resistance through *warden interactions*, modified by
the warden's `NegotiationAbility`. If nothing in vanilla lets an environment tick
resistance down, then this is a **NEW mechanism**, not a coupling to an existing one,
and its shape is:

- A per-interval read of the occupant's own thermal distress — **not of the
  thermometer**. 🔑 That distinction matters: keying off the pawn's own hediffs means
  a heat-adapted xenotype, a Jawa in the right gear, or a naturally cold-tolerant
  species is *correctly* harder to break, with no extra code. Keying off the ambient
  temperature would break all three.
- The vanilla hediffs to key off are `Heatstroke` and `Hypothermia` (and their
  severity stages), which are exactly what an exposed pawn accrues.
- ⚠️ **`RM_PitExposure` already exists** and was the old mechanism for the same
  intent, driven by `Building_PitCell.ApplyExposure` on his 2026-08-30 cover-is-mercy
  ruling. §2 marks it NEEDS A RULING: either it is retargeted as the accumulator that
  reads `Heatstroke`/`Hypothermia` and writes resistance decay, or it is deleted in
  favour of reading vanilla's hediffs directly. **This is his call, in §9.**

### 🔴 On this desert world, the pit is a torture instrument by default

Worth stating plainly, as the item asks: brutal sun is the campaign's **ambient
condition**, not a weather event. So a pit dug on this map is a working torture
device the moment it exists, with no configuration, no research and no ritual. That
is a design fact, not a tuning choice, and it is the reason the next paragraph is
not optional.

### ⛔ The mood / ideoligion cost is HIS, and is not specified here

His words: *"But it's not something nice colonists do…"* — he flagged the cruelty and
deliberately left the cost open. ⛔ **This spec proposes no precept, no meme, no
thought def, no mood penalty and no number.** Recording only what is structurally
true so that his ruling has somewhere to land:

- The behaviour that would carry a cost is *leaving a living pawn in a pit while the
  temperature does the work* — a duration, not an event, and therefore not naturally
  expressible as a one-shot thought.
- It is a **player choice with no in-game actor**: nobody performs it. Whatever shape
  the cost takes has to attach to the colony's knowledge of it, or to the warden who
  benefits from the softened resistance, or to the pit's existence. Those are three
  materially different designs.
- ⚠️ He has an Ideology stack and an adopted cruelty cluster already, so a precept is
  *available* — which is precisely why it must not be invented. Open question D.

## 6. Fluids

His answer 7: oil and poison **are** FluidDefs, not fittings. His wider list from the
original FlowWorks vision: *"fresh water, salt water, tar, propane, colored water,
slime"*. His answer 3: F>0 at D=4 drowns; F>0 at D=1-3 slows strictly more than dry.

### What a fluid IS — CONFIRMED

`FluidDef : Def` at `Source/FluidDef.cs`. CONFIRMED members:

- **Four terrain fields**: `floodTerrain` (tier 1, and mandatory —
  `ConfigErrors` rejects null), `fillTerrainHalf` (tier 2), `fillTerrainBrim`
  (tier 3), `fillTerrainSuperdeep` (D=4, separate *"because the temp layer wins in
  `TerrainAt`"*). All must be `<temporary>true</temporary>` — `ConfigErrors` rejects
  non-temporary, because `TerrainGrid.SetTempTerrain` hard-refuses anything else.
- **Flow/economy tuning**: `volumePerTile`, `ticksPerTile` (the viscosity field — 60
  for water, 360 for tar), `floodedTicks`, `canalCellsPerSourceCell` (his 5:1
  budget), `groundOozePerSourceCellPerDay`, `rainRefillFactor`, `recededTerrain`.
- **Resolution**: `FillTerrainFor(tier, depth)` — returns the superdeep terrain
  whenever `depth >= Superdeep`, otherwise walks tiers 1/2/3 with fallbacks.
- `OwnsFillTerrain(terrain)` so an engine never strips another system's temp terrain.

Two fluids ship: `RM_Fluid_Water` and `RM_Fluid_Tar` (CONFIRMED,
`Defs/Canals/FluidDefs/FlowWorks_Fluids.xml`).

🔑 **And the per-fluid *behaviour* hook already exists too**:
`RM_LiquidProperties : DefModExtension` (CONFIRMED, `Source/LiquidTypes/`) attaches to
a **TerrainDef** and carries `viscosityClass`, `pH`, `damageOnContact`,
`damageOnImmersion` (a `LiquidDamageSpec` = `DamageDef` + `amount`),
`corrodesApparel`, `flammable`, `igniteTemp`. `LiquidIgnitionMapComponent` scans
cells whose `RM_LiquidProperties.flammable` is true and starts fires there, gated by
`RimMandrakeFlowWorksSettings.liquidIgnitionEnabled` (**off by default**, CONFIRMED).

### What a new FluidDef costs

**One `FluidDef` row plus up to four new `TerrainDef`s** (tiers 1/2/3 + superdeep),
each needing a parent, a texture path, a `pathCost`, `<temporary>true</temporary>`,
an empty `<driesTo>`, `<canFreeze>false</canFreeze>`, a `renderPrecedence` and tags —
plus, for anything that burns or harms, an `RM_LiquidProperties` block. Measured
against the shipped tar rows that is roughly **25-30 XML lines per tier**, so a
fluid is ~100-130 lines of def and **zero lines of C#**. That is cheap, and it is the
strongest structural argument for his answer 7.

⚠️ The tar terrains reuse vanilla `WaterShallow` as parent and vanilla water ramp art
tinted by `<color>` (CONFIRMED). A new fluid gets the same free ride on the
edge-aware ramp art. Rulings 34-36 deleted art; nothing here restores any of it.

### Oil

- **Ignitable** — set `flammable` true and an `igniteTemp` on its tier terrains, and
  `LiquidIgnitionMapComponent` already does the rest. It also already binds two
  FlowWorks bars (`canal_burning_reads_as_burning_liquid`,
  `canal_fire_reaches_reservoir`), so the pit's oil route has an existing visual
  floor to land on.
- ⚠️ **`extinguishesFire` is the trap.** The ignition file records (CONFIRMED) that a
  flammable liquid terrain must have `extinguishesFire=false` or the fire is
  destroyed on the spot, and that vanilla's `Fire` has a
  `if (flammabilityMax < 0.01f) { Destroy(); }` path. Water tiers inherit
  `extinguishesFire` from `WaterShallow`; **an oil tier must not.**
- 🔑 His literal reading survives intact: *"oil plus ignition remains a real kill
  route, distinct from the capture route."* A superdeep cell brimming with oil, then
  lit, kills. That is a different mechanic from softening-then-capturing and both
  must remain available.
- ⚠️ `liquidIgnitionEnabled` defaults **off**. If oil is a shipped kill route, either
  it defaults on or the mod ships a feature that does nothing until the player finds
  a checkbox. Flag for his settings pass.

### Poison — toxin keyed to FILL, not a comp

His answer 7 is explicit that the toxin rule keys to fill. 🔑 **`RM_LiquidProperties`
already has the exact field: `damageOnImmersion`**, a `LiquidDamageSpec` on the
terrain. A pawn standing on a poison-filled cell is immersed; the terrain says what
that does. No `ThingComp`, no per-pit building, no `CompPitFitting`.

- The retiring `CompPitFitting.OnStruggleInterval` drove `HediffDefOf.ToxicBuildup`
  on a struggle interval (CONFIRMED). ⚠️ The struggle clock is gone (§2 #8), so
  whatever paces immersion damage now must come from the liquid layer's own interval,
  not from an escape roll. Name that interval explicitly when built.
- ⚠️ `damageOnContact` vs `damageOnImmersion` presumably differ by fill tier. That
  mapping is **UNCERTAIN — not read in this pass**; read `LiquidCorrosion.cs` for how
  the two are already dispatched before adding a third caller.

### Drowning at D=4 — the one clearly surviving def

His answer 3 rules drowning as the consequence of F rising against an occupant.
`RM_PitDrowning` (HediffDef) and `CompPitFitting`'s `CanSwim` check move to the fill
dimension. 🔴 **Do not re-break `CanSwim`**: it keys off
`ageTracker.CurKindLifeStage.swimmingGraphicData != null` after a recorded 2026-09-02
finding that the previous `body.defName.Contains("aquatic")` heuristic *matched
nothing, ever, for any real race* (CONFIRMED in the file's own comment). The
substring test survives only as a secondary OR for modded opt-in.

⚠️ Note the drowning trigger changes shape: it was *"the `Water` fitting is
installed"*; it is now *"F > 0 on the D=4 cell I am standing on"*, which means
**opening a sluice gate on an occupied pit is the drowning action**. That is exactly
his *"Flooding an occupied pit is just opening a sluice"* — the reason the `Water`
fitting retires.

### "Slows strictly more flooded than dry at the same depth" — 🔴 a live contradiction

His answer 3 adds *"all other flooded canal depths just slow you down more with the
water than the empty canal did."* CONFIRMED pathCosts:

| | dry | water fill |
|---|---|---|
| D=1 Shallow | `RM_Channel_Empty` **30** | `RM_Fill_Water_Trace` — inherits `WaterShallow` (**UNCERTAIN**, no explicit `pathCost`) |
| D=2 Mid | `RM_Channel_Mid` **45** | `RM_Fill_Water_Half` **42** |
| D=3 Deep | `RM_Channel_Deep` **80** | `RM_Fill_Water_Brim` **300** |
| D=4 Superdeep | `RM_Channel_Superdeep` **300** | `RM_Fill_Water_Superdeep` **300** |

🔴 **The D=2 row violates his ruling as shipped: 42 flooded is CHEAPER than 45 dry.**
And D=1 cannot be judged without resolving `WaterShallow`'s inherited cost. The
reason is structural, not a typo: **fill terrains are tiers of F, dry terrains are
levels of D, and the two ladders are indexed differently** — `FillTerrainFor` picks
tier 2 for a half-full cell whatever its depth, so one `pathCost` number has to serve
a half-full shallow trench and a half-full deep one.

Two ways out, both real, neither chosen here:

- **Raise every fill tier above the dry cost of the deepest depth it can appear at.**
  Cheap (numbers only, no new defs), but it makes a half-full shallow trench cost as
  much as a half-full deep one — which flattens exactly the depth read ruling 5 built
  the tiers for.
- **Cross the ladders: a terrain per (D, tier).** Correct, and expensive — 4 depths ×
  3 tiers = 12 terrains *per fluid*, against 4 today. It also changes `FluidDef`'s
  shape from four terrain fields to a matrix, which is a breaking change to a def
  that already ships.

⚠️ Also note `extraNonDraftedPerceivedPathCost` (240 on Half, 400 on Brim) is already
doing much of this work for undrafted pawns and is *not* part of the real path cost.
Whether his ruling is about real cost or perceived cost changes which fix is right.
**Open question E.**

### 🔴 `ActiveFluid` is ONE fluid PER MAP — the biggest structural finding in §6

CONFIRMED, `RM_MapComponent_Excavation`: `ActiveFluid` is a single
`FluidDef activeFluid` field on the map component, defaulting to `RM_Fluid_Water`,
with a plain setter. `ApplyFillTerrain(c, ActiveFluid)` and `FillTerrainFor` are
called with it map-wide.

**So "water in this canal, oil in that pit, poison in a third" is not expressible
today.** Switching `ActiveFluid` would retexture every filled cell on the map at
once. His answer 7 — oil and poison are fluids, chosen per pit as *"what do you put
in the canal pit with them"* — **requires fill to become per-cell or per-body typed**,
which is a change to the engine's core state, not to the pit.

⚠️ That is a bigger piece of work than everything else in this item combined, and it
is invisible from the ruling. It is **open question F**, and it is the one that
should be raised first, because if per-cell fluid typing is not wanted then the
oil/poison half of his answer 7 cannot ship and the fittings were doing real work
after all. Also note `FillAt` is a `byte` per cell while fluid identity is not stored
per cell at all — so this needs a new grid, and a save-migration for maps written
before it.

## 7. Spikes

His answer 6, verbatim:

> *"You can put spikes in a capture canal, they just only kill if you fall into the
> part of the canal with spikes. If you walk up to them they don't hurt you.
> everything else is just 'what do you put in the canal pit with them' for oil,
> poison, etc. forget the oubliette/ion thing."*

**Spikes are the one surviving piece of hardware.** Everything else that was a
"fitting" is either a fluid (§6) or CUT.

### The contract, in three lines

1. **Per CELL, not per pit.** One canal may be part spiked and part bare. The unit of
   hardware is the cell, exactly as D and F already are. 🔑 This is the sentence that
   kills `RM_OpenPit_Spiked` as a whole-building def: a building's fitting applies to
   the whole building, and he ruled it applies to one cell.
2. **Lethal ONLY on a fall INTO that cell.** Not on being in it, not over time, not
   on leaving. It is an entry event with a specific cause.
3. **Harmless to walk up to.** A pawn standing beside spikes, or on them at surface
   level, takes nothing.

### What "a fall into that cell" means, precisely

⚠️ This is the one place the contract needs a definition it does not have, and getting
it wrong makes the mechanic either useless or a colonist-killer. A pawn arrives on a
spiked D=4 cell by exactly four routes:

| route | spikes fire? |
|---|---|
| walked in over the lip from an adjacent surface cell (the ordinary capture) | **yes** — this is a fall; the terrain is four levels down |
| fell through a cover that sprang under their mass (§2 #18) | **yes** |
| pushed / blasted / weapon blowback in against their will (his cover ruling) | **yes** |
| climbed **down** a ladder deliberately, or arrived from an adjacent cell that is *itself* already D=4 | 🔴 **no** — needs his ruling, open question G |

The fourth row is the whole of the ambiguity. Moving between two adjacent superdeep
cells is not a fall — you are already at the bottom — so a pawn crossing a long spiked
canal floor must not be killed once per cell. And his *"jump into pit"* gizmo is
voluntary entry from above, which by his ruling strands the jumper; whether it also
impales them is not stated.

**Proposed rule, needing sign-off:** spikes fire when a pawn's *previous* cell had a
strictly lower D than the cell it entered — i.e. it descended. That makes route 4's
same-depth movement free and every genuine descent lethal, with no extra state. ⚠️ It
also means a ladder descent is a fall. That may be exactly right (spikes at the bottom
of a ladder are a bad idea) or exactly wrong; **his call, open question G.**

🔑 Note this predicate is the same "compare the previous cell's D to this cell's D"
information §3's exit veto needs, in the opposite direction. If one is expressible,
both are. If the engine cannot expose the previous cell (see §3's `PathFinder`
question), **both mechanics are blocked on the same unmeasurable**, which makes that
one Desktop check the highest-value thing to run.

### Where spikes live — NEW, needs sign-off

Spikes are a **Thing installed on an excavated cell**, not a terrain and not a comp on
a pit building. Reasons, all from existing precedent in this repo:

- A Thing is the only per-cell installable that the player builds, deconstructs and
  sees. `RM_LadderUtility` already establishes exactly this pattern for the ladder —
  *"a building that makes a dug cell exitable"*, found by
  `Position.GetThingList(map)`, with `PlaceWorker_LadderOnExcavation` refusing
  placement outside an excavation (CONFIRMED). Spikes are the same shape with the
  opposite sign.
- Terrain is already fully spoken for: dry D uses four terrains and fill uses four
  more per fluid, and `TerrainAt` returns one terrain. Spikes cannot be a terrain
  without colliding with fill.

Proposed identifiers, all **NEW and needing his sign-off**:
- **NEW: `RM_Spikes`** — the `ThingDef`. ⛔ Must **not** use
  `Things/Building/Security/TrapSpikeArmed`; that texPath is the defect this whole
  item exists to remove (§8, `pit_not_vanilla_trap`).
- **NEW: `PlaceWorker_SpikesOnExcavation`** — mirroring the ladder's placeworker.
  ⚠️ Open: does it require D=4 specifically, or any excavated cell? His words say
  *"a capture canal"*, and only D=4 captures, but he also says spikes only matter on
  a fall — and a fall can only happen into D=4. Lean D=4; flag it.
- **NEW: `RM_SpikeUtility.HasSpikes(Map, IntVec3)`** — mirroring
  `RM_LadderUtility.HasLadder` exactly, same O(things-in-cell) shape.

### The one number to carry across

`CompProperties_PitFitting.spikeDamage`, applied as
`DamageInfo(DamageDefOf.Stab, Props.spikeDamage)` (CONFIRMED,
`CompPitFitting.OnCapture`). ⚠️ Its shipped value was **not read in this pass** —
read it from `Pit_OpenPits.xml` before deleting the def, or the retune is silent.
Note it stacks with the mass-scaled blunt fall damage
(`FallDamagePerMassKg = 0.08f`, CONFIRMED) which survives as `fallDamageEnabled` /
`fallDamageMultiplier` in §2 #14. **Spikes plus fall damage together must actually
be lethal**, since he said *"they just only kill if you fall into"* — "kill" is his
word, and a non-lethal spike is a failed mechanic. That is a tuning target, not a
number to invent here.

⛔ **`Oubliette` / the ion charge is CUT** — *"forget the oubliette/ion thing."* It
was the only anti-mechanoid fitting; he asked for no replacement (open question H
records that, unresolved).

## 8. The 12 bars, rewritten

Format per `north_star_validation_spec.md` §1 (CONFIRMED, read this pass): a
`## north star` section carrying `state:` and `validated-hash:` header lines, an
`### the experience (OWNER'S WORDS)` block an agent never writes, `### must show`
grouped by mechanic with stable ids answerable yes/no by LOOKING, and an optional
`### cannot show`. Its own discipline: *"An agent distils `must show` from `the
experience` and adds no new claims."*

🔴 **Which is exactly the problem this section has to be honest about.** Today's
ruling changes the *subject* of five of the twelve bars from a Building to a terrain,
so a faithful distillation is not available for all twelve: some lines have no
referent any more, and the replacement is a claim he has not made. Those are marked
🆕 **NEW CLAIM — NOT APPROVED** and must not be filed as if they were his.

⚠️ Two live process findings before the rewrite:

1. **`design/validation_walks/RimMandrake/Pits.md` carries `state: VALIDATED` with a
   `validated-hash`, while the prose immediately below it reads "⚠️ **DRAFT — not a
   bar until the owner validates it.**"** (CONFIRMED, both read this pass.) That is
   precisely the state-dependent-prose trap named in the project's own instructions:
   the hash covers the whole section including prose, so the file now asserts both
   states at once. Fix in the same pass that rewrites the bars, and write only
   state-independent prose inside the section this time.
2. Per the item, these 12 bars **bind nothing** — `modcheck run Pits` cannot resolve
   a mod folder because `src/RimMandrake/Pits/` holds only `__pycache__`. And per the
   project's own measured finding, `shows=` appears in **0 of 17** mod
   `validation.py` files, so even correctly-housed bars are bound-and-uncovered.
   ⛔ **Rewriting these bars does not make them enforce.** Say so to him plainly
   rather than letting a rewrite read as a fix.

### Proposed replacement section

To be filed in **FlowWorks'** walk (the mod that actually ships the content), not in
`Pits.md` — which the item's own verify block says should cease to exist.

```markdown
### must show

**A superdeep excavation, empty**
- [ ] `pit_reads_as_hole` — a superdeep cell reads as a hole you would fall
      into, at play zoom, with no label needed. Walls with depth, not a flat
      tile with a lip shadow.
- [ ] `pit_not_vanilla_trap` — nothing in the excavation family reads as
      vanilla's spike trap.
- [ ] `pit_reads_at_size` — a multi-cell superdeep area reads as one excavated
      place, not as a row of identical tiles.
- [ ] `pit_depth_ladder_legible` — surface, shallow, mid, deep and superdeep are
      distinguishable from each other by looking, without a tooltip.

**An occupied superdeep excavation**
- [ ] `pit_occupant_below_floor` — an occupant reads as being down in the
      excavation, not standing on top of it.
- [ ] `pit_occupied_distinguishable` — occupied and empty superdeep cells are
      distinguishable at a glance.
- [ ] `pit_trapped_reads_as_trapped` — a trapped occupant reads as unable to get
      out, not as a pawn who has chosen to stand there.

**The cover**
- [ ] `pit_covered_invisible` — a covered excavation is invisible at play zoom,
      matching surrounding terrain.
- [ ] `pit_covered_seam_at_max_zoom` — and carries a seam or discoloration at
      maximum zoom, so the player who placed it can find it.

**The built half — ladders and sluice gates**
- [ ] `ladder_state_legible` — a ladder standing in an excavation, versus none,
      is visible on the excavation itself.
- [ ] `sluice_gate_state_legible` — a sluice gate open versus shut is visible
      without selecting it.

**Fill in an excavation**
- [ ] `fill_tier_legible` — dry, trace, half and brimming are distinguishable
      from each other by looking.
- [ ] `fill_fluid_distinct` — different fluids in an excavation are
      distinguishable from each other.

**Hardware**
- [ ] `spikes_read_distinct` — a spiked cell is distinguishable from a bare one
      before anything falls in.

### cannot show

- [ ] `never_snared_standing` — a pawn snared upright on a labelled tile.
- [ ] `never_reads_as_building` — an excavation must not read as a placed
      building sitting on the floor.
```

### The twelve, one by one

| old id | verdict | new expression |
|---|---|---|
| `pit_reads_as_hole` | **KEEP, re-subjected** | Still his words verbatim (*"we need a big dark pit"*). Subject changes Building → superdeep cell. ⚠️ Ruling 33 sharpens it: *"walls with depth, not a flat tile with a lip shadow"* — folded in as his own words, not a new claim. **APPROVED in substance.** |
| `pit_not_vanilla_trap` | 🔴 **REWRITTEN — must change** | The item is right that this one cannot survive as written: it says *"the pit has art of its own, at its own texture path"*, and a terrain has no `texPath` for a Building to own. But the *claim underneath* — never look like vanilla's spike trap — is directly his (*"stuck in a trap with 'Pit' written on it"*). Rewritten to drop the mechanism and keep the claim. **APPROVED in substance; the words change.** 🔑 And it now has teeth: §2 locates the whole defect in **3 abstract-parent `texPath` lines**, all of which retire. |
| `pit_occupant_below_floor` | **KEEP, cheaper than it looks** | 🔑 The item's Quarry finding: *"the depth read comes from the WALL FACES, not from the occupant… therefore `pit_occupant_below_floor` may need no custom pawn draw at all."* If that holds, this bar is satisfied by the terrain edge art already ruled (19, 33) and the `IThingHolderWithDrawnPawn` machinery deletes rather than moves. ⚠️ **UNCERTAIN** — the item labels it a read of a screenshot, not of Quarry's code; verify against `ogliss.thewhitecrayon.quarry` source on the Desktop. **APPROVED as written.** |
| `pit_occupied_distinguishable` | **KEEP** | Unchanged in substance; only "sprung pits" → "superdeep cells". **APPROVED in substance.** |
| `pit_reads_at_size` | **KEEP, strengthened** | Was *"a pit larger than one cell fills its own footprint rather than drawing in one corner"* — a Building-multi-cell-graphic concern that ceases to exist on terrain. The item's Quarry read supplies the real claim: *"a multi-cell enclosed space that reads as a room, with irregular organic edges rather than a tile grid."* ⚠️ **Borderline** — "reads as one excavated place, not a row of identical tiles" is a *higher* bar than "fills its footprint". Marked APPROVED in substance but flag the strengthening to him. |
| `pit_covered_invisible` | **KEEP, unchanged** | His own 2026-08-30 ruling. `TerrainMimicPrinter` rehouses (§2 #17). **APPROVED as written.** |
| `pit_covered_seam_at_max_zoom` | **KEEP, unchanged** | His own words: *"a slight seam/discoloration at high zoom for the player's own eye"* — the specified-but-unbuilt tell. ⚠️ Still unbuilt, and `TerrainMimicPrinter`'s own three UNPROVEN-until-runtime questions (z-fighting, seam at play zoom, dirty-mesh on terrain change) bind here. **APPROVED as written.** |
| `digsite_stage_legible` | 🔴 **DELETE** | Its referent is gone: the `RM_PitDigSite_*` chain retires entirely (§2, 10 defs). Digging is FlowWorks' canal dig, which has its own bars. ⛔ Do not carry this forward and do not re-express it — deleting a bar whose subject no longer exists is correct, not a loss. |
| `pitcell_gate_state_legible` | **REHOUSED as `ladder_state_legible` + `sluice_gate_state_legible`** | `Building_PitCell`'s gate retires (§2 #13), but his ruling gives the *same* legibility claim two new subjects: the ladder (*"pulled up or lowered"*) and the sluice gate (*"acts just like a door"*). Both are his words this sitting, so both are approved claims — but **splitting one bar into two is a structural change**, flag it. **APPROVED in substance, ×2.** |
| `pitcell_occupant_visible` | 🔴 **MERGE into `pit_occupant_below_floor`** | It was the same claim about a different Building (*"discernible as being down in the cell, not standing on it"*). With one collapsed model there is one bar. Merging removes a bar he approved — flag it, do not do it silently. |
| `fitting_reads_distinct` | 🔴 **SPLIT into `fill_fluid_distinct` + `spikes_read_distinct`** | Was *"spiked, oiled, poison and water fittings are distinguishable from bare and from each other"*. Three of the four named fittings become fluids and one becomes cell hardware, so the single bar splits along his own answer 7. ⚠️ `fill_fluid_distinct` is only checkable at all if §6's open question F (one fluid per map) resolves toward per-cell fluids — **a bar that cannot be evaluated must not be filed.** |
| `never_snared_standing` (cannot) | **KEEP, unchanged** | 🔑 The sharpest line in the roster and the one that prompted the whole north-star system. Fully intact under the new model. **APPROVED as written.** |

### 🆕 NEW CLAIMS — HE HAS NOT APPROVED THESE

Marked separately and unmistakably, per the brief. Each is a real gap the collapse
opens, and each is a claim about the *experience* that only he can make.

- 🆕 **`pit_depth_ladder_legible`** — *"surface, shallow, mid, deep and superdeep are
  distinguishable from each other by looking."* **NOT APPROVED.** Justification: with
  the pit collapsed onto the depth ladder, "is this cell the trapping level?" becomes
  a life-or-death read the player makes constantly, and no existing bar covers it.
  Ruling 19 ruled the *mechanism* (fill-tier ramps wet, one inner-shadow edge
  treatment dry) but no bar says the result must be *distinguishable across all
  five*. ⚠️ Cost note: with one inner-shadow treatment for all dry depths, five
  levels may not be separable at play zoom — so this bar may be **unsatisfiable
  under ruling 19 as ruled**, which is itself worth his attention.
- 🆕 **`pit_trapped_reads_as_trapped`** — *"a trapped occupant reads as unable to get
  out, not as a pawn who has chosen to stand there."* **NOT APPROVED.**
  Justification: this is the closest thing to *"Welcome to your pit"* and it is the
  one experience claim the old roster had no line for, because the old model made the
  occupant invisible (despawned into a container). Now the occupant is a spawned pawn
  standing on a floor — which is *visually identical to a pawn standing anywhere
  else*. 🔴 **This is the single largest new visual risk in the collapse**, and the
  honest reading is that it recreates the original defect in a new form: he was
  appalled by *"a pawn stand[ing] there staring at the camera"*, and a spawned pawn
  on terrain does exactly that unless the walls carry the read.
- 🆕 **`fill_tier_legible`** — *"dry, trace, half and brimming are distinguishable."*
  **NOT APPROVED as a pit bar.** It may already exist as a FlowWorks canal bar —
  ⚠️ **not checked in this pass**; read FlowWorks' existing 13+3 bars before filing,
  to avoid a duplicate id.
- 🆕 **`fill_fluid_distinct`** — see the split above. **NOT APPROVED**, and blocked on
  open question F.
- 🆕 **`spikes_read_distinct`** — *"a spiked cell is distinguishable from a bare one
  before anything falls in."* **NOT APPROVED.** Derived from his answer 6 (*"if you
  walk up to them they don't hurt you"*), which implies the player can see them and
  choose to walk up — but he did not say they must be visible. ⚠️ There is a real
  design argument the *other* way: a visible spike pit is a trap the enemy AI might
  avoid, and concealment is the whole point of the cover. Genuinely his call.
- 🆕 **`never_reads_as_building`** (cannot show) — **NOT APPROVED.** Justification:
  it is the negative form of this entire item (*"A pit is not a building"*) and a
  `cannot show` line is where his rejections have historically carried the most
  information. But it is my sentence, not his.

**Count: 12 old bars → 6 kept in substance, 2 rewritten/re-subjected, 1 deleted,
1 merged away, 2 split into 4, and 6 genuinely new claims requiring his approval**
(`pit_depth_ladder_legible`, `pit_trapped_reads_as_trapped`, `fill_tier_legible`,
`fill_fluid_distinct`, `spikes_read_distinct`, `never_reads_as_building`).

⛔ **Do not file any of the 6 as VALIDATED, and do not run
`modcheck/cli.py validate FlowWorks --owner-said` until he has ruled on them.** Note
that `validate` refuses unless both `state:` and `validated-hash:` header lines exist,
and that omitting `--owner-said` is a dry run that writes nothing — use that.
⛔ And do not touch the `## north star` sections of `Pits`, `Graffiti` or
`WreckedMachines` while doing it: the recorded hash covers the whole section including
prose, so any edit silently reverts a VALIDATED checklist to DRAFT.

## 9. Open questions for him

The item's three come first, unresolved and unimproved. Then what this pass surfaced.
⛔ None of these is answered here.

### From the item

**A-item. The shape of the mood / ideoligion cost of temperature torture.**
He flagged it: *"But it's not something nice colonists do…"* ⛔ No precept, meme,
thought or number is proposed (§5). Trade-off to price when he rules: the cost has to
attach to a *duration* with no acting pawn, so the three candidate anchors — the
colony's knowledge, the warden who benefits, or the pit's mere existence — behave very
differently. Cost: a precept is cheap XML; a duration-tracked mood system is not.

**B-item. Do `capture down` / `convert down` require the warden adjacent to the lip,
in line of sight, or merely somewhere on the map?**
Trade-off: *adjacent* is the most physical and reuses vanilla's own
"warden must reach the prisoner" job shape, but ruling 23 already restricts a
superdeep occupant to trading fire with whoever is at their lip, so adjacency puts the
warden in exactly the cell the occupant can shoot. *Anywhere on the map* is safe and
free but reads as remote-control and breaks the physicality he asked for. Cost: low
either way — this is a `JobDriver` reach condition, not a system.

**C-item. What replaces the anti-mechanoid case now the oubliette is cut?**
He asked for no replacement, and it is legitimate to ship none. Cost of nothing: a
mechanoid raid ignores the entire pit family. ⚠️ Related and unnoticed: mechanoids
have no recruitment resistance and do not roast, so §5's whole softening path is
inert against them — a pit full of centipedes is a permanent unreachable hostile with
no resolution, which loops back to §4's raid-AI risk.

### Surfaced by this pass

**D. 🔴 LAW 2 — "an enclosed superdeep area is a room" needs a ruling, because it
reaches room detection, which LAW 2 does not permit.** (§3's verdict.) Two ways out:

- **D1 — derive room-hood from a built lip.** Something impassable at the boundary
  makes the area a room by vanilla's own derivation, and LAW 2 is untouched. Cost: the
  player must build a rim, so a bare dug hole is *not* a prison until they do — which
  contradicts his *"This defines a 'room' if it's enclosed"* unless "enclosed" is read
  as "walled", which is a plausible reading of his word. Cheapest by far, and it
  requires no engine patch.
- **D2 — add a second stated exception to LAW 2.** Explicit, honest, and permanent.
  Cost: LAW 2's value is that it is short and absolute; ruling 23's exception is a
  *restriction* on an existing check, whereas this is an *addition* that makes new
  systems read depth. Every future system then has a precedent to ask for the same.
- ⚠️ **Blocked on an unmeasurable either way:** if vanilla's region/room builder never
  considers terrain at all (UNMEASURABLE HERE; read `RegionAndRoomUpdater`,
  `RegionMaker`), then D1 is not a preference but the only option.

**E. Does "flooded slows more than dry" mean real path cost or perceived path cost?**
(§6.) Real: `RM_Fill_Water_Half` at 42 is *cheaper* than dry `RM_Channel_Mid` at 45
today, so his ruling is violated as shipped and needs a fix. Perceived: the
`extraNonDraftedPerceivedPathCost` values (240/400) already make undrafted pawns avoid
fill heavily, and his ruling may already be satisfied. Trade-off if real cost:
flattening the tiers upward is free but erases the depth read ruling 5's tiers exist
for; crossing the two ladders into a (D × tier) matrix is correct but takes each fluid
from 4 terrains to 12 and changes `FluidDef`'s shipped shape.

**F. 🔴 Should fill become per-cell typed, so different pits can hold different
fluids?** (§6.) This is the largest hidden cost in the item, and it should be answered
first. `ActiveFluid` is one `FluidDef` per **map** today (CONFIRMED), so his answer 7
— oil in this pit, poison in that one — cannot ship without a new per-cell fluid grid
plus a save migration. Trade-offs: *yes* costs new map state, new save format, and a
migration for existing maps, and makes the fluid engine meaningfully more complex.
*No* costs his answer 7: oil and poison would have to stay per-pit hardware after all,
which means the fittings were doing real work and the collapse is smaller than ruled.
⚠️ There is a middle option worth pricing — per **liquid body**, not per cell, since a
pit fed by its own sluice is its own body. Cheaper than per-cell, and may be enough.

**G. Do spikes fire on a deliberate ladder descent, and on movement between two
already-superdeep cells?** (§7.) Proposed rule is "spikes fire on any descent",
which makes same-depth travel free and a ladder descent lethal. Trade-off: lethal
ladder descent is physically right and makes spiked pits unusable as prisons — which
may be the point, or may be a footgun that kills the colonist who climbs down to
retrieve a corpse. Note also his *"jump into pit"* gizmo is voluntary descent and its
interaction with spikes is unstated. Cost: low; this is one predicate either way.

**H. What happens to the three hediffs — `RM_PinnedInPit`, `RM_PitExposure`,
`RM_PitDrowning`?** (§2's def table.) `RM_PitDrowning` clearly survives.
`RM_PinnedInPit` expressed "you are inside a container" and both its writers retire —
delete, or retarget as a fall-injury marker? `RM_PitExposure` was his own
cover-is-mercy mechanism (2026-08-30) and §5's temperature replaces the *intent* with
a different *mechanism*: retarget it as the accumulator, or delete it and read
vanilla's `Heatstroke`/`Hypothermia` directly? ⚠️ **He should know that §5 swaps out a
mechanism he personally ruled**, rather than finding it gone.

**I. Six of the twelve rewritten bars are NEW claims he has never approved** (§8), and
two more are strengthened or split in ways that change what they demand. He is the
only author of a `must show` line. ⚠️ He should also know that rewriting them **does
not make them enforce** — `shows=` appears in 0 of 17 `validation.py` files, so the
bars remain bound-and-uncovered whatever they say.

**J. Does `PitDepthTier.MaxBodySize` survive in any form?** (§2 #6.) The retiring
ladder carried a body-size gate — shallow holds ≤1, deep ≤2.5, chasm anything — with
no equivalent anywhere in `RM_ExcavationDepth`, and today's ruling does not restate
it. Trade-off: without it, a thrumbo and a squirrel are equally held by a D=4 cell,
which is simple and arguably correct now that escape rolls are gone (nothing climbs
out, period). With it, a new per-depth field on the primitive. ⚠️ Silent deletion is
the risk: this is a real mechanic that dies quietly if nobody asks.

## 10. Risks and unknowns

Ordered by how much of the item each could invalidate.

1. 🔴 **The whole trapping mechanism rests on one unmeasurable.** §3's exit veto and
   §7's spike trigger both need "the cell the pawn came *from*". If the engine does
   not expose the previous cell at path-cost time and no higher seam works cleanly,
   the collapse's central promise (*"you can't climb out. Period."*) has no
   implementation and the container model — which does work — was load-bearing.
   **UNMEASURABLE HERE. This is the first thing to check on the Desktop, and nothing
   else in this spec should be built before it returns.** Read
   `Verse.AI.PathFinder.FindPath`, `Pawn_PathFollower.TryEnterNextPathCell`,
   `CostToMoveIntoCell`, `Reachability.CanReach`.
2. 🔴 **A pit full of live, unreachable hostiles may never end a raid.** (§4 state 1.)
   Vanilla's raid AI and `GenHostility.AnyHostileActiveThreatToPlayer` have to cope
   with hostiles that can neither reach nor be reached. If they do not, every
   successful pit capture leaves the colony in permanent combat state and blocks
   end-of-raid resolution and anything waiting on it. UNMEASURABLE HERE; read `Lord`,
   `LordToil_*`, `RaidStrategyWorker`, `JobGiver_ExitMap`. **Highest shipping-bug
   risk in the item.**
3. 🔴 **`pit_trapped_reads_as_trapped` may recreate the original defect.** The
   collapse replaces a despawned occupant with a spawned pawn standing on a floor —
   visually a pawn standing on a floor. The entire depth read then rests on the wall
   edge art of ruling 19/33, and if that art does not carry it, he is looking at
   *"a pawn standing there staring at the camera"* again, this time with correct
   mechanics underneath. The Quarry reference is evidence it *can* work; it is not
   evidence that our one inner-shadow edge treatment will.
4. **Room-hood may be unreachable from terrain at all** (§3, §9-D), in which case
   *"this defines a room"* requires a built lip and a bare dug hole is not a prison.
   That is a change to what he thinks he ruled.
5. **`ActiveFluid` being map-wide may make his answer 7 unshippable as ruled** (§6,
   §9-F) — and this is invisible from the ruling, so it will otherwise be discovered
   mid-build.
6. **A prisoner bed may not be placeable on `RM_Channel_Superdeep`.** Its
   `<affordances>` list only `Light`. Possibly a one-line def fix, possibly a
   blocker. UNMEASURABLE HERE.
7. **`legator.prisonerrealism` may patch the same seam as §3's veto.** Unread
   (UNMEASURABLE HERE, confirmed absent from this Mac), adopted as the *backbone* of
   prisoner behaviour, and it auto-defers to overlapping mods — so it may either
   solve the confinement question for us or silently defeat our patch. Also unchecked:
   **Prison Labor**, which sends prisoners to work stations and therefore wants them
   to leave the pit, which the ruling forbids.
8. **`RM_Fill_Tar_Superdeep` is `Impassable` today** (§3) — a live contradiction with
   ruling 26 and with his answer 3, caused by a caveat that outlived its condition.
   Small fix, but it is the kind of stale gate this project has been burned by before.
9. **Deleting `PitEscapeUtility` removes shipped, tuned feel.** *"A healthy thrumbo in
   a shallow pit is out in seconds and ANGRY"* was a deliberate design and is gone by
   ruling — correctly, but he should see it named.
10. **Retiring `JobDriver_DigPitDeeper` may silently re-price digging** if
    `JobDriver_DigCanal` scales on `ConstructionSpeed` where the pit's driver scaled on
    `MiningSpeed`. UNCERTAIN — not read this pass. It also removes the named attach
    point for a future Jawa dig-speed bonus.
11. **This spec's own def and class names are proposals.** `RM_Spikes`,
    `PlaceWorker_SpikesOnExcavation`, `RM_SpikeUtility`, `RM_SuperdeepTrapUtility`,
    `RM_JobDriver_CaptureDown`, `RM_WorkGiver_CaptureDown` are all **NEW** and need
    his sign-off. None was guessed against an existing identifier.
12. **Nothing here was verified in a running game.** No RimSage, no def dump, no
    launch on this laptop. Every claim tagged CONFIRMED is a reading of this
    repository's own source and defs, and nothing more.

### What was NOT read in this pass, named so nobody assumes it was

`Source/Pits/Debug/PitDebugActions.cs` (442 lines, skimmed only),
`Source/Pits/DigStage/CompPitDigStage.cs`, `Source/Pits/SelfTest/Program.cs`,
`Source/RM_Patch_SuperdeepShooting.cs`, `Source/LiquidTypes/LiquidCorrosion.cs`,
`Source/Designator_DigCanal.cs` / `JobDriver_DigCanal.cs` / `WorkGiver_DigCanal.cs`,
FlowWorks' existing 13+3 north-star bars, `Pit_OpenPits.xml`'s actual `spikeDamage`
value, and `design/RimMandrake/flowworks_mod_definition.md` in full — its rulings 5,
17, 19, 20, 23, 24, 26, 33, 34-36 are cited here as recorded in the source files that
implement them (each names its own ruling in a comment), not re-read from the
definition doc. ⚠️ **Rulings 24, 34, 35 and 36 were not independently confirmed
against that doc in this pass** — they are carried from the item's own summary.
Anyone building from this spec should re-read that doc before touching art.
