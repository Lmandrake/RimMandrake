using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 3. Carries one unit of feed to a pen's
	/// waterline and delivers it -- the FEED verb (spec §3: "to the water's
	/// edge"). Feeding from the bank is explicitly the SAFE half of the
	/// husbandry loop (§3's own text: "Feeding from the bank is safe;
	/// feeding late is not"), so unlike <see cref="RM_JobDriver_NetPoolBreeder"/>
	/// this carries no handler-injury chance -- the risk lives in being
	/// LATE, which <see cref="RM_MapComponent_PoolStock"/>'s unfed-days
	/// tracking already prices in.
	/// </summary>
	public class RM_JobDriver_FeedPoolPen : JobDriver
	{
		private const int FeedTicks = 120;

		private Thing Food => job.targetA.Thing;

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(Food, job, 1, 1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);

			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.ClosestTouch);
			yield return Toils_Haul.StartCarryThing(TargetIndex.A);
			yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.Touch);

			Toil feed = Toils_General.Wait(FeedTicks).WithProgressBarToilDelay(TargetIndex.B);
			feed.FailOnCannotTouch(TargetIndex.B, PathEndMode.Touch);
			yield return feed;

			Toil finish = ToilMaker.MakeToil("MakeNewToils");
			finish.initAction = delegate
			{
				Thing carried = pawn.carryTracker.CarriedThing;
				IntVec3 cell = job.targetB.Cell;
				RM_MapComponent_PoolStock comp = Map.GetComponent<RM_MapComponent_PoolStock>();
				if (comp != null && Map.zoneManager.ZoneAt(cell) is RM_Zone_PoolPen pen)
				{
					RM_PoolBody body = comp.BodyFor(pen);
					if (body != null)
					{
						comp.Notify_Fed(body, Find.TickManager.TicksGame);
					}
				}
				// Consumed as feed either way -- even delivered to a pen that
				// was undesignated mid-carry, this is scrap thrown at water,
				// not returned to the stockpile.
				carried?.Destroy();
			};
			finish.defaultCompleteMode = ToilCompleteMode.Instant;
			yield return finish;
		}
	}
}
