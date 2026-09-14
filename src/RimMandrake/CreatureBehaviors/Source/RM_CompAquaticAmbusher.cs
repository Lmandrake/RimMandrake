using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // GREENTIDE_MECHANICS_2 M7 build (greentide_kit_spec.md M7, "Lunger
    // ambush"). "New small comp RM_CompAquaticAmbusher : ThingComp on the
    // Lunger kind: while the pawn stands on deep-water terrain and has no
    // melee target -> BecomeInvisible(); target acquired in lunge range ->
    // BecomeVisible() + a lunge job... Hunting AI stays vanilla predator
    // ThinkTree — the comp only manages visibility + the opener."
    //
    // Reads "has no melee target" / "target acquired" as one operation
    // (this comp's own active scan for a hostile pawn within lungeRangeCells
    // while submerged) rather than two separately-tracked states — simpler,
    // and behaviorally identical: no target found this check IS "has no
    // melee target", a target found within range IS "acquired".
    //
    // Self-review: the opening strike is dealt MANUALLY (TakeDamage in
    // RM_JobDriver_LungeAttack), not through the pawn's normal melee-verb
    // Verb_MeleeAttackDamage pipeline — deliberately, to avoid a Harmony
    // patch on that private/protected vanilla combat-resolution method for
    // what the spec itself frames as "a small comp" (M-effort). Same manual-
    // TakeDamage idiom this assembly's own RM_JobDriver_Gnaw and the shared
    // EnvironmentalHazards assembly's RM_TreeFallUtility/
    // HediffComp_PeriodicAreaAttack already use for a scripted, non-verb
    // source of damage. Ongoing combat after the opener is 100% vanilla
    // predator ThinkTree, per the spec's own explicit boundary.
    public class RM_CompAquaticAmbusher : ThingComp
    {
        private static readonly HashSet<TerrainDef> DeepWaterTerrains = new HashSet<TerrainDef>();
        private static bool deepWaterTerrainsBuilt;

        public CompProperties_AquaticAmbusher Props => (CompProperties_AquaticAmbusher)props;

        public override void CompTick()
        {
            base.CompTick();

            if (!(parent is Pawn pawn) || !pawn.Spawned || pawn.Dead || pawn.Map == null || pawn.Downed)
            {
                return; // a downed pawn never submerges or lunges — HediffComp_Invisibility's own ForcedVisible already forces it visible regardless, this only stops a fresh lunge job from being force-started on it
            }

            if (!parent.IsHashIntervalTick(System.Math.Max(1, Props.checkIntervalTicks)))
            {
                return;
            }

            if (!RM_CreatureBehaviorsSettings.aquaticAmbushEnabled)
            {
                // mod option: aquatic ambush disabled — clear any lingering
                // invisibility rather than leaving a submerged pawn stuck
                // invisible forever once the player turns this off.
                BecomeVisible(pawn);
                return;
            }

            Evaluate(pawn);
        }

        private void Evaluate(Pawn pawn)
        {
            bool submerged = IsDeepWater(pawn.Position, pawn.Map);
            Pawn target = submerged ? FindLungeTarget(pawn) : null;

            if (target != null)
            {
                BecomeVisible(pawn);
                TriggerLunge(pawn, target);
                return;
            }

            if (submerged)
            {
                BecomeInvisible(pawn);
            }
            else
            {
                BecomeVisible(pawn);
            }
        }

        private Pawn FindLungeTarget(Pawn pawn)
        {
            IReadOnlyList<Pawn> pawns = pawn.Map.mapPawns.AllPawnsSpawned;
            Pawn best = null;
            float bestDistSq = Props.lungeRangeCells * Props.lungeRangeCells;

            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn candidate = pawns[i];
                if (candidate == pawn || candidate.Dead || !candidate.Spawned)
                {
                    continue;
                }

                if (!pawn.HostileTo(candidate))
                {
                    continue;
                }

                float distSq = (candidate.Position - pawn.Position).LengthHorizontalSquared;
                if (distSq <= bestDistSq)
                {
                    bestDistSq = distSq;
                    best = candidate;
                }
            }

            return best;
        }

        private void TriggerLunge(Pawn pawn, Pawn target)
        {
            if (pawn.jobs?.curJob != null && pawn.jobs.curJob.def == RM_JobDefOf.RM_LungeAttack)
            {
                return; // already mid-lunge — don't restart it every interval tick
            }

            if (Props.lungeSpeedHediff != null
                && pawn.health.hediffSet.GetFirstHediffOfDef(Props.lungeSpeedHediff) == null)
            {
                Hediff speedBurst = HediffMaker.MakeHediff(Props.lungeSpeedHediff, pawn);
                pawn.health.AddHediff(speedBurst);
            }

            Job job = JobMaker.MakeJob(RM_JobDefOf.RM_LungeAttack, target);
            job.locomotionUrgency = LocomotionUrgency.Sprint;
            pawn.jobs.StartJob(job, JobCondition.InterruptForced, resumeCurJobAfterwards: false, cancelBusyStances: true);
        }

        private void BecomeInvisible(Pawn pawn)
        {
            if (Props.invisibilityHediff == null || pawn.health == null)
            {
                return;
            }

            if (pawn.health.hediffSet.GetFirstHediffOfDef(Props.invisibilityHediff) != null)
            {
                return; // already submerged/invisible
            }

            Hediff hediff = HediffMaker.MakeHediff(Props.invisibilityHediff, pawn);
            pawn.health.AddHediff(hediff); // HediffComp_Invisibility.CompPostPostAdd calls BecomeInvisible(instant: true) itself
        }

        private void BecomeVisible(Pawn pawn)
        {
            if (Props.invisibilityHediff == null || pawn.health == null)
            {
                return;
            }

            Hediff hediff = pawn.health.hediffSet.GetFirstHediffOfDef(Props.invisibilityHediff);
            if (hediff == null)
            {
                return; // already visible
            }

            pawn.GetInvisibilityComp()?.BecomeVisible(instant: true);
            pawn.health.RemoveHediff(hediff);
        }

        // "Deep water" = vanilla's own named DEEP water terrains — distinct
        // from the matching Shallow ones, which a Lunger cannot ambush from
        // per the spec's own "deep water is never safe" framing (implying
        // shallow water is comparatively safe). INVENTED reading of "deep
        // water terrain", grounded in the actual vanilla TerrainDefOf names
        // rather than a guessed tag.
        private static bool IsDeepWater(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }

            EnsureDeepWaterTerrainsBuilt();
            TerrainDef terrain = c.GetTerrain(map);
            return terrain != null && DeepWaterTerrains.Contains(terrain);
        }

        private static void EnsureDeepWaterTerrainsBuilt()
        {
            if (deepWaterTerrainsBuilt)
            {
                return;
            }

            deepWaterTerrainsBuilt = true;
            if (TerrainDefOf.WaterDeep != null)
            {
                DeepWaterTerrains.Add(TerrainDefOf.WaterDeep);
            }
            if (TerrainDefOf.WaterOceanDeep != null)
            {
                DeepWaterTerrains.Add(TerrainDefOf.WaterOceanDeep);
            }
            if (TerrainDefOf.WaterMovingChestDeep != null)
            {
                DeepWaterTerrains.Add(TerrainDefOf.WaterMovingChestDeep);
            }
        }
    }
}
