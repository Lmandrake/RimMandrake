using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 Part 1 — the sky clock.
    //
    // Owns WHEN a Burn happens, so the Burn frequency is ours and not vanilla
    // WeatherDecider's: RM_ContagionBurn (the weather) sits in NO biome's
    // baseWeatherCommonalities, so the decider can never pick it; the only
    // way into it is RM_GameCondition_ContagionBurn's ForcedWeather, and the
    // only things that register that condition are this component (on a
    // biome carrying RM_ContagionSkyExtension) and the Cloud Repulsor (same
    // gate). Because this component schedules the tear itself it knows it
    // tellLeadTicks early — that head start IS the forecast: vanilla has no
    // forecast UI, so the tells are the forecast (ruled at the sitting).
    //
    // MapComponents are instantiated on every map by reflection; everything
    // here is inert unless RM_ContagionSky.Active(map).
    public class RM_MapComponent_ContagionSky : MapComponent
    {
        private int nextBurnTick = -1;
        private bool tellsBegun;
        private int bloomSinceTick = -1;

        public RM_MapComponent_ContagionSky(Map map) : base(map) { }

        public int NextBurnTick => nextBurnTick;
        public bool TellsBegun => tellsBegun;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref nextBurnTick, "nextBurnTick", -1);
            Scribe_Values.Look(ref tellsBegun, "tellsBegun", false);
            Scribe_Values.Look(ref bloomSinceTick, "bloomSinceTick", -1);
        }

        public bool BurnActive => BurnCondition() != null;

        public GameCondition BurnCondition()
        {
            GameConditionDef def = RM_ContagionSkyDefOf.RM_ContagionBurnCondition;
            // Map-local only: a Burn is never a world-level condition.
            List<GameCondition> active = map.gameConditionManager.ActiveConditions;
            for (int i = 0; i < active.Count; i++)
            {
                if (active[i].def == def) return active[i];
            }
            return null;
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % RM_ContagionSky.Interval != 0) return;

            RM_ContagionSkyExtension ext = RM_ContagionSky.ExtFor(map);
            if (ext == null)
            {
                nextBurnTick = -1;
                tellsBegun = false;
                bloomSinceTick = -1;
                return;
            }

            if (BurnActive)
            {
                // A Burn already holds the sky (natural or Repulsor-forced);
                // the next one is scheduled from its end, and so is the Bloom
                // clock the Coalescence reads.
                nextBurnTick = -1;
                tellsBegun = false;
                bloomSinceTick = -1;
                return;
            }

            if (bloomSinceTick < 0) bloomSinceTick = now;
            TryFormCoalescence(ext, now);

            if (!RM_ContagionSettings.burnEnabled)
            {
                nextBurnTick = -1;
                tellsBegun = false;
                return;
            }

            if (nextBurnTick < 0)
            {
                nextBurnTick = now + RollGap(ext);
                tellsBegun = false;
                return;
            }

            int lead = Mathf.Max(0, ext.tellLeadTicks);
            if (now >= nextBurnTick - lead && now < nextBurnTick)
            {
                if (RM_ContagionSettings.burnTellsEnabled)
                {
                    DoTells(ext, !tellsBegun, nextBurnTick - now);
                }
                tellsBegun = true;
                return;
            }

            if (now >= nextBurnTick)
            {
                StartBurn(ext.burnDurationTicks.RandomInRange, null);
                nextBurnTick = -1;
                tellsBegun = false;
            }
        }

        // Part 2 — the Coalescence forms during a LONG Bloom (bloomSinceTick
        // = when the last Burn ended), one per map at a time, away from the
        // player's home area. Spawned as a faction-less organism-building
        // (Building_RM_Coalescence) that the next Burn kills.
        private void TryFormCoalescence(RM_ContagionSkyExtension ext, int now)
        {
            if (!RM_ContagionSettings.coalescenceEnabled || ext.coalescenceDef == null) return;
            if (now - bloomSinceTick < ext.coalescenceLongBloomTicks) return;
            if (map.listerThings.ThingsOfDef(ext.coalescenceDef).Count > 0) return;
            if (!Rand.MTBEventOccurs(ext.coalescenceMtbDays, GenDate.TicksPerDay, RM_ContagionSky.Interval)) return;

            IntVec2 size = ext.coalescenceDef.size;
            bool found = CellFinderLoose.TryGetRandomCellWith(c =>
            {
                if (map.areaManager.Home[c]) return false;
                CellRect r = GenAdj.OccupiedRect(c, Rot4.North, size).ExpandedBy(1);
                if (!r.InBounds(map)) return false;
                foreach (IntVec3 cc in r)
                {
                    if (!cc.Standable(map) || cc.GetEdifice(map) != null || map.areaManager.Home[cc]) return false;
                }
                return true;
            }, map, 1000, out IntVec3 cell);
            if (!found) return;

            foreach (IntVec3 cc in GenAdj.OccupiedRect(cell, Rot4.North, size))
            {
                List<Thing> things = cc.GetThingList(map);
                for (int i = things.Count - 1; i >= 0; i--)
                {
                    if (things[i] is Plant) things[i].Destroy();
                }
            }
            Thing coal = ThingMaker.MakeThing(ext.coalescenceDef);
            GenSpawn.Spawn(coal, cell, map);
            Find.LetterStack.ReceiveLetter(
                "The Coalescence",
                "The storm has held too long. Somewhere in the goo the Contagion has been left alone long enough to gather itself: "
                + "a swelling of eyes and part-limbs that pulls the Unfinished into itself, grows, and sends the ones it does not eat "
                + "out mad.\n\nIt cannot survive the open sky — the next Burn will kill it.",
                LetterDefOf.ThreatBig, coal);
        }

        private static int RollGap(RM_ContagionSkyExtension ext)
        {
            float freq = Mathf.Max(0.05f, RM_ContagionSettings.burnFrequency);
            float days = ext.meanDaysBetweenBurns / freq * Rand.Range(0.5f, 1.5f);
            return Mathf.Max(ext.tellLeadTicks + RM_ContagionSky.Interval, (int)(days * GenDate.TicksPerDay));
        }

        // Registers a Burn on this map, or stretches the active one so at
        // least minTicks remain. Returns the condition, or null when this map
        // cannot carry a Burn (no sky extension — never a non-Contagion map).
        public GameCondition StartBurn(int minTicks, Thing causer)
        {
            if (RM_ContagionSky.ExtFor(map) == null) return null;
            GameCondition cond = BurnCondition();
            if (cond != null)
            {
                if (cond.TicksLeft < minTicks) cond.TicksLeft = minTicks;
                if (causer != null) cond.conditionCauser = causer;
                return cond;
            }
            cond = GameConditionMaker.MakeCondition(RM_ContagionSkyDefOf.RM_ContagionBurnCondition, minTicks);
            cond.conditionCauser = causer;
            map.gameConditionManager.RegisterCondition(cond);
            return cond;
        }

        // ── the tells ───────────────────────────────────────────────────
        // Tell 1 (Gawpsack sink): on the first pulse every sinker stops what
        // it is doing and settles in place for the rest of the lead; every
        // pulse throws a low dark puff under it. The DRAWN sink (the body
        // dropping from canopy height) needs a render seam and is listed as
        // remaining work — this is the behavioural beat.
        // Tell 2 (rattle): every rattler plant throws an air puff each pulse.
        // Sound and a per-plant shake need assets / a render seam.
        private void DoTells(RM_ContagionSkyExtension ext, bool first, int ticksLeft)
        {
            if (!ext.tellSinkers.NullOrEmpty())
            {
                List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
                for (int i = pawns.Count - 1; i >= 0; i--)
                {
                    Pawn p = pawns[i];
                    if (p == null || p.Dead || p.Downed || !ext.tellSinkers.Contains(p.def)) continue;
                    FleckMaker.ThrowDustPuffThick(p.DrawPos, map, 1.2f, new Color(0.35f, 0.05f, 0.08f));
                    if (first && !p.Drafted && !p.InMentalState && p.jobs != null)
                    {
                        Job wait = JobMaker.MakeJob(JobDefOf.Wait);
                        wait.expiryInterval = Mathf.Max(RM_ContagionSky.Interval, ticksLeft);
                        p.jobs.StartJob(wait, JobCondition.InterruptForced);
                    }
                }
            }

            if (!ext.tellRattlers.NullOrEmpty())
            {
                List<Thing> plants = map.listerThings.ThingsInGroup(ThingRequestGroup.Plant);
                for (int i = 0; i < plants.Count; i++)
                {
                    Thing t = plants[i];
                    if (ext.tellRattlers.Contains(t.def) && Rand.Chance(0.6f))
                    {
                        FleckMaker.ThrowAirPuffUp(t.DrawPos, map);
                    }
                }
            }
        }
    }
}
