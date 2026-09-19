using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1. Scans for pawns too close and psychically
    // stuns them — wild-only by design: a pawn sharing the carrier's OWN
    // faction is skipped, so once tamed (Faction == OfPlayer) its own
    // colonists stop tripping the stun and RM_CompTameSootheAura's soothing
    // effect takes over for them instead, matching the owner's own split
    // ("emits a stun on anyone that gets too close" while wild; "taming one
    // produces a soothing effect" once owned) without any special-casing —
    // a wild carrier has no faction, so EVERY pawn (including a wandering
    // colonist) is "not same faction" and gets stunned, same as the spec.
    public class RM_CompProximityPsychicStun : ThingComp
    {
        private int lastTriggerTick = -999999;

        public RM_CompProperties_ProximityPsychicStun Props => (RM_CompProperties_ProximityPsychicStun)props;

        public override void CompTickRare()
        {
            base.CompTickRare();

            if (!RM_CreatureBehaviorsSettings.soulchimePsychicStunEnabled)
            {
                return;
            }

            if (!(parent is Pawn self) || !self.Spawned || self.Dead || self.Map == null)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            if (now - lastTriggerTick < Props.cooldownTicks)
            {
                return;
            }

            float radiusSq = Props.radius * Props.radius;
            bool stunnedAny = false;

            List<Pawn> pawns = new List<Pawn>(self.Map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn candidate = pawns[i];
                if (candidate == self || candidate.Dead || candidate.Downed || candidate.health == null)
                {
                    continue;
                }

                if (candidate.Faction != null && self.Faction != null && candidate.Faction == self.Faction)
                {
                    continue; // this carrier's own people — soothed, not stunned (RM_CompTameSootheAura)
                }

                if ((candidate.Position - self.Position).LengthHorizontalSquared > radiusSq)
                {
                    continue;
                }

                if (candidate.health.hediffSet.HasHediff(Props.stunHediff))
                {
                    continue; // already reeling from this — don't pile on every rare-tick
                }

                Hediff hediff = HediffMaker.MakeHediff(Props.stunHediff, candidate);
                hediff.Severity = Props.stunSeverity;
                candidate.health.AddHediff(hediff);
                stunnedAny = true;
            }

            if (stunnedAny)
            {
                lastTriggerTick = now;

                if (Props.alsoRingPlantAlarm)
                {
                    parent.GetComp<RM_CompPlantAlarm>()?.TriggerAlarm();
                }
            }
        }
    }
}
