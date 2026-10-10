using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // OLLOPOM_OUTDOOR_BEAUTY — creatures that are pleasant to look at outdoors.
    //
    // MEASURED (RimSage, decompiled 1.6):
    //   Need_Beauty.CurrentInstantBeauty -> BeautyUtility.AverageBeautyPerceptible(pawn.PositionHeld, map),
    //   which averages BeautyUtility.CellBeauty over the ~250 cells within 8.9 of the pawn that are unfogged and in
    //   (or adjacent to) the pawn's own room. CellBeauty skips any Thing whose category fails BeautyRelevant
    //   (Building/Item/Plant/Filth only) — so PAWNS NEVER COUNT, whatever their Beauty stat says.
    //   CellBeauty's own outdoors flag is c.GetRoom(map)?.PsychologicallyOutdoors ?? true.
    //
    // CHANGE: one postfix on BeautyUtility.CellBeauty. For each live pawn on the cell whose race def carries
    // RM_PerceivedBeautyExtension, add its beautyOutdoors when the cell is psychologically outdoors. Dedupes through
    // the caller's countedThings like vanilla. Inert (one empty-set check) when no loaded def carries the extension,
    // or when the setting is off.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_PerceivedBeautyPatches
    {
        private static readonly Dictionary<ThingDef, RM_PerceivedBeautyExtension> byDef = new Dictionary<ThingDef, RM_PerceivedBeautyExtension>();

        static RM_PerceivedBeautyPatches()
        {
            try
            {
                foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    RM_PerceivedBeautyExtension ext = d.GetModExtension<RM_PerceivedBeautyExtension>();
                    if (ext != null) byDef[d] = ext;
                }
                if (byDef.Count == 0) return;   // nothing opts in: do not patch at all
                MethodInfo target = AccessTools.Method(typeof(BeautyUtility), nameof(BeautyUtility.CellBeauty));
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] perceived beauty: BeautyUtility.CellBeauty not found; creatures add no outdoor beauty.");
                    return;
                }
                new Harmony("mandrake.rm.creaturebehaviors.perceivedbeauty")
                    .Patch(target, postfix: new HarmonyMethod(typeof(RM_PerceivedBeautyPatches), nameof(Postfix_CellBeauty)));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] perceived beauty: patch failed; creatures add no outdoor beauty: " + e);
            }
        }

        public static void Postfix_CellBeauty(IntVec3 c, Map map, HashSet<Thing> countedThings, ref float __result)
        {
            if (!RM_CreatureBehaviorsSettings.perceivedBeautyEnabled || map == null) return;
            try
            {
                __result += ContributionAt(c, map, countedThings);
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] perceived beauty: " + e, 0x52504231);
            }
        }

        private static float ContributionAt(IntVec3 c, Map map, HashSet<Thing> countedThings)
        {
            float add = 0f;
            bool? outdoors = null;
            List<Thing> list = map.thingGrid.ThingsListAt(c);
            for (int i = 0; i < list.Count; i++)
            {
                Pawn p = list[i] as Pawn;
                RM_PerceivedBeautyExtension ext;
                if (p == null || !byDef.TryGetValue(p.def, out ext)) continue;
                if (countedThings != null && !countedThings.Add(p)) continue;
                if (outdoors == null) outdoors = c.GetRoom(map)?.PsychologicallyOutdoors ?? true;
                add += RM_PerceivedBeautyMath.Contribution(RM_CreatureBehaviorsSettings.perceivedBeautyEnabled,
                    RM_CreatureBehaviorsSettings.perceivedBeautyMultiplier, ext.beautyOutdoors, p.Dead, outdoors.Value);
            }
            return add;
        }

        /// <summary>Bridge proof (jawa/static_call, arg = a pawn's ThingID on the current map):
        /// "contribution|psychologicallyOutdoors|averagePerceptibleBesideIt". The average is vanilla
        /// AverageBeautyPerceptible from the cell east of the creature, so it INCLUDES this postfix: compare it with
        /// the mechanic on and off. "missing" when no such pawn.</summary>
        public static string Probe(string pawnId)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "missing";
            string id = (pawnId ?? "").Trim();
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.ThingID != id) continue;
                IntVec3 c = p.Position;
                bool outdoors = c.GetRoom(map)?.PsychologicallyOutdoors ?? true;
                float mine = RM_CreatureBehaviorsSettings.perceivedBeautyEnabled ? ContributionAt(c, map, null) : 0f;
                IntVec3 beside = c + IntVec3.East;
                float avg = beside.InBounds(map) ? BeautyUtility.AverageBeautyPerceptible(beside, map) : 0f;
                return mine.ToString("0.###") + "|" + outdoors + "|" + avg.ToString("0.####");
            }
            return "missing";
        }
    }
}
