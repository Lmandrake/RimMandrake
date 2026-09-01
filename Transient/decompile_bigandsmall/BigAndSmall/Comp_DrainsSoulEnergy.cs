using Verse;

namespace BigAndSmall;

public class Comp_DrainsSoulEnergy : Comp_DrainsResource
{
	protected readonly SoulEnergyTracker soulTracker = new SoulEnergyTracker();

	protected SoulResourceHediff Resource => soulTracker.Resource(((Hediff)((HediffComp)this).parent).pawn);

	protected override void DrainResource()
	{
		if (Resource != null)
		{
			Resource.Value -= 0.01f;
			if (Resource.Value <= 0f && base.Props.removeOnZero)
			{
				((Hediff)((HediffComp)this).parent).pawn.health.RemoveHediff((Hediff)(object)((HediffComp)this).parent);
			}
		}
	}
}
