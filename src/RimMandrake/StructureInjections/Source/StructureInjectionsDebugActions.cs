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

            int before = map.listerThings.AllThings.Count;
            GenStep_RimplacePlan.ApplyPlan(map, plan, c.x, c.z, path);
            int after = map.listerThings.AllThings.Count;

            Log.Message("[RMInjectDebug] RAN " + path
                + " origin=" + c
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
