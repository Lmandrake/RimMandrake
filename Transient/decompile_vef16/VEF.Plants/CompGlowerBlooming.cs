using RimWorld;
using Verse;

namespace VEF.Plants;

public class CompGlowerBlooming : CompGlower
{
	private Plant_Blooming plant;

	public CompProperties_GlowerBlooming Props => (CompProperties_GlowerBlooming)(object)((ThingComp)this).props;

	protected override bool ShouldBeLitNow
	{
		get
		{
			if (plant != null && ((Plant)plant).Growth >= 1f && plant.isBlooming)
			{
				return ((CompGlower)this).ShouldBeLitNow;
			}
			return false;
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		plant = ((ThingComp)this).parent as Plant_Blooming;
		((CompGlower)this).PostSpawnSetup(respawningAfterLoad);
	}
}
