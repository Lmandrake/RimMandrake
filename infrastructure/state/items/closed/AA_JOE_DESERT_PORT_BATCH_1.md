# AA_JOE_DESERT_PORT_BATCH_1 — port the remaining round-2 desert imports

## why

`DESERT_ROUND2_IMPORTS_UNLANDED_1` wired the two already-existing defs
(`RSW_Stoneback`, `RSW_TruffleMole`) into `RUT_Desert`/`RUT_ExtremeDesert`. Four
creatures in that same round-2 roster have no def anywhere in `src/` yet and need
porting from scratch; `AA_SandLion` is already tracked separately under
`EXTREME_DESERT_SUBSURFACE_PREDATOR_1` (do not duplicate it here).

## spec

Owner ruling 2026-09-20 (recorded on `DESERT_ROUND2_IMPORTS_UNLANDED_1`): **port
both** `AA_GreatDevourer` and `AA_MatureFleshbeast` (not superseded by
`SARLACC_HABITAT_BUILD_1`). Port `AA_Groundrunner` as well. `JOE_Cephalope` is
ruled "absorb & retire mod" rather than a straight port — absorb its def into our
own tree and retire the JOE donor mod dependency, per the pattern in
`BMT_FAUNA_ABSORPTION_1` (reference closure: retexture patches, biome roster
weights, any tool/patch naming the donor mod).

Port behavior, not donor bugs — check each donor def for known-broken mechanics
before carrying them over verbatim (the standing lesson from `RUT_SCAVENGEREVENTS_BUILD_1`'s
Mo'Events port applies generally: port what works, not what's merely there).

## verify

All four defs (`RSW_`-prefixed per the naming scheme) exist in `src/`, are wired
into whichever biome(s) their roster row specifies at the ruled commonality, and
the JOE donor mod is no longer a dependency anywhere in the active mod list.

## criteria

Every round-2 import the owner approved that isn't already tracked elsewhere
(`EXTREME_DESERT_SUBSURFACE_PREDATOR_1` for `AA_SandLion`) is live in the biome
tables.
