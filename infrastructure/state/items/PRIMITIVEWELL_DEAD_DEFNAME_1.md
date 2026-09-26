
## spec
`THING PrimitiveWell` appears in 4 `design/Jawa/templates/*.lua` source templates
(`cistern.lua`, `moisture_farm.lua`, `oasis_shrine.lua`, `trading_post.lua`) and
their compiled `.txt` plans, which ship in at least 8 installed locations
(MEASURED via `grep -rl PrimitiveWell` over the LIVE Mods folder, not a src-only
search): `Inhabited/Templates/hutt_cistern_court.txt`,
`Inhabited/Templates/deepwater_cistern_hall.txt`,
`StructureInjections/Templates/moisture_farm_test.txt`,
`StructureInjectionsRUT/Templates/{cistern,homestead_compound,
moisture_cistern_head,moisture_walled_compound,oasis_shrine}.txt`,
`StructureInjectionsSW/Templates/moisture_farm.txt`.

`PrimitiveWell` is not a real defName anywhere: zero hits for it (or
case-insensitively) in any `Defs/*.xml` across the entire live Mods folder AND
`Data/{Core,Biotech,Ideology,Royalty,Anomaly,Odyssey}` (checked directly against
the installed game tree, not RimSage's index, which also returned zero). No
existing ThingDef's defName even contains "well". So every `GenStep_
RimplacePlan`/`RimplacePlan` replay of any of these 8 templates has ALWAYS
silently dropped this one THING line -- `DefDatabase<ThingDef>.
GetNamedSilentFail` returns null, `SpawnThing`'s caller logs one
`Log.Error("no ThingDef 'PrimitiveWell'")` and skips it, forever, in every
game that has ever generated one of these scenes. This has nothing to do with
mod-list size or a minimal modcheck environment -- it fails identically with
every DLC and every mod active.

Found via `MODCHECK_SUITE_CORRECTIONS_1`: `StructureInjections`' suite
(`src/RimMandrake/StructureInjections/validation.py`,
`replay_moisture_farm_plan`) asserts `thingsSpawned >= 93` (99 plan things
minus the 6 Armoury-only `KotOR_MoistureVaporator_big` lines a minimal run
can't resolve) and measured 92 live 2026-09-13 -- one short of even that
floor. The extra shortfall is this defect, not a suite miscalculation: 93
assumed every non-KotOR line resolves, and `PrimitiveWell` never does,
regardless of environment.

## verify
Pick a real substitute ThingDef (or author `PrimitiveWell` for real, art
included, if a bespoke well prop is actually wanted) and re-bake all 4 Lua
templates -> all 8 `.txt` plans. Re-run `StructureInjections`' modcheck suite
and confirm `moisture_farm_plan_replays` reaches the corrected exact floor
(93, once this line resolves) with a real placed Thing at that cell, not just
a higher net count.

## criteria
No shipped plan template names a defName that resolves nowhere in the game.
