using System;
using System.Collections.Generic;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace VEF.Abilities;

public class JobDriver_CastAbilityOnce : JobDriver
{
	private CompAbilities cachedComp;

	public CompAbilities CompAbilities
	{
		get
		{
			if (cachedComp == null)
			{
				cachedComp = ((ThingWithComps)base.pawn).GetComp<CompAbilities>();
			}
			return cachedComp;
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		if (CompAbilities.currentlyCasting.def.reserveTargets)
		{
			List<LocalTargetInfo> list = new List<LocalTargetInfo>();
			GlobalTargetInfo[] currentTargets = CompAbilities.currentlyCasting.currentTargets;
			for (int i = 0; i < currentTargets.Length; i++)
			{
				GlobalTargetInfo val = currentTargets[i];
				if (((GlobalTargetInfo)(ref val)).HasThing)
				{
					list.Add(new LocalTargetInfo(((GlobalTargetInfo)(ref val)).Thing));
				}
				else
				{
					list.Add(new LocalTargetInfo(((GlobalTargetInfo)(ref val)).Cell));
				}
			}
			ReservationUtility.ReserveAsManyAsPossible(base.pawn, list, base.job, 1, -1, (ReservationLayerDef)null);
		}
		return true;
	}

	public override string GetReport()
	{
		return CompAbilities.currentlyCasting.def.JobReportString;
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnDespawnedOrNull<JobDriver_CastAbilityOnce>(this, (TargetIndex)1);
		base.job.playerForced = true;
		CompAbilities comp = CompAbilities;
		Toil val = Toils_General.Wait(comp.currentlyCasting.GetCastTimeForPawn(), (TargetIndex)1);
		ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)3, false, -0.5f);
		val.AddPreInitAction((Action)delegate
		{
			comp.currentlyCasting.PreWarmupAction();
		});
		LocalTargetInfo targetA = ((JobDriver)this).TargetA;
		if (((LocalTargetInfo)(ref targetA)).Pawn != base.pawn)
		{
			val.AddPreTickAction((Action)delegate
			{
				//IL_003f: Unknown result type (might be due to invalid IL or missing references)
				if (comp.currentlyCasting.def.drawAimPie && Find.Selector.IsSelected((object)base.pawn))
				{
					GenDraw.DrawAimPie((Thing)(object)base.pawn, ((JobDriver)this).TargetA, base.ticksLeftThisToil, 0.2f);
				}
			});
		}
		comp.currentlyCasting.WarmupToil(val);
		yield return val;
		Toil val2 = ToilMaker.MakeToil("MakeNewToils");
		val2.initAction = delegate
		{
			//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
			base.job.playerForced = !base.pawn.Drafted;
			GlobalTargetInfo[] currentlyCastingTargets = comp.currentlyCastingTargets;
			if (currentlyCastingTargets.Length == 1 && ((GlobalTargetInfo)(ref currentlyCastingTargets[0])).Map == ((Thing)base.pawn).Map)
			{
				comp.currentlyCasting.Cast((GlobalTargetInfo[])(object)new GlobalTargetInfo[1] { (((GlobalTargetInfo)(ref currentlyCastingTargets[0])).Thing != null) ? new GlobalTargetInfo(((GlobalTargetInfo)(ref currentlyCastingTargets[0])).Thing) : new GlobalTargetInfo(((GlobalTargetInfo)(ref currentlyCastingTargets[0])).Cell, ((GlobalTargetInfo)(ref currentlyCastingTargets[0])).Map, false) });
			}
			else
			{
				comp.currentlyCasting.Cast(currentlyCastingTargets);
			}
		};
		val2.defaultCompleteMode = (ToilCompleteMode)1;
		val2.atomicWithPrevious = true;
		yield return val2;
		((JobDriver)this).AddFinishAction((Action<JobCondition>)delegate
		{
			comp.currentlyCasting.EndCastJob();
		});
	}
}
