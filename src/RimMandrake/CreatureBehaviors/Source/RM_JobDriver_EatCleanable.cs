using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// RUST_CATHEDRAL_MECHANICS_1 §6. Executes RM_ThinkNode_EatCleanable's
	/// job: walk to the target and consume it over RM_EatCleanableExtension's
	/// eatDurationTicks, then destroy it (DestroyMode.Vanish — no corpse or
	/// leavings, matching "cleaning" rather than butchering) and top up the
	/// pawn's food need. Works identically whether the target is a named item
	/// (e.g. a wastepack) or Filth.
	/// </summary>
	public class RM_JobDriver_EatCleanable : JobDriver
	{
		private RM_EatCleanableExtension Ext => pawn.def?.GetModExtension<RM_EatCleanableExtension>();

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			RM_EatCleanableExtension ext = Ext;
			if (ext == null)
			{
				yield break;
			}

			this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
			yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);

			Toil eat = Toils_General.Wait(Mathf.Max(30, ext.eatDurationTicks));
			eat.WithProgressBarToilDelay(TargetIndex.A);
			eat.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			eat.AddFinishAction(delegate
			{
				Feed(ext);
				Thing target = job.targetA.Thing;
				if (target != null && !target.Destroyed)
				{
					target.Destroy(DestroyMode.Vanish);
				}
			});
			yield return eat;
		}

		private void Feed(RM_EatCleanableExtension ext)
		{
			Need_Food food = pawn.needs?.food;
			if (food != null)
			{
				food.CurLevel = Mathf.Min(food.MaxLevel, food.CurLevel + ext.nutritionPerMeal);
			}
		}
	}
}
