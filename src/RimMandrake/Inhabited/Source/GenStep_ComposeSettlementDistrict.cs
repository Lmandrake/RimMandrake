using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// STUB compose step -- SETTLEMENT_VISIT_LOOP_1.
    ///
    /// Places exactly one placeholder district: no district art, no template
    /// selection, no layout. Its whole job is to prove the ARRIVAL and COMPOSE
    /// beats of the visit lifecycle exist and run, so the loop can be tested
    /// start-to-finish before DISTRICT_TEMPLATE_LIBRARY_1 lands real Lua
    /// district templates and replaces this step entirely.
    ///
    /// Runs before Inhabited_Cast (order 900): the cast should have a
    /// "composed" place to be dropped into, even though composed here means
    /// nothing more than a casing record and a log line -- there is
    /// deliberately no building, no layout, nothing DISTRICT_TEMPLATE_LIBRARY_1
    /// would have to demolish later.
    ///
    /// Records the arrival on the casing record too: arrival and compose are
    /// one beat in the lifecycle, and this is the one place both naturally run
    /// (map generation happens exactly once per visit, at arrival).
    /// </summary>
    public class GenStep_ComposeSettlementDistrict : GenStep
    {
        public override int SeedPart => 1104459302;

        public override void Generate(Map map, GenStepParams parms)
        {
            WorldObject_InhabitedSettlement settlement =
                Find.WorldObjects.WorldObjectAt<WorldObject_InhabitedSettlement>(map.Tile);
            if (settlement == null)
            {
                return;
            }

            settlement.casing.RecordArrival(Find.TickManager.TicksGame);

            string districtLabel = "placeholder district";
            if (settlement.manifest?.districts != null && settlement.manifest.districts.Count > 0
                && !settlement.manifest.districts[0].label.NullOrEmpty())
            {
                districtLabel = settlement.manifest.districts[0].label;
            }
            settlement.casing.RecordDistrictComposed(districtLabel);

            Log.Message("[RimMandrake.Inhabited] composed stub district '" + districtLabel
                + "' at " + settlement.LabelCap + " (visit #" + settlement.casing.visitCount
                + ") -- DISTRICT_TEMPLATE_LIBRARY_1 replaces this with real district composition.");
        }
    }
}
