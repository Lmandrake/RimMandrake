## spec
Unmasked 2026-09-08 while live-verifying `WORLD_LINT_WATER_HARDCODE_1` on the real
frozen world (`WORLDMAP_V23_dense_biomes_2026-09-08.rws`). `jawa/world_lint`'s
`landBiomeSubmerged` check dropped from 1135 to 181 once the instrument correctly
stopped flagging the three seas' own water tiles. The 181 remaining are real: land
biomes (sampled — `AridShrubland`, `Desert`, `Wasteland`, `AB_RockyCrags`,
`AB_MycoticJungle`, `ZBiome_Badlands`) at elevation ≤ 0, several at exactly −350
(the seas' own elevation). These tiles are not water biomes, so this is not an
instrument problem — either the world genuinely has land tiles sitting at sea
elevation (a real geography defect, likely from whichever pass placed
`RUT_TheScald`/`RUT_GreySea`/`RUT_TwilightSea` bleeding onto neighboring land
tiles), or `SurfaceTile.elevation` for these specific tiles was never re-set
after a biome repaint that should have also fixed elevation.

## verify
```
PROVE   jawa/world_lint's landBiomeSubmerged examples, full list not just the
        12-row sample; jawa/world_tile_get on a handful to confirm biome +
        elevation directly (don't trust the lint tool's own summary alone)
EXPECT  either a real fix (re-elevate these tiles to match their biome) or a
        finding that this is intentional/pre-existing and not worth touching
        -- check whether any of these 181 tiles are ADJACENT to one of the
        three seas first, since a boundary-bleed hypothesis predicts they
        cluster at sea edges, not scattered randomly
LIES    "the count went from 1135 to 181" is itself not proof anything is
        wrong -- confirm at least a few of the 181 by reading elevation AND
        biome directly before assuming this needs a fix rather than being a
        pre-existing, harmless quirk (e.g. if these tiles are unreachable/
        unplayable regardless of elevation)
```

## criteria
Either the 181 tiles are re-elevated to match real land geography (verified via
a re-run of `jawa/world_lint` showing the count drop further), or the finding is
explicitly ruled harmless/expected by whoever investigates and this item closes
on that documented judgment rather than a fix.
