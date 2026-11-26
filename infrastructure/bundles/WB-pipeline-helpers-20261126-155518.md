# WB-pipeline-helpers-20261126-155518

Member: RIMMANDRAKE_BOUND_SCRATCH_REAP_RUN_THAT_GREW_FOUR_MIN_TO_TWO_HOURS: DONE. Fixed at c188af7952cb. list_dispatch closed it early (16:20Z, noCode), before the fix; the note of 0a9b01ac records the real fix.

- Step A done: keep 1. The /tmp walk is not the cost (the tmp phase took 15 s). The apply phase is (5,430 of 7,383 s in the 08:09 PST run). Since 2026-11-25 05:04 each run archived 150 to 600 tiny clones, 4 to 700 s each. They were the fixture repos of two acceptance scripts that run as `cmd:` outcome checks every list_effect beat: `design/specs/2026-11-23-agent-work-to-code/acceptance/rank4_one_test_call_accept.py` (a.py, notes.txt, t.py) and `rank2_visit_and_cycle_kits_accept.py` (a.py). The checks ran with no TMPDIR of their own, and nothing removed the repos.
- Step B done: check `cmd:python3 src/RimMandrake/rimflow/selftest_list_effect.py > /dev/null 2>&1`, red on the parent (7 fails).
- Step C done: fix c188af7952cb. `list_effect.run` gives each `cmd:` check its own run_tmp TMPDIR and deletes it when the check ends. The promise is a-cmd-check-leaves-no-temp-files. Fresh reader: GPT through gpt_consult on Archmagi found NOTHING SIGNIFICANT (receipt consult-20261126-081346-4112570-320fcc).
- Live: the 08:55 PST list_effect beat ran on head 781221fa (it has the fix). It ran the rank4 check (fails) and left 0 new repos. The 09:01 list_dispatch beat also left 0.
- Backlog: 5,055 leaked fixture repos on Archmagi, matched by exact signature, were deleted under the reaper's run.lock at 10:12 PST. Manifest: `/mnt/d/ClaudeWork/scratch/reap_fix_review/purge_check_fixtures.manifest.json` (Archmagi).
- Reaper reading: the 11:02 PST run judged 728 candidates (it was about 6,000) and took 3,660 s (the 08:09 run took 7,383 s), ok=True. The rest of the time is the per-row /proc scan under host load 27 to 38 at nice 19 (one 3.8 KB row took 819 s). That is a polish line: `design/specs/2026-11-26-scratch-row-aged-by-write/polish.md`.
- Found in the run: the shape gate accepted a check that failed only on this clone's edited selftest. Origin's copy held, so list_dispatch closed the item early. Fixed at 45782d40: `attach_gate` refuses a check whose named file differs from origin/main. GPT's fresh read found 3 gaps, each fixed test first. list_effect.py is FLAGGED (6e912fdb).

Next: none. The bundle is finished.
