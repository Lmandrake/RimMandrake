using Verse;

namespace VEF.Buildings;

public class RefuelableExtension : DefModExtension
{
	public bool ejectingFuelRespectsFuelMultiplier;

	public CustomFillableBarGaugeData customFuelGauge;

	public override void ResolveReferences(Def parentDef)
	{
		((DefModExtension)this).ResolveReferences(parentDef);
		if (ejectingFuelRespectsFuelMultiplier)
		{
			VanillaExpandedFramework_CompRefuelable_EjectFuelPatches.patchActive = true;
		}
		if (customFuelGauge != null)
		{
			VanillaExpandedFramework_CompRefuelable_PostDraw_Patch.patchActive = true;
			customFuelGauge.ResolveReferences();
		}
	}
}
