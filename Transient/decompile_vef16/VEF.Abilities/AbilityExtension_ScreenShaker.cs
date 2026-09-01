using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class AbilityExtension_ScreenShaker : AbilityExtension_AbilityMod
{
	public float intensity;

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		Find.CameraDriver.shaker.DoShake(intensity);
	}
}
