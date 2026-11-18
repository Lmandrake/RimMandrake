# RIMMANDRAKE_ADMIT_TEN_WORD_FAULT_ID_INTO_KNOCKBACK_LEDGER

Explosive Knockback's blind fault `RIMMANDRAKE_COVER_FOUR_GAME_SIDE_FAULTS_NO_OFFLINE_TEST_SEES`
(`design/concepts/ExplosiveKnockback/version/blind_challenge/cycle_1/lane2/faults.json`, status NOTED_FOR_CONDUCTOR,
Polish) is the one entry the entry-standard re-backfill (e7342388986d) leaves out: its id has 10 words, so
`finding:<id>` fails the project namecheck (4-9 words) and `modledger append` refuses it. No rimflow item carries that
name, so the "existing item" route does not admit it either. The holder's packet therefore lacks one open polish fault.

## spec

Pick one and do it, tests first: (a) file a rimflow item under a valid name for the fault and record the old id in
the finding's text (the fault record keeps its id), or (b) let `modledger._finding_name_ok` admit an id the mod's own
blind-challenge `faults.json` already uses (a recorded name, like a legacy id), with a selftest that a 10-word id in a
fixture's faults.json passes and an unrecorded 10-word name is still refused. (b) is the smaller change; (a) keeps the
grammar strict. The Conductor's call.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/modledger_backfill.py run --mod ExplosiveKnockback | grep -c "refused, left out"`
prints 0 (prints 1 on 3c96e6e3cc29, watched), and `python3 src/RimMandrake/rimflow/modledger.py lint --mod ExplosiveKnockback`
exits 0.

## criteria

The fault appears in `modledger.py open --mod ExplosiveKnockback`; no other refusal is introduced.
