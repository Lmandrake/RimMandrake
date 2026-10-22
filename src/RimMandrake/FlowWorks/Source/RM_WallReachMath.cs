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
		/// all four squares within K), so every diagonal step has a cardinal detour inside the same component.</summary>
		public static Labels Label(byte[] kind, byte[] depth, int width, int height, int k, int cls, Func<int, int, bool> rampJoins = null)
		{
			if (kind == null || width <= 0 || height <= 0 || kind.Length < width * height || (depth != null && depth.Length < width * height))
			{
				throw new ArgumentException("grids do not match " + width + "x" + height);
			}
			int n = width * height;
			var lab = new int[n];
			for (int i = 0; i < n; i++)
			{
				lab[i] = Passable(kind[i], cls) ? int.MaxValue : -1;   // MaxValue = passable, not yet labelled
			}
			var queue = new int[n];
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
					int x = c % width, z = c / width;
					int d = depth == null ? 0 : depth[c];
					for (int dir = 0; dir < 4; dir++)
					{
						int nx = x, nz = z;
						switch (dir)
						{
							case 0: nz++; break;
							case 1: nx++; break;
							case 2: nz--; break;
							default: nx--; break;
						}
						if (nx < 0 || nz < 0 || nx >= width || nz >= height)
						{
							continue;
						}
						int ni = nz * width + nx;
						if (lab[ni] != int.MaxValue)
						{
							continue;
						}
						if (depth != null)
						{
							bool ramp = rampJoins != null && (rampJoins(c, ni) || rampJoins(ni, c));
							if (!RM_PitTrapMath.StepAllowed(d, depth[ni], k, ramp))
							{
								continue;
							}
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
	}
}
