using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Machinery
{
	// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 3 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P4):
	// what a collapsing bridge deck does to the lines on it, and when the cord it dropped is a live wire. Pure: no Verse, no
	// UnityEngine, so the offline SelfTest compiles this file itself (DeckCollapseLinesChecks.cs). The map side is
	// RM_DeckCollapseLines.cs (the hook in RM_MapComponent_SuspensionBridges.ClearDeckTop, the fallen-cord map component and
	// the soft seam into Gimme Some Slack's RM_FallenWireShock).

	public static class RM_DeckCollapseLinesMath
	{
		/// <summary>P4: a collapsing deck destroys the cords and hoses on its squares. Of the tagged lines only a cord can lie on a
		/// deck (P2) and only a cord falls as a wire; a hose is a route, not a thing on the square, and is cut by its reel
		/// (CompHoseReel.Retract). Rigid pipe and conduit never stand on a deck, so the deck has nothing of theirs to drop.</summary>
		public static bool FallsAsWire(LineKind k) => k == LineKind.FlexCord;

		/// <summary>The cords one cleared deck square drops: every tagged cord still standing. Rules off, untagged things and things
		/// already gone give nothing, so clearing the same square again is a no-op: the teardown is idempotent.</summary>
		public static List<T> CordsToDrop<T>(bool rulesOn, IEnumerable<T> onSquare, Func<T, LineKind?> kindOf, Func<T, bool> gone)
		{
			var hit = new List<T>();
			if (!rulesOn || onSquare == null)
			{
				return hit;
			}
			foreach (T t in onSquare)
			{
				if (t == null || gone(t))
				{
					continue;
				}
				LineKind? k = kindOf(t);
				if (k != null && FallsAsWire(k.Value) && !hit.Contains(t))
				{
					hit.Add(t);
				}
			}
			return hit;
		}

		/// <summary>Does a laid hose cross the cleared square? Its walked trail, else (an old save with no trail) the straight
		/// line the drawbridge cut reads too (RM_Drawbridges.HoseCut).</summary>
		public static bool HoseCrosses(bool laid, IEnumerable<(int X, int Z)> path, int x, int z)
		{
			if (!laid || path == null)
			{
				return false;
			}
			foreach ((int X, int Z) p in path)
			{
				if (p.X == x && p.Z == z)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>A fallen cord is a LIVE wire only while the rules are on, the standing line it hangs from (its end) is still on
		/// the map, that end's power net is one the map really holds (a dropped net is a stale edge, never powered), and that net
		/// has an active power source. Anything else is a dead wire: harmless.</summary>
		public static bool Live(bool rulesOn, bool endStanding, bool netRegistered, bool netHasActiveSource) =>
			rulesOn && endStanding && netRegistered && netHasActiveSource;

		public static long Key(int x, int z) => ((long)x << 32) ^ (uint)z;

		private static readonly (int dx, int dz)[] Cardinal = { (1, 0), (-1, 0), (0, 1), (0, -1) };

		/// <summary>The fallen cells, split into 4-way connected runs (one dropped stretch of cord each).</summary>
		public static List<List<(int X, int Z)>> Runs(IEnumerable<(int X, int Z)> cells)
		{
			var left = new Dictionary<long, (int X, int Z)>();
			var order = new List<long>();
			foreach ((int X, int Z) c in cells)
			{
				long k = Key(c.X, c.Z);
				if (!left.ContainsKey(k))
				{
					left[k] = c;
					order.Add(k);
				}
			}
			var runs = new List<List<(int X, int Z)>>();
			foreach (long seed in order)
			{
				if (!left.TryGetValue(seed, out (int X, int Z) s))
				{
					continue;
				}
				var run = new List<(int X, int Z)>();
				var q = new Queue<(int X, int Z)>();
				left.Remove(seed);
				q.Enqueue(s);
				while (q.Count > 0)
				{
					(int X, int Z) c = q.Dequeue();
					run.Add(c);
					foreach ((int dx, int dz) d in Cardinal)
					{
						long k = Key(c.X + d.dx, c.Z + d.dz);
						if (left.TryGetValue(k, out (int X, int Z) n))
						{
							left.Remove(k);
							q.Enqueue(n);
						}
					}
				}
				runs.Add(run);
			}
			return runs;
		}

		/// <summary>One half of a dropped cord: the standing line it hangs from (end index into the ends passed to
		/// <see cref="Split"/>), the fallen cells that hang from it, and its tip (the cell farthest down the run from the end).</summary>
		public sealed class Half
		{
			public int End;
			public List<(int X, int Z)> Cells = new List<(int X, int Z)>();
			public (int X, int Z) Tip;
		}

		/// <summary>Split one run between the standing lines next to it (ends: their cells, in priority order). Every run cell
		/// edge-adjacent to an end seeds that end; a breadth-first walk inside the run gives each cell to its nearest end (ties to
		/// the earlier end), so a span cut out of the middle of a cord leaves two halves, one per bank, the way a cut aerial span
		/// leaves one fallen half per pole. Cells no end reaches hang from nothing: they are dropped (dead, never a half).</summary>
		public static List<Half> Split(List<(int X, int Z)> run, IList<(int X, int Z)> ends)
		{
			var halves = new List<Half>();
			if (run == null || run.Count == 0 || ends == null || ends.Count == 0)
			{
				return halves;
			}
			var inRun = new HashSet<long>();
			foreach ((int X, int Z) c in run)
			{
				inRun.Add(Key(c.X, c.Z));
			}
			var owner = new Dictionary<long, int>();
			var dist = new Dictionary<long, int>();
			var q = new Queue<(int X, int Z)>();
			for (int e = 0; e < ends.Count; e++)
			{
				foreach ((int X, int Z) c in run)
				{
					long k = Key(c.X, c.Z);
					if (owner.ContainsKey(k))
					{
						continue;
					}
					if (Math.Abs(c.X - ends[e].X) + Math.Abs(c.Z - ends[e].Z) == 1)
					{
						owner[k] = e;
						dist[k] = 0;
						q.Enqueue(c);
					}
				}
			}
			while (q.Count > 0)
			{
				(int X, int Z) c = q.Dequeue();
				long ck = Key(c.X, c.Z);
				foreach ((int dx, int dz) d in Cardinal)
				{
					long k = Key(c.X + d.dx, c.Z + d.dz);
					if (inRun.Contains(k) && !owner.ContainsKey(k))
					{
						owner[k] = owner[ck];
						dist[k] = dist[ck] + 1;
						q.Enqueue((c.X + d.dx, c.Z + d.dz));
					}
				}
			}
			var byEnd = new Dictionary<int, Half>();
			var tipDist = new Dictionary<int, int>();
			foreach ((int X, int Z) c in run)
			{
				long k = Key(c.X, c.Z);
				if (!owner.TryGetValue(k, out int e))
				{
					continue;
				}
				if (!byEnd.TryGetValue(e, out Half h))
				{
					h = new Half { End = e, Tip = c };
					byEnd[e] = h;
					tipDist[e] = -1;
					halves.Add(h);
				}
				h.Cells.Add(c);
				if (dist[k] > tipDist[e])
				{
					tipDist[e] = dist[k];
					h.Tip = c;
				}
			}
			return halves;
		}

		/// <summary>The one message a collapse that dropped a live cord shows (null when none fell live).</summary>
		public static string LiveMessage(int liveHalves) =>
			liveHalves <= 0 ? null
			: liveHalves == 1 ? "A live power cord fell with the bridge deck: it lies in the hole and shocks whoever touches it."
			: liveHalves + " live power cords fell with the bridge deck: they lie in the hole and shock whoever touches them.";
	}
}
