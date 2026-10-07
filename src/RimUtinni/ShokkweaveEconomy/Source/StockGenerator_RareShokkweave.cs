using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.ShokkweaveEconomy
{
    // SHOKKWEAVE_SOLE_SOURCE_1, owner ruling 2026-10-06 23:34 (typed): very small amounts may appear in the
    // Wildsteam's stock, rarer still in the Hutt's. The sole-source strip (RM_WebworkStartupGate) sets
    // Hyperweave tradeability to Sellable, so every vanilla StockGenerator refuses it (TraderCanSell() false).
    // This generator is the ONLY route back: it names Hyperweave itself, rolls `chance` per stock generation,
    // and builds the Thing directly, so the strip stays intact for every other trader.
    public class StockGenerator_RareShokkweave : StockGenerator
    {
        public float chance = 0.1f;
        private const string WeaveDefName = "Hyperweave";

        public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(WeaveDefName);
            if (def == null || Rand.Value >= chance)
            {
                yield break;
            }
            int count = Mathf.Min(RandomCountOf(def), def.stackLimit);
            if (count <= 0)
            {
                yield break;
            }
            Thing t = ThingMaker.MakeThing(def);
            t.stackCount = count;
            yield return t;
        }

        public override bool HandlesThingDef(ThingDef thingDef)
        {
            return thingDef != null && thingDef.defName == WeaveDefName;
        }

        public override Tradeability TradeabilityFor(ThingDef thingDef)
        {
            return HandlesThingDef(thingDef) ? Tradeability.All : Tradeability.None;
        }
    }
}
