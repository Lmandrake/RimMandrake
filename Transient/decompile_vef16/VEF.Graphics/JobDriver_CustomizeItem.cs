using System;
using System.Collections.Generic;
using Verse;
using Verse.AI;

namespace VEF.Graphics;

public class JobDriver_CustomizeItem : JobDriver
{
	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		return ReservationUtility.Reserve(base.pawn, ((JobDriver)this).TargetA, base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		yield return Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false);
		yield return ToilEffects.WithProgressBarToilDelay(Toils_General.Wait(120, (TargetIndex)1), (TargetIndex)1, true, -0.5f);
		yield return Toils_General.Do((Action)delegate
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo targetA = ((JobDriver)this).TargetA;
			ThingCompUtility.TryGetComp<CompGraphicCustomization>(((LocalTargetInfo)(ref targetA)).Thing).Customize();
		});
	}
}
