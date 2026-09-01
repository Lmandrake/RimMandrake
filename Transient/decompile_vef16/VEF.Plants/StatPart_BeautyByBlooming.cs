using RimWorld;
using Verse;

namespace VEF.Plants;

public class StatPart_BeautyByBlooming : StatPart
{
	public override void TransformValue(StatRequest req, ref float val)
	{
		if (((StatRequest)(ref req)).Thing is Plant_Blooming { isBlooming: not false } plant_Blooming && !((Plant)plant_Blooming).LeaflessNow)
		{
			val *= plant_Blooming.GetExtension.BloomBeautyModifier;
		}
	}

	public override string ExplanationPart(StatRequest req)
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		if (((StatRequest)(ref req)).Thing is Plant_Blooming { isBlooming: not false } plant_Blooming && !((Plant)plant_Blooming).LeaflessNow)
		{
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_BeautyByBloming", NamedArgument.op_Implicit(plant_Blooming.GetExtension.BloomBeautyModifier)));
		}
		return null;
	}
}
