# ROT_NAVIGATOR_LOG_SITES_1 — Swallowed Navigator part B: landing ping, the dead ship's log, its salvage sites, the campaign carrier tile

Split from `ROT_SWALLOWED_NAVIGATOR_1` (2026-10-03, FOUNDRY builder r14). Part A shipped the core: the per-world
carrier (`RM_WorldComponent_SwallowedCore`, which already counts `pings`), the timed ping (sound, console chirp,
glow, first letter), integrity, ship-weapon damage, the drop/ruin, the facility link and the range stat part.
The parent item's prose (now in `items/closed/ROT_SWALLOWED_NAVIGATOR_1.md`) is the spec for everything below.

## spec (parent spec items 2, 3, 4 and the campaign half of 1)
- Landing ping: add a listener to the existing landing hook `src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_GravshipArrivalLetter.cs` (never a second patch on that method) so a landing on the carrier's map pings at once (part A pings on a 12 h timer only).
- `RM_NavigatorLogDef` (8 hand-written old flight-log entries) + `RM_GameComponent_NavigatorLog`: every N pings (setting, 4) the next entry is read out as a Narrator letter; entries 2/4/6/8 reveal a salvage site through `QuestScriptDef RM_NavigatorSalvageSite` (vanilla item-stash site shape; defended per ban 8). Free tier: vanilla tile finder in travel range; campaign: `fixedTiles` patched with authored Ash'karr tiles.
- The carrier's death stops the log mid-line (letter); written entries and sites stay.
- Campaign carrier: a `UtinniPatches` patch sets `RM_SwallowedCoreExtension.campaignTile` on `RM_Hwelgrue` to the authored Rot tile (owner/BENCH names the tile).
- Settings: pings per entry.

## criteria
- After 4 pings entry count = 1; after 8 = 2 and one `RM_NavigatorSalvageSite` quest is active with a world object on a valid tile.
- Killing the carrier: further pings do not change the entry count.
- Landing on a map with the living carrier: ping count 0 -> 1; with none, 0.
