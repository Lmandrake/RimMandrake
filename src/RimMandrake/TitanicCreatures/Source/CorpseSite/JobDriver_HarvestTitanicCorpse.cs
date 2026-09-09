using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// One harvest session against a Building_TitanicCorpseSite's remaining
    /// pool. Modeled directly on this codebase's own
    /// RimMandrake.Pits.JobDriver_DigPitDeeper (MiningSpeed-scaled work toil) -
    /// harvesting a titan's remains reads as excavation, not butchery, which is
    /// also why this sits on the Mining work type rather than Cooking/Hunting.
    /// </summary>
    public class JobDriver_HarvestTitanicCorpse : JobDriver
    {
        private float workLeft;
        private const float WorkPerSession = 2500f;

        private Building_TitanicCorpseSite Site => job.targetA.Thing as Building_TitanicCorpseSite;

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Site == null || !Site.HasYield);

            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

            Toil harvest = ToilMaker.MakeToil("MakeNewToils");
            harvest.initAction = delegate { workLeft = WorkPerSession; };
            harvest.tickIntervalAction = delegate(int delta)
            {
                float amount = pawn.GetStatValue(StatDefOf.MiningSpeed) * delta;
                workLeft -= amount;
                if (pawn.skills != null)
                {
                    pawn.skills.Learn(SkillDefOf.Mining, 0.08f * delta);
                }
                if (workLeft <= 0f)
                {
                    Building_TitanicCorpseSite site = Site;
                    if (site != null && !site.Destroyed)
                    {
                        List<Thing> products = site.HarvestOneSession(pawn);
                        foreach (Thing product in products)
                        {
                            GenPlace.TryPlaceThing(product, pawn.Position, pawn.Map, ThingPlaceMode.Near);
                        }
                    }
                    ReadyForNextToil();
                }
            };
            harvest.defaultCompleteMode = ToilCompleteMode.Never;
            harvest.WithProgressBar(TargetIndex.A, () => 1f - workLeft / WorkPerSession);
            harvest.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
            harvest.activeSkill = () => SkillDefOf.Mining;
            yield return harvest;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workLeft, "workLeft", 0f);
        }
    }
}
