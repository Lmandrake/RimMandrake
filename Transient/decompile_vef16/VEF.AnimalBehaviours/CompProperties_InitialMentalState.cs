using Verse;

namespace VEF.AnimalBehaviours;

public class CompProperties_InitialMentalState : CompProperties
{
	public MentalStateDef mentalstate;

	public CompProperties_InitialMentalState()
	{
		base.compClass = typeof(CompInitialMentalState);
	}
}
