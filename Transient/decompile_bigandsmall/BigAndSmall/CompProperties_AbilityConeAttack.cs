using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_AbilityConeAttack : CompProperties_AbilityEffect
{
	public ThingDef projectileDef;

	public int maxDistance = 10;

	public int minDistnace;

	public int maxAngle = 90;

	public int minAngle = 90;

	public int maxConeLength = 9999;

	public int minimumRadiusAroundTarget;

	public List<StatScaling> scaling = new List<StatScaling>();

	public ProjectileByStat projectileByStat;

	public ThingDef GetProjectile(Pawn pawn)
	{
		return projectileByStat?.GetProjectileByStat(projectileDef, pawn) ?? projectileDef;
	}

	public CompProperties_AbilityConeAttack()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_ConeAttack);
	}
}
