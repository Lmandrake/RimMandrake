using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Miasma
{
    // MIASMA_ATTAR_STILL_1. The attar: glaze for a finished artwork (raises its Beauty), balm for a scar
    // (a cosmetic; nothing that is an injury, only a permanent scar, and nothing else heals).
    [DefOf]
    public static class RM_AttarDefOf
    {
        public static ThingDef RM_Attar;
        public static JobDef RM_GlazeArtwork;
        public static JobDef RM_BalmScar;
        static RM_AttarDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_AttarDefOf)); }
    }

    // Which artworks are glazed. Saved with the game.
    public class RM_GlazedRegistry : GameComponent
    {
        private List<int> ids = new List<int>();
        public RM_GlazedRegistry(Game game) { }
        public static RM_GlazedRegistry Instance => Current.Game?.GetComponent<RM_GlazedRegistry>();
        public bool IsGlazed(Thing t) => t != null && ids.Contains(t.thingIDNumber);
        public void Add(Thing t) { if (t != null && !ids.Contains(t.thingIDNumber)) ids.Add(t.thingIDNumber); }
        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref ids, "glazedArtworkIds", LookMode.Value);
            if (ids == null) ids = new List<int>();
        }
    }

    // Added to the Beauty stat by Patches/RM_Attar_BeautyPart.xml.
    public class StatPart_Glazed : StatPart
    {
        public const float Bonus = RM_MiasmaKernel.GlazeBonus;
        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!RM_MiasmaSettings.attarEnabled || !req.HasThing) return;
            if (RM_GlazedRegistry.Instance != null && RM_GlazedRegistry.Instance.IsGlazed(req.Thing))
                val += Bonus;
        }
        public override string ExplanationPart(StatRequest req)
        {
            if (RM_MiasmaSettings.attarEnabled && req.HasThing && RM_GlazedRegistry.Instance != null
                && RM_GlazedRegistry.Instance.IsGlazed(req.Thing))
                return "Attar glaze: +" + Bonus.ToString("0.#");
            return null;
        }
    }

    public static class RM_AttarUtil
    {
        public static bool IsGlazable(Thing t)
        {
            if (t == null || t.def.category != ThingCategory.Building || t.TryGetComp<CompArt>() == null) return false;
            RM_GlazedRegistry reg = RM_GlazedRegistry.Instance;
            return reg != null && !reg.IsGlazed(t);
        }

        public static Hediff_Injury FirstScar(Pawn p)
        {
            if (p?.health?.hediffSet == null) return null;
            return p.health.hediffSet.hediffs.OfType<Hediff_Injury>().FirstOrDefault(h => h.IsPermanent());
        }

        public static void Balm(Pawn p)
        {
            Hediff_Injury scar = FirstScar(p);
            if (scar == null) return;
            scar.Severity = RM_MiasmaKernel.BalmScar(scar.Severity, out bool removed);
            if (removed) p.health.RemoveHediff(scar);
        }
    }

    public class FloatMenuOptionProvider_UseAttar : FloatMenuOptionProvider
    {
        protected override bool Drafted => false;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!RM_MiasmaSettings.attarEnabled) return null;
            Pawn actor = context.FirstSelectedPawn;
            if (actor == null || RM_AttarDefOf.RM_Attar == null) return null;
            JobDef jd; string label;
            if (clickedThing is Pawn target)
            {
                if (RM_AttarUtil.FirstScar(target) == null) return null;
                jd = RM_AttarDefOf.RM_BalmScar;
                label = "Apply attar balm to " + target.LabelShort;
            }
            else if (RM_AttarUtil.IsGlazable(clickedThing))
            {
                jd = RM_AttarDefOf.RM_GlazeArtwork;
                label = "Glaze " + clickedThing.LabelShort + " with attar";
            }
            else return null;

            Thing attar = GenClosest.ClosestThingReachable(actor.Position, actor.Map,
                ThingRequest.ForDef(RM_AttarDefOf.RM_Attar), PathEndMode.ClosestTouch, TraverseParms.For(actor),
                9999f, t => !t.IsForbidden(actor) && actor.CanReserve(t));
            if (attar == null) return new FloatMenuOption(label + " (no attar)", null);
            if (!actor.CanReach(clickedThing, PathEndMode.Touch, Danger.Deadly))
                return new FloatMenuOption(label + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(label, delegate
            {
                Job job = JobMaker.MakeJob(jd, attar, clickedThing);
                job.count = 1;
                actor.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }), actor, clickedThing);
        }
    }

    // A = the attar, B = the artwork or the pawn.
    public class JobDriver_UseAttar : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, 1, null, errorOnFailed)
                && pawn.Reserve(job.targetB, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.B);
            this.FailOn(() => !RM_MiasmaSettings.attarEnabled);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch).FailOnDespawnedNullOrForbidden(TargetIndex.A);
            yield return Toils_Haul.StartCarryThing(TargetIndex.A);
            yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch);
            Toil work = Toils_General.Wait(240).WithProgressBarToilDelay(TargetIndex.B);
            work.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
            yield return work;
            yield return new Toil
            {
                initAction = delegate
                {
                    Thing carried = pawn.carryTracker.CarriedThing;
                    if (carried == null) return;
                    Thing target = job.targetB.Thing;
                    if (job.def == RM_AttarDefOf.RM_BalmScar)
                    {
                        if (!(target is Pawn p) || RM_AttarUtil.FirstScar(p) == null) return;
                        RM_AttarUtil.Balm(p);
                    }
                    else
                    {
                        if (!RM_AttarUtil.IsGlazable(target)) return;
                        RM_GlazedRegistry.Instance.Add(target);
                    }
                    carried.SplitOff(1).Destroy();
                },
                defaultCompleteMode = ToilCompleteMode.Instant
            };
        }
    }
}
