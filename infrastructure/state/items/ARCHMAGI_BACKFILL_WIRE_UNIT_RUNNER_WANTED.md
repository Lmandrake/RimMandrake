# ARCHMAGI_BACKFILL_WIRE_UNIT_RUNNER_WANTED

## proof (corrected 2026-11-17, drain of the retired judge)
    python3 src/RimMandrake/Utils/testq/archmagi_switch_reading.py

## why this is ready, not done — and what is UNMEASURED
Measured 2026-11-17 in a shared clone on a host with no D: drive: rc=1, and the only red line is
`FAIL cannot read /mnt/d/ClaudeWork/rimmandrake/testq/archmagi_state.json`. That is "could not look", not
"failed": the reading this proof is built on lives on the Archmagi host's own disk. The proof is correct as
written; it must be run where that state file exists.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/ARCHMAGI_BACKFILL_WIRE_UNIT_RUNNER_WANTED.txt

Next worker: run the line above on a host that mounts D:\ClaudeWork\rimmandrake\testq, or point the reader at
the live store, before judging the switch reading.
