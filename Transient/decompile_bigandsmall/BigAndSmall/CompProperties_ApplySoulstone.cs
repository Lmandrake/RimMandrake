using Verse;

namespace BigAndSmall;

public class CompProperties_ApplySoulstone : CompProperties
{
	public float factor = 1f;

	public float falloff = 2.5f;

	public CompProperties_ApplySoulstone()
	{
		base.compClass = typeof(CompTargetEffect_ApplySoulstone);
	}
}
