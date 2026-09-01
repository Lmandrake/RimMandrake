using Verse;

namespace VEF.Pawns;

public class CompDependsOnBuilding : ThingComp
{
	public Building myBuilding;

	public CompProperties_DependsOnBuilding Props => (CompProperties_DependsOnBuilding)(object)base.props;

	public virtual void OnBuildingDestroyed(CompPawnDependsOn compPawnDependsOn)
	{
	}

	public override void CompTick()
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTick();
		if (myBuilding != null && ((Pawn)base.parent).Dead)
		{
			ThingCompUtility.TryGetComp<CompPawnDependsOn>((Thing)(object)myBuilding).OnPawnDestroyed();
			ThingCompUtility.TryGetComp<CompPawnDependsOn>((Thing)(object)myBuilding).myPawn = null;
			myBuilding = null;
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Building>(ref myBuilding, "myBuilding", false);
	}
}
