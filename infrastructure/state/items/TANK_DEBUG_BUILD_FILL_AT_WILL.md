---
state: built
needs: bridge
---

# TANK_DEBUG_BUILD_FILL_AT_WILL

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

God-mode debug actions: empty, or fill to max, every universal container with any FlowWorks liquid (default water)

Built at `46a70124622c` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-23: Source committed e609a50675 (not pushed: publish refused, DLL dirty with other helpers' hose/rivers WIP). OWED: add Compile lines FlowWorksTankDebug.cs + RM_TankDebugMath.cs to RimMandrake_FlowWorks.csproj, TankDebugChecks.cs + RM_TankDebugMath.cs to SelfTest csproj, TankDebugChecks.Run in SelfTest/Program.cs (already in working tree, uncommitted shared files); then rebuild DLL, commit, publish. Live check owed: owner uses on walk save.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify TANK_DEBUG_BUILD_FILL_AT_WILL --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=TANK_DEBUG_BUILD_FILL_AT_WILL` first: another commit may already do it.
