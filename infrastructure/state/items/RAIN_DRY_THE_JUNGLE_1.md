## spec
🔴 **OWNER, 2026-08-21: option (a) — apply the rain ban as ruled.** `rain_mm = 0` on every
tile below `hilliness` 4, with no biome exempted.

**What was actually executed was option (b), and nobody recorded it as a choice.** Measured
today from `world/ASHKARR_WORLDMAP_tiles.csv`: **363 tiles** still carry `rain_mm > 0` at
`hilliness < 4`, and **every single one of them is `AB_FeraliskInfestedJungle`** — 121 of
them at the 1668 mm ceiling. `RAIN_BAN_SCOPE_1` offered sparing that biome as option (b);
the edit that ran spared it. The owner has now picked (a).

**Set `rain_mm = 0` on those 363 rows** in `world/ASHKARR_WORLDMAP_tiles.csv`. Selector,
verbatim: `rain_mm > 0 AND hilliness < 4`. Their spread, so a wrong join is visible:
hilliness 1 → 187, hilliness 2 → 78, hilliness 3 → 98. By region: The Dune Sea 120,
unnamed 95, The Dew Belt 76, The Scald Spine 33, The Dew Horn 23, The Anvil 16.

⛔ **Touch nothing at `hilliness >= 4`** — 1,396 tiles keep their rain and that is the
ruling, not an oversight.
✅ **It repaints nothing he can see** — `rain_mm` is not rendered on the world map. The
design already holds that the Feralisk jungles are fed by **rivers, not sky**, so drying
them costs the fiction nothing.
⚠️ The planet is frozen against the painter (`31f4047`). This is a direct edit to the one
map, not a re-run — see `frozen-artifacts` before reaching for a generator.

## verify
- Re-measure the same selector: `rain_mm > 0 AND hilliness < 4` returns **0** rows.
- `rain_mm > 0 AND hilliness >= 4` still returns **1396**.
- `canon.yml > world.rain_mm` `max` changes from **1668** and its `rain_src` is updated with
  the new measurement and the owner's ruling. ⚠️ A `PreToolUse` hook blocks any design-doc
  commit that contradicts canon, so canon moves in the same commit or the next one fails.

## criteria
None live. This is offline paint; CHECK owes nothing.
