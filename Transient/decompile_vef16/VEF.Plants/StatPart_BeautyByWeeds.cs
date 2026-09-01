using RimWorld;
using Verse;

namespace VEF.Plants;

public class StatPart_BeautyByWeeds : StatPart
{
	public override void TransformValue(StatRequest req, ref float val)
	{
		if (((StatRequest)(ref req)).Thing is Plant_Blooming { hasWeeds: not false } plant_Blooming)
		{
			val = plant_Blooming.GetExtension.WeededBeauty;
		}
	}

	public override string ExplanationPart(StatRequest req)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		if (((StatRequest)(ref req)).Thing is Plant_Blooming { hasWeeds: not false } plant_Blooming)
		{
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_BeautyByWeeds", NamedArgument.op_Implicit(plant_Blooming.GetExtension.WeededBeauty)));
		}
		return null;
	}
}
