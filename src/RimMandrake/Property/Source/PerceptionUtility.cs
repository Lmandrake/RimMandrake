using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Property
{
    // Spec item 6's witness half, built SIMPLE per the item brief: "a
    // witness check + a stored suspect-confidence value that decays/
    // propagates on a slow tick or lazy read, whichever is simpler." This
    // is the one-time roll at the moment of the act (cheap: one pass over
    // spawned map pawns, called once per TakingEvent, never ticked). The
    // full "fixed security + ambient surveillance" half of spec item 6
    // (cameras, patrols, orbital eyes) is district/settlement prop content
    // — out of scope here; see PROPERTY_FABRIC_BUILD_1's status report for
    // the explicit defer.
    public static class PerceptionUtility
    {
        public static List<Pawn> RollWitnesses(Thing thing, Pawn actor, float radius = PropertyTuning.DefaultWitnessRadius)
        {
            var witnesses = new List<Pawn>();

            Map map = thing?.MapHeld ?? actor?.Map;
            if (map == null || thing == null) return witnesses;

            IntVec3 targetPos = thing.PositionHeld;
            IReadOnlyList<Pawn> allSpawned = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < allSpawned.Count; i++)
            {
                Pawn p = allSpawned[i];
                if (p == actor || p.Dead || p.Downed || !p.Awake()) continue;
                // Only a humanlike is capable of meaningfully reporting what
                // it saw — a wild animal, tamed livestock, insect or
                // mechanoid standing nearby is not a witness, even if it's
                // technically present and awake.
                if (p.RaceProps == null || !p.RaceProps.Humanlike) continue;
                if (!p.Position.InHorDistOf(targetPos, radius)) continue;
                if (!GenSight.LineOfSight(p.Position, targetPos, map)) continue;

                witnesses.Add(p);
            }
            return witnesses;
        }

        // Flat per-witness confidence for this pass. Real per-trait/
        // perception-stat/security-profile tuning is explicitly deferred
        // (spec's "Open tuning" closing line).
        public static float WitnessConfidence(Pawn witness, ClaimantRef actor)
        {
            return PropertyTuning.DefaultWitnessConfidence;
        }
    }
}
