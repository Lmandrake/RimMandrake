using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ════════════════════════════════════════════════════════════════════
    // ROT_LIVE_PREPARATIONS_1, M4's bioregeneration tea.
    //
    // WHY THIS EXISTS RATHER THAN THE VANILLA COMP. The spec's route was
    // "XML if HediffComp_HealPermanentWounds can ride a temporary hediff".
    // VERIFIED THIS PASS (RimSage, Source/Verse/HediffComp_HealPermanentWounds.cs):
    // it CAN ride any HediffWithComps, but its interval is hardcoded —
    //
    //     private void ResetTicksToHeal() { ticksToHeal = Rand.Range(15, 30) * 60000; }
    //
    // — 15 to 30 DAYS, with no Props field to shorten it (luciferium is
    // permanent, so vanilla never needed one). On a tea whose hediff lasts
    // ~5 days that is a 0% chance of ever firing: the XML route would have
    // shipped a tea that verifiably does nothing. Hence this comp, which is
    // the vanilla one with the interval as a field and the actual healing
    // delegated to vanilla's own public static
    // HediffComp_HealPermanentWounds.TryHealRandomPermanentWound — the same
    // selection rule (IsPermanent() || def.chronic), the same HealthUtility.Cure,
    // the same player message. Nothing about WHAT gets healed is reimplemented.
    // ════════════════════════════════════════════════════════════════════
    public class RM_HediffCompProperties_HealPermanentWounds : HediffCompProperties
    {
        // Days between heal attempts. The tea's own INVENTED-BUILD tuning
        // lives in the HediffDef, not here — this default is only a sane
        // fallback if a def omits it.
        public float daysBetweenHeals = 1f;

        // Heal once immediately on gaining the hediff, so a brew drunk for
        // a specific scar pays off before the drinker can wonder whether it
        // worked at all.
        public bool healOnGain = true;

        public RM_HediffCompProperties_HealPermanentWounds()
        {
            compClass = typeof(RM_HediffComp_HealPermanentWounds);
        }
    }

    public class RM_HediffComp_HealPermanentWounds : HediffComp
    {
        private int ticksToHeal;

        public RM_HediffCompProperties_HealPermanentWounds Props =>
            (RM_HediffCompProperties_HealPermanentWounds)props;

        private int IntervalTicks
        {
            get
            {
                int ticks = (int)(Props.daysBetweenHeals * 60000f);
                return ticks < 1 ? 1 : ticks;
            }
        }

        public override void CompPostMake()
        {
            base.CompPostMake();
            ticksToHeal = Props.healOnGain ? 1 : IntervalTicks;
        }

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);

            Pawn pawn = base.Pawn;
            if (pawn == null || pawn.Dead)
            {
                return;
            }

            ticksToHeal -= delta;
            if (ticksToHeal > 0)
            {
                return;
            }

            ticksToHeal = IntervalTicks;
            HediffComp_HealPermanentWounds.TryHealRandomPermanentWound(pawn, parent.LabelCap);
        }

        public override void CompExposeData()
        {
            base.CompExposeData();
            Scribe_Values.Look(ref ticksToHeal, "ticksToHeal", 0);
        }

        public override string CompDebugString()
        {
            return "ticksToHeal: " + ticksToHeal;
        }
    }
}
