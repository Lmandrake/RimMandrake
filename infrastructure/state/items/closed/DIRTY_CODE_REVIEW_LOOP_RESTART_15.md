# DIRTY_CODE_REVIEW_LOOP_RESTART_15

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor
to `DIRTY_CODE_REVIEW_LOOP_RESTART_14` — read that file (and its own chain)
for fuller history.

## 🔴 Two tracking schemes are BOTH live right now — read before picking

This RESTART_N chain is not the only thing working this backlog tonight.
`DIRTY_CODE_REVIEW_STANDING_LOOP_1` (filed 2026-09-03, still `doing`) is a
SEPARATE FOUNDRY identity running large parallel-subagent waves against the
same `CODE_REVIEW_STATUS.json` this same session — `rimflow show
DIRTY_CODE_REVIEW_STANDING_LOOP_1` shows an Armoury wave (59 files, 2 real
bugs), a RotSporeKit wave (13 files, 4 real bugs), and a FlowWorks wave (71
files, 5 real bugs), all landing in the ~2 hours before this wave ran. Both
schemes write to the same status file and the same shared worktree. Whoever
picks up next: check BOTH `rimflow show DIRTY_CODE_REVIEW_STANDING_LOOP_1`
and this RESTART chain before assuming a file's dirty/clean state is stable
— it decays inside minutes right now, not just across sessions.

## Where things stand

`code_review_status.py list`, freshly re-run at the end of this wave:
**2907 clean / 35 dirty** (was 2901/41 — later re-verified 2903 in the
prior note — at this wave's start; numbers move fast, re-run `list` fresh
rather than trusting either figure).

## What this wave did

1. Re-verified both gates named by RESTART_14: `LIQUID_BOTTLE_LOOP_1` and
   `MLIE_FAUNA_ABSORPTION_1` are BOTH still `doing` (rimflow show, fresh) —
   skipped all of FlowWorks/LiquidTypes and all of SWBestiary +
   `BiomeCast_Ashkarr.xml`, per the standing brief. Also newly checked and
   skipped, all confirmed actively `doing`/mid-churn THIS session:
   `CATHEDRAL_EXPOSURE_COMPLETION_1` (gm_blackboard_shadow.py, last touched
   ~1h before this wave), `TILE_STRUCTURE_DESIGNS_1` (structure_roster_lint.py,
   incremental whisper-batch item, same shape as SWBestiary), EnvironmentalHazards
   (heavy same-night Rot-wave churn, no gating item but high collision risk),
   `FLOWWORKS_BUILD_PROGRAM_1` (MovingDunes.csproj), `RUT_TheRot.xml` (Rot
   wave active), and `selftest_code_review_status.py`/`model.py`/
   `handoff.py`/`selftest_handoff.py` (handoff.py+selftest_handoff.py were
   committed by BENCH literally ~1 minute before this wave started reading
   status — too fresh to touch; `selftest_code_review_status.py` was hit by
   `DIRTY_CODE_REVIEW_STANDING_LOOP_1`'s own C7 wave hours earlier).
2. Marked **6 files CLEAN** after full-file review, no bugs found:
   `design/Jawa/worldbuilding/biomes/rosters/_consolidate.py`,
   `skills/generating-images/scripts/codex_image.py`,
   `src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_Xenotype.xml` (2913
   lines — read manually in two passes, then verified with a one-off
   structural script checking every one of 84 xenotypes' label+description
   PatchOperationConditional/match/nomatch triplets for internal consistency;
   0 issues), `src/RimUtinni/RustCathedralHum/Defs/RM_BiomeAttitudeDefs/
   RUT_RustCathedralAttitude.xml`, `src/RimUtinni/PyrelandsMechanics/About/
   About.xml`, `src/RimMandrake/CreatureBehaviors/Source/
   RM_CreatureBehaviorsMod.cs` (cross-checked all 14 settings fields have a
   real `.cs` consumer — no dead sliders).
3. **Found and fixed a real bug in `src/DEPLOY_HOLD.txt`**: the 2026-09-17
   entry holding `Absorbed_OPTurret.xml` (added by
   `DIRTY_CODE_REVIEW_STANDING_LOOP_1`'s own Armoury wave, mechanically off
   the file's own header comment) claimed donor `rpgwanderer.opturret` was
   "still active". MEASURED against the LIVE `ModsConfig.xml` (634 mods,
   read directly from `/mnt/c/Users/Mandrake/AppData/LocalLow/...`) and the
   repo's `ModsConfig.FULL.LATEST.xml` (635 mods): the donor is absent from
   both, and has been since 2026-08-31/09-01
   (`WEAPONS_DONOR_RETIREMENT_1.md`) — the ORIGINAL hold on this same file
   was already lifted once for exactly that reason. A stale-claim bug
   inside the review loop itself, not a real state change. Rewrote the
   entry as a "HOLD WAS STALE, LIFTED" record in the file's own established
   style. Left `DEPLOY_HOLD.txt` itself DIRTY (a fix, not a clean pass —
   the rest of the file wasn't re-reviewed this wave).
4. **Found, attempted to fix, could NOT land — `src/RimUtinni/PawnFlavor/
   Patches/PawnFlavorPhase2_ThoughtDef.xml`** (7.3 MB, 143,798 lines — too
   large for the Read tool's 256KB cap; reviewed via full XML-tree
   structural verification script instead of a manual read, plus manual
   spot-reads of several sections). Two real findings:
   - **6 stale pre-ruling lines**: `ABF_Thought_Synstruct_
     ArchotechImplantDissonance` stages 1–6 each have three redundant
     branches (stage-exists / stage-missing-but-def-exists /
     def-missing-entirely) that are supposed to carry identical text; the
     "Archotech is Rakatan" ruling (commit `6bc96eaf7`) fixed two of the
     three branches per stage but missed the middle one, which still reads
     "an archotech piece grafted into me" (the pre-ruling, explicitly
     rejected "vanilla AI-god" phrasing) instead of "a piece of Rakatan
     work grafted into me".
   - **7 duplicate `(defName, stage)` PatchOperationConditional blocks**
     inside single `PatchOperationFindMod` sequences (not cross-mod, so not
     load-order-legitimate): `HAR_AlienVsXenophobia` stages 1+2,
     `HAR_XenophobeVsXenophile` stage 1, `HAR_XenophobiaVsAlien` stages
     1+2 — all 5 byte-identical, harmless but wasteful (likely a generator
     dedup bug on its source rows) — **and** `LovinAsexualNegative` /
     `LovinAsexualPositive` stage 1, where the two duplicate blocks carry
     **different** label/description text each. Since
     `PatchOperationSequence` runs in order, the SECOND block silently wins
     and one of two authored flavor lines is permanently discarded with no
     error — a real content-loss bug, but picking which of the two survives
     is a content call I'm not making blind; needs whoever owns this file's
     generator (not found under `src/RimUtinni/PawnFlavor/` — only
     `validation.py` lives there; `git log --follow` shows the file is
     machine-generated, e.g. commit `1f144a387` "regen behind two generator
     fixes") to look at the source rows.
   - I edited the 6 stale lines directly (matching the file's own
     established precedent of hand-editing this generated XML for
     isolated lore fixes, e.g. `6bc96eaf7` itself) **twice**, and **both
     times the edit was silently gone within a few minutes** — `git diff`
     showed zero difference from HEAD, matching this session's
     `drvfs-stale-reads-mimic-revert` pattern OR (more likely, given a
     concurrent `git pull --rebase --autostash` was caught mid-flight via
     `ps aux` during this same wave, see below) a live concurrent process
     rewriting this exact file. **Left dirty, fix NOT applied** — do not
     assume the 6-line fix above is still needed without re-checking
     first; do not re-attempt a hand-edit here without first confirming
     nothing is concurrently regenerating this file.
5. **Git incident, same wave**: `git commit` hit a stale `.git/index.lock`
   (no live git process holding it per `ps aux` — removed it, per the
   documented git recovery step). The immediate retry then hit `git pull
   --rebase --autostash` racing a **different, genuinely live** concurrent
   `git pull --rebase --autostash` (confirmed via `ps aux` mid-race) and
   left `HEAD` **detached** with no `.git/rebase-merge` directory (the
   rebase died at initial checkout, before applying anything). Recovered
   cleanly, no data lost: confirmed the commit was already safely on `main`
   locally, `git checkout main`, `git rebase origin/main` (clean, 3
   commits, no conflicts), pushed at `2398d6a13`. A new `autostash` entry
   appeared in the stash list from the failed pull attempt — inspected
   (`git stash show`), contains only pre-existing Transient dashboard-regen
   drift (same noise already sitting in the working tree at session start),
   left untouched per RESTART_14's own precedent of never popping a stash
   that might be another agent's in-progress work.

`run_selftests.py` not re-run this wave — no code/logic files were
successfully changed (the one landed fix, `DEPLOY_HOLD.txt`, is a data/doc
file; the ThoughtDef.xml code fix never stuck, see above).

## Recommended next steps, in order

1. Re-run `code_review_status.py list` fresh — this backlog is being worked
   by at least two independent tracks tonight (this chain +
   `DIRTY_CODE_REVIEW_STANDING_LOOP_1`) and numbers are stale within
   minutes.
2. `rimflow show DIRTY_CODE_REVIEW_STANDING_LOOP_1` before picking anything
   in Armoury, RotSporeKit, FlowWorks, or Droidworks — that identity is
   actively waving through those trees and has already left `~1522` files
   in Armoury explicitly flagged "confirm scope before continuing" (binary
   assets, Language .txt, `_artsrc` scratch — likely out of this loop's
   scope entirely, worth a scope ruling rather than more silent skipping).
3. `src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_ThoughtDef.xml` — the
   6-line Rakatan fix and the `LovinAsexual*` content-loss bug (see above)
   are real and still open. Confirm nothing is concurrently regenerating
   this file (check `git log` for a very recent commit touching it, and/or
   diff before and after a short wait) before re-attempting either fix.
4. Re-check whether `CATHEDRAL_EXPOSURE_COMPLETION_1`, `TILE_STRUCTURE_DESIGNS_1`,
   and `FLOWWORKS_BUILD_PROGRAM_1` have gone quiet — if so their files
   (`gm_blackboard_shadow.py`, `structure_roster_lint.py`,
   `RimMandrake_MovingDunes.csproj`) are fair game.
5. `src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Weapons/
   Absorbed_KotorWeapons_WeaponRanged_KotORIonPistol.xml` — already known
   dirty with a real, previously-flagged issue (`defaultProjectile` points
   at a dead `KotORElectricBolt` ref from an excluded dependency); needs a
   design call (author a real ProjectileDef, or pick a substitute), not a
   review-only fix — leave dirty until that's ruled.
6. `src/RimStarWars/SWBestiary/Defs/ThoughtDefs/RSW_Bantha_Thoughts.xml` and
   the other 4 standalone SWBestiary def files NOT gated by
   `MLIE_FAUNA_ABSORPTION_1`'s own worklist (check per-file via `rimflow
   show`/git log which item last touched each — some may be older content
   the active port wave hasn't touched and are safe).
