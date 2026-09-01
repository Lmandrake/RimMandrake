using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_OutsideColonyMap : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_OutsideColonyMap"));

	public override bool Applies(StatRequest req)
	{
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		if (((StatRequest)(ref req)).HasThing && ((StatRequest)(ref req)).Thing.Spawned)
		{
			Map map = ((StatRequest)(ref req)).Thing.Map;
			if (map == null)
			{
				return true;
			}
			return !map.IsPlayerHome;
		}
		return false;
	}
}
