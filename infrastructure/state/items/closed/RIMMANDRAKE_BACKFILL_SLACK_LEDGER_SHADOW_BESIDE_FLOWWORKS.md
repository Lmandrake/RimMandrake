# RIMMANDRAKE_BACKFILL_SLACK_LEDGER_SHADOW_BESIDE_FLOWWORKS

Plan step 3 (`design/plans/2026-11-15-holder-pipeline-fusion-build.md`) for Gimme Some Slack, run in parallel with its twin
`RIMMANDRAKE_BACKFILL_FLOWWORKS_LEDGER_SHADOW_BESIDE_SLACK` (his plan change, ledger OWNER 2026-11-16T05:57:46Z: "I would like this tried at the same time on three mods
concurrently so that we can observe different outcomes rapidly."). Explosive Knockback was backfilled by
RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE at 872a7657e2 (383 events, packet 14,990 of 15,000 tokens at
df07a4a7de, compare 3 of 8 agree). Takes over the combined RIMMANDRAKE_BACKFILL_SLACK_AND_FLOWWORKS_LEDGERS_IN_SHADOW.

## spec

- `python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod GimmeSomeSlack`; fix in modledger_backfill.py (tests first, in
  selftest_modledger_backfill.py) whatever store shape this mod holds that Explosive Knockback did not. A fix to the tool
  lands for all three pilots; the twin is editing the same file, so publish small and often.
- `backfill_item_words` in `src/RimMandrake/rimflow/modledger.json`: list a short word only where it names nothing else
  (SLACK also names SlackMaster work).
- Over budget: fix the packet's ordering or line rule, never by dropping an open finding, a refuted cause or his answer
  (spec §3.3).
- Shadow only: nothing redirected, archived or deleted. Put `modledger_backfill.py compare --mod GimmeSomeSlack` in the close note.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_backfill_accept.py GimmeSomeSlack` — expected `PASS 7/7`.
Watched failing at filing on df07a4a7de: `FAIL 7 of 7` (no ledger). Sanity probe: `... modledger_backfill_accept.py
ExplosiveKnockback` passes 7/7 on the same commit.

## criteria

- the acceptance test passes; selftest_modledger and selftest_modledger_backfill stay green;
- the packet size and the compare table are in the close note.
