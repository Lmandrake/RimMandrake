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

## corrected 2026-09-19 — an earlier claim in this item was FALSE

⛔ This item previously said `RM_FE_Pyrelands` carries "thirteen vanilla Earth
animals and no Star Wars fauna at all." **That was wrong and is deleted**, not
superseded: it was read from the biome DEF file without reading the patch.
`Patches/WildAnimals_Pyrelands.xml` opens with a `PatchOperationReplace` that WIPES
`<wildAnimals>` before anything is added, so not one of those 13 survives to runtime.

MEASURED from the live def dump of the running 621-mod game
(`DefDump/captures/2026-09-19T12-48-16Z`, `BiomeDef.json`), the Pyrelands cast is
exactly 13 records and contains **no vanilla Earth animal**:

`RUT_FireHawk` 0.15 · `RUT_FurnaceBeast` 0.08 · `AA_Razorjack` 0.2 ·
`AA_Barbslinger` 0.15 · `AA_FireWasp` 0.4 · `GR_Boomsnake` **0** ·
`Anooba` 0.35 · `Iriaz` 0.5 · `Nuna` 0.5 · `Orray` 0.25 · `Zeer` 0.6 ·
`Dalgo` 0.18 · `Gizka` 1.0

🔑 **The owner has seen these creatures in a live Pyrelands wearing OUR art, and
that is not a contradiction.** Our `RSW_` ports use the SAME relative texPaths as
the donor defs (`swanimals/Iriaz/Iriaz`, `swanimals/Nuna/Nuna_f`, `swanimals/Zeer/Zeer`,
`swanimals/Dalgo/Dalgo`), and `mandrake.rsw.iriazartoverride` is a loose-`Textures/`
mod that `loadAfter`s both the donor and SWBestiary — so the override art wins the
same-path resolution no matter which def spawns. **Therefore the donor→RSW_ swap at
`62195aaf1` changes no art whatsoever.** What it changes is which def spawns: our
port's own stats, body and leather, and no dependency on the donor mod.

⚠️ `GR_Mantistanis` was never live either way — its `MayRequire="Spino.Megafauna"`
gate excluded it, and that mod is not in the list. Removing it changed nothing at
runtime; it only removed a dangling-key hazard.
