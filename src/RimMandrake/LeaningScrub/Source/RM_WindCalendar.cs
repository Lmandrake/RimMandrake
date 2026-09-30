using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 1 — the Stall and the Gale.
    //
    // The two WeatherDefs (Defs/WeatherDefs/RM_LeaningScrub_Weather.xml) do the
    // wind itself through vanilla fields (windSpeedFactor / windSpeedOffset,
    // read by WindManager.WindManagerTick). Everything below keys off the
    // map's CURRENT weather being one of those defs, so the effects follow the
    // weather wherever it runs — a biome kit, not a biome lock.
    //
    // Seams, all read from the decompiled 1.6 source (RimSage), none guessed:
    //   Stall freeze  JobGiver_Wander.TryGiveJob(Pawn) — prefix hands a small
    //                 wild animal a Wait_Wander job instead of a wander walk.
    //   Gale deafen   MapComponent tick → RM_GaleDeafened on unroofed pawns.
    //   Gale turbines CompPowerPlantWind.DesiredPowerOutput (protected getter)
    //                 postfix; breakdowns via public CompBreakdownable.DoBreakdown.
    //   Gale raids    IncidentWorker.ChanceFactorNow(IIncidentTarget) postfix,
    //                 raid workers only. StorytellerComp.IncidentChanceFinal
    //                 multiplies by it when choosing WHICH incident of a
    //                 category fires, so this weights raids among threats
    //                 while the Gale blows; it does not add threat events.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_WindCalendar
    {
        public static bool IsStall(Map map)
        {
            return map?.weatherManager != null && map.weatherManager.curWeather == RM_LeaningScrubDefOf.RM_Stall;
        }

        public static bool IsGale(Map map)
        {
            return map?.weatherManager != null && map.weatherManager.curWeather == RM_LeaningScrubDefOf.RM_Gale;
        }

        public static bool On(bool feature)
        {
            return RM_LeaningScrubSettings.modEnabled && feature;
        }
    }

    public class RM_MapComponent_WindCalendar : MapComponent
    {
        private const int DeafenInterval = 250;
        private const int TurbineInterval = 2500;

        public RM_MapComponent_WindCalendar(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            int tick = Find.TickManager.TicksGame;
            if (tick % DeafenInterval != 0 || !RM_WindCalendar.IsGale(map))
            {
                return;
            }

            if (RM_WindCalendar.On(RM_LeaningScrubSettings.galeDeafenEnabled))
            {
                DeafenOutdoorPawns();
            }

            if (tick % TurbineInterval == 0 && RM_WindCalendar.On(RM_LeaningScrubSettings.galeTurbineSurgeEnabled))
            {
                RollTurbineBreakdowns();
            }
        }

        private void DeafenOutdoorPawns()
        {
            HediffDef def = RM_LeaningScrubDefOf.RM_GaleDeafened;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.RaceProps.IsMechanoid || p.Position.Roofed(map))
                {
                    continue;
                }
                Hediff existing = p.health.hediffSet.GetFirstHediffOfDef(def);
                if (existing != null)
                {
                    existing.Severity = 1f;
                }
                else
                {
                    p.health.AddHediff(def);
                }
            }
        }

        private void RollTurbineBreakdowns()
        {
            float mtbDays = RM_LeaningScrubSettings.galeTurbineBreakdownMtbDays;
            if (mtbDays <= 0f)
            {
                return;
            }
            List<Building> buildings = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < buildings.Count; i++)
            {
                Building b = buildings[i];
                CompPowerPlantWind turbine = b.TryGetComp<CompPowerPlantWind>();
                if (turbine == null || !turbine.PowerOn)
                {
                    continue;
                }
                CompBreakdownable breakdown = b.TryGetComp<CompBreakdownable>();
                if (breakdown == null || breakdown.BrokenDown)
                {
                    continue;
                }
                if (Rand.MTBEventOccurs(mtbDays, GenDate.TicksPerDay, TurbineInterval))
                {
                    breakdown.DoBreakdown();
                }
            }
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_WindCalendarPatches
    {
        static RM_WindCalendarPatches()
        {
            Harmony harmony = new Harmony("mandrake.rm.leaningscrub");
            TryPatch(harmony, "stall-freeze",
                AccessTools.Method(typeof(JobGiver_Wander), "TryGiveJob"),
                prefix: nameof(Wander_Prefix));
            TryPatch(harmony, "gale-turbine-surge",
                AccessTools.PropertyGetter(typeof(CompPowerPlantWind), "DesiredPowerOutput"),
                postfix: nameof(WindOutput_Postfix));
            TryPatch(harmony, "gale-raid-weighting",
                AccessTools.Method(typeof(IncidentWorker), nameof(IncidentWorker.ChanceFactorNow)),
                postfix: nameof(ChanceFactorNow_Postfix));
        }

        private static void TryPatch(Harmony harmony, string rule, MethodBase target, string prefix = null, string postfix = null)
        {
            if (target == null)
            {
                Log.Error("[RM LeaningScrub] " + rule + ": target method not found — rule NOT armed. "
                    + "The engine signature this patch was written against has moved.");
                return;
            }
            try
            {
                harmony.Patch(target,
                    prefix: prefix == null ? null : new HarmonyMethod(typeof(RM_WindCalendarPatches), prefix),
                    postfix: postfix == null ? null : new HarmonyMethod(typeof(RM_WindCalendarPatches), postfix));
            }
            catch (Exception e)
            {
                Log.Error("[RM LeaningScrub] " + rule + ": patch failed, rule NOT armed. " + e);
            }
        }

        // Stall: small wild animals hold still. Only the wander fallback is
        // replaced — fleeing, eating, sleeping and hunting all come from higher
        // think-tree nodes and are untouched.
        public static bool Wander_Prefix(Pawn pawn, ref Job __result)
        {
            if (!RM_WindCalendar.On(RM_LeaningScrubSettings.stallFreezeEnabled))
            {
                return true;
            }
            if (pawn == null || pawn.Faction != null || !pawn.RaceProps.Animal || pawn.Flying)
            {
                return true;
            }
            if (pawn.BodySize > RM_LeaningScrubSettings.stallFreezeMaxBodySize || !RM_WindCalendar.IsStall(pawn.Map))
            {
                return true;
            }
            Job wait = JobMaker.MakeJob(JobDefOf.Wait_Wander);
            wait.expiryInterval = 600;
            __result = wait;
            return false;
        }

        // Gale: turbines surge past their rating (vanilla caps the wind input at 1.5).
        public static void WindOutput_Postfix(CompPowerPlantWind __instance, ref float __result)
        {
            if (__result <= 0f || !RM_WindCalendar.On(RM_LeaningScrubSettings.galeTurbineSurgeEnabled))
            {
                return;
            }
            Map map = __instance.parent?.Map;
            if (RM_WindCalendar.IsGale(map))
            {
                __result *= RM_LeaningScrubSettings.galeTurbineSurgeFactor;
            }
        }

        // Gale: raids weigh heavier among threats while it blows.
        public static void ChanceFactorNow_Postfix(IncidentWorker __instance, IIncidentTarget target, ref float __result)
        {
            if (!(__instance is IncidentWorker_RaidEnemy) || !(target is Map map))
            {
                return;
            }
            if (RM_WindCalendar.On(RM_LeaningScrubSettings.galeRaidWeightingEnabled) && RM_WindCalendar.IsGale(map))
            {
                __result *= RM_LeaningScrubSettings.galeRaidWeightFactor;
            }
        }
    }
}
