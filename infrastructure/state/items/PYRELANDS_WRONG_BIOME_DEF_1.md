# PYRELANDS_WRONG_BIOME_DEF_1 — the Pyrelands was built onto a def nobody can reach

## the defect

The Pyrelands is genuinely built. It is built onto **`RM_FE_Pyrelands`**, a
self-contained, *algorithmically placed* BiomeDef — and 🔴 **there is no worldgen
in this project**. The world is hand-authored and frozen, so an
algorithmically-placed def is never painted onto it.

**MEASURED by BENCH 2026-09-20** against `world/ASHKARR_WORLDMAP_tiles.csv`
(21,872 rows, parsed — not scanned):

| biome | tiles |
|---|---:|
| `RM_FE_Pyrelands` | **0** |
| `ZBiome_Grasslands` | 222 |

`ZBiome_Grasslands` — a **More Vanilla Biomes donor def** — is what the player's
Pyrelands tiles actually carry.

And the patches are split between the two. **MEASURED, same day:**

- `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml` targets
  `RM_FE_Pyrelands` **6 times** and `ZBiome_Grasslands` **once** — so the ruled
  14-species roster lands almost entirely on the unreachable def.
- `src/RimUtinni/UtinniPatches/Patches/AshStorms_Pyrelands.xml` targets
  `ZBiome_Grasslands` — but adds a cosmetic ash storm to the donor's **intact**
  weather table rather than replacing it.

## what the player therefore gets

The biome he walks keeps the donor's ordinary grassland behaviour. Reported by
the reconciliation agent and **not yet personally re-verified by BENCH** — treat
as UNCERTAIN until checked:

- no **EmberGrass** fuel bed (flora patch leaves Quickgrass alone on the shipped def)
- no **BlackRain / AshFall / Cinderfall**
- no **ash-terrain ladder** wired onto the shipped def's mapgen
- the donor's **ordinary rain and snow still fire** — which the card's own
  Hard Ban 2 forbids outright
- two of the card's "four igniters" depend on wild animals that never spawn there

✅ The C# layer is **fine**: `src/RimUtinni/PyrelandsMechanics`
(`PYRELANDS_MECHANICS_1`, closed) is biome-aware of BOTH defNames, so the
scripted systems still run. The defect is in the def/patch layer only.

## why this went unseen

Every Pyrelands item passed its own verify, because each checked its own
artifact. Nothing checked **which def the player's tiles carry**. This is the
third gap of this shape found on 2026-09-20 — see `BLUE_DESERT_LIFE_AUTHORING_1`
(commissioned life never built) and `SLIME_GENE_ARCHIVE_BUILD_1` (placeholder
content shipped under a finished-looking mechanic). 🔑 **All three look correct
from inside the mod and wrong from inside the game.**

## spec — RULED 2026-09-20, option B by way of the repaint

Owner, verbatim: *"Correct we will repaint the whole world when all the biomes
are in. You don't need to keep rediscovering this."*

🔑 **So this is not a patch job. The content stays where it is.**
`RM_FE_Pyrelands` is the def we OWN, the patches already target it, and the
world repaint — which happens once every biome is in, as the last act before the
first play session (`WORLD_REMAKE_FINAL_STEP_1`) — is what puts it on the map.

⛔ **Do NOT repoint the Pyrelands patches at `ZBiome_Grasslands`.** That was
option (A) and it is now the wrong move: it would entrench a More Vanilla Biomes
donor def as our fire biome permanently, in the exact opposite direction from the
donor retirement this whole wave is for.

⛔ **Do not re-file this as a defect.** The zero-tile reading is CORRECT and
EXPECTED until the repaint. Anyone measuring `RM_FE_Pyrelands` tiles before then
will get 0 and it means nothing is wrong.

**What IS still owed here**, and it is small:

1. The two patch files must stop disagreeing about their target. `WildAnimals_Pyrelands.xml`
   hits `RM_FE_Pyrelands` 6× and `ZBiome_Grasslands` 1×; `AshStorms_Pyrelands.xml`
   hits only `ZBiome_Grasslands`. Everything Pyrelands should sit on
   `RM_FE_Pyrelands`, so that the repaint delivers a complete biome in one move.
2. Anything currently reaching the player only via `ZBiome_Grasslands` needs to
   exist on `RM_FE_Pyrelands` too, or it will be missing after the repaint.
3. Add the Pyrelands tiles to whatever the repaint pass uses as its source of
   truth, so `RM_FE_Pyrelands` is actually in the paint list.

## verify

Stand on a Pyrelands tile in game and confirm: ember grass underfoot, the ash
weathers firing, the ruled fauna spawning, and **no ordinary rain or snow**.
Then a post-load def dump — not the patch files, which prove nothing about
which def a tile carries.

## Watch out

- ⚠️ The card's §0 counts **63** tiles as Pyrelands; the CSV carries **222**
  `ZBiome_Grasslands`. So that def is probably NOT only the Pyrelands — check
  what else is painted with it before repointing anything, or option (A) will
  drop ash weather onto tiles that should never see it.
- 🔴 `WORLD_REMAKE_FINAL_STEP_1` is relevant: a remake is expected, so do not
  build migration machinery here. Fix the defs; let the remake carry the paint.
