using Verse;

namespace BigAndSmall;

public class CompProperties_SwapThingDef : CompProperties
{
	public bool sapientVersion;

	public ThingDef target;

	public CompProperties_SwapThingDef()
	{
		base.compClass = typeof(CompUseEffect_SwapThingDef);
	}
}
