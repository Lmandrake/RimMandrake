using RimWorld;
using Verse;

namespace BigAndSmall;

public class CustomButcherProduct
{
	public ThingDef thingDef;

	public int count = 1;

	public EnumRange<QualityCategory>? itemQualityRange;

	public float chance = 1f;

	public bool scaleToBodySize;

	public bool scaleToBodySizeSquared;

	public bool scaleToButcherEfficiency;

	public bool TryMake(Pawn butcher, Pawn entity, out Thing thing)
	{
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		thing = null;
		if (thingDef == null)
		{
			return false;
		}
		if (!Rand.Chance(chance))
		{
			return false;
		}
		int num = count;
		if (scaleToBodySize)
		{
			num = GenMath.RoundRandom((float)count * entity.BodySize);
		}
		else if (scaleToBodySizeSquared)
		{
			num = GenMath.RoundRandom((float)count * entity.BodySize * entity.BodySize);
		}
		if (scaleToButcherEfficiency)
		{
			num = ((!entity.RaceProps.IsMechanoid) ? GenMath.RoundRandom((float)count * StatExtension.GetStatValue((Thing)(object)butcher, BSDefs.ButcheryFleshEfficiency, true, -1)) : GenMath.RoundRandom((float)count * StatExtension.GetStatValue((Thing)(object)butcher, BSDefs.ButcheryMechanoidEfficiency, true, -1)));
		}
		if (num <= 0)
		{
			return false;
		}
		if ((float)num < 1f && Rand.Chance((float)num))
		{
			num = 1;
		}
		thing = ThingMaker.MakeThing(thingDef, (ThingDef)null);
		thing.stackCount = num;
		if (itemQualityRange.HasValue)
		{
			CompQuality obj = ThingCompUtility.TryGetComp<CompQuality>(thing);
			if (obj != null)
			{
				obj.SetQuality(itemQualityRange.Value.RandomInRange, (ArtGenerationContext?)(ArtGenerationContext)1);
			}
		}
		return true;
	}
}
