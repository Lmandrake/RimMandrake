using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// Opt-in for a huge PLANT: a solid trunk of trunkWidth x trunkDepth cells at full size, standing on
    /// the plant's own cell and extending north (the way vanilla draws a single-mesh plant: its sprite's
    /// base sits on the root cell's bottom edge, Plant.Print). The root cell itself stays the plant's,
    /// so pawns can still reach it from the south to cut or harvest it.
    /// </summary>
    public class RM_HugePlantExtension : DefModExtension
    {
        /// <summary>Trunk width in cells at full size (centred on the root column; even widths lean east).</summary>
        public int trunkWidth = 2;

        /// <summary>Trunk depth in cells at full size, from the root row northward. 0 = same as width.</summary>
        public int trunkDepth = 0;

        /// <summary>How tall the drawn stem is, in cells, at full size: the click area runs this far north
        /// even where the ground is not blocked. 0 = same as depth.</summary>
        public int stemHeight = 0;

        /// <summary>Below this growth the plant blocks nothing (a young fungus is not yet a wall).</summary>
        public float minGrowthToBlock = 0.25f;

        public int Depth => trunkDepth > 0 ? trunkDepth : trunkWidth;
        public int Stem => stemHeight > 0 ? stemHeight : Depth;
    }

    /// <summary>
    /// Opt-in for a huge PAWN race: a selection hitbox of (drawn body size x hitboxFraction) cells, centred
    /// on the pawn, never smaller than its footprint (Large Pawns' square when present).
    /// </summary>
    public class RM_HugePawnExtension : DefModExtension
    {
        /// <summary>Share of the current life stage's drawSize that counts as body (sprites carry margin).</summary>
        public float hitboxFraction = 0.6f;
    }
}
