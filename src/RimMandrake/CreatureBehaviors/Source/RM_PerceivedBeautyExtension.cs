using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// OLLOPOM_OUTDOOR_BEAUTY (owner, 2026-10-10: "I was considering it for outdoor beauty instead.").
    /// A creature carrying this adds <see cref="beautyOutdoors"/> to the beauty of the cell it stands on, when that
    /// cell is psychologically outdoors — what a pawn nearby perceives through its Beauty need.
    ///
    /// Why a patch and not a stat: vanilla BeautyUtility.CellBeauty only sums Things whose category passes
    /// BeautyRelevant (Building, Item, Plant, Filth), so a Pawn's Beauty / BeautyOutdoors stat is never read
    /// (MEASURED, RimSage, RimWorld/BeautyUtility.cs). RM_PerceivedBeautyPatches adds the creature's term.
    /// Reusable: any "pretty" creature opts in with this extension; nothing is keyed on the Ollopom.
    /// </summary>
    public class RM_PerceivedBeautyExtension : DefModExtension
    {
        /// <summary>Beauty added to the creature's own cell while it is outdoors. Vanilla rose = 14 (Plant_Rose BeautyOutdoors).</summary>
        public float beautyOutdoors = 8f;
    }
}
