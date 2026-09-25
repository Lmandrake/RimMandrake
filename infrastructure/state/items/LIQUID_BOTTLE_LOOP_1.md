# LIQUID_BOTTLE_LOOP_1 — bottles as real items: fill, use, dirty, wash + special behaviors

Filed by BENCH, 2026-09-13 (`design/RimMandrake/liquids_framework_design.md`
§4 "Bottles are real items" + "Special behaviors").

## spec

Bottle chain: `RM_BottleEmpty` → fill job (terrain edge or tank) →
`RM_Bottle<Liquid>` (generator-emitted per row) → use → `RM_BottleDirty` →
wash job (consumes water) → empty. Buckets = larger bottle, same chain.
BARRELS too (owner-ruled 2026-09-13, "very scavenger"): ~25-unit big sibling,
same chain plus fill/empty bills at a tank; barrels are the vanilla-native
bulk trade route — every trader buys/sells them with zero patches.
Dirty stage behind a Mod Settings toggle, default ON in the campaign; off =
use returns a clean empty. Special behaviors as row data, no per-liquid C#:
revert timer (bottled boiling/icy → fresh), rot (bottled blood via
CompRottable; household recipe → hemopack before spoil). Bottles carry
cuisineTags ThingCategories so the future RSW cuisine mod cooks against tags,
never defNames. Blood is item-only in v1 — no blood terrain.

## verify

Quicktest: full loop observed (fill from a shore, drink, dirty appears, wash
returns empty). Timer checks: a boiling bottle becomes fresh; a blood bottle
rots on schedule and the hemopack recipe beats the clock. Settings-off run:
no dirty bottles anywhere, loop still whole.

## Watch out

- Depends on LIQUID_REGISTRY_CORE_1 (bottles are generator-emitted from rows).
- DBH drinkable registration is a separate item (LIQUID_THIRST_CHAIN_1) — this
  item's bottles must be drinkable-agnostic and work with DBH absent.
- The DBH bottle-inheritance bug ManyWaters hit (`ParentName="DBH_WaterBottle"`
  broken, worked around via `ResourceBasedMom`) — reuse that workaround.

## Tank pass, 2026-09-18

Built the tank the design's own "fill at terrain edge OR tank" names.
`RM_LiquidTank` (`Defs/LiquidTypes/ThingDefs/RM_LiquidTank.xml`) is a real
player-buildable `Building` — `Building_LiquidTank`
(`Source/LiquidTypes/Building_LiquidTank.cs`) holds ONE `LiquidDef` and a unit
count, 300 units base capacity (Mod Settings `tankCapacityMultiplier`, 0.2x-5x).
Filled by pouring a container in
(`WorkGiver_EmptyBottleIntoTank`/`JobDriver_EmptyBottleIntoTank`), drained by
filling an empty one from its stock
(`WorkGiver_FillBottleFromTank`/`JobDriver_FillBottleFromTank`) — the same
opportunistic WorkGiver/JobDriver shape as the terrain fill/wash pair, not a
RecipeDef/IBillGiver, so the whole loop stays one architecture.
`RM_LiquidTankUtility` finds the nearest reachable tank generically off
`LiquidDef.UnitsFor(size)`/`FilledDefFor(size)`, exactly like
`RM_LiquidBottleUtility` does for terrain — no per-liquid, no per-size branch.
Wired into the SAME registry every bottle already reads (`LiquidDef.bottled`),
not a parallel stock model. Mod Settings: `tankLoopEnabled` (master switch,
default on) + `tankCapacityMultiplier`, own contiguous section, defaults =
shipped behaviour.

Art: `src/RimMandrake/FlowWorks/art_source/UniversalCargoTank/` concept
conformed via `conform_sprite.py` onto a 256x256 canvas (drawSize 2.0 x 128
px/cell) rather than regenerated — a synthetic centred-bbox reference, since
no prior real texture of this building exists to match a pose against.
Validated clean (`validate_sprite.py`, 1 benign WARN on faint edge alpha).

Deliberately the v1 slice the item's own notes name: ONE fixed (not
minifiable), single-liquid-at-a-time tank. NOT built, and staying that way for
a future item: the universal cargo tank the full liquid-logistics epic
describes (design §4/§6/§9 — minifiable, ANY liquid via per-net adapters,
pump/hose/tanker-raid interop, VE PipeSystem adoption). Stale "no tank exists"
notes in `RM_LiquidBottles_Base.xml`/`LiquidDef.cs`/`RM_LiquidBottleUtility.cs`
corrected to point at what actually ships now.

Build: `dotnet build` on `RimMandrake_FlowWorks.csproj`, 0 warnings/0 errors.
`validate_patch.py` clean against both `--live` (2026-09-18T02-17-44Z capture,
632 mods) and `--defs` (Data+Workshop+Mods, `ModsConfig.FULL.LATEST.xml`) —
22 files, 0 errors, 0 warnings; only pre-existing informational notes about
custom `Class=` attributes the validator cannot resolve from XML (every
existing bottle def carries the same note; not new).

Deployed: `deploy_custom_mods.py --mod FlowWorks --apply` — 27 files written
(this also caught up the earlier-tonight bottle/bucket/barrel commits, which
had never been deployed either). `Assemblies/RimMandrakeFlowWorks.dll` is the
ONE file still undeployed — locked by the running game (bridge held by BENCH
throughout this pass) — owed on the next restart/shutdown window.

**OWED, explicitly**: a live quicktest of the tank loop (pour a filled
container in, drain an empty one out, watch the inspect string move) — bridge
was held and idle 0 min the entire pass, so this stayed offline per the
item's own "stay offline in doubt" discipline. Same quicktest debt the
fill/wash half already carried.

## live pass — 2026-09-25 (FOUNDRY, full 627-mod list, scratch map at tile 7344)

FlowWorks XML redeployed before the load. Settings live:
`bottleLoopEnabled`/`bottleDirtyStageEnabled` both true.

- **🔴 Fill never produced a filled bottle.** An `RM_BottleEmpty` 5 cells from
  `WaterShallow` (157,119). Four attempts through `prioritized_work` (real
  `RM_FillBottleWorkGiver`) and `ordered_job`, with three different colonists including one
  freshly spawned. The job is accepted, then ends, and the empty bottle sits back at its
  spawn cell with no `RM_Bottle_*` anywhere. The fresh pawn visibly reached the water
  cell before it ended. The WorkGiver also never picked the bottle up on its own. Cause
  not isolated: Player.log was already at its message cap (GreentideRoil
  static-ctor spam), so any exception in `JobDriver_FillBottle`'s finish toil
  would not show. Next step is a fresh-log load and reading
  `RM_LiquidBottleUtility.LiquidAt(WaterShallow)` live.
- The drink, dirty, wash and settings-off steps were never reached, because they depend on
  the fill.
- **The verify bar's timer checks cannot pass as built:** `revertsTo`/`rotsTo` row
  data is still unimplemented ("nothing reads them yet"), and blood is deferred. This
  is a scope gap in the item, not a live failure.
- Deleted the stale "no tank building exists" claim from `RM_LiquidBottles.xml`
  and its generator (`5fb3dd079`).
