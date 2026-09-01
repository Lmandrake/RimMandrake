using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_FixedGender : CompProperties
{
	public Gender gender = (Gender)2;

	public CompProperties_FixedGender()
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		base.compClass = typeof(CompFixedGender);
	}
}
