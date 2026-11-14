using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>The dig and fill jobs' engine: vanilla <see cref="JobDriver_AffectFloor"/> with its work kept per square
	/// (RIMMANDRAKE_KEEP_DIG_PROGRESS_ACROSS_MEALS_AND_NAPS; see <see cref="RM_DigProgressMath"/>). Vanilla's toils run as
	/// they are (designation FailOn, Goto, the work tick at 1.7 x the speed stat, the bar, DoEffect then the designation's
	/// deletion). Two hooks, neither per tick: the work toil's initAction, after vanilla sets workLeft to the full work,
	/// takes the square's parked work off it; a finish action parks what an unfinished job did on a standing order. A job
	/// mid-work saves vanilla's workLeft as before, plus the total it started from.</summary>
	public abstract class RM_JobDriver_ShovelFloor : JobDriver_AffectFloor
	{
		/// <summary>vanilla's private countdown, read and written only when the work starts and when the job ends. Null if a
		/// game update renamed it: the jobs then run as vanilla (work not kept), never broken.</summary>
		private static readonly AccessTools.FieldRef<JobDriver_AffectFloor, float> WorkLeft = WorkLeftRef();

		private static AccessTools.FieldRef<JobDriver_AffectFloor, float> WorkLeftRef()
		{
			try
			{
				return AccessTools.FieldRefAccess<JobDriver_AffectFloor, float>("workLeft");
			}
			catch (Exception e)
			{
				Log.Warning("[FlowWorks] JobDriver_AffectFloor.workLeft not found; dig and fill work is not kept across breaks: " + e.Message);
				return null;
			}
		}

		/// <summary>The work total the work toil started from (vanilla's BaseWorkAmount then).</summary>
		private float rmWorkTotal;

		private bool rmWorkStarted;

		/// <summary>Fill and dig work on a square are kept apart.</summary>
		protected abstract bool IsFill { get; }

		/// <summary>True after DoEffect when the finished work was not spent (a cut refused at this digger's cap that someone
		/// else may still make): it is parked for them rather than lost.</summary>
		protected virtual bool KeepWorkAfterEffect => false;

		/// <summary>Subclasses add their own finish actions BEFORE calling this, so the dig's re-designation runs first and an
		/// order it restores counts as standing.</summary>
		protected override IEnumerable<Toil> MakeNewToils()
		{
			AddFinishAction(delegate (JobCondition cond)
			{
				ParkUnfinishedWork();
			});
			return ResumeOnWorkToil(base.MakeNewToils());
		}

		private IEnumerable<Toil> ResumeOnWorkToil(IEnumerable<Toil> vanilla)
		{
			foreach (Toil t in vanilla)
			{
				// vanilla's work toil: the only one that never completes by itself and ticks (Goto completes on arrival)
				if (t.defaultCompleteMode == ToilCompleteMode.Never && t.initAction != null && t.tickIntervalAction != null)
				{
					Action setFullWork = t.initAction;
					t.initAction = delegate
					{
						setFullWork();
						ResumeParkedWork();
					};
				}
				yield return t;
			}
		}

		private void ResumeParkedWork()
		{
			if (WorkLeft == null)
			{
				return;
			}
			float total = WorkLeft(this);
			rmWorkTotal = total;
			rmWorkStarted = true;
			Map map = pawn?.MapHeld;
			if (map == null || !job.targetA.IsValid)
			{
				return;
			}
			float parked = map.GetComponent<RM_MapComponent_DigProgress>()?.Take(job.targetA.Cell, IsFill) ?? 0f;
			WorkLeft(this) = RM_DigProgressMath.WorkLeftAtStart(total, parked);
		}

		private void ParkUnfinishedWork()
		{
			Map map = pawn?.MapHeld;
			if (WorkLeft == null || map == null || job == null || !job.targetA.IsValid)
			{
				return;
			}
			float workLeft = WorkLeft(this);
			bool started = rmWorkStarted;
			float total = rmWorkTotal;
			if (!started && RM_DigProgressMath.WasMidWork(workLeft))
			{
				// a job saved mid-work before this fix: vanilla's countdown, against today's total
				started = true;
				total = Math.Max(workLeft, BaseWorkAmount);
			}
			float done = RM_DigProgressMath.DoneAtEnd(total, workLeft, started);
			bool landed = workLeft <= 0f && !KeepWorkAfterEffect;
			IntVec3 c = job.targetA.Cell;
			bool orderStands = job.ignoreDesignations || map.designationManager.DesignationAt(c, DesDef) != null;
			if (RM_DigProgressMath.Keep(done, landed, orderStands))
			{
				map.GetComponent<RM_MapComponent_DigProgress>()?.Put(c, IsFill, done);
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref rmWorkTotal, "rmShovelWorkTotal", 0f);
			Scribe_Values.Look(ref rmWorkStarted, "rmShovelWorkStarted", false);
		}
	}
}
