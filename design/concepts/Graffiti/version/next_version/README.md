# Graffiti: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*Empty at entry on 2026-11-15: no open judge gap sorted as next version.*

## Re-judge coverage under a calibrated brief when the next version opens

- **What:** this mod's coverage signature was made before the coverage brief read CALIBRATED (`coverage_judge.unproven_signatures` flags it; flagged, never voided). When its next Design Version opens, its coverage is judged again by a coverage brief that reads CALIBRATED at that time.
- **Who, when, why not now:** owner, by question card 2026-11-16 11:36 PM PST (point 19), picked "Leave them, re-judge at next version": "two of the three are already in live in-game visits, which find real failures better than a paper re-read. Buys: no spend or delay now; each gets a tested judge when its next Design Version opens." Filed by RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD.
- **Acceptance test:** `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` reads `coverage_judge` CALIBRATED, and `python3 -c "import sys; sys.path.insert(0, 'src/RimMandrake/rimflow'); import coverage_judge as C; print([u['concept'] for u in C.unproven_signatures('.')])"` no longer lists `design/concepts/Graffiti`.

## Caller scenario tests from the mined live bugs: gr_edgeon_migrate, gr_disabled_paints, gr_weak_hands_paint, gr_double_please

- **What:** four offline scenario tests of Graffiti callers on real game types. Trial 1's ThoughtWorker harness (`design/RimMandrake/2026-11-07-pocock-design/trial1_scenario/`) and `pilot_realtypes/` show the pattern. Trial 1 planted 11 faults in Graffiti callers and the offline tests caught none (`design/RimMandrake/2026-11-07-pocock-design/04-trial1-callers.md`).
  - `gr_edgeon_migrate` (`GraffitiSocial`, `Filth_Mark`, `WallPlane`): a save with seven edge-on pictures loads with no picture left on an edge-on face. This bug took four fixes in one evening.
  - `gr_disabled_paints` (`GraffitiTemperament`, `JoyGiver_PaintGraffiti`, `JobGiver_IdleTag`): an Artistic-disabled colonist never starts a paint job.
  - `gr_weak_hands_paint` (same callers): over three days, a level-15 artist paints more marks than a level-2 hand.
  - `gr_double_please` (`GraffitiSocial`, `ThoughtWorker_ViewedGraffitiMark`): a colonist who sees their faith's sign gets one mood line for it, not two.
- Graffiti is on the owner's hold. This entry is design text only. Nothing runs until the hold is lifted.
- **Who, when, why not now:** the owner adopted the scenario policy by card 2026-11-08 ("Policy plus real-types pilot"; item `RIMMASTER_WEIGH_POCOCK_SKILLS_TRIAL_BEFORE_INSTALL`, `design/RimMandrake/2026-11-07-pocock-design/06-mined-live-bugs.md` §Seed set). The seed is a live-found caller bug: its fix is on the build, and no offline test reads the caller. It moves no bar of the current version. It adds a cheaper regression check beside the live scene that decides the bar today. The Conductor decides at filing whether it stays here (recommended: next version).
- **Acceptance test:** each scenario runs offline from the mod's tests. `maturation.py red-seen Graffiti <test id>` records each one red on a planted fault that reverts its fix's caller line, and green on the build.
