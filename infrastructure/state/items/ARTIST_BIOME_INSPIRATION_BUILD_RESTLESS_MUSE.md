## spec
Build `RimMandrake/ArtistMuse` (packageId `mandrake.rimmandrake.artistmuse`, namespace `RimMandrake.ArtistMuse`,
prefix `RM_`) as designed in `design/RimMandrake/artist_biome_inspiration_design.md`: Restless mode by default and
Fixed mode as a setting. The section "Independent judge's verdict", fixes 1-6, binds. Ruling: a delegated design
call on `ARTIST_BIOME_INSPIRATION_MOD_1` (2026-11-03).

## criteria
- An offline quality sweep covers every base 0-5, inspired or not, role offset -1..+1, and each mode. With the mod
  off the output is identical to vanilla, the caps hold, and an existing Legendary is never lowered.
- Pool tests: the muse and stale biomes are never picked, each stale biome expires on its own timer, and an empty
  pool gives a null muse with a retry rather than a throw.
- A save round-trip keeps the muse, the stale dict and the cooldown; toggling the mod or the mode freezes state and
  never resets it.
- Mod Settings match the doc's table, and every setting turned off gives vanilla.
- The mod ships with its first functional script.
- Live L2: on a quicktest map of biome X with the muse forced to X, a sculpture comes out shifted, then the muse
  rerolls to a biome other than X and the letter fires.
