# SCRATCH_REAP_FIX_ROUND_TEN_STILL_FINDS

## Findings

Codex full-file review of scratch_reap.py at 494774e9d3 (round 4 of CLEANER_SANITY_REVIEW_FINISH_FULL_FILES), quoted as it answered. Each is a claim: verify it before fixing, and drop any that is not real.

1. **`corpus()` misses transient user services.** It reads only `~/.config/systemd/user/*.service` and their drop-ins. A deferred job created with `systemd-run --user --on-active=2h`, whose working directory is an otherwise old scratch clone, has its reservation under `/run/user/<uid>/systemd/transient/`. With no worker running yet, neither `/proc` nor the corpus protects it. The hourly reaper can delete the clone before the scheduled job starts, causing that job to fail.

2. **`ledger_mentions()` misses paths supplied through systemd template specifiers.** For example, `worker@.service` contains `WorkingDirectory=/home/mandrake/rm/scratch/%i`, and a timer will start `worker@job1.service`. The corpus contains no literal `scratch/job1`; reading the template and its drop-ins therefore does not protect `/home/mandrake/rm/scratch/job1`. Once otherwise eligible, that reserved clone is deleted and the next activation fails.

3. **`path_forms()` can exhaust memory or stall the reaper on ordinary long option values.** For every argument beginning with `-`, it constructs almost every suffix of the entire argument, including its value. A live process carrying `--prompt=<100 KiB of text>`—within Linux’s individual argument limit—produces roughly 5 GiB of suffix strings before subsequent path copies. The repeated `raw not in out` searches also perform billions of comparisons. A large inline prompt, JSON payload, or schema can therefore OOM-kill the unattended reaper or make it exceed its service timeout.
