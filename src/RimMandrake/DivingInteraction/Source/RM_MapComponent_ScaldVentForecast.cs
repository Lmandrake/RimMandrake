using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.DivingInteraction
{
    // SCALD_FLOOR_VENT_FIELDS_1 — the Sail Forecast (GPT idea 2, owner sitting 2026-10-02).
    // One vent at a time cycles quiet -> warning -> discharge. During the warning every RM_Noohm
    // on the map gathers over that vent; the discharge then burns and interrupts anyone near it.
    // The same gathering ALWAYS precedes a discharge, so the sails are a reliable tell. Outside the
    // warning, a sailor that has drifted far from every vent is sent back to the nearest one (its
    // tether: sails never leave their bubble line).
    //
    // Not built: displacement of loose items near a discharge (damage + job interrupt only).
    // All timings, radii and damage are first guesses. Scope: Scald floor maps only.
    public class RM_MapComponent_ScaldVentForecast : MapComponent
    {
        private const int SweepInterval = 60;
        private const int QuietMin = 6000;
        private const int QuietMax = 12000;
        private const int WarningTicks = 2500;
        private const int DischargeTicks = 300;
        private const float DischargeRadius = 3f;
        private const float GatherNear = 4f;
        private const float GatherFar = 6f;
        private const float TetherRadius = 10f;
        private const float DischargeDamage = 3f;

        // 0 quiet, 1 warning, 2 discharge
        private int phase;
        private int phaseEnd = -1;
        private int ventId = -1;
        private bool isScaldFloor;

        public RM_MapComponent_ScaldVentForecast(Map map) : base(map)
        {
        }

        public static bool IsScaldFloorMap(Map map)
        {
            string b = map?.Biome?.defName;
            return b == "RM_SeabedFloor_TheScald" || (b == "RM_TheScald" && map.IsPocketMap);
        }

        public int Phase => phase;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref phase, "scaldVentPhase", 0);
            Scribe_Values.Look(ref phaseEnd, "scaldVentPhaseEnd", -1);
            Scribe_Values.Look(ref ventId, "scaldVentId", -1);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isScaldFloor = IsScaldFloorMap(map);
        }

        private List<Thing> Vents()
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_ScaldVent");
            return def == null ? new List<Thing>() : map.listerThings.ThingsOfDef(def);
        }

        private static Thing ById(List<Thing> vents, int id)
        {
            foreach (Thing t in vents)
            {
                if (t.thingIDNumber == id)
                {
                    return t;
                }
            }
            return null;
        }

        private IEnumerable<Pawn> Sailors()
        {
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.def.defName == "RM_Noohm" && p.Faction == null && !p.Dead)
                {
                    yield return p;
                }
            }
        }

        public override void MapComponentTick()
        {
            if (!isScaldFloor || !RM_DivingSettings.masterEnabled || !RM_DivingSettings.scaldVentForecastEnabled)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (phase == 2 && now % 15 == 0 && now < phaseEnd)   // an expired phase never discharges
            {
                Discharge(now);
            }
            if (now % SweepInterval != 0)
            {
                return;
            }

            List<Thing> vents = Vents();
            if (vents.Count == 0)
            {
                return;
            }
            if (phaseEnd < 0)
            {
                phaseEnd = now + Rand.RangeInclusive(QuietMin, QuietMax);
            }
            if (now >= phaseEnd)
            {
                Advance(now, vents);
            }

            Thing target = phase == 1 ? ById(vents, ventId) : null;
            foreach (Pawn sailor in Sailors())
            {
                if (sailor.Downed || sailor.Map != map || sailor.jobs == null)
                {
                    continue;
                }
                if (target != null)
                {
                    Gather(sailor, target);
                }
                else
                {
                    Tether(sailor, vents);
                }
            }
            if (target != null)
            {
                FleckMaker.ThrowAirPuffUp(target.DrawPos + new Vector3(Rand.Range(-1f, 1f), 0f, Rand.Range(-1f, 1f)), map);
            }
        }

        private void Advance(int now, List<Thing> vents)
        {
            if (phase == 0)
            {
                phase = 1;
                ventId = vents.RandomElement().thingIDNumber;
                phaseEnd = now + WarningTicks;
            }
            else if (phase == 1)
            {
                phase = 2;
                phaseEnd = now + DischargeTicks;
            }
            else
            {
                phase = 0;
                ventId = -1;
                phaseEnd = now + Rand.RangeInclusive(QuietMin, QuietMax);
            }
        }

        private void Gather(Pawn sailor, Thing vent)
        {
            float d = (sailor.Position - vent.Position).LengthHorizontal;
            if (d >= GatherNear && d <= GatherFar)
            {
                return;
            }
            GoNear(sailor, vent.Position, GatherNear, GatherFar);
        }

        private void Tether(Pawn sailor, List<Thing> vents)
        {
            Thing nearest = null;
            float best = float.MaxValue;
            foreach (Thing v in vents)
            {
                float d = (sailor.Position - v.Position).LengthHorizontal;
                if (d < best)
                {
                    best = d;
                    nearest = v;
                }
            }
            if (nearest != null && best > TetherRadius)
            {
                GoNear(sailor, nearest.Position, 3f, TetherRadius - 3f);
            }
        }

        private void GoNear(Pawn sailor, IntVec3 center, float minR, float maxR)
        {
            if (sailor.CurJobDef == JobDefOf.Goto)
            {
                return;
            }
            for (int i = 0; i < 12; i++)
            {
                IntVec3 c = center + GenRadial.RadialPattern[Rand.Range(1, GenRadial.NumCellsInRadius(maxR))];
                float d = (c - center).LengthHorizontal;
                if (d < minR || !c.InBounds(map) || !c.Standable(map) || !sailor.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    continue;
                }
                sailor.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Goto, c), JobCondition.InterruptForced);
                return;
            }
        }

        private void Discharge(int now)
        {
            Thing vent = ById(Vents(), ventId);
            if (vent == null)
            {
                return;
            }
            FleckMaker.ThrowAirPuffUp(vent.DrawPos, map);
            if (!RM_DivingSettings.scaldVentDischargeHarms || now % 60 != 0)
            {
                return;
            }
            // Snapshot: a burn can kill and despawn a pawn, which mutates the live list.
            foreach (Pawn p in new List<Pawn>(map.mapPawns.AllPawnsSpawned))
            {
                if (p.Dead || !p.Spawned || p.Map != map || p.def.defName == "RM_Noohm" || (p.Position - vent.Position).LengthHorizontal > DischargeRadius)
                {
                    continue;
                }
                p.TakeDamage(new DamageInfo(DamageDefOf.Burn, DischargeDamage, 0f, -1f, vent));
                if (p.jobs != null && p.CurJob != null)
                {
                    p.jobs.EndCurrentJob(JobCondition.InterruptForced, true, false);
                }
            }
        }
    }
}
