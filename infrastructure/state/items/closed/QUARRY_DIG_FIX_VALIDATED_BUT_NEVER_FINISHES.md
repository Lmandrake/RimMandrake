---
state: built
needs: bridge
---

# QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Quarry dig job never finishes on the test machine (26 failed / 41 partial runs) while FLOWWORKS_QUARRY_DIGGING_1 stands validated

Built at `2352e59c0249` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-31: 30 more UNTRIAGED findings (rows cut_turns_up_local_find x25, finds_off_none x5; latest FAIL 10-31T05:19Z, 0 passes since) are this same 'dig job never finished'; retyped TRACKED.
- 2026-11-06: relentless game phase: game_fail (withheld for attribution, no strike): A1 FAIL on the running game (/home/mandrake/rm/relentless/live/QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES-A1-20261106T160329Z.log): FAIL FlowWorks
- 2026-11-06: relentless: game_fail at 2352e59c0249 explained (SITE+CHECKER): assert_bland counts every dead non-fixture colonist on the map as contamination; the running game's map still held three dead colonists from an earlier session and restore_colonists (acted 15) does not clear them, so the chain went UNMEASURED with only a site-hold component; judge() treats a missing row as FAIL rather than UNMEASURED,

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES` first: another commit may already do it.
