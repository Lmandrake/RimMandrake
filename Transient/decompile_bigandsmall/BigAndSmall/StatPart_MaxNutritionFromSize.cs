using RimWorld;
using Verse;

namespace BigAndSmall;

public class StatPart_MaxNutritionFromSize : StatPart
{
	public override void TransformValue(StatRequest req, ref float val)
	{
		Thing thing = ((StatRequest)(ref req)).Thing;
		Pawn val2 = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val2 != null)
		{
			val *= StatExtension.GetStatValue((Thing)(object)val2, BSDefs.BS_MaxNutritionFromSize, true, int.MaxValue);
		}
	}

	public override string ExplanationPart(StatRequest req)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		Thing thing = ((StatRequest)(ref req)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			float statValue = StatExtension.GetStatValue((Thing)(object)val, BSDefs.BS_MaxNutritionFromSize, true, int.MaxValue);
			if (statValue != 1f)
			{
				return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_StatsReport_BodySize", NamedArgument.op_Implicit(statValue.ToString("F2"))) + ": x" + GenText.ToStringPercent(statValue));
			}
		}
		return null;
	}
}
