using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperticesIntegrateGenesEffect : CompAbilityEffect
{
	public CompPropertiesMimicOff Props => (CompPropertiesMimicOff)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		Discombobulator.IntegrateGenes(((AbilityComp)this).parent.pawn);
	}
}
