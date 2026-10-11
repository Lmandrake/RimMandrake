# Skill curation — lessons of 2026-10-10/11

Fresh-context curation pass (BENCH helper). Input: 39 lesson files under `infrastructure/state/lessons/` (left in place — they are the record).
Actions: merged · already-covered · project-only (belongs in a doc, not a skill) · rejected.

| lesson file | gist | target skill | action | where |
|---|---|---|---|---|
| `20261010T004445Z-BENCH-art-py-enact-ingest-ran-before.md` | enact ingest ran before purge; dry run and apply disagreed | (art ledger tooling) | project-only | fixed 7c623ab47 + selftest_enact_selfpurge.py; the code is the record |
| `20261010T004445Z-BENCH-legacy-pre-2026-10-04-no.md` | legacy (pre-snapshot) sheet decisions refused by enact; 229 rows never redrawn | (art ledger tooling) | project-only | legacy_redo_triage.py; belongs in art_ledger_design doc |
| `20261010T004445Z-BENCH-owner-quote-provenance-guard-treats-owner.md` | guard refuses a question and joined quotes | using-rimflow | merged (question half already-covered) | owner-quote provenance section: new 'one verbatim statement per quote' bullet |
| `20261010T004445Z-BENCH-shared-bench-clone-pull-rebase-refuses.md` | pull --rebase refuses on peers' dirty files; path-scoped stash; push in a separate call | (GIT_WORKFLOW.md) | project-only | proposed text below (P1) |
| `20261010T004445Z-BENCH-subagent-s-deployed-n-files-verified.md` | 'Deployed, VERIFIED' goes false when another clone redeploys an older sha | rimworld-deploy | merged | §8 After deploying: 'true only until the next writer' |
| `20261010T051816Z-FOUNDRY-mod-hiding-headgear-can-sit-pawnrendernodeworker.md` | hat hidden via HeadgearVisible not CanDrawNow (ReGrowthCore swimming) | rimworld-modding | merged | references/traps-mods-and-managers.md: 'Another mod hid every hat' |
| `20261010T051816Z-FOUNDRY-short-mental-state-rm-parentalenrage-lasts.md` | scenelib.run overshoots ~100 ticks; short states invisible | rimbridge | merged | references/traps.md: 'Bridge time is TICKS' |
| `20261010T104515Z-BENCH-enact-redo-job-for-make-it.md` | anatomy-rejecting redo must carry no reference image | generating-rimworld-sprites | merged | 'Before filing a job through the artpipe queue' |
| `20261010T104517Z-BENCH-rimflow-owner-quote-flag-refused-for.md` | mid-turn owner words refused by forged-quote guard | using-rimflow | already-covered | owner-quote provenance section: 'A message that arrives MID-TURN is refused too' |
| `20261010T164936Z-BENCH-publish-runs-git-pull-rebase-autostash.md` | ./publish autostash can strand peers' work in stash@{0} | (GIT_WORKFLOW.md) | project-only | proposed text below (P1) |
| `20261010T205804Z-BENCH-pre-push-ledger-lint-hook-checks.md` | pre-push ledger_lint checks LOCAL HEAD; push the sha from a clone at origin/main | (GIT_WORKFLOW.md); using-rimflow | merged (ledger half) + project-only (landing half) | using-rimflow Committing ledger writes; P1 |
| `20261010T235838Z-BENCH-landing-commits-through-scratch-clone-because.md` | landing via scratch clone leaves seat clone behind; stale-tree selftest reds | (GIT_WORKFLOW.md) | project-only | P1 |
| `20261010T235838Z-BENCH-run-selftests-py-skips-tests-unchanged.md` | run_selftests skips unchanged tests; low PASS count is cache skips | (run_selftests.py) | project-only | already stated in run_selftests.py docstring + evidence line; no skill covers selftests |
| `20261011T015018Z-BENCH-bridge-tests-step-game-few-ticks.md` | tick-keyed mod cache stale across bridge calls | rimbridge | merged | references/traps.md: 'Bridge time is TICKS' |
| `20261011T015018Z-BENCH-game-that-has-run-for-hours.md` | list_logs limit=500 loses startup line on long sessions | rimbridge | merged | references/traps.md: 'list_logs is a ring, not the log' |
| `20261011T015018Z-BENCH-owner-ruling-that-refuses-behaviour-gss.md` | a refusing ruling invalidates live test scenes built before it | deciding-and-superseding | merged | 'A stale belief hides in a comment or a table cell' |
| `20261011T015018Z-BENCH-polling-player-log-for-bridge-token.md` | Bridge token grep matches the previous session's log | rimworld-load-round | already-covered + pointer | rimbridge traps.md 'Player.log PERSISTS between runs'; one-line pointer added at load-round §0 Bridge-token rule |
| `20261011T015018Z-BENCH-proof-labelled-with-tier-can-run.md` | a tier-labelled proof ran on 550 mods; read len(env.running) | rimworld-debug-testing | merged | §3 'Say which MOD LIST too' |
| `20261011T015019Z-BENCH-install-precheck-that-judges-simplified-model.md` | precheck on a simplified model accepted what the real lay refused | rimworld-debug-testing | merged | references/long-proofs.md 'A simplified model passes what the real operation refuses' |
| `20261011T025641Z-BENCH-betterstacktraces-writes-only-ref-xxxxxxxx-duplicate.md` | [Ref] duplicate stacktrace has no frames; known full-list NREs | rimworld-modding | merged | references/player-log-triage.md |
| `20261011T025641Z-BENCH-log-budget-550-mod-list-cannot.md` | charge log errors to a mod only against a same-list control | rimworld-modding | merged | references/player-log-triage.md 'Charge an error to a mod only against a CONTROL' |
| `20261011T025641Z-BENCH-owner-s-full-list-out-combat.md` | Out of Combat ReBoost: walk pace not predicted by MoveSpeed | rimbridge | merged | references/traps.md: 'Bridge time is TICKS' |
| `20261011T025641Z-BENCH-rimworld-frame-cell-rect-keeps-current.md` | frame_cell_rect keeps current zoom; zoom to sizeRange.min first | rimworld-live-review | merged | §5 Frame bullet |
| `20261011T025641Z-BENCH-rimworld-load-game-answers-queued-old.md` | load_game 'queued'; old map stays Playing 3-8 s | rimbridge | merged | references/traps.md under load_game_ready section |
| `20261011T052223Z-FOUNDRY-dotnet-selftests-need-winstage.md` | dotnet.exe selftests fail from ext4; use selftest_winstage.py | (GIT_WORKFLOW.md / Windows-side tools) | project-only | P2 |
| `20261011T052223Z-FOUNDRY-fresh-clones-14gb-delete-when-pushed.md` | clones ~14 GB; --filter=blob:none; delete only when 0 unpushed | (GIT_WORKFLOW.md) | project-only | P1 |
| `20261011T052223Z-FOUNDRY-phantom-selftest-reds-stale-seat-clone.md` | stale dirty seat clone shows phantom selftest reds | (GIT_WORKFLOW.md) | project-only | P1 |
| `20261011T052223Z-FOUNDRY-reconcile-sweep-use-fresh-clone.md` | RECONCILE sweeps must re-check in a fresh origin clone | using-rimflow | merged | Reading projections: 'a view is only as current as the clone' |
| `20261011T052223Z-FOUNDRY-seat-clone-recovery-reset-hook-refuses.md` | hook refuses reset --hard; stale clone recovery is a procedure | (GIT_WORKFLOW.md) | project-only | P1 (procedure lives in Transient/seat_clone_audit_20261011.md, which expires: promote it) |
| `20261011T052223Z-FOUNDRY-selftest-watch-dirtied-fixtures-json.md` | selftest_watch dirtied fixtures.json, blocked pull --rebase | (fixed) | project-only | fixed dcb08c809; historical |
| `20261011T052223Z-FOUNDRY-stale-clone-ledger-events-ledger-sync.md` | stale clone can't push its shard; ledger_sync.py rescues | using-rimflow | merged | Committing ledger writes: stale-clone paragraph |
| `20261011T053330Z-BENCH-full-list-proof-run-surfaces-2.md` | one fragility-class audit finds 8 harness assumptions at once | rimworld-debug-testing | merged | references/long-proofs.md + §4b pointer |
| `20261011T053330Z-BENCH-owner-s-full-list-proof-map.md` | proof map not calm: respawning wildlife, wandering colonists, hive NREs | rimworld-debug-testing | merged | references/long-proofs.md 'The proof map does not stay calm' |
| `20261011T053330Z-BENCH-vanilla-faction-factiontick-logs-faction-leader.md` | Faction leader null ErrorOnce on first tick; control window misses it | rimworld-modding | merged | references/player-log-triage.md (control paragraph) |
| `20261011T060426Z-BENCH-rimpulse-lists-review-sheets-only-from.md` | RimPulse lists sheets only from *.serve.log; 8 servers raced loopback | (RimPulse / review-sheets tooling) | project-only | P3 (review-sheets skill is a separate repo, generic; RimPulse is project tooling) |
| `20261011T061409Z-BENCH-artpipe-owner-kind-canon-check-grades.md` | canon check grades every owner_note sentence; vacuous pass; pose change is a generator limit | generating-rimworld-sprites | merged | 'Before filing a job through the artpipe queue' (two bullets) |
| `20261011T063941Z-BENCH-reader-that-re-derives-rimflow-item.md` | re-deriving item state from raw events drifts; use replay(observe=) | using-rimflow | merged | Reading projections: 'fold through model.replay' |
| `20261011T064401Z-BENCH-gss-2026-10-10-build-out.md` | sweep read doc 'not changed yet' lines; 4 of 7 'unworked' pieces built | deciding-and-superseding | merged (rule already-covered by CLAUDE.md 'search src before filing') | 'A doc's state column decays…' + git log -S instrument |
| `20261011T064841Z-BENCH-sheet-serve-log-can-carry-several.md` | serve.log has several blocks; read the LAST answering url | (refresh_sheets.py) | project-only | fixed 2026-10-10 with selftest; P3 |

## Tally

merged 24 (incl. 3 partial: one also already-covered, one also project-only, one also already-covered by CLAUDE.md) · already-covered 2 · project-only 13 · rejected 0. No lesson found false; spot-verified: guard substring match (`block_forged_owner_said.py` `_norm(q) not in haystack`), `scenelib.run` uses `play_for`, `model.replay(observe=)`, `ledger_sync.py`, `selftest_winstage.py`, `canon_check.py` `canon_na`, `proof_all` `env["running"]`.

Skills touched: using-rimflow, rimbridge (references/traps.md), rimworld-load-round, rimworld-modding (references/player-log-triage.md, traps-mods-and-managers.md), rimworld-live-review, rimworld-debug-testing (SKILL.md + new references/long-proofs.md, description), deciding-and-superseding, rimworld-deploy, generating-rimworld-sprites.

## Proposed text for BENCH (not in a skill — design/RimMandrake/GIT_WORKFLOW.md is not this pass's to edit)

**P1 — GIT_WORKFLOW.md, "Landing when pull --rebase is refused":**
- `./publish` runs `pull --rebase --autostash`; in a dirty shared clone the re-apply can conflict and strand peers' uncommitted work (sheet HTML, owner decisions) in `stash@{0}` (53 files, 2026-10-10; restored with `git restore --source=stash@{0}`). Helpers in a dirty clone land via `land.sh` / temp `GIT_INDEX_FILE` + `commit-tree` on origin/main, never `./publish`.
- The pre-push `ledger_lint` hook evaluates the LOCAL HEAD: push a commit-tree'd sha from a clone sitting at origin/main, and push in a separate Bash call from the rebase.
- Landing through a scratch clone leaves the seat clone BEHIND; a stale or dirty seat clone shows phantom selftest reds (ledger_lint NOT_APPEND, a "lost" bridge tool). Sync (path-scoped stash of your own paths → pull --rebase → pop) or verify on a clean origin clone before fixing any red.
- Stale-clone recovery: `git reset --hard` is hook-refused on purpose. Rescue ledger events with `ledger_sync.py` first, then follow the procedure now in `Transient/seat_clone_audit_20261011.md` — which expires in ~14 days, so promote it into this doc.
- Clones are ~14 GB with selftest stages (18 strays filled 276 GB, 2026-10-11): `--filter=blob:none`, and delete a finished clone only after `git log origin/main..HEAD` is empty and `git status` is clean.

**P2 — GIT_WORKFLOW.md, "Windows-side tools":** selftests that run Windows `dotnet.exe` fail from any ext4 clone (MSB3101/MSB3030/MSB1009 — not regressions); `src/RimMandrake/Utils/selftest_winstage.py` stages them on the Windows drive.

**P3 — review-sheet tooling doc (wherever RimPulse/serve_gated are documented):** RimPulse lists sheets only from `Transient/biome_ffar/*.serve.log` (last URL answering 200) — redirect `serve_gated.py` output there; a dead sheet's log keeps it listed until its server stops; a log may hold several server blocks, so read the LAST answering url; start servers one at a time (8 at once raced the WSL loopback relay).
