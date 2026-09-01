using System;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.AnimalBehaviours;

public class CompBlink : ThingComp
{
	public CompProperties_Blink Props => (CompProperties_Blink)(object)base.props;

	public override void CompTickInterval(int delta)
	{
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_019b: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_0285: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!AnimalBehaviours_Settings.flagBlinkMechanics || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.blinkInterval, delta))
		{
			return;
		}
		Pawn pawn = default(Pawn);
		ref Pawn reference = ref pawn;
		ThingWithComps parent = base.parent;
		reference = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (ModsConfig.OdysseyActive)
		{
			Pawn_TrainingTracker training = pawn.training;
			if (training != null && training.HasLearned(InternalDefOf.VEF_ControlledBlinking))
			{
				return;
			}
		}
		if (((Thing)pawn).Map == null || pawn.CurJob == null)
		{
			return;
		}
		IntVec3 position2 = default(IntVec3);
		if (pawn.CurJob.def == JobDefOf.GotoWander || pawn.CurJob.def == JobDefOf.Wait_Wander || pawn.CurJob.def == JobDefOf.Wait_MaintainPosture)
		{
			IntVec3 position = default(IntVec3);
			if (CellFinderLoose.TryFindRandomNotEdgeCellWith(10, (Predicate<IntVec3>)((IntVec3 x) => IntVec3Utility.DistanceTo(x, ((Thing)base.parent).Position) < (float)((IntRange)(ref Props.distance)).RandomInRange), ((Thing)base.parent).Map, ref position))
			{
				if (Props.warpEffect && !Props.effectOnlyWhenManhunter)
				{
					FleckMaker.Static(((Thing)base.parent).Position, ((Thing)pawn).Map, FleckDefOf.PsycastAreaEffect, 10f);
				}
				pawn.pather.StopDead();
				((Thing)pawn).Position = position;
				pawn.pather.ResetToCurrentPosition();
				IntVec3 val = default(IntVec3);
				CellFinder.TryFindRandomCellNear(((Thing)pawn).Position, ((Thing)pawn).Map, 10, (Predicate<IntVec3>)null, ref val, -1);
				pawn.pather.StartPath(LocalTargetInfo.op_Implicit(val), (PathEndMode)3);
			}
		}
		else if ((pawn.CurJob.def == JobDefOf.AttackMelee || pawn.mindState.mentalStateHandler.InMentalState) && Props.blinkWhenManhunter && IntVec3Utility.DistanceTo(((Thing)base.parent).Position, ((LocalTargetInfo)(ref pawn.CurJob.targetA)).Cell) > 2f && CellFinderLoose.TryFindRandomNotEdgeCellWith(10, (Predicate<IntVec3>)((IntVec3 x) => IntVec3Utility.DistanceTo(x, ((LocalTargetInfo)(ref pawn.CurJob.targetA)).Cell) < (float)((IntRange)(ref Props.distance)).RandomInRange), ((Thing)base.parent).Map, ref position2))
		{
			if (Props.warpEffect)
			{
				FleckMaker.Static(((Thing)base.parent).Position, ((Thing)pawn).Map, FleckDefOf.PsycastAreaEffect, 10f);
			}
			pawn.pather.StopDead();
			((Thing)pawn).Position = position2;
			pawn.pather.ResetToCurrentPosition();
			pawn.pather.StartPath(LocalTargetInfo.op_Implicit(((LocalTargetInfo)(ref pawn.CurJob.targetA)).Cell), (PathEndMode)3);
		}
	}
}
