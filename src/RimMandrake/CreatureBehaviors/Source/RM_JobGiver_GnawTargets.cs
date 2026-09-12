using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Generic "chew a data-listed building/comp or floor
	/// terrain" JobGiver, inserted globally the same way as
	/// RM_JobGiver_SeekMarkedTerrain (see that class's header) — a no-op for
	/// any pawn whose race lacks RM_GnawTargetExtension.
	/// </summary>
	public class RM_JobGiver_GnawTargets : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_CreatureBehaviorsSettings.gnawBehaviorEnabled)
			{
				return null; // mod option: gnawing behavior disabled
			}
			RM_GnawTargetExtension ext = pawn.def?.GetModExtension<RM_GnawTargetExtension>();
			if (ext == null || pawn.Map == null)
			{
				return null;
			}
			float pressure = pawn.Map.GetComponent<RM_MapComponent_VerminPopulation>()?.GetPressure(pawn) ?? 0f;
			float seekChance = Mathf.Lerp(ext.seekChanceAtLowPressure, ext.seekChanceAtHighPressure, pressure);
			if (!Rand.Chance(seekChance))
			{
				return null;
			}

			Thing buildingTarget = FindGnawBuilding(pawn, ext);
			if (buildingTarget != null)
			{
				return JobMaker.MakeJob(RM_JobDefOf.RM_Gnaw, buildingTarget);
			}

			if (TryFindGnawTerrainCell(pawn, ext, out IntVec3 cell))
			{
				return JobMaker.MakeJob(RM_JobDefOf.RM_Gnaw, cell);
			}
			return null;
		}

		private static Thing FindGnawBuilding(Pawn pawn, RM_GnawTargetExtension ext)
		{
			if (ext.gnawBuildingDefNames.NullOrEmpty() && ext.gnawCompTypeNames.NullOrEmpty())
			{
				return null;
			}
			Map map = pawn.Map;
			return GenClosest.ClosestThingReachable(pawn.Position, map, ThingRequest.ForGroup(ThingRequestGroup.BuildingArtificial),
				PathEndMode.Touch, TraverseParms.For(pawn), ext.searchRadius, (Thing t) => Matches(t, ext) && !t.IsForbidden(pawn) && pawn.CanReach(t, PathEndMode.Touch, Danger.Some));
		}

		private static bool Matches(Thing t, RM_GnawTargetExtension ext)
		{
			if (!ext.gnawBuildingDefNames.NullOrEmpty() && ext.gnawBuildingDefNames.Contains(t.def.defName))
			{
				return true;
			}
			if (!ext.gnawCompTypeNames.NullOrEmpty())
			{
				List<ThingComp> comps = (t as ThingWithComps)?.AllComps;
				if (comps != null)
				{
					for (int i = 0; i < comps.Count; i++)
					{
						if (ext.gnawCompTypeNames.Contains(comps[i].GetType().Name))
						{
							return true;
						}
					}
				}
			}
			return false;
		}

		private static bool TryFindGnawTerrainCell(Pawn pawn, RM_GnawTargetExtension ext, out IntVec3 result)
		{
			result = IntVec3.Invalid;
			if (ext.gnawFloorTerrainDefNames.NullOrEmpty())
			{
				return false;
			}
			Map map = pawn.Map;
			return CellFinder.TryFindRandomCellNear(pawn.Position, map, (int)ext.searchRadius,
				(IntVec3 c) => c.InBounds(map) && map.terrainGrid.CanRemoveTopLayerAt(c)
					&& ext.gnawFloorTerrainDefNames.Contains(map.terrainGrid.TerrainAt(c)?.defName)
					&& map.reachability.CanReach(pawn.Position, c, PathEndMode.Touch, TraverseParms.For(pawn)),
				out result);
		}
	}
}
