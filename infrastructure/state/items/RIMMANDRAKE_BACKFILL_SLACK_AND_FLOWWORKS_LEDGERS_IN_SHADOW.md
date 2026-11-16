# RIMMANDRAKE_BACKFILL_SLACK_AND_FLOWWORKS_LEDGERS_IN_SHADOW

Plan step 3 (`design/plans/2026-11-15-holder-pipeline-fusion-build.md`) for the other two pilots, after Explosive Knockback (backfilled by RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE at 872a7657e2: 383 events,
packet 14,980 of 15,000 tokens, compare 3 of 8 agree). His card 2026-11-15: "Do all three side by side as a deeper test.
When one reveals a needed fix to the system all three benefit."

## spec

- Run `python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod GimmeSomeSlack` and `--mod FlowWorks`; fix in
  modledger_backfill.py (tests first, in selftest_modledger_backfill.py) whatever store shape those two hold that
  Explosive Knockback did not (Gimme Some Slack has ~17 stores and 413 ledger items, spec §1.1). A fix lands for all three.
- `backfill_item_words` in `src/RimMandrake/rimflow/modledger.json`: list a short word only where it names nothing else
  (SLACK also names SlackMaster work, so Gimme Some Slack likely needs none).
- If the packet passes its budget, fix the packet's ordering or line rule, never by dropping an open finding, a refuted
  cause or his answer (spec §3.3).
- Shadow only: nothing redirected, archived or deleted. Report `modledger_backfill.py compare --mod <Mod>` for each.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_backfill_accept.py GimmeSomeSlack FlowWorks` —
expected `PASS 14/14`. Watched failing at filing on 6a171f08f2: `FAIL 14 of 14` (no ledger for either mod). Sanity
probe: `... modledger_backfill_accept.py ExplosiveKnockback` passes 7/7 on the same commit.

## criteria

- the acceptance test passes; selftest_modledger and selftest_modledger_backfill stay green;
- each mod's packet size and its compare table are in the close note.
