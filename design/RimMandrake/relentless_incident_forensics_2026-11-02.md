# Relentless forensics (read-only), times UTC; PST = UTC-8
Outage start 05:36:43Z (21:36:43 PST). Last pre-outage journal tick 05:35:59Z. Restart tick 11:29:28Z (03:29:28 PST); round 11:30:23Z; ticks 11:32:33Z, 11:33:25Z(staffing). No journal after 11:32:33Z.
## Timeline after restart (journal.jsonl lines 1221-1228)
- 11:29:28 alarm books_stale; released+bundled orphans CONDUCTOR_RESTART_REDESIGN_NEVER_FREEZE_HIM, MOD_DEFINITION_LESSONS, SEATRESTART_AUDIT_WHOLE_FILE (store/orphans/bundles/20261102T1129xxZ-*); proof_weak HOT_RELEASE (returned queued); worker_lost PIPE_ATLAS (returned queued); VEE closed_waiting_for_seat; checker_lost WALK_SAVE; leased COMB gen5, STONE gen7 (unit rm-relentless-work-2b94e1a8dc-g7). live_round pid 149186 at 11:29:28 (round out 11:30:23: "no running game").
- 11:29:41 ledger BENCH close VEE (blind PASS 9d5b089d5f) + RUNNER verify (commit 58959bf05a). Also BENCH note HOT_RELEASE WEAK.
- 11:30:21 COMB gen5 ended gate_unmet, no edits (returned, not_before +6h).
- 11:31:33 STONE gen7 contract; 11:33:50 finish sha 8038889d89 -> commits 0b79d93acf, 8038889d89 published 11:33:36Z.
- 11:32:33 released check-WALK_SAVE-c1 (bundle null), PIPE_ATLAS clone (bundle 20261102T113236Z), returned COMB, check_started WALK_SAVE (c2 in 3828271b36), lease LIVE_PROOFS gen7 (fresh clone 11:33:12Z).
- 11:33:25 staffing record; 11:33:47 LIVE_PROOFS gen7 returned contract_unprovable (not_before +2h), status stopping. timer_guard_reading 11:48. Timer stopped by Luke ~11:45Z. 
- Git (origin/main since 03:21 PST): b31f6e2f14 03:33:25, 58959bf05a 03:30:25 (ledger supervisor), 0b79d93acf + 8038889d89 03:33:36 (STONE). Nothing else.
## staffing.jsonl NUL region
Bytes 305774..306238 (464 bytes, one whole record incl. newline, all NUL). Before: record at 05:33:20Z (923 B, "pool full: 9 clones, cap 10..."), complete, ends "}\n". After: record 11:29:28Z. The lost record is the 05:35:59Z tick's staffing line (journal has that tick). 654 lines, ends with newline. Journal.jsonl: 0 NULs, 1228 lines all parse.
## NUL/empty relentless files written 21:36-21:38 PST
- store/items/PIPE_ATLAS_REBUILD_OTHER_LOOKS_KINK/circling_marks.json (3975 B all NUL, 21:37:11); state.json.tmp.3772256 (2065 B all NUL, 21:37:53, orphan tmp; real state.json rewritten 03:32:37 OK)
- store/runs/roles/rm-relentless-check-3828271b36-g1-c1.err (146 B NUL) and .json 0 B (WALK_SAVE c1 checker verdict lost -> checker_lost)
- rm-relentless-check-f799ead7e4-g1-c1.json 0 B (HOT_RELEASE checker output; WEAK note/proof_weak recorded 11:29 -- verdict source unverified)
- rm-relentless-work-7276742958-g1.json 0 B at 22:10 PST (PIPE_ATLAS worker; "ended with no receipt")
- rm-relentless-check-b1cb61a919-g1-c1.json (VEE) 3539 B intact, valid JSON, real PASS text (written 21:37:03, 20 s into outage; content sane) -> VEE close at 11:29:41Z is based on a good verdict.
- .err files hold sandbox noise ("mkdir Permission denied ... seat-tmp") only.
## Published commits (origin/main after 03:21 PST)
- 0b79d93acf: 4 files (12_rocks_design.md +2, stone_buildstats_table.json, selftest_stone_buildstats.py, stone_buildstats.py): 0 NUL, sizes sane. 8038889d89: code_review/BENCH.jsonl +2 lines, 0 NUL. Neither touches any of the 369 NUL-filled tracked files in STONE/COMB clones (intersection empty).
- 58959bf05a (BENCH.jsonl +2, RUNNER.jsonl +1): 0 NUL, all lines parse.
- b31f6e2f14: BENCH.jsonl 15 ins/15 del, SAME multiset of lines, only reordered (merge artifact); 10238 lines all parse. No loss.
- Clone-local commit 7554f2da77 (STONE ledger events) is not in bench object store / not published.
## Clones at 21:36 PST and where now
Existed: COMB_HOLDS (cloned 21:30:56), REPAINT_SAVES (21:27, bundled 04:50Z... 05:... released 04:50:46Z, then dir remains), STONE_BUILDSTATS (cloned 21:36:08 = inside outage; 369 NUL files, worker committed on it), plus VEE, PIPE_ATLAS, HOT_RELEASE, WALK_SAVE, CONDUCTOR_RESTART, MOD_DEFINITION_LESSONS, SEATRESTART_AUDIT, check-WALK_SAVE-c1/ c2. Now in clones/: COMB (369 NUL), LIVE_PROOFS (fresh 03:33), REPAINT_SAVES, STONE (369 NUL), check-WALK_SAVE-c2 (fresh 03:32). Others bundled+removed (bundles exist, patches apply, PNGs decode per Luke) except check-WALK_SAVE-c1: removed, no bundle (bundle null).
Reflogs 21:36-03:21: bench reset 21:36:01 (pre-outage), dispatch ff-pull 21:36:26 (diff vs prior tiny, 0 files changed), STONE clone clone/checkout 21:36:08-22. No other checkout/reset of rm/* repos in the window.
## Restaffed after restart
COMB gen5 (no edits; clone NUL files but did nothing), STONE gen7 (built on NUL-filled clone; its 5 changed files fine; selftest green per candidate evidence), WALK_SAVE checker c2 (fresh clone, killed by Luke), LIVE_PROOFS gen7 (fresh clone, nothing built). HOT/PIPE/VEE were not rebuilt.
