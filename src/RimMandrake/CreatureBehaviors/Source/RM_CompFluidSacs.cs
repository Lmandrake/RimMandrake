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

            FillSacks(self, severity);

            if (IsPoisonous(victim))
            {
                ApplyPoison(self, severity);
                return;
            }

            RestoreHunger(self, severity);
        }

        /// <summary>Raise the visible RM_FluidSacks gauge (a hediff on the
        /// drinker itself; its own maxSeverity caps it). The gauge decides
        /// how many drainedFluidsThing drop on death — see Notify_Killed.</summary>
        private void FillSacks(Pawn self, float severity)
        {
            if (Props.sacksHediff == null || Props.sackFillPerSeverity <= 0f)
            {
                return;
            }

            Hediff gauge = self.health.hediffSet.GetFirstHediffOfDef(Props.sacksHediff);
            if (gauge == null)
            {
                gauge = HediffMaker.MakeHediff(Props.sacksHediff, self);
                gauge.Severity = 0f;
                self.health.AddHediff(gauge);
            }

            gauge.Severity += Props.sackFillPerSeverity * severity;
        }

        /// <summary>Seam: ThingComp.Notify_Killed(Map prevMap, DamageInfo?)
        /// — called from ThingWithComps.Kill (l.318), which Pawn.Kill
        /// reaches through base.Kill (Pawn.cs l.3511). Drops the stored
        /// fluids next to the corpse: count = round(gauge severity *
        /// drainedFluidsAtFull). A drinker that never fed drops nothing.</summary>
        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            base.Notify_Killed(prevMap, dinfo);

            if (!RM_CreatureBehaviorsSettings.drinkerFluidSacsEnabled)
            {
                return;
            }

            if (Props.sacksHediff == null || Props.drainedFluidsThing == null || Props.drainedFluidsAtFull <= 0)
            {
                return;
            }

            if (!(parent is Pawn self) || self.health == null || prevMap == null)
            {
                return;
            }

            Hediff gauge = self.health.hediffSet.GetFirstHediffOfDef(Props.sacksHediff);
            if (gauge == null)
            {
                return;
            }

            int count = UnityEngine.Mathf.RoundToInt(gauge.Severity * Props.drainedFluidsAtFull);
            if (count <= 0)
            {
                return;
            }

            IntVec3 pos = self.PositionHeld;
            if (!pos.IsValid || !pos.InBounds(prevMap))
            {
                return;
            }

            Thing fluids = ThingMaker.MakeThing(Props.drainedFluidsThing);
            fluids.stackCount = count;
            GenPlace.TryPlaceThing(fluids, pos, prevMap, ThingPlaceMode.Near);
        }

        private bool IsPoisonous(Pawn victim)
        {
            if (Props.poisonousFleshTypes.NullOrEmpty() || Props.poisonHediff == null)
            {
                return false;
            }

            if (victim.def.HasModExtension<RM_HydrocarbonBloodExtension>())
            {
                return false; // flagged hydrocarbon blood — safe whatever its flesh type says
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
            hediff.Severity = severity * mult; // RM_FluidSacPoison_Hediffs.xml: "a big initial severity (set by RM_CompFluidSacs, not here)"
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
