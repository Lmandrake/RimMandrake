using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE — the wall-aware reach map (owner 2026-10-21 ~21:20 PDT: "Have to say (3) and let's
	/// look carefully (make a note) to measure how often that bug case occurs."; spec Transient/pile_2026-10-21/
	/// reachability_review.md §4, option C).
	///
	/// WHAT: per climb band and per coarse pawn class (RM_WallReachMath.ClassOf: opens doors or not, bashes or not, hostile to
	/// the player's doors, fence-blocked, non-swimmer), one component labelling over squares that are passable for that class
	/// AND joined by an allowed climb step (RM_WallReachMath.Label). passable[] is built here from the path grid and the edifice
	/// (V1: ConnectivitySource's byte admits destroyable walls, so it is never reused). Ladder edges are re-keyed onto these
	/// labels (V5, RM_PocketGrid.LadderJoins). Labels are built lazily, the first time a pawn of that class asks.
	///
	/// WHERE IT IS READ: only by the CanReach postfix veto below (RM_Patch_Reachability_WallReach), which can only turn vanilla's
	/// yes into a no. Pockets, trapping, pit rooms and CanReachMapEdge stay on the depth-only labels (ruling 1).
	///
	/// WHEN IT MOVES: a stamp of (climb generation, climb settings salt, the walkability generation, the door print, the swim
	/// grids' version). The walkability generation is bumped at once from RegionDirtyer (a wall built or removed, a door or
	/// fence spawned or despawned: REACH_WINCH_FIX_GHOST_ROAD_RETURNS) and again from the ConnectivitySource.UpdateIncrementally
	/// / ComputeAll postfixes (inside GatherData, which runs only on a tick some pawn asks for a path); the door print (doors held open, the player's doors, drawbridge gates shut
	/// to everyone) is re-read every DoorPrintTicks; a gate lock flip bumps at once (RM_Drawbridges.Mode). Stale labels are
	/// rebuilt from the map tick at most once per RebuildMinTicks; a breach (a delta square that became walkable), a drawbridge
	/// toggle (RM_PocketGrid.ForceRebuild), a gate lock or hold, or a swim change forces the next tick's rebuild. Like the
	/// pocket grid, a query reads the last built labels and never rebuilds (the only query-time build is the first one).
	///
	/// THE RESIDUAL (the owner's explicit ask): RM_Patch_PathFollower_ReachResidual counts every pather failure whose path request
	/// came back Found == false after StartPath's CanReach said yes, classifies it (RM_WallReachMath.Classify), and keeps counts
	/// per faction/class and per suspect door (a door this pawn cannot pass that its class counts open). Logged in a bounded way
	/// (RM_WallReachMath.ShouldLog). Read through ProofReach.
	/// </summary>
	public static class RM_WallReach
	{
		public const int RebuildMinTicks = 60;
		public const int DoorPrintTicks = 10;
		public const int DropUnusedTicks = 2500;
		public const int LogFirst = 10;
		private const int MaxKeys = 64;

		public sealed class Entry
		{
			public RM_PocketGrid grid;   // the depth view (null: walls only)
			public int band;             // RM_PocketGridMath.BandFor(k); 0 with no grid
			public int cls;
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES / WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP: the labelling, its spare array
			// and the inputs it was built from (RM_WallReachMath.LabelSlot: the buffer contract and skip rule the selftest drives).
			public readonly RM_WallReachMath.LabelSlot slot = new RM_WallReachMath.LabelSlot();
			public RM_WallReachMath.Labels labels => slot.labels;
			public long stamp;
			public int builtTick;
			public int lastUsedTick;
			// WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP (GPT review F2): built while the game was loading (half-spawned kinds or
			// depth); rebuilt from a fresh read on the first tick or frame in play, whatever the stamp says.
			public bool midLoad;
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (r14 lead c): the stamp's parts this labelling was built at (StampPart*),
			// so a rebuild can say which part moved
			public readonly long[] builtParts = new long[StampParts];
		}

		// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (r14 leads b and c): diagnostic counters read through TimingLine. Nothing reads
		// them back. The stamp's parts, in StampOf's order:
		private const int StampClimb = 0, StampSalt = 1, StampWall = 2, StampDoor = 3, StampSwim = 4, StampRamps = 5, StampParts = 6;
		private static readonly string[] StampPartNames = { "climb", "salt", "wall", "door", "swim", "ramps" };
		// why a Tick rebuilt an entry: one count per stamp part that moved since the entry's build, plus a post-load redo and a
		// rebuild with no part moved (forced only, or a first build by a query)
		private const int CauseReload = StampParts, CauseNoPart = StampParts + 1, RebuildCauses = StampParts + 2;
		private static readonly string[] RebuildCauseNames = { "climb", "salt", "wall", "door", "swim", "ramps", "reload", "none" };
		// who moved wallGen
		private const int WgWalk = 0, WgWalkPocket = 1, WgConnAll = 2, WgConnBreach = 3, WgConnNoSnap = 4, WgDelta = 5, WgBarrier = 6,
			WgBump = 7, WgUnjudged = 8, WgSources = 9;
		private static readonly string[] WallGenNames =
			{ "walk", "walkPocketFlip", "connAll", "connBreach", "connNoSnap", "delta", "barrier", "bump", "unjudged" };
		// Tick's phases (milliseconds): the delta flush, the door re-read, the stamp, the entry loop outside Build, Build
		private const int TpFlush = 0, TpDoor = 1, TpStamp = 2, TpLoop = 3, TpBuild = 4, TickPhases = 5;
		private static readonly string[] TickPhaseNames = { "flush", "door", "stamp", "loop", "build" };
		/// <summary>Set by RM_PocketGrid's pocket-flip notifications (main thread): NoteWalkability calls inside are counted
		/// apart, so the cascade pocket rebuild -> RegionDirtyer -> wallGen shows in WallGenNames' walkPocketFlip.</summary>
		internal static bool pocketFlipNotifying;

		private sealed class MapState
		{
			public int wallGen;
			public int forced;
			public int doorPrint;
			public int doorTick = int.MinValue / 2;
			public readonly Dictionary<(RM_PocketGrid, int, int), Entry> entries = new Dictionary<(RM_PocketGrid, int, int), Entry>();
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES / WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP: the published kinds (never
			// written after publication; NoteConnectivity reads it on a worker) and the scratch the next read goes into.
			public readonly RM_WallReachMath.KindsSnapshot kinds = new RM_WallReachMath.KindsSnapshot();
			public bool builtMidLoad;     // some entry or the kinds were built while loading (Tick's post-load rebuild)
			public int viewsReused;       // Build took the pocket grid's built view instead of reading the map again
			public int builds;
			public int skipped;      // EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: builds whose inputs were identical (labels kept)
			public int deltaBumps, deltaQuiet;   // connectivity deltas that moved a kind / that did not
			public readonly long[] partsNow = new long[StampParts];   // StampOf's parts, last computed
			public readonly int[] rebuildCauses = new int[RebuildCauses];
			public readonly int[] wallGenBy = new int[WgSources];
			public int walkQuiet, walkMoved;     // NoteWalkability calls whose square's kind the snapshot already held (no bump) / that bumped
			public int flushes, flushCells, flushMaxCells, flushOverflows;
			public readonly double[] tickPhaseMs = new double[TickPhases];
			public double maxTickMs;
			public int ticks;
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: GatherData's deltas, queued (under the lock: Parallel.ForEach worker)
			// and judged on the map tick against the kinds snapshot (DeltaMovesKinds).
			public readonly object deltaLock = new object();
			public readonly List<int> pendingDeltas = new List<int>();
			public bool deltaOverflow;
			public readonly List<int> deltaScratch = new List<int>();
			public double lastMs, maxMs, totalMs;
			public int firstBuiltTick = int.MinValue;
			public int pausedFrameTick = int.MinValue;   // the tick and stamp the last paused frame left (PausedUnthrottled)
			public long pausedFrameStamp = long.MinValue;
			public int steppedFrames;                    // paused frames whose clock had moved (time stepped under the pause)
			// ladder joins, per (grid, pawn) for one tick and one ladder state
			public int ladderTick = int.MinValue;
			public int ladderVersion = -1;
			public readonly Dictionary<(RM_PocketGrid, int), List<(int ladder, int other)>> ladderJoins =
				new Dictionary<(RM_PocketGrid, int), List<(int ladder, int other)>>();
		}

		private static readonly ConditionalWeakTable<Map, MapState> states = new ConditionalWeakTable<Map, MapState>();
		private static readonly List<int> goalScratch = new List<int>();
		private static readonly List<(int a, int b)> edgeScratch = new List<(int a, int b)>();

		/// <summary>Session counters (process statics; a load does not reset them; ProofReachReset does).</summary>
		public static int Queries, Vetoes;

		public static bool On => RimMandrakeFlowWorksSettings.reachSeesWallsAndCliffs;

		private static MapState StateOf(Map map)
		{
			return states.GetValue(map, _ => new MapState());
		}

		// ── invalidation ────────────────────────────────────────────────────────────

		/// <summary>From the ConnectivitySource postfixes (inside GatherData: maybe a worker thread, main thread blocked). all:
		/// ComputeAll (the whole array is new). A delta square that is walkable now but was a WALL in the last kinds snapshot is
		/// a breach (a wall gone, a door built in a wall): the next tick rebuilds at once. Anything else (a wall built: vanilla's
		/// deltas also list its walkable neighbours) only bumps: stale labels are more connected than the map, so they can only
		/// miss a veto for up to RebuildMinTicks, never invent one. (Live 2026-10-21, first run: "any walkable delta forces"
		/// rebuilt on every wall placed, 436 builds in 463 ticks of staging.)</summary>
		internal static void NoteConnectivity(Map map, List<IntVec3> deltas, bool all)
		{
			if (map == null)
			{
				return;
			}
			MapState st = StateOf(map);
			if (all)
			{
				Interlocked.Increment(ref st.wallGenBy[WgConnAll]);
				Interlocked.Increment(ref st.wallGen);
				Interlocked.Exchange(ref st.forced, 1);
				return;
			}
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: an empty delta list (most gathers) changes nothing; the rest is queued and
			// judged on the map tick (FlushDeltas), which bumps the generation only when a square's kind really moved.
			if (deltas == null || deltas.Count == 0)
			{
				return;
			}
			PathGrid pg = map.pathing?.Normal?.pathGrid;
			byte[] kinds = st.kinds.published;
			CellIndices ci = map.cellIndices;
			lock (st.deltaLock)
			{
				for (int i = 0; i < deltas.Count && !st.deltaOverflow; i++)
				{
					if (!deltas[i].InBounds(map))
					{
						continue;
					}
					if (st.pendingDeltas.Count >= RM_WallReachMath.MaxQueuedDeltas)
					{
						st.deltaOverflow = true;
						break;
					}
					st.pendingDeltas.Add(ci.CellToIndex(deltas[i]));
				}
			}
			if (pg == null || kinds == null)
			{
				Interlocked.Increment(ref st.wallGenBy[WgConnNoSnap]);
				Interlocked.Increment(ref st.wallGen);   // no snapshot to judge against: stale, as before
				return;
			}
			for (int i = 0; i < deltas.Count; i++)
			{
				if (!deltas[i].InBounds(map))
				{
					continue;
				}
				int idx = ci.CellToIndex(deltas[i]);
				if (idx < kinds.Length && kinds[idx] == RM_WallReachMath.Wall && pg.WalkableFast(idx))
				{
					Interlocked.Increment(ref st.wallGenBy[WgConnBreach]);
					Interlocked.Increment(ref st.wallGen);
					Interlocked.Exchange(ref st.forced, 1);
					return;
				}
			}
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: judge the queued connectivity deltas (main thread, from Tick before
		/// the stamp is read): the walkability generation moves only if some delta square's kind differs from the kinds
		/// snapshot the current labels were built from (RM_WallReachMath.DeltaMovesKinds). Bounded: at most MaxQueuedDeltas
		/// squares, each one KindAt.</summary>
		private static void FlushDeltas(Map map, MapState st)
		{
			List<int> work = st.deltaScratch;
			work.Clear();
			bool overflow;
			lock (st.deltaLock)
			{
				if (st.pendingDeltas.Count == 0 && !st.deltaOverflow)
				{
					return;
				}
				work.AddRange(st.pendingDeltas);
				st.pendingDeltas.Clear();
				overflow = st.deltaOverflow;
				st.deltaOverflow = false;
			}
			st.flushes++;
			st.flushCells += work.Count;
			if (work.Count > st.flushMaxCells)
			{
				st.flushMaxCells = work.Count;
			}
			if (overflow)
			{
				st.flushOverflows++;
			}
			byte[] kinds = st.kinds.published;
			bool swim = Swimming.RM_SwimWater.On && Swimming.RM_SwimPathing.DeepCount(map) > 0;
			PathGrid pg = map.pathing.Normal.pathGrid;
			if (kinds != null && kinds.Length != map.cellIndices.NumGridCells)
			{
				kinds = null;
			}
			if (RM_WallReachMath.DeltaMovesKinds(kinds, work, i => KindAt(map, pg, swim, i), overflow))
			{
				st.wallGenBy[WgDelta]++;
				Interlocked.Increment(ref st.wallGen);
				st.deltaBumps++;
			}
			else
			{
				st.deltaQuiet++;
			}
			work.Clear();
		}

		/// <summary>REACH_WINCH_FIX_GHOST_ROAD_RETURNS: the path grid's walkability moved on one square (RegionDirtyer, called
		/// synchronously from PathGrid when a wall is built or removed). ConnectivitySource's deltas (NoteConnectivity) arrive
		/// only when the pathfinder GATHERS, i.e. when some pawn asks for a path that tick (PathFinder.PathFinderTick: no work,
		/// no GatherData). A labelling built before a wall went up therefore stayed current-looking until the next path request:
		/// on a map where nobody walked, CanReach read a ghost road through the new wall (reach_map_proof REACH_WINCH_SITE, live
		/// 2026-10-22 on a reused map: canReach=True found=False; the A* call itself gathered, so the next read agreed).</summary>
		internal static void NoteWalkability(Map map, IntVec3 c, bool nowWalkable)
		{
			if (map == null || !On || !states.TryGetValue(map, out MapState st))
			{
				return;
			}
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (r15 fix 1): the generation moves only when the square's kind (KindAt, the
			// rule Kinds builds with; PathGrid has already written the new cost when RegionDirtyer is told) differs from the
			// published snapshot. No snapshot, an out-of-range square or no path grid yet: bump, as before.
			byte[] kinds = st.kinds.published;
			int idx = c.InBounds(map) ? map.cellIndices.CellToIndex(c) : -1;
			PathGrid pg = map.pathing?.Normal?.pathGrid;
			bool moved = kinds == null || idx < 0 || pg == null
				|| RM_WallReachMath.WalkabilityMovesKind(kinds, idx, KindAt(map, pg, Swimming.RM_SwimWater.On, idx));
			if (moved)
			{
				Interlocked.Increment(ref st.wallGenBy[pocketFlipNotifying ? WgWalkPocket : WgWalk]);
				Interlocked.Increment(ref st.wallGen);
				Interlocked.Increment(ref st.walkMoved);
			}
			else
			{
				Interlocked.Increment(ref st.walkQuiet);
			}
			if (kinds != null && idx >= 0 && idx < kinds.Length && RM_WallReachMath.WalkabilityBreach(kinds[idx], nowWalkable))
			{
				Interlocked.Exchange(ref st.forced, 1);
			}
		}

		/// <summary>REACH_WINCH_FIX_GHOST_ROAD_RETURNS: a door or a fence (region-affecting, walkability unchanged) spawned or
		/// despawned: the kinds snapshot is stale at once; a removal opens a way (forced, as a breach).</summary>
		internal static void NoteBarrier(Map map, Thing t, bool removed)
		{
			if (map == null || t == null || !On || !(t is Building_Door || t.def.IsFence) || !states.TryGetValue(map, out MapState st))
			{
				return;
			}
			Interlocked.Increment(ref st.wallGenBy[WgBarrier]);
			Interlocked.Increment(ref st.wallGen);
			if (removed)
			{
				Interlocked.Exchange(ref st.forced, 1);
			}
		}

		/// <summary>A drawbridge leaf toggled (RM_PocketGrid.ForceRebuild): rebuild what is stale on the next walk, unthrottled.</summary>
		public static void Force(Map map)
		{
			if (map != null)
			{
				Interlocked.Exchange(ref StateOf(map).forced, 1);
			}
		}

		/// <summary>Something the labels read changed outside the path grid (a gate lock flip): stale now, rebuilt unthrottled.</summary>
		public static void Bump(Map map)
		{
			if (map == null)
			{
				return;
			}
			MapState st = StateOf(map);
			Interlocked.Increment(ref st.wallGenBy[WgBump]);
			Interlocked.Increment(ref st.wallGen);
			Interlocked.Exchange(ref st.forced, 1);
		}

		private static int SwimVersion(Map map)
		{
			return Swimming.RM_SwimWater.On ? Swimming.RM_SwimPathing.VersionOf(map) : -1;
		}

		private static long StampOf(Map map, MapState st)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			long[] p = st.partsNow;
			p[StampClimb] = eng == null ? 0 : eng.ClimbGeneration;
			p[StampSalt] = RM_CliffMask.settingsSalt;
			p[StampWall] = Volatile.Read(ref st.wallGen);
			p[StampDoor] = st.doorPrint;
			p[StampSwim] = SwimVersion(map);
			p[StampRamps] = RimMandrakeFlowWorksSettings.pitRampsEnabled ? 1 : 0;
			long s = p[StampClimb];
			s = s * 31 + p[StampSalt];
			s = s * 1000003 + p[StampWall];
			s = s * 1000003 + p[StampDoor];
			s = s * 31 + p[StampSwim];
			s = s * 2 + p[StampRamps];
			return s;
		}

		/// <summary>A cheap fingerprint of every door's state the labels read (position, held open, the player's, a gate shut
		/// to everyone).</summary>
		private static int DoorPrint(Map map)
		{
			unchecked
			{
				int h = 17;
				List<Thing> doors = map.listerThings.ThingsInGroup(ThingRequestGroup.Door);
				for (int i = 0; i < doors.Count; i++)
				{
					if (doors[i] is Building_Door d)
					{
						h = h * 31 + d.thingIDNumber;
						h = h * 31 + KindOfDoor(d);
					}
				}
				return h;
			}
		}

		private static byte KindOfDoor(Building_Door d)
		{
			if (d is Pits.Building_DrawbridgeGate g && g.ShutToEveryone)
			{
				return RM_WallReachMath.ShutGate;
			}
			if (d.HoldOpen)
			{
				return RM_WallReachMath.HeldDoor;
			}
			return d.Faction != null && d.Faction == Faction.OfPlayer && !(d is Building_HackableDoor) ? RM_WallReachMath.PlayerDoor
				: RM_WallReachMath.Door;
		}

		private static void RefreshDoorPrint(Map map, MapState st, int now, bool paused)
		{
			if (!paused && now - st.doorTick < DoorPrintTicks && now >= st.doorTick)
			{
				return;
			}
			st.doorTick = now;
			int p = DoorPrint(map);
			if (p != st.doorPrint)
			{
				st.doorPrint = p;
				Interlocked.Exchange(ref st.forced, 1);   // a gate locked or held, a door held open: no throttle
			}
		}

		// ── building ────────────────────────────────────────────────────────────────

		/// <summary>The kind of every square: the path grid (walkable or not), doors and fences from the edifice, deep swim
		/// water. Shared by every (band, class) labelling of one stamp.</summary>
		private static byte[] Kinds(Map map, MapState st, long stamp)
		{
			int w = map.Size.x, h = map.Size.z;
			if (st.kinds.CurrentFor(stamp, w, h))
			{
				return st.kinds.published;
			}
			int n = map.cellIndices.NumGridCells;
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: read into the scratch (every square written below); it is published only
			// when its content (or the map's geometry) moved, else it stays scratch for the next stamp, so a labelling built
			// from the published array can tell by reference that its walls did not move (LabelSlot's skip).
			byte[] kinds = st.kinds.Take(n);
			PathGrid pg = map.pathing.Normal.pathGrid;
			bool swim = Swimming.RM_SwimWater.On && Swimming.RM_SwimPathing.DeepCount(map) > 0;
			for (int i = 0; i < n; i++)
			{
				kinds[i] = KindAt(map, pg, swim, i);
			}
			return st.kinds.Publish(kinds, stamp, w, h);
		}

		/// <summary>The kind of one square (Kinds' rule, and FlushDeltas' judge of a delta).</summary>
		private static byte KindAt(Map map, PathGrid pg, bool swim, int i)
		{
			Building ed = map.edificeGrid[i];
			if (ed is Building_Door d)
			{
				return KindOfDoor(d);
			}
			if (ed != null && ed.def.IsFence)
			{
				return RM_WallReachMath.Fence;
			}
			if (!pg.WalkableFast(i))
			{
				return RM_WallReachMath.Wall;
			}
			return swim && Swimming.RM_SwimWater.IsDeepSwimCell(map, map.cellIndices.IndexToCell(i)) ? RM_WallReachMath.DeepWater : RM_WallReachMath.Open;
		}

		private static void Build(Map map, MapState st, Entry e, long stamp, Dictionary<RM_PocketGrid, (byte[] depth, Dictionary<int, int> ramps)> views)
		{
			// WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP: every caller holds the owner gate (EntryFor under Judge or
			// RecordPathFailure, Tick); one more check costs nothing and keeps a future caller honest.
			if (!RM_PocketGrid.EnterOwner(out bool nested))
			{
				return;
			}
			try
			{
				BuildOwned(map, st, e, stamp, views);
			}
			finally
			{
				RM_PocketGrid.ExitOwner(nested);
			}
		}

		private static void BuildOwned(Map map, MapState st, Entry e, long stamp, Dictionary<RM_PocketGrid, (byte[] depth, Dictionary<int, int> ramps)> views)
		{
			var sw = System.Diagnostics.Stopwatch.StartNew();
			byte[] kinds = Kinds(map, st, stamp);
			byte[] depth = null;
			Dictionary<int, int> ramps = null;
			if (e.grid != null)
			{
				if (views == null || !views.TryGetValue(e.grid, out (byte[] depth, Dictionary<int, int> ramps) v))
				{
					// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: the pocket grid's own view when it is still the map's (same climb
					// generation, salt and ramp settings), else read the map
					if (e.grid.BuiltView(out byte[] builtDepth, out Dictionary<int, int> builtRamps))
					{
						v = (builtDepth, builtRamps);
						st.viewsReused++;
					}
					else
					{
						byte[] d = e.grid.ViewDepth();
						bool anyDug = false;
						for (int i = 0; i < d.Length && !anyDug; i++)
						{
							anyDug = d[i] != 0;
						}
						v = (anyDug ? d : null, anyDug ? e.grid.RampPairs(d, true) : null);
					}
					views?.Add(e.grid, v);
				}
				depth = v.depth;
				ramps = v.ramps;
			}
			// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: the labelling is a pure function of (kinds, depth, ramps, band, class, the
			// map's width and height); identical inputs keep it (LabelSlot.Rebuild: WallReach_content_skip_equals_rebuild,
			// WallReach_slot_lifecycle), a whole-map flood saved.
			if (!e.slot.Rebuild(kinds, depth, ramps, map.Size.x, map.Size.z, e.band, e.cls))
			{
				st.skipped++;
			}
			e.stamp = stamp;
			System.Array.Copy(st.partsNow, e.builtParts, StampParts);
			e.midLoad = Current.ProgramState != ProgramState.Playing;
			st.builtMidLoad |= e.midLoad;
			int now = Find.TickManager?.TicksGame ?? 0;
			e.builtTick = now;
			st.builds++;
			st.lastMs = sw.Elapsed.TotalMilliseconds;
			st.totalMs += st.lastMs;
			if (st.lastMs > st.maxMs)
			{
				st.maxMs = st.lastMs;
			}
			if (st.firstBuiltTick == int.MinValue)
			{
				st.firstBuiltTick = now;
			}
		}

		/// <summary>From RM_PocketGrid.UpdatePaused (every frame while the game is paused). WALL_REACH_TUNE_REBUILDS_TENFOLD:
		/// unthrottled only for a write made while the clock is stopped (RM_WallReachMath.PausedUnthrottled); a stepped frame
		/// (safe_advance, the dev step button) or an idle frame between step bursts runs the throttled Tick. The first paused
		/// frame after time ran only records, so a write made paused is seen at most one frame later, never 60 ticks later.
		/// The stamp is recorded after Tick (whose door re-read can move it), so the next frame compares against what this
		/// one left.</summary>
		public static void PausedFrame(Map map)
		{
			if (map == null || !On || !states.TryGetValue(map, out MapState st) || !RM_PocketGrid.EnterOwner(out bool nested))
			{
				return;
			}
			try
			{
				PausedFrameOwned(map, st);
			}
			finally
			{
				RM_PocketGrid.ExitOwner(nested);
			}
		}

		private static void PausedFrameOwned(Map map, MapState st)
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now != st.pausedFrameTick)
			{
				st.steppedFrames++;
			}
			FlushDeltas(map, st);   // a paused write's deltas move the stamp before it is compared (as the eager bump did)
			bool unthrottled = RM_WallReachMath.PausedUnthrottled(now, st.pausedFrameTick, StampOf(map, st), st.pausedFrameStamp);
			Tick(map, unthrottled);
			st.pausedFrameTick = now;
			st.pausedFrameStamp = StampOf(map, st);
		}

		/// <summary>From RM_PocketGrid.Tick (every map tick), PausedFrame and ForceRebuild (paused = unthrottled): re-read the
		/// doors, drop labellings nobody asked for in DropUnusedTicks (only classes of pawns now asking are kept), rebuild the
		/// stale ones when due. Never inside a query.</summary>
		public static void Tick(Map map, bool paused)
		{
			if (map == null || !On || !states.TryGetValue(map, out MapState st) || !RM_PocketGrid.EnterOwner(out bool nested))
			{
				return;
			}
			try
			{
				TickOwned(map, st, paused);
			}
			finally
			{
				RM_PocketGrid.ExitOwner(nested);
			}
		}

		private static void TickOwned(Map map, MapState st, bool paused)
		{
			long t0 = System.Diagnostics.Stopwatch.GetTimestamp(), mark = t0;
			RM_PocketGrid.ReportRefusals();
			FlushDeltas(map, st);
			TickLap(st, ref mark, TpFlush);
			if (st.entries.Count == 0)
			{
				TickDone(st, t0);
				return;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			RefreshDoorPrint(map, st, now, paused);
			TickLap(st, ref mark, TpDoor);
			long stamp = StampOf(map, st);
			TickLap(st, ref mark, TpStamp);
			bool forced = Volatile.Read(ref st.forced) != 0;
			double buildMs = 0;
			// WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP (GPT review F2): a labelling (or the kinds) built while the game was
			// loading read half-spawned ground; the first tick or frame in play re-reads the kinds and rebuilds those entries,
			// unthrottled, even though no stamp input moved (RM_PocketGrid's RELOAD_POCKETS rule).
			bool playing = Current.ProgramState == ProgramState.Playing;
			if (RM_WallReachMath.StaleAfterLoad(st.builtMidLoad, playing))
			{
				st.kinds.Invalidate();
				st.builtMidLoad = false;
			}
			List<(RM_PocketGrid, int, int)> drop = null;
			Dictionary<RM_PocketGrid, (byte[], Dictionary<int, int>)> views = null;
			bool any = false;
			foreach (KeyValuePair<(RM_PocketGrid, int, int), Entry> kv in st.entries)
			{
				Entry e = kv.Value;
				if (now - e.lastUsedTick > DropUnusedTicks || now < e.lastUsedTick - DropUnusedTicks)
				{
					(drop ?? (drop = new List<(RM_PocketGrid, int, int)>())).Add(kv.Key);
					continue;
				}
				bool reload = RM_WallReachMath.StaleAfterLoad(e.midLoad, playing);
				if (RM_WallReachMath.RebuildDue(e.stamp != stamp || reload, forced || reload, paused, now, e.builtTick, RebuildMinTicks))
				{
					views = views ?? new Dictionary<RM_PocketGrid, (byte[], Dictionary<int, int>)>();
					CountRebuildCause(st, e, reload);
					long b0 = System.Diagnostics.Stopwatch.GetTimestamp();
					Build(map, st, e, stamp, views);
					buildMs += (System.Diagnostics.Stopwatch.GetTimestamp() - b0) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
					any = true;
				}
			}
			if (drop != null)
			{
				foreach ((RM_PocketGrid, int, int) k in drop)
				{
					st.entries.Remove(k);
				}
			}
			if (any || forced)
			{
				Interlocked.Exchange(ref st.forced, 0);
			}
			TickLap(st, ref mark, TpLoop);
			st.tickPhaseMs[TpLoop] -= buildMs;
			st.tickPhaseMs[TpBuild] += buildMs;
			TickDone(st, t0);
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: which stamp parts moved since this entry was built (each counted).</summary>
		private static void CountRebuildCause(MapState st, Entry e, bool reload)
		{
			bool anyPart = false;
			for (int i = 0; i < StampParts; i++)
			{
				if (st.partsNow[i] != e.builtParts[i])
				{
					st.rebuildCauses[i]++;
					anyPart = true;
				}
			}
			if (reload)
			{
				st.rebuildCauses[CauseReload]++;
			}
			else if (!anyPart)
			{
				st.rebuildCauses[CauseNoPart]++;
			}
		}

		private static void TickLap(MapState st, ref long mark, int phase)
		{
			long t = System.Diagnostics.Stopwatch.GetTimestamp();
			st.tickPhaseMs[phase] += (t - mark) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
			mark = t;
		}

		/// <summary>One Tick's count and the slowest Tick's milliseconds (the phases are totals: tickPhaseMs).</summary>
		private static void TickDone(MapState st, long t0)
		{
			st.ticks++;
			double ms = (System.Diagnostics.Stopwatch.GetTimestamp() - t0) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
			if (ms > st.maxTickMs)
			{
				st.maxTickMs = ms;
			}
		}

		// ── the query ───────────────────────────────────────────────────────────────

		/// <summary>Does the depth rule apply to this query at all (RM_SuperdeepTrap.RelativeVeto's own gate), and at which climb
		/// limit? Pawnless: the person band.</summary>
		private static bool DepthApplies(Map map, Pawn p, out int k)
		{
			k = 0;
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (!RM_SuperdeepTrap.RuleOn || !RM_PocketGrid.Relative || eng == null || eng.ClimbCellCount == 0)
			{
				return false;
			}
			if (p != null && !RM_CliffMask.On && !RM_SuperdeepTrap.Captures(p))
			{
				return false;
			}
			k = p == null ? RM_PocketGrid.PersonBand : RM_PocketGrid.ClimbLimitOf(p);
			return RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount) != 0;
		}

		/// <summary>Its pather request carries the deep-water block (RM_SwimPathing.CustomizerFor): offset ≥ Blocked.</summary>
		public static bool NonSwimmer(Pawn p)
		{
			if (p == null || p.Flying || !Swimming.RM_SwimWater.On)
			{
				return false;
			}
			return RM_SwimMath.PlanOffset(Swimming.RM_Swim.ProfileOf(p).cls, p.RaceProps.Animal, Swimming.RM_SwimSettings.animalsAvoidDeepWater,
				Swimming.RM_SwimSettings.animalAvoidCost) >= RM_SwimMath.Blocked;
		}

		/// <summary>The class of this query (see RM_WallReachMath.ClassOf). <paramref name="walker"/>: vanilla StartPath's
		/// pawnless PassDoors check answered for the pawn starting the walk; its real walk is a ByPawn request with its job's
		/// bash flags (PathFinder.ResolveCanBash) and its own fence rule (TraverseParms.For(pawn)).</summary>
		public static int ClassOf(TraverseParms tp, Pawn walker, bool swimMap)
		{
			Pawn p = tp.pawn ?? walker;
			if (p == null)
			{
				return RM_WallReachMath.ClassOf(false, true, false, false, tp.fenceBlocked && !tp.canBashFences, false);
			}
			bool explicitPawn = tp.pawn != null;
			bool byPawn = explicitPawn ? tp.mode == TraverseMode.ByPawn : true;
			bool canBash = explicitPawn ? tp.canBashDoors : walker.CurJob != null && walker.CurJob.canBashDoors;
			bool fence = explicitPawn ? tp.fenceBlocked && !tp.canBashFences
				: walker.ShouldAvoidFences && !(walker.CurJob != null && walker.CurJob.canBashFences);
			bool playerShut = byPawn && !canBash && PlayerDoorsShutFor(p);
			bool nonSwimmer = swimMap && tp.mode != TraverseMode.NoPassClosedDoorsOrWater && NonSwimmer(p);
			return RM_WallReachMath.ClassOf(byPawn, p.CanOpenDoors, canBash, playerShut, fence, nonSwimmer);
		}

		/// <summary>Vanilla Building_Door.PawnCanOpen for a plain player door, answered for the pawn alone (the door-def roamer
		/// rule is left out: unknown here, so counted open). The player's own pawns, a pawn whose lord or mutation opens any
		/// door, and a released guest open them; otherwise the faction rule (GenAI.MachinesLike: hostiles, wild animals and
		/// prisoners are shut out).</summary>
		public static bool PlayerDoorsShutFor(Pawn p)
		{
			if (p == null || p.Faction == Faction.OfPlayer)
			{
				return false;
			}
			if (p.CanOpenAnyDoor || (p.guest != null && p.guest.Released))
			{
				return false;
			}
			return !GenAI.MachinesLike(Faction.OfPlayer, p);
		}

		/// <summary>The labelling for a query (built here only the first time; else the last build, stale or not, as the pocket
		/// grid does). Null when it does not apply.</summary>
		private static Entry EntryFor(Map map, Pawn p, TraverseParms tp, Pawn walker, out RM_PocketGrid g, out int k, out bool depthOn)
		{
			g = null;
			k = 0;
			depthOn = false;
			Pawn who = tp.pawn ?? walker;
			if (who != null && (who.Flying || RM_PocketGrid.FreePitTraveller(who)))
			{
				return null;   // flyers, jumpers, floaters: exempt (C6-C8), as the depth veto exempts them
			}
			depthOn = DepthApplies(map, who, out k);
			bool swimMap = Swimming.RM_SwimWater.On && Swimming.RM_SwimPathing.DeepCount(map) > 0;
			int cls = ClassOf(tp, walker, swimMap);
			if (!depthOn && (cls & RM_WallReachMath.NonSwimmer) == 0)
			{
				return null;   // no depth and no water this pawn sinks in: vanilla's regions already see walls and doors exactly
			}
			int band = 0;
			if (depthOn)
			{
				g = RM_PocketGrid.ForPawn(map, who);
				band = RM_PocketGridMath.BandFor(k, RM_PocketGrid.BandCount);
			}
			MapState st = StateOf(map);
			int now = Find.TickManager?.TicksGame ?? 0;
			var key = (g, band, cls);
			if (!st.entries.TryGetValue(key, out Entry e))
			{
				e = new Entry { grid = g, band = band, cls = cls };
				if (st.doorTick == int.MinValue / 2)
				{
					st.doorPrint = DoorPrint(map);
					st.doorTick = now;
				}
				// EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: deltas not yet judged may have moved a kind the snapshot holds;
				// a first build here (a query, on the cache owner: RM_PocketGrid.Owner) takes them as a change, the eager bump's rule, so it never labels
				// from a stale snapshot. Tick judges them later; one extra rebuild at worst.
				bool unjudged;
				lock (st.deltaLock)
				{
					unjudged = st.pendingDeltas.Count > 0 || st.deltaOverflow;
				}
				if (unjudged)
				{
					st.wallGenBy[WgUnjudged]++;
					Interlocked.Increment(ref st.wallGen);
				}
				Build(map, st, e, StampOf(map, st), null);
				st.entries[key] = e;
			}
			e.lastUsedTick = now;
			return e;
		}

		/// <summary>The ladder joins of this query (cell pairs), cached per (grid, pawn) for one tick and one ladder state.</summary>
		private static List<(int ladder, int other)> LadderJoinsFor(Map map, RM_PocketGrid g, Pawn p)
		{
			MapState st = StateOf(map);
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now != st.ladderTick || st.ladderVersion != RM_LadderUtility.StateVersion || st.ladderJoins.Count > 512)
			{
				st.ladderJoins.Clear();
				st.ladderTick = now;
				st.ladderVersion = RM_LadderUtility.StateVersion;
			}
			var key = (g, p == null ? -1 : p.thingIDNumber);
			if (!st.ladderJoins.TryGetValue(key, out List<(int ladder, int other)> joins))
			{
				joins = new List<(int ladder, int other)>();
				g.LadderJoins(p, joins);
				st.ladderJoins[key] = joins;
			}
			return joins;
		}

		/// <summary>The squares that finish a walk to dest (V10): the destination; for a touch, its occupied rect and the ring
		/// around it, minus the corners vanilla refuses (TouchPathEndModeUtility.IsAdjacentCornerAndNotAllowed, the rule A* and
		/// regions use). Their labels go into <paramref name="into"/>.</summary>
		private static void GoalLabels(Map map, RM_WallReachMath.Labels l, LocalTargetInfo dest, PathEndMode peMode, TraverseParms tp,
			List<int> into)
		{
			into.Clear();
			CellIndices ci = map.cellIndices;
			into.Add(l.At(ci.CellToIndex(dest.Cell)));
			if (peMode == PathEndMode.OnCell)
			{
				return;
			}
			CellRect rect = dest.HasThing ? dest.Thing.OccupiedRect() : CellRect.SingleCell(dest.Cell);
			GenAdj.GetAdjacentCorners(dest, out IntVec3 bl, out IntVec3 tl, out IntVec3 tr, out IntVec3 br);
			PathingContext pc = map.pathing.For(tp);
			foreach (IntVec3 c in rect.ExpandedBy(1))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				if (!rect.Contains(c) && TouchPathEndModeUtility.IsAdjacentCornerAndNotAllowed(c, bl, tl, tr, br, pc, dest.Thing))
				{
					continue;
				}
				into.Add(l.At(ci.CellToIndex(c)));
			}
		}

		/// <summary>The veto: vanilla (and the depth veto) said yes; is there NO single route in the wall-aware graph for this
		/// pawn's class? True = CanReach must say no. Never for PassAllDestroyable* (walls are passable to sappers: the wall
		/// half is skipped, the depth veto still runs, V12), nor when either end lies in a pocket too narrow to hold the pawn
		/// (it braces out; the masks hand it vanilla's array, so vanilla is right there).</summary>
		public static bool Veto(Map map, IntVec3 start, LocalTargetInfo dest, PathEndMode peMode, TraverseParms tp, Pawn walker)
		{
			return Judge(map, start, dest, peMode, tp, walker, true);
		}

		/// <summary>WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP (GPT review F1): the query reads and may build shared state (the
		/// entries, goalScratch, edgeScratch, the labels' spare arrays); a caller overlapping the cache owner gets vanilla's
		/// answer (no veto, the safe direction: the veto only ever turns a yes into a no).</summary>
		private static bool Judge(Map map, IntVec3 start, LocalTargetInfo dest, PathEndMode peMode, TraverseParms tp, Pawn walker, bool count)
		{
			if (!On || map == null || !RM_PocketGrid.EnterOwner(out bool nested))
			{
				return false;
			}
			try
			{
				return JudgeOwned(map, start, dest, peMode, tp, walker, count);
			}
			finally
			{
				RM_PocketGrid.ExitOwner(nested);
			}
		}

		private static bool JudgeOwned(Map map, IntVec3 start, LocalTargetInfo dest, PathEndMode peMode, TraverseParms tp, Pawn walker, bool count)
		{
			if (!On || map == null || !dest.IsValid || !start.InBounds(map) || !dest.Cell.InBounds(map))
			{
				return false;
			}
			if (tp.mode == TraverseMode.PassAllDestroyableThings || tp.mode == TraverseMode.PassAllDestroyablePlayerOwnedThings
				|| tp.mode == TraverseMode.PassAllDestroyableThingsNotWater)
			{
				return false;
			}
			Entry e = EntryFor(map, tp.pawn ?? walker, tp, walker, out RM_PocketGrid g, out int k, out bool depthOn);
			if (e?.labels == null || e.labels.label.Length != map.cellIndices.NumGridCells)
			{
				return false;
			}
			if (count)
			{
				Queries++;
			}
			Pawn who = tp.pawn ?? walker;
			if (depthOn)
			{
				int width = RM_SuperdeepTrap.RequiredWidth(who);
				int cs = g.ComponentOf(k, start), cd = g.ComponentOf(k, dest.Cell);
				if ((g.ComponentIsPocket(k, cs) && !g.WideEverywhere(k, cs, width)) || (g.ComponentIsPocket(k, cd) && !g.WideEverywhere(k, cd, width)))
				{
					return false;
				}
			}
			RM_WallReachMath.Labels l = e.labels;
			int sl = l.At(map.cellIndices.CellToIndex(start));
			GoalLabels(map, l, dest, peMode, tp, goalScratch);
			edgeScratch.Clear();
			if (depthOn && sl >= 0 && !goalScratch.Contains(sl))
			{
				List<(int ladder, int other)> joins = LadderJoinsFor(map, g, who);
				for (int i = 0; i < joins.Count; i++)
				{
					(int a, int b)? edge = RM_WallReachMath.LadderEdge(l, joins[i].ladder, joins[i].other, true);
					if (edge.HasValue)
					{
						edgeScratch.Add(edge.Value);
					}
				}
			}
			bool veto = RM_WallReachMath.Vetoed(sl, goalScratch, edgeScratch);
			if (veto && count)
			{
				Vetoes++;
			}
			return veto;
		}

		// ── the residual counter ──────────────────────────────────────────────────────

		public static int Fails, OutOfScope, Stale, Residual;
		private static readonly Dictionary<string, int> residualByKey = new Dictionary<string, int>();
		private static readonly Dictionary<string, int> residualByDoor = new Dictionary<string, int>();
		private static readonly List<Building_Door> doorScratch = new List<Building_Door>();

		private static void Add(Dictionary<string, int> d, string key)
		{
			if (!d.ContainsKey(key) && d.Count >= MaxKeys)
			{
				key = "other";
			}
			d.TryGetValue(key, out int n);
			d[key] = n + 1;
		}

		/// <summary>From the PatherFailed prefix, when the pather's own path request came back Found == false (StartPath's
		/// CanReach had said yes). Cheap: one veto read plus, for a residual only, one pass over the map's doors.</summary>
		internal static void RecordPathFailure(Pawn p, LocalTargetInfo dest, PathEndMode peMode)
		{
			if (p == null || !p.Spawned || !dest.IsValid || !RM_PocketGrid.EnterOwner(out bool nested))
			{
				return;
			}
			try
			{
				RecordPathFailureOwned(p, dest, peMode);
			}
			finally
			{
				// WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP (GPT review F3): the suspect doors hold their map; a static list
				// that kept them past this call rooted a removed map (and its weak-table grids) until the next residual.
				doorScratch.Clear();
				RM_PocketGrid.ExitOwner(nested);
			}
		}

		private static void RecordPathFailureOwned(Pawn p, LocalTargetInfo dest, PathEndMode peMode)
		{
			Fails++;
			Map map = p.Map;
			bool canBash = p.CurJob != null && p.CurJob.canBashDoors;
			bool canBashFences = p.CurJob != null && p.CurJob.canBashFences;
			TraverseParms tp = TraverseParms.For(p, Danger.Deadly, TraverseMode.ByPawn, canBash, false, canBashFences);
			Entry e = On ? EntryFor(map, p, tp, null, out _, out _, out _) : null;
			bool inScope = e != null;
			bool nowNo = inScope && Judge(map, p.Position, dest, peMode, tp, null, false);
			switch (RM_WallReachMath.Classify(inScope, nowNo))
			{
				case RM_WallReachMath.FailKind.OutOfScope:
					OutOfScope++;
					return;
				case RM_WallReachMath.FailKind.Stale:
					Stale++;
					return;
			}
			Residual++;
			string who = (p.Faction?.def?.defName ?? "none") + "/" + (p.RaceProps.Humanlike ? "humanlike" : p.RaceProps.Animal ? "animal" : "other")
				+ "/c" + e.cls;
			Add(residualByKey, who);
			// suspect doors: closed to THIS pawn (vanilla's own rule), counted open for its class
			doorScratch.Clear();
			foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Door))
			{
				if (t is Building_Door d && RM_WallReachMath.Passable(KindOfDoor(d), e.cls)
					&& ((!d.FreePassage && !d.CanPhysicallyPass(p) && !canBash) || (!canBash && d.IsForbiddenToPass(p))))
				{
					doorScratch.Add(d);
				}
			}
			doorScratch.Sort((a, b) => a.Position.DistanceToSquared(p.Position).CompareTo(b.Position.DistanceToSquared(p.Position)));
			int shown = Math.Min(4, doorScratch.Count);
			var doors = new List<string>(shown);
			for (int i = 0; i < shown; i++)
			{
				string dk = doorScratch[i].Position.x + "," + doorScratch[i].Position.z;
				Add(residualByDoor, dk);
				doors.Add(dk);
			}
			if (RM_WallReachMath.ShouldLog(Residual, LogFirst))
			{
				Log.Message("[FlowWorks] reach residual #" + Residual + ": " + p.LabelShort + " (" + who + ") at " + p.Position.x + ","
					+ p.Position.z + " -> " + dest.Cell.x + "," + dest.Cell.z + " " + peMode + "; CanReach said yes, A* found nothing; "
					+ "suspect doors [" + string.Join(" ", doors) + "]. " + Summary());
			}
		}

		private static string Top(Dictionary<string, int> d)
		{
			return string.Join(",", d.OrderByDescending(kv => kv.Value).Take(8).Select(kv => kv.Key + ":" + kv.Value));
		}

		private static string Summary()
		{
			return "RESIDUAL fails=" + Fails + " outOfScope=" + OutOfScope + " stale=" + Stale + " residual=" + Residual
				+ " byKey=[" + Top(residualByKey) + "] byDoor=[" + Top(residualByDoor) + "]";
		}

		// ── proof surface (jawa/static_call, one string arg) ───────────────────────────────

		/// <summary>One line of this map's wall-aware build cost (ProofPocketTiming's tail).</summary>
		public static string TimingLine(Map map)
		{
			if (map == null || !states.TryGetValue(map, out MapState st))
			{
				return "WALLREACH entries=0 builds=0";
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			int span = st.firstBuiltTick == int.MinValue ? 0 : now - st.firstBuiltTick;
			return "WALLREACH entries=" + st.entries.Count + " builds=" + st.builds + " overTicks=" + span
				+ " per1000=" + (span > 0 ? (st.builds * 1000.0 / span).ToString("0.00") : "-")
				+ " lastMs=" + st.lastMs.ToString("0.000") + " maxMs=" + st.maxMs.ToString("0.000")
				+ " meanMs=" + (st.builds > 0 ? (st.totalMs / st.builds).ToString("0.000") : "-")
				+ " steppedFrames=" + st.steppedFrames + " skipped=" + st.skipped
				+ " deltaBumps=" + st.deltaBumps + " deltaQuiet=" + st.deltaQuiet + " viewsReused=" + st.viewsReused
				+ " ownerRefused=" + RM_PocketGrid.OwnerRefused + DiagnosticTail(st);
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (r14 leads b and c): Tick's phase totals, the delta flushes, why
		/// entries rebuilt, who moved wallGen, and how many walkability notes were quiet (kind unchanged, no bump: r15 fix 1).</summary>
		private static string DiagnosticTail(MapState st)
		{
			var sb = new System.Text.StringBuilder();
			sb.Append(" ticks=").Append(st.ticks).Append(" maxTickMs=").Append(st.maxTickMs.ToString("0.000")).Append(" tickMs=");
			for (int i = 0; i < TickPhases; i++)
			{
				sb.Append(i > 0 ? "," : "").Append(TickPhaseNames[i]).Append(':').Append(st.tickPhaseMs[i].ToString("0.0"));
			}
			sb.Append(" flushes=").Append(st.flushes).Append(" flushCells=").Append(st.flushCells).Append(" flushMaxCells=")
				.Append(st.flushMaxCells).Append(" flushOverflows=").Append(st.flushOverflows).Append(" rebuildCauses=");
			for (int i = 0; i < RebuildCauses; i++)
			{
				sb.Append(i > 0 ? "," : "").Append(RebuildCauseNames[i]).Append(':').Append(st.rebuildCauses[i]);
			}
			sb.Append(" wallGenBy=");
			for (int i = 0; i < WgSources; i++)
			{
				sb.Append(i > 0 ? "," : "").Append(WallGenNames[i]).Append(':').Append(Volatile.Read(ref st.wallGenBy[i]));
			}
			sb.Append(" walkQuiet=").Append(Volatile.Read(ref st.walkQuiet)).Append(" walkMoved=").Append(Volatile.Read(ref st.walkMoved));
			return sb.ToString();
		}

		/// <summary>"" -> "WALLREACH on=b entries=N builds=N … queries=N vetoes=N | RESIDUAL fails=N outOfScope=N stale=N
		/// residual=N byKey=[faction/race/cCLS:n,…] byDoor=[x,z:n,…]" for the current map.</summary>
		public static string ProofReach(string arg)
		{
			Map map = Find.CurrentMap;
			return TimingLine(map).Replace("WALLREACH ", "WALLREACH on=" + On + " ") + " queries=" + Queries + " vetoes=" + Vetoes
				+ " | " + Summary();
		}

		/// <summary>"" -> zero every session counter (the residual included). "RESET ok=True".</summary>
		public static string ProofReachReset(string arg)
		{
			Queries = Vetoes = Fails = OutOfScope = Stale = Residual = 0;
			residualByKey.Clear();
			residualByDoor.Clear();
			doorScratch.Clear();
			return "RESET ok=True";
		}

		/// <summary>"" -> rebuild every stale labelling of the current map now (staging: a proof that cannot wait 60 ticks).
		/// "FORCE builds=N".</summary>
		public static string ProofReachForce(string arg)
		{
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return "REFUSED: no current map";
			}
			Bump(map);
			Tick(map, true);
			return "FORCE builds=" + (states.TryGetValue(map, out MapState st) ? st.builds : 0);
		}

		/// <summary>"pawnId;x,z[;touch]" -> "REACHPAIR canReach=T|F found=T|F veto=T|F inScope=T|F cls=N band=K": canReach is
		/// the pawn's full CanReach (vanilla + every postfix), found is A* for the same walk as its pather would ask it (ByPawn,
		/// the pit and swim offset grids, RM_Patch_PathFollower_PitRoute's recipe), veto is this map's answer alone.</summary>
		public static string ProofReachPair(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(';');
			if (map == null || a.Length < 2 || !int.TryParse(a[0], out int id))
			{
				return "REFUSED: arg must be pawnId;x,z[;touch]";
			}
			string[] xz = a[1].Split(',');
			if (xz.Length != 2 || !int.TryParse(xz[0], out int x) || !int.TryParse(xz[1], out int z))
			{
				return "REFUSED: bad cell";
			}
			var dest = new IntVec3(x, 0, z);
			Pawn p = map.mapPawns.AllPawnsSpawned.FirstOrDefault(q => q.thingIDNumber == id);
			if (p == null || !dest.InBounds(map))
			{
				return "REFUSED: no such pawn or cell";
			}
			PathEndMode pe = a.Length > 2 && a[2] == "touch" ? PathEndMode.Touch : PathEndMode.OnCell;
			bool canReach = p.CanReach(dest, pe, Danger.Deadly);
			bool canBash = p.CurJob != null && p.CurJob.canBashDoors;
			TraverseParms tp = TraverseParms.For(p, Danger.Deadly, TraverseMode.ByPawn, canBash, false, p.CurJob != null && p.CurJob.canBashFences);
			bool veto = Judge(map, p.Position, dest, pe, tp, null, false);
			Entry e = On ? EntryFor(map, p, tp, null, out _, out int band, out _) : null;
			bool found;
			LocalTargetInfo target = dest;
			PathEndMode mode = pe;
			bool pit = RM_PitPathing.TryPlan(p, p.Position, dest, pe, out RM_PitTrapMath.PitRoute route, out PathRequest.IPathGridCustomizer custom);
			PathRequest.IPathGridCustomizer swim = Swimming.RM_SwimPathing.CustomizerFor(p);
			PathRequest.IPathGridCustomizer both = pit || swim != null ? Swimming.RM_SwimPathing.Combine(map, pit ? custom : null, swim) : null;
			if (pit && route.leg != RM_PitTrapMath.PitLeg.AvoidPits && route.leg != RM_PitTrapMath.PitLeg.StayInPit
				&& route.leg != RM_PitTrapMath.PitLeg.ClosedLadders)
			{
				target = new IntVec3(route.x, 0, route.z);
				mode = PathEndMode.OnCell;
			}
			using (PawnPath path = map.pathFinder.FindPathNow(p.Position, target, tp, PathFinderCostTuning.For(p), mode, both))
			{
				found = path != null && path.Found;
			}
			return "REACHPAIR canReach=" + canReach + " found=" + found + " veto=" + veto + " inScope=" + (e != null)
				+ " cls=" + (e?.cls ?? -1) + " band=" + (e?.band ?? 0) + " agree=" + (canReach == found);
		}
	}

	/// <summary>REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE: the wall-aware veto, after vanilla and the depth veto (low priority: they
	/// run first, so a no they already gave is never re-judged). Turns a yes into a no only.</summary>
	[HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach),
		new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(PathEndMode), typeof(TraverseParms) })]
	[RimMandrake.Shared.PatchFeature("Reachability sees walls and cliffs together", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_Reachability_WallReach
	{
		[HarmonyPostfix]
		[HarmonyPriority(Priority.Low)]
		public static void Postfix(IntVec3 start, LocalTargetInfo dest, PathEndMode peMode, TraverseParms traverseParams,
			ref bool __result, Map ___map)
		{
			if (!__result || !RM_WallReach.On)
			{
				return;
			}
			Pawn walker = traverseParams.pawn == null ? RM_Patch_PathFollower_ReachWalker.WalkerAt(___map, start) : null;
			if (RM_WallReach.Veto(___map, start, dest, peMode, traverseParams, walker))
			{
				__result = false;
			}
		}
	}

	/// <summary>REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE, the owner's measurement: vanilla PatherTick calls PatherFailed when its
	/// path request came back Found == false; StartPath's CanReach had said yes. Counted (and classified) before the pather
	/// clears the request. Off with the setting.</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "PatherFailed")]
	[RimMandrake.Shared.PatchFeature("Reachability sees walls and cliffs together", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_PathFollower_ReachResidual
	{
		[HarmonyPrefix]
		public static void Prefix(Pawn_PathFollower __instance, Pawn ___pawn, LocalTargetInfo ___destination, PathEndMode ___peMode)
		{
			PathRequest req = __instance.curPathRequest;
			if (req == null || req.Found != false || !RM_WallReach.On)
			{
				return;
			}
			try
			{
				RM_WallReach.RecordPathFailure(___pawn, ___destination, ___peMode);
			}
			catch (Exception ex)
			{
				Log.ErrorOnce("[FlowWorks] reach residual counter failed: " + ex.Message, 0x52455344);
			}
		}
	}

	/// <summary>REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE: the walkability generation, from vanilla's own connectivity updates
	/// (inside PathFinderMapData.GatherData, the moment the pathfinder's walls move). Own patches, not RM_CliffMask's, so the
	/// reach map stays current with the pit features off (the non-swimmer half).</summary>
	[HarmonyPatch(typeof(ConnectivitySource), nameof(ConnectivitySource.UpdateIncrementally))]
	[RimMandrake.Shared.PatchFeature("Reachability sees walls and cliffs together", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_ConnectivitySource_WallReach
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map, List<IntVec3> cellDeltas)
		{
			RM_WallReach.NoteConnectivity(___map, cellDeltas, false);
		}
	}

	/// <summary>REACH_WINCH_FIX_GHOST_ROAD_RETURNS: walkability changed on a square, synchronously (PathGrid ->
	/// RegionDirtyer). GatherData's deltas come only when some pawn paths that tick; this one comes always.</summary>
	[HarmonyPatch(typeof(RegionDirtyer), "Notify_WalkabilityChanged")]
	[RimMandrake.Shared.PatchFeature("Reachability sees walls and cliffs together", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_RegionDirtyer_WallReach
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map, IntVec3 c, bool newWalkability)
		{
			RM_WallReach.NoteWalkability(___map, c, newWalkability);
		}
	}

	/// <summary>REACH_WINCH_FIX_GHOST_ROAD_RETURNS: a door or fence spawned (walkability unchanged, kind changed).</summary>
	[HarmonyPatch(typeof(RegionDirtyer), "Notify_ThingAffectingRegionsSpawned")]
	[RimMandrake.Shared.PatchFeature("Reachability sees walls and cliffs together", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_RegionDirtyer_WallReachSpawned
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map, Thing b)
		{
			RM_WallReach.NoteBarrier(___map, b, false);
		}
	}

	/// <summary>REACH_WINCH_FIX_GHOST_ROAD_RETURNS: a door or fence despawned (a way opened: forced).</summary>
	[HarmonyPatch(typeof(RegionDirtyer), "Notify_ThingAffectingRegionsDespawned")]
	[RimMandrake.Shared.PatchFeature("Reachability sees walls and cliffs together", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_RegionDirtyer_WallReachDespawned
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map, Thing b)
		{
			RM_WallReach.NoteBarrier(___map, b, true);
		}
	}

	[HarmonyPatch(typeof(ConnectivitySource), nameof(ConnectivitySource.ComputeAll))]
	[RimMandrake.Shared.PatchFeature("Reachability sees walls and cliffs together", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_ConnectivitySource_WallReachAll
	{
		[HarmonyPostfix]
		public static void Postfix(Map ___map)
		{
			RM_WallReach.NoteConnectivity(___map, null, true);
		}
	}
}
