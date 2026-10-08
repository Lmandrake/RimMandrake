# FLOOD_LEDGER_LOAD_LOSS_1 — FloodedCanyon flood ledger is lost on every load

Found by the kernel extraction audit, `Transient/kernel_audit_20261008.md` (2026-10-08).

## spec
Commit `3f5701d45` moved the flood ledger into the kernel and rewrote
`RM_MapComponent_CanyonFlood.ExposeData` (`src/RimMandrake/FloodedCanyon/Source/RM_MapComponent_CanyonFlood.cs`,
~lines 519-538) to scribe `activeFloodCells` / `raisedFillCells` / `raisedFillPrior` through LOCAL
variables initialised to `null`. ExposeData runs once per load phase, so the lists read in
`LoadingVars` are discarded; the `PostLoadInit` pass starts with fresh null locals, clears the
ledger and refills it with nothing.

- Old (`3f5701d45^`, lines ~773-781): the three lists were fields and survived load.
- New: a save made mid-flood reloads with an empty ledger, so on recede the `WaterMovingShallow`
  cells stay forever, raised excavation cells never get their prior fill back, and the
  aftermath / fossil re-cut get an empty wetted list. Scalar state is fine.

Fix: hold the loaded lists in fields (or apply them to the ledger in `LoadingVars`), keep the same
Scribe labels so existing saves still load.

## verify
Fuzz/selftest: a save-load roundtrip of the component mid-flood (or a kernel test of the
ExposeData shim) keeps all three lists. Offline review of ExposeData across all three load modes.

## criteria
After load mid-flood, `ledger.Active`, `RaisedCells`, `RaisedPrior` equal their pre-save contents.
