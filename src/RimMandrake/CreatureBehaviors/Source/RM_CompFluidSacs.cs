using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // DEEPS_FAUNA_MECHANICS_1. Attach to a race's OWN ThingDef (the drinker,
    // never the victim). Fed by RM_Hediff_Drained.PostAdd, which fires on
    // whatever this pawn just bit — content-blind on both ends: this comp
    // never names a species, and the marker hediff that calls it can ride
    // ANY bite DamageDef via <additionalHediffs> (already wired onto the
    // shared RSW_BloodSuck DamageDef for the Deeps' proboscis fauna).
    //
    //   <comps>
    //     <li Class="RimMandrake.CreatureBehaviors.RM_CompProperties_FluidSacs">
    //       <poisonousFleshTypes><li>Normal</li></poisonousFleshTypes>
    //       <poisonHediff>RM_FluidSacPoison</poisonHediff>
    //     </li>
    //   </comps>
    public class RM_CompFluidSacs : ThingComp
    {
        public RM_CompProperties_FluidSacs Props => (RM_CompProperties_FluidSacs)props;

        /// <summary>Called by RM_Hediff_Drained.PostAdd on the VICTIM's
        /// marker hediff, with `victim` being the pawn this comp's owner
        /// just bit and `severity` being that marker hediff's own severity
        /// (severityPerDamageDealt * the bite's actual damage dealt — a
        /// direct read of how much was drained this hit).</summary>
        public void Notify_Fed(Pawn victim, float severity)
        {
            if (!RM_CreatureBehaviorsSettings.drinkerFluidSacsEnabled)
            {
                return;
            }

            if (!(parent is Pawn self) || !self.Spawned || self.Dead || self.health == null)
            {
                return;
            }

            if (victim == null || severity <= 0f)
            {
                return;
            }

            if (IsPoisonous(victim))
            {
                ApplyPoison(self, severity);
                return;
            }

            RestoreHunger(self, severity);
        }

        private bool IsPoisonous(Pawn victim)
        {
            if (Props.poisonousFleshTypes.NullOrEmpty() || Props.poisonHediff == null)
            {
                return false;
            }

            FleshTypeDef victimFlesh = victim.RaceProps?.FleshType;
            if (victimFlesh == null)
            {
                return false; // no flesh type (e.g. a mechanoid) — not "warm iron blood", never poisons
            }

            return Props.poisonousFleshTypes.Contains(victimFlesh);
        }

        private void ApplyPoison(Pawn self, float severity)
        {
            float mult = UnityEngine.Mathf.Max(0f, RM_CreatureBehaviorsSettings.drinkerPoisonMultiplier);
            if (mult <= 0f)
            {
                return; // mod option: poison scaled to zero — a bad bite is simply not fed, same as any other unwanted meal
            }

            Hediff hediff = HediffMaker.MakeHediff(Props.poisonHediff, self);
            self.health.AddHediff(hediff);

            // Literal, not a translation key: this mod ships no Languages/
            // folder (same posture as RM_CompPlantAlarm's own inspect string).
            Messages.Message(self.LabelShortCap + "'s fluid sacs curdle — that blood was never meant for it.",
                self, MessageTypeDefOf.NegativeEvent);
        }

        private void RestoreHunger(Pawn self, float severity)
        {
            if (self.needs?.food == null)
            {
                return;
            }

            float amount = Props.hungerRestoredPerSeverity * severity;
            if (amount <= 0f)
            {
                return;
            }

            self.needs.food.CurLevel = UnityEngine.Mathf.Min(self.needs.food.MaxLevel, self.needs.food.CurLevel + amount);
        }
    }
}
