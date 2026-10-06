using System.Collections.Generic;
using RimWorld;
using Unity.Collections;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SOLAR_MIRRORS_MOD_DESIGN_1 §2.3 (design/RimMandrake/solar_mirrors_mod_design_2026-10-04.md):
	/// a source of light that un-shades cells (Solar Mirrors' beam layer is the
	/// first). Register with RM_MapComponent_ShadeGrid.RegisterLightSource; the
	/// grid owns the buffer and calls AddLight once per Recompute, on the main
	/// thread, before it composes exposure, path costs and the patch graph — so
	/// all of them, and ShadeAt, see the same light under one GridVersion.
	/// A provider whose light changed calls Recompute (throttle it yourself).
	/// For its own input a provider must read only the mirror-free layers
	/// (RoofShadeAt, CastShadeAt), never ShadeAt/ExposureAt, which carry light.
	/// </summary>
	public interface IRM_LightLayer
	{
		/// <summary>ADD (never assign) this source's light, 0..N per cell
		/// (N &gt; 1 = several beams), into `into` (one float per cell index,
		/// zero where nothing lit it yet). Return true if any cell got light.
		/// Must not allocate: it runs inside every grid rebuild.</summary>
		bool AddLight(float[] into);
	}

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
	///
	/// Light sources (IRM_LightLayer, RegisterLightSource) un-shade cells:
	/// folded into ShadeAt and into the cached exposure, so sun path cost
	/// and the patch graph see them too. None registered = no effect.
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

		// STILLSAND_SUN_FROM_LATITUDE_1: the map's sun elevation (NaN when
		// unknown — no pin, no heat extension, no planet tile), and the sand
		// glare floor per cell (null when no glare applies).
		private float sunElevationDeg = float.NaN;
		private float[] glareFloor;

		private RM_SunPathCustomizer pathCustomizer;
		private readonly List<RM_SunPathCustomizer> retiredCustomizers = new List<RM_SunPathCustomizer>();

		// SHADE_GEAR_FAMILY_1 (RM_ShadeGear.cs). gearShade: pitched gear
		// (tent footprints, shield lees), kind-resolved, rebuilt with the rest
		// of the grid. parasolShade: the one cell each parasol's shadow falls
		// on, refreshed every ParasolRefreshTicks because its wearer moves.
		private const int ParasolRefreshTicks = 250;
		private float[] gearShade;
		private float[] parasolShade;
		private readonly List<int> parasolTouched = new List<int>();
		private readonly HashSet<Thing> gearThings = new HashSet<Thing>();
		private bool recomputeRequested;

		// LONGSHADE_GPT_ENRICHMENT_1 §2 (RM_MovingShadeMath.cs): living shade
		// casters (RM_CompProperties_ShadowCaster.castShadeHeight > 0, the
		// gloomcast). Their shade is its own layer, refreshed every
		// MovingShadeRefreshTicks, and only when a caster moved: its OLD
		// rectangle is cleared and its NEW one written — never a full-map pass.
		// Read live by ShadeAt and ExposureAt. NOT folded into the exposure
		// array, so the sun path cost and the shade-patch graph do not see it
		// (both rebuild every 2000 ticks, far slower than the shadow moves):
		// a creature reaches a moving shadow by seeking shade or by following
		// its host, never by a path cached under it.
		// TUNED: 60 ticks — the gloomcast walks ~2 cells a second (MoveSpeed
		// 2.2), so its shadow trails by at most a couple of cells.
		private const int MovingShadeRefreshTicks = 60;
		private float[] movingShade;
		private readonly Dictionary<Thing, MovingCasterState> movingCasters = new Dictionary<Thing, MovingCasterState>();
		private bool movingDirty;

		private class MovingCasterState
		{
			public IntVec3 lastPos = IntVec3.Invalid;
			public bool hasRect;
			public int minX, minZ, maxX, maxZ;
		}

		// SOLAR_HEAT_EXPOSURE_1 §5: the shade-patch graph (RM_ShadePatchGraph),
		// built lazily from the exposure layer. It is built only when a hop,
		// escape or ring asks for it, and only after the grid has recomputed
		// since the last build. On a map with no sun heat it is never built.
		private int gridVersion;
		private int patchGraphVersion = -1;

		// SOLAR_MIRRORS_MOD_DESIGN_1 §2.3: registered light sources and the
		// light they add (rebuilt each Recompute). With no source registered
		// anyLight stays false and nothing below reads lightLayer, so every
		// output is byte-for-byte what it was before the hook existed.
		private readonly List<IRM_LightLayer> lightSources = new List<IRM_LightLayer>();
		private float[] lightLayer;
		private bool anyLight;
		private RM_ShadePatchGraph patchGraph;
		private bool[] patchShadeMask;
		private bool[] patchWalkMask;

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

		/// <summary>Bumped on every Recompute, so a consumer can tell that
		/// what it derived from the grid is stale.</summary>
		public int GridVersion => gridVersion;

		/// <summary>True when shade hopping and the dash ring can run here: a
		/// sun-heat map whose heat kind shade can help against.</summary>
		public bool ShadeHopsApply => SunHeatActive && exposure != null
		                              && EffectiveHeatKind != RM_HeatKind.ambient;

		/// <summary>The map's sun elevation in degrees from the last
		/// recompute, or NaN when there is none.</summary>
		public float SunElevationDegrees => sunElevationDeg;

		/// <summary>STILLSAND_SUN_FROM_LATITUDE_1 §3: the heat kind in force —
		/// the biome's own, or (when it sets overheadAboveElevationDegrees and
		/// the setting is on) overhead/lowSun by this map's sun elevation.
		/// Which cover counts, never a new kind of heat. Overhead on a biome
		/// with no sun heat (ordinary shade).</summary>
		public RM_HeatKind EffectiveHeatKind
		{
			get
			{
				RM_SunHeatExtension ext = HeatExtension;
				if (ext == null)
				{
					return RM_HeatKind.overhead;
				}
				if (!RM_CreatureBehaviorsSettings.kindFromElevationEnabled)
				{
					return ext.heatKind;
				}
				return RM_SunHeatMath.KindFromElevation(ext.heatKind, sunElevationDeg, ext.overheadAboveElevationDegrees);
			}
		}

		/// <summary>STILLSAND_SUN_FROM_LATITUDE_1 §4: °C of sun at full
		/// exposure for a size-1 pawn before the strength dial — heatOffsetC,
		/// or heatOffsetC × sin(elevation) on a biome that scales by angle.</summary>
		public float EffectiveHeatOffsetC
		{
			get
			{
				RM_SunHeatExtension ext = HeatExtension;
				if (ext == null)
				{
					return 0f;
				}
				if (!ext.heatScalesWithElevation)
				{
					return ext.heatOffsetC;
				}
				return RM_SunHeatMath.ElevationHeatOffset(ext.heatOffsetC, sunElevationDeg, ext.minScaledHeatOffsetC);
			}
		}

		/// <summary>STILLSAND_SUN_FROM_LATITUDE_1 §5: the sand glare floor at
		/// this cell (0 where none).</summary>
		public float GlareFloorAt(IntVec3 cell)
		{
			if (glareFloor == null || !cell.InBounds(map))
			{
				return 0f;
			}
			return glareFloor[map.cellIndices.CellToIndex(cell)];
		}

		/// <summary>The shade-patch graph for the current grid, or null where
		/// hopping does not apply. The first call after a recompute rebuilds
		/// it, which is O(cells) at most once per recompute interval.</summary>
		public RM_ShadePatchGraph PatchGraph
		{
			get
			{
				if (!ShadeHopsApply)
				{
					return null;
				}
				if (patchGraph == null || patchGraphVersion != gridVersion)
				{
					BuildPatchGraph();
				}
				return patchGraph;
			}
		}

		private void BuildPatchGraph()
		{
			RM_SunHeatExtension ext = HeatExtension;
			int n = map.cellIndices.NumGridCells;
			if (patchShadeMask == null || patchShadeMask.Length != n)
			{
				patchShadeMask = new bool[n];
				patchWalkMask = new bool[n];
			}
			PathGrid pg = map.pathing.Normal.pathGrid;
			float thr = ext.shadeExposureMax;
			foreach (IntVec3 c in map.AllCells)
			{
				int i = map.cellIndices.CellToIndex(c);
				bool walk = pg.Walkable(c);
				patchWalkMask[i] = walk;
				// An enclosed room is sheltered whatever the kind (ExposureAt's
				// live room test). Only a roofed, walkable, exposed cell can be
				// in one, so only those pay for the room lookup.
				patchShadeMask[i] = walk && (exposure[i] <= thr
					|| (map.roofGrid.Roofed(c) && !c.UsesOutdoorTemperature(map)));
			}
			int capCells = Mathf.CeilToInt(Mathf.Max(ext.maxDashCells, ext.ringMaxCells));
			patchGraph = RM_ShadePatchGraph.Build(map.Size.x, map.Size.z, patchShadeMask, patchWalkMask,
				capCells * RM_ShadePatchGraph.CardinalCost, ext.minPatchCells);
			patchGraphVersion = gridVersion;
		}

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
			lightSources.Clear();
			anyLight = false;
		}

		public override void MapComponentTick()
		{
			base.MapComponentTick();
			if (!RM_CreatureBehaviorsSettings.shadeGridEnabled)
			{
				return; // mod option: shade grid disabled — ShadeAt reports full sun everywhere
			}
			int now = Find.TickManager.TicksGame;
			if (recomputeRequested || now % RecomputeIntervalTicks == 0)
			{
				Recompute();
			}
			else if (now % ParasolRefreshTicks == 0)
			{
				RefreshParasolLayer();
			}
			if (now % MovingShadeRefreshTicks == 30)
			{
				RefreshMovingShade(false);
			}
			// STILLSAND_GLARE_BLIND_GOGGLES_1, offset off the recompute ticks.
			if (now % RM_GlareBlind.CheckIntervalTicks == 125)
			{
				RM_GlareBlind.Tick(map, this);
			}
		}

		/// <summary>The heat kind gear effectiveness is read under: the
		/// biome's, or overhead on a biome with no sun heat (ordinary shade —
		/// what the creature shade consumers read there).</summary>
		public RM_HeatKind GearKind => EffectiveHeatKind;

		/// <summary>RM_CompShadeGear: a tent or shield appeared. Recomputed
		/// on the next tick rather than waiting for the coarse interval.</summary>
		public void RegisterGear(Thing t)
		{
			if (t != null && gearThings.Add(t))
			{
				recomputeRequested = true;
			}
		}

		/// <summary>LONGSHADE_GPT_ENRICHMENT_1 §2: a living shade caster
		/// spawned (RM_Comp_ShadowCaster with castShadeHeight).</summary>
		public void RegisterMovingCaster(Thing t)
		{
			if (t != null && !movingCasters.ContainsKey(t))
			{
				movingCasters.Add(t, new MovingCasterState());
				movingDirty = true;
			}
		}

		public void UnregisterMovingCaster(Thing t)
		{
			if (t != null && movingCasters.TryGetValue(t, out MovingCasterState st))
			{
				if (st.hasRect && movingShade != null)
				{
					RM_MovingShadeMath.ClearRect(movingShade, map.Size.x, map.Size.z, st.minX, st.minZ, st.maxX, st.maxZ);
				}
				movingCasters.Remove(t);
				movingDirty = true;
			}
		}

		/// <summary>Shade 0..1 from living casters alone at this cell.</summary>
		public float MovingShadeAt(IntVec3 cell)
		{
			if (!Ready(cell) || movingShade == null)
			{
				return 0f;
			}
			return movingShade[map.cellIndices.CellToIndex(cell)];
		}

		/// <summary>Clears the old rectangle of every caster that moved and
		/// recasts every caster whose rectangle touched a cleared one. force:
		/// the sun vector or the arrays changed, so redo all of them.</summary>
		private void RefreshMovingShade(bool force)
		{
			if (movingCasters.Count == 0 && !force)
			{
				return;
			}
			int w = map.Size.x;
			int h = map.Size.z;
			int n = map.cellIndices.NumGridCells;
			if (movingShade == null || movingShade.Length != n)
			{
				movingShade = new float[n];
				force = true;
			}
			bool on = RM_CreatureBehaviorsSettings.shadeGridEnabled && RM_CreatureBehaviorsSettings.movingShadeEnabled;
			if (force)
			{
				System.Array.Clear(movingShade, 0, n);
				foreach (MovingCasterState st in movingCasters.Values)
				{
					st.hasRect = false;
					st.lastPos = IntVec3.Invalid;
				}
			}
			List<Thing> gone = null;
			bool any = force || movingDirty;
			foreach (KeyValuePair<Thing, MovingCasterState> kv in movingCasters)
			{
				Thing t = kv.Key;
				if (t == null || !t.Spawned || t.Map != map)
				{
					(gone ??= new List<Thing>()).Add(t);
					any = true;
					continue;
				}
				if (t.Position != kv.Value.lastPos)
				{
					any = true;
				}
			}
			if (gone != null)
			{
				foreach (Thing t in gone)
				{
					UnregisterMovingCaster(t);
				}
			}
			movingDirty = false;
			if (!any)
			{
				return;
			}
			// Clear every old rectangle first, then cast every caster at its
			// new place: overlapping shadows of two casters stay whole. With
			// the one or two giants a map holds this is a few hundred cells.
			foreach (MovingCasterState st in movingCasters.Values)
			{
				if (st.hasRect)
				{
					RM_MovingShadeMath.ClearRect(movingShade, w, h, st.minX, st.minZ, st.maxX, st.maxZ);
					st.hasRect = false;
				}
			}
			if (!on)
			{
				return;
			}
			foreach (KeyValuePair<Thing, MovingCasterState> kv in movingCasters)
			{
				Thing t = kv.Key;
				MovingCasterState st = kv.Value;
				st.lastPos = t.Position;
				RM_CompProperties_ShadowCaster p = t.TryGetComp<RM_Comp_ShadowCaster>()?.Props;
				if (p == null || p.castShadeHeight <= 0f)
				{
					continue;
				}
				float len = directional ? RM_SunHeatMath.ShadowLength(p.castShadeHeight, sunLengthPerHeight, MaxCastCells) : 0f;
				if (!RM_MovingShadeMath.ShadowBounds(w, h, t.Position.x, t.Position.z, p.castShadeRadius,
					directional, sunShadowDir.x, sunShadowDir.y, len, out st.minX, out st.minZ, out st.maxX, out st.maxZ))
				{
					continue;
				}
				st.hasRect = true;
				RM_MovingShadeMath.CastBody(movingShade, w, h, t.Position.x, t.Position.z, p.castShadeRadius,
					directional, sunShadowDir.x, sunShadowDir.y, len, ShadowTipShade, p.castShadeDepth);
			}
		}

		public void UnregisterGear(Thing t)
		{
			if (t != null && gearThings.Remove(t))
			{
				recomputeRequested = true;
			}
		}

		/// <summary>SOLAR_MIRRORS_MOD_DESIGN_1 §2.3: add a light source. Takes
		/// effect at the next Recompute (requested here, so the next tick).</summary>
		public void RegisterLightSource(IRM_LightLayer source)
		{
			if (source != null && !lightSources.Contains(source))
			{
				lightSources.Add(source);
				recomputeRequested = true;
			}
		}

		public void UnregisterLightSource(IRM_LightLayer source)
		{
			if (source != null && lightSources.Remove(source))
			{
				recomputeRequested = true;
			}
		}

		/// <summary>Registered light (0..N) at this cell as of the last
		/// Recompute; 0 with no source, or before the first recompute.</summary>
		public float LightAt(IntVec3 cell)
		{
			if (!anyLight || !Ready(cell))
			{
				return 0f;
			}
			return lightLayer[map.cellIndices.CellToIndex(cell)];
		}

		/// <summary>Shade 0..1 from shade gear alone at this cell (pitched and
		/// parasol), already scaled by the heat kind.</summary>
		public float GearShadeAt(IntVec3 cell)
		{
			if (!Ready(cell) || gearShade == null)
			{
				return 0f;
			}
			int i = map.cellIndices.CellToIndex(cell);
			float p = parasolShade != null ? parasolShade[i] : 0f;
			return Mathf.Max(gearShade[i], p);
		}

		/// <summary>SHADE_GEAR_FAMILY_1: exposure for this pawn where it
		/// stands, including the shade of a parasol it is wearing.</summary>
		public float ExposureFor(Pawn pawn)
		{
			float ex = ExposureAt(pawn.Position);
			if (ex <= 0f)
			{
				return 0f;
			}
			ex = RM_SunHeatMath.WithCover(ex, RM_ShadeGear.WornCover(pawn, GearKind, out _));
			ex = RM_SunHeatMath.WithGlareFloor(ex, GlareFloorAt(pawn.Position));
			// STILLSAND_DUNE_GALE_1 §3: a dim sky (the dune gale) takes the sun off,
			// glare floor included — the sand does not shine under a brown sky.
			return ex * RM_WeatherSenseExtension.SunFactor(map);
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
			float s = Mathf.Max(roofShade[i], castShade[i]);
			if (anyLight)
			{
				// Light cuts roof/cast shade only; gear, parasols and living
				// casters below still shade you inside a beam.
				s = RM_SunHeatMath.ShadeWithLight(s, lightLayer[i]);
			}
			if (gearShade != null)
			{
				s = Mathf.Max(s, gearShade[i]);
			}
			if (parasolShade != null)
			{
				s = Mathf.Max(s, parasolShade[i]);
			}
			if (movingShade != null && RM_CreatureBehaviorsSettings.movingShadeEnabled)
			{
				s = Mathf.Max(s, movingShade[i]);
			}
			return s;
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
			int i = map.cellIndices.CellToIndex(cell);
			float ex = exposure[i];
			if (parasolShade != null && EffectiveHeatKind != RM_HeatKind.ambient)
			{
				ex = RM_SunHeatMath.WithCover(ex, parasolShade[i]);
			}
			// LONGSHADE_GPT_ENRICHMENT_1 §2: a living caster's shadow is cast
			// shade, so it covers under overhead and low sun alike, never
			// under ambient heat.
			if (movingShade != null && RM_CreatureBehaviorsSettings.movingShadeEnabled && EffectiveHeatKind != RM_HeatKind.ambient)
			{
				ex = RM_SunHeatMath.WithCover(ex, movingShade[i]);
			}
			if (glareFloor != null)
			{
				ex = RM_SunHeatMath.WithGlareFloor(ex, glareFloor[i]);
			}
			return ex;
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
				gearShade = new float[n];
				parasolShade = new float[n];
				parasolTouched.Clear();
			}
			recomputeRequested = false;
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
			BuildGearLayer();
			RefreshParasolLayer();
			RefreshMovingShade(true);
			BuildLightLayer();
			RebuildHeatLayers();
			gridVersion++;
			// STILLSAND_MIRAGE_CONDITION_1: hold or end the mirage to match the sun.
			RM_Mirage.Sync(map, this);
		}

		/// <summary>SOLAR_MIRRORS_MOD_DESIGN_1 §2.3: zero the buffer (only if
		/// the last build lit anything) and let each source add its light.</summary>
		private void BuildLightLayer()
		{
			int n = map.cellIndices.NumGridCells;
			if (lightSources.Count == 0)
			{
				anyLight = false;
				return;
			}
			if (lightLayer == null || lightLayer.Length != n)
			{
				lightLayer = new float[n];
			}
			else if (anyLight)
			{
				System.Array.Clear(lightLayer, 0, n);
			}
			bool lit = false;
			for (int k = 0; k < lightSources.Count; k++)
			{
				lit |= lightSources[k].AddLight(lightLayer);
			}
			anyLight = lit;
		}

		/// <summary>SHADE_GEAR_FAMILY_1: tent footprints and shield lees, at
		/// their kind-resolved depth (0 under ambient heat, so nothing is
		/// written there at all).</summary>
		private void BuildGearLayer()
		{
			System.Array.Clear(gearShade, 0, gearShade.Length);
			if (gearThings.Count == 0)
			{
				return;
			}
			RM_HeatKind kind = GearKind;
			int width = map.Size.x;
			int height = map.Size.z;
			List<Thing> gone = null;
			foreach (Thing t in gearThings)
			{
				if (t == null || !t.Spawned || t.Map != map)
				{
					(gone ??= new List<Thing>()).Add(t);
					continue;
				}
				RM_CompProperties_ShadeGear p = t.def.GetCompProperties<RM_CompProperties_ShadeGear>();
				float depth = RM_ShadeGear.DepthOf(t, p, kind);
				if (depth <= 0f)
				{
					continue;
				}
				CellRect r = t.OccupiedRect();
				if (p.mode == RM_ShadeGearMode.footprint)
				{
					RM_SunHeatMath.FillRect(gearShade, width, height, r.minX, r.minZ, r.maxX, r.maxZ, depth);
					continue;
				}
				// lee: along the sun when there is one, else away from the
				// panel's face (its rotation is the way the face looks).
				float dx, dz, len;
				if (directional)
				{
					dx = sunShadowDir.x;
					dz = sunShadowDir.y;
					len = RM_SunHeatMath.ShadowLength(p.leeHeight, sunLengthPerHeight, MaxCastCells);
				}
				else
				{
					IntVec3 away = t.Rotation.Opposite.FacingCell;
					dx = away.x;
					dz = away.z;
					len = p.fallbackLeeCells;
				}
				// At least one cell of lee, however high the sun: a panel you
				// stand behind always has a behind.
				len = Mathf.Max(len, 1f);
				foreach (IntVec3 c in r)
				{
					RM_SunHeatMath.CastInto(gearShade, width, height, c.x, c.z, dx, dz, len, ShadowTipShade, depth);
				}
			}
			if (gone != null)
			{
				foreach (Thing t in gone)
				{
					gearThings.Remove(t);
				}
			}
		}

		/// <summary>SHADE_GEAR_FAMILY_1: each parasol also shades, weakly, the
		/// one cell its shadow falls on (along the sun, else the way its
		/// wearer faces). The wearer's own cover is read live in ExposureFor.</summary>
		private void RefreshParasolLayer()
		{
			if (parasolShade == null)
			{
				return;
			}
			for (int k = 0; k < parasolTouched.Count; k++)
			{
				parasolShade[parasolTouched[k]] = 0f;
			}
			parasolTouched.Clear();
			if (!RM_CreatureBehaviorsSettings.shadeGridEnabled || !RM_CreatureBehaviorsSettings.parasolShadeEnabled)
			{
				return;
			}
			RM_HeatKind kind = GearKind;
			if (kind == RM_HeatKind.ambient)
			{
				return;
			}
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int k = 0; k < pawns.Count; k++)
			{
				Pawn pawn = pawns[k];
				if (pawn.apparel == null)
				{
					continue;
				}
				float cover = RM_ShadeGear.WornCover(pawn, kind, out Apparel best);
				if (cover <= 0f || best == null)
				{
					continue;
				}
				float adj = cover * best.def.GetCompProperties<RM_CompProperties_ShadeGear>().adjacentFactor;
				float dx, dz;
				if (directional)
				{
					dx = sunShadowDir.x;
					dz = sunShadowDir.y;
				}
				else
				{
					IntVec3 f = pawn.Rotation.FacingCell;
					dx = f.x;
					dz = f.z;
				}
				if (!RM_SunHeatMath.AdjacentShadowCell(pawn.Position.x, pawn.Position.z, dx, dz, out int ax, out int az))
				{
					continue;
				}
				IntVec3 cell = new IntVec3(ax, 0, az);
				if (!cell.InBounds(map))
				{
					continue;
				}
				int i = map.cellIndices.CellToIndex(cell);
				if (adj > parasolShade[i])
				{
					if (parasolShade[i] == 0f)
					{
						parasolTouched.Add(i);
					}
					parasolShade[i] = adj;
				}
			}
		}

		/// <summary>Picks the sun vector for this recompute: pinned sun, else
		/// the heat extension's own geometry, else none (legacy ring).</summary>
		private void ResolveSun()
		{
			directional = false;
			sunElevationDeg = float.NaN;
			RM_MapComponent_PinnedSun pin = RM_MapComponent_PinnedSun.For(map);
			if (pin != null && pin.IsActive)
			{
				// The pinned sun's elevation is the map's sun elevation whether
				// or not shadows are cast directionally (it drives the heat kind
				// and the heat-by-angle offset too).
				sunElevationDeg = pin.SunElevationDegrees;
				if (RM_CreatureBehaviorsSettings.directionalShadeEnabled)
				{
					sunShadowDir = pin.ShadowDirection;
					sunLengthPerHeight = pin.ShadowLengthPerHeight;
					directional = true;
				}
				return;
			}
			RM_SunHeatExtension ext = HeatExtension;
			if (ext == null || Find.WorldGrid == null || !map.Tile.Valid)
			{
				return;
			}
			Vector2 longLat = Find.WorldGrid.LongLatOf(map.Tile);
			RM_MapComponent_PinnedSun.SunGeometry(longLat.y, longLat.x, ext.substellarLatitude, ext.substellarLongitude,
				out float bearingDeg, out float arcDeg);
			float elev = Mathf.Clamp(90f - arcDeg, ext.minElevationDegrees, ext.maxElevationDegrees);
			sunElevationDeg = elev;
			if (!RM_CreatureBehaviorsSettings.directionalShadeEnabled)
			{
				return;
			}
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
				glareFloor = null;
				RetireCustomizer();
				return;
			}
			int n = castShade.Length;
			if (exposure == null || exposure.Length != n)
			{
				exposure = new float[n];
			}
			RM_HeatKind kind = EffectiveHeatKind;
			BuildGlareLayer(ext, kind);
			bool wantPath = kind != RM_HeatKind.ambient && ext.sunPathCostPerCell > 0f
			                && RM_CreatureBehaviorsSettings.sunPathingEnabled;
			NativeArray<ushort> cost = default;
			if (wantPath)
			{
				cost = new NativeArray<ushort>(n, Allocator.Persistent);
			}
			float pathStrength = RM_CreatureBehaviorsSettings.sunPathCostMultiplier;
			// Under ambient heat (steam, volcanic) shade does nothing, so light does nothing either.
			bool applyLight = anyLight && kind != RM_HeatKind.ambient;
			for (int i = 0; i < n; i++)
			{
				// outdoors=true here: the enclosed-room test is live in ExposureAt.
				float ex = RM_SunHeatMath.Exposure(kind, true, roofShade[i], thickRoof[i], castShade[i], gearShade[i]);
				if (glareFloor != null)
				{
					ex = RM_SunHeatMath.WithGlareFloor(ex, glareFloor[i]);
				}
				if (applyLight)
				{
					ex = RM_SunHeatMath.WithLight(ex, lightLayer[i]);
				}
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

		/// <summary>STILLSAND_SUN_FROM_LATITUDE_1 §5: the sand glare floor on
		/// every cell of natural sand (TerrainDef categoryType Sand, not a
		/// constructed floor). Null when the biome sets no floor, the setting
		/// is off, or the heat is ambient (exposure is already full there).</summary>
		private void BuildGlareLayer(RM_SunHeatExtension ext, RM_HeatKind kind)
		{
			float floor = ext.sandGlareExposureFloor * RM_CreatureBehaviorsSettings.sandGlareStrength;
			if (!RM_CreatureBehaviorsSettings.sandGlareEnabled || floor <= 0f || kind == RM_HeatKind.ambient)
			{
				glareFloor = null;
				return;
			}
			floor = Mathf.Clamp01(floor);
			int n = map.cellIndices.NumGridCells;
			if (glareFloor == null || glareFloor.Length != n)
			{
				glareFloor = new float[n];
			}
			TerrainGrid tg = map.terrainGrid;
			for (int i = 0; i < n; i++)
			{
				TerrainDef t = tg.TerrainAt(i);
				glareFloor[i] = t != null && t.categoryType == TerrainDef.TerrainCategoryType.Sand && !t.IsFloor ? floor : 0f;
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
					if (thing.def.HasComp(typeof(RM_CompShadeGear)))
					{
						continue; // shade gear casts through BuildGearLayer, by heat kind
					}
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
				if (thing is Building && thing.def.fillPercent >= ShadeCastingFillPercentThreshold
					&& !thing.def.HasComp(typeof(RM_CompShadeGear)))
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
