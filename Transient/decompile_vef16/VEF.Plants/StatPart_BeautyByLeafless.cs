using RimWorld;
using Verse;

namespace VEF.Plants;

public class StatPart_BeautyByLeafless : StatPart
{
	public override void TransformValue(StatRequest req, ref float val)
	{
		if (((StatRequest)(ref req)).Thing is Plant_Blooming plant_Blooming && ((Plant)plant_Blooming).LeaflessNow && plant_Blooming.GetExtension.LeaflessBeauty != 0)
		{
			val = plant_Blooming.GetExtension.LeaflessBeauty;
		}
	}

	public override string ExplanationPart(StatRequest req)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		if (((StatRequest)(ref req)).Thing is Plant_Blooming plant_Blooming && ((Plant)plant_Blooming).LeaflessNow && plant_Blooming.GetExtension.LeaflessBeauty != 0)
		{
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VPE_BeautyByLeafless", NamedArgument.op_Implicit(plant_Blooming.GetExtension.LeaflessBeauty)));
		}
		return null;
	}
}
