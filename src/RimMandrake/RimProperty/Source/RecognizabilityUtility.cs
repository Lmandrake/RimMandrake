using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Property
{
    // Spec item 2: "Strength decays from the timestamp at a rate set by a
    // per-Thing RECOGNIZABILITY score (uniqueness, serials, quality/art,
    // market value, named things, droids). A steel bar's stolen-claim dies
    // in days; a named astromech's never does." This reads only vanilla
    // fields — no authored per-item data — matching the fabric's
    // campaign-blind, zero-storage mandate: nothing here is a Comp, nothing
    // is written anywhere, every call recomputes from the Thing itself.
    public static class RecognizabilityUtility
    {
        // Every Thing starts slightly identifiable — a serial number exists
        // even on a steel bar, it's just never checked.
        private const float BaselineScore = RM_PropertyKernel.Baseline;

        private const float QualityWeight = RM_PropertyKernel.QualityWeight;
        private const float MarketValueWeight = RM_PropertyKernel.MarketValueWeight;
        private const float NamedWeight = RM_PropertyKernel.NamedWeight;
        private const float MechanoidWeight = RM_PropertyKernel.MechanoidWeight;
        private const float NonStackableWeight = RM_PropertyKernel.NonStackableWeight;

        // Market values above this are treated as maximally distinctive —
        // there's no meaningful difference between "priceless" and "very
        // expensive" for recognizability purposes.
        private const float MarketValueSaturation = RM_PropertyKernel.MarketValueSaturation;

        public static float Score(Thing thing)
        {
            if (thing == null) return 0f;

            bool hasQuality = thing.TryGetQuality(out QualityCategory qc);
            return RM_PropertyKernel.Recognizability(true, hasQuality, (int)qc, thing.MarketValue, HasPersistentName(thing),
                thing is Pawn pawn && pawn.RaceProps != null && pawn.RaceProps.IsMechanoid,
                thing.def != null, thing.def != null ? thing.def.stackLimit : 0);
        }

        // "Named things" (spec item 2): a Pawn who has been given (or
        // generated with) a persistent Name — every humanlike, a tamed/
        // bonded animal, or a player-named mech, but NOT an unnamed hostile
        // mechanoid — or a weapon carrying vanilla's own persona-weapon comp
        // (CompBladelinkWeapon), which is exactly RimWorld's "this specific
        // item has an identity" marker for non-Pawn Things.
        private static bool HasPersistentName(Thing thing)
        {
            if (thing is Pawn pawn) return pawn.Name != null;

            if (thing is ThingWithComps twc)
            {
                return twc.GetComp<CompBladelinkWeapon>() != null;
            }

            return false;
        }
    }
}
