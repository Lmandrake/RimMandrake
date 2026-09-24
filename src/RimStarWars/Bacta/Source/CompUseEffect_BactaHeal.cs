using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    /// <summary>
    /// The item-scale end of BACTA_SIDE_ITEMS_1: a bacta patch or spray applies ONE guarded
    /// healing dose via BactaHealingUtility.ApplyHealingDose — the exact mechanism
    /// CompBactaImmersion runs continuously in the tank, scaled down to a single burst. Same
    /// two laws, same code path: never regrows a missing part, never touches the brain or
    /// the mind.
    ///
    /// Wired the vanilla way: CompProperties_Usable (the "Use ..." float-menu/gizmo, vanilla
    /// CompUsable, JobDef UseItem) drives every CompUseEffect comp on the item when used —
    /// the exact shape Core's own MechSerumHealer ("healer mech serum") uses, verified against
    /// Data/Core/Defs/ThingDefs_Items/Items_Exotic.xml and RimWorld/CompUsable.cs,
    /// RimWorld/CompUseEffect.cs in the decompiled source.
    ///
    /// Deliberately NOT reusing Core's own CompUseEffect_FixWorstHealthCondition: that comp
    /// calls Verse.HealthUtility.FixWorstHealthCondition, which explicitly regrows the
    /// biggest missing body part (Cure(part, pawn)) and can select a permanent brain injury as
    /// the "worst condition" — exactly the two things bacta must never do (BACTA_TANK_CORE_1
    /// card 2, owner ruling). Hence this comp instead of that one.
    /// </summary>
    public class CompProperties_UseEffect_BactaHeal : CompProperties_UseEffect
    {
        /// <summary>Severity healed off every fresh wound/burn/organ injury, applied once.</summary>
        public float woundHealAmount = 6f;

        /// <summary>
        /// Severity removed from permanent injuries/scars, applied once. Only spent if
        /// scarErasureEnabled is also true on this comp — 0 by default because the field
        /// items are for fresh wounds, not old ones.
        /// </summary>
        public float scarHealAmount;

        /// <summary>Tend quality applied to any fresh wound this dose tends.</summary>
        public float tendQuality = 0.7f;

        /// <summary>Extra immunity granted to one treatable infection, applied once. 0 = does nothing for disease.</summary>
        public float immunityGainAmount;

        public bool scarErasureEnabled;

        public bool infectionAssistEnabled;

        public CompProperties_UseEffect_BactaHeal()
        {
            compClass = typeof(CompUseEffect_BactaHeal);
        }
    }

    public class CompUseEffect_BactaHeal : CompUseEffect
    {
        private CompProperties_UseEffect_BactaHeal FieldProps => (CompProperties_UseEffect_BactaHeal)props;

        public override AcceptanceReport CanBeUsedBy(Pawn p)
        {
            if (!BactaSettings.fieldItemsEnabled)
            {
                return "RSW_BactaFieldItemsDisabled".Translate();
            }
            if (!BactaHealingUtility.HasHealableCondition(p, FieldProps.scarErasureEnabled, FieldProps.infectionAssistEnabled))
            {
                return "RSW_BactaFieldNothingToHeal".Translate();
            }
            return true;
        }

        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);

            float potency = BactaSettings.fieldItemPotency;
            bool did = BactaHealingUtility.ApplyHealingDose(
                usedBy,
                FieldProps.woundHealAmount * potency,
                FieldProps.scarHealAmount * potency,
                FieldProps.tendQuality,
                FieldProps.immunityGainAmount * potency,
                FieldProps.scarErasureEnabled,
                FieldProps.infectionAssistEnabled);

            if (PawnUtility.ShouldSendNotificationAbout(usedBy))
            {
                Messages.Message(
                    (did ? "RSW_BactaFieldUsed" : "RSW_BactaFieldNothingHappened").Translate(usedBy.Named("PAWN")),
                    usedBy,
                    did ? MessageTypeDefOf.PositiveEvent : MessageTypeDefOf.NeutralEvent,
                    historical: false);
            }
        }
    }
}
