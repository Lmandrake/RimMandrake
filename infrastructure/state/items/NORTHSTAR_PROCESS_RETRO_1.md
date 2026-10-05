# NORTHSTAR_PROCESS_RETRO_1 — Northstar process retro after GimmeSomeSlack goes Green

## spec
Owner, 2026-10-05: after GimmeSomeSlack reaches Green validation, run a Northstar review pass on the PROCESS itself,
not the mod: what worked, what did not, update the associated skills and suggestions, and think about new Python
helper-library functions that would have made this easier — and make them.

**Gate: do not start until GimmeSomeSlack is GREEN** (`modcheck status`). Until the owner validates its seeded
checklist and views the sheet once, the highest reachable status is DRAFT-CHECKLIST / PENDING-OWNER-REVIEW; start only
once it flips.

Inputs to read first: the FOUNDRY handoff written 2026-10-05, the seeding agent's notes
`Transient/gss_northstar_seed_notes.md`, `design/RimMandrake/debug_process.md`, the seeded `## north star` in
`design/validation_walks/RimMandrake/GimmeSomeSlack.md`, and today's friction: proof_all needs `--live` and the repo root;
human_review.py needs the repo root (relative log path); `modcheck` counts RECORD rows as RED (only PASS/SKIP/UNCOVERED/
UNBUILT are OK); a proof run goes stale when ANY mod-folder file changes; Player.log greps are refused by the blind-scan hook.

## verify
Skills touched (rimworld-load-round, rimbridge, using-rimflow, whichever the retro names) carry the new lessons; each new
helper has a selftest in `run_selftests.py`; the retro note lists what was NOT changed and why.

## criteria
Candidate helpers to evaluate (make the ones that pay for themselves): a one-call `game_cycle(tier)` (down, swap tier,
deploy, launch, wait for Bridge token, stamp state); `run_from_root()` so scripts never depend on cwd; a
`kill_hostiles(B)` shared by every review-map builder; `save_keeper(B, name)` with the before/after Saves stat;
`literal_log_wait(token)` that waits on a literal Player.log string without tripping the blind-scan hook; a proof-row
status-vocabulary check so a new status cannot silently read RED.
