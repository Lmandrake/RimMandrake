---
state: validated
needs: offline
---

# HOSE_REEL_FIX_TURNS_WITH_THE_SHIP

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Hose reels cannot rotate (every look's outlet faces west), so a reel can't turn with a gravship and a hose to an east target must U-turn. Make RM_HoseReel rotatable: four facings per look (art), nozzle/outlet position per facing (reel_intake_geometry.py + selftest_hose_ports.py), hose leaves along the outlet axis.

Built at `0ab8470911c8` (origin/main); code is in, what is owed is below.

## what is left

- A2

## latest ledger notes

- 2026-10-29: Conductor triage 2026-10-29: N/S art was redrawn (REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED done; REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON built). Which candidate goes live is art (§1): the art-eval judge picks, install, deploy, then stage a reel at all four facings. The L4 look stays his (delegation_policy §2.1, L4 is his by definition) and rides the one FlowWorks/water look-sitting card in conductor/owner_cards_2026-10-29.md; FOUNDRY stages, then needs owner.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_REEL_FIX_TURNS_WITH_THE_SHIP --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_REEL_FIX_TURNS_WITH_THE_SHIP` first: another commit may already do it.
