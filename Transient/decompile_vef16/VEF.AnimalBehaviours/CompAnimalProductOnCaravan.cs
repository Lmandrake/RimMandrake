using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompAnimalProductOnCaravan : ThingComp
{
	public CompProperties_AnimalProductOnCaravan Props => (CompProperties_AnimalProductOnCaravan)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Invalid comparison between Unknown and I4
		if (!Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.gatheringIntervalTicks, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (Props.femaleOnly && (int)val.gender != 2)
		{
			return;
		}
		Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)val);
		if (caravan != null)
		{
			float num = Props.resourceDef.BaseMass * (float)Props.resourceAmount;
			if (caravan.MassUsage + num < caravan.MassCapacity)
			{
				Thing val2 = ThingMaker.MakeThing(Props.resourceDef, (ThingDef)null);
				val2.stackCount = Props.resourceAmount;
				CaravanInventoryUtility.GiveThing(caravan, val2);
			}
		}
	}

	public override string CompInspectStringExtra()
	{
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Invalid comparison between Unknown and I4
		if (!Props.femaleOnly || (int)((Pawn)base.parent).gender == 2)
		{
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF_WhileCaravaning", NamedArgument.op_Implicit(Props.resourceAmount), NamedArgument.op_Implicit(((Def)Props.resourceDef).LabelCap)) + ColoredText.Colorize(GenDate.ToStringTicksToPeriod(Props.gatheringIntervalTicks, true, false, true, true, false), ColoredText.DateTimeColor));
		}
		return null;
	}
}
