using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_Outdoors : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_Outside"));

	public override bool Applies(StatRequest req)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		if (((StatRequest)(ref req)).HasThing && ((StatRequest)(ref req)).Thing.Spawned)
		{
			return !((StatRequest)(ref req)).Thing.Map.roofGrid.Roofed(((StatRequest)(ref req)).Thing.Position);
		}
		return false;
	}
}
