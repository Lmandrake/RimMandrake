using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Webwork
{
	/// <summary>
	/// WEBWORK_RESELL (owner, Webwork Q8 by card, 2026-10-22): the one route back from the thrixweave strip. The strip
	/// makes Hyperweave Sellable, which every vanilla StockGenerator refuses; this generator names it directly, rolls
	/// thrixweaveResaleChance per stock generation and builds the Thing itself, so the strip stays intact for every
	/// other trader. Added to Orbital_Exotic by Patches/RM_Thrixweave_Resale.xml; its price tier is set at startup.
	/// </summary>
	public class StockGenerator_ThrixweaveResale : StockGenerator
	{
		private const string WeaveDefName = "Hyperweave";

		public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
		{
			ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(WeaveDefName);
			if (def == null || !RM_ThrixweaveResaleKernel.Stocks(RM_WebworkSettings.thrixweaveTraderStripEnabled,
				RM_WebworkSettings.thrixweaveResaleEnabled, RM_WebworkSettings.thrixweaveResaleChance, Rand.Value))
			{
				yield break;
			}
			int count = RM_ThrixweaveResaleKernel.Count(RandomCountOf(def), def.stackLimit);
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
