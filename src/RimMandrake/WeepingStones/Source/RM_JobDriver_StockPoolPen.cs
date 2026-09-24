using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3. Carries a breeding-stock item to a pen
	/// cell and releases it as a live pawn of its species -- the STOCK
	/// verb's second half. Same carry-to-cell-then-swap shape as
	/// <c>JobDriver_FillBottle</c> (empty container -> filled container);
	/// here the "swap" is item -> live pawn.
	/// </summary>
	public class RM_JobDriver_StockPoolPen : JobDriver
	{
		private const int ReleaseTicks = 150;

		private Thing Stock => job.targetA.Thing;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(Stock, job, 1, 1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);

			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return Toils_Haul.StartCarryThing(TargetIndex.A);
			yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.Touch);

			Toil release = Toils_General.Wait(ReleaseTicks).WithProgressBarToilDelay(TargetIndex.B);
			release.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
			yield return release;

			Toil finish = ToilMaker.MakeToil("MakeNewToils");
			finish.initAction = delegate
			{
				Thing carried = pawn.carryTracker.CarriedThing;
				if (carried == null)
				{
					return;
				}
				IntVec3 cell = job.targetB.Cell;
				// Re-check the pen still exists -- it can be undesignated
				// mid-carry, same staleness discipline as JobDriver_FillBottle
				// re-reading the liquid body instead of trusting the scan.
				if (!(Map.zoneManager.ZoneAt(cell) is RM_Zone_PoolPen))
				{
					return; // leave the carried stock alone; a later job can retry elsewhere
				}
				if (!RM_PoolBreederUtility.TryGetPawnKindDefName(carried.def, out string kindDefName))
				{
					return;
				}
				PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindDefName);
				if (kind == null)
				{
					return;
				}
				carried.Destroy();
				PawnGenerationRequest req = new PawnGenerationRequest(
					kind, faction: null, context: PawnGenerationContext.NonPlayer,
					forceGenerateNewPawn: true, allowDowned: false, allowDead: false,
					canGeneratePawnRelations: false, colonistRelationChanceFactor: 0f);
				Pawn released = PawnGenerator.GeneratePawn(req);
				GenSpawn.Spawn(released, cell, Map);
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
