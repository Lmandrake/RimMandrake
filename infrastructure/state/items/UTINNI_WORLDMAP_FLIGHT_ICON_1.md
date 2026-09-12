# UTINNI_WORLDMAP_FLIGHT_ICON_1 — the Utinni's own icon in flight on the world map

Owner, 2026-09-12, at the bench mid-flight: *"Make a ticket to change the graphic of
the Utinni as it flies on the worldmap."*

## Where the graphic comes from (READ AT SOURCE, Odyssey `WorldObjectDefs/WorldObjects.xml`)
`WorldObjectDef Gravship` (`worldObjectClass Gravship`, "A gravship in flight"):
- `<expandingIconTexture>World/WorldObjects/Expanding/Gravship</expandingIconTexture>`
  — the icon you see on the globe (`expandingIcon true`, `expandingIconDrawSize 1.35`,
  `expandingIconPriority 60`, `fullyExpandedInSpace true`).
- `<texture>World/WorldObjects/Caravan</texture>` — the non-expanded/dynamic-drawer
  fallback; patch it too so both zoom regimes show the same ship.
- Also on screen during a flight: `WorldObjectDef GravshipLaunch` uses
  `World/WorldObjects/Expanding/GravshipLaunchSite` for the launch site marker —
  optional second sprite, same pass.

## spec
- Art: a top-down silhouette of THE ship as it is now — the ring hull without booms
  (`design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml`
  is the current shape; its PNG beside it is a reference). Read as a Jawa-built
  Rakatan hulk, not a vanilla shuttle. Two sizes are not needed: the expanding icon
  is drawn at 1.35 and scaled by the engine; author at the vanilla texture's pixel
  size (measure the vanilla PNG in the game's resources — `reading-rimworld-graphics`
  skill — do not guess).
- Delivery: a PatchOperationReplace on both texture fields under our tier
  (`RimUtinni` patch mod), texPath `World/WorldObjects/Expanding/RUT_Utinni` and
  `World/WorldObjects/RUT_UtinniCaravan`. Texture binds by texPath, not defName
  (memory: `texture-binds-by-texpath-not-defname`).
- Mod Settings toggle per the standing rule (`MOD_OPTIONS_RETROFIT_1`): "Utinni
  world-map icon" on/off, default on.

## verify
- Live: launch (or load a flight save — `FLIGHT_hop1_seas_cleaned_2026-09-12.rws` is
  parked mid-hop) and screenshot the globe with the ship in flight; the owner LOOKS.
- Zoomed in and zoomed out both show our sprite (the two fields).

## traps
- The gravship is only a world object DURING flight; on the ground it is a map.
  A quicktest never shows it — you need a launch or a flight save.
- Expanding icons are drawn through `WorldObjectDef.ExpandingIconColor` / faction
  colour tinting in `ExpandableWorldObjectsUtility`; author the sprite so a tint
  doesn't wreck it (read that class before picking colours).
