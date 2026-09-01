using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompTargetEffect_ApplySoulstone : CompTargetEffect
{
	public CompProperties_ApplySoulstone Props => (CompProperties_ApplySoulstone)(object)((ThingComp)this).props;

	public override void DoEffectOn(Pawn user, Thing target)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((target is Pawn) ? target : null);
		if (val == null)
		{
			return;
		}
		CompAbilityEffect_ConsumeSoul.MakeGetSoulCollectorHediff(val).AddSoulPowerDirect(Props.factor, Props.falloff);
		if (((val != null) ? ((Thing)val).Map : null) == null)
		{
			return;
		}
		ThingDef filth_Blood = ThingDefOf.Filth_Blood;
		for (int i = 0; i < 2; i++)
		{
			IntVec3 val2 = ((Thing)val).Position + GenRadial.RadialPattern[i];
			if (GenGrid.InBounds(val2, ((Thing)val).Map))
			{
				FilthMaker.TryMakeFilth(val2, ((Thing)val).Map, filth_Blood, 1, (FilthSourceFlags)0, true);
			}
		}
	}
}
