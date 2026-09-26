using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §4.1's thoughts, minus the two that need room stats over painted
    // furniture (RM_DeepfireBedroom, RM_ImpressedByDeepfire) -- both wait on
    // CompDeepfire/floor coats (piece 1, painting), deferred to
    // DEEPFIRE_PAINT_LIVE_VERIFY_1. The three here only need worn apparel /
    // equipped weapons, so they work today even though nothing is tagged
    // with StatusGoodExtension yet (score is always 0 -> every worker
    // returns Inactive -- the engine is present, real, and silent).
    public abstract class ThoughtWorker_DeepfireStatusBase : ThoughtWorker
    {
        protected abstract bool RequireTitled { get; }

        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!LuminousPigmentSettings.statusEnabled) return ThoughtState.Inactive;
            bool titled = SumptuaryUtility.IsTitled(p);
            if (titled != RequireTitled) return ThoughtState.Inactive;
            if (!RequireTitled && !SumptuaryUtility.RanklessColonyThoughtAllowed()) return ThoughtState.Inactive;

            int score = SumptuaryUtility.DisplayScoreFor(p);
            if (score <= 0) return ThoughtState.Inactive;
            int stage = score >= 5 ? 2 : (score >= 3 ? 1 : 0);
            return ThoughtState.ActiveAtStage(stage);
        }
    }

    // RM_WearingDeepfireTitled: +3/+5/+8 by display score bucket 1-2/3-4/5-6.
    public class ThoughtWorker_DeepfireStatusTitled : ThoughtWorker_DeepfireStatusBase
    {
        protected override bool RequireTitled => true;
    }

    // RM_WearingDeepfireCommon: +1/+2/+3 by the same buckets.
    public class ThoughtWorker_DeepfireStatusCommon : ThoughtWorker_DeepfireStatusBase
    {
        protected override bool RequireTitled => false;
    }

    // RM_WearsAboveStation (social): a titled pawn's opinion of a commoner
    // whose display score meets offenceThreshold. Opinion -15, one stage.
    public class ThoughtWorker_WearsAboveStation : ThoughtWorker
    {
        protected override ThoughtState CurrentSocialStateInternal(Pawn p, Pawn otherPawn)
        {
            if (!LuminousPigmentSettings.statusEnabled) return ThoughtState.Inactive;
            if (!SumptuaryUtility.IsTitled(p)) return ThoughtState.Inactive;
            if (SumptuaryUtility.IsTitled(otherPawn)) return ThoughtState.Inactive;
            if (SumptuaryUtility.DisplayScoreFor(otherPawn) < LuminousPigmentSettings.offenceThreshold)
            {
                return ThoughtState.Inactive;
            }
            return ThoughtState.ActiveAtStage(0);
        }
    }

    // RM_SawCommonerInDeepfire: a titled pawn on a map holding any commoner
    // over the offence threshold takes the mood hit (spec: "same map,
    // Notify_Seen-free -- evaluated on the situational-thought tick").
    public class ThoughtWorker_SawCommonerInDeepfire : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!LuminousPigmentSettings.statusEnabled) return ThoughtState.Inactive;
            if (!SumptuaryUtility.IsTitled(p)) return ThoughtState.Inactive;

            Map map = p.MapHeld;
            if (map == null) return ThoughtState.Inactive;

            foreach (Pawn other in map.mapPawns.AllPawnsSpawned)
            {
                if (other == p || !other.RaceProps.Humanlike) continue;
                if (SumptuaryUtility.IsTitled(other)) continue;
                if (SumptuaryUtility.DisplayScoreFor(other) >= LuminousPigmentSettings.offenceThreshold)
                {
                    return ThoughtState.ActiveAtStage(0);
                }
            }
            return ThoughtState.Inactive;
        }
    }
}
