using RimWorld;
using Verse;

namespace BigAndSmall;

public class ConditionalStatAffecter_AtNight : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("StatsReport_AtNight"));

	public override bool Applies(StatRequest req)
	{
		Thing thing = ((StatRequest)(ref req)).Thing;
		bool flag = thing != null && thing.Spawned;
		if (((StatRequest)(ref req)).HasThing)
		{
			if (!flag)
			{
				IThingHolder parentHolder = ((StatRequest)(ref req)).Thing.ParentHolder;
				PawnFlyer val = (PawnFlyer)(object)((parentHolder is PawnFlyer) ? parentHolder : null);
				if (val == null || !((Thing)val).Spawned)
				{
					goto IL_0078;
				}
			}
			Thing val2 = ((StatRequest)(ref req)).Thing;
			if (!flag)
			{
				IThingHolder parentHolder2 = ((StatRequest)(ref req)).Thing.ParentHolder;
				val2 = (Thing)(object)((parentHolder2 is PawnFlyer) ? parentHolder2 : null);
			}
			Map map = val2.Map;
			if (map == null)
			{
				return false;
			}
			return map.skyManager.CurSkyGlow < 0.3f;
		}
		goto IL_0078;
		IL_0078:
		return false;
	}
}
