// SUMP_SINKING_RITE_BUILD_1: the Sinking's ritual target filter and outcome worker (defs in Defs/RUT_Sinking.xml).
// Nothing is put on participants (no hediff, no stat): cohesion comes only from the outcome memories in the def.
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Utinni.Rites
{
    public class RUT_RitualObligationTargetWorker_SinkingOffering : RitualObligationTargetFilter
    {
        public RUT_RitualObligationTargetWorker_SinkingOffering() { }

        public RUT_RitualObligationTargetWorker_SinkingOffering(RitualObligationTargetFilterDef def) : base(def) { }

        public override IEnumerable<TargetInfo> GetTargets(RitualObligation obligation, Map map)
        {
            if (map == null || !RM_NinefoldSettings.sinkingEnabled) yield break;
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver).ToList())
            {
                // Cheap checks first (spawned, seen, an item, at the tar); MarketValue only for what is left.
                if (!t.Spawned || t.Fogged() || t.def.category != ThingCategory.Item || t is Corpse) continue;
                if (!SinkingGlue.NearTar(t)) continue;
                if (SinkingGlue.PlanFor(SinkingGlue.Facts(t, true)).accepted)
                    yield return t;
            }
        }

        /// <summary>Why <paramref name="t"/> cannot be sunk, or null when it can. Public so the proof reads the same words.</summary>
        public static string RefusalReason(Thing t)
        {
            if (t == null) return "nothing to sink";
            SinkingPlan plan = SinkingGlue.PlanFor(t);
            return plan.accepted ? null : plan.reason;
        }

        protected override RitualTargetUseReport CanUseTargetInternal(TargetInfo target, RitualObligation obligation)
        {
            if (!target.HasThing) return false;
            Thing t = target.Thing;
            string why = RefusalReason(t);
            if (why == null) return true;
            // A REASON shows a disabled gizmo on that thing (see NineFaults.cs). Only the colony's own people (its
            // faction's pawns, its prisoners, its slaves) and corpses get the reason; everything else, wild animals,
            // visitors and ordinary items included, gets a plain refusal so the rite hangs no greyed button on it.
            if (t is Corpse) return why;
            if (t is Pawn p && (p.Faction == Faction.OfPlayer || p.IsPrisonerOfColony || p.IsSlaveOfColony)) return why;
            return false;
        }

        public override IEnumerable<string> GetTargetInfos(RitualObligation obligation)
        {
            yield return "a thing of worth given to the tar: pitch, a find from the dig, or anything else of value (never a person or a body)";
        }
    }

    public class RUT_RitualOutcomeEffectWorker_Sinking : RitualOutcomeEffectWorker_FromQuality
    {
        public RUT_RitualOutcomeEffectWorker_Sinking() { }

        public RUT_RitualOutcomeEffectWorker_Sinking(RitualOutcomeEffectDef def) : base(def) { }

        protected override void ApplyExtraOutcome(Dictionary<Pawn, int> totalPresence, LordJob_Ritual jobRitual,
            RitualOutcomePossibility outcome, out string extraOutcomeDesc, ref LookTargets letterLookTargets)
        {
            extraOutcomeDesc = null;
            Map map = jobRitual?.Map;
            Thing offering = jobRitual?.selectedTarget.Thing;
            if (map == null || offering == null || offering.Destroyed) return;
            IntVec3 at = offering.PositionHeld;
            SinkingPlan plan = SinkingGlue.Apply(map, offering, out string text, ref letterLookTargets);
            if (!plan.accepted)
            {
                Messages.Message("The tar would not take it: " + plan.reason, MessageTypeDefOf.RejectInput, false);
                return;
            }
            extraOutcomeDesc = text;
            Messages.Message("The offering goes down into the tar, slowly, with one last bubble.",
                             new TargetInfo(at, map), MessageTypeDefOf.NeutralEvent, false);
        }
    }

    /// <summary>Quality from what is given: the offering's market value (MarketValue * stackCount) read through the def's
    /// curve, beside the participant count.</summary>
    public class RUT_RitualOutcomeComp_OfferingValue : RitualOutcomeComp_Quality
    {
        public override RitualOutcomeComp_Data MakeData() { return null; }

        public static float OfferingValue(Thing t) { return t == null || t.Destroyed ? 0f : t.MarketValue * t.stackCount; }

        public override float Count(LordJob_Ritual ritual, RitualOutcomeComp_Data data)
        {
            return OfferingValue(ritual?.selectedTarget.Thing);
        }

        public override QualityFactor GetQualityFactor(Precept_Ritual ritual, TargetInfo ritualTarget, RitualObligation obligation,
                                                       RitualRoleAssignments assignments, RitualOutcomeComp_Data data)
        {
            float value = OfferingValue(ritualTarget.Thing);
            float q = curve.Evaluate(value);
            return new QualityFactor
            {
                label = label.CapitalizeFirst(),
                count = value.ToStringMoney(),
                qualityChange = ExpectedOffsetDesc(q > 0f, q),
                positive = q > 0f,
                quality = q,
                priority = 0f,
            };
        }
    }

    /// <summary>The offering is forbidden when the rite starts (no hauler walks off with it mid-rite) and unforbidden in
    /// Cleanup if it is still there (the rite was cancelled or interrupted). Only a forbid this worker made is undone.</summary>
    public class RUT_RitualBehaviorWorker_Sinking : RitualBehaviorWorker
    {
        private static readonly HashSet<int> forbadeByUs = new HashSet<int>();

        public RUT_RitualBehaviorWorker_Sinking() { }

        public RUT_RitualBehaviorWorker_Sinking(RitualBehaviorDef def) : base(def) { }

        public override void Tick(LordJob_Ritual ritual)
        {
            base.Tick(ritual);
            Thing t = ritual?.selectedTarget.Thing;
            if (t == null || !t.Spawned || forbadeByUs.Contains(t.thingIDNumber)) return;
            if (t.IsForbidden(Faction.OfPlayer)) { forbadeByUs.Add(-t.thingIDNumber - 1); return; } // already forbidden: not ours to undo
            t.SetForbidden(true, false);
            forbadeByUs.Add(t.thingIDNumber);
        }

        public override void Cleanup(LordJob_Ritual ritual)
        {
            base.Cleanup(ritual);
            Thing t = ritual?.selectedTarget.Thing;
            if (t == null) return;
            bool ours = forbadeByUs.Remove(t.thingIDNumber);
            forbadeByUs.Remove(-t.thingIDNumber - 1);
            if (ours && !t.Destroyed) t.SetForbidden(false, false);
        }
    }
}
