## spec
✅ **OWNER'S RULING, 2026-08-22 12:52:** jungle *"ABSOLUTELY belongs on a desert world but
only adjacent to steaming evaporating rivers."*

**The dayside map already obeys it exactly.** `AB_FeraliskInfestedJungle`, 534 tiles, 100%
dayside: **222 on a river, 261 one hop out, 51 two hops out, ZERO beyond two hops.**

## 🔑 the question, and it is the owner's alone
**Does that rule also bind the MERIDIAN?** Three biomes sit there and touch no river:

| biome | tiles | at arc > 82 | nearest river |
|---|---|---|---|
| `AB_MycoticJungle` | 1,939 | 1,874 | 3+ hops, all of them |
| `PoisonForest` | 604 | 575 | 3+ hops, all of them |
| `BMT_FungalForest` | 425 | 394 | 3+ hops, all of them |

🔴 **A meridian river cannot exist.** Measured: the highest arc carrying a river anywhere on
the planet is **71.52**, and there are **zero** river tiles at arc > 74. So this is not a
placement failure that could be repaired by moving tiles — the band has no water to sit beside.

⭐ **DECIDE's reading: the rule does NOT bind the meridian, and nothing should move.**
`ASHKARR_WORLD_DEFINITION.md` §5 already distinguishes them — *"Terrestrial foliage belongs
to the Scald; the meridian gets mycoid and poison forest. **Two greens that mean different
things.**"* Mycoid forest is watered by the terminator, not by rivers, and that is why it
reads as a different green.

⛔ **If the owner rules the other way, 2,968 tiles change biome — 14% of the planet.** That is
a large authoring job on the one map and must not be started on an inference.

## what was already fixed
`ASHKARR_WORLD_DEFINITION.md` §5's table put `AB_MycoticJungle` / `PoisonForest` in an
**"on the river / meridian"** cell. That cell describes a place that does not exist, and it
contradicted the section's own closing line. Corrected in place 2026-08-22.

## verify
`world/ASHKARR_WORLDMAP_tiles.csv` + `_links.csv`: no river link or non-zero `river_flow` at
arc > 74; Feralisk tile-hop distribution 222/261/51/0.

## criteria
An owner ruling recorded either way. No tile moves until then.

## watch out
⚠️ **DECIDE first measured this as "93% of jungle violates the ruling" and nearly filed a map
rewrite.** That number came from applying a dayside-river rule to a meridian fungal belt. The
band a biome sits in has to be established before its distance to water means anything.
