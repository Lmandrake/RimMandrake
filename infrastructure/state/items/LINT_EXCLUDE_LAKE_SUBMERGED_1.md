# LINT_EXCLUDE_LAKE_SUBMERGED_1 — a Lake below its own shoreline is a lake, not submerged land

## spec

`jawa/world_lint`'s `landBiomeSubmerged` check reports **312 findings** on Ash'karr — every
one of them the Scald, `Lake` at elevation `-30.0` (tiles 86, 146, 202, 204, 205, 382, …).
A lake below its own shoreline is the definition of a lake.

**The line, and it is one line:**
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWorldTools.cs:2385`

    bool biomeIsWater = b.defName == "Ocean" || b.defName == "SeaIce";
    if (b.defName == "Lake" && t.elevation > 0f) lakesAboveSeaLevelN++;      // 2386
    if (biomeIsWater && t.elevation > 0f)  { wbolN++;  … }                   // 2387
    if (!biomeIsWater && t.elevation <= 0f) { lbsN++;  … }                   // 2392

`Lake` is deliberately absent from `biomeIsWater`, so line 2392's `!biomeIsWater` sweeps
every submerged Lake tile into `landBiomeSubmerged`.

🔑 **This is the same 312 tiles, and the same author, half-fixed.** The comment directly
above 2385 records the fix going the OTHER way — *"2026-08-20 after it produced 312
findings on the Ash'karr import, exactly the CSV's Lake count. A lake at positive elevation
is ordinary geography… Lakes are counted separately below and do NOT score."* That reasoning
was applied to `waterBiomeOnRaisedLand` and to `lakesAboveSeaLevel`, and never to
`landBiomeSubmerged`. Sinking the Scald simply moved the 312 from the check that scores
zero into the check that scores.

⇒ Exclude `Lake` from `landBiomeSubmerged` as well. Do NOT add `Lake` to `biomeIsWater` —
that flips `waterBiomeOnRaisedLand` back on for every ordinary high-altitude lake, which is
exactly what 2026-08-20 fixed. The narrow change is the right one.

⚠️ Companion change ⇒ needs the game DOWN to deploy. Batch it.

## verify

With the frozen CSV imported (`jawa/world_tile_import` … `apply=true`, then
`jawa/world_commit`), on any world carrying the Scald:

    jawa/world_lint  ->  landBiomeSubmerged.count

and confirm the check still FIRES for a genuine case — set one land tile submerged and see
it counted:

    jawa/world_tile_set  {"tiles":"<a Desert tile>","elevation":-5}
    jawa/world_commit ; jawa/world_lint

## criteria

- `landBiomeSubmerged` reads **0** on Ash'karr with the Scald at −30
- and reads **1** with one Desert tile forced to elevation −5, proving the check was
  narrowed and not disabled
- `lakesAboveSeaLevel` still reads 0, and `waterBiomeOnRaisedLand` still reads 0 —
  neither sibling moved

## notes

Filed by CHECK 2026-08-21 from `LINT_COUNTS_LAKE_AS_LAND_1`, off
`THE_SCALD_LOST_ITS_WATER_1/run-1@full-583`.
Evidence: `observed/bridge/THE_SCALD_LOST_ITS_WATER_1_2026-08-21.md`.
Until this lands, `landBiomeSubmerged: 312` on Ash'karr is EXPECTED and is not a fault.
