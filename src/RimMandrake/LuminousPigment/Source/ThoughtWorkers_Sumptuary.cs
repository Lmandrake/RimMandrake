using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §4.1's thoughts. The wearer/observer four read
    // SumptuaryUtility.DisplayScoreFor (CompDeepfire coats on worn apparel
    // and the primary weapon, plus any StatusGoodExtension good).
    // RM_DeepfireBedroom reads the room display score
    // (MapComponent_DeepfireStatus.CachedRoomScore). RM_ImpressedByDeepfire
    // is goodwill, not a thought: MapComponent_DeepfireStatus.
    public abstract class ThoughtWorker_DeepfireStatusBase : ThoughtWorker
    {
        protected abstract bool RequireTitled { get; }

        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!LuminousPigmentSettings.statusEnabled) return ThoughtState.Inactive;
            bool titled = SumptuaryUtility.IsTitled(p);
            if (titled != RequireTitled) return ThoughtState.Inactive;
            if (!RequireTitled && !SumptuaryUtility.RanklessColonyThoughtAllowed()) return ThoughtState.Inactive;

            int stage = RM_DeepfireRules.ScoreStage(SumptuaryUtility.DisplayScoreFor(p));
            return stage < 0 ? ThoughtState.Inactive : ThoughtState.ActiveAtStage(stage);
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

    // RM_DeepfireBedroom: a titled pawn whose bedroom or throne room has a
    // room display score >= BedroomScoreLow (+4) / >= BedroomScoreHigh (+6).
    // The better of the two rooms counts. Royalty's own throne-room
    // requirements are untouched.
    public class ThoughtWorker_DeepfireBedroom : ThoughtWorker
    {
        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            if (!LuminousPigmentSettings.statusEnabled) return ThoughtState.Inactive;
            if (!SumptuaryUtility.IsTitled(p)) return ThoughtState.Inactive;
            int score = BestOwnRoomScore(p);
            int stage = RM_DeepfireRules.BedroomStage(true, true, score, DeepfireStatusDefaults.BedroomScoreLow, DeepfireStatusDefaults.BedroomScoreHigh);
            return stage < 0 ? ThoughtState.Inactive : ThoughtState.ActiveAtStage(stage);
        }

        public static int BestOwnRoomScore(Pawn p)
        {
            if (p?.ownership == null) return 0;
            int best = 0;
            Room bedroom = p.ownership.OwnedRoom;
            if (bedroom != null) best = MapComponent_DeepfireStatus.CachedRoomScore(bedroom);
            Building_Throne throne = p.ownership.AssignedThrone;
            if (throne != null && throne.Spawned)
            {
                Room throneRoom = throne.GetRoom();
                if (throneRoom != null && throneRoom != bedroom)
                {
                    int s = MapComponent_DeepfireStatus.CachedRoomScore(throneRoom);
                    if (s > best) best = s;
                }
            }
            return best;
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
