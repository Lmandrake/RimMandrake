# RIMMANDRAKE_RENAME_DEPLOY_CHECKOUT_OFF_THE_PULSE_NAME

## spec

The live deploy checkout `/home/mandrake/rm/pulse-deploy` (run by `rm-deploy-update.service` and
`rm-streams-collect.service`), the env names `RM_PULSE_DEPLOY` and `RM_PULSE_STATE`, `ops_watch.PULSE_DEPLOY`, its
`.git/pulse_update_last_good` stamp and the state dir `~/.local/state/rm-dashboard/` (now holding only the steward's
`failures.jsonl` and `phone_push.json`; the retired daemon's twelve files moved 2026-11-19 to
`D:\ClaudeWork\retired-trees\rimmandrake_eras_20261119\`) all carry the retired RimPulse name. Do: a fresh ext4 clone at a
neutral path, both units and `ops_watch` in one commit, the env names and state dir renamed, `scratch_reap.PROTECTED`
updated; `selftest_deploy_on_ext4.py` keeps its promise.

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    git grep -l -E 'pulse-deploy|RM_PULSE_(DEPLOY|STATE)|rm-dashboard' -- src .claude ':!*selftest*'

prints nothing and exits 1 once done. Watched failing 2026-11-19 BENCH at `fbdf50a5b2`: 14 files, exit 0. Plus
`grep -l -E 'pulse-deploy|RM_PULSE' ~/.config/systemd/user/*` prints nothing and `rm-deploy-update.service` succeeds once
after the move.

## criteria

- A1: no live file or unit names pulse-deploy, RM_PULSE_* or rm-dashboard (the greps above).
- A2: rm-deploy-update.service fast-forwards the new checkout (its next run succeeds).

## refs

file: src/RimMandrake/Utils/ops_core/deploy_update.py
file: src/RimMandrake/Utils/ops_watch.py
file: src/RimMandrake/Utils/scratch_reap.py
