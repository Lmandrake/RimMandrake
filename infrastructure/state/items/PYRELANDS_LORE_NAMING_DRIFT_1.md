# PYRELANDS_LORE_NAMING_DRIFT_1

## spec
Found by PYRELANDS_SELF_CONTAINED_BIOME_1's closing agent (2026-09-09), out of that
item's scope: `design/Jawa/worldbuilding/biomes/the_pyrelands.md` still names the
biome's defs/namespace as `RSW_FE_*`, but the shipped biome
(`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml` etc., commits `2b29b3cb`,
`339aba05`, `a3e5ba3d`) is RM-tier: `RM_FE_Pyrelands`. Per the naming scheme
(`design/NAMING_SCHEME_PLAN.md`), Pyrelands is a base-game biome mechanic, correctly
RM-tier — the doc is stale, not the defs.

## verify
Grep `the_pyrelands.md` for every `RSW_FE_` occurrence and confirm each corresponding
def in `src/RimMandrake/Pyrelands/` actually carries the `RM_FE_` prefix before
changing the doc — don't rename defs to match a stale doc.

## criteria
`the_pyrelands.md` names only prefixes that exist in the shipped defs; no other
content changes.
