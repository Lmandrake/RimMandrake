using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP — the cached per-band pocket grid (design/RimMandrake/
	/// relative_depth_climb_design_2026-10-12.md §8.3). It replaces RM_SuperdeepTrap.TryGetTrapRegion's per-pawn BFS and its
	/// 4000-cell cap while the relative rule is on (RimMandrakeFlowWorksSettings.pitRelativeClimbEnabled).
	///
	/// For each climb band K = 1..RM_PitTrapMath.MaxClimbLimit one component labelling over the whole map (RM_PocketGridMath.Label,
	/// selftested). PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: sized by who climbs, not by the dig cap (with digs past 2 m no K is
	/// "climbs every step there is"); ClimbLimit never exceeds MaxClimbLimit. Depth is <see cref="RM_MapComponent_Excavation.ClimbDepthAt"/>
	/// with an intact cover read as 0 (a cover is ground until it gives way).
	///
	/// INVALIDATION (GPT #12, #14): RM_MapComponent_Excavation.ClimbGeneration moves on every depth write (Deepen, FillIn), on
	/// cover spawn/despawn, and with a climb setting. The grid is REBUILT from the map tick, at most once per
	/// <see cref="RebuildMinTicks"/> (and, while paused, from the frame update at once: <see cref="UpdatePaused"/>), never from inside a query: region building reads IsPersonPocketCell mid-flood and must
	/// see one grid throughout. The only query-time build is the very first one (no grid yet). After a rebuild every cell whose
	/// person-band pocket bit flipped is handed to RM_PitRooms.NotifyPitnessChanged (§8.5 step 7), batched per generation.
	///
	/// Ladders are NOT in the grid (design: "Ladders stay a per-pawn read"): <see cref="UsableLadderIn"/> scans the map's
	/// ladders for one in the pocket that THIS pawn may climb (RM_LadderRules.LadderLetsOut); a pawnless query counts any
	/// lowered one, as the cliff masks do.
	/// </summary>
	public sealed class RM_PocketGrid
	{
		public const int RebuildMinTicks = 60;

		/// <summary>The band rooms and pawnless queries use: a person (K = 2, design §8.5 steps 6-7).</summary>
		public const int PersonBand = 2;

		private readonly List<Thing> ladderScratch = new List<Thing>();

		private static readonly ConditionalWeakTable<Map, RM_PocketGrid> grids = new ConditionalWeakTable<Map, RM_PocketGrid>();
		// TITAN_TRENCHES_WIRE_MIND_THE_GAP: per map, the grids labelled on a stride view (index s = 1..MaxStride; RM_TrenchStride)
		private static readonly ConditionalWeakTable<Map, RM_PocketGrid[]> strideGrids = new ConditionalWeakTable<Map, RM_PocketGrid[]>();
		private static int settingsSalt;

		private readonly Map map;
		/// <summary>TITAN_TRENCHES_WIRE_MIND_THE_GAP: 0 = the plain grid; s &gt; 0 = labelled on the depth a stride-s creature sees
		/// (every trench of width &lt;= s read as ground, RM_TrenchStrideMath.BridgedDepth). Never feeds the rooms.</summary>
		private readonly int stride;
		private RM_PocketGridMath.Labels[] bands;
		private int builtGeneration = int.MinValue;
		private int builtSalt = int.MinValue;
		private int builtTick = int.MinValue / 2;
		private readonly Dictionary<long, List<int>> cellsCache = new Dictionary<long, List<int>>();
		private readonly Dictionary<long, bool> wideCache = new Dictionary<long, bool>();
		private readonly Dictionary<long, bool> edgeCache = new Dictionary<long, bool>();

		/// <summary>Rebuild count, for the bridge proof (a pocket must survive save/reload identically).</summary>
		public int Rebuilds { get; private set; }

		private RM_PocketGrid(Map map, int stride = 0)
		{
			this.map = map;
			this.stride = stride;
		}

		public static bool Relative => RimMandrakeFlowWorksSettings.pitRelativeClimbEnabled;

		/// <summary>Band array length (index K = 1..MaxClimbLimit; 0 unused). PIT_DEPTH_WIDEN: was the dig cap (4).</summary>
		public static int BandCount => RM_PitTrapMath.ClimbBands;

		/// <summary>The grid for this map, built on first use. Never rebuilt here (see the class note).</summary>
		/// <summary>TITAN_TRENCHES_WIRE_MIND_THE_GAP: the grid this pawn's walk is judged on: the stride view for a creature that
		/// steps over the trenches on this map (RM_TrenchStride.ViewStride), else the plain grid. Every per-pawn hold, trap and
		/// reach verdict asks here, so it agrees with the stride cliff masks.</summary>
		public static RM_PocketGrid ForPawn(Map map, Pawn p)
		{
			int s = p == null ? 0 : RM_TrenchStride.ViewStride(p, map);
			return s > 0 ? For(map, s) : For(map);
		}

		/// <summary>The stride-s grid (s = 1..RM_TrenchStrideMath.MaxStride; 0 or out of range: the plain one), built on first use
		/// like the plain one and rebuilt with it.</summary>
		public static RM_PocketGrid For(Map map, int stride)
		{
			if (map == null || stride <= 0 || stride > RM_TrenchStrideMath.MaxStride)
			{
				return For(map);
			}
			RM_PocketGrid[] set = strideGrids.GetValue(map, m => new RM_PocketGrid[RM_TrenchStrideMath.MaxStride + 1]);
			RM_PocketGrid g = set[stride] ?? (set[stride] = new RM_PocketGrid(map, stride));
			if (g.bands == null)
			{
				g.Build(false);
			}
			return g;
		}

		public static RM_PocketGrid For(Map map)
		{
			if (map == null)
			{
				return null;
			}
			RM_PocketGrid g = grids.GetValue(map, m => new RM_PocketGrid(m));
			if (g.bands == null)
			{
				g.Build(false);
			}
			return g;
		}

		/// <summary>A climb setting changed: every map's grid is stale (and its rooms with it).</summary>
		public static void SettingsChanged()
		{
			settingsSalt++;
			RM_CliffMask.settingsSalt++;
			RM_PitRooms.RebuildAllMaps();
		}

		/// <summary>From RM_MapComponent_Excavation.MapComponentTick, every tick: rebuild if stale and allowed.</summary>
		public static void Tick(Map map, RM_MapComponent_Excavation eng)
		{
			RebuildIfStale(map, eng, false);
		}

		/// <summary>From RM_MapComponent_Excavation.MapComponentUpdate (every frame), only while the game is paused: the tick
		/// throttle can never pass with the clock stopped, so a depth write made paused (a dev tool, the bridge) left every trap
		/// verdict reading the old ground until time ran (V2_PIT_ROWS_DIAGNOSE_NOBODY_STAYS_IN: D4 pits dug paused held nobody).
		/// Paused, nothing writes depth on its own, so this is one rebuild per such write. Like Tick, never inside a query.</summary>
		public static void UpdatePaused(Map map, RM_MapComponent_Excavation eng)
		{
			if (Find.TickManager != null && Find.TickManager.Paused)
			{
				RebuildIfStale(map, eng, true);
			}
		}

		private static void RebuildIfStale(Map map, RM_MapComponent_Excavation eng, bool paused)
		{
			if (map == null || eng == null || !Relative)
			{
				return;
			}
			if (strideGrids.TryGetValue(map, out RM_PocketGrid[] set))
			{
				for (int s = 1; s < set.Length; s++)
				{
					if (set[s] != null)
					{
						set[s].RebuildIfStale(eng, paused, false);
					}
				}
			}
			if (grids.TryGetValue(map, out RM_PocketGrid g))
			{
				g.RebuildIfStale(eng, paused, true);
			}
		}

		private void RebuildIfStale(RM_MapComponent_Excavation eng, bool paused, bool notifyFlips)
		{
			if (bands == null)
			{
				return; // built on first query; nothing reads it yet
			}
			if (builtGeneration == eng.ClimbGeneration && builtSalt == settingsSalt)
			{
				return;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			if (!paused && now - builtTick < RebuildMinTicks)
			{
				return;
			}
			Build(notifyFlips);
		}

		private void Build(bool notifyFlips)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			int w = map.Size.x, h = map.Size.z;
			int n = w * h;
			byte[] depth = EffectiveDepth(map, eng);
			if (stride > 0)
			{
				// TITAN_TRENCHES_WIRE_MIND_THE_GAP: the stride view (RM_TrenchStride's masks bridge the same cells)
				depth = RM_TrenchStrideMath.BridgedDepth(depth, RM_TrenchStrideMath.RunWidths(depth, w, h), stride);
			}
			RM_PocketGridMath.Labels[] old = bands;
			var fresh = new RM_PocketGridMath.Labels[BandCount];
			bool anyDug = false;
			for (int i = 0; i < n && !anyDug; i++)
			{
				anyDug = depth[i] != 0;
			}
			// PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS: a ramp joins its square to the one it faces, for every band (design §8.3).
			Dictionary<int, int> ramps = anyDug ? RM_PitRamp.Pairs(map, depth) : null;
			System.Func<int, int, bool> rampJoins = ramps == null || ramps.Count == 0 ? null
				: (System.Func<int, int, bool>)((a, b) => ramps.TryGetValue(a, out int t) && t == b);
			for (int k = 1; k < BandCount; k++)
			{
				// No dug cell: every band is one surface component per map; skip the floods.
				fresh[k] = anyDug ? RM_PocketGridMath.Label(depth, w, h, k, rampJoins) : AllSurface(w, h, k);
			}
			bands = fresh;
			builtGeneration = eng?.ClimbGeneration ?? 0;
			builtSalt = settingsSalt;
			builtTick = Find.TickManager?.TicksGame ?? 0;
			cellsCache.Clear();
			wideCache.Clear();
			edgeCache.Clear();
			Rebuilds++;
			if (notifyFlips && stride == 0 && old != null && old[PersonBand] != null && RM_PitRooms.RoomsOn)
			{
				RM_PocketGridMath.Labels a = old[PersonBand], b = fresh[PersonBand];
				for (int i = 0; i < n; i++)
				{
					if (a.IsPocketCell(i) != b.IsPocketCell(i))
					{
						RM_PitRooms.NotifyPitnessChanged(map, map.cellIndices.IndexToCell(i));
					}
				}
			}
		}

		/// <summary>The climb depth of every cell (ClimbDepthAt), an intact cover read as ground (0): the one input the pocket
		/// grid and the cliff masks (RM_CliffMask) both derive from, so they never disagree. Read-only on the map.</summary>
		public static byte[] EffectiveDepth(Map map, RM_MapComponent_Excavation eng)
		{
			return EffectiveDepth(map, eng, false);
		}

		/// <summary>SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: <paramref name="floorView"/> = the floor band's view, where a
		/// suspension deck the floor band passes under reads as the floor beneath it (RM_CliffMask's floor-view masks).</summary>
		public static byte[] EffectiveDepth(Map map, RM_MapComponent_Excavation eng, bool floorView)
		{
			var depth = new byte[map.cellIndices.NumGridCells];
			if (eng != null)
			{
				eng.CopyClimbDepth(depth);
			}
			List<Thing> covers = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
			for (int i = 0; i < covers.Count; i++)
			{
				// SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT: any intact deck is ground at its walking height (a cover: 0).
				if (covers[i] is Pits.Building_SpanDeck c && c.Decked && c.Position.InBounds(map) && !(floorView && c.FloorBandPassesUnder))
				{
					int idx = map.cellIndices.CellToIndex(c.Position);
					depth[idx] = (byte)RM_SpanMath.WalkingDepth(depth[idx], c.Read);
				}
			}
			return depth;
		}

		private static RM_PocketGridMath.Labels AllSurface(int w, int h, int k)
		{
			return new RM_PocketGridMath.Labels
			{
				label = new int[w * h], count = 1, surface = new[] { true }, size = new[] { w * h },
				width = w, height = h, k = k,
			};
		}

		// ── reads ─────────────────────────────────────────────────────────

		/// <summary>The climb limit of this pawn (design §8.2): body size (life stage included) × the height setting, plus
		/// RM_ClimbAbility's extra levels.</summary>
		public static int ClimbLimitOf(Pawn p)
		{
			if (p == null)
			{
				return PersonBand;
			}
			// PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS: climbing gear climbs any wall (a K no band answers for: "climbs every step").
			return RM_PitAccessMath.ClimbLimitWithGear(NaturalClimbLimitOf(p), WearsClimbingGear(p),
				RimMandrakeFlowWorksSettings.climbingGearEnabled);
		}

		/// <summary>The climb limit without climbing gear: body size and the race's RM_ClimbAbility.</summary>
		public static int NaturalClimbLimitOf(Pawn p)
		{
			if (p == null)
			{
				return PersonBand;
			}
			RM_ClimbAbility ext = p.def?.GetModExtension<RM_ClimbAbility>();
			int extra = ext == null ? 0 : ext.extraLevels + (ext.leaper ? 1 : 0);
			return RM_PitTrapMath.ClimbLimit(p.BodySize, extra, RimMandrakeFlowWorksSettings.pitClimbAbilityMultiplier);
		}

		/// <summary>PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS: wearing apparel whose def carries RM_ClimbAbility with scalesAnyWall
		/// (RM_ClimbingGear). Setting-blind: the caller applies climbingGearEnabled.</summary>
		public static bool WearsClimbingGear(Pawn p)
		{
			List<Apparel> worn = p?.apparel?.WornApparel;
			if (worn == null)
			{
				return false;
			}
			for (int i = 0; i < worn.Count; i++)
			{
				RM_ClimbAbility ext = worn[i].def.GetModExtension<RM_ClimbAbility>();
				if (ext != null && ext.scalesAnyWall)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Climbing gear is worn AND switched on.</summary>
		public static bool ClimbsOnGear(Pawn p)
		{
			return RimMandrakeFlowWorksSettings.climbingGearEnabled && WearsClimbingGear(p);
		}

		private static StatDef maxFlightTime;
		private static bool maxFlightLooked;

		/// <summary>Flyers are never trapped (design §8.2): flying now, or able to fly (the MaxFlightTime stat, Core 1.6).</summary>
		public static bool CanFly(Pawn p)
		{
			if (p == null)
			{
				return false;
			}
			if (p.Flying)
			{
				return true;
			}
			if (!maxFlightLooked)
			{
				maxFlightLooked = true;
				maxFlightTime = DefDatabase<StatDef>.GetNamedSilentFail("MaxFlightTime");
			}
			return maxFlightTime != null && p.GetStatValue(maxFlightTime, true, 250) > 0f;
		}

		private RM_PocketGridMath.Labels BandOf(int k)
		{
			int b = RM_PocketGridMath.BandFor(k, BandCount);
			return b == 0 || bands == null || b >= bands.Length ? null : bands[b];
		}

		public bool IsPocketCell(int k, IntVec3 c)
		{
			RM_PocketGridMath.Labels l = BandOf(k);
			return l != null && c.InBounds(map) && l.IsPocketCell(map.cellIndices.CellToIndex(c));
		}

		/// <summary>Component id of a cell for band K; -1 out of bounds; for K past the bands every cell is component 0.</summary>
		public int ComponentOf(int k, IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return -1;
			}
			RM_PocketGridMath.Labels l = BandOf(k);
			return l == null ? 0 : l.label[map.cellIndices.CellToIndex(c)];
		}

		public bool ComponentIsPocket(int k, int component)
		{
			RM_PocketGridMath.Labels l = BandOf(k);
			return l != null && component >= 0 && component < l.count && !l.surface[component];
		}

		private static long Key(int k, int label, int w = 0)
		{
			return ((long)k << 56) | ((long)w << 40) | (uint)label;
		}

		/// <summary>Every cell of a component, cached until the next rebuild.</summary>
		public List<int> CellsOf(int k, int component)
		{
			RM_PocketGridMath.Labels l = BandOf(k);
			if (l == null)
			{
				return new List<int>();
			}
			long key = Key(k, component);
			if (!cellsCache.TryGetValue(key, out List<int> cells))
			{
				cells = RM_PocketGridMath.CellsOf(l, component);
				cellsCache[key] = cells;
			}
			return cells;
		}

		/// <summary>W×W over the pocket, every cell (RM_PocketGridMath.WideEverywhere), cached per (band, pocket, W).</summary>
		public bool WideEverywhere(int k, int component, int w)
		{
			if (w <= 1)
			{
				return true;
			}
			RM_PocketGridMath.Labels l = BandOf(k);
			if (l == null)
			{
				return false;
			}
			long key = Key(k, component, w);
			if (!wideCache.TryGetValue(key, out bool wide))
			{
				wide = RM_PocketGridMath.WideEverywhere(l, component, w);
				wideCache[key] = wide;
			}
			return wide;
		}

		/// <summary>REACH_VETO_FIX_ONE_END_ENOUGH: the component holds a map-border cell (RM_PocketGridMath.TouchesEdge),
		/// cached per (band, component) until the next rebuild. K past the bands: one component, the whole map.</summary>
		public bool TouchesEdge(int k, int component)
		{
			RM_PocketGridMath.Labels l = BandOf(k);
			if (l == null)
			{
				return true;
			}
			long key = Key(k, component);
			if (!edgeCache.TryGetValue(key, out bool edge))
			{
				edge = RM_PocketGridMath.TouchesEdge(l, component);
				edgeCache[key] = edge;
			}
			return edge;
		}

		/// <summary>Is (x, z) in a W×W square of this pocket's cells (the per-cell width rule, §8.1)?</summary>
		public bool WideAt(int k, int component, IntVec3 c, int w)
		{
			RM_PocketGridMath.Labels l = BandOf(k);
			if (l == null)
			{
				return false;
			}
			return RM_PitTrapMath.PitWidthAt((x, z) => x >= 0 && z >= 0 && x < l.width && z < l.height
				&& l.label[z * l.width + x] == component, c.x, c.z, w);
		}

		/// <summary>Widest square of this pocket's cells containing c: the inspect pane's "too big for it" read.</summary>
		public int MeasuredWidth(int k, IntVec3 c)
		{
			RM_PocketGridMath.Labels l = BandOf(k);
			if (l == null || !c.InBounds(map))
			{
				return 0;
			}
			int comp = l.label[map.cellIndices.CellToIndex(c)];
			return RM_PitTrapMath.MeasuredPitWidth((x, z) => x >= 0 && z >= 0 && x < l.width && z < l.height
				&& l.label[z * l.width + x] == comp, c.x, c.z);
		}

		/// <summary>A ladder that is a way out for this query stands in this component and leads out of it: one this pawn may
		/// climb; pawn null, any lowered one (RM_PocketGridMath.LadderIsAWay: the masks' structural view, which vanilla's
		/// pawnless StartPath reachability check must share).</summary>
		public bool UsableLadderIn(int k, int component, Pawn p)
		{
			// PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS: both ladder defs (the portable one's reach is LoweredLadderAt/LadderLetsOut's).
			List<Thing> ladders = RM_LadderUtility.AllLadders(map, ladderScratch);
			for (int i = 0; i < ladders.Count; i++)
			{
				IntVec3 c = ladders[i].Position;
				if (ComponentOf(k, c) == component && LadderLeadsOut(k, component, c, ladders[i].Rotation.AsInt)
					&& RM_PocketGridMath.LadderIsAWay(p != null, p == null && RM_ClimbJoins.LoweredLadderAt(map, c),
						p != null && RM_LadderRules.LadderLetsOut(map, c, p)))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS: a ladder is a way out only where it joins its cell to a SHALLOWER
		/// cardinal neighbour of another component (RM_CliffMaskMath.LadderJoins), the edge the masks and the step floor
		/// restore. A ladder in the middle of a flat floor leads nowhere, so the pocket and the pathfinder agree.
		/// PIT_LADDER_REDRAW_HUNG_ON_THE_WALL: only the wall it hangs on (its rotation, RM_LadderWallMath.Joins).</summary>
		private bool LadderLeadsOut(int k, int component, IntVec3 c, int rot)
		{
			if (rot < 0 || rot > 3)
			{
				return false;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			int d = RM_SuperdeepTrap.StepDepthAt(map, eng, c);
			int dx = RM_LadderWallMath.FX[rot], dz = RM_LadderWallMath.FZ[rot];
			var o = new IntVec3(c.x + dx, 0, c.z + dz);
			return o.InBounds(map) && ComponentOf(k, o) != component
				&& RM_LadderWallMath.Joins(rot, d, dx, dz, RM_SuperdeepTrap.StepDepthAt(map, eng, o));
		}

		// ── TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP: the ladder graph between components ───────────────
		private int edgeTick = int.MinValue;
		private int edgeRebuilds = -1;
		private int edgeVersion = -1;
		private readonly Dictionary<long, List<(int a, int b)>> ladderEdgeCache = new Dictionary<long, List<(int a, int b)>>();

		/// <summary>Every component join a ladder makes for this query (RM_PocketGridMath.LadderEdge: its square's component and
		/// the one across the wall it hangs on, when it is a way for this pawn — LadderLetsOut — or, pawnless, lowered). Cached
		/// per (band, pawn) for one tick and one grid build: ladders are raised, lowered, set and shot between ticks.</summary>
		public List<(int a, int b)> LadderEdges(int k, Pawn p)
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now != edgeTick || edgeRebuilds != Rebuilds || edgeVersion != RM_LadderUtility.StateVersion || ladderEdgeCache.Count > 512)
			{
				ladderEdgeCache.Clear();
				edgeTick = now;
				edgeRebuilds = Rebuilds;
				edgeVersion = RM_LadderUtility.StateVersion;
			}
			long key = ((long)k << 40) | (uint)(p == null ? -1 : p.thingIDNumber);
			if (ladderEdgeCache.TryGetValue(key, out List<(int a, int b)> edges))
			{
				return edges;
			}
			edges = new List<(int a, int b)>();
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			List<Thing> ladders = RM_LadderUtility.AllLadders(map, ladderScratch);
			for (int i = 0; i < ladders.Count; i++)
			{
				IntVec3 c = ladders[i].Position;
				int rot = ladders[i].Rotation.AsInt;
				if (rot < 0 || rot > 3 || !c.InBounds(map))
				{
					continue;
				}
				var o = new IntVec3(c.x + RM_LadderWallMath.FX[rot], 0, c.z + RM_LadderWallMath.FZ[rot]);
				if (!o.InBounds(map))
				{
					continue;
				}
				bool way = RM_PocketGridMath.LadderIsAWay(p != null, p == null && RM_ClimbJoins.LoweredLadderAt(map, c),
					p != null && RM_LadderRules.LadderLetsOut(map, c, p));
				int a = ComponentOf(k, c), b = ComponentOf(k, o);
				if (RM_PocketGridMath.LadderEdge(rot, RM_SuperdeepTrap.StepDepthAt(map, eng, c), a,
					RM_SuperdeepTrap.StepDepthAt(map, eng, o), b, way))
				{
					edges.Add((a, b));
				}
			}
			ladderEdgeCache[key] = edges;
			return edges;
		}

		/// <summary>Are two components of band K joined through ladders this query may use (down one wall, across a floor, up
		/// another — any number of hops)?</summary>
		public bool JoinedByLadders(int k, int from, int to, Pawn p)
		{
			return RM_PocketGridMath.JoinedByLadders(from, to, LadderEdges(k, p));
		}

		/// <summary>Does this component reach a map-border component on foot, its own border or through ladders?</summary>
		public bool ReachesEdge(int k, int component, Pawn p)
		{
			if (TouchesEdge(k, component))
			{
				return true;
			}
			List<(int a, int b)> edges = LadderEdges(k, p);
			var seen = new HashSet<int>();
			foreach ((int a, int b) e in edges)
			{
				seen.Add(e.a);
				seen.Add(e.b);
			}
			foreach (int c in seen)
			{
				if (c != component && TouchesEdge(k, c) && RM_PocketGridMath.JoinedByLadders(component, c, edges))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>No way out at all for this pawn from its pocket (design §8.3).</summary>
		public bool TrappedIn(int k, int component, Pawn p)
		{
			// Surface components are never traps: skip the ladder scan and the whole-component width walk (the map-edge
			// reach patch asks this for ordinary surface cells).
			if (!ComponentIsPocket(k, component))
			{
				return false;
			}
			return RM_PocketGridMath.Trapped(ComponentIsPocket(k, component), UsableLadderIn(k, component, p),
				WideEverywhere(k, component, RM_SuperdeepTrap.RequiredWidth(p)));
		}

		/// <summary>Rooms (§8.5 step 7): a pit room is a person-band pocket. Pawn-independent (GPT #11). Never rebuilds (region
		/// building reads it mid-flood), except the first build.</summary>
		public static bool IsPersonPocketCell(Map map, IntVec3 c)
		{
			RM_PocketGrid g = For(map);
			return g != null && g.IsPocketCell(PersonBand, c);
		}

		/// <summary>Bridge/proof read (jawa/static_call): "POCKET k=K comp=N pocket=b size=N gen=N built=N rebuilds=N".</summary>
		public static string ProofPocket(Map map, IntVec3 c, int k)
		{
			RM_PocketGrid g = For(map);
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (g == null || !c.InBounds(map))
			{
				return "REFUSED: no grid or out of bounds";
			}
			int comp = g.ComponentOf(k, c);
			RM_PocketGridMath.Labels l = g.BandOf(k);
			int size = l == null ? map.cellIndices.NumGridCells : l.size[comp];
			return "POCKET k=" + k + " comp=" + comp + " pocket=" + g.ComponentIsPocket(k, comp) + " size=" + size
				+ " depth=" + (eng?.ClimbDepthAt(c) ?? 0) + " gen=" + (eng?.ClimbGeneration ?? 0) + " built=" + g.builtGeneration
				+ " rebuilds=" + g.Rebuilds;
		}

		/// <summary>Player text (design §8.2: "the size table is stated, not hidden"), from the live band edges.</summary>
		public static string BandText()
		{
			float[] e = RM_PitTrapMath.ClimbBandEdges;
			return "under body size " + e[0].ToString("0.##") + " (rats, cats, dogs, children) a 1-level step; up to "
				+ e[1].ToString("0.##") + " (people, deer, wolves) 2 levels, the second slowly, so 3 traps them; up to "
				+ e[2].ToString("0.##") + " (muffalo, bears) 3 levels; bigger (thrumbos, elephants) 4 levels (2 m). "
				+ "Climbers and leapers manage one level more, and flyers are never trapped.";
		}
	}

	/// <summary>Design §8.2 modifiers (PROVISIONAL): patched onto a race's ThingDef. Climbers (insects, monkeys, squirrels) and
	/// leapers (hares, cats) each manage one level more (Patches/Canals/FlowWorks_ClimbAbility.xml).</summary>
	public class RM_ClimbAbility : DefModExtension
	{
		public int extraLevels;
		public bool leaper;

		/// <summary>PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS: on an APPAREL def (climbing gear), the wearer climbs any pit wall,
		/// slowly (RimMandrakeFlowWorksSettings.climbingGearSlowness per level).</summary>
		public bool scalesAnyWall;
	}
}
