using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class Ability_ShootProjectile_Snow : Ability_ShootProjectile
{
	public override void TargetEffects(params GlobalTargetInfo[] targetInfos)
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		base.TargetEffects(targetInfos);
		AbilityExtension_ShootProjectile_Snow modExtension = ((Def)def).GetModExtension<AbilityExtension_ShootProjectile_Snow>();
		for (int i = 0; i < targetInfos.Length; i++)
		{
			GlobalTargetInfo val = targetInfos[i];
			WeatherBuildupUtility.AddSnowRadial(((GlobalTargetInfo)(ref val)).Cell, ((Thing)pawn).Map, modExtension?.radius ?? 3f, modExtension?.depth ?? 1f);
		}
	}
}
