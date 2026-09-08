using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_WIPE_AND_SPIKE_1; per-faction keys added
    /// DROIDWORKS_HEADS_BRAINS_SPIKES_1 (packet B3). Data-driven faction key
    /// for a data spike - see JobDriver_DWDataSpike.cs and
    /// CompTargetable_DWDataSpike.cs for how it is read. Each keyed faction
    /// is its own ThingDef of this same shape with a different spikeFaction
    /// value (or factionless=true) - never a C# change. v0's single generic
    /// RSW_DW_DataSpike (design/Jawa/droid_ruling.md's KotOR ruling, "THE
    /// capture target") is untouched by B3; RSW_DW_DataSpike_Empire/Hutt/
    /// Junker/Wild are the new siblings.
    /// </summary>
    public class CompProperties_DWDataSpike : CompProperties
    {
        /// <summary>FactionDef defName this spike is keyed to.</summary>
        public string spikeFaction;

        /// <summary>
        /// RSW_DW_DataSpike_Wild (packet B3): targets a FACTIONLESS droid -
        /// the crashed/gone-wild units of DROIDWORKS_WILD_DROIDS_1 (E4,
        /// unbuilt), which per that item's own design carry Faction == null,
        /// never a real FactionDef. When true, spikeFaction is ignored.
        /// </summary>
        public bool factionless;

        public CompProperties_DWDataSpike()
        {
            compClass = typeof(CompDWDataSpike);
        }
    }

    public class CompDWDataSpike : ThingComp
    {
        public CompProperties_DWDataSpike Props => (CompProperties_DWDataSpike)props;

        /// <summary>
        /// True only when the target's ACTUAL faction (read live, not cached)
        /// matches this spike's key - a spike keyed to the wrong faction
        /// refuses rather than silently working on anyone.
        /// </summary>
        public bool MatchesFaction(Pawn target)
        {
            if (target == null) return false;
            if (Props.factionless) return target.Faction == null;
            if (target.Faction?.def == null || Props.spikeFaction.NullOrEmpty()) return false;
            return target.Faction.def.defName == Props.spikeFaction;
        }
    }
}
