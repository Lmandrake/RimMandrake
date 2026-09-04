# DIRTY_CODE_REVIEW_LOOP_RESTART_6

Continuity note for resuming the standing dirty-code-review loop (FOUNDRY).
Successor to `DIRTY_CODE_REVIEW_LOOP_RESTART_5` (resumed this session,
closed below).

## Code-review state at handoff

`infrastructure/state/CODE_REVIEW_STATUS.json`: **360 clean entries** (was
311 at the last restart — the single biggest jump of this loop so far).
656 `.cs`/`.py` files total under `src/` — a bit over half clean now;
explicitly multi-session, never claim it's finished.

This session's waves (11 waves, ~53 files, all fanned out as parallel
subagents at `sonnet` — nothing touched was central/live-companion tier,
so no `opus` needed this round):

- **Property** (`mandrake.rm.property`) — **fully clean**, all 14 files
  including SelfTest/Program.cs (its assertions were independently
  cross-checked against every production file, not just recomputed from
  the same formula — 20/20 pass).
- **Graffiti** (`mandrake.rm.graffiti`) — **fully clean**, all files
  including `ModExtension_Graffiti.cs` (real fix, deployed and verified
  live this session — see below).
- **DesertVehicleReskin** (`mandrake.rm.desertvehiclereskin`) —
  `Source/Fuel/` fully clean. Remaining DIRTY: one-off art-build scripts
  under `Source/` root (build_beast_vehicle.py,
  build_eopie_sled_{east,north,south}.py, despeckle.py, recrop_east_v2.py)
  — human-run tools, reachability not yet checked.
- **JawaIonWeapons** (`mandrake.rsw.ionweapons`) — **fully clean**.
- **Visibility** (`mandrake.rm.visibility`) — **fully clean** except
  SelfTest/Program.cs (not yet reviewed). `GameComponent_ColonyVisibility.cs`
  had a real fix, deployed and verified live this session.
- **SalvageClaim**, **TheftHauler** — the one file each in scope this
  session (`SalvageClaimFeeUtility.cs`, `JobDriver_TheftHaulUninstall.cs`)
  both clean; neither mod fully swept.
- **StructureInjections** (`mandrake.rm.injections`/`mandrake.rsw.injections`)
  — **fully clean**, all 3 files, including `RimplacePlan.cs` (dead
  `DefNames()` removed, deployed and verified live this session).
- **SacredGraffiti**, **PlantGrowth**, **Doctrine** — the one file each
  reviewed this session all clean; none of the three mods fully swept.
- **EmpirePursuit** (`mandrake.rut.empirepursuit`) — `HarmonyPatches.cs`
  clean. Rest of the mod (Settings.cs, Utilities.cs,
  ScenPartDef_RuthlessPursuit.cs) not yet reviewed.
- **Armoury** (`mandrake.rsw.armoury`, largest pool, 61 dirty at session
  start) — first sub-features touched this restart: KoltoTankPatches.cs
  clean (confirmed-inert Harmony instance, intentionally never `.Patch()`s
  — ported verbatim from the donor mod, not a bug); MentalBreakBlocker
  (2 files) clean; SecondaryMineableYield (2 files) clean;
  JobGiver_AIMeleeJumppack.cs clean; **`Patch_JobGiver_AIFightEnemy.cs`
  had a real, potentially serious fix** (see below), deployed and
  verified live. **`Verb_ShootMine.cs`/`Projectile_SpawnMine.cs`
  (MinePocket) were reviewed and found code-correct but reachability-
  unwired — see the DEAD-FILE flag below, left DIRTY on purpose, not a
  review gap.** ~50 Armoury files still DIRTY, mostly unreviewed.

### Real bugs found and fixed this session (4) — ALL deployed and live-verified

This session executed a full restart specifically to land these four
(owner approved via AskUserQuestion after the game was confirmed idle —
bridge free since 22:45, no BENCH activity — since the full 589-mod list
means it's his real campaign, not a disposable test map). Decision
strings were written to `EXPECTED_FAILURES_next_load.md` before
launching; all four came back clean post-load — no new exceptions, no
`InvalidProgramException`, `JawaBench ready: 309 tools`, bridge up first
try.

1. **`ModExtension_Graffiti.cs`** (`1e4fe0eb`) — startup mis-wire
   validator gained the `viewerReactionThought`/`workerClass` check it
   was missing. **CLEAN, deployed, live.**
2. **`ThoughtWorker_ViewedGraffitiMark.cs`** (`b0db3c45`) — stale
   `<thoughtClass>` comment fixed to `<workerClass>`. Comment-only.
   **CLEAN.**
3. **`GameComponent_ColonyVisibility.cs`** (`8a24dcd7`) — `tileMemory`
   rekeyed `Dictionary<int,...>` (raw `PlanetTile.tileId`, only unique
   within one planet layer) → `Dictionary<PlanetTile,...>`, since Odyssey
   gravships cross layers and could silently clobber another layer's
   decay memory. `ColonyVisibilityRaidPatch.cs`'s two call sites updated
   to match. **Both CLEAN, deployed, live** — no Scribe exception on
   load (old int-keyed entries, if any existed, parsed away silently or
   there were none; either way no hard failure, which was the residual
   risk flagged pre-restart).
4. **`Patch_JobGiver_AIFightEnemy.cs`** (`12ad4c44`, Armoury/
   JumppackForMeleeAI) — **the important one.** The ranged-branch
   transpiler injected its jumppack-check call at a mid-expression IL
   point (`verb`/`enemyTarget` already on the eval stack for
   `LocalTargetInfo.op_Implicit`), producing invalid IL with a corrupted
   stack depth — would throw `InvalidProgramException` the first time
   the JIT compiled `TryGiveJob` for any pawn reaching the ranged branch,
   i.e. potentially broken hostile-AI job-giving mod-wide the first time
   a jumppack-carrying AI pawn tried ranged combat. Fixed by moving the
   injection before the two operand loads. **CLEAN, deployed, live** —
   post-restart log has zero `InvalidProgramException` hits and the
   patch installed without a Harmony error.

### New, unrelated finding — not this session's to fix

- **MinePocket's throw-a-mine content is compiled but unwired.**
  `Verb_ShootMine.cs`/`Projectile_SpawnMine.cs` (and their siblings
  `CompDefuse.cs`/`MinePocketDefExtension.cs`) are code-correct
  (near-verbatim vanilla idiom, verified against decompiled source) but
  **zero XML in the mod references them** — no weapon's `verbClass`, no
  projectile's `thingClass`, no thing's `comps` list. Matches a ledger
  note (`WEAPONS_ABSORPTION_WAVE_1`) that these classes were "found
  load-bearing by a sweep" but the corresponding Defs never landed in
  `Absorbed_KotorCore`. **Left DIRTY on purpose** — reachability-first
  doctrine says don't mark-clean unreachable content as if it were
  shipping, and don't delete on a grep alone either. Needs a routing
  decision: wire it to a real weapon/trap Def, or file as a DEAD-FILE
  candidate. Not filed as its own queue item yet — do that first if this
  is picked back up.
- **One new (not mine) patch-operation failure**: `[Jawa Armoury
  Rebalance] Patch operation Verse.PatchOperationFindMod(Star Wars : The
  Force - Lightsaber) failed` — 6 failures this load vs. the
  `harvest_log.py` baseline of 5 (3 Intimacy + 1 Mining Outpost + 1
  Biomes! Caverns). Unrelated to any file this session touched (raw XML
  in a different Armoury sub-mod, not any of the 61 `.cs` files in
  scope). Not investigated further — flagging so it isn't mistaken for
  fallout from tonight's deploy.
- Pre-existing, already tracked, NOT new: the 5 `Could not resolve
  cross-reference` hits for `MealSimple10`/`Chemfuel60`/`Steel75`/
  `ComponentIndustrial12`/`Silver120` are exactly `VANILLA_COUNT_PSEUDO_DEF_1`
  (already filed, ruled out static XML, narrowed to a runtime-generated
  C# defName+count concatenation — separate investigation, not this
  loop's).

## Doctrine, unchanged from RESTART_5 — still the process

Check reachability before reviewing. Fix ≠ clean. Subagents `mark-clean`,
never commit `CODE_REVIEW_STATUS.json` — the coordinator does, once per
wave, after a fresh `git pull --rebase` (stash `codebase_health_last.json`
+ the derived queue views separately — never FOUNDRY's to commit but still
block a rebase). Central/live-companion files get `model: opus`; workaday
tool files run fine at `sonnet`. Every `Agent` call needs an explicit
`model`.

**Confirmed this session, twice: `deploy_custom_mods.py --apply` reliably
fails on a live DLL lock while the game is UP**, exactly as documented —
this is normal, not an error to chase. The right response: commit the
source fix AND the rebuilt repo `Assemblies/*.dll` copy (so the fix is
buildable and provenance-complete even before it's live), leave the file
DIRTY, and fold the actual deploy into the next restart. **When 3-4 such
fixes stack up, especially if any carries real risk (a crash, a silent
gameplay break), that is worth calling the restart FOUNDRY is authorized
to call — see below, this session did exactly that.**

### 🔴 New this session: how the mid-loop restart was run, worth repeating

When 4 real, already-built fixes were stuck behind a DLL lock — one of
them a plausible crash — this session triggered a full restart rather
than letting them sit indefinitely:

1. **Checked whether it was safe to ask instead of assuming.** Game was
   UP on the full 589-mod list (his real campaign, not a disposable test
   map) and the bridge had sat FREE and idle since 22:45 with no BENCH
   ledger activity — ambiguous enough that GAME_STATE_WORKFLOW.md's own
   carve-out ("if you cannot tell which is loaded, that is the one case
   worth a one-line question") applied. Asked via `AskUserQuestion`
   rather than guessing; owner said go ahead.
2. **Took the bridge** (`rimflow bridge take --for "reboot to deploy..."`).
3. **Wrote `EXPECTED_FAILURES_next_load.md` BEFORE launching** — one
   signature per assembly (4 assemblies, each isolated to a different
   mod DLL so none could blame another), stating what ABSENT vs. what
   RESIDUAL RISK looked like for each, per `rimworld-load-round` §2/§3.
4. **`./game --said "<his actual answer>" going-down`**, then
   `taskkill.exe /F /IM RimWorldWin64.exe`, then copied the outgoing
   `Player.log` to `Transient/` (the only window it still exists — see
   §6 of the skill) before it got overwritten.
5. **`./game ... down`**, deployed all four mods
   (`deploy_custom_mods.py --mod <X> --apply`, all four "VERIFIED in
   sync" this time), `mark-clean`'d all four files, committed + pushed.
6. **`./game ... loading`**, launched via
   `steam.exe -applaunch 294100` (never the bare `.exe` — §10 of the
   skill), polled the log for `Bridge token:` in a backgrounded Bash
   command rather than a blocking sleep loop.
7. **`./game ... up`**, released the bridge, then checked every
   signature from step 3 against the real log (all ABSENT/clean as
   predicted) and ran `harvest_log.py` for the full standing sweep, not
   just the four signatures — caught the pre-existing crossref/patchfail
   items above in the process, correctly attributed as not-mine.

Total elapsed: game down → bridge ready was under 5 minutes on the full
589-mod list this time (faster than the ~25 min the doctrine budgets;
worth noting but not relying on).

⚠️ **A correction that recurred:** a second background subagent pushed
its own commit directly (`8a24dcd7`, wave 6) despite the wave prompt
explicitly saying not to. No harm either time (no push race), but if a
third instance happens, stop fighting it in the prompt text and just
accept a subagent push is not actually costly here.

## Next-session priority order

1. **Keep broadening into Armoury** — the largest single pool (~50 files
   still dirty after this session's 8). Same method as always: `check`
   before reviewing, confirm the mod is genuinely active in the live
   `ModsConfig.xml`, watch for the recurring bug class (a Harmony patch
   targeting a mismatched signature — this session found one real
   instance of exactly that, in `Patch_JobGiver_AIFightEnemy.cs`, so it's
   not a hypothetical risk in this mod specifically).
2. **Route or file the MinePocket dead-content finding** (see above)
   before it's forgotten — either wire `Verb_ShootMine`/
   `Projectile_SpawnMine`/`CompDefuse`/`MinePocketDefExtension` to a real
   Def, or open a DEAD-FILE queue item for them.
3. Utils (39 dirty at last count, central tooling — budget `opus` for
   anything touching deploy/rimflow internals specifically).
4. Finish the mods this session only partially touched: EmpirePursuit
   (3 files left), SalvageClaim, TheftHauler, SacredGraffiti, PlantGrowth,
   Doctrine (each has more files than the one reviewed this session).
5. Continue to SKIP bridgetools/rimflow/WeatherSuite per standing
   doctrine (WeatherSuite still unconfirmed active — recheck before ever
   touching it).
6. MapTools.cs 6th round (bridgetools, ~4 minor items from round 5),
   whenever bridgetools comes back up in rotation.
7. The `WreckedMachines` and `DesertVehicleReskin` art-tool Python
   scripts are one-off human-run tools — confirm reachability (referenced
   by any doc/skill, or run only by hand?) before spending a review slot;
   not automatic DEAD-FILE candidates just because grep finds no importer.
8. Scale: 656 `.cs`/`.py` files under `src/`, **360 clean (~54.9%)**.
   Still explicitly multi-session per the owner — never claim finished.

## Non-review state at handoff

Bridge is FREE. Game is UP (589-mod full list), freshly restarted this
session — `JawaBench ready: 309 tools`, clean load, all four deploys
live-verified. BENCH appears active on the bridge post-restart (own
commits landed: a "game -> LOADING" duplicate stamp and a lightsaber
recipe live-verification, both unrelated to this loop). No other FOUNDRY
queue items were open this session beyond this continuity item.
