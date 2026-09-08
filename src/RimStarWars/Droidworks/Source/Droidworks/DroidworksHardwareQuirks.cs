using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Marker DefModExtension declaring a TraitDef to be a PERMANENT hardware
    /// quirk. DROIDWORKS_WIPE_SEVERITY_1 (packet B10), owner ruling 7 verbatim:
    /// "Frequently also adds a permanent hardware quirk that cannot be reset but
    /// only accrete further."
    ///
    /// A marker extension rather than a defName list in C# on purpose: the pool
    /// has to be answerable as a QUESTION ("is this trait a quirk?") in two
    /// places at once - Recipe_DWMemoryWipe must never strip one while
    /// randomizing traits, and the roll must never pick a non-quirk. A defName
    /// list would have to be kept in sync in both; a marker on the def cannot
    /// drift, and a later packet adds a quirk with XML alone.
    /// </summary>
    public class HardwareQuirkExtension : DefModExtension
    {
    }

    /// <summary>
    /// The quirk pool and the two rules that make quirks permanent:
    /// nothing removes them, and they only ever accrete.
    ///
    /// ⚠️ The permanence guarantee is OURS, not the engine's. Vanilla has no
    /// "unremovable trait" flag - TraitSet.RemoveTrait will take any trait
    /// handed to it. What actually holds the line is that the only code in this
    /// mod that removes traits (Recipe_DWMemoryWipe.RandomizeTraits) asks
    /// IsQuirk first. Confirmed 2026-09-08 by a repo-wide grep for
    /// RemoveTrait: the only other callers are RimMandrake.Inhabited's
    /// CharacterApplier (a different mod, applies an authored character sheet)
    /// and the JawaBench bridge tool (a debug instrument). Any FUTURE code in
    /// this mod that removes traits must make the same check.
    /// </summary>
    public static class DroidworksHardwareQuirks
    {
        public static bool IsQuirk(TraitDef def) =>
            def != null && def.HasModExtension<HardwareQuirkExtension>();

        public static bool IsQuirk(Trait trait) => trait != null && IsQuirk(trait.def);

        /// <summary>
        /// Every TraitDef marked as a hardware quirk. Not cached: the list is a
        /// handful of defs and this is read once per memory wipe, so a cache
        /// would buy nothing and could go stale across a def reload.
        /// </summary>
        public static IEnumerable<TraitDef> Pool =>
            DefDatabase<TraitDef>.AllDefsListForReading.Where(IsQuirk);

        /// <summary>
        /// Adds one quirk the pawn does not already carry, chosen uniformly.
        /// Returns the trait gained, or null if the pawn already has every
        /// quirk in the pool (accretion has a ceiling - the pool size - and
        /// that is the only thing that ever stops it).
        /// </summary>
        public static Trait TryGainRandomQuirk(Pawn pawn)
        {
            if (pawn?.story?.traits == null) return null;

            List<TraitDef> candidates =
                Pool.Where(d => !pawn.story.traits.HasTrait(d)).ToList();
            if (candidates.Count == 0) return null;

            // degree 0 (every quirk is single-degree), forced: true - the same
            // shape DroidAssembly.SpawnDroid already uses for traits it grants
            // deliberately rather than rolls.
            Trait quirk = new Trait(candidates.RandomElement(), 0, true);
            pawn.story.traits.GainTrait(quirk);
            return quirk;
        }
    }
}
