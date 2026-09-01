using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_InColonyMap : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_ColonyMap"));

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
				return false;
			}
			return map.IsPlayerHome;
		}
		return false;
	}
}
