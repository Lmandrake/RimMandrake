using Verse;

namespace VEF.Hediffs;

public class HediffCompProperties_Draw : HediffCompProperties
{
	public GraphicData graphic;

	public override void PostLoad()
	{
		((HediffCompProperties)this).PostLoad();
		ShieldsSystem.ApplyDrawPatches();
	}
}
