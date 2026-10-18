using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FALL_GUARDRAILS_BUILD_REAL_OBJECT (owner, 2026-10-18: <i>"build guardrails as a real object with real need (and support
	/// existing fences acting this way too)."</i>). Verse-free: the edge rule a rail enforces, shared by the doors where a fall
	/// reaches a pawn (RM_FallRails) and the SelfTest.
	///
	/// A rail stands on one cell and guards every edge from that cell to an 8-neighbour lower by a sheer drop
	/// (<see cref="RM_RelativeRulesMath.StepIsAFall"/>: the spikes' and covers' edge set, read from the top). "Sheer" is the
	/// fall the doors already judge: for a pawn of climb limit K a drop of more than K (RM_PitTrapMath.ArrivalDropsTooFar),
	/// which is StepIsAFall with K + 1 (<see cref="FallNotchesFor"/>). Depths in notches (0.5 m), 0 = undug ground.
	/// </summary>
	public static class RM_FallRailMath
	{
		private static readonly int[] Dx8 = { 0, 1, 0, -1, 1, 1, -1, -1 };
		private static readonly int[] Dz8 = { 1, 0, -1, 0, 1, -1, -1, 1 };

		/// <summary>The StepIsAFall threshold for a pawn of climb limit <paramref name="climbLimit"/>: a drop past what it climbs.
		/// StepIsAFall(f, t, FallNotchesFor(k)) == ArrivalDropsTooFar(f, t, k) for every f, t, k.</summary>
		public static int FallNotchesFor(int climbLimit)
		{
			return Math.Max(1, climbLimit) + 1;
		}

		/// <summary>Does a rail guard the edge from a cell at <paramref name="fromD"/> to an adjacent cell at <paramref name="toD"/>?
		/// Only with a rail on the FROM cell (the lip) and only DOWN by a sheer drop: climbing up out of the pit past a rail is
		/// never refused (ladders are still the way in and out), nor is a gentle step.</summary>
		public static bool GuardsEdge(bool railOnFrom, int fromD, int toD, int fallNotches)
		{
			return railOnFrom && RM_RelativeRulesMath.StepIsAFall(fromD, toD, fallNotches);
		}

		/// <summary>The fall is stopped: the edge is guarded and the pawn did not choose to go over (the jump-in order, a jump
		/// pack's landing). A cover giving way never reaches here: it is a fall from ON the pit, which no rail can stop.</summary>
		public static bool FallBlocked(bool edgeGuarded, bool deliberateJump)
		{
			return edgeGuarded && !deliberateJump;
		}

		/// <summary>The fence rule: a cell holds a rail when the rule is on and a built (not blueprint or frame) building on it is
		/// our guardrail or any def with building.isFence (Core's fence, mods' fences that set it).</summary>
		public static bool IsRailThing(bool ruleOn, bool built, bool isOurRail, bool isFence)
		{
			return ruleOn && built && (isOurRail || isFence);
		}

		/// <summary>Placement: some 8-neighbour of (x, z) is lower by a sheer drop of <paramref name="fallNotches"/>, i.e. a rail
		/// here would guard at least one edge. <paramref name="depthAt"/> answers -1 out of bounds (skipped).</summary>
		public static bool HasDropBeside(Func<int, int, int> depthAt, int x, int z, int fallNotches)
		{
			int here = depthAt(x, z);
			if (here < 0)
			{
				return false;
			}
			for (int k = 0; k < 8; k++)
			{
				int n = depthAt(x + Dx8[k], z + Dz8[k]);
				if (n >= 0 && RM_RelativeRulesMath.StepIsAFall(here, n, fallNotches))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The cells of a straight throw from (x0, z0) to (x1, z1), both ends included, every step 8-adjacent
		/// (Bresenham).</summary>
		public static List<(int x, int z)> Line(int x0, int z0, int x1, int z1)
		{
			var cells = new List<(int, int)>();
			int dx = Math.Abs(x1 - x0), dz = Math.Abs(z1 - z0);
			int sx = x0 < x1 ? 1 : -1, sz = z0 < z1 ? 1 : -1;
			int err = dx - dz;
			int x = x0, z = z0;
			for (int guard = 0; guard <= dx + dz + 1; guard++)
			{
				cells.Add((x, z));
				if (x == x1 && z == z1)
				{
					break;
				}
				int e2 = 2 * err;
				if (e2 > -dz)
				{
					err -= dz;
					x += sx;
				}
				if (e2 < dx)
				{
					err += dx;
					z += sz;
				}
			}
			return cells;
		}

		/// <summary>Where a throw along <paramref name="n"/> line cells stops at a rail: the first guarded edge i → i + 1
		/// (<paramref name="edgeGuarded"/>(i)) stops it on cell i, or on the nearest standable cell before it (cell 0, the
		/// take-off, as the last resort). -1: no guarded edge, the throw lands where it was going.</summary>
		public static int ThrowStopIndex(int n, Func<int, bool> edgeGuarded, Func<int, bool> standable)
		{
			for (int i = 0; i + 1 < n; i++)
			{
				if (!edgeGuarded(i))
				{
					continue;
				}
				for (int j = i; j > 0; j--)
				{
					if (standable(j))
					{
						return j;
					}
				}
				return 0;
			}
			return -1;
		}
	}
}
