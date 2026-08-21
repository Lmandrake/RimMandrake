## spec
REPORT, carried out of B63 and now measured rather than suspected.
`SeaIce` is in our `biomeBlacklist`, and the blacklist is enforced by AWF's
`GetBiomeScorePrefix` returning false and setting `__result = -1000f`
(`.../3626210061/Source/PlanetTypeManager.cs:108-119`). But the Tidally Locked
mod patches `BiomeWorker_SeaIce.GetScore` with a **Postfix that assigns
unconditionally** — `__result = tile.WaterCovered ? PermaIceScore(tile)-23f : -100f`
(`.../3631364335/Source/PlanetTypeDef.cs:137-141`). A Harmony postfix still runs
when a prefix skipped the original, and AWF's own postfix only `+=`, so it cannot
undo an assignment. ⇒ **the blacklist entry for `SeaIce` does nothing.**
⭐ Consequence is small and bounded: it affects the vanilla substrate only, and
every tile is overwritten by the painted map. Nothing to fix in our files —
the fix would be load order or a patch on another mod's C#, both worse.
🔎 Also chased and NOT reproducing: the `[Def Error]: TidallyLocked … Parsed 0.3
as int` line B63 recorded. No `as int` error in either the current or the
previous `Player.log`, and no `0.3` in the mod's `PlanetTypes.xml`.

## verify
read off both mods' source, above.

## criteria
after the next full load, `SeaIce` tiles on the GENERATED world are cosmetic
only — confirm the painted import overwrites them. If any survives into the
final map, that is a real defect and comes back as a new item.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
