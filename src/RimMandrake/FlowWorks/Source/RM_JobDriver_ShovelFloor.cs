using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>The dig and fill jobs' engine: vanilla <see cref="JobDriver_AffectFloor"/>'s toils, rebuilt so hours of shovel
	/// work no longer hold a pawn until it starves (live, save NS_Pyrelands_play_q_col_d3dig: over 10 game hours on one
	/// square, food 0.05, thirst 0.0, square still undug; see <see cref="RM_DigProgressMath"/>).
	///
	/// Two changes, everything else as vanilla (designation FailOn, Goto Touch, FailOnCannotTouch, progress bar,
	/// Construction learning, the speed stat at 1.7 per tick, DoEffect then the designation's deletion, same two-toil
	/// layout so a saved toil index lands on the same toil):
	///  1. The job re-reads the think tree every <see cref="RM_DigProgressMath.OverrideCheckTicks"/> ticks
	///     (expiryInterval + checkOverrideOnExpire): Pawn_JobTracker.CheckForJobOverride starts food, drink, rest, joy or a
	///     fire job over it, and with nothing better it keeps digging (same JobDef from the same JobGiver is a continuation).
	///  2. The work done is the driver's own, saved with the job, and when the job ends unfinished on a standing order it
	///     is parked per square in <see cref="RM_MapComponent_DigProgress"/>; the next job on the square starts from it.
	/// Vanilla's per-job private workLeft lost all of it on any interruption.</summary>
	public abstract class RM_JobDriver_ShovelFloor : JobDriver_AffectFloor
	{
		/// <summary>Vanilla's private countdown, read once to carry on a job saved before this driver existed.</summary>
		private static readonly FieldInfo VanillaWorkLeft = AccessTools.Field(typeof(JobDriver_AffectFloor), "workLeft");

		private float workDone;

		private float workTotal;

		/// <summary>Set when the work completed and DoEffect spent it; not saved (the job ends the same tick).</summary>
		private bool workLanded;

		/// <summary>Fill and dig work on a square are kept apart.</summary>
		protected abstract bool IsFill { get; }

		/// <summary>True after DoEffect when the finished work was not spent (a cut refused at this digger's cap that someone
		/// else may still make): the work is parked for them rather than lost.</summary>
		protected virtual bool KeepWorkAfterEffect => false;

		public override void Notify_Starting()
		{
			base.Notify_Starting();
			EnsureInterruptible();
		}

		/// <summary>Set at the start and checked every work tick, so a job saved without it (an old save, a job made by
		/// another mod or a bridge tool) gets it too.</summary>
		private void EnsureInterruptible()
		{
			if (job != null && (job.expiryInterval != RM_DigProgressMath.OverrideCheckTicks || !job.checkOverrideOnExpire))
			{
				job.expiryInterval = RM_DigProgressMath.OverrideCheckTicks;
				job.checkOverrideOnExpire = true;
			}
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			// Added after any finish action the subclass added before calling this, so the dig's re-designation runs first
			// and the order it restores counts as standing.
			AddFinishAction(delegate (JobCondition cond)
			{
				ParkUnfinishedWork();
			});
			return ShovelToils();
		}

		private IEnumerable<Toil> ShovelToils()
		{
			this.FailOn(() => !job.ignoreDesignations && Map.designationManager.DesignationAt(TargetLocA, DesDef) == null);
			yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);
			Toil doWork = ToilMaker.MakeToil("RM_ShovelWork");
			doWork.initAction = delegate
			{
				BeginWork(TakeParked());
			};
			doWork.tickIntervalAction = delegate (int delta)
			{
				if (workTotal <= 0f)
				{
					// loaded mid-work from a save made before this driver: vanilla's countdown says how far it got
					float old = VanillaWorkLeft != null ? (float)VanillaWorkLeft.GetValue(this) : -1000f;
					BeginWork(0f);
					float carried = RM_DigProgressMath.FromWorkLeft(old, workTotal);
					workDone = carried > 0f ? carried : TakeParked();
				}
				EnsureInterruptible();
				Pawn actor = doWork.actor;
				StatDef stat = SpeedStat;
				float speed = stat != null && !stat.Worker.IsDisabledFor(actor) ? actor.GetStatValue(stat) : 1f;
				workDone = RM_DigProgressMath.AfterTicks(workDone, speed, delta);
				actor.skills?.Learn(SkillDefOf.Construction, 0.1f * delta);
				if (clearSnow)
				{
					Map.snowGrid.SetDepth(TargetLocA, 0f);
					Map.sandGrid?.SetDepth(TargetLocA, 0f);
				}
				if (RM_DigProgressMath.Finished(workDone, workTotal))
				{
					IntVec3 c = TargetLocA;
					DoEffect(c);
					workLanded = !KeepWorkAfterEffect;
					Map.designationManager.DesignationAt(c, DesDef)?.Delete();
					ReadyForNextToil();
				}
			};
			doWork.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			doWork.WithProgressBar(TargetIndex.A, () => RM_DigProgressMath.Fraction(workDone, workTotal));
			doWork.defaultCompleteMode = ToilCompleteMode.Never;
			doWork.activeSkill = () => SkillDefOf.Construction;
			yield return doWork;
		}

		private void BeginWork(float resumed)
		{
			// never 0: vanilla finished a zero-work job on its first tick, and so does this
			workTotal = System.Math.Max(1, BaseWorkAmount);
			workDone = resumed;
			workLanded = false;
		}

		private float TakeParked()
		{
			Map map = Map;
			if (map == null || !job.targetA.IsValid)
			{
				return 0f;
			}
			return map.GetComponent<RM_MapComponent_DigProgress>()?.Take(job.targetA.Cell, IsFill) ?? 0f;
		}

		private void ParkUnfinishedWork()
		{
			Map map = pawn?.MapHeld;
			if (map == null || job == null || !job.targetA.IsValid)
			{
				return;
			}
			IntVec3 c = job.targetA.Cell;
			bool orderStands = job.ignoreDesignations || map.designationManager.DesignationAt(c, DesDef) != null;
			if (RM_DigProgressMath.Keep(workDone, workLanded, orderStands))
			{
				map.GetComponent<RM_MapComponent_DigProgress>()?.Put(c, IsFill, workDone);
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref workDone, "rmShovelWorkDone", 0f);
			Scribe_Values.Look(ref workTotal, "rmShovelWorkTotal", 0f);
		}
	}
}
