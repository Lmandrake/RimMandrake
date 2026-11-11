using System.Collections.Generic;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT (owner, by card 2026-10-21): the titan passage "should draw from the hints of their
    /// own biome always". Attach to a BiomeDef's &lt;modExtensions&gt; to author that biome's hints:
    ///
    ///   passers  -&gt; the giants that may pass through this biome. When present (non-empty) it IS the pool: a giant need not
    ///               be homed here, and one homed here but not listed never passes. Absent, the biome's own roster is the pool.
    ///   none     -&gt; this biome never hosts a passage (owner: "A few exceptions such as rust cathedral and dark side biomes.
    ///               Only if giants can exist there.").
    ///
    /// Every listed kind still passes the rest of the gate (adult tier T2+, sea giants only on sea maps and land giants only on
    /// land, season, one T3 per map): RM_TitanicKernel.TitanEventEligible.
    /// </summary>
    public class RM_TitanPassageExtension : DefModExtension
    {
        public List<PawnKindDef> passers;
        public bool none;
    }
}
