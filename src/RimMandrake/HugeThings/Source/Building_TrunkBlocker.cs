using RimWorld;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// One invisible solid cell of a huge plant's trunk. It reads as the plant (label, mouseover), can't be
    /// deconstructed or claimed, and removes itself on a rare tick if its plant is gone for any reason the
    /// comp did not see (mod removed from the def, a save edited by hand, a map transfer).
    /// </summary>
    public class Building_TrunkBlocker : Building
    {
        public Plant owner;

        public override string LabelNoCount => owner != null ? owner.LabelNoCount : base.LabelNoCount;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref owner, "owner");
        }

        public override AcceptanceReport DeconstructibleBy(Faction faction) => false;

        public override AcceptanceReport ClaimableBy(Faction by) => false;

        public override void TickRare()
        {
            base.TickRare();
            if (owner == null || owner.Destroyed || !owner.Spawned || owner.Map != Map
                || !owner.def.HasModExtension<RM_HugePlantExtension>())
            {
                Destroy(DestroyMode.Vanish);
            }
        }
    }
}
