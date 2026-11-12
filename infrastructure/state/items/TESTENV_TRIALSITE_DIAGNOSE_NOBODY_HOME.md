---
state: built
needs: bridge
---

# TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Test environment: NS_FlowWorks_TrialSite_v1 on ratchet_pilot+patches loads with NO living colonist on the current map (list_pawns: 0 colonists) and a GameEnded 'Game Over' letter stops safe_advance within 360 ticks; it also raises 18 VEF new-faction dialogs, not 5 (the quiet-site broker answers them). Find where the fixture's colonists went before any FlowWorks row trusts that save. Evidence Transient/night_20261013/quiet_live/quiet_probe2_out.json, quiet_probe3_out.json

Built at `97af3a11ea8e` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-15: DIAGNOSED OFFLINE: the save holds zero player pawns by design (prep_site.py step 2 despawns every pawn; sidecar despawned=[]; map holds only cryptosleep ancient soldiers/megascarabs, world pawns are faction leaders). So 0 colonists and GameEnded at ~360 ticks are expected, not a corrupt save; the 18 VEF dialogs are a separate matter. Fixed in 97af3a11ea8e: verify() no longer reads an empty colony as quiet, quiet_site.ensure_colonists(session,3) spawns drafted colonists. NEXT: call ensure_colonis
- 2026-10-22: K0 2026-10-21 selftest record at 0e73732369: northstar/selftest_live_session.py + selftest_river_site.py PASS. The owed criterion is an in-game check, so it STAYS OWED (not verified by selftest).
- 2026-10-26: 2026-10-26 BENCH L1 pass: A1 NOT run. NS_FlowWorks_TrialSite_v1.rws is absent from Saves\ (only in Saves_backup_FOUNDRY_20261017T2025Z / _20261018T0100Z) and was built on ratchet_pilot+patches, while the live game runs the 320-mod list. Owed: restore the fixture to Saves (decide which backup is current) and load it on its own list, then ensure_colonists(3) + 600 ticks.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=TESTENV_TRIALSITE_DIAGNOSE_NOBODY_HOME` first: another commit may already do it.
