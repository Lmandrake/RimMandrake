using System.Collections.Generic;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_DIANOGA_PRISON_1. XML shape for RM_CompCapturedSpecimen — the
    // "prison tank, not a pen" building (design sheet §6j/§6m, item's own
    // "build it GENERIC — it is the model for a whole class" note).
    //
    // ⭐ The item explicitly left "what the generic abstraction actually is"
    // as its own first unmade decision. THIS is that decision: one
    // CompProperties parameterised by occupant + product + upkeep + escape,
    // hung off a plain abstract Building base (RM_LivingCapturePodBase) —
    // never a bespoke ThingDef per captive species. A later venom/egg/blood
    // vessel (4a's own named candidates) reuses this same comp with a
    // different occupant/product set, not a new class.
    //
    // Every numeric field below is INVENTED tuning, flagged per-field — the
    // design sheet and the owner's 2026-09-23 rulings settle the SHAPE
    // (teaches/produces/escapes, the three-stage escape ladder, "advanced
    // training but only after release") but name no numbers for feed rate,
    // product rate, tank materials, or the damage fraction that triggers an
    // immediate escape roll. Real tuning is owed to
    // FEVERWOOD_DIANOGA_TANK_TUNING_1, same posture as the tentacle
    // bestiary's own FEVERWOOD_TENTACLE_SETPIECE_TUNING_1.
    //
    //   <comps>
    //     <li Class="RimMandrake.FeverWood.RM_CompProperties_CapturedSpecimen">
    //       <occupantKindDefName>RM_Sekkulaath_Juvenile</occupantKindDefName>
    //       ...
    //     </li>
    //   </comps>
    public class RM_CompProperties_CapturedSpecimen : CompProperties
    {
        /// <summary>Resolved by defName, not a typed PawnKindDef reference,
        /// specifically so a PatchOperationReplace can retarget this one
        /// string when the Star Wars tier is present — see
        /// RSW_SekkulaathTank_DianogaSwap.xml (mandrake.rsw.swbestiary,
        /// MayRequire="mandrake.rm.feverwood"). "Swap, not add" (owner,
        /// 2026-09-23): the def-slot never holds two kinds at once, it is
        /// simply repointed.</summary>
        public string occupantKindDefName = "RM_Sekkulaath_Juvenile";

        /// <summary>What escapes/gets spawned is the SAME kind as the
        /// occupant — one species at whatever scale the swap resolves to
        /// (item's own "it is not a second creature invented for the
        /// tank"). Kept as a separate field only so a later captivity class
        /// (venom creature, egg-layer) can occupant != escapee if that ever
        /// turns out to matter; unused divergence here.</summary>
        public bool escapeesAreOccupantKind = true;

        // --- feeding / upkeep (rides the sibling CompRefuelable) ---

        /// <summary>Consecutive days with the tank's CompRefuelable empty
        /// before neglect starts contributing to the escape roll. INVENTED:
        /// 3 — "a neglected... tank releases it" (§6j) needs upkeep to be a
        /// real, sustained failure, not a single missed day.</summary>
        public float neglectDaysBeforeEscapeRisk = 3f;

        /// <summary>Mean days-to-escape once neglected (Rand.MTBEventOccurs
        /// unit: days). INVENTED: 4 — slow enough that a colonist who
        /// notices the gizmo warning has time to feed it.</summary>
        public float neglectEscapeMtbDays = 4f;

        // --- damage-triggered escape ("a damaged tank releases it") ---

        /// <summary>Fraction of the tank's MaxHitPoints that must be lost
        /// (from full) before each further hit rolls an immediate escape
        /// chance. INVENTED: 0.5 — a cracked tank, not a scratched one.</summary>
        public float damageEscapeThresholdFraction = 0.5f;

        /// <summary>Chance per damage instance, once past the threshold
        /// above, that THIS hit is the one that breaches the tank. INVENTED:
        /// 0.35.</summary>
        public float damageEscapeChancePerHit = 0.35f;

        // --- production ("fed... it yields the canon product line") ---

        public List<RM_CapturedSpecimenProduct> products = new List<RM_CapturedSpecimenProduct>();

        // --- teaches ("seeing it names the creature... before it kills them") ---

        /// <summary>On first successful production tick, calls
        /// RUT_MapComponent_TheTenant.Notify_Taught() on this map — a real,
        /// small mechanical payoff for "learning the warning": colonists
        /// become somewhat less likely to be struck at registered water
        /// (see that class's own ScanExposure). Off: the tank still
        /// produces/escapes, it just never files that teach.</summary>
        public bool teachesColonyWarning = true;

        public RM_CompProperties_CapturedSpecimen()
        {
            compClass = typeof(RM_CompCapturedSpecimen);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string err in base.ConfigErrors(parentDef))
            {
                yield return err;
            }

            if (string.IsNullOrEmpty(occupantKindDefName))
            {
                yield return "RM_CompProperties_CapturedSpecimen occupantKindDefName is required.";
            }

            if (damageEscapeThresholdFraction <= 0f || damageEscapeThresholdFraction > 1f)
            {
                yield return "RM_CompProperties_CapturedSpecimen damageEscapeThresholdFraction must be in (0,1].";
            }
        }
    }

    /// <summary>One product line the tank yields while fed — e.g. meat,
    /// spleen chemicals, cream (§6j/§4a). Plain data, not a ThingSetMaker:
    /// this is a slow drip from one comp, not a reward table.</summary>
    public class RM_CapturedSpecimenProduct
    {
        public ThingDef thing;

        /// <summary>Mean days between drops of this product while fed.
        /// INVENTED per-product default set in XML.</summary>
        public float mtbDays = 3f;

        public IntRange countRange = new IntRange(1, 3);
    }
}
