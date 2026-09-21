using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_WHALE_FILTERFEED_1. Executes RM_JobGiver_FilterFeedTerrain's
	/// job: walk onto the target cell, strain it for boutDurationTicks, then top
	/// up Need_Food directly and (optionally) leave churned ground behind.
	///
	/// 🔑 The feeding step is a plain write to Need_Food.CurLevel, which is the
	/// whole mechanism of this item. FoodTypeFlags gates WHICH Thing a pawn is
	/// willing to ingest; it has no say over a need being satisfied by
	/// something that is not a Thing. The race's declared foodType is therefore
	/// untouched and still governs every ordinary meal — this adds a second,
	/// terrain-keyed route rather than replacing the first. Precedent in this
	/// same assembly: RM_JobDriver_EatCleanable.Feed does the identical thing
	/// for filth and named items.
	///
	/// No reservation is taken. The target is a cell, wild animals do not
	/// reserve, and two filter-feeders straining the same patch of sand is a
	/// correct outcome rather than a conflict.
	/// </summary>
	public class RM_JobDriver_FilterFeedTerrain : JobDriver
	{
		private RM_FilterFeedExtension Ext => pawn.def?.GetModExtension<RM_FilterFeedExtension>();

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return true;
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			RM_FilterFeedExtension ext = Ext;
			if (ext == null)
			{
				yield break;
			}

			// The ground can be built over, mined out or flooded mid-bout; if it
			// stops being feeding ground the job ends rather than paying out.
			this.FailOn(() => !RM_CreatureBehaviorsSettings.filterFeedingEnabled);
			this.FailOn(() => pawn.Map == null
				|| !RM_JobGiver_FilterFeedTerrain.MatchesFeedTerrain(job.targetA.Cell, pawn.Map, ext));

			yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.OnCell);

			Toil strain = Toils_General.Wait(Mathf.Max(30, ext.boutDurationTicks));
			strain.WithProgressBarToilDelay(TargetIndex.A);
			strain.AddFinishAction(delegate
			{
				Feed(ext);
				LeaveChurnedGround(ext);
			});
			yield return strain;
		}

		/// <summary>
		/// Restores a fraction of the pawn's FULL food need. A fraction, not an
		/// absolute nutrition value, because Need_Food.MaxLevel scales with body
		/// size and this kit has to read the same on a bodySize-16 megafauna as
		/// on anything smaller that adopts the extension later.
		/// </summary>
		private void Feed(RM_FilterFeedExtension ext)
		{
			Need_Food food = pawn.needs?.food;
			if (food == null)
			{
				return;
			}
			float gain = food.MaxLevel * Mathf.Max(0f, ext.foodPercentPerBout)
				* Mathf.Max(0f, RM_CreatureBehaviorsSettings.filterFeedNutritionMultiplier);
			food.CurLevel = Mathf.Min(food.MaxLevel, food.CurLevel + gain);
		}

		private void LeaveChurnedGround(RM_FilterFeedExtension ext)
		{
			if (ext.leavingsFilthDef == null || ext.leavingsFilthCount <= 0)
			{
				return;
			}
			Map map = pawn.Map;
			if (map == null || !job.targetA.Cell.InBounds(map))
			{
				return;
			}
			FilthMaker.TryMakeFilth(job.targetA.Cell, map, ext.leavingsFilthDef, ext.leavingsFilthCount);
		}
	}
}
