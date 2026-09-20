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

## spec — the ruling comes first

⛔ **Do not start patching until the owner rules on the direction.** There are two,
and they are not equivalent:

- **(A) Move the content** — repoint every Pyrelands patch at `ZBiome_Grasslands`,
  and replace the donor's weather table rather than appending to it. Cheapest;
  leaves the Pyrelands living inside a donor def named "Grasslands", which is
  also a donor-retirement question.
- **(B) Paint the real def** — put `RM_FE_Pyrelands` onto the world's Pyrelands
  tiles via the bridge, the way every other authored biome was placed, and leave
  the patches where they are. Keeps the def we own; costs a world-edit pass and a
  live look.

🔑 B is the one that matches how the rest of the planet was authored, and it
removes a donor def instead of entrenching one. But it touches the frozen world,
so it is his call, not mine.

⚠️ Either way the two patch files must stop disagreeing about their target — the
6-vs-1 split is how this hid.

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
