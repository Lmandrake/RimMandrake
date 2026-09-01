using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_DieAndChangeIntoOtherDef : CompProperties
{
	public bool needsDiggableTerrain;

	public bool mustBeTamed = true;

	public ThingDef defToChangeTo;

	public string gizmoImage;

	public string gizmoLabel;

	public string gizmoDesc;

	public CompProperties_DieAndChangeIntoOtherDef()
	{
		base.compClass = typeof(CompDieAndChangeIntoOtherDef);
	}
}
