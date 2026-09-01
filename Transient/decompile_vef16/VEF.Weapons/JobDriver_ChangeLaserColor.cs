using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

public class JobDriver_ChangeLaserColor : JobDriver
{
	private Thing Gun
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	private IBeamColorThing BeamColorThing
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return ((LocalTargetInfo)(ref target)).Thing as IBeamColorThing;
		}
	}

	private Thing Prism
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)2);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		if (BeamColorThing == null)
		{
			return false;
		}
		if (ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(Gun), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false))
		{
			return ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(Prism), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
		}
		return false;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnDespawnedNullOrForbidden<JobDriver_ChangeLaserColor>(this, (TargetIndex)1);
		yield return ToilFailConditions.FailOnSomeonePhysicallyInteracting<Toil>(ToilFailConditions.FailOnDespawnedNullOrForbidden<Toil>(Toils_Goto.GotoThing((TargetIndex)2, (PathEndMode)2, false), (TargetIndex)2), (TargetIndex)2);
		yield return Toils_Haul.StartCarryThing((TargetIndex)2, false, false, false, true, false);
		yield return ToilFailConditions.FailOnDespawnedOrNull<Toil>(Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false), (TargetIndex)1);
		Toil val = Toils_General.Wait(75, (TargetIndex)0);
		ToilFailConditions.FailOnDespawnedOrNull<Toil>(val, (TargetIndex)1);
		ToilFailConditions.FailOnCannotTouch<Toil>(val, (TargetIndex)1, (PathEndMode)2);
		ToilEffects.WithEffect(val, ((BuildableDef)Gun.def).repairEffect, (TargetIndex)1, (Color?)null);
		ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)1, false, -0.5f);
		yield return val;
		Toil val2 = ToilMaker.MakeToil("MakeNewToils");
		val2.initAction = delegate
		{
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			BeamColorThing.BeamColor = base.pawn.CurJob.maxNumMeleeAttacks;
			TargetInfo val3 = default(TargetInfo);
			((TargetInfo)(ref val3))._002Ector(Gun.Position, ((JobDriver)this).Map, false);
			Effecter obj = EffecterDefOf.Deflect_Metal.Spawn();
			obj.Trigger(val3, val3, -1);
			obj.Cleanup();
			Prism.Destroy((DestroyMode)0);
		};
		yield return val2;
	}
}
