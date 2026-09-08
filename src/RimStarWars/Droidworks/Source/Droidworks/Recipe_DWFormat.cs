using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_FORMAT_TIERS_1. Shared machinery for the three format recipes.
    /// Each concrete subclass names ONE target tier; eligibility is "is a droid, and
    /// is not already there (or below, for the downward ones)".
    ///
    /// Whole-pawn, targetsBodyPart=false - so, exactly as Recipe_RebootDroid.cs's
    /// header records, GetPartsToApplyOn is a DEAD GATE for these recipes and the
    /// real gates are AvailableOnNow and CompletableEver. Both are overridden.
    ///
    /// There is deliberately NO recipe that formats a droid UP to Sapient. Sapience
    /// is what a long-unwiped droid drifts INTO (DROIDWORKS_SERVICE_RECORD_DRIFT_1,
    /// packet E2) - the head-gate ruling (ruling 6) exists precisely so a bench
    /// cannot manufacture a mind. Formatting can only ever restore a droid to
    /// working order, cripple it, or blank it.
    /// </summary>
    public abstract class Recipe_DWFormatBase : Recipe_Surgery
    {
        protected abstract DroidFormatTier TargetTier { get; }

        protected virtual bool ApplicableFrom(DroidFormatTier current) => current != TargetTier;

        public override IEnumerable<BodyPartRecord> GetPartsToApplyOn(Pawn pawn, RecipeDef recipe)
        {
            yield return null;
        }

        private bool EligibleNow(Thing thing) =>
            thing is Pawn p
            && DroidFormatTierUtility.IsDroid(p)
            && ApplicableFrom(DroidFormatTierUtility.EffectiveTierOf(p));

        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null) =>
            base.AvailableOnNow(thing, part) && EligibleNow(thing);

        public override bool CompletableEver(Pawn surgeryTarget) => EligibleNow(surgeryTarget);

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            DroidFormatTier before = DroidFormatTierUtility.EffectiveTierOf(pawn);
            DroidFormatTierUtility.SetTier(pawn, TargetTier);

            // "Deformat sapient = murder thought per faction ethics" (packet B1;
            // build spec unit 9). Fired for ANY operation that takes a droid that
            // WAS sapient below the programmable rung - deformatting to blank and
            // restrictive-formatting to mindless destroy that mind equally, and the
            // spec's own reason ("which is exactly why deformatting a sapient is
            // killing someone", droid_system_spec.md section 5) does not
            // distinguish between them. JUDGEMENT CALL: the design text names only
            // deformatting; extending it to the restrictive format is ours, and is
            // recorded in infrastructure/state/items/DROIDWORKS_FORMAT_TIERS_1.md.
            if (before == DroidFormatTier.Sapient && TargetTier < DroidFormatTier.Programmable)
            {
                NotifySapientMindDestroyed(pawn, billDoer);
            }
        }

        /// <summary>
        /// The two vanilla-native consequence routes, in the exact idiom vanilla
        /// itself uses for a moral violation on the operating table (read from
        /// RimWorld.ThoughtUtility.GiveThoughtsForPawnOrganHarvested and
        /// RimWorld.Recipe_RemoveBodyPart.ApplyOnPawn):
        ///
        ///  1. A HistoryEvent, which is how EVERY 1.6 witness reaction reaches a
        ///     pawn - vanilla has no non-ideoligious witness-thought path left; the
        ///     thought comes from a PreceptComp_KnowsMemoryThought on whichever
        ///     ideoligion cares.
        ///  2. ReportViolation against the droid's home faction, scaled by that
        ///     faction's DeformatStance.
        ///
        /// 🔴 CONSEQUENCE OF (1): with Ideology active and NO precept wired to this
        /// event, no colonist feels anything. That precept is campaign data
        /// (RimUtinni ideoligions), not platform - see the item file. The direct
        /// memory below is therefore applied ONLY when Ideology is inactive, so the
        /// mechanism works in a no-Ideology load without double-counting against a
        /// precept in a load that has one.
        /// </summary>
        private void NotifySapientMindDestroyed(Pawn pawn, Pawn billDoer)
        {
            if (billDoer != null)
            {
                Find.HistoryEventsManager.RecordEvent(
                    new HistoryEvent(DroidworksDefOf.RSW_DW_DeformattedSapientDroid,
                                     billDoer.Named(HistoryEventArgsNames.Doer)));
            }

            Faction home = pawn.HomeFaction;
            int impact = DroidEthicsExtension.GoodwillImpactFor(DroidEthicsExtension.StanceOf(home));
            if (impact != 0)
            {
                ReportViolation(pawn, billDoer, home, impact,
                                DroidworksDefOf.RSW_DW_DeformattedSapientDroid);
            }

            if (!ModsConfig.IdeologyActive)
            {
                GiveFallbackWitnessThought(pawn, billDoer);
            }
        }

        private static void GiveFallbackWitnessThought(Pawn victim, Pawn billDoer)
        {
            Map map = billDoer?.MapHeld ?? victim?.MapHeld;
            if (map == null) return;

            foreach (Pawn witness in map.mapPawns.FreeColonistsSpawned.ToList())
            {
                if (witness == billDoer || witness == victim) continue;
                witness.needs?.mood?.thoughts?.memories?.TryGainMemory(
                    DroidworksDefOf.RSW_DW_KnowSapientDroidDeformatted);
            }
        }
    }

    /// <summary>
    /// Restore working programming: blank or mindless -> programmable. Not a
    /// violation - this is the repair, not the harm.
    /// </summary>
    public class Recipe_DWFormatStandard : Recipe_DWFormatBase
    {
        protected override DroidFormatTier TargetTier => DroidFormatTier.Programmable;

        // Only ever an upgrade. A sapient droid is NOT offered this: pushing a
        // sapient down to programmable is a mind-narrowing, which is what the
        // restrictive format is for, and silently hiding that behind a
        // benign-sounding "format" would launder the violation.
        protected override bool ApplicableFrom(DroidFormatTier current) =>
            current < DroidFormatTier.Programmable;
    }

    /// <summary>
    /// The restrictive format: anything above -> mindless. "A reduced state due to
    /// damage, hacking, or a deeply restrictive restraining bolt" (sheet row
    /// abf_formatting) - here, done deliberately at the bench.
    /// </summary>
    public class Recipe_DWRestrictiveFormat : Recipe_DWFormatBase
    {
        protected override DroidFormatTier TargetTier => DroidFormatTier.Mindless;

        protected override bool ApplicableFrom(DroidFormatTier current) =>
            current > DroidFormatTier.Mindless;
    }

    /// <summary>
    /// Deformat: anything -> blank. "The standby chassis after deformatting, no
    /// programming at all, ready to reformat" (droid_system_spec.md section 5).
    /// </summary>
    public class Recipe_DWDeformat : Recipe_DWFormatBase
    {
        protected override DroidFormatTier TargetTier => DroidFormatTier.Blank;

        protected override bool ApplicableFrom(DroidFormatTier current) =>
            current > DroidFormatTier.Blank;
    }
}
