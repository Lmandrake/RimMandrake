using RimWorld;
using Verse;

namespace RimMandrake.WeepingStones
{
    // WEEPINGSTONES_WALKING_CONDENSER_1: the last working condenser, cut out of the gorrask. Makes water on its own
    // (no power); installable on a gravship because it is an ordinary minifiable building.
    public class CompProperties_AncientCondenser : CompProperties
    {
        public int intervalTicks = 2500;
        public int litres = 1;
        public int cap = 60;
        public CompProperties_AncientCondenser() { compClass = typeof(RM_CompAncientCondenser); }
    }

    public class RM_CompAncientCondenser : ThingComp
    {
        private int acc;

        public override void PostExposeData() { Scribe_Values.Look(ref acc, "acc"); }

        public override void CompTickRare()
        {
            if (!RM_WeepingStonesSettings.condenserEnabled || !parent.Spawned) return;
            acc += 250;
            if (acc < ((CompProperties_AncientCondenser)props).intervalTicks) return;
            acc = 0;
            ThingDef water = DefDatabase<ThingDef>.GetNamedSilentFail("RM_CondenserWater");
            if (water == null) return;
            CompProperties_AncientCondenser p = (CompProperties_AncientCondenser)props;
            Map map = parent.Map;
            int have = 0;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(parent))
                foreach (Thing t in c.GetThingList(map)) if (t.def == water) have += t.stackCount;
            if (have >= p.cap) return;
            Thing w = ThingMaker.MakeThing(water); w.stackCount = p.litres;
            GenPlace.TryPlaceThing(w, parent.Position, map, ThingPlaceMode.Near);
        }
    }
}
