using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1. Only acts once the carrier is owned by the
    // player (Faction == Faction.OfPlayer) — a wild carrier never soothes
    // anyone, matching "TAMING one produces a soothing effect", and is the
    // direct counterpart to RM_CompProximityPsychicStun's own "same faction
    // is exempt from the stun" rule: together the two comps mean a wild
    // carrier stuns everyone that gets close (including a wandering
    // colonist) and a tamed one stuns nobody of its own faction while
    // actively soothing them instead.
    public class RM_CompTameSootheAura : ThingComp
    {
        public RM_CompProperties_TameSootheAura Props => (RM_CompProperties_TameSootheAura)props;

        public override void CompTickRare()
        {
            base.CompTickRare();

            if (!RM_CreatureBehaviorsSettings.soulchimeTameSootheEnabled)
            {
                return;
            }

            if (!(parent is Pawn self) || !self.Spawned || self.Dead || self.Map == null)
            {
                return;
            }

            if (self.Faction != Faction.OfPlayer)
            {
                return; // wild — nothing to soothe (and RM_CompProximityPsychicStun handles this case instead)
            }

            float radiusSq = Props.radius * Props.radius;
            List<Pawn> colonists = self.Map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < colonists.Count; i++)
            {
                Pawn colonist = colonists[i];
                if (colonist.Dead || colonist.needs?.mood == null)
                {
                    continue;
                }

                if ((colonist.Position - self.Position).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                colonist.needs.mood.thoughts.memories.TryGainMemory(Props.sootheThought);
            }
        }
    }
}
