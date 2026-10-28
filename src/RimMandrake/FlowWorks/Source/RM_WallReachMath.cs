using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE — the wall-aware reach map's arithmetic (owner 2026-10-21, by card: "3: the wall-aware
	/// reach map, kept per pawn class"; spec Transient/pile_2026-10-21/reachability_review.md §4). Verse-free so Source/SelfTest/
	/// compiles THIS production file.
	///
	/// Why it exists: CanReach was (vanilla regions: walls, no depth) AND (the pocket grid: depth, no walls). Each half could say
	/// yes about a DIFFERENT route, so a wall plus a trench that cut every route only together read "reachable" while A* found
	/// nothing, and vanilla jobs looped (offer, StartPath, PatherFailed, offer again). This labelling sees walls, doors, fences,
	/// deep water AND the climb step rule in ONE graph, per climb band and per coarse pawn class, and is read only by the
	/// CanReach veto (RM_WallReach), which can only turn a yes into a no. Pockets, trapping and pit rooms stay on the depth-only
	/// labels (ruling 1, PIT_SUPERDEEP_COLLAPSE_1).
	///
	/// Every rule here must keep the labels AT LEAST as connected as the pathfinder's graph for a pawn of the class (a wrongly
	/// closed square is a false "no", which is worse than the residual false "yes" the veto exists to shrink). Where a door's
	/// state is transient or pawn-specific, the square counts as OPEN.
	/// </summary>
	public static class RM_WallReachMath
	{
		// ── square kinds (one byte per square, from the path grid and the edifice) ──────────────────────
		public const byte Open = 0;
		/// <summary>Impassable in the path grid (a wall, a rock, an impassable building or terrain).</summary>
		public const byte Wall = 1;
		/// <summary>A door that is not the player's (or has no faction), not held open.</summary>
		public const byte Door = 2;
		/// <summary>A player-faction door that checks faction (not a hackable door), not held open.</summary>
		public const byte PlayerDoor = 3;
		/// <summary>A door held open: free passage for everyone (vanilla Building_Door.FreePassage once open).</summary>
		public const byte HeldDoor = 4;
		/// <summary>A drawbridge gate closed to EVERYONE (map locked and not held, or its leaf off its seat:
		/// Building_DrawbridgeGate.PawnCanOpen / RM_DrawbridgeMath.GateOpensFor false). Only a door-basher passes.</summary>
		public const byte ShutGate = 5;
		public const byte Fence = 6;
		/// <summary>Deep swim water (RM_SwimWater.IsDeepSwimCell): walkable to vanilla, closed to non-swimmers by an A* offset.</summary>
		public const byte DeepWater = 7;

		// ── pawn class bits ─────────────────────────────────────────────────────────────────
		/// <summary>Cannot open doors and does not bash them (animals on a ByPawn walk): every door not held open is closed.</summary>
		public const int NonOpener = 1;
		/// <summary>Does not bash doors on a ByPawn walk: a gate closed to everyone is closed to it.</summary>
		public const int GateShut = 2;
		/// <summary>Cannot open the player's doors (vanilla Building_Door.PawnCanOpen's faction rule: hostiles, wild animals,
		/// prisoners — GenAI.MachinesLike) and does not bash doors on a ByPawn walk: the player's doors not held open are closed.</summary>
		public const int PlayerDoorsShut = 4;
		/// <summary>Fence-blocked (a roamer) and does not bash fences.</summary>
		public const int FenceBlocked = 8;
		/// <summary>Its A* offset grid blocks deep water (RM_SwimMath.PlanOffset ≥ Blocked).</summary>
		public const int NonSwimmer = 16;
		public const int ClassCount = 32;

		/// <summary>The class of one reachability query. <paramref name="byPawnDoors"/>: the walk the pathfinder will plan is a
		/// ByPawn one (a ByPawn query with a pawn, or vanilla StartPath's pawnless PassDoors check answered for its walker). Only
		/// then are doors judged per pawn: PassDoors with a pawn prices a closed door at 150 (passable), NoPassClosedDoors is
		/// already closed by vanilla's regions, so both keep every door open here.</summary>
		public static int ClassOf(bool byPawnDoors, bool canOpenDoors, bool canBashDoors, bool playerDoorsShut, bool fenceBlocked,
			bool nonSwimmer)
		{
			int c = 0;
			if (byPawnDoors && !canBashDoors)
			{
				c |= GateShut;
				if (!canOpenDoors)
				{
					c |= NonOpener;
				}
				if (playerDoorsShut || !canOpenDoors)
				{
					c |= PlayerDoorsShut;
				}
			}
			if (fenceBlocked)
			{
				c |= FenceBlocked;
			}
			if (nonSwimmer)
			{
				c |= NonSwimmer;
			}
			return c;
		}

		/// <summary>May a pawn of class <paramref name="cls"/> stand on and walk through a square of this kind?</summary>
		public static bool Passable(byte kind, int cls)
		{
			switch (kind)
			{
				case Open:
				case HeldDoor:
					return true;
				case Wall:
					return false;
				case Door:
					return (cls & NonOpener) == 0;
				case PlayerDoor:
					return (cls & (NonOpener | PlayerDoorsShut)) == 0;
				case ShutGate:
					return (cls & GateShut) == 0;
				case Fence:
					return (cls & FenceBlocked) == 0;
				case DeepWater:
					return (cls & NonSwimmer) == 0;
				default:
					return true;   // an unknown kind is never a reason to say no
			}
		}

		/// <summary>One labelling. label[i] = component id, or -1 for a square this class cannot stand on.</summary>
		public sealed class Labels
		{
			public int[] label;
			public int count;
			public int width;
			public int height;
			public int k;
			public int cls;

			public int At(int i)
			{
				return i >= 0 && i < label.Length ? label[i] : -1;
			}

			public int At(int x, int z)
			{
				return x >= 0 && z >= 0 && x < width && z < height ? label[z * width + x] : -1;
			}
		}

		/// <summary>Label every square for climb band <paramref name="k"/> and class <paramref name="cls"/>. Two N/S/E/W
		/// neighbours join when both are passable for the class and (depth given) the step between them is allowed for K
		/// (RM_PitTrapMath.StepAllowed, a ramp joining any pair it spans). depth null: walls only (no dug square on the map, or a
		/// pawn the depth rule does not apply to). Four-neighbour components are exact for the pathfinder's eight-way walk: a
		/// diagonal is never cut past an impassable corner (vanilla) nor past a cliff corner (RM_PitTrapMath.DiagonalAllowed holds
		/// all four squares within K), so every diagonal step has a cardinal detour inside the same component.
		/// reuse, optional (EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES): an int[width × height] no reader holds any more, overwritten
		/// whole and returned as the label array; the BFS queue is per-thread scratch (RM_PocketGridMath.QueueScratch).</summary>
		public static Labels Label(byte[] kind, byte[] depth, int width, int height, int k, int cls, Func<int, int, bool> rampJoins = null,
			int[] reuse = null)
		{
			if (kind == null || width <= 0 || height <= 0 || kind.Length < width * height || (depth != null && depth.Length < width * height))
			{
				throw new ArgumentException("grids do not match " + width + "x" + height);
			}
			int n = width * height;
			int[] lab = reuse != null && reuse.Length == n ? reuse : new int[n];
			for (int i = 0; i < n; i++)
			{
				lab[i] = Passable(kind[i], cls) ? int.MaxValue : -1;   // MaxValue = passable, not yet labelled
			}
			int[] queue = RM_PocketGridMath.QueueScratch(n);
			int count = 0;
			for (int seed = 0; seed < n; seed++)
			{
				if (lab[seed] != int.MaxValue)
				{
					continue;
				}
				int id = count++;
				int head = 0, tail = 0;
				queue[tail++] = seed;
				lab[seed] = id;
				while (head < tail)
				{
					int c = queue[head++];
					int z = c / width, x = c - z * width;
					int d = depth == null ? 0 : depth[c];
					for (int dir = 0; dir < 4; dir++)
					{
						int ni;
						switch (dir)
						{
							case 0: if (z + 1 >= height) { continue; } ni = c + width; break;
							case 1: if (x + 1 >= width) { continue; } ni = c + 1; break;
							case 2: if (z == 0) { continue; } ni = c - width; break;
							default: if (x == 0) { continue; } ni = c - 1; break;
						}
						if (lab[ni] != int.MaxValue)
						{
							continue;
						}
						// A ramp only adds a join (StepAllowed is true whenever rampJoins is): read the pairs only for a refused step.
						if (depth != null && !RM_PitTrapMath.StepAllowed(d, depth[ni], k)
							&& !(rampJoins != null && (rampJoins(c, ni) || rampJoins(ni, c))))
						{
							continue;
						}
						lab[ni] = id;
						queue[tail++] = ni;
					}
				}
			}
			return new Labels { label = lab, count = count, width = width, height = height, k = k, cls = cls };
		}

		/// <summary>The veto's decision on the wall-aware labels: true = no single route exists, so CanReach must say no.
		/// <paramref name="start"/>: the start square's label (-1: it stands where its class cannot, e.g. mid-door for an animal
		/// or on an impassable square: never vetoed, vanilla decides). <paramref name="goals"/>: the labels of the squares that
		/// finish the walk (the destination itself, plus for a touch the allowed neighbours); none passable = never vetoed (an
		/// unknown is not a no). A goal in the start's component, or joined to it through ladders this query may use (each edge
		/// both ways), clears the veto.</summary>
		public static bool Vetoed(int start, IReadOnlyList<int> goals, IReadOnlyList<(int a, int b)> ladderEdges)
		{
			if (start < 0 || goals == null)
			{
				return false;
			}
			bool any = false;
			for (int i = 0; i < goals.Count; i++)
			{
				if (goals[i] < 0)
				{
					continue;
				}
				any = true;
				if (goals[i] == start)
				{
					return false;
				}
			}
			if (!any)
			{
				return false;
			}
			if (ladderEdges == null || ladderEdges.Count == 0)
			{
				return true;
			}
			for (int i = 0; i < goals.Count; i++)
			{
				if (goals[i] >= 0 && RM_PocketGridMath.JoinedByLadders(start, goals[i], ladderEdges))
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>A ladder's edge on the wall-aware labels: the components of its own square and of the square across the wall
		/// it hangs on, when the ladder joins them for this query (the pocket grid's structural decision, RM_PocketGrid.LadderJoins)
		/// and both squares are passable for the class. Null when it adds nothing.</summary>
		public static (int a, int b)? LadderEdge(Labels l, int ladderIndex, int otherIndex, bool joins)
		{
			if (!joins || l == null)
			{
				return null;
			}
			int a = l.At(ladderIndex), b = l.At(otherIndex);
			if (a < 0 || b < 0 || a == b)
			{
				return null;
			}
			return (a, b);
		}

		// ── the residual (owner 2026-10-21: "let's look carefully (make a note) to measure how often that bug case occurs") ──

		/// <summary>What one pather failure (vanilla Pawn_PathFollower: CanReach said yes at StartPath, then the path request came
		/// back Found == false) was. OutOfScope: no dug square and no swim water a non-swimmer meets, or a pawn the veto never
		/// judges (flyers, sappers), or the setting off; the bug class this item is about cannot be the cause. Stale: the reach map
		/// says NO now, so it said yes only because it had not caught up (≤ 60 ticks; latency, not the residual). Residual: the
		/// reach map still says yes and A* found nothing: the case option 3 leaves (a door shut to this one pawn plus a cliff,
		/// the corner of a touch, a wall the labels never saw...).</summary>
		public enum FailKind { OutOfScope, Stale, Residual }

		public static FailKind Classify(bool inScope, bool vetoNowSaysNo)
		{
			if (!inScope)
			{
				return FailKind.OutOfScope;
			}
			return vetoNowSaysNo ? FailKind.Stale : FailKind.Residual;
		}

		/// <summary>REACH_WINCH_FIX_GHOST_ROAD_RETURNS: a square's walkability changed (RegionDirtyer.Notify_WalkabilityChanged, at
		/// once, on the main thread). A square the last kinds snapshot read as a WALL that is walkable now is a breach (more
		/// connected than the labels): rebuild unthrottled. Anything else only makes the labels stale (they over-connect, so the
		/// throttle can only delay a veto, never invent one).</summary>
		public static bool WalkabilityBreach(byte lastKind, bool nowWalkable)
		{
			return lastKind == Wall && nowWalkable;
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES (r15 fix 1): does a walkability note move the labels' input? The labels
		/// read kinds[] only, so a note whose square's kind now equals what the published snapshot holds cannot change them
		/// (live r15: 90,790 of 90,800 wall-generation bumps were the pocket grid's own pit-room notifies, walkability unchanged,
		/// each one staling every labelling). True: no snapshot, the square is out of its range, or its kind moved.</summary>
		public static bool WalkabilityMovesKind(byte[] snapshot, int idx, byte kindNow)
		{
			return snapshot == null || idx < 0 || idx >= snapshot.Length || snapshot[idx] != kindNow;
		}

		/// <summary>Bounded logging: the first <paramref name="firstN"/> residuals are logged one by one, then only a summary at
		/// each power of two (2·firstN, 4·firstN, …), so a looping pawn can never spam the log.</summary>
		public static bool ShouldLog(int nth, int firstN)
		{
			if (nth <= 0)
			{
				return false;
			}
			if (nth <= firstN)
			{
				return true;
			}
			if (firstN <= 0 || nth % firstN != 0)
			{
				return false;
			}
			int q = nth / firstN;
			return (q & (q - 1)) == 0;
		}

		/// <summary>WALL_REACH_TUNE_REBUILDS_TENFOLD: may this paused frame rebuild unthrottled? Only when the clock is stopped
		/// (its tick equals the previous paused frame's) AND the labels' stamp moved since that frame: a write made while
		/// paused (a dev tool, bridge staging). Time stepped under the pause flag (the bridge's safe_advance, the dev step
		/// button: DoSingleTick inside a paused frame) moves the tick, and an idle frame between two step bursts moves neither
		/// tick nor stamp (the burst's own changes were seen by the frame that ran it): both stay throttled. Before this, every
		/// paused frame rebuilt every stale labelling: ~1 build per tick on the 2026-10-22 residual soak (8 labellings, ~8
		/// ticks a frame) against the throttle's 8 per 60 ticks.</summary>
		public static bool PausedUnthrottled(int now, int lastPausedFrameTick, long stamp, long lastPausedFrameStamp)
		{
			return now == lastPausedFrameTick && stamp != lastPausedFrameStamp;
		}

		/// <summary>Should a stale labelling be rebuilt now? Throttled to once per <paramref name="minTicks"/> unless forced (a
		/// breach, a drawbridge toggle, a gate lock or hold, a swim terrain change) or paused (no tick will ever pass).</summary>
		public static bool RebuildDue(bool stale, bool forced, bool paused, int now, int builtTick, int minTicks)
		{
			if (!stale)
			{
				return false;
			}
			return forced || paused || now - builtTick >= minTicks;
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: the most queued connectivity deltas checked one by one; past this
		/// the labels are simply marked stale (the old behaviour), so the per-tick check stays bounded.</summary>
		public const int MaxQueuedDeltas = 4096;

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: do these connectivity deltas move the labels' input? Vanilla's
		/// PathFinderMapData.GatherData hands ConnectivitySource EVERY cell delta of the tick (a thing spawned or despawned, a
		/// reservation, a haul en route, a terrain or path-cost change), so nearly every tick a pawn paths carried one, and
		/// stamping each of them stale rebuilt every labelling at the throttle ceiling (~100 whole-map builds per 1000 ticks on a
		/// quiet map, 2026-10-22 soak). The labels read kinds[] only, so a delta whose square's kind is what the snapshot
		/// already holds cannot change them. True: some delta square's kind differs (or there is no snapshot, or a delta is out
		/// of range, or the queue overflowed); false: none does (an empty list included).</summary>
		public static bool DeltaMovesKinds(byte[] snapshot, IReadOnlyList<int> deltas, Func<int, byte> kindNow, bool overflowed)
		{
			if (overflowed || snapshot == null)
			{
				return overflowed || (deltas != null && deltas.Count > 0);
			}
			if (deltas == null)
			{
				return false;
			}
			for (int j = 0; j < deltas.Count; j++)
			{
				int i = deltas[j];
				if (i < 0 || i >= snapshot.Length || kindNow(i) != snapshot[i])
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: byte-identical inputs (both null counts as identical). Labelling is
		/// a pure function of (kinds, depth, ramps, band, class), so identical inputs give identical labels and a rebuild may
		/// keep the old ones.</summary>
		public static bool SameBytes(byte[] a, byte[] b)
		{
			if (ReferenceEquals(a, b))
			{
				return true;
			}
			if (a == null || b == null || a.Length != b.Length)
			{
				return false;
			}
			for (int i = 0; i < a.Length; i++)
			{
				if (a[i] != b[i])
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES: the same ramp pairs (both null or empty counts as identical).</summary>
		public static bool SameRamps(IReadOnlyDictionary<int, int> a, IReadOnlyDictionary<int, int> b)
		{
			int na = a?.Count ?? 0, nb = b?.Count ?? 0;
			if (na != nb)
			{
				return false;
			}
			if (na == 0)
			{
				return true;
			}
			foreach (KeyValuePair<int, int> kv in a)
			{
				if (!b.TryGetValue(kv.Key, out int v) || v != kv.Value)
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>EXCAVATION_COMPONENT_DIAGNOSE_TICK_SPIKES / WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP: ramp pairs as the flood's
		/// join test (null with none). RM_PocketGrid.RampJoinsOf forwards here.</summary>
		public static Func<int, int, bool> RampJoins(Dictionary<int, int> ramps)
		{
			return ramps == null || ramps.Count == 0 ? null
				: (Func<int, int, bool>)((a, b) => ramps.TryGetValue(a, out int t) && t == b);
		}

		/// <summary>WALLREACH_RELABEL_TAME_SLICED_BUFFERED (design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md §4 #8):
		/// one labelling built a slice at a time, so a whole-map relabel never has to fit in one tick. It is <see cref="Label"/>'s
		/// flood made resumable: the same passable marking, the same seed order and the same breadth-first order, so a job run to
		/// the end in any slicing gives the label array Label gives (WallReach_sliced_equals_one_shot drives that over random
		/// grids, edits and budgets). Its inputs are held by reference and must not be written for the job's life: RM_WallReach
		/// passes the published kinds (never written after publication), the pocket grid's built depth view (never written after
		/// a build) and that build's ramp pairs. The label array and the queue are the job's alone until it ends; nothing reads
		/// the half-built array (<see cref="LabelSlot"/> publishes it only when <see cref="Done"/>).
		/// One unit of work: one square marked, one seed square scanned, or one square popped and its four neighbours tried.</summary>
		public sealed class LabelJob
		{
			public readonly byte[] kinds;
			public readonly byte[] depth;
			public readonly Dictionary<int, int> ramps;
			public readonly int width, height, band, cls;
			private readonly Func<int, int, bool> rampJoins;
			private readonly int[] lab;
			private readonly int[] queue;
			private readonly int n;
			private int phase;   // 0: marking passable squares, 1: flooding, 2: done
			private int cursor, head, tail, count;
			/// <summary>Units spent so far (diagnostic; the whole job costs about 3 x width x height).</summary>
			public long work;
			public int steps;

			/// <summary><paramref name="reuse"/>: an int[width × height] no reader holds (overwritten whole), else a new one.
			/// <paramref name="queue"/>: at least width × height, owned by this job until it is done or dropped.</summary>
			public LabelJob(byte[] kinds, byte[] depth, Dictionary<int, int> ramps, int width, int height, int band, int cls, int[] reuse,
				int[] queue)
			{
				if (kinds == null || width <= 0 || height <= 0 || kinds.Length < width * height || (depth != null && depth.Length < width * height))
				{
					throw new ArgumentException("grids do not match " + width + "x" + height);
				}
				n = width * height;
				if (queue == null || queue.Length < n)
				{
					throw new ArgumentException("queue shorter than the map");
				}
				this.kinds = kinds;
				this.depth = depth;
				this.ramps = ramps;
				this.width = width;
				this.height = height;
				this.band = band;
				this.cls = cls;
				rampJoins = RampJoins(ramps);
				lab = reuse != null && reuse.Length == n ? reuse : new int[n];
				this.queue = queue;
			}

			public bool Done => phase == 2;

			/// <summary>The finished labelling (null until <see cref="Done"/>).</summary>
			public Labels Result => phase == 2 ? new Labels { label = lab, count = count, width = width, height = height, k = band, cls = cls } : null;

			/// <summary>The array this job writes, for a caller dropping it unfinished (it may be reused: no reader ever held it).</summary>
			public int[] Buffer => lab;

			/// <summary>Do at most <paramref name="budget"/> units (at least one while not done). Returns the units done.</summary>
			public int Step(int budget)
			{
				if (budget < 1)
				{
					budget = 1;
				}
				steps++;
				int spent = 0;
				while (spent < budget && phase != 2)
				{
					int room = budget - spent;
					if (phase == 0)
					{
						int end = room >= n - cursor ? n : cursor + room;
						for (int i = cursor; i < end; i++)
						{
							lab[i] = Passable(kinds[i], cls) ? int.MaxValue : -1;   // MaxValue = passable, not yet labelled
						}
						spent += end - cursor;
						cursor = end;
						if (cursor == n)
						{
							phase = 1;
							cursor = 0;
							head = tail = 0;
						}
						continue;
					}
					if (head < tail)
					{
						int c = queue[head++];
						int id = lab[c];
						int z = c / width, x = c - z * width;
						int d = depth == null ? 0 : depth[c];
						for (int dir = 0; dir < 4; dir++)
						{
							int ni;
							switch (dir)
							{
								case 0: if (z + 1 >= height) { continue; } ni = c + width; break;
								case 1: if (x + 1 >= width) { continue; } ni = c + 1; break;
								case 2: if (z == 0) { continue; } ni = c - width; break;
								default: if (x == 0) { continue; } ni = c - 1; break;
							}
							if (lab[ni] != int.MaxValue)
							{
								continue;
							}
							if (depth != null && !RM_PitTrapMath.StepAllowed(d, depth[ni], band)
								&& !(rampJoins != null && (rampJoins(c, ni) || rampJoins(ni, c))))
							{
								continue;
							}
							lab[ni] = id;
							queue[tail++] = ni;
						}
						spent++;
						if (head == tail && cursor >= n)
						{
							phase = 2;   // the last component is finished and no square is left to scan: done on this unit
						}
						continue;
					}
					// the component in hand is finished: scan for the next seed, as Label's seed loop does
					if (cursor >= n)
					{
						phase = 2;
						break;
					}
					if (lab[cursor] == int.MaxValue)
					{
						head = tail = 0;
						queue[tail++] = cursor;
						lab[cursor] = count++;
					}
					cursor++;
					spent++;
					if (head == tail && cursor >= n)
					{
						phase = 2;
					}
				}
				work += spent;
				return spent;
			}
		}

		/// <summary>WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP (GPT review F4): one (grid, band, class) labelling's buffers and
		/// skip rule, as RM_WallReach.Build runs them (Verse-free so the selftest drives the production policy, not a copy).
		/// THE CONTRACT: <see cref="labels"/> is published by reference; a holder may keep it across ONE later flood (the
		/// labelling before it is the one whose array the flood overwrites) and must let go before the second. RM_WallReach's
		/// readers hold it only inside one call, under the owner gate (<see cref="OwnerGate"/>), so none ever holds two.
		/// Identical inputs (kinds by reference, depth and ramps by content, the same width and height) keep the labels: the
		/// labelling is a pure function of them.
		/// WALLREACH_RELABEL_TAME_SLICED_BUFFERED: the double buffer. <see cref="Begin"/> starts a <see cref="LabelJob"/> in the
		/// spare array; <see cref="Advance"/> runs it a slice at a time while <see cref="labels"/> (the last finished labelling)
		/// keeps serving; the finished job is published in one assignment. A reader therefore sees the old labels whole or the
		/// new labels whole, never a half-built array. <see cref="Rebuild"/> is Begin plus one unbounded Advance.</summary>
		public sealed class LabelSlot
		{
			public Labels labels;
			public Labels spare;
			public byte[] builtKinds;
			public byte[] builtDepth;
			public Dictionary<int, int> builtRamps;
			public int builtWidth = -1, builtHeight = -1;
			public int floods, skips, dropped;
			/// <summary>The labelling being built (null: none in flight).</summary>
			public LabelJob job;
			private int[] spareArray;   // a dropped job's array, reused by the next job

			/// <summary>Do (kinds, depth, ramps) equal the inputs of the published labelling?</summary>
			public bool SameAsPublished(byte[] kinds, byte[] depth, Dictionary<int, int> ramps, int width, int height)
			{
				return labels != null && ReferenceEquals(kinds, builtKinds) && width == builtWidth && height == builtHeight
					&& SameBytes(depth, builtDepth) && SameRamps(ramps, builtRamps);
			}

			/// <summary>Start labelling (kinds, depth, ramps) for (band, cls), dropping any job in flight. False (no job): the
			/// inputs are the published labelling's, which stays (a skip). <paramref name="queue"/>: the job's own queue
			/// (≥ width × height), not shared with another job that may still be mid-flood.</summary>
			public bool Begin(byte[] kinds, byte[] depth, Dictionary<int, int> ramps, int width, int height, int band, int cls, int[] queue)
			{
				Drop();
				if (SameAsPublished(kinds, depth, ramps, width, height))
				{
					skips++;
					return false;
				}
				int[] reuse = spareArray ?? spare?.label;
				spareArray = null;
				spare = null;
				job = new LabelJob(kinds, depth, ramps, width, height, band, cls, reuse, queue);
				return true;
			}

			/// <summary>Run the job in flight for at most <paramref name="budget"/> units. True when it finished in this call
			/// and was published (the labels before it become the spare). <paramref name="spent"/>: units done.</summary>
			public bool Advance(int budget, out int spent)
			{
				spent = 0;
				if (job == null)
				{
					return false;
				}
				spent = job.Step(budget);
				if (!job.Done)
				{
					return false;
				}
				Labels built = job.Result;
				builtKinds = job.kinds;
				builtDepth = job.depth;
				builtRamps = job.ramps;
				builtWidth = job.width;
				builtHeight = job.height;
				job = null;
				spare = labels;
				labels = built;
				floods++;
				return true;
			}

			/// <summary>Drop the job in flight unfinished (its array, never published, is kept for the next job).</summary>
			public void Drop()
			{
				if (job != null)
				{
					spareArray = job.Buffer;
					job = null;
					dropped++;
				}
			}

			/// <summary>Label (kinds, depth, ramps) for (band, cls) at once unless the inputs are those of the published
			/// labelling. True when it flooded.</summary>
			public bool Rebuild(byte[] kinds, byte[] depth, Dictionary<int, int> ramps, int width, int height, int band, int cls)
			{
				if (!Begin(kinds, depth, ramps, width, height, band, cls, RM_PocketGridMath.QueueScratch(width * height)))
				{
					return false;
				}
				Advance(int.MaxValue, out _);
				return true;
			}
		}

		/// <summary>WALLREACH_RELABEL_TAME_SLICED_BUFFERED: may a veto answer from a published labelling? Only when no change
		/// that can OPEN a way (a breach, a door held open, a gate unlocked, a reload: every place RM_WallReach sets forced also
		/// moves the unsafe generation) has happened since the inputs of that labelling were read. A labelling begun before
		/// such a change covers an older generation, so until a job begun after it is published the answer is "unknown", and
		/// the postfix leaves vanilla's yes alone. Stale in the safe direction (a wall built: labels more connected than the
		/// map) still serves, as before.</summary>
		public static bool Covers(int coveredGen, int unsafeGenNow)
		{
			return coveredGen == unsafeGenNow;
		}

		/// <summary>WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP: the map's kinds snapshot, as RM_WallReach.Kinds runs it. The
		/// published array is never written after it is published (a worker thread reads it: NoteConnectivity); a read whose
		/// content (and geometry) equals it becomes scratch for the next read, so a labelling built from the published array
		/// can tell by reference that no kind moved. <see cref="Invalidate"/> (a load finished) makes the next ask re-read.
		/// WALLREACH_BEGINJOB_TAME_INPUTS_OUT_OF_SLICE: a replaced published array is written again only once it is no longer
		/// published and <see cref="inUse"/> says no labelling holds it (NoteConnectivity's worker reads only the array
		/// published while the main thread is blocked in GatherData, and Publish runs on the main thread, so a worker never
		/// holds a replaced one).</summary>
		public sealed class KindsSnapshot
		{
			public byte[] published;
			public long stamp = long.MinValue;
			public int width = -1, height = -1;
			private byte[] scratch;
			/// <summary>WALLREACH_BEGINJOB_TAME_INPUTS_OUT_OF_SLICE: does some labelling still hold this array (built from it or
			/// flooding from it)? A replaced published array is reused for a later read only when this says no. Null: never
			/// reused.</summary>
			public Func<byte[], bool> inUse;
			/// <summary>Arrays allocated by <see cref="Take"/> (diagnostic: zero in steady play).</summary>
			public int allocs;
			public int readsBegun, readsDone, readRestarts, readAborts;
			public long readCells;
			private readonly List<byte[]> retired = new List<byte[]>();
			private const int MaxRetired = 4;
			private byte[] reading;
			private int readCursor, readW, readH;
			private long readStamp;

			/// <summary>A sliced read is in flight (<see cref="BeginRead"/> .. <see cref="ReadStep"/> true or
			/// <see cref="AbortRead"/>).</summary>
			public bool Reading => reading != null;
			/// <summary>Squares [0, ReadCursor) of the read in flight are read.</summary>
			public int ReadCursor => readCursor;

			public bool CurrentFor(long s, int w, int h)
			{
				return published != null && stamp == s && width == w && height == h && published.Length == w * h;
			}

			/// <summary>An array of n to read the map into (the last unchanged read, else a new one). Every square must be
			/// written before <see cref="Publish"/>.</summary>
			public byte[] Take(int n)
			{
				byte[] a = scratch != null && scratch.Length == n ? scratch : null;
				scratch = null;
				for (int i = 0; a == null && inUse != null && i < retired.Count; i++)
				{
					if (retired[i].Length == n && !inUse(retired[i]))
					{
						a = retired[i];
						retired.RemoveAt(i);
					}
				}
				if (a == null)
				{
					allocs++;
					a = new byte[n];
				}
				return a;
			}

			/// <summary>The read becomes the published snapshot when its content or geometry moved; else the old array stays
			/// published and the read waits as scratch. Returns the published array.</summary>
			public byte[] Publish(byte[] read, long s, int w, int h)
			{
				if (w != width || h != height || !SameBytes(read, published))
				{
					Retire(published);
					published = read;
				}
				else
				{
					scratch = read;
				}
				stamp = s;
				width = w;
				height = h;
				return published;
			}

			/// <summary>The next ask re-reads; a read in flight (begun while loading) is dropped with it.</summary>
			public void Invalidate()
			{
				stamp = long.MinValue;
				AbortRead();
			}

			/// <summary>A replaced published array waits here (newest first, at most MaxRetired) until no labelling holds it.
			/// Only with an <see cref="inUse"/> predicate: without one nothing is known to be free.</summary>
			private void Retire(byte[] a)
			{
				if (a == null || inUse == null)
				{
					return;
				}
				if (retired.Count >= MaxRetired)
				{
					retired.RemoveAt(retired.Count - 1);
				}
				retired.Insert(0, a);
			}

			/// <summary>WALLREACH_BEGINJOB_TAME_INPUTS_OUT_OF_SLICE: start reading the map a slice at a time into an array of
			/// w × h (<see cref="Take"/>); it is published at stamp <paramref name="s"/> when the last square is read. A read in
			/// flight is dropped first.</summary>
			public void BeginRead(long s, int w, int h)
			{
				AbortRead();
				reading = Take(w * h);
				readCursor = 0;
				readStamp = s;
				readW = w;
				readH = h;
				readsBegun++;
			}

			/// <summary>Read at most <paramref name="budget"/> more squares with <paramref name="kindAt"/>. True when this call
			/// read the last one and published the read (<see cref="Publish"/> at the stamp it began with).</summary>
			public bool ReadStep(int budget, Func<int, byte> kindAt, out int spent)
			{
				spent = 0;
				if (reading == null)
				{
					return false;
				}
				int n = reading.Length;
				int end = budget >= n - readCursor ? n : readCursor + Math.Max(1, budget);
				for (int i = readCursor; i < end; i++)
				{
					reading[i] = kindAt(i);
				}
				spent = end - readCursor;
				readCursor = end;
				readCells += spent;
				if (readCursor < n)
				{
					return false;
				}
				byte[] read = reading;
				reading = null;
				readsDone++;
				Publish(read, readStamp, readW, readH);
				return true;
			}

			/// <summary>Square <paramref name="i"/> may have changed since the read in flight passed it: read it again.</summary>
			public void Touch(int i, Func<int, byte> kindAt)
			{
				if (reading != null && i >= 0 && i < readCursor)
				{
					reading[i] = kindAt(i);
				}
			}

			/// <summary>Changes were lost (a delta overflow): read the whole map again, same stamp.</summary>
			public void RestartRead()
			{
				if (reading != null)
				{
					readCursor = 0;
					readRestarts++;
				}
			}

			/// <summary>Drop the read in flight unpublished (its array becomes the scratch).</summary>
			public void AbortRead()
			{
				if (reading != null)
				{
					scratch = scratch ?? reading;
					reading = null;
					readAborts++;
				}
			}
		}

		/// <summary>WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP: was this built while the game was still loading, and is the game
		/// now playing? Then it is rebuilt from a fresh read on the first tick or frame in play, whatever its stamp says (the
		/// pocket grid's RELOAD_POCKETS rule).</summary>
		public static bool StaleAfterLoad(bool builtMidLoad, bool playing)
		{
			return builtMidLoad && playing;
		}

		/// <summary>WALLREACH_CACHE_HARDEN_DOOR_HOLDS_OLD_MAP (GPT review F1): the pocket and wall-reach caches (labels, their
		/// spare arrays, the query scratch) have ONE owner at a time. In play that is the main thread; while a save loads or a
		/// map generates it is the long-event worker (Root_Play queues both doAsynchronously, and region building asks the
		/// pocket grid), with the main thread only drawing the loading screen. So the rule is "never two at once", not "main
		/// thread only". A thread entering while another holds the gate is refused (its caller answers as vanilla: no veto, no
		/// build) and counted; the holder's own nested calls pass.</summary>
		public sealed class OwnerGate
		{
			private int holder;
			public int refused;

			/// <summary>True: the caller owns the caches until <see cref="Exit"/>(nested). nested: it already held them.</summary>
			public bool TryEnter(int threadId, out bool nested)
			{
				int prev = System.Threading.Interlocked.CompareExchange(ref holder, threadId, 0);
				nested = prev == threadId;
				if (prev == 0 || nested)
				{
					return true;
				}
				System.Threading.Interlocked.Increment(ref refused);
				return false;
			}

			public void Exit(bool nested)
			{
				if (!nested)
				{
					System.Threading.Volatile.Write(ref holder, 0);
				}
			}

			public int Holder => System.Threading.Volatile.Read(ref holder);

			/// <summary>RAIN_REVIEW_FIX_SLUICES_AND_OVERFILL (MED5): a query that fills a shared per-build cache (the pocket
			/// grid's cells, width and edge caches) holds the gate for the whole read-or-fill, so a build on another thread can
			/// neither clear the cache under it nor see it half-written. A caller refused here is counted and answered from its
			/// state alone (compute(s)), the shared cache untouched.</summary>
			public T Cached<TS, T>(int threadId, System.Collections.Generic.Dictionary<long, T> cache, long key, TS s, System.Func<TS, T> compute)
			{
				if (!TryEnter(threadId, out bool nested))
				{
					return compute(s);
				}
				try
				{
					if (!cache.TryGetValue(key, out T v))
					{
						v = compute(s);
						cache[key] = v;
					}
					return v;
				}
				finally
				{
					Exit(nested);
				}
			}
		}
	}
}
