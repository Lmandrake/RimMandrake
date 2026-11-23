---
state: proposed
needs: offline
---

# DRAWBRIDGE_SWING_DESIGN_LESS_RIDICULOUS

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Design how a drawbridge leaf and gate move when opening and shutting, in all four directions, so it does not look ridiculous; offline motion study first, then build, then his look in game.

## what is left

- proposed: nothing recorded as owed beyond the title; read `rimflow show DRAWBRIDGE_SWING_DESIGN_LESS_RIDICULOUS` history before building.

## latest ledger notes

- 2026-11-03: RULED: no stretching. Smooth if possible, else 4-10 stepped poses; art count must be worked out across bridge sizes.
- 2026-11-03: Designer found: today's swing breaks his no-stretching ruling. RM_DrawbridgeArt.DrawLeafUp (cs:236-244) scales the picture height by length*rise; the deck stops printing on the first step, so the deck vanishes and a scaled leaf grows from nothing. Design R12 line 197 also stretches a steel leaf over 4 cells. Checks: design/concepts/FlowWorks_Drawbridge/sitting_01_brief.md rows 8-9.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_SWING_DESIGN_LESS_RIDICULOUS --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_SWING_DESIGN_LESS_RIDICULOUS` first: another commit may already do it.
