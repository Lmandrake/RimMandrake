using Verse;

namespace BigAndSmall;

public class CompProperties_TargetAddHediff : CompProperties
{
	public HediffDef hediffDef;

	public CompProperties_TargetAddHediff()
	{
		base.compClass = typeof(CompUseEffect_TargetAddHediff);
	}
}
