using RimWorld.Planet;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Puts the place's goods on the ground. INHABITED_STOCK_ONTO_MAP_AND_FATE_1.
    ///
    /// The larder stops being bookkeeping here. Everything the place holds is
    /// dropped as real Things inside its own district, where the cast can eat it,
    /// the player can steal it and a stray incendiary can burn it -- and
    /// Patch_MapRemoval takes back whatever is still there when the player leaves,
    /// so the holder afterwards is what actually survived rather than what was
    /// authored.
    ///
    /// ORDER 910, AFTER Inhabited_Cast (900) AND NOT BEFORE IT. The stock holder
    /// is filled by WorldObject_Inhabited.InstantiateCast, which the cast step is
    /// what triggers; dropping first would empty a holder that is still empty.
    /// The InstantiateCast call below is the same idempotent guard the cast step
    /// uses, so this step is also correct on a map that has the stock step wired
    /// and not the cast one.
    ///
    /// WHERE THE GOODS GO, AND WHY IT IS NOT A GRANARY YET. The authored template
    /// format has no role or marker vocabulary at all -- a compiled rimplace plan
    /// is a footprint plus flat lists of terrain, things, roof and paint
    /// (src/RimMandrake/StructureInjections/Source/RimplacePlan.cs), with nothing
    /// that could say "this building is the store". So the anchor is derived
    /// rather than authored: the composed district's own rect, published by
    /// GenStep_ComposeSettlementDistrict, preferring a roofed standable cell in
    /// it, which in practice means inside one of the district's buildings. A
    /// marked storage room is the obvious successor and belongs to whichever item
    /// gives the template format a marker layer, not to this one.
    /// </summary>
    public class GenStep_InhabitedStock : GenStep
    {
        /// <summary>The var GenStep_ComposeSettlementDistrict publishes the
        /// composed district's map-space rect under. Absent on a map that had no
        /// district composed -- the wilderness Inhabited_Place path, or a
        /// settlement whose district label has no template yet.</summary>
        public const string DistrictRectVar = "Inhabited_DistrictRect";

        /// <summary>How many cells to try before giving up on a roofed spot.</summary>
        private const int RoofedTries = 60;

        public override int SeedPart => 1104459303;

        public override void Generate(Map map, GenStepParams parms)
        {
            WorldObject_Inhabited place = Find.WorldObjects.WorldObjectAt<WorldObject_Inhabited>(map.Tile);
            if (place == null)
            {
                return;
            }
            if (!place.castInstantiated)
            {
                place.InstantiateCast();
            }
            if (place.stock == null)
            {
                return;
            }

            place.stockOnTheGround.Clear();
            place.stockSpawnedCount = 0;
            place.stockSpot = Anchor(map);
            if (!place.stockSpot.IsValid)
            {
                Log.Warning("[RimMandrake.Inhabited] no standable anchor for the stock of "
                            + place.LabelCap + "; the goods stay in the holder.");
                return;
            }

            int placed = place.stock.DumpOnto(map, place.stockSpot, place.stockOnTheGround);
            place.stockSpawnedCount = placed;
            if (placed > 0)
            {
                Log.Message("[RimMandrake.Inhabited] put " + placed + " of "
                            + place.LabelCap + "'s goods on the ground at " + place.stockSpot
                            + " (" + place.stockOnTheGround.Count + " stacks).");
            }
        }

        /// <summary>
        /// A cell inside the composed district, roofed if one can be found, else
        /// the district's centre, else the map's. Every fallback is a real place
        /// to stand -- goods in the open are still findable and stealable, which
        /// is the bar; being indoors is the nicety.
        /// </summary>
        private static IntVec3 Anchor(Map map)
        {
            if (MapGenerator.TryGetVar(DistrictRectVar, out CellRect district)
                && district.Area > 0)
            {
                for (int i = 0; i < RoofedTries; i++)
                {
                    IntVec3 c = district.RandomCell;
                    if (c.InBounds(map) && c.Standable(map) && c.Roofed(map))
                    {
                        return c;
                    }
                }
                IntVec3 centre = district.CenterCell;
                if (centre.InBounds(map) && centre.Standable(map))
                {
                    return centre;
                }
                if (CellFinder.TryFindRandomCellInsideWith(district,
                        (IntVec3 c) => c.Standable(map), out IntVec3 inside))
                {
                    return inside;
                }
            }

            // Same anchor GenStep_InhabitedCast falls back to for its worksite, so
            // a place with no composed district still puts its people and its
            // goods in the same part of the map.
            IntVec3 mid = map.Center;
            return mid.Standable(map) ? mid : CellFinder.RandomNotEdgeCell(12, map);
        }
    }
}
