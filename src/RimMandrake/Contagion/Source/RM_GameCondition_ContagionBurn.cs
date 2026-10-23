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
            if (!RM_SkyKernel.PressureActive(ext != null, RM_ContagionSettings.burnEnabled, map.weatherManager.curWeather == def.weatherDef, dmgFactor))
            {
                RM_BurnProof.NoteSkipped();
                return;
            }
            RM_BurnProof.NotePulse();

            HashSet<ThingDef> natives = RM_ContagionSky.NativesOf(map.Biome, ext);

            tmpPawns.Clear();
            tmpPawns.AddRange(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < tmpPawns.Count; i++)
            {
                Pawn p = tmpPawns[i];
                if (p == null || p.Dead || !p.Spawned) continue;
                if (!RM_ContagionSky.Exposed(p.Position, map))
                {
                    RM_BurnProof.For(p).sheltered++;
                    continue;
                }

                BurnEffect effect = RM_SkyKernel.Classify(natives.Contains(p.def), ext.armoredNatives.Contains(p.def),
                    ext.leakerNatives.Contains(p.def), p.RaceProps != null && !p.RaceProps.IsMechanoid && p.health != null);
                RM_BurnProof.Rec rec = RM_BurnProof.For(p);
                rec.exposed++;
                rec.lastEffect = effect;
                if (effect == BurnEffect.Damage || effect == BurnEffect.DamageAndDive)
                {
                    DamageWorker.DamageResult res = p.TakeDamage(new DamageInfo(DamageDefOf.Burn, ext.nativeBurnDamagePerInterval * dmgFactor));
                    rec.damaged++;
                    rec.dealt += res?.totalDamageDealt ?? 0f;
                    if (p.Dead || !p.Spawned) continue;
                    if (effect == BurnEffect.DamageAndDive && TryDive(p, map)) rec.dives++;
                }
                else if (effect == BurnEffect.Dose)
                {
                    HealthUtility.AdjustSeverity(p, RM_ContagionSkyDefOf.RM_BurnDose, ext.visitorDosePerInterval * dmgFactor);
                    rec.dosed++;
                }
            }
            tmpPawns.Clear();
        }

        // The dive: nearest sheltered, standable, reachable cell, at a sprint.
        // Skipped for a drafted pawn, one in a mental state (a manhunter keeps
        // its fury), a downed one, and one already running for shelter.
        private static bool TryDive(Pawn p, Map map)
        {
            Job cur = p.CurJob;
            bool running = cur != null && cur.def == JobDefOf.Goto && cur.targetA.IsValid && !RM_ContagionSky.Exposed(cur.targetA.Cell, map);
            if (!RM_SkyKernel.MayDive(p.Downed, p.Drafted, p.InMentalState, p.jobs != null, running)) return false;

            List<IntVec3> sheltered = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(p.Position, DiveSearchRadius, false))
            {
                if (!c.InBounds(map) || !c.Standable(map)) continue;
                if (RM_ContagionSky.Exposed(c, map)) continue;
                sheltered.Add(c);
                if (sheltered.Count >= RM_SkyKernel.DiveCandidates) break;
            }
            // Four reachability checks a pulse, but a different window of four each pulse (DiveOffset).
            int n = sheltered.Count;
            int off = RM_SkyKernel.DiveOffset(Find.TickManager.TicksGame / RM_ContagionSky.Interval, n);
            int pick = RM_SkyKernel.PickDive(n, i => p.CanReach(sheltered[(off + i) % n], PathEndMode.OnCell, Danger.Deadly));
            if (pick >= 0)
            {
                Job job = JobMaker.MakeJob(JobDefOf.Goto, sheltered[(off + pick) % n]);
                job.locomotionUrgency = LocomotionUrgency.Sprint;
                job.expiryInterval = 2000;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
                return true;
            }
            return false;
        }
    }

    // jawa/static_call proof hook (validation.py, burn_forced chain). CONTAGION_BURN_DIAGNOSE_NATIVE_FEELS_NOTHING (live
    // 2026-10-23): the UV-shy native's living rows carried only 'MissingBodyPart' and no Burn, so the harness could not
    // tell "never exposed during a pulse", "exposed but classed as something else", "hit for zero" and "hit, and the
    // 3-point burn took a whole part off a 0.25-health-scale gnashling" (a destroyed part leaves no Burn hediff) apart.
    // These counters, per pawn and never scribed, are the mod's own account of what each pressure pulse did to it.
    public static class RM_BurnProof
    {
        public class Rec
        {
            public int sheltered, exposed, damaged, dosed, dives;
            public float dealt;
            public BurnEffect lastEffect = BurnEffect.None;
        }

        private static readonly Dictionary<int, Rec> recs = new Dictionary<int, Rec>();
        private static int pulses, skipped;

        public static void NotePulse() { pulses++; }
        public static void NoteSkipped() { skipped++; }

        public static Rec For(Pawn p)
        {
            if (!recs.TryGetValue(p.thingIDNumber, out Rec r))
            {
                if (recs.Count > 2048) recs.Clear();      // diagnostics only: a long game must not grow this forever
                r = new Rec();
                recs[p.thingIDNumber] = r;
            }
            return r;
        }

        // "OK pulses=N skipped=N pawn[sheltered=a exposed=b damaged=c dealt=d dosed=e dives=f last=Effect]",
        // or pawn[unseen] when no pressure pulse ever reached it.
        public static string PressureReport(Thing pawn)
        {
            if (!(pawn is Pawn p)) return "UNMEASURED " + (pawn?.ThingID ?? "null") + " is not a pawn";
            string head = "OK pulses=" + pulses + " skipped=" + skipped + " ";
            if (!recs.TryGetValue(p.thingIDNumber, out Rec r)) return head + "pawn[unseen]";
            return head + "pawn[sheltered=" + r.sheltered + " exposed=" + r.exposed + " damaged=" + r.damaged
                + " dealt=" + r.dealt.ToString("0.##", System.Globalization.CultureInfo.InvariantCulture)
                + " dosed=" + r.dosed + " dives=" + r.dives + " last=" + r.lastEffect + "]";
        }
    }
}
