using System;
using RimWorld;
using Verse;

namespace VEF.Plants;

public class StatPart_BeautyByAge : StatPart
{
	public override void TransformValue(StatRequest req, ref float val)
	{
		if (((StatRequest)(ref req)).Thing is Plant_Blooming plant_Blooming && !((Plant)plant_Blooming).LeaflessNow)
		{
			int num = plant_Blooming.realAge / 3600000;
			val += Math.Min(plant_Blooming.GetExtension.MaxAgeBeautyModifier, plant_Blooming.GetExtension.AgeBeautyModifier * num);
		}
	}

	public override string ExplanationPart(StatRequest req)
	{
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		if (((StatRequest)(ref req)).Thing is Plant_Blooming plant_Blooming && !((Plant)plant_Blooming).LeaflessNow)
		{
			int num = plant_Blooming.realAge / 3600000;
			int num2 = Math.Min(plant_Blooming.GetExtension.MaxAgeBeautyModifier, plant_Blooming.GetExtension.AgeBeautyModifier * num);
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_BeautyByAge", NamedArgument.op_Implicit(num2)));
		}
		return null;
	}
}
