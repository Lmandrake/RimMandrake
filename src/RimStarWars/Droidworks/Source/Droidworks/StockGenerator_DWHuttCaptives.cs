using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROID_HUTT_CAPTIVES_1 (packet C6) — the purchase half. Same droid-market
    /// shape as <see cref="StockGenerator_DWDroids"/> (reused, not duplicated:
    /// GenerateThings/HandlesThingDef both inherited), but every pawn this
    /// generator produces already carries RSW_DW_RestrainingBolt and a
    /// pre-seeded RSW_DW_BoltResentment via
    /// <see cref="DroidworksBoltUtility.ApplyCaptiveBolt"/> — these are debtors
    /// the Hutts have been holding, not fresh stock off a shelf. See that
    /// class's own doc for why a bare AddHediff would be wrong (a bolt that
    /// never earns resentment never rebels when freed).
    ///
    /// Deliberately still a droid market, priced and bought the ordinary way —
    /// no slavery gate, matching StockGenerator_DWDroids's own reasoning
    /// (a droid is property, not a person).
    /// </summary>
    public class StockGenerator_DWHuttCaptives : StockGenerator_DWDroids
    {
        /// <summary>How long a given debtor has already been held, expressed as
        /// resentment severity at the moment of sale. FOUNDRY's own flavor
        /// number — no owner ruling exists for "how long a Hutt holds a debtor"
        /// — chosen so some captives are fresh (well under
        /// Recipe_RemoveRestrainingBolt.RebellionThreshold, 0.6f) and some are
        /// already past it: buying one is not always a clean purchase.</summary>
        public FloatRange resentmentSeverityRange = new FloatRange(0.2f, 0.8f);

        public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
        {
            foreach (Thing t in base.GenerateThings(forTile, faction))
            {
                if (t is Pawn pawn)
                {
                    DroidworksBoltUtility.ApplyCaptiveBolt(pawn, resentmentSeverityRange);
                }
                yield return t;
            }
        }
    }
}
