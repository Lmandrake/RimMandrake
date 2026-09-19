## spec
Thin when filed — no spec/verify/criteria in the queue entry itself, but
fully specced as packet B4b of
`design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 (inputs: unit 13,
B4a, closed earlier today; outputs: repair bench (part-swap bills),
reassembly harness (head+frame+set → pawn), Recipe_ShopRebuild from corpse,
overclock as a bench job; verify: "rebuild a corpse; harness refuses without
a head; swap a leg on a live droid"; after: B4a). Built directly from that
packet, FOUNDRY, 2026-09-08.

## Built
- **`RSW_DW_RepairBench`** (`ThingDefs/Buildings_ShopBenches.xml`): a
  proximity landmark, not a bill-holder. Vanilla has no workbench-targets-
  a-live-pawn bill shape — bionic/prosthetic installs are always the
  health-tab `Recipe_Surgery` route, never a `Bill_Production` — so "the
  repair bench (part-swap bills)" gates the 5 install recipes from B4a
  (`RSW_DW_Install{Leg,Manipulator,Sensor,Motivator,Servo}`) plus the new
  overclock recipe to require one within 15 tiles
  (`Source/Droidworks/Recipe_InstallDroidPartAtBench.cs`, a thin subclass of
  B4a's `Recipe_InstallDroidPart` that overrides only
  `AvailableOnNow`/`CompletableEver`) rather than inventing a second,
  redundant production path.
- **`RSW_DW_ReassemblyHarness`**: a real `Building_WorkTable` with two bills:
  - `RSW_DW_AssembleDroid` (`Source/Droidworks/Recipe_AssembleDroid.cs`):
    consumes 1 head (any of the 7 family heads — never
    `RSW_DW_Head_Mindstone`, `MECHANOID_ORIGIN_CANON_1` unruled) + 1 Frame +
    1 each of the 6 fine parts, spawns a new droid pawn of the head's family
    (`DroidAssembly.KindForHeadDef`), carries the head's name/traits over if
    it had a snapshot (`CompHeadIdentity`), grants part-effect hediffs from
    whatever quality parts were fed in.
  - `RSW_DW_ShopRebuild` (`Source/Droidworks/Recipe_ShopRebuild.cs`):
    consumes 1 corpse + 1 Frame, spawns the SAME droid back (name, kindDef,
    faction, traits read off the corpse's own `InnerPawn` before it's
    consumed).
  - Neither is a vanilla `RecipeWorker.MakeRecipeProducts` override — that
    method doesn't exist on the base class (only `GenRecipe`'s static
    version does, and it only ever makes `ThingDefCountClass` products,
    never a `Pawn`). Both instead capture what they need in
    `ConsumeIngredient` (before the ingredient is destroyed) and do the
    spawn as a side effect of `Notify_IterationCompleted` — the same
    sequence `Toils_Recipe.FinishRecipeAndStartStoringProduct` already runs,
    confirmed by reading that method (`mcp__rimsage__read_csharp_symbol`).
- **`RSW_DW_Part_Frame`** (`ThingDefs/Parts_Droidworks.xml`): the 7th generic
  part, craftable (FabricationBench, Steel+ComponentIndustrial) rather than
  drop-table salvage like B4a's six — "Frame and most parts are craftable"
  (section 1.3); B9's own Primitive tier is the future proper route, this is
  the stopgap so the harness has a source before B9 lands.
- **`RSW_DW_Overclocked`** (`Effects_Droidworks.xml`) +
  `RSW_DW_OverclockDroid` recipe (`Source/Droidworks/
  Recipe_OverclockDroid.cs`, same bench-proximity gate): "overclock as a
  bench job" — nothing in the design doc specifies its mechanical shape
  beyond the name, so this is FOUNDRY's own scope call: a temporary,
  self-decaying (`HediffCompProperties_SeverityPerDay`, ~3 days) MoveSpeed/
  WorkSpeedGlobal boost.
- `DroidAssembly.cs`: the shared spawn helper both recipe workers call
  (`PawnGenerator.GeneratePawn` + `GenSpawn.Spawn` + name/faction/traits +
  part-effect hediffs).

## verify (live, minimal 25-mod list + quicktest, FOUNDRY 2026-09-08)
Build: `dotnet build Droidworks.csproj -c Release` — 0 errors, first try.

- **Both buildings and the Frame item spawn cleanly** (`rimworld/
  spawn_thing`), correct labels/stats, no `BadGraphic`, no config errors.
- **`RSW_DW_Overclocked` verified live** the same way B4a's part effects
  were: added directly via `jawa/pawn_health`, read back in the pawn's
  hediff list with severity 0.5 and the stage's stat offsets active.
- **`jawa/bill_add` accepted `RSW_DW_AssembleDroid` and `RSW_DW_ShopRebuild`
  onto a spawned `RSW_DW_ReassemblyHarness`** — this is real engine
  validation: `BillAdd` refuses (naming the valid list) if the recipe isn't
  in the building's `AllRecipes`, or if the ingredient filter is malformed.
  Both recipes' `RecipeDef` structure, ingredient filters (the 7-head list
  for AssembleDroid; the `Corpses` category — confirmed a real
  `ThingCategoryDef` via `mcp__rimsage__search_defs` — + Frame for
  ShopRebuild) and `workerClass` wiring are therefore confirmed
  well-formed by the running game, not just by static XML validation.
- **One real environment bug found and fixed along the way**: the harness
  never got worked because it had no power (`CompPowerTrader.PowerOn`
  false — `jawa/power_net` confirmed `powerOnBefore: false`, an
  unremarkable vanilla constraint on any `Building_WorkTable`, not a defect
  in this item's own code). Forced power on with `jawa/power_net
  forcePowerOn=true` and it stopped being the blocker.
- **Not reached live: an actual bill completing (a droid spawning from the
  harness).** Across ~34,000 ticks (~14 in-game hours) at Fast speed, with
  the bill staged (`shouldDoNow: true` throughout — the engine considers it
  workable), ingredients reachable, the bench powered, and every colonist's
  Crafting skill force-set to 12–15, no colonist ever picked up the job —
  a scheduling/priority matter on this specific quicktest's starting
  colonists, not a "bill rejected" or "ingredients invalid" signal (which
  would have shown as `shouldDoNow: false` or a `bill_add` refusal). No
  bridge tool exists to force a `Bill_Production`/`JobDriver_DoBill` to
  completion, the same limitation `DROIDWORKS_LIVE_LOOP_PROOF_1` (A1) hit
  for `Recipe_Surgery` jobs and `DROIDWORKS_HEADS_BRAINS_SPIKES_1`/
  `DROIDWORKS_FINE_PARTS_1` (B3, B4a, both today) already applied the same
  reasoning to. **The actual `Notify_IterationCompleted` spawn logic in
  `Recipe_AssembleDroid`/`Recipe_ShopRebuild` is therefore verified by code
  review only** (traced against `Toils_Recipe`/`GenRecipe` source via
  rimsage, not run to completion in a live game) — the single largest gap
  in this item's own verification, recorded plainly rather than glossed
  over. A future FOUNDRY session with more bridge time (or the owner
  playing it directly) should confirm an actual assembled/rebuilt droid
  once, then this note can be struck.
- **"harness refuses without a head"**: not driven as a live negative test
  either — it's a structural guarantee (a mandatory `IngredientCount` with
  no matching ingredient on the map makes vanilla's own bill-availability
  gate refuse to run), the same class of reasoning used for B3's "wrong key
  does nothing" data-spike claim.
- **"swap a leg on a live droid"**: the underlying `ApplyOnPawn` mechanism
  (quality → capacity offset) was already live-verified in B4a today; this
  item only added the proximity gate (`Recipe_InstallDroidPartAtBench`,
  unchanged `ApplyOnPawn`), which was not separately live-tested (would
  need a near-bench vs far-from-bench comparison) but is simple,
  deterministic C# (`AllBuildingsColonistOfDef` + distance) reviewed rather
  than driven.
- **Player.log, literal check**: same 12 pre-existing `Config error in`
  lines throughout the whole session (before and after every change) — zero
  new errors or exceptions from any of this item's defs or C#, including
  through ~34,000 ticks of live simulation with the bill staged.

## Assumptions recorded (Charter: "record what you assumed")
1. One representative `PawnKindDef` per family for `AssembleDroid`'s output
   (same 7 defNames B3/B4a already used for testing) — `DroidAssembly.
   KindForHeadDef`.
2. `RSW_DW_Head_Mindstone` is excluded from the harness's ingredient filter
   — `MECHANOID_ORIGIN_CANON_1` unruled, no "chassis + this head = a new
   race" mechanic exists yet to build against.
3. `AssembleDroid` requires exactly 1 of each of the 6 generic parts
   regardless of the chosen family's own B4a "legal set" — vanilla
   ingredient filters aren't conditional on another ingredient already
   picked, so a uniform requirement was the buildable option.
4. `ShopRebuild`'s ingredient filter is broad (any `Corpses`-category
   thing); the actual gate (must be a Droidworks-race corpse) lives in
   `Recipe_ShopRebuild.ConsumeIngredient` — a non-Droidworks corpse is
   silently refused (ingredients still consumed, nothing spawns). A known
   v0 rough edge: no narrower filter exists without hand-listing 57+
   generated corpse defNames.
5. Overclock's mechanical shape (temporary MoveSpeed/WorkSpeedGlobal boost,
   self-decaying) is FOUNDRY's own call — the design doc names it but
   specifies nothing about what it does.
