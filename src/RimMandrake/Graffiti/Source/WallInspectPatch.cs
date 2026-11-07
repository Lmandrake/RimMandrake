using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace RimMandrake.Graffiti
{
    // A mark isn't selectable (it's filth, on the floor cell its painter stood on), but it's drawn on the wall. So click the wall: its
    // inspect pane says what's painted on it, by whom, about whom, and how it landed.
    [StaticConstructorOnStartup]
    public static class WallInspectPatch
    {
        static WallInspectPatch()
        {
            new Harmony("mandrake.rm.graffiti.wallinspect").Patch(
                AccessTools.Method(typeof(ThingWithComps), nameof(ThingWithComps.GetInspectString)),
                postfix: new HarmonyMethod(typeof(WallInspectPatch), nameof(Postfix)));
        }

        public static void Postfix(ThingWithComps __instance, ref string __result)
        {
            if (!(__instance is Building wall) || !wall.Spawned || !GraffitiJobUtility.IsPaintableWall(wall.def)) return;
            var seen = new List<Filth_Mark>();
            foreach (int side in new[] { 0, 1, 3 })
            {
                foreach (Filth_Mark m in Filth_Mark.MarksOverlapping(wall.Position, side, 0.5f, wall.Map, null))
                {
                    if (!seen.Contains(m)) seen.Add(m);
                }
            }
            foreach (Filth_Mark m in seen)
            {
                float beauty = m.NetBeauty;
                string line = m.StoryLines() + ". Beauty " + beauty.ToString("+0;-0;0") + ": " + RM_GraffitiKernel.BeautyWord(beauty);
                __result = __result.NullOrEmpty() ? line : __result + "\n" + line;
            }
        }
    }
}
