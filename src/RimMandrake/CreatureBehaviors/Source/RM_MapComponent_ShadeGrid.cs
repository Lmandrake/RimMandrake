using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_GRID_KEYSTONE_1. design/Jawa/worldbuilding/desert_ecology_feasibility.md
	/// §2: neither GlowGrid nor outdoor temperature vary per cell — both are one
	/// map-wide scalar (Verse.GlowGrid.GroundGlowAt reads SkyManager.CurSkyGlow;
	/// outdoor temperature resolves to one Room reading MapTemperature.OutdoorTemp).
	/// Nothing casts a shadow and no engine grid can be queried for "shade" —
	/// §2's own words: "shade must be a thing we compute and store ourselves."
	/// This is that grid. §10 calls it the keystone: shade-seeking wander (this
	/// assembly's RM_JobGiver_WanderInShadeGrid), a burst-predator's heat-driven
	/// retreat (RM_HediffComp_ShadeDrivenSeverity) and any future heat-budget
	/// hediff for herbivores/megafauna are all meant to read ShadeAt instead of
	/// re-deriving their own version of this scan.
	///
	/// ShadeAt(IntVec3) returns 0f (full sun) .. 1f (full shade): 1f for any
	/// roofed cell (constructed roof or overhead mountain — RoofGrid.Roofed does
	/// not distinguish them, and neither does this), otherwise a falloff score
	/// against the nearest adjacent "shade-casting" thing (a building at or above
	/// ShadeCastingFillPercentThreshold, or a plant at or above
	/// ShadeCastingPlantVisualSize) within ShadeSearchRadius cells.
	///
	/// Recompute is a full-map scan on a coarse tick interval, not dirty-event
	/// driven off roof/plant/building change — §10 names dirty-event handling as
	/// "the fiddly part" of this component and a first landing does not need it:
	/// RecomputeIntervalTicks trades a few seconds of staleness after a build/dig
	/// for zero event-wiring risk. A future pass can move to incremental
	/// recompute without changing the public ShadeAt(IntVec3) contract any
	/// consumer already depends on.
	/// </summary>
	public class RM_MapComponent_ShadeGrid : MapComponent
	{
		private const int RecomputeIntervalTicks = 2000;

		private const int ShadeSearchRadius = 2;

		private const float ShadeCastingFillPercentThreshold = 0.8f;

		private const float ShadeCastingPlantVisualSize = 1.5f;

		private float[] shade;

		public RM_MapComponent_ShadeGrid(Map map)
			: base(map)
		{
		}

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			Recompute();
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (!RM_CreatureBehaviorsSettings.shadeGridEnabled)
			{
				return; // mod option: shade grid disabled — ShadeAt reports full sun everywhere
			}
			if (Find.TickManager.TicksGame % RecomputeIntervalTicks == 0)
			{
				Recompute();
			}
		}

		/// <summary>
		/// 0f (full sun) .. 1f (full shade) at the given cell. Returns 0f for an
		/// out-of-bounds cell, before the first recompute has run, or while the
		/// mod option disables the mechanic — every case reads as "no shade
		/// anywhere" rather than a stale or garbage value, which degrades any
		/// consumer to plain vanilla behaviour rather than a wrong one.
		/// </summary>
		public float ShadeAt(IntVec3 cell)
		{
			if (!RM_CreatureBehaviorsSettings.shadeGridEnabled || shade == null || !cell.InBounds(map))
			{
				return 0f;
			}
			return shade[map.cellIndices.CellToIndex(cell)];
		}

		public void Recompute()
		{
			int numGridCells = map.cellIndices.NumGridCells;
			if (shade == null || shade.Length != numGridCells)
			{
				shade = new float[numGridCells];
			}
			foreach (IntVec3 cell in map.AllCells)
			{
				shade[map.cellIndices.CellToIndex(cell)] = ComputeShadeAt(cell);
			}
		}

		private float ComputeShadeAt(IntVec3 cell)
		{
			if (map.roofGrid.Roofed(cell))
			{
				return 1f;
			}
			float best = 0f;
			for (int dz = -ShadeSearchRadius; dz <= ShadeSearchRadius; dz++)
			{
				for (int dx = -ShadeSearchRadius; dx <= ShadeSearchRadius; dx++)
				{
					if (dx == 0 && dz == 0)
					{
						continue;
					}
					IntVec3 neighbor = new IntVec3(cell.x + dx, cell.y, cell.z + dz);
					if (!neighbor.InBounds(map) || !CastsShade(neighbor))
					{
						continue;
					}
					float dist = Mathf.Sqrt(dx * dx + dz * dz);
					float score = Mathf.Clamp01(1f - dist / (ShadeSearchRadius + 1));
					if (score > best)
					{
						best = score;
					}
				}
			}
			return best;
		}

		private bool CastsShade(IntVec3 cell)
		{
			List<Thing> thingList = cell.GetThingList(map);
			for (int i = 0; i < thingList.Count; i++)
			{
				Thing thing = thingList[i];
				if (thing is Building && thing.def.fillPercent >= ShadeCastingFillPercentThreshold)
				{
					return true;
				}
				if (thing is Plant plant && plant.def.plant != null
					&& plant.def.plant.visualSizeRange.max >= ShadeCastingPlantVisualSize)
				{
					return true;
				}
			}
			return false;
		}
	}
}
