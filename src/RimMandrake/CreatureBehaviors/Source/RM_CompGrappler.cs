using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1. The GRABBER-side half of the hold: crush
    // damage each round, and the rescue roll when a third pawn hits it.
    // See RM_CompProperties_Grappler for the XML shape and tuning.
    //
    // Seams (RimSage-verified this pass, RimWorld 1.6 decompile):
    //   - ThingComp.PostPostApplyDamage(DamageInfo, float totalDamageDealt)
    //     — called from ThingWithComps.PostApplyDamage (ThingWithComps.cs
    //     l.394) after the grabber's own damage is applied, the same seam
    //     RM_CompWoundLink already uses.
    //   - DamageInfo(DamageDef, float amount, float armorPenetration, float
    //     angle, Thing instigator, BodyPartRecord hitPart, ...) —
    //     DamageInfo.cs l.144; BodyDef.corePart (BodyDef.cs l.8) is the
    //     torso-equivalent of any race body.
    //
    // Calling Pawn.TakeDamage on the VICTIM from the GRABBER's CompTick is
    // safe — it is not inside the victim's HediffSet tick loop (the
    // re-entrancy hazard RM_Hediff_Grappled's own header avoids by never
    // dealing damage from inside its own Tick).
    public class RM_CompGrappler : ThingComp
    {
        private int ticksUntilRound;

        public RM_CompProperties_Grappler Props => (RM_CompProperties_Grappler)props;

        public override void CompTick()
        {
            base.CompTick();

            if (!RM_CreatureBehaviorsSettings.grapplerHoldEnabled)
            {
                return;
            }

            ticksUntilRound--;
            if (ticksUntilRound > 0)
            {
                return;
            }
            ticksUntilRound = Props.crushIntervalTicks;

            if (!(parent is Pawn self) || !self.Spawned || self.Dead || self.Downed || self.Map == null)
            {
                return;
            }

            if (self.MentalStateDef == MentalStateDefOf.PanicFlee)
            {
                return; // a fleeing grabber isn't squeezing anyone; the hold releases on distance anyway
            }

            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.grapplerCrushMultiplier);
            float amount = Props.crushDamage * mult;
            if (amount <= 0f)
            {
                return;
            }

            float radiusSq = Props.crushRadius * Props.crushRadius;
            List<RM_Hediff_Grappled> holds = Holds(self);
            for (int i = 0; i < holds.Count; i++)
            {
                Pawn victim = holds[i].pawn;
                if (victim == null || victim.Dead || !victim.Spawned)
                {
                    continue;
                }
                if ((victim.Position - self.Position).LengthHorizontalSquared > radiusSq)
                {
                    continue; // the hediff's own Tick releases on distance; don't crush across the room
                }

                BodyPartRecord torso = victim.RaceProps?.body?.corePart;
                DamageDef def = Props.crushDamageDef ?? DamageDefOf.Blunt;
                victim.TakeDamage(new DamageInfo(def, amount, Props.crushArmorPenetration, -1f, self, torso));
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);

            if (!RM_CreatureBehaviorsSettings.grapplerHoldEnabled || totalDamageDealt <= 0f)
            {
                return;
            }

            if (!(parent is Pawn self) || !(dinfo.Instigator is Pawn attacker) || attacker == self)
            {
                return;
            }

            if (!self.Spawned || self.Map == null)
            {
                return;
            }

            List<RM_Hediff_Grappled> holds = Holds(self);
            if (holds.Count == 0)
            {
                return;
            }

            for (int i = 0; i < holds.Count; i++)
            {
                if (holds[i].pawn == attacker)
                {
                    return; // a held pawn's own struggle is RM_HediffDef_Grapple.escapeChancePerRound, not this roll
                }
            }

            for (int i = 0; i < holds.Count; i++)
            {
                if (!Rand.Chance(Props.breakHoldChanceOnHit))
                {
                    continue;
                }

                Pawn victim = holds[i].pawn;
                // Literal, not a translation key: this mod ships no Languages/
                // folder (same posture as RM_CompPlantAlarm's own inspect string).
                Messages.Message(attacker.LabelShortCap + " breaks " + self.LabelShort + "'s hold on " + victim.LabelShort + "!",
                    victim, MessageTypeDefOf.PositiveEvent);
                holds[i].ReleaseHold();
            }
        }

        /// <summary>Every live RM_Hediff_Grappled on this map whose grappler
        /// is <paramref name="self"/>. A scan, not a registry: it runs once
        /// per crush round (default every 2 s) or per hit taken, and a
        /// registry would need re-deriving on load anyway since the hediff
        /// on the victim is what the save actually stores.</summary>
        private static List<RM_Hediff_Grappled> Holds(Pawn self)
        {
            List<RM_Hediff_Grappled> result = new List<RM_Hediff_Grappled>();
            IReadOnlyList<Pawn> pawns = self.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn candidate = pawns[i];
                if (candidate == self || candidate.Dead || candidate.health == null)
                {
                    continue;
                }

                List<Hediff> hediffs = candidate.health.hediffSet.hediffs;
                for (int j = 0; j < hediffs.Count; j++)
                {
                    if (hediffs[j] is RM_Hediff_Grappled hold && hold.Grappler == self)
                    {
                        result.Add(hold);
                        break;
                    }
                }
            }
            return result;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksUntilRound, "ticksUntilRound", 0);
        }
    }
}
