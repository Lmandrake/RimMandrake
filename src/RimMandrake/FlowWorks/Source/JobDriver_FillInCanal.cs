using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>Raises a cell one level. Same vanilla JobDriver_AffectFloor
	/// engine the dig job rides, read in the other direction.</summary>
	public class JobDriver_FillInCanal : JobDriver_AffectFloor
	{
		/// <summary>Filling in is cheaper than cutting, and cheaper at every
		/// level: shovelling spoil back into a hole is not the same labour as
		/// cutting it and throwing it clear. Half the dig cost for the level
		/// being undone, so the ladder still costs more the deeper it goes and
		/// a fill-in is never free.</summary>
		protected override int BaseWorkAmount
		{
			get
			{
				Map map = base.Map;
				if (map == null || !job.targetA.IsValid)
				{
					return RM_DigDepthMath.LabourWork(RM_ExcavationDepth.WorkPerLevel / 2, RimMandrakeFlowWorksSettings.digLabourMultiplier);
				}
				IntVec3 c = job.targetA.Cell;
				if (!c.InBounds(map))
				{
					return RM_DigDepthMath.LabourWork(RM_ExcavationDepth.WorkPerLevel / 2, RimMandrakeFlowWorksSettings.digLabourMultiplier);
				}
				RM_MapComponent_Excavation excavation = map.GetComponent<RM_MapComponent_Excavation>();
				byte current = excavation != null
					? excavation.DepthAt(c)
					: RM_ExcavationDepth.DepthOfDryTerrain(map.terrainGrid.BaseTerrainAt(c));
				if (current < 1)
				{
					current = 1;
				}
				// DIG_FILL_TUNE_HOURS_OF_SHOVEL_WORK (owner card 2026-10-25): "... or filling a ditch takes hours".
				return RM_DigDepthMath.LabourWork(RM_ExcavationDepth.WorkToDeepen((byte)(current - 1)) / 2, RimMandrakeFlowWorksSettings.digLabourMultiplier);
			}
		}

		protected override DesignationDef DesDef => RimMandrakeFlowWorks_DefOf.RM_FillInCanal;

		/// <summary>DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY: the pit (Floor layer, as vanilla) and one unit of the gravel or chunk
		/// the filler fetches (targetB; absent for a pit already paid for).</summary>
		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			if (!base.TryMakePreToilReservations(errorOnFailed))
			{
				return false;
			}
			return !job.targetB.IsValid || pawn.Reserve(job.targetB, job, 10, 1, null, errorOnFailed);
		}

		/// <summary>Owner 2026-10-25: "it takes 1 gravel or 2 chunks to put it all back in again". With targetB set the filler
		/// first carries one unit to the pit and tips it in as credit (gravel or crushed ice 2, chunk 1); short of a notch's 2 the job ends
		/// there with the order kept, and the work giver sends someone for more. Then vanilla's fill work, which runs only on
		/// a paid-up pit.</summary>
		protected override IEnumerable<Toil> MakeNewToils()
		{
			// One toil layout whether or not material is fetched: a save taken after the tip has a destroyed targetB, and a
			// layout that dropped the fetch toils on load would put the saved toil index on the wrong toil.
			Toil check = ToilMaker.MakeToil("RM_FillPaidCheck");
			check.initAction = delegate
			{
				// the pit is filled only when paid for; a short pit keeps its order for the next carry
				if (RimMandrakeFlowWorksSettings.fillCostsSpoilEnabled && RM_GroundClassMath.CreditShort(CreditHere()) > 0)
				{
					EndJobWith(job.targetB.IsValid ? JobCondition.Succeeded : JobCondition.Incompletable);
				}
			};
			check.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return Toils_Jump.JumpIf(check, () => !job.targetB.IsValid);
			yield return Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.ClosestTouch).FailOnDespawnedNullOrForbidden(TargetIndex.B)
				.FailOnSomeonePhysicallyInteracting(TargetIndex.B);
			yield return Toils_Haul.StartCarryThing(TargetIndex.B, false, true);
			yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);
			Toil tip = ToilMaker.MakeToil("RM_TipFillMaterial");
			tip.initAction = delegate
			{
				Thing carried = pawn.carryTracker.CarriedThing;
				RM_MapComponent_FillCredit credit = Map.GetComponent<RM_MapComponent_FillCredit>();
				if (carried == null || credit == null)
				{
					EndJobWith(JobCondition.Incompletable);
					return;
				}
				// ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN: by kind (crushed ice pays as gravel does)
				int n = carried.stackCount;
				credit.AddCredit(TargetLocA, n * RM_GroundClassMath.CreditOf(RM_DigSpoil.FillKindOf(carried.def)));
				carried.Destroy();
			};
			tip.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return tip;
			yield return check;
			foreach (Toil t in base.MakeNewToils())
			{
				// a cost switched on mid-work: stop before vanilla's last toil deletes the order of a pit DoEffect left unfilled
				t.FailOn(() => RimMandrakeFlowWorksSettings.fillCostsSpoilEnabled && RM_GroundClassMath.CreditShort(CreditHere()) > 0);
				yield return t;
			}
		}

		private int CreditHere()
		{
			return Map.GetComponent<RM_MapComponent_FillCredit>()?.CreditAt(TargetLocA) ?? 0;
		}

		protected override StatDef SpeedStat => StatDefOf.MiningSpeed;

		protected override void DoEffect(IntVec3 c)
		{
			RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
			if (excavation == null)
			{
				// Defensive only: MapComponents are auto-discovered by
				// reflection, so this branch means something is badly wrong. Do
				// NOTHING rather than writing terrain behind the grid's back —
				// a depth grid that disagrees with the map is worse than a job
				// that quietly accomplished nothing.
				return;
			}
			RM_MapComponent_FillCredit credit = Map.GetComponent<RM_MapComponent_FillCredit>();
			bool costs = RimMandrakeFlowWorksSettings.fillCostsSpoilEnabled && credit != null;
			if (costs && RM_GroundClassMath.CreditShort(credit.CreditAt(c)) > 0)
			{
				// paid for when the work began, not now (a setting changed mid-job): fill nothing rather than for free
				return;
			}
			int before = excavation.ExcavatedDepthAt(c);
			excavation.FillIn(c);
			if (costs)
			{
				// spent only when the depth actually moved: a fill that changed nothing keeps what was tipped in
				credit.SetCredit(c, RM_GroundClassMath.CreditAfterFill(credit.CreditAt(c), excavation.ExcavatedDepthAt(c) != before));
			}
		}
	}
}
