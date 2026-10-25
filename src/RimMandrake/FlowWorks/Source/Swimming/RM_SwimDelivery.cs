using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Swimming
{
	/// <summary>SUSPENSION_TOWER_DIAGNOSE_UNSUPPLIED_IN_POOL (run8: a tower blueprint in the middle of a brim-full superdeep cut
	/// stayed Steel 0/300 for 10k ticks with steel on the bank and idle builders, while the same colonists swam out to fill
	/// work). Vanilla's delivery job picks up as much as the hauler can carry (75 steel, 37.5 kg on a person's 35 kg
	/// capacity); the swim profile counts carried mass (RM_SwimMath.Load), so the loaded hauler sank (class None): its path
	/// grid closed the water and the non-swimmer reach veto refused the blueprint. Empty-handed fill work never hit it.
	/// Here: when a needer this job delivers to can be touched only from deep swim water (no dry standable square beside it),
	/// the job carries no more than the hauler can swim with (RM_SwimMath.MaxSwimCarryKg at SwimCarryEnduranceFloor), so it
	/// makes more, lighter trips; if not even one unit can be swum out, there is no job. A needer touching the bank is left
	/// to vanilla. Frames go through the same vanilla method, so a half-supplied frame is covered too.</summary>
	[HarmonyPatch(typeof(WorkGiver_ConstructDeliverResources), "ResourceDeliverJobFor")]
	[RimMandrake.Shared.PatchFeature("Swimming in deep water", typeof(RM_SwimSettings), "deepSwimEnabled")]
	public static class RM_Patch_DeliverResources_SwimLoad
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, ref Job __result)
		{
			if (__result == null || __result.def != JobDefOf.HaulToContainer || !RM_SwimWater.On || pawn?.Map == null
				|| !(__result.targetA.Thing is Thing res) || !NeedsSwimDelivery(pawn.Map, __result))
			{
				return;
			}
			int count = CappedCount(pawn, res, __result.count);
			// vanilla may reuse a stack already in hand (CanUseCarriedResource): the driver then skips the pickup and swims
			// the whole stack whatever job.count says, so a held stack heavier than the swim-safe count gets no job; the
			// hauler drops it when the current job ends and picks up a capped one on its next scan.
			bool held = res == pawn.carryTracker?.CarriedThing;
			bool heldTooHeavy = held && CappedCount(pawn, res, res.stackCount) < res.stackCount;
			if (count <= 0 || heldTooHeavy)
			{
				__result = null;   // nothing swimmable: no job, not a sinking trip
				return;
			}
			__result.count = count;
			if (held)
			{
				// the skipped pickup leaves job.count unspent, so queued stacks (targetQueueA) could be collected on top of
				// the held one: deliver the swim-safe held stack alone
				__result.targetQueueA = null;
			}
		}

		/// <summary>Does any needer of this delivery (its target, the constructible, the queued needers) need a swim to touch?</summary>
		public static bool NeedsSwimDelivery(Map map, Job job)
		{
			if (SwimOnly(map, job.targetB.Thing) || SwimOnly(map, job.targetC.Thing))
			{
				return true;
			}
			if (job.targetQueueB != null)
			{
				for (int i = 0; i < job.targetQueueB.Count; i++)
				{
					if (SwimOnly(map, job.targetQueueB[i].Thing))
					{
						return true;
					}
				}
			}
			return false;
		}

		/// <summary>A spawned thing with no dry standable square beside it, and deep swim water beside it (the same footing rule
		/// as RM_Patch_Reachability_NonSwimmer).</summary>
		public static bool SwimOnly(Map map, Thing t)
		{
			if (t == null || !t.Spawned || t.Map != map)
			{
				return false;
			}
			bool swim = false;
			foreach (IntVec3 n in GenAdj.CellsAdjacent8Way(t))
			{
				if (!n.InBounds(map))
				{
					continue;
				}
				if (RM_SwimWater.IsDeepSwimCell(map, n))
				{
					swim = true;
				}
				else if (n.Standable(map))
				{
					return false;
				}
			}
			return swim;
		}

		/// <summary>The hauler's swim-safe count of <paramref name="res"/> (RM_SwimMath.SwimCarryCount).</summary>
		public static int CappedCount(Pawn pawn, Thing res, int wanted)
		{
			RM_SwimProfile pr = RM_Swim.ProfileOf(pawn);
			float moving = pawn.health?.capacities != null ? pawn.health.capacities.GetLevel(PawnCapacityDefOf.Moving) : 1f;
			float maxKg = RM_SwimMath.MaxSwimCarryKg(pr.natural, moving, pawn.BodySize, MassUtility.GearAndInventoryMass(pawn),
				MassUtility.Capacity(pawn), RM_SwimSettings.swimWeightEndurancePenalty, RM_SwimMath.SwimCarryEnduranceFloor);
			return RM_SwimMath.SwimCarryCount(wanted, res.GetStatValue(StatDefOf.Mass), maxKg);
		}
	}
}
