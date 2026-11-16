# RIMMANDRAKE_ACCEPT_LEDGER_ONLY_TICKET_NAMES_THIRST_WAS_VALID

`modledger.append` refused a `finding:<NAME>` subject when the ticket had no prose file and its legacy name fails
today's namecheck (`THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY`, `FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE`). Older names
stay valid forever (CLAUDE.md), and most tickets are recorded only by their rimflow events. Found by the FlowWorks
backfill (RIMMANDRAKE_BACKFILL_FLOWWORKS_LEDGER_SHADOW_BESIDE_SLACK): 156 refusals.

## spec

`src/RimMandrake/rimflow/modledger.py` `_finding_name_ok`: a name filed in the rimflow ledger (a `file` event in
`infrastructure/state/ledger/events/*.jsonl`) is an existing item. The filed ids are read once per root and re-read
when a shard grows.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_modledger.py` -> `0 failures`; its check "a finding named
for a ticket filed in the rimflow ledger (no prose file, legacy name) passes" failed on c2b0236c96 (watched) and passes
at e04d509dcc.

## criteria

- the acceptance test passes;
- `modledger_backfill.py run --mod FlowWorks` refuses none of those 156 subjects.
