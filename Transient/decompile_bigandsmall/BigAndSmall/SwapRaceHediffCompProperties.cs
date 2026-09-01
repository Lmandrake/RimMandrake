using RimWorld;
using Verse;

namespace BigAndSmall;

public class SwapRaceHediffCompProperties : HediffCompProperties
{
	public ThingDef swapTarget;

	public XenotypeDef xenotype;

	public SwapRaceHediffCompProperties()
	{
		base.compClass = typeof(SwapRaceHediffComp);
	}
}
