using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Marker CompProperties for CompTitanicWake. Never written by hand in a
    /// race's XML &lt;comps&gt; block - RM_TitanicCreaturesMod's static
    /// constructor appends one to every ThingDef TitanicTierUtility.DefQualifies
    /// accepts, at def-load time, the same way vanilla would if the XML had
    /// declared it. See that file for why (ThingWithComps.AllComps has no safe
    /// public way to inject a comp onto an already-spawned instance).
    /// </summary>
    public class CompProperties_TitanicWake : CompProperties
    {
        public CompProperties_TitanicWake()
        {
            compClass = typeof(CompTitanicWake);
        }
    }
}
