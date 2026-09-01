using RimWorld;
using Verse;

namespace VEF.Buildings;

public class LootBoxExtension : DefModExtension
{
	public ThingSetMakerDef thingSetMakerDef;

	public FloatRange totalMarketValueRange = new FloatRange(850f, 1000f);

	public float? minSingleItemMarketValuePct;

	public bool allowNonStackableDuplicates = true;

	public IntRange countRange = new IntRange(1, 1);
}
