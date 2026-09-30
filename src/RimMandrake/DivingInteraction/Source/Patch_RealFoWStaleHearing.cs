using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // REALFOW_POCKET_MAP_COMPAT_1, 2026-09-30. Compatibility with the
    // third-party Real Fog of War (packageId Mlie.NWNRealFogOfWar, assembly
    // rimworld-mod-real-fow.dll, namespace RimWorldRealFoW).
    //
    // The defect (donor-side, read from the installed 1.6 assembly with
    // ilspycmd): CompFieldOfViewWatcher keeps a private List<Pawn> nearByPawn
    // of pawns within hearing range, refreshed every 200 ticks. Its
    // PostSpawnSetup re-points mapCompSeenFog at the NEW map but never clears
    // that list. Every 100 ticks livePawnHear calls
    // mapCompSeenFog.IsShown(faction, item.Position) for each moving
    // non-faction pawn in the list, and IsShown indexes
    // shownCells[z * mapSizeX + x] with no bounds check. So a colonist who
    // walks from the home map into a smaller map (our sea-floor pocket map,
    // Anomaly's undercave, anything) indexes the new map's grid with pawns
    // still standing on the OLD one. It throws IndexOutOfRangeException
    // before the list refresh can run, and the refresh's exact-equality tick
    // check then never fires again, so it throws every 100 ticks for the rest
    // of the visit.
    //
    // The fix is at the root: before each hearing pass, drop every cached pawn
    // that is not on the listening pawn's own current map. That covers both
    // cases (the listener changed map, or a heard pawn left). The list is a
    // fresh List<Pawn> built per refresh by MapUtils.GetPawnsAround, so
    // editing it in place touches no shared state.
    //
    // Prepare() returns false when Real FoW is not loaded, and Harmony's
    // PatchAll then skips this class entirely, so without Real FoW it does
    // nothing at all.
    // ════════════════════════════════════════════════════════════════════
    [HarmonyPatch]
    public static class Patch_RealFoWStaleHearing
    {
        private const string WatcherTypeName = "RimWorldRealFoW.CompFieldOfViewWatcher";

        private static MethodBase target;
        private static FieldInfo nearByPawnField;
        private static FieldInfo pawnField;

        private static bool Prepare()
        {
            Type watcher = AccessTools.TypeByName(WatcherTypeName);
            if (watcher == null)
                return false;

            MethodInfo hear = AccessTools.Method(watcher, "livePawnHear");
            FieldInfo nearBy = AccessTools.Field(watcher, "nearByPawn");
            FieldInfo pawn = AccessTools.Field(watcher, "pawn");
            if (hear == null || nearBy == null || pawn == null
                || nearBy.FieldType != typeof(List<Pawn>) || pawn.FieldType != typeof(Pawn))
            {
                Log.Warning("[RM DivingInteraction] Real Fog of War is loaded but "
                    + WatcherTypeName + " no longer has the members this compatibility "
                    + "patch expects (livePawnHear / nearByPawn / pawn). Patch skipped.");
                return false;
            }

            target = hear;
            nearByPawnField = nearBy;
            pawnField = pawn;
            return true;
        }

        private static MethodBase TargetMethod() => target;

        // Runs once per colonist per 100 ticks, only when Real FoW's hearing
        // pass does, so plain reflection reads cost nothing measurable.

        private static void Prefix(object __instance)
        {
            if (!RM_DivingSettings.realFowCompatEnabled)
                return;

            List<Pawn> heard = (List<Pawn>)nearByPawnField.GetValue(__instance);
            if (heard == null || heard.Count == 0)
                return;

            Map map = ((Pawn)pawnField.GetValue(__instance))?.Map;
            if (map == null)
            {
                heard.Clear();
                return;
            }
            heard.RemoveAll(p => p == null || p.Map != map);
        }
    }
}
