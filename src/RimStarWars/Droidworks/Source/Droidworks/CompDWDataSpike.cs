using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_WIPE_AND_SPIKE_1. Data-driven faction key for a data spike -
    /// see JobDriver_DWDataSpike.cs and CompTargetable_DWDataSpike.cs for how it
    /// is read. v0 keys ONE generic RSW_DW_DataSpike def to a single faction
    /// (spikeFaction is a static XML value on that one ThingDef's comp, not a
    /// per-instance runtime field) - design/Jawa/droid_ruling.md's own KotOR
    /// ruling ("THE capture target") picks guy762_KotORFaction_RogueDroids as
    /// that one faction. Adding another keyed faction later is another
    /// ThingDef of this same shape with a different spikeFaction value, not a
    /// C# change.
    /// </summary>
    public class CompProperties_DWDataSpike : CompProperties
    {
        /// <summary>FactionDef defName this spike is keyed to.</summary>
        public string spikeFaction;

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
            if (target?.Faction?.def == null || Props.spikeFaction.NullOrEmpty()) return false;
            return target.Faction.def.defName == Props.spikeFaction;
        }
    }
}
