# DIRTY_CODE_REVIEW_LOOP_RESTART_16

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor
to `DIRTY_CODE_REVIEW_LOOP_RESTART_15` — read that file (and its own chain)
for fuller history.

## Two tracking schemes, still both live — but the game shut down mid-wave

`DIRTY_CODE_REVIEW_STANDING_LOOP_1` (filed 2026-09-03, still `doing`) is the
other identity working this same backlog. It ran a very large number of
waves through the night of 2026-09-17/18 (waves 29-43 plus named Armoury/
RotSporeKit/FlowWorks waves — see its own `rimflow show` history for detail,
it is long). This wave started **right after** `d946c8522` — "FOUNDRY reboot
handoff 202609181353: big wave, cut short by owner shutdown" — i.e. right
after the *previous* FOUNDRY window handed off and the owner shut the game
down. No other window appeared to be actively committing during this wave
(checked `git log -10` at the start: nothing newer than that handoff), so
collision risk this time was lower than RESTART_15's account of a genuinely
concurrent night. Still, most of the backlog sits inside mods with an
actively-`doing` build item (FlowWorks, SWBestiary/Mlie, ShipShields,
RimProperty, Droidworks, Ninefold, the biome-kit build items, etc.) — those
are mid-construction, not idle, and were skipped on that basis, not because
of live collision.

## Where things stand

`code_review_status.py list`, freshly re-run at the end of this wave:
**2862 clean / 79 dirty / 2 orphaned** (was 2855/86/2 at this wave's start —
re-run `list` fresh, don't trust either number, it moves fast).

## What this wave did

Reviewed 7 files full-file (all were either genuinely idle or had their only
recent touch be this review loop's own prior work), fixed 0 bugs (all
already correct), marked all 7 clean:

1. `src/DEPLOY_HOLD.txt` — re-reviewed after RESTART_15 left it dirty (its
   own fix was landed, file not re-marked). Current dirty state is a NEW,
   well-formed append (`FISH_BESTIARY_BUILD_1` wave 5's Twilight Deep hold,
   `UtinniPatches/Patches/BiomeFishTypes_TwilightDeep.xml`) — matches the
   file's own documented format, reason is present and dated, glob is
   correct. No bug.
2. `src/RimStarWars/IriazArtOverride/About/About.xml` — `IRIAZ_ART_REGEN_1`
   closed at `039622eff` (~7.5h before this wave), so its final state is
   settled. `loadAfter` names both real collision targets
   (`Mlie.StarWarsAnimalCollection`, `mandrake.rsw.swbestiary`); both
   packageIds confirmed present+active against
   `ModsConfig.FULL.LATEST.xml`. No bug.
3. `src/RimStarWars/Armoury/Source/gen_kotorweapons_absorption.py` — the
   file the Armoury wave (`0fc737f9d`) itself edited (stale
   BLOCKED_manifest header fix) but did not mark clean, since fixing a
   finding doesn't clean a file. Re-read whole file: the comp-porting/MW2
   blocklist correction is internally consistent with its own docstring,
   `absorption_content_fixes.py` import target exists. No bug found this
   pass.
4. `src/RimMandrake/Utils/handoff.py` — full read of all ~735 lines
   (seat resolution, gate logic, todo_scan, harvest/cull, build). No bug.
   Cross-verified against its own selftest (next item) — 0 failures.
5. `src/RimMandrake/Utils/selftest_handoff.py` — ran it: **0 failures**,
   24/24 checks pass.
6. `src/RimMandrake/Utils/selftest_code_review_status.py` — ran it: **0
   failures**, all 12 documented behaviours (hash round-trip, binary
   content, migrate-hashes, prune, find_untracked, git() timeout
   degradation, hook-log-path agreement) still hold.
7. `src/RimMandrake/Utils/run_selftests.py` — full read (discovery glob,
   parallel pool, isolated-sequential carve-out for `selftest_render.py`,
   UNMEASURED-vs-FAIL distinction, dropped-result detection). No bug.

`run_selftests.py` itself was run as part of this wave's own close-out
(the full suite, not just the two selftests above) — see the commit for
the pass/fail count, it ran long enough to background.

## Skipped this wave, and why

- **All of `src/RimMandrake/FlowWorks/`** (~30 dirty files) —
  `FLOWWORKS_BUILD_PROGRAM_1` is `doing`, actively mid-construction
  (bottle loop / liquid registry sub-items `LIQUID_BOTTLE_LOOP_1` and
  `LIQUID_REGISTRY_CORE_1` also both `doing`). The prior FlowWorks wave's
  own clean marks (`6bc642cb9`, noted in the standing-loop ledger) no
  longer match current content — real ongoing edits, not review-loop churn.
- **SWBestiary Mlie files** (`RSW_MlieWaveC_*`, `RSW_Anooba`, `RSW_Boma`,
  `RSW_Convor`, `RSW_Bantha_Thoughts.xml`) — `MLIE_FAUNA_ABSORPTION_1` is
  `doing`; the outgoing handoff itself says "MLIE at Pass 19 (29/90
  remaining), Pass 20 interrupted mid-flight by the shutdown" — genuinely
  live, unfinished work.
- **`src/RimUtinni/ShipShields/*`** — `SHIELD_MODS_LEVERAGE_1` `doing`,
  touched 06:14 (same morning, before this wave).
- **`src/RimMandrake/RimProperty/*`** (`PropertySettings.cs`,
  `PropertyTuning.cs`, `RM_Property.csproj`) — last touched by
  `SETTLEMENT_VERBS_WAVE_1` (`doing`) 9.5h before this wave; that item's
  own commit message describes an in-progress verb family, not settled.
- **`src/RimMandrake/Utils/expectations_manifest.py`,
  `run_expectations.py`, `selftest_expectations_manifest.py`,
  `modset_builder.py`** — all last touched by `MASS_VALIDATION_LADDER_1`
  or `FISH_BESTIARY_BUILD_1`, both `doing`, ~9-10h before this wave.
- **`src/RimMandrake/Ninefold/Source/*`** (`FirstContactCorpus.cs`,
  `GameComponent_Ninefold.cs`, `Patch_KillManner.cs`) —
  `NINEFOLD_ENGINE_M0_1`/`NINEFOLD_MISSING_EVENT_HOOKS_1` both `doing`,
  last commit ("ground and wire Ishko/Oomo's first-contact hooks") ~8.5h
  before this wave.
- **`src/RimMandrake/Utils/gm_blackboard_shadow.py`** —
  `CATHEDRAL_EXPOSURE_COMPLETION_1` / `GM_BLACKBOARD_SHADOW_M4_1`, both
  `doing`.
- **`src/RimMandrake/Utils/structure_roster_lint.py`,
  `src/RimMandrake/StructureInjections/About/About.xml`** —
  `TILE_STRUCTURE_DESIGNS_1` `doing`, last touched ~14.5h before this
  wave ("promise batch 1 — 3 of 6 promise gaps closed").
- **`src/RimStarWars/Droidworks/Defs/PawnKinds_*.xml`,
  `gen_droidworks_defs.py`** — `DROIDWORKS_PRIMITIVE_TIER_1`/
  `DROIDWORKS_FORMAT_TIERS_1`/`DROIDWORKS_WIPE_SEVERITY_1` all `doing`,
  several with commits inside the last few hours (`8d4f6fe39`,
  `6ded2767f`, `d24a4fdd9`).
- **`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/*`** (CrackedLands,
  Greentide, TheRot, TheScald, Wasteland, WeepingStones),
  **`BiomeCast_Ashkarr.xml`**, **`SandFishing_CrackedLands.xml`** — each
  ties to an actively-`doing` biome-kit build item (Greentide/Scald/etc).
  `BiomeCast_Ashkarr.xml` in particular is the RESTART_15-flagged
  generated-file regression — still open, still needs whoever owns
  `gen_cast_patch.py`/the FOUNDRY window running the kit builds.
- **`src/RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/RUT_PaleTree.xml`** —
  dirty since a mark just hours after the RotSporeKit wave closed; likely
  a genuine post-review edit, not investigated this pass.
- **`src/RimMandrake/rimflow/model.py`** (1455 lines) — no active named
  gate found and its last touch (`b32878458`, "emergency repair path for
  a torn ledger line") is ~23h old, so it's a legitimate next-wave
  candidate, but it's core ledger machinery and long enough that this
  wave's budget didn't stretch to it. Good pick for RESTART_17.

## Recommended next steps, in order

1. Re-run `code_review_status.py list` fresh — do not trust the 2862/79
   figure above past this session.
2. `rimflow show DIRTY_CODE_REVIEW_STANDING_LOOP_1` before picking
   anything in FlowWorks, SWBestiary, ShipShields, RimProperty, Ninefold,
   Droidworks, or any `UtinniPatches/Defs/BiomeDefs/*` — all tied to
   `doing` build items as of this wave; check whether they've gone
   `close`d/`block`ed since.
3. `src/RimMandrake/rimflow/model.py` — good next candidate: large but
   no live gate found this pass.
4. `src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_ThoughtDef.xml` —
   RESTART_15's un-landed 6-line Rakatan fix + the `LovinAsexual*`
   content-loss bug are still open (not re-checked this wave — not on
   the dirty list I reviewed in detail, carry the same caveat RESTART_15
   gave: confirm nothing is concurrently regenerating this file before
   touching it).
5. `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Weapons/
   Absorbed_KotorWeapons_WeaponRanged_KotORIonPistol.xml` — still dirty,
   still needs a design call on the dead `KotORElectricBolt` projectile
   reference (RESTART_15 item 5, unchanged).
6. `src/RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/RUT_PaleTree.xml` —
   worth a quick look; wasn't investigated this wave.
