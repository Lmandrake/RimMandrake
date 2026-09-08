# DesertFixtures — validation walk
subject: src/RimUtinni/DesertFixtures
packageId: mandrake.rut.desertfixtures  (from About.xml, verbatim)
deps: none (only Ludeon.RimWorld in modDependencies+loadAfter)
list: minimal
status-hint: One real, player-buildable, stuffable wall-slot window (`RUT_WindowAdobe`, `ParentName="Wall"`) — the only wall-slot window in the mod stack with a `designationCategory`, i.e. the only one actually buildable rather than ruin-scatter decoration.

## must be true
- `RUT_WindowAdobe` (ThingDef, ParentName="Wall") inherits Wall's real wall mechanics (isWall, isPlaceOverableWall, holdsRoof, `terrainAffordanceNeeded=Heavy`, `designationCategory=Structure` — none of these are overridden in this file, so the buildable-wall behavior comes entirely from inheritance).
- `blockLight=false` is set explicitly, overriding Wall's own light-blocking — this is what makes it read as a window rather than a wall in disguise.
- `stuffCategories` is replaced with `Inherit="False"` to exactly `{Stony, Metallic}` — Wall's own `Woody` category must NOT be selectable for this window (the file's own comment: "vanilla Wall itself also allows Woody, which this window deliberately excludes").
- `Beauty=2` statBase is added on top of Wall's inherited stats (MaxHitPoints/WorkToBuild/SellPriceFactor/Mass are untouched, per the file's comment).
- Its texture file exists on disk at the declared texPath and is a real, non-placeholder PNG (this mod is not using AIPersonaCore or any other stand-in).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.desertfixtures" and no XML error naming RUT_DesertFixtures_Buildings.xml
2. [D] def read-back: ThingDef RUT_WindowAdobe; designationCategory = Structure, terrainAffordanceNeeded = Heavy, isWall = true (confirms the inherited wall mechanics actually resolved, not just declared in the parent)
3. [D] def read-back: ThingDef RUT_WindowAdobe; blockLight = false
4. [D] def read-back: ThingDef RUT_WindowAdobe; stuffCategories = [Stony, Metallic] exactly (Woody absent — the Inherit="False" reset took effect rather than appending to Wall's list)
5. [D] def read-back: ThingDef RUT_WindowAdobe; statBases.Beauty = 2
6. [B] jawa/blueprint_place def=RUT_WindowAdobe x=X z=Z stuff=BlocksGranite → accepted (not refused as BuildableByPlayer=false), blueprint spawns
7. [B] jawa/build_batch ops='RUT_WindowAdobe:X,Z' stuff=Steel faction=player → finished window spawns with the Metallic stuff category accepted
8. [B] jawa/list_things defName=RUT_WindowAdobe → confirms the placed window is present on the map
9. [B] jawa/inspect_string thingIds=<window id> → inspect text present and does not read as broken/blocked
X. [S] (human pass) confirm RUT_WindowAdobe.png actually reads as an adobe-style window in the wall line, not a stretched/misaligned single-frame texture (Graphic_Single, no directional atlas, so it will not blend edges with neighboring wall tiles — a deliberate scope cut per About.xml, worth eyeballing once)
