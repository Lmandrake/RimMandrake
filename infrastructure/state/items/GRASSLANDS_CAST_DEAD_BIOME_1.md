# GRASSLANDS_CAST_DEAD_BIOME_1

## spec

`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` casts eight creatures
into `ZBiome_Grasslands` across 4 PatchOperations. That biome carries **ZERO tiles
on the frozen world** — MEASURED at `f7e2bd21c` via `jawa/world_tile_export` over
all 21872 surface tiles, against 222 `RM_FE_Pyrelands` tiles.

So none of these eight can ever spawn in the campaign:

| def | weight | note in the file |
|---|---|---|
| `RSW_Iriaz` | 0.5 | iriaz — small-herd, import |
| `RSW_Nuna` | 0.5 | nuna — small, adjust-keep |
| `RSW_Anooba` | 0.35 | anooba — medium-predator, import |
| `RSW_Zeer` | 0.6 | zeer — large-herd, adjust-keep |
| `Nuna` | 0.5 | nuna — small, adjust-keep (the donor def, beside RSW_Nuna) |
| `RSW_Gizka` | 0.3 | gizka — grain, adjust-keep |
| `RSW_Orray` | 0.25 | orray — medium, import |
| `AA_FireWasp` | 0.4 | fire wasp — small-predator, keep |

This is the same dead-def class `f7e2bd21c` fixed for river-steam and
subsurface-liquid wiring. That sweep fixed two mechanisms and **did not touch the
fauna cast**, which is why these survived. `RUT_Emberscythe` was the ninth and is
already corrected (`e41749a52`) on the owner's ruling *"YES for Pyrelands and no
elsewhere."*

## why this needs the owner

⛔ Do not retarget these eight on inference. Emberscythe had an unambiguous home —
its own description names the Pyrelands. These do not: Iriaz, Nuna, Zeer and Gizka
are open-country herbivores with several plausible Ash'karr biomes, and picking one
is a cast decision, not a repair.

🔑 Ask him which biome each belongs in, or whether some were only ever meant for a
biome the frozen world does not carry and should simply be dropped.

⚠️ Worth showing him at the same time: `RM_FE_Pyrelands`'s own `<wildAnimals>` is
**thirteen vanilla Earth animals** (Hare, Rat, Gazelle, Ostrich, Emu, Dromedary,
Muffalo, Iguana, Elephant, Rhinoceros, Cougar, Fox_Fennec, Warg) and no Star Wars
fauna at all — which sits oddly against his standing "terrestrial, not wanted" call
on creature art.

## verify

`validate_patch.py <the file> --live <dump> --defs <Data> --defs <workshop> --defs <Mods>`
must report a non-zero match count for every retargeted operation. A
`PatchOperationConditional` returns true on no match, so a zero-match retarget is
silent — the match count is the only proof.
