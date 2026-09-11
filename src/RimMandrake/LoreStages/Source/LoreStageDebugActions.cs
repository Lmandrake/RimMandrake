using System.Collections.Generic;
using LudeonTK;
using Verse;

namespace RimMandrake.LoreStages
{
    // Dev-mode entry points. These exist so the in-game proof of this mechanism
    // costs a quicktest and a menu click rather than a scripted reveal gate:
    // open the world tile inspector on a staged biome, set the rung here, and
    // the text must change on the next frame.
    //
    // They are also the only thing a bridge-driven live test needs — no consumer
    // has to exist yet for a ladder to be walked end to end.
    public static class LoreStageDebugActions
    {
        [DebugAction("Lore stages", "Set ladder stage...", allowedGameStates = AllowedGameStates.Playing)]
        private static void SetLadderStage()
        {
            GameComponent_LoreStage comp = GameComponent_LoreStage.Current;
            if (comp == null)
            {
                Log.Warning("[LoreStages] no GameComponent_LoreStage on the current Game.");
                return;
            }

            var ladders = new List<DebugMenuOption>();
            foreach (RM_LoreStageTableDef table in DefDatabase<RM_LoreStageTableDef>.AllDefsListForReading)
            {
                RM_LoreStageTableDef localTable = table;
                string label = $"{localTable.LadderId} (now {comp.GetStage(localTable.LadderId)})";
                ladders.Add(new DebugMenuOption(label, DebugMenuOptionMode.Action, delegate
                {
                    int top = localTable.maxStage > 0 ? localTable.maxStage : 9;
                    var rungs = new List<DebugMenuOption>();
                    for (int i = 0; i <= top; i++)
                    {
                        int localStage = i;
                        rungs.Add(new DebugMenuOption("stage " + localStage, DebugMenuOptionMode.Action, delegate
                        {
                            comp.SetStage(localTable.LadderId, localStage);
                            Log.Message($"[LoreStages] {localTable.LadderId} -> stage {localStage}");
                        }));
                    }

                    Find.WindowStack.Add(new Dialog_DebugOptionListLister(rungs));
                }));
            }

            if (ladders.Count == 0)
            {
                Log.Warning("[LoreStages] no RM_LoreStageTableDef is loaded — nothing to stage.");
                return;
            }

            Find.WindowStack.Add(new Dialog_DebugOptionListLister(ladders));
        }

        // Prints what each staged field currently holds, so a live check does not
        // depend on finding the right tooltip. Reads the CACHED getters on
        // purpose where they exist (ThingDef.DescriptionDetailed,
        // HediffDef.Description): those are the two paths that go stale if the
        // reflection clear ever stops working, so a mismatch here IS the bug.
        [DebugAction("Lore stages", "Log staged fields", allowedGameStates = AllowedGameStates.Playing)]
        private static void LogStagedFields()
        {
            GameComponent_LoreStage comp = GameComponent_LoreStage.Current;
            if (comp == null) return;

            Log.Message("[LoreStages] cache reachability: " + LoreStageApplier.CacheReachabilityReport);

            foreach (RM_LoreStageTableDef table in DefDatabase<RM_LoreStageTableDef>.AllDefsListForReading)
            {
                Log.Message($"[LoreStages] ladder {table.LadderId} at stage {comp.GetStage(table.LadderId)}");
                foreach (LoreStageTarget target in table.targets)
                {
                    Def def = LoreStageDefDatabase.Resolve(target.defType, target.defName);
                    if (def == null)
                    {
                        Log.Message($"  {target.defType} {target.defName}: NOT PRESENT");
                        continue;
                    }

                    System.Reflection.FieldInfo fi = def.GetType().GetField(
                        target.field,
                        System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
                    string raw = fi != null ? fi.GetValue(def) as string : "<no such field>";
                    Log.Message($"  {target.defType} {target.defName}.{target.field} = {raw}");

                    if (def is ThingDef thingDef)
                    {
                        Log.Message($"    DescriptionDetailed (cached path) = {thingDef.DescriptionDetailed}");
                    }

                    if (def is HediffDef hediffDef)
                    {
                        Log.Message($"    Description (cached path) = {hediffDef.Description}");
                    }
                }
            }
        }
    }
}
