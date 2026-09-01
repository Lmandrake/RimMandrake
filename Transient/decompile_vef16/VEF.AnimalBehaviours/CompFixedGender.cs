using Verse;

namespace VEF.AnimalBehaviours;

public class CompFixedGender : ThingComp
{
	private bool changeGenderOnce = true;

	public CompProperties_FixedGender Props => (CompProperties_FixedGender)(object)base.props;

	public void ExposeData()
	{
		Scribe_Values.Look<bool>(ref changeGenderOnce, "changeGenderOnce", true, false);
	}

	public override void CompTick()
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTick();
		if (changeGenderOnce && ((Thing)base.parent).Map != null)
		{
			ThingWithComps parent = base.parent;
			((Pawn)((parent is Pawn) ? parent : null)).gender = Props.gender;
			changeGenderOnce = false;
		}
	}
}
