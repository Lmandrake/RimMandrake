PW7 graphics audit, GimmeSomeSlack + FlowWorks review maps, 2026-10-15: 277 subjects, 759 slots, 260 pictures resolved, 4 missing (0 plain missing, 4 known art-board fallbacks, 0 deploy-only)

Measured against the DEPLOYED mods in `/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods` in ModsConfig.xml order (23 activeMods, 23 resolved to a folder; later wins). Re-run: `python3 /home/mandrake/rm/bench/Transient/review_graphics_audit_gssfw_20261015/audit.py`.
Subjects = every ThingDef/TerrainDef/ThingStyleDef/StyleCategoryDef (any def with a texture path) in the DEPLOYED Defs of both mods (168 of them named by a station builder; the rest are shown by their style or not at all) plus the C#-built art rows.

## Defects

1. [FALLBACK (art board M, the code draws its fallback)] `art slot: overhead span cable` slot `Scrapper` (GimmeSomeSlack): expected `RimMandrake/GimmeSomeSlack/Aerial/Styles/Scrapper/SpanWire`; found nothing in any active mod
2. [FALLBACK (art board M, the code draws its fallback)] `art slot: overhead span cable` slot `Industrial` (GimmeSomeSlack): expected `RimMandrake/GimmeSomeSlack/Aerial/Styles/Industrial/SpanWire`; found nothing in any active mod
3. [FALLBACK (art board M, the code draws its fallback)] `art slot: overhead span cable` slot `Modern` (GimmeSomeSlack): expected `RimMandrake/GimmeSomeSlack/Aerial/Styles/Modern/SpanWire`; found nothing in any active mod
4. [FALLBACK (art board M, the code draws its fallback)] `art slot: overhead span cable` slot `Futuristic` (GimmeSomeSlack): expected `RimMandrake/GimmeSomeSlack/Aerial/Styles/Futuristic/SpanWire`; found nothing in any active mod
5. [DEPLOY-STALE-DEF] FlowWorks Defs/Machinery/RM_LiquidWorksScatter.xml: bytes differ (the audit read the deployed copy)

## Notes (resolved, with a caveat)

- `RM_HoseReel` slot `graphicData/texPath` `RimMandrake/FlowWorks/Hose/Reel_PumpHookup`: custom graphicClass RimMandrake.FlowWorks.Hose.Graphic_HoseReel: any layout accepted
- `RM_HoseReel_Scrapper` slot `graphicData/texPath` `RimMandrake/FlowWorks/Hose/Reel_PumpHookup`: custom graphicClass RimMandrake.FlowWorks.Hose.Graphic_HoseReel: any layout accepted
- `RM_HoseReel_Industrial` slot `graphicData/texPath` `RimMandrake/FlowWorks/Hose/Styles/Industrial/Reel_PumpHookup`: custom graphicClass RimMandrake.FlowWorks.Hose.Graphic_HoseReel: any layout accepted
- `RM_HoseReel_Modern` slot `graphicData/texPath` `RimMandrake/FlowWorks/Hose/Styles/Modern/Reel_PumpHookup`: custom graphicClass RimMandrake.FlowWorks.Hose.Graphic_HoseReel: any layout accepted
- `RM_HoseReel_Futuristic` slot `graphicData/texPath` `RimMandrake/FlowWorks/Hose/Styles/Futuristic/Reel_PumpHookup`: custom graphicClass RimMandrake.FlowWorks.Hose.Graphic_HoseReel: any layout accepted
- `RM_Filth_Tar` slot `graphicData/texPath` `Things/Filth/RM_FilthTar`: custom graphicClass Graphic_Cluster: any layout accepted

## Orphans (deployed textures no def, style, or traced C# rule references): not defects

GimmeSomeSlack: 1
  - `RimMandrake/GimmeSomeSlack/PowerStrip.png`
FlowWorks: 14
  - `RimMandrake/FlowWorks/Hose/Coupling_Brass.png`
  - `Terrain/Surfaces/RM_FordStones.png`
  - `Things/Building/FlowWorks/Doors/RM_SecurityGrateDoor_MenuIcon.png`
  - `Things/Building/FlowWorks/Doors/RM_SecurityGrateDoor_Mover.png`
  - `Things/Building/FlowWorks/Doors/RM_Sluice_MenuIcon.png`
  - `Things/Building/FlowWorks/Doors/RM_Sluice_Mover.png`
  - `Things/Building/FlowWorks/Excavation/RM_WallFace_North.png`
  - `Things/Building/FlowWorks/Excavation/RM_WallFace_Side.png`
  - `Things/Building/FlowWorks/Machinery/RM_PipeAdapter_Chemfuel.png`
  - `Things/Building/FlowWorks/Machinery/RM_PipeAdapter_Propane.png`
  - `Things/Building/FlowWorks/RM_LiquidPump.png`
  - `Things/Building/FlowWorks/RM_Spikes.png`
  - `Things/Building/FlowWorks/Rivers/RM_FerryRope.png`
  - `Things/Item/Resource/FlowWorks/RM_WaterBottle.png`

Orphan caveat: C# builds more paths than the rule tables above list; each orphan name should be grepped in Source/ before it is called dead.

## UNMEASURED

- Vanilla/Core/DLC textures (354 slots across 131 defs) live in .assets bundles: matched by file name against the extracted bundle index only, otherwise 'vanilla, not checked on disk'.
- Vanilla station subjects (their art is vanilla or patched at runtime by C#; textures not read here): Battery, BlocksGranite, Chicken, Colonist, Cooler, CraftingSpot, ElectricStove, Empty, FirefoamPopper, FlatscreenTelevision, Gravel, Hare, Heater, HiTechResearchBench, Husky, Leather_Plain, Muffalo, Pirate, Plasteel, PowerConduit, PowerSwitch, RoofConstructed, RoofRockThick, Sand, Scrapper, Soil, StandingLamp, Steel, SunLamp, Turret_MiniTurret, WallLamp, WaterDeep, WaterMovingChestDeep, WaterMovingShallow, WaterShallow, WaterproofConduit, WildBoar, WoodLog
- C# paths built from runtime state (settings, per-net colour, tint) are covered only through the rule tables in audit.py; a path the code builds that is not in a table is not seen.
- Other mods' XML patches on our defs: none found by text search. Our own patches touching graphics: FlowWorks/RM_Fluid_Tar_AlphaBiomesAdoption.xml; FlowWorks/RM_PipeNetAdapters.xml.
- Station-to-def matching is by name appearing anywhere in the builder data (both builders imported).
- ParentName not found in Core/DLC/our Defs (a third-party mod's abstract, e.g. Dubs Bad Hygiene ResourceBasedMom): RM_WaterBottle_Rust<-ResourceBasedMom, RM_WaterBottle_Verdigris<-ResourceBasedMom, RM_WaterBottle_Amber<-ResourceBasedMom, RM_WaterBottle_Violet<-ResourceBasedMom, RM_WaterBottle_Chalk<-ResourceBasedMom. Their own graphicData paths WERE checked; anything inherited from the parent was not.
- GATED OFF in the live list (MayRequire donor not in activeMods, def never loads, nothing to draw): 5 slots on RM_WaterBottle_Amber, RM_WaterBottle_Chalk, RM_WaterBottle_Rust, RM_WaterBottle_Verdigris, RM_WaterBottle_Violet; needs `dubwise.dubsbadhygiene.lite,dubwise.dubsbadhygiene`.
- Styles: ThingStyleDef graphics are read from XML. GSS conduit styles are markers with no graphicData by design (ConduitStyles.xml header), so their art is the code rows above.

Fine: 396 of 759 slots resolved to a picture the game will load (260 distinct files, 258 of them mod art on the sheet); 354 vanilla slots not checked on disk.
