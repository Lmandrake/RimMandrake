# TRIO_CRITIC_FIX_RC1_REREAD_BURNS_ROUNDS

Found in the attempt-6 restart on 8ff2858a8c (2026-10-31).

## Defect
1. Trio round 1 on RP_DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER: both critic tries (CRITIC_TRIES)
   returned invalid "no JSON envelope from claude (rc 1)" in 1-2 s each.
   L4OpusCritic.review keeps only meta.stderr_tail, and that tail is not persisted, so the cause is lost.
2. Round 2 (18:25:51): the build gave the same head 477f8ee58817. tester_pass / _logged_verdict
   re-read the logged INVALID verdict for that unchanged build and recorded it as a reject,
   "critic INVALID (from the log)". A round burned with no critic run.
   An invalid verdict must never be reused as a verdict.

## Not reproduced
Probes in /home/mandrake/.seat-tmp/FOUNDRY/r6probe/ (critic_probe.py through critic_probe4.py) covered
my shell, systemd-run in rm-harness.slice, the real diff plus .claude/CLAUDE.md at that head, and
spend_mirror running. Every probe returned rc 0 and accept.

## Fix owed
- Persist stderr_tail (and argv/cwd) on an invalid critic verdict.
- Do not count an invalid logged verdict as a reject on reread; rerun the critic instead.
- Rerun trio task 1 after clearing ctl/trio/RP_DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER/state.json (n=3),
  then remove ctl/trio/STOP.

## Evidence
- /mnt/d/ClaudeWork/rimmandrake/arena/events/trio.jsonl (critic_round events)
- /mnt/d/ClaudeWork/rimmandrake/foundry_arena/replay/launcher.log (RESTART6 lines)
- /mnt/d/ClaudeWork/rimmandrake/foundry_arena/replay/ctl/trio/STOP
