## spec
Full ruling: `design/Jawa/ownership_settlement_spec.md` (owner sitting 2026-08-31).
Build the **Inhabited** mod (RimMandrake tier, `mandrake.rm.inhabited`, `Inhabited_`
def prefix per `design/NAMING_SCHEME_PLAN.md`): the peaceful-entry visit
lifecycle for named frozen-world settlements, sitting on top of
`RM_Property` (built and committed this session, PROPERTY_FABRIC_BUILD_1).

Scope for this pass:
- **Manifest schema**: a settlement manifest def (districts present, sizes,
  adjacency, cast assignment slots, security props, faction security
  profile) — data-only shape, consumed later by DISTRICT_TEMPLATE_LIBRARY_1.
  This item does NOT author district content, only the schema + a loader.
- **Lifecycle**: arrival → compose (stub: single placeholder district until
  the template library lands) → cast → routes → departure → teardown to
  roster. Teardown persists a lightweight "casing" record (what the colony
  now knows about this settlement — not full map state) so a return visit
  can read prior knowledge without holding the whole map in memory.
- **Gate-search hook**: departure-time check reading the settlement's
  security profile (spec: "a faction searches leavers only if its profile
  says so") — stub the profile source as a def field for now, real per-
  faction tuning is RimUtinni data landing with SETTLEMENT_VERBS_WAVE_1.
- **Junkers pilot manifest** (RimUtinni data): one real settlement manifest
  using an actually-named Jawa_Junkers settlement from
  `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` (candidates: The
  Ore Moot, The Claim Jump, The Slagfield, The Fuel Works — pick one, low
  security per spec's "Junkers pilot: low security, forgiving").

Explicitly OUT of this item: district Lua templates (DISTRICT_TEMPLATE_LIBRARY_1),
crime/commerce/social verbs (SETTLEMENT_VERBS_WAVE_1), any claim-math change
(owned by RM_Property, do not touch).

## verify
- `validate_patch.py` clean against the live mod set.
- `Def.ConfigErrors()` triage: FOUNDRY runs a live quicktest cold load after
  build, greps `Player.log` for `^Config error in`, fixes or documents any hit
  (see memory: config-errors-are-invisible-to-validate-patch).
- Live-quicktest-observed: the visit lifecycle actually runs start-to-finish
  on the Junkers pilot manifest — arrival fires, a placeholder district
  composes, departure fires the gate-search hook (log line or screenshot),
  teardown leaves a casing record readable on a second visit.
- Folder-basename check before deploy: confirm via `deploy_custom_mods.py`
  plan output that `Inhabited`'s folder name is unique across
  RimMandrake/RimStarWars/RimUtinni/SPLIT_Phase3 (this exact collision has
  hit twice already this session — fire ecology, weather suite).

## criteria
A correct v1: the Inhabited mod loads, RM_Property's claim engine is
untouched, one real Junkers settlement can be visited start-to-finish on a
quicktest map with a stub district, and a casing record persists across a
second visit. District art/verbs are deliberately absent — this item proves
the LOOP, not the content.

## FOUNDRY, 2026-09-06/07: RimWorld crashed mid-live-check — environment note

Built the missing settlement producer (two debug actions: "Create settlement
here", "Leave settlement now", "Re-enter settlement here" — see
`DebugActions_Inhabited.cs`), deployed, and launched the game on the owner's
full 603-mod `ModsConfig.xml` to run the batched live check. RimWorld's
process RAM climbed to ~21GB during `rimworld/start_debug_game_ready`'s full
world+map generation (this list auto-completes the entire research tree on
a dev quicktest, firing hundreds of `[Ninefold]` hook lines — a real,
healthy sign those hooks work — right up to the point the process vanished
with no exception, no crash dialog, nothing in `Player.log` past the last
research-completion line). Base boot to main menu on this same 603-mod list
was clean (bridge up, responded normally) — the crash is specific to the
heavy dev-quicktest generation, not the mod load itself.

**Ruled out, not just asserted**: the owner had Codex open concurrently;
checked its footprint directly (`Get-Process codex*`) — `codex` ~180MB +
`codex-code-mode-host` ~37MB, and the Windows host still had ~34.5GB free
of 66GB total at the time. Codex is not a plausible contributor to a 21GB
RimWorld spike on a 66GB machine.

Not yet determined: whether this is a `start_debug_game_ready`-specific
regression on unusually large (600+) mod counts, a one-off, or something
else. Retrying via an existing scratch save (`gravship_scratch_d.rws`)
instead of a fresh quicktest world, to avoid the same heavy path while
still completing this item's live-check bar. Worth its own queue item if it
reproduces on a clean retry — flagging here rather than letting it be lost
to conversation, per the "code review" doctrine that only a recorded finding
counts.

## FOUNDRY, 2026-09-07: scratch-save retry — debug actions confirmed registered and callable; compose-step proof still blocked, honestly

The `start_debug_game_ready` OOM was not retried. Loaded `gravship_scratch_d`
instead (`rimworld/load_game_ready`, `ignoreModCompatibility: true` for one
unrelated missing mod, "Just F*King Landing" — not one of this session's
mods), which succeeded cleanly with RimWorld's own RAM staying flat (~16.7GB,
no further growth) through the whole session. Re-saved as `gravship_scratch_e`
and `WORLDMAP_V1_original_e` (owner's request) once the full active 598-mod
set was confirmed to include every mod this session touched.

**Real bug found and fixed along the way, unrelated to the crash**:
`rimworld/execute_debug_action`'s own catalogue (the correct discovery route
per `skills/rimbridge/SKILL.md` §4 — never `search_debug_actions` on a 590+
mod list) never listed ANY of this session's three new debug actions across
Inhabited/TheftHauler/Visibility except Inhabited's (which only worked
because those methods were added to an ALREADY-COMPILING file, not a new
one). Root cause, confirmed with `strings -el` against the actual installed
DLLs, not guessed: both `RM_TheftHauler.csproj` and `Visibility.csproj` set
`EnableDefaultCompileItems=false` with a hand-maintained `<Compile Include>`
list that silently never named the new `DebugActions_*.cs` files — the exact
trap `Ninefold.csproj`'s own comment already documents from an earlier
session. "0 warnings/0 errors" meant the compiler was never told the file
existed. Fixed both csproj files (switched to the default SDK glob;
Visibility needed an explicit `<Compile Remove="SelfTest/**/*.cs">` since
that's a separate sub-project). Also found `DebugActions_TheftHauler.cs`
itself was missing `using LudeonTK;` — a second, independent bug the fix
surfaced. Committed `6e6ce2d9`, not yet deployed (would need another
restart; the game is up this session).

**Inhabited's three debug actions ARE genuinely registered and callable** —
confirmed via `rimworld/list_debug_action_children` (path
`Actions\Create settlement here (pick manifest)` etc., `actionType: Action`,
`execution.kind: Direct`) and `rimworld/execute_debug_action`, which
returned `success: true` with no error.

**Still NOT proven: the compose step actually running.** `execute_debug_action`
ran `CreateSettlementHere()`, which opened its `Dialog_DebugOptionListLister`
manifest picker as designed — but that dialog cannot be clicked through via
the bridge (no tool exists to select a debug-menu list item by index/label;
`rimworld/close_window` closed it cleanly instead, leaving the game in a
clean, unblocked state). Separately, and more fundamentally: `CurrentTile()`
(copied from the pre-existing `CreatePlaceHere()` pattern) returns
`Find.CurrentMap.Tile` whenever a map is loaded — which is ALWAYS true once
a colony is loaded, including via world-view camera switches
(`jawa/world_view` moves the CAMERA, not `Find.CurrentMap`). So even with
the picker completed, this debug action as written can only ever target the
CURRENT colony's own tile, where `GetOrGenerateMapUtility.GetOrGenerateMap`
finds the existing map and returns it UNCHANGED — `Inhabited_SettlementMapGenerator`
never runs, so `GenStep_ComposeSettlementDistrict.Generate` never fires. A
real proof needs either an explicit tile parameter on a `ToolMap`-typed
debug action (so the bridge can supply `x`/`z` on an empty tile), or a
picker-answering bridge tool. Neither built this pass — flagged rather than
forced.

**Net for this item**: the producer gap this pass's earlier note found is
now demonstrably real and callable, not just "should work" — a meaningful
step past "no way to reach it at all." The end-to-end compose/cast/
departure/casing proof this item's own verify bar wants is still owed, and
now has a precise, narrow reason why (same-tile GetOrGenerateMap no-op +
no picker-click tool) rather than a vague "needs a live session." Left
`doing`.

## FOUNDRY, 2026-09-09: offline re-verify after a wave of sibling-item fixes — mechanically complete, live bar still owed

Re-checked from scratch rather than re-authoring, per this pass's brief. RimWorld
was mid-cold-load on the full ~600-mod list the whole session (crashed twice
overnight, currently rebooting again) — `rimflow bridge who` showed FREE, but
no live bridge call was attempted per this pass's own instruction; everything
below is offline.

**The two blockers named in the 2026-09-07 note are both gone, closed by sibling
items filed off this one's own findings, not by this pass:**
- `CurrentTile()` (`DebugActions_Inhabited.cs`) now falls back to
  `Find.WorldSelector.SelectedObjects` when no map is open, so "Create
  settlement here" can target an empty world tile instead of only ever
  re-resolving the CURRENT colony's own tile (the same-tile `GetOrGenerateMap`
  no-op the last note flagged is no longer the only path in).
- A real, live-verified, non-debug-menu producer exists:
  `jawa/world_settlements_import` with a `world_object_def=Inhabited_Settlement`
  column (`INHABITED_SETTLEMENT_PRODUCER_GAP_1`, closed `39050abc`,
  live-verified 2026-09-04 down to an independent `jawa/world_objects_get`
  read-back showing `isSettlement: false` — a genuinely different C# type, not
  a relabeled `Settlement`). This sidesteps the debug-menu
  `Dialog_DebugOptionListLister` picker-click gap entirely for a real
  end-to-end proof; the debug actions remain a second, harness-only route.
- `WorldObject_Inhabited`/`WorldObject_InhabitedSettlement` now derive
  `MapParent` (`INHABITED_SETTLEMENT_MAPPARENT_GAP_1`, rebased+live-verified
  2026-09-04, owner card ruling G10) — the `InvalidCastException`
  `GetOrGenerateMap` used to throw on any `Inhabited_Settlement` is gone.
- `SettlementManifestDef` binding is live (`SETTLEMENT_MANIFEST_BINDING_1`,
  closed `a2b307b3`).
- The compose step is no longer a bare single-district stub: all four Junkers
  district templates (scrapyard, dwelling cluster, cantina block, depot) are
  wired live (`DISTRICT_TEMPLATE_LIBRARY_1`, closed v1, `a0816bec`) —
  ahead of this item's own scoped bar ("stub: single placeholder district
  until the template library lands").

**This pass, independently re-run, all clean:**
- `dotnet build -c Release` on `Inhabited.csproj` — 0 warnings/0 errors,
  output already matched the committed DLL (no drift to rebuild).
- `validate_patch.py` on `src/RimMandrake/Inhabited` and
  `src/RimUtinni/AshkarrInhabited`, with `--defs` covering Mods + Workshop +
  the base game's own `Data` folder (needed or `MapCommonBase` false-positives
  as unresolved — it's a shipped Core abstract def, confirmed by reading
  `CommonMapGenerator.xml` directly) **and** `--live` against tonight's
  `2026-09-09T01-54-07Z` DefDump capture (590 mods; current `ModsConfig.xml`
  has 587 — a 3-mod drift, both `mandrake.rm.inhabited` and
  `mandrake.rut.inhabited` present in the capture, close enough for a
  defName-existence check): **29 files, 0 errors, 0 warnings.**
- Folder-basename uniqueness: exactly one `Inhabited` directory anywhere under
  `src/` (`src/RimMandrake/Inhabited`) — no collision across tiers.
- `git status` on `src/RimMandrake/Inhabited` and `src/RimUtinni/AshkarrInhabited`:
  clean, nothing uncommitted.
- Read `GateSearchHook.cs` and `SettlementCasing.cs` in full against the spec's
  own language ("a faction searches leavers only if its profile says so";
  casing as "the residue... how many times we have been here, which district
  labels were composed, whether the gate has ever searched us") — both match
  exactly, correct `Scribe_Values`/`Scribe_Collections` usage, `PostLoadInit`
  null-guard present.

**Still genuinely owed, not attempted this pass (bridge unavailable by this
pass's own brief, game mid-cold-load all session):** the item's own live bar —
`Def.ConfigErrors()` triage against a fresh `Player.log` on this exact code
(current deployed `Mods/Inhabited/` copy is stale relative to repo HEAD per
`deploy_custom_mods.py --mod Inhabited`'s plan output — About.xml, the DLL and
one district template all drifted since the last deploy; not deployed this
pass since the game was mid-load the whole session and a companion/mod DLL
should only be written while the game is down), and the actual
arrival→compose→cast→departure→gate-search→teardown→casing run on the Junkers
pilot manifest, observed rather than inferred from source. Left `doing` — this
is offline-complete, not done.

## FOUNDRY, 2026-09-12: deploy staleness already resolved elsewhere; deep re-read against RimSage, no bugs found; live bar still owed

Reclaimed and started per this pass's brief (a staleness audit flagged the
deployed copy stale vs. HEAD). Re-checked rather than trusting that claim:

**Not stale anymore.** `deploy_custom_mods.py --mod Inhabited` and
`--mod AshkarrInhabited` both now report "in sync" — a `filecmp.cmp` byte
comparison, not a timestamp guess (read the tool's own `compare()` to confirm).
Both mods' folders match repo HEAD exactly (40 and 8 files respectively). The
2026-09-09 note's staleness was real at the time and has since been closed by
an intervening deploy (most likely `MOD_OPTIONS_RETROFIT_1`'s 46-mod pass,
which touched `RM_InhabitedMod.cs`/`RM_InhabitedSettings` — new this session,
not mentioned in any prior note on this item). No deploy action was needed or
taken this pass.

**Game was mid-cold-load all session; this pass's own brief said stay off the
bridge entirely** — no live attempt made, deploy or otherwise.

**Full re-read of the arrival→compose→cast→stock→fate-detection→departure→
gate-search→teardown→casing chain, cross-checked against RimSage rather than
trusting the 2026-09-09 clean bill:** `WorldObject_Inhabited`/
`WorldObject_InhabitedSettlement`, `GenStep_ComposeSettlementDistrict`,
`GenStep_InhabitedCast`, `GenStep_InhabitedStock`, `InhabitedFateWorker`,
`MapComponent_InhabitedWatch`, `GateSearchHook`, `Patch_SettlementDeparture`,
`Patch_Game_DeinitAndRemoveMap` (Patch_MapRemoval.cs), `InhabitedStock`,
`SettlementCasing`, `DisplacedPool`, `Patch_BeggarsFromPool`,
`StructureInjectionsBridge`, `SettlementManifestDef`, `InhabitedCastDef`,
`LordJob_Inhabited`/`LordToil_InhabitedRoutine`, `CharacterApplier`,
`RM_InhabitedMod`/`RM_InhabitedSettings` (today's Mod Settings addition,
previously unreviewed on this item). Verified against the actual 1.6 source
via RimSage, not assumed: `Game.DeinitAndRemoveMap(Map, bool)` signature,
`GravshipUtility.PlayerHasGravEngine(Map)`, `ThingOwner.TryAddOrTransfer`,
`LordJob.ShouldRemovePawn` default-true, `Thing.DeSpawnOrDeselect` (exists on
`Thing`, not `Pawn` — confirmed against `MapDeiniter.cs`'s own identical
call), `QuestGen_Pawns.GeneratePawn(Quest, PawnGenerationRequest, bool)`,
`PawnKindDefOf.Beggar`, `PawnGenerationRequest.KindDef`, the
`StructureInjectionsBridge` reflection targets (`RimplacePlan.Parse`,
`GenStep_RimplacePlan.ApplyPlan`, and all five `Footprint*`/`HasFootprint`
fields — confirmed as public fields, not properties, matching
`AccessTools.Field`), and `Lord.lastPawnHarmTick`. Also confirmed GenStep
order values in XML (850/900/910) match every code comment's claimed
ordering, and the Junkers pilot manifest (`SettlementManifestDefs_TheClaimJump.xml`)
matches spec exactly: settlementName "The Claim Jump", low-security
(`searchesLeavers=false`), a real `RM_InhabitedPlace_Scrapyard` place ref, and
the `FleeIfThreatened` fate. **Found no new bugs** — every prior fix
("opus code review" comments throughout, several dated) checked out, and
nothing this pass's more careful RimSage cross-check contradicted. Re-ran
`validate_patch.py` on both mods: 29 files, 0 errors, 0 warnings, matching
2026-09-09.

**Net: this item is unchanged in substance — offline-complete, mechanically
verified twice now — and the live bar is still the only thing between it and
close.** Nothing was deployed because nothing needed to be, and the bridge
was correctly left alone this pass. Left `doing`; `needs=deploy` is NOT set
(already in sync) — the actual blocker is a live quicktest with bridge
access, not a deploy.
