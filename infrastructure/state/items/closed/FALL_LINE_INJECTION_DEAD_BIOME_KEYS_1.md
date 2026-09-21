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


---

## 🔴 SUPERSEDED IN PART 2026-09-20 — rekeying is the wrong fix

This item proposed rekeying `injection_layer`'s `defNames` from the dead
`ExtremeDesert` / `Desert` / `AridShrubland` to the live `RUT_*` names.

**The owner has since ruled that these rows do not belong in a biome table under
EITHER key.** Verbatim: *"They are not part of 'the biome' there are simply
events and subregions where you can meet them."* Full ruling:
`design/Jawa/worldbuilding/biomes/fall_line.md` §8a, and
`EXTREME_DESERT_UNRULED_VERMIN_1`.

⛔ **Do not rekey the 15 fauna rows to `RUT_*` and call this done.** That would
carry a mechanism the owner rejected onto correct names, which is worse than the
current state — it would look fixed.

### What survives of this item

- ✅ The **measurement** stands: `defNames` names three biome defs that carry zero
  painted tiles, and `rosters_to_cast.py` routes by those dead names.
- ✅ The finding that the injected rows are **invisible to anyone diffing the
  desert rosters against the defs** stands, and is now more important, not less.
- 🔑 **Re-home the rows first** (that is `EXTREME_DESERT_UNRULED_VERMIN_1`'s
  work). Then rekey only whatever genuinely remains biome-scoped — possibly
  nothing, in which case this item closes with the `defNames` key deleted rather
  than corrected.

⚠️ This item's original fix is still cited by `ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`
as a same-pass job. That pairing is no longer safe — say so there before either
is worked.
