# Notes (newest first)

## 2026-11-11 20:10 -08:00 — picked by CLAUDE_ARCHMAGI_OFFLINE3 (setup)
- Runs so far: 0. No past failures to classify.
- History: filed 2026-09-13 by BENCH (caused by CATHEDRAL_PLAYER_CONCEALMENT_ARC_1); FOUNDRY blocked it
  2026-09-17 on item 1 (CATHEDRAL_REGARD_BLACKBOARD_1) and item 3 (CATHEDRAL_STAGE_COMMENTARY_POOLS_1).
  Both are now `built` (needs=bridge): the blackboard 5be1588179 (+ review fix 7a6e6245bc), the linter
  7b150aa8f2. Unblocked 2026-11-05. The block is gone.
- Where the state lives: Regard, stage (WARY/TOLERATED/VOUCHED, REVEALED = 3 only via the reveal),
  exposure pressure, go-dark flips and Imperial Heat are all in the OUT-OF-GAME shadow blackboard
  `src/RimMandrake/Utils/gm_blackboard_shadow.py` (`ShadowBlackboard.poll`, `compute_conduct_posture`,
  `HEAT_HIGH_BAND=40`, `HEAT_LOW_BAND=10`). Missions already feed Regard there as the story flag
  `assailant_mission_completions` (`--story-flags-file`), and gate VOUCHED via
  `CATHEDRAL_STAGE_VOUCHED_MISSIONS_REQUIRED`. Heat is never scrubbed there by a mission: confirm.
- Surface (spec §239): CQF quest/event or bridge-injected letters, kyber spec §7 caveat. Lightest real
  surface consistent with shadow mode: the blackboard decides the offer set each poll and records
  `would_fire` offer entries; the text ships as defs (RulePack / letter text) in
  `src/RimMandrake/RustCathedral/Defs/`, RUT_ tier names `RUT_CathedralAssailantMission_*`.
  Search first: `KYBER_TRADE_PLOT_1` / `compute_hutt_extraction_offer` is the sibling pattern for an
  offer computed in the shadow.
- Linter: `cathedral_arc_lint.py --xml <file> --stage N` / `--text`; `--selftest`.
- Existing selftests to copy from: `src/RimMandrake/RustCathedral/selftest_rustcathedral_commentary.py`.
- Live step (≥1 mission + gate live on a quicktest) is NOT this lane: finish offline, note it, set
  needs=bridge, give back to BENCH.
- Code-review rule: every touched file must reach CLEAN (`code_review_status.py check`).
