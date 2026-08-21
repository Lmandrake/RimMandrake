## spec
`LINT_EXCLUDE_LAKE_SUBMERGED_1` (`dbfe46d`) narrows `world_lint`'s `landBiomeSubmerged`
so a `Lake` tile below sea level no longer counts as submerged land. **The change is in
the companion DLL and is NOT deployed** — the game was up when it was written, and the
assembly is locked while it runs. Deploy is already step 1 of the `NEXT_RELOAD.md` §1.0
shutdown manifest: `python.exe src/RimMandrake/bridgetools/build.py --gm --apply`.

⚠️ **Confirm the deployed companion is the one carrying this** before believing any
number below — a stale companion and a working fix look identical from the bridge.

⛔ The risk being checked is that the check was **disabled** rather than **narrowed**.
`Lake` was NOT added to `biomeIsWater`, deliberately: that would flip
`waterBiomeOnRaisedLand` back on for every ordinary high-altitude lake, which is exactly
what the 2026-08-20 fix removed.

## verify
With the frozen CSV imported (`jawa/world_tile_import` … `apply=true`, then
`jawa/world_commit`), on any world carrying the Scald:

    jawa/world_lint  ->  landBiomeSubmerged.count

then force a genuine case and confirm the check still FIRES:

    jawa/world_tile_set  {"tiles":"<a Desert tile>","elevation":-5}
    jawa/world_commit ; jawa/world_lint

## criteria
- `landBiomeSubmerged` reads **0** on Ash'karr with the Scald at −30
- and reads **1** with one Desert tile forced to elevation −5, proving the check was
  narrowed and not disabled
- `lakesAboveSeaLevel` still reads 0, and `waterBiomeOnRaisedLand` still reads 0 —
  neither sibling moved
