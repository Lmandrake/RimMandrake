using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_DEDICATED_GRAZER_1 — opt-in marker for "this race burrows to
    /// survive a fire front instead of fleeing it" (the_pyrelands.md §4:
    /// "burrowers — grazers that let the fire pass over and emerge into the
    /// fertilized ash"). A race with no extension is invisible to
    /// RM_JobGiver_BurrowOnFire, the same opt-in shape RM_ShadowFollowerExtension
    /// already established for CreatureBehaviors' shade-follow mechanism
    /// (DESERT_GLITTER_BIRDS_COMMENSALS_1) — safe to keep the think-tree insert
    /// global rather than gated per-race in XML.
    ///
    /// Deliberately generic: no species is named anywhere in this file.
    /// RM_Ashwallow is the first consumer; a second dedicated burrower the
    /// biome wants later opts in with the same extension and needs no new C#.
    /// </summary>
    public class RM_BurrowOnFireExtension : DefModExtension
    {
        /// <summary>How close a free-standing fire has to be before this race
        /// goes to ground. Default lives on PyrelandsTuning so every consumer
        /// starts from the same reasoned number unless a def overrides it.</summary>
        public float detectionRadius = PyrelandsTuning.BurrowDetectionRadius;

        /// <summary>Safety cap: never stays burrowed longer than this even if
        /// the fire-near check somehow never clears.</summary>
        public int maxBurrowTicks = PyrelandsTuning.BurrowMaxTicks;
    }
}
