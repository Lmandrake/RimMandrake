using RimWorld;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    // ════════════════════════════════════════════════════════════════════
    // PORTED_BEAST_MECHANICS_REBUILD_1 — the voltmaw's and the cindermite's
    // ranged weapon.
    //
    // Owner, 2026-09-20: "Rebuild in our c#."
    //
    // DESERT_FAMILY_PORT_EXECUTION_1 dropped
    // VEF.AnimalBehaviours.CompProperties_InitialAbility from RSW_Vozzik
    // (Alpha Animals' AA_TetraSlug) and RSW_Zhakka (VFE Insectoids 2's
    // VFEI2_Fuelmite). That comp is the ONLY reason those two creatures had a
    // ranged attack at all: everything else about the ability is a vanilla
    // AbilityDef. MEASURED from
    // vendor/mod_sources/VanillaExpandedFramework-main/Source/VEF/AnimalBehaviours/
    //   Comps/CompInitialAbility.cs
    //
    // An animal has no Pawn_AbilityTracker unless something gives it one, so
    // the comp creates the tracker if it is missing and then grants the
    // ability. Once granted it is saved on the pawn like any other ability, so
    // the flag stops it being re-granted every rare tick.
    //
    // DEPARTURE from the donor: it also kept a static HashSet of every
    // ability-using animal alive, which nothing in the current VEF source
    // reads except a draftable-animal gizmo helper. We do not carry it.
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_InnateAbility : CompProperties
    {
        public AbilityDef ability;

        public CompProperties_InnateAbility()
        {
            compClass = typeof(CompInnateAbility);
        }
    }

    public class CompInnateAbility : ThingComp
    {
        private bool granted;

        public CompProperties_InnateAbility Props => (CompProperties_InnateAbility)props;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref granted, "granted", defaultValue: false);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (granted || !RSW_BeastMechanicsSettings.innateAbilitiesEnabled)
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
