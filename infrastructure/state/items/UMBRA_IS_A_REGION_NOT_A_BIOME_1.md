# UMBRA_IS_A_REGION_NOT_A_BIOME_1 — Umbra is a region, not a biome

## the ask

🔴 **Owner ruling, 2026-09-21 (BENCH question card), verbatim:**

> *"Umbra is a region not a biome. The Propane Lake is an ocean-biome made of propane,
> definitely its own biome."*

`RUT_Umbra` ships today as a `BiomeDef` and `design/RimMandrake/biome_mod_architecture.md`
listed it as biome row 24 sharing a mod with the Propane Lake. Both are now wrong. Umbra is
the antistellar cap — a named REGION of the planet, in the same class as the Dune Sea and
Sootreach, not a biome a tile can be.

## spec

1. Umbra leaves the biome row list (§2 of the architecture spec is already corrected).
2. Decide, and say in this item, what happens to the tiles `RUT_Umbra` carries: they need a
   real biome underneath the region. `the_propane_lakes.md` defines the cap's energy regime
   (fuel snow, ammonia flats, aurora) — that regime is either an existing biome or a new one,
   and this item is where that is settled.
3. Umbra becomes a named world region alongside the other 10, matching their convention.
   🔑 **No leading "The "** — he ruled 2026-09-21 that region names carry no article.
4. Retire the `RUT_Umbra` BiomeDef only once its tiles have somewhere to go.

## Watch out

- ⛔ **Do not cite a tile count as evidence about what is or is not built.** The planet is
  painted once at the end; the 2531 figure in the architecture spec is a pre-ruling reading
  and is not an instrument for this work.
- ⚠️ `ashkarr_paint.py`'s region literals were corrected by `ASHKARR_PAINTER_NAMES_DIVERGED_1`.
  If Umbra is added as a region, add it there in the corrected (no-article) form.

## criteria

`RUT_Umbra` no longer exists as a `BiomeDef`, its tiles carry a real biome, and Umbra is a
named region of the planet in the same form as the other ten.
