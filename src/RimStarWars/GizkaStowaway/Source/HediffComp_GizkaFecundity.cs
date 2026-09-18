using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.GizkaStowaway
{
    public class HediffCompProperties_GizkaFecundity : HediffCompProperties
    {
        public float baseReplicateIntervalDays = 4f;
        public float intervalStretchAtCap = 8f;
        public float minBreedingTemperature = 12f;
        public float minFoodLevel = 0.35f;

        public HediffCompProperties_GizkaFecundity()
        {
            compClass = typeof(HediffComp_GizkaFecundity);
        }
    }

    /// <summary>
    /// GIZKA_TRIBBLE_ADAPTATION_1, draft §2 — "the turn". Comfort is the fuse.
    ///
    /// This is the ONLY fast-breeding path the feature adds, and it is per-PAWN
    /// on purpose (draft §4's guard): it rides a hediff rather than a comp so
    /// that it attaches to stowaway lineage and nothing else. A gizka the
    /// player bought, tamed off the map or bred deliberately never carries it,
    /// so "farm the problem" stays the deliberately mediocre exit it is
    /// designed to be and never becomes a ladder.
    ///
    /// Replication is asexual — one stowaway must be enough, per the owner's
    /// premise and KotOR — and the offspring inherits the hediff and the
    /// parent's faction, so a tame stowaway's descendants are tame colony
    /// animals eating out of your stores, which is the whole problem.
    ///
    /// Shape only is borrowed from the Tribble module's
    /// CompProperties_TribbleSpawner (one interval knob, logic in C#). None of
    /// that inactive mod's code or numbers are used.
    ///
    /// The anti-exponential clamp lives here and nowhere else:
    ///   - a hard per-map cap (Mod Settings), above which nothing replicates;
    ///   - an interval that stretches toward `intervalStretchAtCap` as the cap
    ///     is approached, so the curve flattens before it hits the wall rather
    ///     than doubling into it.
    /// Geometric onset, flat ceiling.
    /// </summary>
    public class HediffComp_GizkaFecundity : HediffComp
    {
        private int ticksUntilReplicate = -1;

        public HediffCompProperties_GizkaFecundity Props =>
            (HediffCompProperties_GizkaFecundity)props;

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ticksUntilReplicate, "ticksUntilReplicate", -1);
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            Pawn pawn = Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Map == null) return;

            RSW_GizkaSettings s = RSW_GizkaStowawayMod.Settings;
            if (s == null || !s.stowawayEventsEnabled) return;

            // Juveniles do not breed. Adulthood is the donor's own lifeStage
            // boundary (patched, but read live so the two never drift).
            if (pawn.ageTracker != null &&
                pawn.ageTracker.CurLifeStageIndex < pawn.RaceProps.lifeStageAges.Count - 1)
            {
                return;
            }

            if (ticksUntilReplicate < 0)
            {
                ticksUntilReplicate = ResetInterval(pawn);
                return;
            }

            // The fuse only burns while fed AND warm. This is checked every
            // tick-interval rather than at the moment of replication so that a
            // vented hold genuinely STALLS the swarm instead of merely delaying
            // it by one interval — which is the difference between the cold
            // exit being a real answer and being a rounding error.
            if (!IsComfortable(pawn)) return;

            ticksUntilReplicate -= delta;
            if (ticksUntilReplicate > 0) return;

            ticksUntilReplicate = ResetInterval(pawn);
            TryReplicate(pawn);
        }

        private bool IsComfortable(Pawn pawn)
        {
            float temp = GenTemperature.GetTemperatureForCell(pawn.Position, pawn.Map);
            if (temp < Props.minBreedingTemperature) return false;

            Need_Food food = pawn.needs?.food;
            if (food != null && food.CurLevelPercentage < Props.minFoodLevel) return false;

            return true;
        }

        private int ResetInterval(Pawn pawn)
        {
            RSW_GizkaSettings s = RSW_GizkaStowawayMod.Settings;
            float rate = (s == null || s.breedingRate <= 0.01f) ? 1f : s.breedingRate;

            int cap = s?.populationCap ?? 22;
            int pop = RSW_GizkaPopulation.CountOnMap(pawn.Map);
            float fill = cap <= 0 ? 1f : Mathf.Clamp01((float)pop / cap);

            // Linear stretch from 1x at an empty map to intervalStretchAtCap at
            // the cap. Combined with the hard cap below, this is the whole of
            // the anti-exponential clamp.
            float stretch = Mathf.Lerp(1f, Mathf.Max(1f, Props.intervalStretchAtCap), fill);

            float days = Props.baseReplicateIntervalDays * stretch / rate;
            // Jittered so a wave of siblings does not replicate in lockstep and
            // produce a visible staircase.
            return Mathf.Max(2500, Mathf.RoundToInt(days * 60000f * Rand.Range(0.85f, 1.15f)));
        }

        private void TryReplicate(Pawn pawn)
        {
            RSW_GizkaSettings s = RSW_GizkaStowawayMod.Settings;
            int cap = s?.populationCap ?? 22;
            if (RSW_GizkaPopulation.CountOnMap(pawn.Map) >= cap) return;

            if (!CellFinder.TryFindRandomCellNear(pawn.Position, pawn.Map, 4,
                    c => c.Standable(pawn.Map) && !c.Fogged(pawn.Map), out IntVec3 cell))
            {
                cell = pawn.Position;
            }

            // Deliberately left unnamed: colonists name the first one they meet,
            // and the moment they stop naming them is the moment the joke turns.
            RSW_GizkaPopulation.SpawnStowaway(pawn.Map, cell, pawn.Faction, newborn: true);
        }
    }
}
