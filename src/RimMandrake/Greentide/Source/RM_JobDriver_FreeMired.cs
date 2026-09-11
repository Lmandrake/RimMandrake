using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 (M8, mire half). One pawn hauls another
	/// free of a churnmud mire: walk adjacent, work a fixed toil, then zero
	/// the target's RM_Mired severity. Standard three-toil JobDriver shape
	/// (goto / wait-with-progress-bar / effect), no vanilla base class fits
	/// a pawn-target rescue-style interaction the way JobDriver_AffectFloor
	/// fits cell work.
	/// </summary>
	public class RM_JobDriver_FreeMired : JobDriver
	{
		private const int WorkTicks = 240;

		private Pawn Target => (Pawn)job.targetA.Thing;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(Target, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedOrNull(TargetIndex.A);
			this.FailOn(() => !Target.health.hediffSet.HasHediff(RM_DefOf.RM_Mired));

			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

			Toil work = Toils_General.Wait(WorkTicks);
			work.WithProgressBarToilDelay(TargetIndex.A);
			work.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			yield return work;

			Toil finish = ToilMaker.MakeToil("FreeMired");
			finish.initAction = delegate
			{
				Hediff mired = Target.health.hediffSet.GetFirstHediffOfDef(RM_DefOf.RM_Mired);
				if (mired != null)
				{
					Target.health.RemoveHediff(mired);
				}
				Messages.Message("RM_Greentide_PulledFree".Translate(Target.LabelShort, pawn.LabelShort), Target, MessageTypeDefOf.PositiveEvent);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
