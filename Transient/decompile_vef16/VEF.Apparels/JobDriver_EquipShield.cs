using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Apparels;

public class JobDriver_EquipShield : JobDriver_Equip
{
	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		return ReservationUtility.Reserve(((JobDriver)this).pawn, ((JobDriver)this).job.targetA, ((JobDriver)this).job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
	}

	protected override IEnumerable<Toil> MakeNewToils()
	{
		ToilFailConditions.FailOnDestroyedOrNull<JobDriver_EquipShield>(this, (TargetIndex)1);
		ToilFailConditions.FailOnBurningImmobile<JobDriver_EquipShield>(this, (TargetIndex)1);
		yield return ToilFailConditions.FailOnDespawnedNullOrForbidden<Toil>(Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)3, false), (TargetIndex)1);
		Toil val = ToilMaker.MakeToil("MakeNewToils");
		val.initAction = delegate
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Expected O, but got Unknown
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_003a: Expected O, but got Unknown
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_0085: Expected O, but got Unknown
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00bb: Expected O, but got Unknown
			ThingWithComps val2 = (ThingWithComps)((LocalTargetInfo)(ref ((JobDriver)this).job.targetB)).Thing;
			ThingWithComps val3;
			if (((Thing)val2).def.stackLimit > 1 && ((Thing)val2).stackCount > 1)
			{
				val3 = (ThingWithComps)((Thing)val2).SplitOff(1);
			}
			else
			{
				val3 = val2;
				if (((Thing)val3).Spawned)
				{
					((Entity)val3).DeSpawn((DestroyMode)0);
				}
				else
				{
					((Thing)val3).ParentHolder.GetDirectlyHeldThings().Remove((Thing)(object)val3);
				}
			}
			((JobDriver)this).pawn.MakeRoomForShield(val3);
			((JobDriver)this).pawn.apparel.Wear((Apparel)val3, true, false);
			if (((JobDriver)this).pawn.outfits != null && ((JobDriver)this).job.playerForced)
			{
				((JobDriver)this).pawn.outfits.forcedHandler.SetForced((Apparel)val3, true);
			}
			if (((Thing)val2).def.soundInteract != null)
			{
				SoundStarter.PlayOneShot(((Thing)val2).def.soundInteract, SoundInfo.op_Implicit(new TargetInfo(((Thing)((JobDriver)this).pawn).Position, ((Thing)((JobDriver)this).pawn).Map, false)));
			}
		};
		val.defaultCompleteMode = (ToilCompleteMode)1;
		yield return val;
	}
}
