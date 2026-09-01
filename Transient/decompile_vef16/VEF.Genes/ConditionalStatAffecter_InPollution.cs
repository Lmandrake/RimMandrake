using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_InPollution : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_InPollution"));

	public override bool Applies(StatRequest req)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		if (((StatRequest)(ref req)).HasThing && ((StatRequest)(ref req)).Thing.Spawned)
		{
			return GridsUtility.IsPolluted(((StatRequest)(ref req)).Thing.Position, ((StatRequest)(ref req)).Thing.Map);
		}
		return false;
	}
}
