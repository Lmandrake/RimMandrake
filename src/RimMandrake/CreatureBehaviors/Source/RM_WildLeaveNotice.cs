using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_CREATURES_VANISH_1 — "no animal or pawn ever vanishes without a
    // readable sign" (owner, 2026-09-29/30, CLAUDE.md "One kind of heat").
    //
    // Found 2026-10-07: four Chill creatures spawned on a temperate debug map
    // disappeared with no corpse. Cause (from decompiled 1.6 source): vanilla's
    // Animal think tree runs LeaveIfWrongSeason for every wild animal —
    // ThinkNode_ConditionalAnimalWrongSeason is !SeasonAcceptableFor(race), and
    // the Chill's natives are comfortable only between -150 and -30 C, so on any
    // ordinary map they walk to the edge (JobGiver_ExitMapRandom) and ExitMap.
    // That migration is intended vanilla behaviour and is KEPT; what was wrong is
    // that it was silent, and these creatures are drawn at 0.25-0.45 cells, so
    // the walk to the edge is invisible.
    //
    // Prefix on Pawn.ExitMap: a wild animal leaving a map the player is on, for a
    // temperature or starvation reason, posts one message per species per map per
    // in-game hour naming the reason. Random 60-day wanders are not announced
    // (the animal is seen walking off in the ordinary way).
    // Toggle: RM_CreatureBehaviorsSettings.wildLeaveNoticeEnabled.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_WildLeaveNotice
    {
        public const int WindowTicks = 2500;

        private static readonly Dictionary<long, int> lastNotified = new Dictionary<long, int>();

        static RM_WildLeaveNotice()
        {
            try
            {
                var target = AccessTools.Method(typeof(Pawn), nameof(Pawn.ExitMap), new[] { typeof(bool), typeof(Rot4) });
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] wild-leave notice: Pawn.ExitMap not found; notice is off.");
                    return;
                }
                new Harmony("mandrake.rm.creaturebehaviors.wildleave")
                    .Patch(target, prefix: new HarmonyMethod(typeof(RM_WildLeaveNotice), nameof(Prefix_ExitMap)));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] wild-leave notice patch failed: " + e);
            }
        }

        public static void Prefix_ExitMap(Pawn __instance)
        {
            try
            {
                if (!RM_CreatureBehaviorsSettings.wildLeaveNoticeEnabled) return;
                Pawn p = __instance;
                if (p == null || !p.Spawned || p.Faction != null || p.RaceProps == null || !p.RaceProps.Animal) return;
                Map map = p.Map;
                if (map == null || !(map.IsPlayerHome || map.mapPawns.AnyColonistSpawned)) return;

                ThingDef race = p.def;
                FloatRange safe = p.SafeTemperatureRange();
                bool starving = p.needs?.food != null && p.needs.food.Starving;
                RM_WildLeaveReason why = RM_WildLeaveMath.Classify(
                    map.mapTemperature.SeasonalTemp,
                    race.GetStatValueAbstract(StatDefOf.ComfyTemperatureMin),
                    race.GetStatValueAbstract(StatDefOf.ComfyTemperatureMax),
                    p.AmbientTemperature, safe.min, safe.max, starving);
                if (why == RM_WildLeaveReason.None) return;

                long key = ((long)map.uniqueID << 32) ^ (uint)race.shortHash;
                int now = Find.TickManager.TicksGame;
                int last = lastNotified.TryGetValue(key, out int l) ? l : -1;
                if (!RM_WildLeaveMath.ShouldNotify(now, last, WindowTicks)) return;
                lastNotified[key] = now;

                string text;
                if (why == RM_WildLeaveReason.Starving)
                {
                    text = "RM_WildLeave_Starving".Translate(p.LabelIndefinite().CapitalizeFirst());
                }
                else
                {
                    string comfy = race.GetStatValueAbstract(StatDefOf.ComfyTemperatureMin).ToStringTemperature("F0")
                        + " .. " + race.GetStatValueAbstract(StatDefOf.ComfyTemperatureMax).ToStringTemperature("F0");
                    text = (why == RM_WildLeaveReason.TooWarm ? "RM_WildLeave_TooWarm" : "RM_WildLeave_TooCold")
                        .Translate(p.LabelIndefinite().CapitalizeFirst(), comfy);
                }
                Messages.Message(text, new TargetInfo(p.Position, map), MessageTypeDefOf.NeutralEvent, historical: true);
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] wild-leave notice: " + e, 0x52574C4E);
            }
        }
    }
}
