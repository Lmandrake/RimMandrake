using Verse;

namespace BigAndSmall;

public class CompProperties_XenogermCreator : CompProperties
{
	public bool archite;

	public bool endogenes;

	public bool xenogenes;

	public bool inactivegenes = true;

	public CompProperties_XenogermCreator()
	{
		base.compClass = typeof(CompTargetEffect_CreateXenogerm);
	}
}
