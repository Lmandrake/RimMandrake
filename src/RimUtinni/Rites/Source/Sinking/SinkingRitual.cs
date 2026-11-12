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
                if (t.Spawned && !t.Fogged() && SinkingGlue.PlanFor(t).accepted)
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
            // A REASON shows a disabled gizmo on that thing (see NineFaults.cs). Corpses and pawns that could be carried
            // to the tar (prisoners, the downed, animals) get the reason; free colonists and ordinary items get a plain
            // refusal so the rite does not hang a greyed button on everything.
            if (t is Corpse) return why;
            if (t is Pawn p && !(p.IsColonist && !p.Downed)) return why;
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
}
