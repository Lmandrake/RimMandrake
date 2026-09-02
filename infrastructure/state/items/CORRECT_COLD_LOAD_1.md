# CORRECT_COLD_LOAD_1

## Spec

`infrastructure/state/items/COLD_LOAD_RUN_SHEET_2.md`'s "🔴 DEPLOY BATCH staged
2026-09-02 (BENCH) — four fixes written and COMPILED, none deployed" section is
stale as of the 2026-09-02 game-DOWN signal. FOUNDRY ran the three staged
commands at that signal:

```
python.exe src/RimMandrake/bridgetools/build.py --gm --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod StructureInjections --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod RimDefDump --apply
```

Results:
- Companion (`--gm --apply`): built clean, 0 warnings/errors, GM tools present
  (`jawa/fire_incident`, `jawa/send_letter`), deployed. This build also
  carries this session's `JawaBenchLoadStallProbe.cs` field-not-found /
  spinner-delta fix (commit `e94717ce`, `LOAD_STALL_PROBE_INSTRUMENT_GAPS_1`).
- `StructureInjections`: reported "in sync (2 files)" — already deployed
  before this command ran (presumably BENCH, same sitting).
- `RimDefDump`: same, "in sync (2 files)", already deployed.

**Correction**: retitle that section from "staged... none deployed" to
deployed, and change the "🔴" to "✅". None of the four fixes is PROVEN LIVE
yet — that still needs the next launch and the decision strings already
written in that section (`jawa/inventory_transfer` movedCount, `spawn_pawn`
substitutedCount, rimplace click position, def-dump-on-demand action). Only
the deploy status changes, not the verify plan.

## Watch out

I did not diff the companion DLL bytes before/after — build.py reported
"state: identical, nothing to do" then "deployed" in the same run, which
reads as idempotent-deploy logic (skip the copy if a hash already matches)
rather than a no-op that silently skipped my `JawaBenchLoadStallProbe.cs`
change. Worth a sanity check at the next launch's ready-line/tool-count
rather than assuming byte-for-byte trust from this note alone.

## verify

Next launch's decision strings (already in COLD_LOAD_RUN_SHEET_2 section 1
and the deploy-batch table) confirm the fixes are live, not just deployed.

## criteria

COLD_LOAD_RUN_SHEET_2's deploy-batch section reflects "deployed, not yet
live-proven" instead of "staged, none deployed."
