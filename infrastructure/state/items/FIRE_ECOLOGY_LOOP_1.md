# FIRE_ECOLOGY_LOOP_1 — the self-igniting savanna, v1 slice

Green-lit slice of `design/Jawa/proposals/fire_ecology_deep_design.md` (owner,
2026-09-01). The rest of that doc (creatures, pyroconvective cell, Tribes burn
behavior) awaits PROPOSAL_SUITE_REVIEW_1 — build ONLY the v1 ladder.

## spec

Per the doc's §1 Stage 0, §3, §4, §6:
1. **The loop**: strip rain from the Pyrelands biome's `baseWeatherCommonalities`,
   crank `DryThunderstorm`; freak regrowth stands (already lore-ruled R-H3/R-H4).
   Pure XML weather-table patch.
2. **Black Rain**: an ash-storm WeatherDef that follows and extinguishes any
   sufficiently large burn; converts accumulated ash to fast-clearing slurry.
3. **Ash-accumulation ladder**: trace→light→heavy→deep terrain overlay states
   left by burns (doc §3) — a walkable, legible aftermath.
4. **Scorch-fruit**: harvest window opens only during/immediately after fire
   (doc §4) — the reason to walk INTO the burn.
5. **Fulgurites**: lightning strikes spawn fire-glass prop/item (the one light
   C# hook: strike-spawns-prop; the weather doc's v2 reuses this same hook).
6. **Firefoam sprayer + layable firebreak line** (doc §6) — the player's answer.

Tier RimStarWars/RimUtinni per NAMING_SCHEME_PLAN; all numbers from the doc,
deviations noted in this file.

## verify

Quicktest on a Pyrelands map: (a) no rain event over an accelerated multi-day
run, dry thunderstorms occur, a burn self-seeds at least once; (b) a large burn
triggers Black Rain and the fire dies; (c) ash states visible and clearing;
(d) scorch-fruit unharvestable cold / harvestable in the window; (e) a strike
leaves a fulgurite; (f) firebreak line stops a front. Player.log clean of patch
failures; validate_patch on every patch before deploy.

## criteria

The loop OBSERVED end-to-end in one quicktest session (ignite→burn→Black
Rain→ash→regrowth) plus one deliberate player walk-in harvesting scorch-fruit
under fire risk. No creature content, no C# beyond the strike-spawns-prop hook.

## Watch out

- A patch that matches nothing logs nothing — weather-table xpath must be
  verified against the RESOLVED dump (post-RR), and the Pyrelands biome def
  may inherit weather from a parent: check inheritance before patching the
  child (inherited `<li>` cannot be patched away — see memory).
- `wildAnimalScariaChance` and regrowth interactions with PLANTS_VISIBLE_GROWTH_1
  scope — do not double-implement regrowth.
- Fire spread constants are GLOBAL (FireUtility) — tune via biome/terrain
  flammability, never by patching global fire tick values, or every map burns.
