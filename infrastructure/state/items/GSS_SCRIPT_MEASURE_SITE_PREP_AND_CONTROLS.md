---
state: proposed
needs: offline
---

# GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Designer deep pass on GimmeSomeSlack (GSS): read its proof scripts, name each scene's missing site prep and control case, and file the build items for Relentless

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS` history before building.

## latest ledger notes

- 2026-11-06: a_flagship_pick answered (turn_04): the workshop floor is the face of the mod, judged first; the yard of masts is showcase 2.
- 2026-11-06: dispatcher alarm : RimMandrake/GimmeSomeSlack Designer turn (stage 2) waits on you since 2026-11-06 15:24:57Z: 1 ask (a_shock_floor_ends) in D:\Luke\dev\RimMandrake\design\concepts\GimmeSomeSlack\turn_05.md | a_shock_floor_ends: Does a sparking floor-cord end (left when a conduit cell is destroyed) shock a colonist who crosses it, with the one rebuilding that conduit safe, or do only fa
- 2026-11-06: a_shock_floor_ends answered (GSS turn_05): default = every sparking end shocks (floor cord ends too; the rebuilder stays safe per the 2026-11-05 rule). Add a Mod Settings choice with three values: None / Only downed (overhead) lines / All sparking ends; default All.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS` first: another commit may already do it.
