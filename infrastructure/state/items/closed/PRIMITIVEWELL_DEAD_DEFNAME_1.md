
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

## DROPPED 2026-09-26 -- premise was false

`PrimitiveWell` IS a real, resolvable defName -- shipped by `Dubs Bad Hygiene
Lite` (`dubwise.dubsbadhygiene.lite`, `Defs/ThingDefs_Buildings/
BuildingsB_Hygiene.xml`, present unchanged in every 1.3-1.6 version folder).
That mod **is active** in the owner's live `ModsConfig.xml`
(`activeMods` includes `dubwise.dubsbadhygiene.lite`, confirmed directly, not
via a scan of `ModsConfig.xml` line-counting). No active mod patches or
removes it.

The "zero hits ... across the entire live Mods folder" check that filed this
item only searched this repo's own deployed `Mods` folder
(`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, 164 entries --
our own mods only) plus the DLC `Data/{Core,...}` trees. It never searched
`steamapps\workshop\content\294100\`, where every third-party Steam-
subscribed mod actually lives -- including Dubs Bad Hygiene Lite. Same trap
CLAUDE.md already documents for "is there a mod that does X": scan BOTH
roots. RimSage's own index also missed it (its own def index does not cover
this mod either), which the original check took as corroboration rather than
a second instance of the same gap.

This was already known and audited correctly *before* this item existed:
`infrastructure/state/items/TILE_STRUCTURE_DESIGNS_1.md` (line ~160,
"defNames confirmed: `PrimitiveWell` (Dubs Bad Hygiene Lite)") and
`design/Jawa/worldbuilding/desert_world_design.md` (line ~169,
"SOURCE-CONFIRMED (DBH-Lite `1.6/` defs audited...)") both independently
verified this defName against the real DBH Lite XML. `cistern.lua`'s own
header comment says the same thing and names the exact file
(`BuildingsB_Hygiene.xml`). Three independent sources agreed it was real;
this item is the first and only one that said otherwise, and it did so
without checking the workshop root.

**What IS real, from this investigation:** none of the three mods that ship
these templates (`StructureInjections`, `StructureInjectionsRUT`,
`StructureInjectionsSW`) declare `dubwise.dubsbadhygiene.lite` as a
`<modDependencies>` entry, so the dependency is real but undeclared --
harmless today (it's active in the owner's full list) but silently fragile,
and it's why `StructureInjections`' own minimal modcheck tier (which never
pulls in DBH Lite) measured `thingsSpawned=92` against an assumed floor of
93. Corrected in `src/RimMandrake/StructureInjections/validation.py` by
folding it into the floor the same way the suite already handles the
Armoury-only KotOR vaporators (both are real cross-mod content, neither
resolves in this suite's deliberately minimal closure).

No template or `.txt` plan needed changing -- `PrimitiveWell` was always the
correct defName.
