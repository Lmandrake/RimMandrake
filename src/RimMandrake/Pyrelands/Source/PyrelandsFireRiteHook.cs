using System;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_RM_MOD_BUILD_1 §6 — the one door a campaign-specific mod may
    /// walk through to answer the biome's fire clock, without RM_Pyrelands
    /// ever depending on it.
    ///
    /// mandrake.rm.pyrelands must work "unchanged on a random planet with no
    /// Star Wars and no Ash'karr" (§3a) — but the shipped Deep Desert Tribes
    /// fire rite (mandrake.rut.pyrelandsmechanics' PyrelandsFireRite, which
    /// names a campaign faction and therefore stays in Utinni) sometimes
    /// intercepts a scheduled front. RM_Pyrelands cannot call into Utinni
    /// (wrong dependency direction — Utinni already loads after this mod,
    /// never the other way), so PyrelandsFireFront offers this hook instead
    /// and Utinni's own Mod constructor fills it in when that mod is present.
    ///
    /// Null on a franchise-free world: PyrelandsFireFront.TryRunRite then
    /// declines instantly and falls straight through to its own plain front —
    /// exactly the "all-off degrades to the fire clock" behavior the moved
    /// class already documented before this hook existed.
    /// </summary>
    public static class PyrelandsFireRiteHook
    {
        /// <summary>(map, origin) -> true if a rite actually took over this
        /// front-lighting. The hook implementation is responsible for its own
        /// enabled/frequency gating — the front just offers every scheduled
        /// firing and takes no for an answer.</summary>
        public static Func<Map, IntVec3, bool> TrySend;
    }
}
