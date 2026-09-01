using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_TargetEffectReanimate : CompProperties
{
	public ThingDef moteDef;

	public XenotypeDef xenoTypeDef;

	public CompProperties_TargetEffectReanimate()
	{
		base.compClass = typeof(CompTargetEffect_Reanimate);
	}
}
