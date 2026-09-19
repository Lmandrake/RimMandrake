# STAGED_LORE_PROOF_SPIKE_1 — live proof that staged-lore text swaps actually work

Owner ordered a live experiment 2026-09-11: one real description that changes
by campaign stage in a running game, with a genuine before/after screenshot,
before any build/no-build ruling.

## This is not a fresh spike — it closes a gap on STAGED_LORE_BUILD_1

`STAGED_LORE_DESCRIPTIONS_1.md` already carries the owner's GO ruling
(2026-09-11) and `STAGED_LORE_BUILD_1` (commit `dd882616e`) already built the
real mechanism: `mandrake.rm.lorestages` (engine) + `mandrake.rut.scarlandsladder`
(the Scarlands SSGM 1-5 ladder, placeholder text, wired to `RUT_Scarlands`'
`description`/`settleWarning`). That build was closed (`fc82d9030`) as "built
and proven" — but its own commit body says **"live in-game proof... owed"**,
because the 18/18 evidence was an offline selftest compiling the production
files against the real `Assembly-CSharp.dll`, never an actual running game.
This item is that missing live proof, not a reimplementation.

## What was proven, live, on a 7-mod minimal stack

Deployed `mandrake.rm.lorestages` + `mandrake.rut.scarlandsladder` (previously
built but never deployed to the game's `Mods\` folder) alongside their real
dependency `mandrake.rut.patches` (ships `RUT_Scarlands` itself), on a fresh
minimal `ModsConfig.xml` (harmony, core, rimbridgeserver, the three above, plus
`mandrake.rm.weathersuite` pulled in as a transitive dep). Quicktest colony,
tick 1.

1. Forced world tile 100 to biome `RUT_Scarlands` via `jawa/world_tile_set` +
   `jawa/world_commit` (no worldgen involved — a direct field write on a
   disposable quicktest planet, per `rimworld-debug-testing`'s "test
   destructively" ruling).
2. Selected that tile in the real World screen and opened its real Terrain
   inspector tab (`WITab_Terrain`) — the exact display surface the mechanism
   targets.
3. **BEFORE**: `Transient/staged_lore_proof_2026-09-11/BEFORE_stage0_scarlands_terrain_tab.png`
   — stage 0, the shipped baseline description verbatim.
4. Advanced the ladder: `jawa/lore_stage_set {ladderId: "Scarlands", stage: 3}`
   (a new bridge tool, see below). Read back the raw def field via
   `jawa/get_defs` first — it already showed the stage-3 placeholder text.
5. **AFTER**: `Transient/staged_lore_proof_2026-09-11/AFTER_stage3_scarlands_terrain_tab.png`
   — same tile (`Debug world tile ID 100,0`), same panel, **no reselect, no
   reopen** — the text changed on the next frame, confirming the mechanism's
   own claim that this display path is read-live and needs no cache
   invalidation for the biome surface.
6. Reset to stage 0 and confirmed the raw field returned to the shipped
   baseline byte-for-byte — proves the load-hazard fix (defs are process-global
   and are not reloaded between saves; `GameComponent_LoreStage.Apply()` must
   restore-then-apply every time, not advance-in-place) also works, not just
   the forward direction.
7. `[LoreStages] cache reachability: ThingDef.descriptionDetailedCached=found,
   HediffDef.descriptionCached=found` printed to the live log — the two
   reflection targets the mechanism depends on resolve correctly against this
   RimWorld build (this ladder doesn't exercise them, since it targets a
   BiomeDef, not a ThingDef/HediffDef, but their reachability is itself part of
   what needed live proof).

Zero exceptions or config errors attributable to either mod. The unrelated
noise on this minimal list (474 cross-ref errors, 411 patch failures) is
donor content wanting DLCs/mods this 7-mod stack doesn't carry (confirmed by
reading the actual lines — `Odyssey`-only GenStepDefs, a DLC-only ModExtension
type) and does not touch `RUT_Scarlands`, `RUT_ScarlandsLadder` or
`RimMandrakeLoreStages.dll`.

## A tool was added, not just a test: `jawa/lore_stage_get` / `jawa/lore_stage_set`

The mod's own dev-mode entry point (`Actions\Set ladder stage...`) opens a
hand-built two-level `LudeonTK.Dialog_DebugOptionListLister` — genuine runtime
UI, not a node in the enumerable debug-action tree, so
`execute_debug_action` cannot reach into it. The only route is a real mouse
click, and on this shared desktop a live human's own File Explorer search
window intercepted two clicks mid-attempt (measured, not theoretical). Rather
than fight OS-level click contention on a machine other people are using,
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchLoreStageTools.cs`
adds two reflection-based tools that call the exact same public API
(`GameComponent_LoreStage.GetStage`/`SetStage`) the debug action calls, with no
project reference to `RimMandrake.LoreStages.dll` (so the companion still
loads fine on any mod list that doesn't carry it). This is now the
unattended-proof route for every future ladder, not a one-off hack — deployed
with `--gm` build 22404bef088c, registered live (companion tool count
317→320).

## Verdict: BUILD. The mechanism works exactly as designed, live.

- **Feasibility**: confirmed, a third time, now with an actual screenshot
  instead of a selftest. The def-mutation approach (no Harmony) is real: the
  world tile inspector reads `BiomeDef.description` at draw time, a plain
  field write is visible on the very next frame, and restoring the shipped
  baseline before reapplying correctly undoes a previous session's stage.
- **How a content author would actually author a staged description**: exactly
  the shape `RUT_ScarlandsLadder.xml` already uses — an XML `RM_LoreStageTableDef`
  naming `defType`/`defName`/`field`, then a `stages` list of `{stage, text}`.
  No code per ladder, no code per def; a designer edits XML only. That is
  already the real authoring surface, not a sketch of one.
- **Cost/complexity if this became a real system across many defs**: low and
  flat. Each new consumer is one more `RM_LoreStageTableDef` XML file (the
  Contagion, the war lab, the Webwork, per `STAGED_LORE_DESCRIPTIONS_1.md`'s
  own list) — zero engine changes required. The one recurring cost is the
  reflection cache-clear for `ThingDef`/`HediffDef` targets (not exercised by
  the Scarlands ladder, which is BiomeDef-only) — that code path exists and its
  reflection targets resolve on this build, but this session's live proof did
  not exercise a ThingDef/HediffDef target end-to-end; that's the one honest
  gap left, worth a second short live check before leaning on it for an item
  like the Propane Lakes' war lab where the description lives on a ThingDef.
- **What is NOT proven here and shouldn't be oversold**: reveal GATES. Nothing
  calls `AdvanceStage` from a quest or dialogue yet — every stage change in
  this proof and in the mod's own debug action is manual. That's a separate,
  smaller piece of work (a quest/signal calling one method) and is explicitly
  out of this item's scope.

## Cleanup

Full mod list restored (`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`),
bridge released. `mandrake.rm.lorestages` and `mandrake.rut.scarlandsladder`
are deployed to the game's `Mods\` folder but not enabled on the owner's real
list — enabling them for the campaign is a separate call (BENCH/owner), not
this item's to make.
