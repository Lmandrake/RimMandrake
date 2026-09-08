using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_SHOP_BENCHES_1 (packet B4b): "the repair bench (part-swap
    /// bills)". Vanilla has no workbench-targets-a-live-pawn bill shape -
    /// bionic/prosthetic installs are always the health-tab Recipe_Surgery
    /// route, never a Bill_Production - so the bench is a PROXIMITY
    /// requirement on the same surgery recipes DROIDWORKS_FINE_PARTS_1
    /// already built, not a second production path. Same shape everywhere
    /// else; only AvailableOnNow/CompletableEver add the "near a
    /// RSW_DW_RepairBench" gate.
    /// </summary>
    public class Recipe_InstallDroidPartAtBench : Recipe_InstallDroidPart
    {
        private const float BenchRadius = 15f;

        public static bool NearRepairBench(Pawn pawn)
        {
            Map map = pawn?.MapHeld;
            if (map == null) return false;
            return map.listerBuildings.AllBuildingsColonistOfDef(DroidworksDefOf.RSW_DW_RepairBench)
                .Any(b => b.Position.DistanceTo(pawn.PositionHeld) <= BenchRadius);
        }

        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null) =>
            base.AvailableOnNow(thing, part) && thing is Pawn p && NearRepairBench(p);

        public override bool CompletableEver(Pawn surgeryTarget) =>
            NearRepairBench(surgeryTarget);
    }
}
