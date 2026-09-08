using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class CompProperties_DWFormatTier : CompProperties
    {
        /// <summary>
        /// Overridable per race/family: a Primitive-tier drone chassis
        /// (DROIDWORKS_PRIMITIVE_TIER_1) could legitimately ship at Mindless.
        /// Left at the platform default here.
        /// </summary>
        public DroidFormatTier defaultTier = DroidFormatTierUtility.DefaultTier;

        public CompProperties_DWFormatTier()
        {
            compClass = typeof(CompDWFormatTier);
        }
    }

    /// <summary>
    /// DROIDWORKS_FORMAT_TIERS_1. Guarantees every droid carries an
    /// RSW_DW_FormatTier hediff, so the tier is a thing the player can SEE in the
    /// health tab rather than an invisible default inferred in code.
    ///
    /// Spawn-time rather than tick-time on purpose. The alternative routes were
    /// weighed and rejected:
    ///   - RaceProperties.hediffGiverSets runs a HediffGiver every 60 ticks for the
    ///     life of every droid on the map, to do work that is correct exactly once.
    ///   - A Harmony hook on PawnGenerator would fire for world pawns that may never
    ///     be seen, and would have to be undone for pawns loaded from a save.
    /// PostSpawnSetup fires on first spawn AND on every load (respawningAfterLoad),
    /// and EnsureTier is idempotent, so a droid formatted to Sapient two years ago
    /// is not silently reset to Programmable when its save is reloaded.
    ///
    /// Wired onto DW_Race_Base (Defs/Races_Base.xml), so every DW_Race_* inherits it.
    /// </summary>
    public class CompDWFormatTier : ThingComp
    {
        public CompProperties_DWFormatTier Props => (CompProperties_DWFormatTier)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);

            if (!(parent is Pawn pawn)) return;
            if (pawn.Dead) return;
            if (!DroidFormatTierUtility.IsDroid(pawn)) return;

            DroidFormatTierUtility.EnsureTier(pawn, Props.defaultTier);
        }
    }
}
