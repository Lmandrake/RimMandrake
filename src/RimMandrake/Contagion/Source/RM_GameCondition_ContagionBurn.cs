using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 Part 1 — the Burn itself.
    //
    // Forces RM_ContagionBurn (def.weatherDef) through the engine's own
    // WeatherDecider.ForcedWeather seam, and every 250 ticks puts UV pressure
    // on everything under open sky (RM_ContagionSky.Exposed):
    //   - a UV-shy native: Burn damage, and it is ordered to DIVE — sprint to
    //     the nearest roof / tree canopy / water cell;
    //   - a leaker native (Scorchpod): Burn damage, no dive — it cooks;
    //   - an armored native (Scaldhide, Crispling): nothing — it hunts;
    //   - anything else (colonists, visitors, off-biome animals): RM_BurnDose,
    //     the radiation-flavoured sunscald that fades once out of the light.
    // Registered only by RM_MapComponent_ContagionSky.StartBurn, which refuses
    // a map without RM_ContagionSkyExtension — and the pressure loop re-checks
    // the extension itself, so even a dev-tool-added Burn on another biome
    // changes the weather and hurts nobody.
    public class RM_GameCondition_ContagionBurn : GameCondition
    {
        private const float DiveSearchRadius = 14f;

        public override WeatherDef ForcedWeather()
        {
            return def.weatherDef;
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            if (TicksPassed % RM_ContagionSky.Interval != 0) return;
            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                Pressure(maps[i]);
            }
        }

        private static readonly List<Pawn> tmpPawns = new List<Pawn>();

        private void Pressure(Map map)
        {
            RM_ContagionSkyExtension ext = RM_ContagionSky.ExtFor(map);
            // The tear needs the weather to have actually arrived: during the forced transition the sky is still closing over.
            float dmgFactor = RM_ContagionSettings.burnDamageFactor;
            if (!RM_SkyKernel.PressureActive(ext != null, RM_ContagionSettings.burnEnabled, map.weatherManager.curWeather == def.weatherDef, dmgFactor)) return;

            HashSet<ThingDef> natives = RM_ContagionSky.NativesOf(map.Biome, ext);

            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (p == null || p.Dead || !p.Spawned) continue;
                if (!RM_ContagionSky.Exposed(p.Position, map)) continue;

                BurnEffect effect = RM_SkyKernel.Classify(natives.Contains(p.def), ext.armoredNatives.Contains(p.def),
                    ext.leakerNatives.Contains(p.def), p.RaceProps != null && !p.RaceProps.IsMechanoid && p.health != null);
                if (effect == BurnEffect.Damage || effect == BurnEffect.DamageAndDive)
                {
                    p.TakeDamage(new DamageInfo(DamageDefOf.Burn, ext.nativeBurnDamagePerInterval * dmgFactor));
                    if (p.Dead || !p.Spawned) continue;
                    if (effect == BurnEffect.DamageAndDive) TryDive(p, map);
                }
                else if (effect == BurnEffect.Dose)
                {
                    HealthUtility.AdjustSeverity(p, RM_ContagionSkyDefOf.RM_BurnDose, ext.visitorDosePerInterval * dmgFactor);
                }
            }
            tmpPawns.Clear();
        }

        // The dive: nearest sheltered, standable, reachable cell, at a sprint.
        // Skipped for a drafted pawn, one in a mental state (a manhunter keeps
        // its fury), a downed one, and one already running for shelter.
        private static void TryDive(Pawn p, Map map)
        {
            Job cur = p.CurJob;
            bool running = cur != null && cur.def == JobDefOf.Goto && cur.targetA.IsValid && !RM_ContagionSky.Exposed(cur.targetA.Cell, map);
            if (!RM_SkyKernel.MayDive(p.Downed, p.Drafted, p.InMentalState, p.jobs != null, running)) return;

            List<IntVec3> sheltered = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(p.Position, DiveSearchRadius, false))
            {
                if (!c.InBounds(map) || !c.Standable(map)) continue;
                if (RM_ContagionSky.Exposed(c, map)) continue;
                sheltered.Add(c);
                if (sheltered.Count > 4) break;   // only the first four are ever tried
            }
            int pick = RM_SkyKernel.PickDive(sheltered.Count, i => p.CanReach(sheltered[i], PathEndMode.OnCell, Danger.Deadly));
            if (pick >= 0)
            {
                Job job = JobMaker.MakeJob(JobDefOf.Goto, sheltered[pick]);
                job.locomotionUrgency = LocomotionUrgency.Sprint;
                job.expiryInterval = 2000;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
            }
        }
    }
}
