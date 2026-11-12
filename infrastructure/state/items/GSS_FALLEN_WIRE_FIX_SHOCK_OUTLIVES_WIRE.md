---
state: built
needs: bridge
---

# GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

colonists downed by fallen-wire shock beside a lone mast with 0 links/0 fallen wires in census

Built at `c29007b6b66e` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-11-06: relentless game phase: game_fail (withheld for attribution, no strike): A1 FAIL on the running game (/home/mandrake/rm/relentless/live/GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE-A1-20261106T150134Z.log): A_probe_channel              FAIL      {'success': False, 'error': 'aerial probe timed out (no frame serviced it)'}
- 2026-11-06: relentless: game_fail at c29007b6b66e explained (PROOF): The binding has no site step, so the proof ran against whatever state the game was in. With no current map, MapComponentUpdate never runs, AerialProbe.Service never bumps serial, and ap() times out. The wrapper exits 1 for both 'row FAIL' and 'row never measured', so the live tier recorded a FAIL | follow-up: GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIV
- 2026-11-07: FROZEN STOP 2026-11-07: was checking/prove, gen 3, returns 1, checks 2, candidate 5b69373ab11c; released the check clone (clean: nothing unpushed to bundle); bundle /home/mandrake/rm/relentless/store/items/GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE/bundles/20261107T021515Z-GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE (from an earlier release); hold refused by design for checking items (it waits for the verdict/phase), item left as checking. NEXT: lift PAUSE and let the tick re-lease the checker on candi

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_FALLEN_WIRE_FIX_SHOCK_OUTLIVES_WIRE` first: another commit may already do it.
