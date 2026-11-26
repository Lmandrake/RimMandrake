# WB-pipeline-helpers-20261126-155518

Member: RIMMANDRAKE_BOUND_SCRATCH_REAP_RUN_THAT_GREW_FOUR_MIN_TO_TWO_HOURS: fixed at c188af7952cb; close waits on one reaper run.

- Step A done: keep 1. The /tmp walk is not the cost (the tmp phase took 15 s). The apply phase is (5,430 of 7,383 s in the 08:09 PST run). Since 2026-11-25 05:04 each run archived 150 to 600 tiny clones, 4 to 700 s each. They were the fixture repos of two acceptance scripts that run as `cmd:` outcome checks every list_effect beat: `design/specs/2026-11-23-agent-work-to-code/acceptance/rank4_one_test_call_accept.py` (a.py, notes.txt, t.py) and `rank2_visit_and_cycle_kits_accept.py` (a.py). The checks ran with no TMPDIR of their own, and nothing removed the repos.
- Step B done: check `cmd:python3 src/RimMandrake/rimflow/selftest_list_effect.py > /dev/null 2>&1`, red on the parent (7 fails).
- Step C done: fix c188af7952cb. `list_effect.run` gives each `cmd:` check its own run_tmp TMPDIR and deletes it when the check ends. The promise is a-cmd-check-leaves-no-temp-files. Fresh reader: GPT through gpt_consult on Archmagi found NOTHING SIGNIFICANT (receipt consult-20261126-081346-4112570-320fcc).
- Live: the 08:55 PST list_effect beat ran on head 781221fa (it has the fix). It ran the rank4 check (fails) and left 0 new repos. The 09:01 list_dispatch beat also left 0.
- Backlog: 5,055 leaked fixture repos on Archmagi, matched by exact signature, were deleted under the reaper's run.lock at 10:12 PST. Manifest: `/mnt/d/ClaudeWork/scratch/reap_fix_review/purge_check_fixtures.manifest.json` (Archmagi).

Next: read the 11:01 PST rm-scratch-reap run on Archmagi (`last_run.json` seconds and phase_s), then close the member.
