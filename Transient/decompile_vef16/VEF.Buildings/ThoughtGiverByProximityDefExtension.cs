using Verse;

namespace VEF.Buildings;

public class ThoughtGiverByProximityDefExtension : DefModExtension
{
	public ThingDef ThingToGiveThought;

	public float DistanceToGiveThought = 15f;
}
