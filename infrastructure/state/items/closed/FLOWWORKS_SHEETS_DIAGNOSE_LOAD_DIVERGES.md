---
state: built
needs: bridge
---

# FLOWWORKS_SHEETS_DIAGNOSE_LOAD_DIVERGES

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

canal_overflow SAVE_LOAD_CONTINUES_IDENTICAL FAILs 7x on 10-28 (last 10-29, never passed): hashes match at save/load (h0==h0AfterLoad) but continuing 3 pulses diverges from load+3 pulses (hContinued != hLoadedContinued) so some sheet state is not saved or reset on load. Row in sheet_overflow_proof.py:~917

Built at `c1340e0dbc76` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-11-01: b9264604c6: two causes of the 0114 SAVE_LOAD FAIL (h0==h0AfterLoad, 3 pulses later 3ab20b22 vs 59078fb2). (1) the deployed FlowWorks DLL (10-31 10:48) predates the wake-record fix c1340e0dbc: it holds no 'RM_sheetKinds' literal, the repo DLL does (strings -el, repo DLL the positive control). (2) new: ClassifyCell read GenTemperature.GetTemperatureForCell, whose outdoor value is TileTemperaturesComp's 60-tick cache phased from its first query (restarts on load) and whose room temps are saved trun
- 2026-11-01: sha correction: the previous note's b9264604c6 landed on origin/main as df7afe1371 (rebased by ./publish).

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify FLOWWORKS_SHEETS_DIAGNOSE_LOAD_DIVERGES --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=FLOWWORKS_SHEETS_DIAGNOSE_LOAD_DIVERGES` first: another commit may already do it.
