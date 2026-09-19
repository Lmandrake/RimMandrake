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

## ruling (owner, 2026-09-19)

> "Zeer, Nuna, Gizka, Orray and Firewasp are all legitimate occupants of the
> Pyrelands. They should be using OUR creatures, not the donor references. The
> donor references, if any, should never be used again. The Gizka can spawn in
> several places natively, including Pyrelands."

DONE at `0757cefca` — the four dead operations deleted, `RSW_Zeer` / `RSW_Nuna` /
`RSW_Gizka` / `RSW_Orray` added to `RM_FE_Pyrelands`, live-validated at 1 match
each. The bare donor `<Nuna>` is gone, and the `mlie.starwarsanimalcollection`
gate went with it — all six defs live in SWBestiary, so a donor gate could only
ever have dropped our own creatures.

⛔ The replaced block WIPED its target's `<wildAnimals>` before adding. That wipe
was deliberately NOT carried across: `RM_FE_Pyrelands` ships 13 animals of its own
and clearing them has never been ruled.

## still open — two things the ruling did not cover

1. **`AA_FireWasp` — no creature of ours exists.** The ruling names Firewasp as a
   legitimate Pyrelands occupant AND forbids donor references. We have no
   `RSW_`/`RUT_` firewasp: `grep` across `src/` returns the donor `AA_FireWasp`
   only. So it was NOT carried into the Pyrelands cast — adding it would have
   broken the ruling it was meant to satisfy. Owed: author our own firewasp, then
   cast it at the donor's old weight (0.4).

2. **`RSW_Iriaz` and `RSW_Anooba` were not named** and are therefore not cast
   anywhere — they were deleted along with the dead grasslands block, which is
   where they already were doing nothing. Both are ours, in SWBestiary.
   🔑 The anooba is the stronger candidate of the two: `RUT_Emberscythe`'s own
   description reads *"A second flame-edge hunter beside the anooba — where the
   anooba runs its prey down, the emberscythe waits in the ash and takes it in one
   cut"*, which places it in the Pyrelands in our own prose. That is evidence, not
   a ruling — do not cast either on it.

## also worth his eye

`RM_FE_Pyrelands`'s own `<wildAnimals>` is thirteen vanilla Earth animals — hare,
rat, gazelle, ostrich, emu, dromedary, muffalo, iguana, elephant, rhinoceros,
cougar, fennec fox, warg — and no Star Wars fauna at all, which sits oddly against
the standing "terrestrial, not wanted" call on creature art.
