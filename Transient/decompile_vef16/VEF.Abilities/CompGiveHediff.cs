using RimWorld;
using Verse;

namespace VEF.Abilities;

internal class CompGiveHediff : CompAbilityEffect
{
	public CompProperties_GiveHediff Props => (CompProperties_GiveHediff)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		if (Props.applyToCaster)
		{
			((AbilityComp)this).parent.pawn.health.AddHediff(Props.hediffDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
		if (!Props.applyToRadius)
		{
			return;
		}
		foreach (Pawn item in ((Thing)((AbilityComp)this).parent.pawn).Map.mapPawns.AllPawnsSpawned)
		{
			if (((Thing)item).Spawned)
			{
				IntVec3 position = ((Thing)item).Position;
				if (((IntVec3)(ref position)).InHorDistOf(((LocalTargetInfo)(ref target)).Cell, ((AbilityComp)this).parent.def.EffectRadius))
				{
					item.health.AddHediff(Props.hediffDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
			}
		}
	}
}
