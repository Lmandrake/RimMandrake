# Middenshell build report (WASTELAND_MIDDENSHELL_FOOTPRINT_1)

Owner ruling, verbatim 2026-09-30: *"Yes it can make 20 wide. Just do it."* Built at 20.

## Spec (read from)
- `WASTELAND_MECHANICS_BUILD_1` §1 + BENCH note 2026-09-29 (tentacle pulls objects in, eats
  them; never gravplating / ship walls / inherent gravship items).
- `design/Jawa/worldbuilding/biomes/wasteland_survivor_cast_2026-09-28.md` §4: never hostile,
  proximity dose aura, walk is the danger (destruction wake), corpse = permanent bezoar quarry
  (`RM_ContaminantBezoar` + rarer `RM_VitrifiedBezoar`), one per map at most, never `<wildAnimals>`.

## Mechanism + precedent (RimSage, decompiled 1.6)
- **Why not a pawn:** a pawn occupies one cell; the TitanicCreatures engine gets multi-cell
  bodies from Large Pawns, whose `GetSize` has no branch above 4
  (`design/Jawa/worldbuilding/research/large_pawns_decompile_2026-09-09.md` §2). That ceiling is
  Large Pawns', not RimWorld's.
- **What does 20:** a `Building` subclass with `<size>(20,20)</size>`. `GenSpawn.Spawn` takes
  `GenAdj.OccupiedRect(loc, rot, def.Size)` with no size cap; `ThingDef.ConfigErrors` has no size
  check. Largest vanilla single-Thing footprint: Ideology's 11x11 (`Buildings_Special.xml`).
- **How it walks:** the Odyssey gravship precedent — `GravshipUtility` relocates multi-cell
  buildings by `DeSpawn(DestroyMode.WillReplace)` + `GenSpawn.Spawn` at the new cell. The
  Middenshell does that one cell per step (default 400 ticks), after crushing its leading edge.
  `GenSpawn.Spawn` itself calls `pawn.pather.TryRecoverFromUnwalkablePosition` for any pawn left
  in an impassable rect, so pawns get shoved out by the engine.
- **Smooth draw:** `Thing.DrawPos` is virtual (Anomaly's `VoidMonolithPyramid` overrides it);
  `drawerType RealtimeOnly` + a lerp from the previous cell. Culling reads `OccupiedDrawRect()`,
  so a 20x20 body is culled by its whole rect.
- **Fog:** `fillPercent` below 1 so it is not a fog blocker (`ThingDef.MakeFog` = Fillage Full),
  plus `seeThroughFog`, so its interior cells never fog and the dynamic drawer never culls it.

## Build (mod `src/RimMandrake/Wasteland`, `mandrake.rm.wasteland`)
- `Source/RM_Middenshell.cs` (new, `<Compile Include>` added): `Building_Middenshell`
  (crawl, destruction wake, tentacle grab, smooth DrawPos, inspect string reports
  `Footprint: WxH`), `RM_MiddenshellExtension` (tuning), `RM_IncidentWorker_MiddenshellArrives`,
  `RM_MapComponent_MiddenshellCarcass` (dose while mining the quarry), `RM_MiddenshellSeamMarker`.
- `Defs/ThingDefs_Buildings/RM_Middenshell.xml`: `RM_Middenshell` **size (20,20)**, 30000 HP,
  Impassable, never claimable/deconstructible, aura = `RM_CompAmbientDose` radius 8 from the
  body edge; carcass seams `RM_MiddenshellSeam` (-> `RM_ContaminantBezoar`) and
  `RM_MiddenshellVitrifiedSeam` (12% of cells, -> `RM_VitrifiedBezoar`), laid as an ellipse
  along its last heading.
- `Defs/IncidentDefs/RM_MiddenshellArrives.xml`: Misc, `allowedBiomes` RM_Wasteland (and the
  worker re-checks the biome), refused while one is alive on the map, `minRefireDays` 20; it
  crawls in from a map edge where the whole 20x20 body fits.
- `RM_CompAmbientDose` now measures distance from the source's `OccupiedRect` edge (identical
  for a 1-cell pawn; required for a 20-wide source).
- Mod Settings: "The Middenshell" (default ON), "Middenshell tentacle grabs" (default ON),
  crawl speed slider (default one cell per 400 ticks).
- Blockers it turns from: map margin, gravship substructure, natural/resource rock, thick
  (mountain) roof, impassable terrain, indestructible things. Tentacle never takes pawns,
  plants, anything on substructure, `Building_GravEngine`, or anything with
  `CompGravshipFacility`/`CompSubstructureFootprint`.
- Not ridden on TitanicCreatures (that engine's footprint IS Large Pawns' 4x4); no dependency added.

## Art
- WIRED: the owner's tubeworm regen `RM_Middenshell_v2_{north,east,south}` (artpipe, validated
  pass, 512 RGBA, from `D:\Luke\dev\Rimworld\infrastructure\artpipe\_artsrc\RM_Middenshell_v2_*`)
  copied to `src\RimMandrake\Wasteland\Textures\Things\Building\RM_Middenshell\RM_Middenshell_{north,east,south}.png`,
  `Graphic_Multi`, drawSize 22. No decisions file rules on it; no job queued. Nothing BLOCKED.
- Carcass seams reuse the vanilla `RockFlecked_Atlas` retinted (same as the brine deposits).

## Verification
- `dotnet build` of `RM_Wasteland.csproj`: 0 warnings, 0 errors; DLL + `.srchash` rebuilt.
- XML parse: both new def files + csproj OK.
- `run_selftests.py`: 77/79, 1 unmeasured (bridge metadata, needs Windows), 1 FAIL
  `selftest_deployed_biome_refs.py` — deployed `RUT_TheRot.xml` rows gated on
  `mandrake.rut.rotsporekit`; unrelated to this change (no Wasteland/Middenshell row).
- NOT live-tested (no game/bridge by brief). Proof script for the coordinator:
  `python.exe src\RimMandrake\bridgetools\prove_middenshell.py` (after deploying Wasteland)
  — makes an RM_Wasteland map, fires the incident (falls back to a direct spawn if
  `jawa/fire_incident` is compiled out), reads the footprint from the inspect string, steps
  2500 ticks, and PASSes only on biome RM_Wasteland + 20x20 before and after + moved.
- Unverified until that runs: the crawl's region-rebuild cost at 400-tick steps on a full list,
  and how the square footprint reads under the long east/west sprite.
