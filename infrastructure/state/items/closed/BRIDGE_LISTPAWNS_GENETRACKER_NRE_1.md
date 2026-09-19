# BRIDGE_LISTPAWNS_GENETRACKER_NRE_1

Found live, 2026-09-03, while verifying `DROIDWORKS_POWEREDDOWN_NOT_WIRED_1` on a
Droidworks-tier quicktest (`mandrake.rsw.droidworks` + `mandrake.rsw.ionweapons` +
Core/Harmony/RimBridge, closed over deps).

## spec

`jawa/list_pawns` throws unconditionally once a pawn with no `Pawn_GeneTracker`
(or one whose xenotype can't resolve) is anywhere on the current map — a droid
race (`RSW_DW_Race_OuterRim_GNKDroid`, spawned with `xenotype: null`,
`xenotypeApplied: true` per `jawa/pawn_get`) reproduces it reliably, with
`includeHealth` true OR at its default:

```
System.NullReferenceException: Object reference not set to an instance of an object
  at RimWorld.Pawn_GeneTracker.get_XenotypeLabel ()
  at JawaBench.BridgeTools.JawaBenchTerrainTools+<>c__DisplayClass309_0.<ListPawns>b__0 ()
```

`jawa/list_pawns` is used by ~everything (censuses, the sea-beast review agent, this
session's own DROIDWORKS work) — a single non-genetic pawn on the map (any droid,
any mechanoid-adjacent race without Biotech genes) makes the whole tool unusable for
the rest of that map, with no workaround short of not calling it.

## verify

Reproduce with a minimal case (spawn one droid, call `jawa/list_pawns`, confirm the
NRE), then null-guard `XenotypeLabel` access in `ListPawns` — likely check
`pawn.genes != null` before reading `XenotypeLabel`, or wrap the read in a try/catch
per-pawn so one bad pawn doesn't take down the whole list (matches this file's own
established pattern elsewhere per `BRIDGE_TERRAINTOOLS_REMAINING_FINDINGS_1`'s fixes).

## criteria

`jawa/list_pawns` (any `includeHealth` value) succeeds on a map containing a
non-genetic pawn, and still reports every other pawn's data correctly.
