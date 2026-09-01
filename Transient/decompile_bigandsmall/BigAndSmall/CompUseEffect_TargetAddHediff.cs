using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompUseEffect_TargetAddHediff : CompTargetEffect
{
	public CompProperties_TargetAddHediff Props => (CompProperties_TargetAddHediff)(object)((ThingComp)this).props;

	public override void DoEffectOn(Pawn _, Thing target)
	{
		Pawn val = (Pawn)(object)((target is Pawn) ? target : null);
		if (val != null)
		{
			val.health.AddHediff(Props.hediffDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}
}
