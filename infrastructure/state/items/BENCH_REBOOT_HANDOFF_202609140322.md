# BENCH reboot handoff — 2026-09-14 03:22 UTC

Session with the owner at the bench, 2026-09-13 → 14. Everything below is
committed and pushed unless it says otherwise. FOUNDRY was working live
throughout (holds/held the bridge for ARMOURY_MW2_CUT_1).

## Finished this session (committed + pushed)

1. **git-efficiency skill — NEW machine-wide skill, its own repo.**
   `/mnt/d/Luke/dev/git_efficiency` → private GitHub `github.com/Lmandrake/git_efficiency`.
   Distilled from a git-usage audit of this repo; **evaluated** (with/without-skill
   on 3 tasks — cleared: wins on the rename + audit tasks, neutral where the model
   already batches) and **activated** (symlinked into `~/.claude/skills/git-efficiency`,
   live in all sessions now). Three Rimworld repair tickets filed for FOUNDRY:
   `SELFTEST_GIT_FIXTURE_TEMPLATE_1`, `MIGRATE_NAMES_BATCH_MV_1`,
   `CODE_REVIEW_STATUS_MIGRATE_BATCH_1`.

2. **Bacta Tank core mod — builds clean, NOT deployed.** `src/RimStarWars/Bacta`
   (`mandrake.rsw.bacta`). Owner-specced at the bench: 1.6 growth-vat chassis
   (visible suspended pawn, zero Harmony), **healing-not-regeneration** (brain
   excluded via ConsciousnessSource, missing parts never restored), trade-scarce
   bacta fluid, full Mod Settings. DLL compiles 0/0. **Placeholder art**;
   **untested** — needs a minimal-list quicktest, and it is deliberately NOT in
   the full modlist. Items: `BACTA_TANK_CORE_1` (built) + `BACTA_PAWNINTANK_RECON_1`,
   `BACTA_REVIVAL_MECHANIC_1`, `BACTA_TANK_ART_1`, `BACTA_SIDE_ITEMS_1`.

3. **ModularWeapons2 — owner ruled CUT.** Skeptical review (Fable) proved MW2's
   modularity on our KotOR gear is unreachable (0 GunsmithPresetDefs) and
   invisible (all parts NullTex). Owner: remove the 2 gadgets, cut thoroughly,
   restore SMYH. Filed `ARMOURY_MW2_CUT_1` for FOUNDRY with a BENCH
   completeness audit adding 3 gaps (the 4 wrist/droid upgrade darts, save
   migration via savemap.py not grep, a stray MVCF root-tag def). Gate-only
   `ARMOURY_MW2_DEP_UNGATED_1` superseded. Review: `Transient/mw2_disentanglement_review_2026-09-13.md`.

4. **SMYH × MW2 pawn-gen crash — root-caused.** SMYH's DLL rebuilt 2026-09-13;
   MW2's Aug-9 transpiler of DrawHandsOnWeapon now emits invalid IL → every
   weapon-holding pawn crashes map generation. **SMYH disabled in ModsConfig**
   as the interim fix (backup: `Transient/ModsConfig.backup.20260913_183819.xml`).
   The real fix is the MW2 cut; SMYH restore is folded in as its LAST step.

5. **Pyrelands fauna wiring — deployed.** `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`
   wires the ruled 15-animal roster into RM_FE_Pyrelands (validated 0 errors,
   deployed to Mods). Needs next-load verification. Roster derived + recorded on
   `PYRELANDS_CREATURE_RERENDER_1`.

6. **Pyrelands art regen — re-filed reference-less.** First attempt used the
   donor sprites as `reference`, which forced reskin-validate and **rejected all
   21** (my briefing error — a restyle can't validate against the old silhouette).
   Re-filed reference-less (legibility-gated); ~18/21 done at handoff, daemon
   finishing the rest. Lesson saved to memory (`artpipe-reference-triggers-reskin-validate`).

7. **Capture Expansion vs pits — analyzed.** It's ferny's above-ground restraint
   furniture (not active), zero pits, no license. We already ship `mandrake.rm.pits`.
   Recommendation: ignore it, finish our own art pass (`PIT_TRAP_VISUAL_REDESIGN_1`).

8. **Plot sitting review artifact — PUBLISHED.** The owner's read-ahead for the
   campaign-story pass: https://claude.ai/code/artifact/5b7132a8-c982-4328-9d42-e4df619caf0b
   (built from `design/Jawa/campaign/CAMPAIGN_ARC_GATHER.md`).

## Half-done / where it stops

- **Pyrelands art:** last few facings rendering in the artpipe daemon. Owed: a
  **contact-sheet LOOK** before any deploy — the batch is NOT eyeballed yet.
- **Pyrelands live verification** (roster in-world, mechanics, world-tile switch)
  waits for the bridge to free — FOUNDRY held it for the MW2 cut.
- **The plot sitting itself (Phase B)** is the owner's next interactive session;
  the artifact is the read-ahead. Phase B must NOT fork a fourth canon layer (G84).
- **PyrelandsMechanics** is not in ModsConfig — mechanics won't run until enabled
  (do NOT touch ModsConfig while FOUNDRY is mid-cut).

## Look at first

1. The **plot sitting artifact** (link above) — the owner asked for it to review.
2. **FOUNDRY's MW2 cut** status — was at step 8 (cold-load verify) at handoff.

## Traps for whoever resumes

- **SMYH is disabled in ModsConfig.** Its restore is the LAST step of the MW2 cut
  (safe only once MW2's transpiler is gone). Do NOT restore it before MW2 is
  removed, or the pawn-gen crash returns.
- **Do NOT commit FOUNDRY's in-flight `src/` edits** (EnvironmentalHazards.dll,
  atomic_copy.py, modcheck/runner.py, modcheck/selftest.py) — not BENCH's.
- **git-efficiency skill is now active machine-wide** — affects every session.
- The artpipe daemon is finishing Pyrelands jobs; don't double-start it.
- Game state was GOING_DOWN at handoff (owner broadcast); bridge FREE.

Nothing of BENCH's is mid-edit or unpushed. git_efficiency and Rimworld repos
both in sync with origin.
