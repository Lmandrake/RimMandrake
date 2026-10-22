using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP — owner 2026-10-18, by card (Q7): <i>"Raiders reach a trench they cannot cross →
	/// Go around, and breach if no way"</i>, and in his words: <i>"(4) plus some may have jump packs to cross. Ladders make sense
	/// for shallower pits (they could start building them in preparation). Siege raids still work fine with mortars."</i>
	///
	/// The pure half (no Verse; selftested in SelfTest/RaiderTrenchChecks.cs). The Verse half is RM_RaiderTrench.cs.
	///
	/// A crossing is judged along ONE line of cardinal steps from a lip the raider stands on (index 0) to the first square of
	/// the far side (the last index), as climb depths in levels. Going around is vanilla's: while any target is reachable the
	/// cliff masks route the raid round the trench and nothing here runs. Only when NO target is reachable does a raider pick,
	/// in this order: jump (a jump pack or a leaping ability, in range), scaling ladders (every wall on the line within the
	/// portable ladder's reach: the "shallower pits"), else breach by shovelling a causeway in (the least fill that leaves
	/// every step on the line climbable). Sieges never cross (they shell; owner: "Siege raids still work fine with mortars").
	/// </summary>
	public static class RM_RaiderTrenchMath
	{
		public enum Crossing
		{
			/// <summary>Not this pawn's business, or no way it can manage: vanilla decides (it mills, shoots across, leaves).</summary>
			None,
			/// <summary>A target is reachable: the masks already route round the trench (vanilla's job givers act).</summary>
			GoAround,
			Jump,
			Ladder,
			Fill,
		}

		/// <summary>The owner's order. <paramref name="eligible"/>: a hostile raider of a lord (not a siege, not trapped);
		/// <paramref name="toolUser"/>: may build ladders and shovel (a person, not an animal or a mech).</summary>
		public static Crossing Choose(bool masterOn, bool eligible, bool siege, bool anyTargetReachable,
			bool jumpOn, bool jumpReady, bool toolUser, bool laddersOn, bool laddersFeasible, bool fillOn, bool fillFeasible)
		{
			if (!masterOn || !eligible || siege)
			{
				return Crossing.None;
			}
			if (anyTargetReachable)
			{
				return Crossing.GoAround;
			}
			if (jumpOn && jumpReady)
			{
				return Crossing.Jump;
			}
			if (!toolUser)
			{
				return Crossing.None;
			}
			if (laddersOn && laddersFeasible)
			{
				return Crossing.Ladder;
			}
			if (fillOn && fillFeasible)
			{
				return Crossing.Fill;
			}
			return Crossing.None;
		}

		/// <summary>A 4-connected line from (x0, z0) to (x1, z1), both ends included: Bresenham with each diagonal step split
		/// into two cardinal ones (the x step first), so every adjacent pair is a cardinal neighbour, as the climb masks judge.</summary>
		public static List<(int x, int z)> CardinalLine(int x0, int z0, int x1, int z1, int maxCells)
		{
			var line = new List<(int x, int z)> { (x0, z0) };
			int dx = Math.Abs(x1 - x0), dz = Math.Abs(z1 - z0);
			int sx = x0 < x1 ? 1 : -1, sz = z0 < z1 ? 1 : -1;
			int err = dx - dz;
			int x = x0, z = z0;
			while ((x != x1 || z != z1) && line.Count < maxCells)
			{
				int e2 = 2 * err;
				bool stepX = e2 > -dz;
				bool stepZ = e2 < dx;
				if (stepX)
				{
					err -= dz;
					x += sx;
					line.Add((x, z));
				}
				if (stepZ && line.Count < maxCells)
				{
					err += dx;
					z += sz;
					line.Add((x, z));
				}
			}
			return line;
		}

		/// <summary>The least fill that makes every step of the line climbable: each square raised (made shallower) only as far
		/// as it must, never dug. t[i] = min over j of (d[j] + k·|i − j|), the deepest profile under d whose neighbours differ by
		/// at most k (StepAllowed's max(1, k)); the two ends are never touched (they already belong to each side).</summary>
		public static int[] FillTargets(int[] d, int k)
		{
			int n = d.Length;
			int kk = Math.Max(1, k);
			var t = new int[n];
			for (int i = 0; i < n; i++)
			{
				t[i] = d[i];
			}
			// Two passes of the min-plus envelope (forward, back) give the exact lower envelope for a 1-D line.
			for (int i = 1; i < n; i++)
			{
				t[i] = Math.Min(t[i], t[i - 1] + kk);
			}
			for (int i = n - 2; i >= 0; i--)
			{
				t[i] = Math.Min(t[i], t[i + 1] + kk);
			}
			if (n > 0)
			{
				t[0] = d[0];
				t[n - 1] = d[n - 1];
			}
			return t;
		}

		/// <summary>Is every step of this profile climbable at k? False for a fill plan whose end is deeper than its neighbour
		/// by more than k: shovelling only makes the neighbour shallower, so fill cannot fix it.</summary>
		public static bool StepsClimbable(int[] t, int k)
		{
			int kk = Math.Max(1, k);
			for (int i = 0; i + 1 < t.Length; i++)
			{
				if (Math.Abs(t[i + 1] - t[i]) > kk)
				{
					return false;
				}
			}
			return true;
		}

		/// <summary>Total levels to shovel in (the breach's size).</summary>
		public static int FillLevels(int[] d, int[] t)
		{
			int s = 0;
			for (int i = 0; i < d.Length; i++)
			{
				s += Math.Max(0, d[i] - t[i]);
			}
			return s;
		}

		/// <summary>The square to shovel next: the first (from the raider's side) still deeper than its target. Every square
		/// before it already meets its target, so the raider can stand on its near neighbour. -1: the causeway is done.</summary>
		public static int NextFill(int[] current, int[] target)
		{
			for (int i = 1; i < current.Length - 1; i++)
			{
				if (current[i] > target[i])
				{
					return i;
				}
			}
			return -1;
		}

		public struct LadderSlot
		{
			/// <summary>Line index of the (deeper) square the ladder stands in.</summary>
			public int cell;
			/// <summary>Line index of the shallower neighbour whose wall it hangs on.</summary>
			public int toward;
			/// <summary>The drop the ladder spans, in levels.</summary>
			public int drop;
		}

		/// <summary>The scaling ladders a crossing needs: one in the deeper square of every step taller than the raider climbs,
		/// hung toward the shallower one. Null when ladders cannot do it: a drop past the portable ladder's reach (reach &gt; 0;
		/// 0 = any depth), a square that would need two ladders (a 1-square-wide slot between two walls: a square holds one),
		/// or a ladder that would have to stand on either end (those are each side's own ground).</summary>
		public static List<LadderSlot> LadderSlots(int[] d, int k, int reach)
		{
			int kk = Math.Max(1, k);
			var slots = new List<LadderSlot>();
			var used = new HashSet<int>();
			for (int i = 0; i + 1 < d.Length; i++)
			{
				int drop = Math.Abs(d[i + 1] - d[i]);
				if (drop <= kk)
				{
					continue;
				}
				int deep = d[i + 1] > d[i] ? i + 1 : i;
				int shallow = deep == i ? i + 1 : i;
				if (deep == 0 || deep == d.Length - 1 || (reach > 0 && drop > reach) || !used.Add(deep))
				{
					return null;
				}
				slots.Add(new LadderSlot { cell = deep, toward = shallow, drop = drop });
			}
			return slots;
		}

		/// <summary>Card Q7's scaling ladder: about 10 s + 1 s a metre (PROVISIONAL), divided by the speed setting. Ticks.</summary>
		public static int LadderTicks(double metres, float speed)
		{
			double s = Math.Max(0.1, speed);
			return (int)Math.Ceiling((600.0 + 60.0 * Math.Max(0.0, metres)) / s);
		}

		/// <summary>One level of fill, as vanilla's JobDriver_AffectFloor spends work (speed stat × 1.7 a tick), divided by the
		/// breach speed setting. Ticks.</summary>
		public static int FillTicks(int work, float speedStat, float speed)
		{
			double rate = Math.Max(0.1, speedStat) * 1.7 * Math.Max(0.1, speed);
			return (int)Math.Ceiling(Math.Max(1, work) / rate);
		}

		/// <summary>CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP: the work of shovelling ONE level of spoil into a trench square, the same at
		/// every depth: half the first notch's cut (RM_DigDepthMath.WorkPerNotch / 2). Tipping earth down into a hole is not
		/// cutting and lifting it out, so the deep-dig cost curve (3,200 x the notch) does not apply: priced on it, one level
		/// at 4 m took a gunner (MiningSpeed 0.336) ~22,400 ticks and a 4 m ring never got one square filled before the raid
		/// left (~t+28,000, belt 2026-10-22). At this price that gunner shovels a level in ~2,800 ticks.</summary>
		public const int FillWorkPerLevel = RM_DigDepthMath.WorkPerNotch / 2;

		/// <summary>How many raiders shovel into one causeway square at once (each its own level; the last one re-checks the
		/// square's target first, so the step is never over-filled). One a square left the rest of the raid waiting at the lip.</summary>
		public const int MaxFillersPerSquare = 3;

		/// <summary>Ticks for a raid to shovel the whole causeway of a line: the squares one after another (the next square is
		/// reached only over the last one), each square's levels shared among <paramref name="fillers"/> raiders.</summary>
		public static int BreachTicks(int[] d, int[] t, int ticksPerLevel, int fillers)
		{
			int f = Math.Max(1, fillers);
			long total = 0;
			for (int i = 0; i < d.Length; i++)
			{
				int levels = Math.Max(0, d[i] - t[i]);
				total += (long)((levels + f - 1) / f) * ticksPerLevel;
			}
			return (int)Math.Min(int.MaxValue, total);
		}

		/// <summary>One crossing point per raid, kept while the raid works it. <paramref name="have"/>: a lip is remembered,
		/// set at <paramref name="tick"/>. A lip expired after <paramref name="cacheTicks"/> is replaced by the offered one; a
		/// live lip that the raid is still given work on (<paramref name="workedHere"/>) is renewed, so a breach that takes
		/// longer than the cache is not abandoned: CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP's 4 raiders each shovelled a DIFFERENT
		/// line, because every later raider re-planned from its own lip once the first lip was 2,500 ticks old.
		/// Returns the tick to store, or -1 to leave the memory as it is.</summary>
		public static int LipTick(bool have, int tick, int now, int cacheTicks, bool sameLip, bool workedHere)
		{
			if (!have || now - tick >= cacheTicks)
			{
				return now;
			}
			return sameLip && workedHere ? now : -1;
		}

		/// <summary>"Some may have jump packs": does this raider arrive with one? A stable hash of its id against the share, so
		/// a reload or a re-roll never changes who has one.</summary>
		public static bool GetsJumpPack(int pawnId, float share)
		{
			if (share <= 0f)
			{
				return false;
			}
			if (share >= 1f)
			{
				return true;
			}
			unchecked
			{
				uint h = (uint)pawnId * 2654435761u;
				h ^= h >> 16;
				h *= 0x7feb352du;
				h ^= h >> 15;
				return (h % 10000u) < (uint)(share * 10000f);
			}
		}

		/// <summary>The landing for a jump across: the first square from the far side's first square (<paramref name="from"/>)
		/// outward that is a valid landing within range, looking at most <paramref name="look"/> squares on. -1: none.</summary>
		public static int JumpLanding(int from, int count, int look, Func<int, bool> valid, Func<int, bool> inRange)
		{
			for (int i = from; i < count && i < from + look; i++)
			{
				if (valid(i) && inRange(i))
				{
					return i;
				}
			}
			return -1;
		}
	}
}
