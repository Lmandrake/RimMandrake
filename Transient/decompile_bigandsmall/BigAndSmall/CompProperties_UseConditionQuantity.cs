using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_UseConditionQuantity : CompProperties_UseEffect
{
	public int quantity = 1;

	public string failMessage = "Needs at least 1 to use.";

	public CompProperties_UseConditionQuantity()
	{
		((CompProperties)this).compClass = typeof(CompUseConditionQuantity);
	}
}
