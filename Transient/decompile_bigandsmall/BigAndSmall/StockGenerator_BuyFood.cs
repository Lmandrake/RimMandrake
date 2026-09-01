using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace BigAndSmall;

public class StockGenerator_BuyFood : StockGenerator
{
	public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
	{
		return Enumerable.Empty<Thing>();
	}

	public override bool HandlesThingDef(ThingDef thingDef)
	{
		if (thingDef.IsWithinCategory(ThingCategoryDefOf.Foods))
		{
			return true;
		}
		if (thingDef == ThingDefOf.InsectJelly)
		{
			return true;
		}
		return false;
	}

	public override Tradeability TradeabilityFor(ThingDef thingDef)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		if ((int)thingDef.tradeability != 0 && ((StockGenerator)this).HandlesThingDef(thingDef))
		{
			return (Tradeability)1;
		}
		return (Tradeability)0;
	}
}
