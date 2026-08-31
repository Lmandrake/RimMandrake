using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StructureInjections
{
    // Replays a rimplace BuildPlan (compiled to the flat text format by
    // rimplace.plan.compile_flat, src/RimMandrake/Utils/rimplace/plan.py) onto
    // a freshly generated map. This is the mapgen-time twin of rimplace's LIVE
    // path (rimplace.plan.compile_calls -> jawa/set_terrain_batch / build_batch
    // / set_roof_batch over the bridge) -- same plan, same ordering, different
    // executor: direct engine calls instead of bridge round-trips, because
    // there is no running client to call back into during mapgen.
    //
    // Order mirrors compile_calls() exactly, because that order is not a
    // style choice -- it is what the live path proved necessary:
    //   foundation -> terrain -> things (transmitters before connectors,
    //   or a power network spawns dead) -> roof.
    // Paint and floor colour are best-effort and NOT part of the ordering
    // proof this class exists to make; see the TODO below.
    public class GenStep_RimplacePlan : GenStep
    {
        // Path to the compiled .txt plan, relative to THIS DEF'S owning mod's
        // root folder, e.g. "Templates/moisture_farm.txt". Ordinary XML-to-
        // field binding on the GenStepDef -- confirmed against
        // GenStep_ScatterThings' filthDef/filthExpandBy/filthChance pattern.
        public string planFile;

        // Where the plan's own (x,z) origin lands on the real map. Plans are
        // authored at small, arbitrary offline coordinates (rimplace's own
        // render defaults to rect "0,0,w,h"), so by default this GenStep
        // centers the plan's footprint on the map. Set false and supply
        // offsetX/offsetZ for placement logic driven by the caller instead
        // (e.g. a landmark-specific rect).
        public bool centerOnMap = true;
        public int offsetX;
        public int offsetZ;

        public override int SeedPart => 8462013; // arbitrary, stable, distinct from vanilla gensteps

        public override void Generate(Map map, GenStepParams parms)
        {
            if (string.IsNullOrEmpty(planFile))
            {
                Log.Error("[RimMandrake.StructureInjections] GenStep_RimplacePlan on " +
                          def.defName + " has no planFile.");
                return;
            }

            var modRoot = def.modContentPack?.RootDir;
            if (string.IsNullOrEmpty(modRoot))
            {
                Log.Error("[RimMandrake.StructureInjections] GenStepDef " + def.defName +
                          " has no owning modContentPack; cannot resolve planFile.");
                return;
            }
            var path = Path.Combine(modRoot, planFile);
            if (!File.Exists(path))
            {
                Log.Error("[RimMandrake.StructureInjections] plan file not found: " + path);
                return;
            }

            RimplacePlan plan;
            try
            {
                plan = RimplacePlan.Parse(path);
            }
            catch (System.Exception ex)
            {
                Log.Error("[RimMandrake.StructureInjections] failed to parse " + path +
                          ": " + ex);
                return;
            }

            int dx = offsetX, dz = offsetZ;
            if (centerOnMap && plan.HasFootprint)
            {
                var mapCenter = map.Center;
                var planCenterX = plan.FootprintX + plan.FootprintW / 2;
                var planCenterZ = plan.FootprintZ + plan.FootprintH / 2;
                dx = mapCenter.x - planCenterX + offsetX;
                dz = mapCenter.z - planCenterZ + offsetZ;
            }

            ApplyPlan(map, plan, dx, dz, planFile ?? "(debug)");
        }

        // Shared by Generate() (production path, driven off a GenStepDef's
        // planFile field) and the debug action (StructureInjectionsDebugActions,
        // which parses a plan itself and calls straight in) so both exercise
        // the identical ordering logic -- there is exactly one implementation
        // of "what does replaying a plan mean", proven live from either entry
        // point.
        public static void ApplyPlan(Map map, RimplacePlan plan, int dx, int dz, string sourceLabel)
        {
            // 1. foundation (Odyssey substructure) -- must exist before terrain
            foreach (var c in plan.Foundation)
                SetTerrainCell(map, c, dx, dz, foundation: true);

            // 2. terrain -- floors under things
            foreach (var c in plan.Terrain)
                SetTerrainCell(map, c, dx, dz, foundation: false);

            // 3. things, transmitters first: a connector (cooler, most
            // machines) binds to the nearest transmitter within
            // ConnectMaxDist AT SPAWN; a transmitter appearing afterwards
            // does not retroactively claim it (same trap compile_calls'
            // comment documents for the live path).
            var byPriority = plan.Things
                .Select(t => new { t, def2 = DefDatabase<ThingDef>.GetNamedSilentFail(t.DefName) })
                .Where(x =>
                {
                    if (x.def2 == null)
                    {
                        Log.Error("[RimMandrake.StructureInjections] no ThingDef '" +
                                  x.t.DefName + "' (plan " + sourceLabel + ")");
                        return false;
                    }
                    return true;
                })
                .OrderByDescending(x => x.def2.EverTransmitsPower);

            foreach (var x in byPriority)
                SpawnThing(map, x.t, x.def2, dx, dz);

            // 4. roof -- last: a roof over a wall that does not exist yet is
            // an unsupported span (WALLS CREATE NO ROOF is the live path's
            // own warning, and the ordering constraint is identical here).
            foreach (var c in plan.Roof)
                SetRoofCell(map, c, dx, dz);

            // TODO(paint/floor colour): the live path applies these AFTER
            // things exist via jawa/paint_building and jawa/set_terrain_layer
            // (CompColorable + a PaintColorDef -> Color lookup). Not
            // implemented here yet -- no roster row's promise depends on it
            // for v1, and it does not touch the ordering this class exists
            // to prove. Left as a known gap, not silently dropped.
        }

        private static void SetTerrainCell(Map map, PlanCell c, int dx, int dz, bool foundation)
        {
            var cell = new IntVec3(c.X + dx, 0, c.Z + dz);
            if (!cell.InBounds(map)) { LogOOB(cell, c.DefName); return; }
            var td = DefDatabase<TerrainDef>.GetNamedSilentFail(c.DefName);
            if (td == null)
            {
                Log.Error("[RimMandrake.StructureInjections] no TerrainDef '" + c.DefName + "'");
                return;
            }
            if (foundation)
                map.terrainGrid.SetFoundation(cell, td);
            else
                map.terrainGrid.SetTerrain(cell, td);
        }

        private static void SetRoofCell(Map map, PlanCell c, int dx, int dz)
        {
            var cell = new IntVec3(c.X + dx, 0, c.Z + dz);
            if (!cell.InBounds(map)) { LogOOB(cell, c.DefName); return; }
            var rd = DefDatabase<RoofDef>.GetNamedSilentFail(c.DefName);
            if (rd == null)
            {
                Log.Error("[RimMandrake.StructureInjections] no RoofDef '" + c.DefName + "'");
                return;
            }
            map.roofGrid.SetRoof(cell, rd);
        }

        private static void SpawnThing(Map map, PlanThing t, ThingDef td, int dx, int dz)
        {
            var cell = new IntVec3(t.X + dx, 0, t.Z + dz);
            if (!cell.InBounds(map)) { LogOOB(cell, t.DefName); return; }

            ThingDef stuffDef = null;
            if (t.Stuff != null)
            {
                stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(t.Stuff);
                if (stuffDef == null)
                    Log.Error("[RimMandrake.StructureInjections] no stuff ThingDef '" +
                              t.Stuff + "' for " + t.DefName + " -- spawning unstuffed.");
            }

            var thing = ThingMaker.MakeThing(td, td.MadeFromStuff ? stuffDef : null);
            var rot = new Rot4(t.Rot);
            GenSpawn.Spawn(thing, cell, map, rot, WipeMode.Vanish);
        }

        private static void LogOOB(IntVec3 cell, string defName)
        {
            Log.Warning("[RimMandrake.StructureInjections] " + defName +
                        " at " + cell + " is outside the generated map; skipped.");
        }
    }
}
