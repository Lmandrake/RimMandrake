using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Executes RM_JobGiver_GnawTargets' job: walk to the
	/// target (a building Thing, or a bare floor cell) and periodically bite it
	/// — damaging/destroying a building, or stripping a floor terrain back to
	/// its substructure (TerrainGrid.RemoveTopLayer, RimSage-verified: leaves
	/// the foundation intact) — feeding the pawn per bite. Bite damage scales
	/// with RM_MapComponent_VerminPopulation's pressure, same curve the
	/// JobGiver used to decide whether to seek at all.
	/// </summary>
	public class RM_JobDriver_Gnaw : JobDriver
	{
		private int ticksToNextBite;

		private bool HasThingTarget => job.targetA.HasThing;

		private RM_GnawTargetExtension Ext => pawn.def?.GetModExtension<RM_GnawTargetExtension>();

		public override bool TryMakePreToilReservations(bool errorOnFailed)
		{
			if (HasThingTarget)
			{
				return pawn.Reserve(job.targetA.Thing, job, 1, -1, null, errorOnFailed);
			}
			return pawn.Reserve(job.targetA.Cell, job, 1, -1, null, errorOnFailed);
		}

		protected override IEnumerable<Toil> MakeNewToils()
		{
			RM_GnawTargetExtension ext = Ext;
			if (ext == null)
			{
				yield break;
			}

			if (HasThingTarget)
			{
				this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
				yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
			}
			else
			{
				yield return Toils_Goto.GotoCell(TargetIndex.A, PathEndMode.Touch);
			}

			Toil gnaw = ToilMaker.MakeToil("MakeNewToils");
			gnaw.tickIntervalAction = delegate(int delta)
			{
				ticksToNextBite -= delta;
				if (ticksToNextBite > 0)
				{
					return;
				}
				ticksToNextBite = Mathf.Max(30, ext.ticksBetweenBites);

				float pressure = pawn.Map?.GetComponent<RM_MapComponent_VerminPopulation>()?.GetPressure(pawn) ?? 0f;
				float damage = Mathf.Lerp(ext.biteDamage, ext.biteDamage * ext.meannessDamageMultiplier, pressure);
				Feed(ext);

				if (HasThingTarget)
				{
					Thing target = job.targetA.Thing;
					if (target == null || target.Destroyed)
					{
						ReadyForNextToil();
						return;
					}
					target.TakeDamage(new DamageInfo(DamageDefOf.Bite, damage, 0f, -1f, pawn));
					if (target.Destroyed)
					{
						ReadyForNextToil();
					}
				}
				else
				{
					IntVec3 cell = job.targetA.Cell;
					if (pawn.Map.terrainGrid.CanRemoveTopLayerAt(cell))
					{
						pawn.Map.terrainGrid.RemoveTopLayer(cell, doLeavings: false);
					}
					ReadyForNextToil();
				}
			};
			gnaw.defaultCompleteMode = ToilCompleteMode.Never;
			if (HasThingTarget)
			{
				gnaw.WithProgressBar(TargetIndex.A, () =>
				{
					Thing target = job.targetA.Thing;
					if (target == null || target.MaxHitPoints <= 0)
					{
						return 1f;
					}
					return 1f - (float)target.HitPoints / target.MaxHitPoints;
				});
				gnaw.FailOnCannotTouch(TargetIndex.A, PathEndMode.Touch);
			}
			yield return gnaw;
		}

		private void Feed(RM_GnawTargetExtension ext)
		{
			Need_Food food = pawn.needs?.food;
			if (food != null)
			{
				food.CurLevel = Mathf.Min(food.MaxLevel, food.CurLevel + ext.nutritionPerBite);
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref ticksToNextBite, "ticksToNextBite", 0);
		}
	}
}
