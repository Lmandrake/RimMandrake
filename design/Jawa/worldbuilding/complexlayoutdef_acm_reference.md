<!-- status: live -->
# `ComplexLayoutDef` worked reference — decompiled from Ancient Urban Ruins' `ACM_RandomBuildings.dll`

**Filed under `ANCIENT_RUINS_FAMILY_CUT_1`, 2026-09-09**, per the audit's §3
finding that this donor mod's procedural-dungeon mechanism is genuinely
redeemable technique even though its content (mall/loot defs) is cut. This is
NOT a build spec — `dungeons_arc_spec.md` already rules the Assailant/Forsaken
dungeons onto hand-authored **KCSG** templates, a different (static,
template-then-hand-finish) authoring route than the one documented here. This
file exists so the *procedural weighted-room* pattern is not lost when the
donor mod leaves the list — reach for it if a future site wants genuine
per-visit randomization rather than a fixed template.

**Source:** `AncientMarket_Libraray.dll` / `ACM_RandomBuildings.dll` (mod
`xmb.ancienturbanruins.mo`, workshop id 3316062206), decompiled with
`ilspycmd` 8.2.0.7535 from
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3316062206\1.6\Assemblies\ACM_RandomBuildings (1).dll`
(rimsage has no index of workshop-mod assemblies, so this went straight to
decompile). Classes read: `GenStep_RandomAncientComplex`, `LayoutWorkerComplex`
(the mod's own, NOT vanilla's `LayoutWorkerComplex_AncientComplex`),
`ACM_AncientRandomComplex_Loot`, `ACM_RandomSitePartWorker`.

## The mechanism, end to end

1. **`SitePartDef` (`ACM_AncientRandomComplex`) → `GenStepDef`
   (`GenStep_RandomAncientComplex : GenStep_ScattererBestFit`).** At map
   generation the site part carries a `LayoutStructureSketch` in
   `parms.sitePart.parms.ancientLayoutStructureSketch`, pre-built at the
   **quest-offer** step (`ACM_QuestNode_Root_AncientSite` /
   `QuestNode_Root_AncientComplex.QuestSetupComplex`) so the map the player
   sees matches what the quest description promised. If that sketch is
   missing (e.g. quest lost), it falls back to
   `LayoutDefOf.AncientComplex.Worker.GenerateStructureSketch` with a default
   80×80 `StructureGenParams` — i.e. it degrades to vanilla's own Ancient
   Complex generator rather than failing.
2. **`LayoutWorkerComplex : LayoutWorker` (the mod's OWN class, not a vanilla
   override) does the real generation:**
   - `GenerateSketch` calls vanilla's `RoomLayoutGenerator.GenerateRandomLayout`
     directly (the same BaseGen utility vanilla Ancient Complexes and
     Sanguophage vaults use) with a room-count curve keyed on plan area
     (`EntranceCountOverAreaCurve`: 1 entrance per room-tier below 1000 tiles,
     scaling to 4 above 10000) and a `LayoutSketch` subclass overriding
     `GetWallStuff` per room.
   - `Def.threats` (a `List<ComplexThreat>`, each with `def`, `chancePerComplex`,
     `selectionWeight`, `maxPerComplex`, `maxPerRoom`) is resolved in
     `SpawnThreats`: threats are budgeted against `threatPoints` (~200 default,
     0.25–0.35 of the budget per pick — `ThreatPointsFactorRange`), picked by
     weighted random from whichever threats still have budget under BOTH their
     per-complex and per-room caps, then each threat's own
     `ComplexThreatDef.Worker.Resolve()` spawns it (the family's one threat def,
     `HangingPirates`, is a `ComplexThreatWorker_HangingPirates : ComplexThreatWorker`
     — not decompiled in this pass, out of the 1-hour budget).
   - `SpawnThings` places the pre-rolled loot ThingSetMaker output
     (`structureSketch.thingsToSpawn`, filled from
     `parms.sitePart.parms.ancientComplexRewardMaker` — the site's
     `ThingSetMakerDef`) into rooms via `LayoutWorker.FindBestSpawnLocation`,
     with an optional "first discovery" `RectTrigger` + `SignalAction_Message`
     letter per room (`thingDiscoveredMessage`).
   - `PostSpawnStructure` does terrain/roof cleanup (strips the mod's
     `AncientConcrete` terrain back to the map's default under-terrain, removes
     roofs, keeps only one `AM_DownwardStairs`) and stitches an exit door
     through whichever room's rects touch the map edge and can reach it
     (`AddDoorToExternalWall`).
3. **Room *content* variety is entirely data, not code**: the room-type pool
   the audit's §3 quotes (`ACM_HoboRoomLayout`, `ACM_StoreRoomLayout`,
   `ACM_BuildingRoomLayout`, `ACM_BuildingRoomWithNoForkliftLayout`,
   `ACM_ResturantLayout`, `ACM_UnderRoomLayout`, each a `LayoutRoomDef` with a
   weight) is configured entirely in XML and consumed by
   `RoomLayoutGenerator.GenerateRandomLayout` — the C# never special-cases a
   room type by name. Each `LayoutRoomDef` in turn names a
   `SketchResolverDef` (one `.cs` file each in this DLL:
   `ACM_SketchResolver_HoboRoom`, `_StoreRoom`, `_BuildingRoom`,
   `_BuildingRoomWithNoForklift`, `_ACM_Resturant`, `_UnderRoom`,
   `_ContainerRoom`, `_Gallery`) that paints that specific room's furniture —
   these were skimmed, not fully read, for the same budget reason.

## Why this is the reusable part

The **data-driven room-pool + weighted-threat-budget** shape is the piece worth
lifting: a `ComplexLayoutDef` names a *pool of room templates* and a *pool of
threats*, both weighted and capped, and the C# only orchestrates picking and
budget — it never hardcodes what a room contains. That is a genuinely different
axis of reuse from KCSG's fixed-template route (`dungeons_arc_spec.md` §3.5):
KCSG places one hand-authored StructureLayoutDef verbatim; this pattern
re-rolls a fresh room arrangement and threat mix from a shared pool on every
generation, at the cost of the content being generic-looking (which is exactly
what made the family's OWN room content off-theme — the mechanism and the
content are separable, and only the content was Star-Wars-incompatible).

**Not investigated (budget cut here, ~40 min spent):** `ComplexThreatWorker`
base class internals, `SymbolResolver_Main`/`SymbolResolver_OutdoorsDefence`
(the outer-approach symbol stack pushed in `GenerateComplex`), and the six
`ACM_SketchResolver_*` room-painting classes' actual furniture placement logic.
Decompiled source for all of these sits alongside the read files at
`/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/a3c4f7fa-8f6b-48a4-b20e-b02897a38df6/scratchpad/acm_decomp/out_acm/`
(session-scratch, not committed — re-run `ilspycmd` against the same DLL path
above if this needs revisiting before the mod is cut from the list).
