using Verse;

namespace BigAndSmall;

public class CompProperties_CanCancelHediff : HediffCompProperties
{
	public string iconPath = "UI/Designators/Cancel";

	public CompProperties_CanCancelHediff()
	{
		base.compClass = typeof(Comp_CanCancelHediff);
	}
}
