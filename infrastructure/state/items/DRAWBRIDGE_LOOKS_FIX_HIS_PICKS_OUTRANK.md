---
state: built
needs: bridge
---

# DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

With a FlowWorks look loaded, the look's drawbridge (and suspension bridge) pictures override the owner's Timber/Steel material picks; make material picks win, looks restyle only pipes/machinery

Built at `718c799cc239` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-22: Drafted (NOT installed) shut gates matching the installed open frames: A/B Timber south/east, C/D Scrapper south/east. Phone: Transient/pile_2026-10-22/phone/gate_shut_phone.png (+.md), f663a8e106. Awaiting his pick.
- 2026-10-22: RULED: install gate_shut A-D
- 2026-10-22: Shut gate A-D (Timber/Scrapper south/east) installed per owner card 2026-10-22; sha f97f51d2dd. Scrapper Closed_* never read (Steel_Closed/Timber_Closed outrank look picture); OWED emptied in selftest

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK` first: another commit may already do it.
