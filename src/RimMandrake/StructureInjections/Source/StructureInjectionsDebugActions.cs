using LudeonTK;
using Verse;

namespace RimMandrake.StructureInjections
{
    // Bridge-reachable proof surface for GenStep_RimplacePlan, mirroring
    // PitDebugActions' pattern (src/RimMandrake/Pits/Source/Debug/). ToolMap
    // actions are reachable from RimBridge by x/z, so this is how a quicktest
    // proves the ordering guarantee (foundation -> terrain -> things
    // transmitters-first -> roof) without a full LandmarkDef/TileMutatorDef
    // wiring pass -- that is content work; this is the engine proof.
    public static class StructureInjectionsDebugActions
    {
        private const string CAT = "RMInject";

        // Absolute path so the debug tool needs no modContentPack/GenStepDef
        // plumbing at all -- it is a standalone proof of ApplyPlan(), not a
        // simulation of the production planFile-resolution path (that path
        // is exercised for real once a promise's TileMutatorDef/GenStepDef
        // wiring exists).
        [DebugAction(CAT, "Run plan: dwelling_test.txt",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void RunDwellingTest()
        {
            RunAt(@"D:\Luke\dev\Rimworld\Transient\dwelling_test.txt");
        }

        [DebugAction(CAT, "Run plan: moisture_farm_test.txt",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void RunMoistureFarmTest()
        {
            RunAt(@"D:\Luke\dev\Rimworld\Transient\moisture_farm_test.txt");
        }

        private static void RunAt(string path)
        {
            Map map = Find.CurrentMap;
            if (map == null) { Log.Message("[RMInjectDebug] NO_MAP"); return; }

            IntVec3 c = UI.MouseCell();
            RimplacePlan plan;
            try
            {
                plan = RimplacePlan.Parse(path);
            }
            catch (System.Exception ex)
            {
                Log.Error("[RMInjectDebug] PARSE_FAILED " + path + ": " + ex);
                return;
            }

            // 🔴 ApplyPlan's dx/dz are an OFFSET ADDED to each plan cell, not an origin.
            // Passing the clicked cell straight through built the structure at
            // click + footprint origin — 100 cells away for any plan whose FOOTPRINT
            // starts at 100,100, which is all of them — while the log below cheerfully
            // printed the cell you clicked. Measured live 2026-09-02: clicked (60,60),
            // built at (160,160), and every verification against (60,60) read as a
            // total failure of a GenStep that had in fact worked perfectly.
            // Subtract the footprint so the plan lands WHERE YOU CLICKED.
            int dx = c.x - (plan.HasFootprint ? plan.FootprintX : 0);
            int dz = c.z - (plan.HasFootprint ? plan.FootprintZ : 0);

            int before = map.listerThings.AllThings.Count;
            GenStep_RimplacePlan.ApplyPlan(map, plan, dx, dz, path);
            int after = map.listerThings.AllThings.Count;

            Log.Message("[RMInjectDebug] RAN " + path
                + " clicked=" + c
                + " offset=(" + dx + "," + dz + ")"
                + " foundationCells=" + plan.Foundation.Count
                + " terrainCells=" + plan.Terrain.Count
                + " things=" + plan.Things.Count
                + " roofCells=" + plan.Roof.Count
                + " thingsBefore=" + before
                + " thingsAfter=" + after
                + " thingsSpawned=" + (after - before));
        }
    }
}
