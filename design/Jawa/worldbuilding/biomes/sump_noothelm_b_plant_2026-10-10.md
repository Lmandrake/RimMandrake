# Sump plant from "noothelm B" art — SUMP_NOOTHELM_B_PLANT_1 (2026-10-10)

Owner, Twilight sheet, render "noothelm B" (south, sha 610a8fe0): *"keep art (b) for a new plant in the Sump. It's pretty. Make something new with Star Wars cuisine implications."*

## Art
The B render is artpipe job `RM_NoothelmPlant_south` (single 256x256 RGBA, sha 610a8fe01edf…), a clump of dark arching stalks hanging glowing amber pods. Only a south view exists; plants draw one facing, so it ships as a `Graphic_Single` (same as RM_Tolleth). Installed via `art.py install … --reason artpipe-collect` at `src/RimMandrake/TheSump/Textures/Things/Plant/RM_Lanneth/RM_Lanneth.png`. The A render (`twilightsea_noothelm_redo_v1`) stays with the Twilight noothelm.

## Where the Sump lives
`src/RimMandrake/TheSump` (About packageId `mandrake.rm.thesump`), a composed member of `mandrake.rm.biomes` (Biomes.compose.json wave 0 <= compose_wave 2). Live ModsConfig (parsed 2026-10-10, 565 active): `mandrake.rm.biomes` ACTIVE, `mandrake.rsw.cuisine` ACTIVE, `mandrake.rm.thesump` not listed (folded, as expected). Flora: `Defs/ThingDefs_Plants/RM_SumpFlora.xml` (9 chemotrophs; header bans: no sunlight dependence, no plant emits light).

## Existing cuisine chain
`mandrake.rsw.cuisine` (`src/RimStarWars/Cuisine`) is the one Star Wars cuisine mod: wave 1 is campfire skewers. `RSW_CookFruitOnAStick`/`…4` take an explicit fruit list (RawBerries, RawAgave, VCE_Fruit); the veg/blended skewers disallow those same fruits. Precedent for biome ingredients: GreySalt cures and RSW_MarshFungus, both MayRequire-guarded from the Cuisine side.

## The plant
**Lanneth** (`RM_Lanneth`), RM tier, invented. Wild only (no sowTags), chemotroph posture identical to siblings, no glower (ban: the pods are *painted* luminous wax, not a light). Harvest: `RM_RawLanneth` "lanneth pods", 6 per plant, RawTasty fruit, rot 12 d. Sump wildPlants commonality 0.06 (rare, like dorvel/pallick). Fits the biome text's "low waxy plants that glow faintly where the Junker stations keep their lamp-gardens": the Sump's one sweet thing. Cuisine: Cuisine's fruit skewers accept it and the veg/blended skewers exclude it, by `<li MayRequire="mandrake.rm.biomes">` (no hard dependency either way). No canon dish is claimed, so nothing in the RM tier names Star Wars IP. Numbers INVENTED-BUILD.

## Canon checks
Wookieepedia search API (`list=search`), 2026-10-10: sanity probe `dewback` gave 10 results with title hits; `lanneth` gave **0** results, so the name is free. Repo collision grep for `lanneth`: 0. No canon ingredient or dish claimed.

## Built
`src/RimMandrake/TheSump/Defs/ThingDefs_Plants/RM_Lanneth.xml` (plant + pods), the Sump BiomeDef wildPlants row, `src/RimStarWars/Cuisine/Defs/RecipeDefs_Cuisine.xml` (8 filter lines), and a TheSump `validation.py` static check (defined, sprite, roster row, fruit-skewer hook). Deployed: Cuisine plus `--compose biomes` (lanneth files written; 7 unrelated DLLs locked by the running game). Not live-verified: the next cold load, and the owner's next Sump look.
