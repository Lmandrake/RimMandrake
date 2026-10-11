# 13 — live-debugging-proof-harness skill: progress

Started 2026-10-11.

## Milestones
- [x] sources read (debug_process, live validation log 2026-10-11, validation_core, proof_all, lessons clusters D+F+G)
- [x] skill written: skills/live-debugging-proof-harness/ (SKILL.md 237 L + 6 references)
- [x] symlink .claude/skills/live-debugging-proof-harness + README roster row + CHECK domain row
- [x] rimworld-debug-testing: §4b/§7/§9 now pointers; references/long-proofs.md folded in and removed; POLICY.md cite -> CHARTER.md; description redirects proof work
- [x] published 8484b46ee
- [x] absorbed lessons deleted (33, below)

## Absorbed lessons (deleted)
- 20260916T114419Z-UNSEATED-modcheck-checklist-section-s-cannot-show.md
- 20260917T051009Z-UNSEATED-north-star-walk-whose-lines-are.md
- 20260917T133121Z-BENCH-north-star-bar-about-change-was.md
- 20260917T133121Z-BENCH-walk-file-filed-under-mod-s.md
- 20260924T183825Z-FOUNDRY-right-after-fresh-rimworld-launch-player.md
- 20260925T150224Z-BENCH-player-log-watcher-started-right-after.md
- 20260925T230954Z-FOUNDRY-jawa-world-tile-map-generate-d.md
- 20260930T133957Z-FOUNDRY-regenerate-current-map-wipes-colonists-generated.md
- 20261002T001825Z-FOUNDRY-modcheck-everyone-dead-floods-were-session.md
- 20261003T200004Z-FOUNDRY-bland-world-setup-full-mod-list.md
- 20261003T223850Z-FOUNDRY-belt-hang-classes.md
- 20261003T224033Z-FOUNDRY-modcheck-run-that-starts-with-another.md
- 20261004T001940Z-FOUNDRY-verse-log-stops-writing-after-1000.md
- 20261004T220351Z-FOUNDRY-launch-wait-sh-gives-up-after.md
- 20261004T220351Z-FOUNDRY-never-hand-edit-result-json-flip.md
- 20261005T155316Z-FOUNDRY-proof-run-goes-stale-when-any.md
- 20261009T024339Z-BENCH-player-log-going-silent-for-17.md
- 20261010T235838Z-BENCH-run-selftests-py-skips-tests-unchanged.md
- 20261011T015018Z-BENCH-game-that-has-run-for-hours.md
- 20261011T015018Z-BENCH-owner-ruling-that-refuses-behaviour-gss.md
- 20261011T015018Z-BENCH-polling-player-log-for-bridge-token.md
- 20261011T015018Z-BENCH-proof-labelled-with-tier-can-run.md
- 20261011T015019Z-BENCH-install-precheck-that-judges-simplified-model.md
- 20261011T025641Z-BENCH-betterstacktraces-writes-only-ref-xxxxxxxx-duplicate.md
- 20261011T025641Z-BENCH-log-budget-550-mod-list-cannot.md
- 20261011T053330Z-BENCH-full-list-proof-run-surfaces-2.md
- 20261011T053330Z-BENCH-owner-s-full-list-proof-map.md
- 20261011T053330Z-BENCH-vanilla-faction-factiontick-logs-faction-leader.md
- 20261011T095900Z-BENCH-perf-selftest-that-times-modelled-cost.md
- 20261011T120617Z-BENCH-fresh-pump-power-up-gap.md
- 20261011T120617Z-BENCH-staggered-check-defeats-per-tick-cache.md
- 20261011T121232Z-FOUNDRY-restoring-planted-defect-c-file-with.md
- 20261011T142704Z-BENCH-full-list-log-budgets-are-blind.md

## Kept on purpose
- 20261001T221817Z-FOUNDRY-generated-bridge-map-needs-player-settlement.md: its zsh `${=P}` clause is not proof-harness content.
- rimworld-modding/references/validation-plan.md left in place (other skills cite it; not in this brief) — the audit proposed moving it.

## Notes
- Description-trigger eval (skill-creator run_loop) NOT run: 20 queries x 3 runs of `claude -p` per iteration in this repo context is not cheap. debug-testing description keeps a redirect clause so old triggers still route here.
