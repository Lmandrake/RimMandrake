using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_TargetableExtended : CompProperties_Targetable
{
	public TargetingParameters targetInfo = new TargetingParameters();

	public bool playerOwnedOnly;

	public bool animalsOnly;

	public bool humanlikeOnly;

	public CompProperties_TargetableExtended()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Expected O, but got Unknown
		((CompProperties)this).compClass = typeof(CompTargetable_Extended);
	}
}
