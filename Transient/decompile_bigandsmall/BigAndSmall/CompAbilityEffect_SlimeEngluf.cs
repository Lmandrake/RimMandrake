using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_SlimeEngluf : CompAbilityEffect_SlimeEngluf_Abstract
{
	public override CompProperties_AbilityEngluf_Abstract Props => (CompProperties_AbilityEngluf)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn == null)
		{
			return;
		}
		foreach (int item in Enumerable.Range(0, Rand.Range(2, 6)))
		{
			_ = item;
			IntVec3 cell = ((LocalTargetInfo)(ref target)).Cell;
			FleckMaker.ThrowDustPuff(((IntVec3)(ref cell)).ToVector3ShiftedWithAltitude((AltitudeLayer)12), ((Thing)((AbilityComp)this).parent.pawn).Map, 1f);
		}
		DoEngulf(((AbilityComp)this).parent.pawn, pawn);
	}
}
