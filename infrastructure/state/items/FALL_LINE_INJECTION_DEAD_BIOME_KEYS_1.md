# FALL_LINE_INJECTION_DEAD_BIOME_KEYS_1 — fall_line.json injects vermin at dead biome keys

## what is wrong

`design/Jawa/worldbuilding/biomes/rosters/fall_line.json`'s
`injection_layer.defNames` lists `['ExtremeDesert','Desert','AridShrubland']`
— the pre-rename biome defNames, from before the RUT_ tier-prefix migration
(`NAMING_SCHEME_EXECUTION_1`, closed 2026-08-31). The 11-12 vermin/droid rows
this layer injects are therefore invisible to anyone diffing `desert.json`/
`dune_sea_deep_desert.json` against the live defs, because
`rosters_to_cast.py` routes them by these dead keys — the same defect
tracked generically in `ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`.

## why it matters

An entire injection layer of wildlife rows is silently disconnected from the
biomes it is supposed to feed, and any roster diff or audit that doesn't
already know to look for this will conclude the rows simply don't exist.

## the work

Rekey `injection_layer.defNames` to `RUT_ExtremeDesert` / `RUT_Desert` /
`RUT_AridShrubland`, in the **same pass** as
`ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`'s `BIOMECAST_DEFS` rebuild — do not
do this as a separate, uncoordinated edit. Add a one-line pointer in each
desert roster's `law_sources` section back to the injection layer, so future
audits know to look for it.

## Watch out

This is exactly the class of bug the naming-scheme migration's closing note
warns about: a stale pre-rename key surviving quietly in a file nobody
re-checked after the rename. Do this in the same sitting as
`ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`, not before or after it, or the two
fixes can conflict with each other.

## verify

`fall_line.json`'s `injection_layer.defNames` reads `RUT_`-prefixed names;
`rosters_to_cast.py` correctly routes the 11-12 injected rows to both desert
biomes; each desert roster's `law_sources` cites the injection layer.

## criteria

The Fall Line injection layer is visible to anyone auditing the desert
rosters against the live defs.
