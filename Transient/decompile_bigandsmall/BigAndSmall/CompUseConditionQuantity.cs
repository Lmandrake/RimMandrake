using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompUseConditionQuantity : CompUseEffect
{
	public override float OrderPriority => -100f;

	public CompProperties_UseConditionQuantity Props => (CompProperties_UseConditionQuantity)(object)((ThingComp)this).props;

	public override AcceptanceReport CanBeUsedBy(Pawn p)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		CompProperties_UseConditionQuantity props = Props;
		if (((Thing)((ThingComp)this).parent).stackCount < props.quantity)
		{
			return new AcceptanceReport(props.failMessage);
		}
		return AcceptanceReport.op_Implicit(true);
	}

	public override void DoEffect(Pawn usedBy)
	{
		((Thing)((ThingComp)this).parent).SplitOff(Props.quantity).Destroy((DestroyMode)0);
	}
}
