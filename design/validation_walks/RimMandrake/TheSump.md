# RimMandrake: the Sump — validation walk
subject: src/RimMandrake/TheSump  (packageId `mandrake.rm.thesump`)
deps: `sarg.alphabiomes` (modDependencies); loadAfter environmentalhazards and flowworks
list: biomes tier; folded into mandrake.rm.biomes
status-hint: THE_SUMP_FIRST_SCRIPT_1 — first script drafted, never run live. TEN FILES ARE HELD FROM DEPLOY (src/DEPLOY_HOLD.txt): flora, fauna, flora items, tar-beast bulge + gen step + 2 patches, moat fuse post, mouse filth, and the BiomeDef.

Sources: `src/RimMandrake/TheSump/About/About.xml`, `Defs/**`, `Patches/**`, `Source/RM_TheSumpMod.cs`.

## must be true
- Every def that actually deploys resolves; a bogus name reads notFound. → defs_resolve.every_deployed_def_resolves
- Held defs are reported, never failed. → defs_resolve.held_defs_are_unmeasured_by_hold (UNMEASURED-by-hold)
- Every Mod Settings field (`biomeRarityFactor`, `tarVaultEnabled`, `deepBlackMereEnabled`) round-trips. → settings_roundtrip.*
- The biome's densities are positive. → biome_wiring.* (UNMEASURED-by-hold: the BiomeDef is held)
- Deep Black mere, tar vault, moat/fuse post, dig lottery, tar beast, mouse trail, wick garden, dusk lock. → map_mechanics.* (UNMEASURED; the vault def lives in UtinniPatches, several others are held)

## the walk
1. [D] `jawa/get_defs` over every deployed def derived from `Defs/**/*.xml` minus the DEPLOY_HOLD globs   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field of `RM_TheSumpSettings`   # settings_roundtrip
3. [B] map-generation and tick mechanics   # map_mechanics (UNMEASURED)

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "held defs missing live are failures" — DEPLOY_HOLD.txt holds them on purpose; they are UNMEASURED-by-hold.
RULED OUT: "a zero-tile biome is a defect" — the planet is painted once at the end (BIOME_PAINT_ONCE_AT_THE_END_1).
