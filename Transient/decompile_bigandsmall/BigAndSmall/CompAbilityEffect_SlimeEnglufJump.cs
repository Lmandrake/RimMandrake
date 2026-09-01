using System;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_SlimeEnglufJump : CompAbilityEffect_SlimeEngluf_Abstract, ICompAbilityEffectOnJumpCompleted
{
	public override CompProperties_AbilityEngluf_Abstract Props => (CompProperties_AbilityEnglufJump)(object)((AbilityComp)this).props;

	public void OnJumpCompleted(IntVec3 origin, LocalTargetInfo target)
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		try
		{
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
		catch (Exception ex)
		{
			Log.Error($"Error in OnJumpCompleted (target {((LocalTargetInfo)(ref target)).Pawn}, user: {((AbilityComp)this).parent?.pawn}).\n{ex.Message}\n{ex.StackTrace}");
		}
	}
}
