using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // ASHFALL_RESEARCH_BASE_1's half of the war lab's two-key gate
    // (the_propane_lakes.md §8 amendment, ashfall_research_base.md §6): the
    // crater event opens the GROUND (WarLabCraterMutation.Ignite(), a
    // sibling class in this same assembly); this flag records that the
    // Rakatan command codes have been redeemed, so the DOOR may be opened.
    // Deliberately mirrors WarLabCraterMutation's static-class-over-
    // GameComponent shape so a future door-check item can read
    // AshfallCommandCodesFlag.HasBeenSeized exactly the way existing callers
    // already read GameComponent_WarLabCrater.Triggered.
    public static class AshfallCommandCodesFlag
    {
        public static bool HasBeenSeized
        {
            get
            {
                if (Current.Game == null)
                    return false;
                var comp = Current.Game.GetComponent<GameComponent_AshfallCommandCodes>();
                return comp != null && comp.CommandCodesSeized;
            }
        }

        /// <summary>
        /// Marks the codes seized. Idempotent -- safe to call more than
        /// once. Returns true only the first time (the moment the flag
        /// actually flips), matching WarLabCraterMutation.Ignite()'s own
        /// "did this call actually do something" return convention.
        /// </summary>
        public static bool Seize()
        {
            if (!StructureInjectionsRUTSettings.ashfallCommandCodesEnabled)
                return false;

            if (Current.Game == null)
                return false;

            var comp = Current.Game.GetComponent<GameComponent_AshfallCommandCodes>();
            if (comp == null || comp.CommandCodesSeized)
                return false;

            comp.CommandCodesSeized = true;
            Log.Message("[ASHFALL_RESEARCH_BASE_1] Rakatan command codes redeemed -- " +
                "the war lab's shielding may now be opened.");
            return true;
        }
    }
}
