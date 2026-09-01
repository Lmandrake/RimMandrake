using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions;

public class StockGenerator_ThingSetMakerTags : StockGenerator
{
	[NoTranslate]
	public List<string> thingSetMakerTags;

	private IntRange thingDefCountRange = IntRange.One;

	private List<ThingDef> excludedThingDefs;

	public override IEnumerable<Thing> GenerateThings(PlanetTile forTile, Faction faction = null)
	{
		List<ThingDef> generatedDefs = new List<ThingDef>();
		int numThingDefsToUse = ((IntRange)(ref thingDefCountRange)).RandomInRange;
		IEnumerable<ThingDef> list = DefDatabase<ThingDef>.AllDefs.Where((ThingDef d) => ((StockGenerator)this).HandlesThingDef(d) && TradeabilityUtility.TraderCanSell(d.tradeability));
		ThingDef chosenThingDef = default(ThingDef);
		for (int i = 0; i < numThingDefsToUse; i++)
		{
			if (!GenCollection.TryRandomElement<ThingDef>(list.Where((ThingDef d) => (excludedThingDefs == null || !excludedThingDefs.Contains(d)) && !generatedDefs.Contains(d)), ref chosenThingDef))
			{
				break;
			}
			foreach (Thing item in StockGeneratorUtility.TryMakeForStock(chosenThingDef, ((StockGenerator)this).RandomCountOf(chosenThingDef), (Faction)null))
			{
				yield return item;
			}
			generatedDefs.Add(chosenThingDef);
			chosenThingDef = null;
		}
	}

	public override bool HandlesThingDef(ThingDef thingDef)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		if ((int)thingDef.tradeability != 0 && thingDef.techLevel <= base.maxTechLevelBuy && thingDef.thingSetMakerTags != null)
		{
			foreach (string thingSetMakerTag in thingSetMakerTags)
			{
				if (thingDef.thingSetMakerTags.Contains(thingSetMakerTag))
				{
					return true;
				}
			}
		}
		return false;
	}
}
