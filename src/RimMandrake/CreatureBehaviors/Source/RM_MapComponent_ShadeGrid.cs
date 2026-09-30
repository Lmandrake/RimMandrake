using System.Collections.Generic;
using RimWorld;
using Unity.Collections;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_GRID_KEYSTONE_1. design/Jawa/worldbuilding/desert_ecology_feasibility.md
	/// §2: neither GlowGrid nor outdoor temperature vary per cell — both are one
	/// map-wide scalar. Nothing casts a shadow and no engine grid can be queried
	/// for "shade" — "shade must be a thing we compute and store ourselves."
	/// This is that grid, the keystone every shade consumer reads (shade-seeking
	/// wander, heat-burst retreat, dung seeding, stagger, false shade, sun heat).
	///
	/// ShadeAt(IntVec3) returns 0f (full sun) .. 1f (full shade): 1f under any
	/// roof, otherwise the CAST shade at that cell. It is built from two layers,
	/// both readable on their own:
	///   RoofShadeAt  — 1 under any roof (constructed or overhead mountain).
	///   CastShadeAt  — shade thrown by vertical casters (buildings, rock,
	///                  big plants).
	///
	/// SOLAR_HEAT_EXPOSURE_1 §3 (design longshade_shade_ideation_2026-09-29.md
	/// §1.3): cast shade is DIRECTIONAL whenever the map has a sun direction —
	/// every caster throws a strip along the sun vector, length = caster height
	/// × cells-per-height, so "a shadow four times its own height", all
	/// parallel. The direction comes from, in order:
	///   1. RM_MapComponent_PinnedSun, when active (the SAME vector every
	///      rendered shadow uses, so the shade the player sees and the shade
	///      animals use are the same cells);
	///   2. the biome's RM_SunHeatExtension substellar geometry (a sun-heat
	///      biome without a pinned sky — mechanically directional, rendered
	///      shadows still swing with the real sun);
	///   3. otherwise the original isotropic radius-2 ring, unchanged, for
	///      every other biome that already reads this grid.
	///
	/// On a sun-heat biome (RM_SunHeatExtension) Recompute also builds the
	/// per-cell exposure (RM_SunHeatMath.Exposure by heat kind) and the sun
	/// path-cost grid handed to vanilla path requests (RM_SunHeatPatches).
	/// Recompute is a full-map scan on a coarse interval, not dirty-event
	/// driven: a few seconds of staleness after a build/dig for zero
	/// event-wiring risk. The public ShadeAt contract is unchanged.
	/// </summary>
	public class RM_MapComponent_ShadeGrid : MapComponent
	{
		private const int RecomputeIntervalTicks = 2000;

		private const int ShadeSearchRadius = 2;

		private const float ShadeCastingFillPercentThreshold = 0.8f;

		private const float ShadeCastingPlantVisualSize = 1.5f;

		/// <summary>A big plant's shadow height, per unit of its maximum
		/// visual size (a 2.0 tree stands about as tall as a 1.0 rock).</summary>
		private const float PlantHeightPerVisualSize = 0.5f;

		/// <summary>No single shadow runs further than this, however low the
		/// sun: at 2° elevation cot is ~29 and one pebble would shade a
		/// quarter of the map.</summary>
		private const float MaxCastCells = 16f;

		/// <summary>Shade at the far tip of a directional shadow.</summary>
		private const float ShadowTipShade = 0.6f;

		private float[] roofShade;
		private bool[] thickRoof;
		private float[] castShade;
		private float[] exposure;

		private bool directional;
		private Vector2 sunShadowDir;
		private float sunLengthPerHeight;

		private RM_SunPathCustomizer pathCustomizer;
		private readonly List<RM_SunPathCustomizer> retiredCustomizers = new List<RM_SunPathCustomizer>();

		public RM_MapComponent_ShadeGrid(Map map)
			: base(map)
		{
		}

		public static RM_MapComponent_ShadeGrid For(Map map)
		{
			return map?.GetComponent<RM_MapComponent_ShadeGrid>();
		}

		/// <summary>This map's sun-heat extension, or null. Every map-wide
		/// sun-heat effect is gated on it.</summary>
		public RM_SunHeatExtension HeatExtension => map?.Biome?.GetModExtension<RM_SunHeatExtension>();

		/// <summary>True when sun heat runs on this map: the biome carries
		/// RM_SunHeatExtension, the grid and sun heat are both on in settings.</summary>
		public bool SunHeatActive => RM_CreatureBehaviorsSettings.shadeGridEnabled
		                             && RM_CreatureBehaviorsSettings.sunHeatEnabled
		                             && HeatExtension != null;

		/// <summary>True when the last recompute cast shadows along a sun
		/// vector rather than the legacy ring.</summary>
		public bool IsDirectional => directional;

		public Vector2 SunShadowDirection => sunShadowDir;

		public override void FinalizeInit()
		{
			base.FinalizeInit();
			RM_SunHeatPatches.Register(map, this);
			Recompute();
		}

		public override void MapRemoved()
		{
			base.MapRemoved();
			RM_SunHeatPatches.Unregister(map);
			pathCustomizer?.Dispose();
			pathCustomizer = null;
			for (int i = 0; i < retiredCustomizers.Count; i++)
			{
				retiredCustomizers[i].Dispose();
			}
			retiredCustomizers.Clear();
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
		/// anywhere", which degrades any consumer to plain vanilla behaviour.
		/// </summary>
		public float ShadeAt(IntVec3 cell)
		{
			if (!Ready(cell))
			{
				return 0f;
			}
			int i = map.cellIndices.CellToIndex(cell);
			return Mathf.Max(roofShade[i], castShade[i]);
		}

		/// <summary>1 under any roof, else 0.</summary>
		public float RoofShadeAt(IntVec3 cell)
		{
			return Ready(cell) ? roofShade[map.cellIndices.CellToIndex(cell)] : 0f;
		}

		/// <summary>Shade thrown by vertical casters only, 0..1.</summary>
		public float CastShadeAt(IntVec3 cell)
		{
			return Ready(cell) ? castShade[map.cellIndices.CellToIndex(cell)] : 0f;
		}

		/// <summary>SOLAR_HEAT_EXPOSURE_1: 0 (sheltered) .. 1 (full sun) for a
		/// pawn standing here, by this biome's heat kind. 0 on any map that is
		/// not a sun-heat biome. The enclosed-room test is live (vanilla room
		/// temperature); the shade part is from the last recompute.</summary>
		public float ExposureAt(IntVec3 cell)
		{
			if (exposure == null || !SunHeatActive || !cell.InBounds(map))
			{
				return 0f;
			}
			if (!cell.UsesOutdoorTemperature(map))
			{
				return 0f;
			}
			return exposure[map.cellIndices.CellToIndex(cell)];
		}

		/// <summary>The shared per-map path-cost customizer, or null when sun
		/// pathing does not apply (not a sun-heat biome, ambient heat, the
		/// setting off, or the grid not built yet).</summary>
		public RM_SunPathCustomizer PathCustomizer
		{
			get
			{
				if (!SunHeatActive || !RM_CreatureBehaviorsSettings.sunPathingEnabled)
				{
					return null;
				}
				return pathCustomizer;
			}
		}

		private bool Ready(IntVec3 cell)
		{
			return RM_CreatureBehaviorsSettings.shadeGridEnabled && roofShade != null && cell.InBounds(map);
		}

		public void Recompute()
		{
			int n = map.cellIndices.NumGridCells;
			if (roofShade == null || roofShade.Length != n)
			{
				roofShade = new float[n];
				thickRoof = new bool[n];
				castShade = new float[n];
			}
			System.Array.Clear(castShade, 0, n);
			ResolveSun();
			int width = map.Size.x;
			int height = map.Size.z;
			foreach (IntVec3 cell in map.AllCells)
			{
				int i = map.cellIndices.CellToIndex(cell);
				RoofDef roof = map.roofGrid.RoofAt(cell);
				roofShade[i] = roof != null ? 1f : 0f;
				thickRoof[i] = roof != null && roof.isThickRoof;
				if (directional)
				{
					float h = CasterHeight(cell);
					if (h > 0f)
					{
						float len = RM_SunHeatMath.ShadowLength(h, sunLengthPerHeight, MaxCastCells);
						RM_SunHeatMath.CastInto(castShade, width, height, cell.x, cell.z,
							sunShadowDir.x, sunShadowDir.y, len, ShadowTipShade);
					}
				}
				else if (roof == null)
				{
					castShade[i] = RingShadeAt(cell);
				}
			}
			RebuildHeatLayers();
		}

		/// <summary>Picks the sun vector for this recompute: pinned sun, else
		/// the heat extension's own geometry, else none (legacy ring).</summary>
		private void ResolveSun()
		{
			directional = false;
			RM_MapComponent_PinnedSun pin = RM_MapComponent_PinnedSun.For(map);
			if (RM_CreatureBehaviorsSettings.directionalShadeEnabled && pin != null && pin.IsActive)
			{
				sunShadowDir = pin.ShadowDirection;
				sunLengthPerHeight = pin.ShadowLengthPerHeight;
				directional = true;
				return;
			}
			RM_SunHeatExtension ext = HeatExtension;
			if (!RM_CreatureBehaviorsSettings.directionalShadeEnabled || ext == null
				|| Find.WorldGrid == null || !map.Tile.Valid)
			{
				return;
			}
			Vector2 longLat = Find.WorldGrid.LongLatOf(map.Tile);
			RM_MapComponent_PinnedSun.SunGeometry(longLat.y, longLat.x, ext.substellarLatitude, ext.substellarLongitude,
				out float bearingDeg, out float arcDeg);
			float elev = Mathf.Clamp(90f - arcDeg, ext.minElevationDegrees, ext.maxElevationDegrees);
			float b = bearingDeg * Mathf.Deg2Rad;
			sunShadowDir = new Vector2(-Mathf.Sin(b), -Mathf.Cos(b));
			float e = Mathf.Max(0.5f, elev) * Mathf.Deg2Rad;
			sunLengthPerHeight = Mathf.Cos(e) / Mathf.Sin(e);
			directional = true;
		}

		private void RebuildHeatLayers()
		{
			RM_SunHeatExtension ext = HeatExtension;
			if (ext == null || !RM_CreatureBehaviorsSettings.sunHeatEnabled)
			{
				exposure = null;
				RetireCustomizer();
				return;
			}
			int n = castShade.Length;
			if (exposure == null || exposure.Length != n)
			{
				exposure = new float[n];
			}
			bool wantPath = ext.heatKind != RM_HeatKind.ambient && ext.sunPathCostPerCell > 0f
			                && RM_CreatureBehaviorsSettings.sunPathingEnabled;
			NativeArray<ushort> cost = default;
			if (wantPath)
			{
				cost = new NativeArray<ushort>(n, Allocator.Persistent);
			}
			float pathStrength = RM_CreatureBehaviorsSettings.sunPathCostMultiplier;
			for (int i = 0; i < n; i++)
			{
				// outdoors=true here: the enclosed-room test is live in ExposureAt.
				float ex = RM_SunHeatMath.Exposure(ext.heatKind, true, roofShade[i], thickRoof[i], castShade[i]);
				exposure[i] = ex;
				if (wantPath)
				{
					cost[i] = RM_SunHeatMath.PathCost(ex, ext.sunPathCostPerCell, pathStrength);
				}
			}
			RetireCustomizer();
			if (wantPath)
			{
				// A NEW customizer object each rebuild, never the old array
				// rewritten in place: path grid jobs read the array on worker
				// threads, and PathFinder keys its cached cost grids on the
				// customizer's identity, so a fresh object is what makes the
				// new costs take effect at all.
				pathCustomizer = new RM_SunPathCustomizer(cost);
			}
		}

		/// <summary>Old customizers are disposed one rebuild later, never at
		/// once: a queued path request may still hold one, and its grid job
		/// reads the array off the main thread.</summary>
		private void RetireCustomizer()
		{
			for (int i = 0; i < retiredCustomizers.Count; i++)
			{
				retiredCustomizers[i].Dispose();
			}
			retiredCustomizers.Clear();
			if (pathCustomizer != null)
			{
				retiredCustomizers.Add(pathCustomizer);
				pathCustomizer = null;
			}
		}

		/// <summary>Shadow height of whatever stands in this cell, 0 if none
		/// (staticSunShadowHeight scale — a rock or wall is 1.0).</summary>
		private float CasterHeight(IntVec3 cell)
		{
			float best = 0f;
			List<Thing> thingList = cell.GetThingList(map);
			for (int i = 0; i < thingList.Count; i++)
			{
				Thing thing = thingList[i];
				if (thing is Building)
				{
					float h = thing.def.staticSunShadowHeight;
					if (thing.def.fillPercent >= ShadeCastingFillPercentThreshold)
					{
						h = Mathf.Max(h, thing.def.fillPercent);
					}
					best = Mathf.Max(best, h);
				}
				else if (thing is Plant plant && plant.def.plant != null
					&& plant.def.plant.visualSizeRange.max >= ShadeCastingPlantVisualSize)
				{
					best = Mathf.Max(best, plant.def.plant.visualSizeRange.max * PlantHeightPerVisualSize);
				}
			}
			return best;
		}

		private float RingShadeAt(IntVec3 cell)
		{
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

	/// <summary>
	/// SOLAR_HEAT_EXPOSURE_1 §4. The per-map sun path-cost grid, in the shape
	/// vanilla's path finder already accepts: PathRequest.IPathGridCustomizer
	/// (decompiled 1.6: PathFinderMapData.ParameterizeGridJob hands
	/// GetOffsetGrid() to the grid job, and PathGridJob adds custom[index] to
	/// each cell's cost; ≥ 10000 would make it impassable, which sun cost never
	/// reaches). Same shape as vanilla's UsedRectPathGridCustomizer.
	/// </summary>
	public class RM_SunPathCustomizer : PathRequest.IPathGridCustomizer, System.IDisposable
	{
		private NativeArray<ushort> grid;

		public RM_SunPathCustomizer(NativeArray<ushort> grid)
		{
			this.grid = grid;
		}

		public NativeArray<ushort> GetOffsetGrid()
		{
			return grid;
		}

		public void Dispose()
		{
			if (grid.IsCreated)
			{
				grid.Dispose();
			}
		}
	}
}
