using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_FORMAT_TIERS_1 (packet B1). The four format tiers a droid's
    /// programming can sit at, per design/Jawa/droid_system_spec.md section 5 and
    /// the owner's ruling 4 (DROID_UNIFIED_FRAMEWORK_DESIGN.md section 0):
    ///
    ///   BLANK        the standby chassis after deformatting - no programming at
    ///                all, ready to reformat. No needs, no work.
    ///   MINDLESS     NOT a default state: a REDUCED one (damage, hacking, or a
    ///                deeply restrictive bolt). Low-level work only; "no rest,
    ///                recreation, break chance, morale checks" (sheet row
    ///                abf_formatting, frozen droid_verbs_decisions.json).
    ///   PROGRAMMABLE the ordinary working droid: machines, repair, plant tending,
    ///                self-defense. Ruling 4 gives it Mood but NOT
    ///                Joy/Beauty/Comfort/Outdoors.
    ///   SAPIENT      the whole roster - morale, breaks, savants, idiosyncrasies,
    ///                bonding, rebellion if mistreated.
    ///
    /// The enum's integer values ARE the severity ladder minus one: severity
    /// 1/2/3/4 maps to blank/mindless/programmable/sapient, and the four
    /// RSW_DW_FormatTier HediffDef stages (HediffDefs_Droidworks.xml) cut at
    /// 0 / 1.5 / 2.5 / 3.5 so a half-point of float wobble can never change tier.
    /// </summary>
    public enum DroidFormatTier
    {
        Blank = 0,
        Mindless = 1,
        Programmable = 2,
        Sapient = 3
    }

    public static class DroidFormatTierUtility
    {
        /// <summary>
        /// What a droid is when nobody has formatted it: PROGRAMMABLE. Mindless is
        /// explicitly "NOT the default droid setting ... a reduced state" (owner,
        /// sheet row abf_formatting) and sapience is what a long-unwiped droid
        /// DRIFTS into (DROIDWORKS_SERVICE_RECORD_DRIFT_1, packet E2) rather than
        /// what it ships as - so the middle rung is where every droid starts.
        /// </summary>
        public const DroidFormatTier DefaultTier = DroidFormatTier.Programmable;

        public static float SeverityFor(DroidFormatTier tier) => (int)tier + 1f;

        public static bool IsDroid(Pawn pawn) =>
            pawn?.RaceProps?.FleshType == DroidworksDefOf.RSW_DW_FleshType_Droid;

        /// <summary>
        /// The tier this pawn is formatted at, or null if it carries no
        /// RSW_DW_FormatTier hediff at all (every non-droid, and any droid that has
        /// not yet been through CompDWFormatTier's spawn-time ensure).
        /// </summary>
        public static DroidFormatTier? TierOf(Pawn pawn)
        {
            Hediff h = pawn?.health?.hediffSet?.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_FormatTier);
            if (h == null) return null;
            return TierForSeverity(h.Severity);
        }

        /// <summary>Tier, treating "no hediff" as the default rather than as absent.</summary>
        public static DroidFormatTier EffectiveTierOf(Pawn pawn) => TierOf(pawn) ?? DefaultTier;

        public static DroidFormatTier TierForSeverity(float severity) =>
            (DroidFormatTier)Mathf.Clamp(Mathf.RoundToInt(severity) - 1, 0, 3);

        /// <summary>
        /// Add the tier hediff at <paramref name="tier"/> if the pawn has none.
        /// Idempotent: a pawn that already carries one keeps whatever tier it is at,
        /// so this is safe to call on every spawn and every load.
        /// </summary>
        public static void EnsureTier(Pawn pawn, DroidFormatTier tier)
        {
            if (pawn?.health?.hediffSet == null) return;
            if (pawn.health.hediffSet.HasHediff(DroidworksDefOf.RSW_DW_FormatTier)) return;
            SetTier(pawn, tier);
        }

        /// <summary>
        /// Move a droid to <paramref name="tier"/>, creating the hediff if needed.
        ///
        /// The explicit AddOrRemoveNeedsAsAppropriate is LOAD-BEARING and not
        /// belt-and-braces: vanilla rebuilds the need list from a stage's
        /// disablesNeeds only when a hediff is ADDED or REMOVED
        /// (HediffSet.Notify_HediffAdded / Hediff.PostRemoved). A pure severity
        /// change routes through Hediff.Severity -> Pawn_HealthTracker
        /// .Notify_HediffChanged -> HediffSet.DirtyCache, which refreshes
        /// cachedDisabledNeeds but never touches pawn.needs - so without this call a
        /// droid formatted from sapient down to mindless would keep a live Joy need
        /// that ShouldHaveNeed now says it should not have.
        /// </summary>
        public static void SetTier(Pawn pawn, DroidFormatTier tier)
        {
            if (pawn?.health?.hediffSet == null) return;

            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_FormatTier);
            if (h == null)
            {
                h = HediffMaker.MakeHediff(DroidworksDefOf.RSW_DW_FormatTier, pawn);
                h.Severity = SeverityFor(tier);
                pawn.health.AddHediff(h);
            }
            else
            {
                h.Severity = SeverityFor(tier);
            }

            if (!pawn.Dead) pawn.needs?.AddOrRemoveNeedsAsAppropriate();
        }
    }
}
