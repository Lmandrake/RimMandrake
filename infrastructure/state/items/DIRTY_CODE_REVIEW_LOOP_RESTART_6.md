# DIRTY_CODE_REVIEW_LOOP_RESTART_6

Continuity note for resuming the standing dirty-code-review loop (FOUNDRY).
Successor to `DIRTY_CODE_REVIEW_LOOP_RESTART_5` (resumed this session,
closed below).

## Code-review state at handoff

`infrastructure/state/CODE_REVIEW_STATUS.json`: **338 clean entries** (was
311 at the last restart). 656 `.cs`/`.py` files total under `src/` — just
over half clean now; explicitly multi-session, never claim it's finished.

This session's waves (7 waves, 27 files, all fanned out as parallel
subagents at `sonnet` — nothing this session's files touched was
central/live-companion tier, so no `opus` needed this round):

- **Property** (`mandrake.rm.property`) — GameComponent_PropertyLedger.cs,
  RecognizabilityUtility.cs, ClaimDecay.cs, PerceptionUtility.cs,
  TakingAct.cs, PropertyTuning.cs, WitnessEntry.cs, FactionRecord.cs — all
  clean, no bugs. Remaining DIRTY: ClaimBasis.cs, ClaimantKind.cs,
  ClaimantRef.cs, PropertyEvents.cs, TakingEvent.cs, SelfTest/Program.cs.
- **Graffiti** (`mandrake.rm.graffiti`) — GraffitiJobUtility.cs,
  JobDriver_PaintGraffiti.cs, JobGiver_GraffitiPaintingSpree.cs,
  RMGraffitiDefOf.cs, ThoughtWorker_ViewedGraffitiMark.cs — clean.
  **`ModExtension_Graffiti.cs` has a REAL FIX NOT YET DEPLOYED** (see
  below) and stays DIRTY until it lands. Remaining DIRTY otherwise:
  BreachBiasHook.cs, GraffitiCategory.cs, JoyGiver_PaintGraffiti.cs,
  MentalState_GraffitiSpree.cs.
- **DesertVehicleReskin** (`mandrake.rm.desertvehiclereskin`) —
  VehicleFuelPatches.cs, VegetableFuel.cs, FuelDebugActions.cs — the whole
  `Source/Fuel/` subfolder is now clean. Remaining DIRTY: the art-build
  scripts under `Source/` root (build_beast_vehicle.py,
  build_eopie_sled_{east,north,south}.py, despeckle.py, recrop_east_v2.py)
  — one-off human-run art tools, not yet reachability-checked this pass.
- **JawaIonWeapons** (`mandrake.rsw.ionweapons`) — **fully clean**:
  DamageWorker_IonBuildup.cs, IonDamageDef.cs, StatPart_InverseBodySize.cs,
  SelfTest/Program.cs.
- **Visibility** (`mandrake.rm.visibility`) — VisibilityModInit.cs clean.
  **`GameComponent_ColonyVisibility.cs` has a REAL FIX NOT YET DEPLOYED**
  (see below), stays DIRTY. `ColonyVisibilityRaidPatch.cs` was
  re-marked clean after its two call sites were updated for that same fix.
  Remaining DIRTY: SelfTest/Program.cs.
- **SalvageClaim** (`mandrake.rm.salvageclaim`) — SalvageClaimFeeUtility.cs
  clean.
- **TheftHauler** (`mandrake.rm.theft_hauler`) —
  JobDriver_TheftHaulUninstall.cs clean.
- **StructureInjections** (`mandrake.rm.injections`/`mandrake.rsw.injections`)
  — GenStep_RimplacePlan.cs clean (terrain/roof ordering, the repo's own
  known trap class, specifically checked and confirmed correct).
- **SacredGraffiti** (`mandrake.rm.sacredgraffiti`) — SacredGraffiti.cs
  clean.
- **PlantGrowth** (`mandrake.rut.plantgrowth`) —
  Patch_Plant_GrowthRate.cs clean.
- **EmpirePursuit** (`mandrake.rut.empirepursuit`) — HarmonyPatches.cs
  clean (no repeat of the earlier RuthlessPursuingMechanoids.cs
  raid-timer-floor bug class).

### Real bugs found and fixed this session (3)

1. **`ModExtension_Graffiti.cs`** (commit `1e4fe0eb`) — the startup
   mis-wire validator checked only 2 of 3 possible shapes; added the
   `viewerReactionThought`/`workerClass` check (a mark pointing at a
   `ThoughtDef` whose `workerClass` isn't `ThoughtWorker_ViewedGraffitiMark`
   loaded clean and silently never reacted). Built clean; **deploy to the
   live Mods folder failed — DLL locked, game up.** Repo's own
   `Assemblies/RimMandrakeGraffiti.dll` was rebuilt and committed
   (`75a5f517`) so the fix is real and buildable, just not yet live.
   **File stays DIRTY until a deploy succeeds; then `mark-clean` it.**
2. **`ThoughtWorker_ViewedGraffitiMark.cs`** (commit `b0db3c45`) — stale
   `<thoughtClass>` comment fixed to `<workerClass>`, matching #1's real
   gate. Comment-only, no behavior change, no deploy needed — already
   marked CLEAN.
3. **`GameComponent_ColonyVisibility.cs`** (commit `8a24dcd7`) — `tileMemory`
   was `Dictionary<int, TileVisibilityMemory>` keyed on raw
   `PlanetTile.tileId`, which is only unique *within* one planet layer;
   Odyssey gravships can cross layers (`CompLaunchable.TryLaunch(...,
   canTraverseLayers: true)`), so a surface tile and an orbital tile
   sharing a `tileId` would silently clobber each other's decay memory.
   Rekeyed to `Dictionary<PlanetTile, ...>` (vanilla precedent:
   `WorldLandmarks.landmarks` uses the identical Scribe shape). Both
   csproj and SelfTest build clean, `selftest_colony_visibility.py` still
   36/36. **Deploy to the live Mods folder failed — DLL locked, game up.**
   Repo's own `Assemblies/RimMandrakeVisibility.dll` rebuilt and committed
   alongside. `ColonyVisibilityRaidPatch.cs`'s two call sites were updated
   for the new signature and it was re-marked CLEAN (coordinator did this
   directly, having read the full diff — trivial signature-following
   change). **`GameComponent_ColonyVisibility.cs` itself stays DIRTY
   until a deploy succeeds; then `mark-clean` it.**

**Both pending deploys are small, safe, already-built fixes blocked only
by the live game holding the DLL open.** Neither is worth forcing a
restart on its own — fold them into the next natural restart's deploy
step (`deploy_custom_mods.py --mod Graffiti --apply` and
`--mod ColonyVisibility --apply`, or whatever the exact folder names are —
verify under the Steam Mods path), then run `mark-clean` on both files.

## Doctrine, unchanged from RESTART_5 — still the process

Check reachability before reviewing. Fix ≠ clean. Subagents `mark-clean`,
never commit `CODE_REVIEW_STATUS.json` — the coordinator does, once per
wave, after a fresh `git pull --rebase` (stash `codebase_health_last.json`
+ the derived queue views separately — never FOUNDRY's to commit but still
block a rebase). Central/live-companion files get `model: opus`; workaday
tool files run fine at `sonnet`. Every `Agent` call needs an explicit
`model`. A C# fix is not real until rebuilt and deployed — this session
confirmed the game-up DLL-lock failure mode is common and expected; when
it happens, commit the source fix AND the rebuilt repo `Assemblies/*.dll`
copy (so the fix is buildable and provenance-complete even before it's
live), but do NOT `mark-clean` until an actual deploy to the Mods folder
succeeds.

⚠️ One correction from this session: a background subagent pushed its own
commit directly (`8a24dcd7`) instead of leaving it for the coordinator to
push once per wave, against the standing instruction given to it. No harm
resulted (no push race happened), but re-emphasize "do NOT push" more
firmly in future wave prompts, or accept that a subagent push is not
catastrophic and stop worrying about it.

## Next-session priority order

1. **Deploy the two pending fixes** (see above) at the next natural
   restart, then `mark-clean` both files.
2. **Keep broadening.** Active mods with meaningful DIRTY counts not yet
   touched this restart: Armoury (61, largest single pool — mostly
   already-reviewed per RESTART_5's notes, re-check with `check`),
   Utils (39, central tooling — read carefully, may deserve `opus` for
   anything touching deploy/rimflow internals), StructureInjections (2
   files left: RimplacePlan.cs, StructureInjectionsDebugActions.cs),
   Ninefold (0 dirty — fully clean already, skip), Doctrine
   (`mandrake.rut.doctrine`, 1 file: DoctrinePatches.cs — not yet
   reviewed), the rest of Property/Graffiti/Visibility (lists above).
   Same method: fast count via
   `python3 -c "import json; print(len(json.load(open('infrastructure/state/CODE_REVIEW_STATUS.json'))))"`,
   `code_review_status.py check <path>...` to confirm DIRTY/NO-ENTRY,
   `grep -io '<li>mandrake[^<]*</li>' "<ModsConfig.xml path>"` to confirm
   a mod is actually live before spending a review on it.
2b. Continue to SKIP bridgetools/rimflow/WeatherSuite per standing
   doctrine (WeatherSuite still unconfirmed active — recheck before ever
   touching it).
3. MapTools.cs 6th round (bridgetools, ~4 minor items from round 5),
   whenever bridgetools comes back up in rotation.
4. The `WreckedMachines` art-tool Python scripts and the
   `DesertVehicleReskin` art-build scripts are one-off human-run tools —
   confirm reachability (are they referenced by any doc/skill, or run
   only by hand?) before spending a review slot on them; not automatically
   DEAD-FILE candidates just because grep finds no importer.
5. Scale: 656 `.cs`/`.py` files under `src/`, 338 clean (~51.5%). Still
   explicitly multi-session per the owner — never claim it's finished.

## Non-review state at handoff

Bridge is FREE and game is UP (589-mod full list) — same as at the last
restart, no restart happened this session. No other FOUNDRY queue items
were open this session (checked `rimflow next --seat FOUNDRY` at start:
nothing offered beyond this continuity item).
