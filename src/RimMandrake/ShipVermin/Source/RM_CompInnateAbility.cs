using RimWorld;
using Verse;

namespace RimMandrake.ShipVermin
{
    // ════════════════════════════════════════════════════════════════════
    // SHIPVERMIN_FREE_TIER_BEASTS_1 — grants an animal its one ability.
    //
    // RM-tier copy of SWBestiary's CompInnateAbility
    // (src/RimStarWars/SWBestiary/Source/BeastMechanics/CompInnateAbility.cs),
    // carried here so the free-tier fethrik gets its fuel spew exactly as the
    // canon fuel mite does, without this RM mod naming an RSW type.
    //
    // An animal has no Pawn_AbilityTracker unless something gives it one, so
    // the comp creates the tracker if it is missing and then grants the
    // ability. Once granted it is saved on the pawn like any other ability, so
    // the flag stops it being re-granted every rare tick. Gated by
    // ShipVerminSettings.fuelSpewEnabled (the SWBestiary copy reads its own
    // mod's setting instead).
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_InnateAbility : CompProperties
    {
        public AbilityDef ability;

        public RM_CompProperties_InnateAbility()
        {
            compClass = typeof(RM_CompInnateAbility);
        }
    }

    public class RM_CompInnateAbility : ThingComp
    {
        private bool granted;

        public RM_CompProperties_InnateAbility Props => (RM_CompProperties_InnateAbility)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref granted, "granted", defaultValue: false);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (granted || !ShipVerminSettings.fuelSpewEnabled)
            {
                return;
            }
            if (Props.ability == null)
            {
                granted = true;
                return;
            }
            if (!(parent is Pawn pawn))
            {
                return;
            }
            if (pawn.abilities == null)
            {
                pawn.abilities = new Pawn_AbilityTracker(pawn);
            }
            pawn.abilities.GainAbility(Props.ability);
            granted = true;
        }
    }
}
