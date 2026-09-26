# GREENTIDE_DENSITY_SETTINGS_1 — Mod Settings sliders for the Greentide's density/movement tuning

Follow-on from `GREENTIDE_BIOME_DENSITY_1` (closed 2026-09-26). That item tuned
`RM_Greentide_Biome.xml`'s `plantDensity` (0.99) and `movementDifficulty` (4,
world-tile) against vanilla's own `TropicalSwamp` precedent — see its closed
prose for the full mechanism writeup (`infrastructure/state/items/closed/GREENTIDE_BIOME_DENSITY_1.md`).

## what this owes

Per the standing every-mod-ships-settings rule (`MOD_OPTIONS_RETROFIT_1` and CLAUDE.md's "Every
mod ships superb Mod Settings"): `plantDensity` and `movementDifficulty` are exactly the "a number
is the experience" case that rule names for a tuning slider, and both are now set at or near the
most extreme value found on any vanilla BiomeDef — an extreme default needs an escape hatch for a
player who finds the biome literally unplayable.

## spec

1. Add (or extend, if `mandrake.rm.greentide` already has a settings class) a `Mod_GreentideSettings`
   with sliders for `plantDensity` and `movementDifficulty`, defaulting to the shipped values
   (0.99 / 4), read by `RM_Greentide`'s `BiomeDef` at the point those fields are consumed — check
   whether `BiomeDef` fields can be live-patched from settings (likely a Harmony postfix on the
   getter, or a settings-driven `DefModExtension`, since `BiomeDef` itself has no settings hook) —
   UNMEASURED, confirm the mechanism before authoring rather than guessing a patch shape.
2. All-off (or slider at minimum) should degrade to roughly vanilla `TropicalRainforest` levels
   (`plantDensity 0.9`, `movementDifficulty 2`), not to zero — this is a jungle, not a plain.
3. Label the movementDifficulty slider honestly as affecting world-map/caravan travel speed across
   the biome's tiles, not in-map crossing (per the parent item's own correction) so a player is not
   confused about what the number does.

## verify

The settings screen shows both sliders, changing them changes `RM_Greentide`'s live generation
density and world-tile travel cost, and the shipped defaults reproduce today's tuned values.

## criteria

A player who finds the Greentide too dense or too slow to cross on the world map can turn it down
without editing XML, and the honest default stays exactly as intimidating as the ruling asked for.
