using RimWorld;
using Verse;

namespace BigAndSmall;

public class ConditionalStatAffecter_Tipsy : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("BS_StatsReport_Tipsy"));

	public override bool Applies(StatRequest req)
	{
		Thing thing = ((StatRequest)(ref req)).Thing;
		if (thing != null && thing.Spawned)
		{
			Thing thing2 = ((StatRequest)(ref req)).Thing;
			Pawn val = (Pawn)(object)((thing2 is Pawn) ? thing2 : null);
			if (val != null)
			{
				BSCache cache = FastAcccess.GetCache(val);
				if (cache != null && cache.alcoholAmount >= 0.25f)
				{
					return true;
				}
			}
		}
		return false;
	}
}
