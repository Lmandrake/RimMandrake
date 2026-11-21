using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>RIMMANDRAKE_BLOCK_SLACK_ROOF_OVER_POLE_KEEP_THE_CUT (his walk of 2026-11-20, row 14): "You shouldn't be able to build a power
    /// pole inside a roofed building at all, they're too big... but nice test if you ever did, you can leave the behavior in the code,
    /// just disable building it that way." PlaceWorker_NotUnderRoof refuses a pole under a roof that stands at placement; these refuse a
    /// roof that would come later over a standing pole: the build-roof designator (with a message naming the pole) and every write of
    /// the build-roof area (vanilla's auto-roof of a closed room writes it directly, AutoBuildRoofAreaSetter.TryGenerateAreaNow; the
    /// roof work giver reads only that area). A roof that still comes (a debug action, a collapse, another mod) cuts the spans as before
    /// (RM_MapComponent_Aerial, verdict Roofed). The wall bracket hangs on a wall and is outside this.</summary>
    public static class RoofOverMast
    {
        public const string Refusal = "No roof over a {0}: it stands too tall for a roof.";

        /// <summary>The standing (not wall-hung) aerial anchor on a cell, or null.</summary>
        public static Thing MastAt(Map map, IntVec3 c)
        {
            if (map == null || !c.InBounds(map)) return null;
            var list = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < list.Count; i++)
            {
                Thing t = list[i];
                if (CompAerialAnchor.Of(t) != null && !(t.def.building?.isAttachment ?? false)) return t;
            }
            return null;
        }

        /// <summary>A standing pole clears the build-roof mark of its own cell (an area painted before the pole was built).</summary>
        public static void ClearUnder(Thing pole)
        {
            Map map = pole?.Map;
            if (!AerialSettings.enabled || map?.areaManager?.BuildRoof == null || (pole.def.building?.isAttachment ?? false)) return;
            if (map.areaManager.BuildRoof[pole.Position]) map.areaManager.BuildRoof[pole.Position] = false;
        }
    }

    [HarmonyPatch(typeof(Designator_AreaBuildRoof), nameof(Designator_AreaBuildRoof.CanDesignateCell))]
    [RimMandrake.Shared.PatchFeature("Aerial lines: no roof over a pole", typeof(AerialSettings), "enabled")]
    internal static class Patch_BuildRoofDesignator_RefuseOverMast
    {
        private static void Postfix(IntVec3 c, ref AcceptanceReport __result)
        {
            if (!__result.Accepted || !AerialSettings.enabled) return;
            Thing mast = RoofOverMast.MastAt(Find.CurrentMap, c);
            if (mast != null) __result = new AcceptanceReport(string.Format(RoofOverMast.Refusal, mast.LabelNoCount));
        }
    }

    [HarmonyPatch(typeof(Area), "Set")]
    [RimMandrake.Shared.PatchFeature("Aerial lines: no roof over a pole", typeof(AerialSettings), "enabled")]
    internal static class Patch_AreaBuildRoof_RefuseOverMast
    {
        private static bool Prefix(Area __instance, IntVec3 c, bool val)
        {
            if (!val || !AerialSettings.enabled || !(__instance is Area_BuildRoof)) return true;
            return RoofOverMast.MastAt(__instance.Map, c) == null;
        }
    }
}
