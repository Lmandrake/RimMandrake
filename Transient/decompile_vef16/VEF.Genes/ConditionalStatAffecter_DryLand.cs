using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_DryLand : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_NotWater"));

	public override bool Applies(StatRequest req)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		Pawn val;
		if (((StatRequest)(ref req)).HasThing && (val = (Pawn)/*isinst with value type is only supported in some contexts*/) != null && ((Thing)val).Map != null && !GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map).IsWater)
		{
			return true;
		}
		return false;
	}
}
