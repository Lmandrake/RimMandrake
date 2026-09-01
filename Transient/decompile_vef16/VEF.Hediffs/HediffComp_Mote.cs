using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Hediffs;

public class HediffComp_Mote : HediffComp
{
	public Mote mote;

	public HediffCompProperties_Mote Props => base.props as HediffCompProperties_Mote;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (mote == null || ((Thing)mote).Destroyed)
		{
			mote = MoteMaker.MakeAttachedOverlay((Thing)(object)((HediffComp)this).Pawn, Props.mote, Vector3.zero, Props.scale, -1f);
		}
		else
		{
			mote.Maintain();
		}
	}

	public override void CompPostPostRemoved()
	{
		((HediffComp)this).CompPostPostRemoved();
		if (mote != null)
		{
			((Thing)mote).Destroy((DestroyMode)0);
		}
	}
}
