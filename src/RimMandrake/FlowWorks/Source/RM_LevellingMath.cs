using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>One body of liquid as the levelling solver sees it (PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL).</summary>
	public sealed class RM_LevelBody
	{
		/// <summary>Identity: two link ends with the same key are in the same body, and such a link moves nothing.</summary>
		public long Key;
		/// <summary>The liquid it holds (compared by reference); null = dry, and a dry body takes the source's liquid.</summary>
		public object Fluid;
		/// <summary>Never runs down or fills up (sea, edge river): surface pinned at the brim (0), any volume, any room.</summary>
		public bool Limitless;
		/// <summary>Floor histogram, RM_LevelSolve's pond convention: H[L] = squares whose floor is at least L notches deep.</summary>
		public int[] Hist;
		/// <summary>Water in decilitres (the model volume over <see cref="Hist"/>).</summary>
		public long Water;
	}

	/// <summary>A pipe or hose with one end in body <see cref="A"/> and the other in body <see cref="B"/>.</summary>
	public struct RM_LevelLink
	{
		public int A, B;
		/// <summary>The floor under each end, as a surface height (dL-per-square, 0 = brim, negative below ground): a body
		/// stops giving through this link once its surface falls to the floor under its end (the intake is exposed).</summary>
		public double FloorA, FloorB;
		/// <summary>The most each end can hand out this cycle in dL (a dug end cell gives what it holds; long.MaxValue = the
		/// body's whole stock).</summary>
		public long TakeA, TakeB;
		/// <summary>The most each end can take in this cycle in dL (a pour's room; long.MaxValue = the body's whole room).</summary>
		public long RoomA, RoomB;
	}

	/// <summary>One planned transfer: <see cref="Dl"/> decilitres from body <see cref="From"/> to body <see cref="To"/> through link <see cref="Link"/>.</summary>
	public struct RM_LevelMove
	{
		public int Link, From, To;
		public long Dl;
	}

	/// <summary>Why a link moved nothing this cycle (the readout, design P9).</summary>
	public enum RM_LevelLinkState { Flowing, Level, SameBody, DifferentLiquids, IntakeExposed, Full, Skipped }

	/// <summary>
	/// PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL: passive gravity levelling between bodies of liquid joined by pipes and hoses
	/// (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md P6; owner answer 7, <i>"connecting two bodies of
	/// water will cause them to slowly flow from one to the other until they level out"</i>). Verse-free; selftested by
	/// Source/SelfTest/LevellingChecks.cs.
	/// <list type="bullet">
	/// <item>Each body's surface is RM_LevelSolve.PondSurfaceHeight over its floor histogram (one convention for ponds and dug
	/// runs: dL-per-square, 0 = brim). A limitless body stands at 0.</item>
	/// <item>Links are visited in a fixed order, at most <c>maxLinks</c> per cycle from a rotating cursor (the hard budget);
	/// a link visited every k cycles moves up to k (capped at <see cref="MaxCatchUp"/>) cycles' worth (elapsed integration).</item>
	/// <item>Gauss-Seidel: each link plans against the volumes the earlier links in this cycle left, so parallel links sum and
	/// a body on many links is never overdrawn.</item>
	/// <item>A link moves from the higher surface to the lower, up to the rate, and never past the half-way point to its own
	/// equilibrium (found by bisection on the exact surfaces): no transfer reverses a gap, so heights converge monotonically
	/// and nothing oscillates; the halving also absorbs the game's model error (a run's histogram over- or under-counting
	/// area at a sill).</item>
	/// <item>Siphon always: no crest test. A source stops at the floor under its end (exposed intake). Different liquids
	/// never exchange; a dry receiver takes the source's liquid. Same key: nothing. Volume: every move is debited from one
	/// body and credited to another in whole decilitres; limitless bodies are counted apart.</item>
	/// </list>
	/// </summary>
	public static class RM_LevellingMath
	{
		/// <summary>A gap under this (dL-per-square, = 0.5 cm) is level: nothing moves (owner R9's 1 cm bar, halved).</summary>
		public const double LevelTolerance = 100.0;

		/// <summary>A link visited every k cycles moves at most this many cycles' worth at once.</summary>
		public const int MaxCatchUp = 8;

		/// <summary>The body's surface (dL-per-square, 0 = brim, negative below).</summary>
		public static double Surface(RM_LevelBody b, long water)
		{
			if (b.Limitless)
			{
				return 0.0;
			}
			if (b.Hist == null || b.Hist.Length <= 1)
			{
				return 0.0;
			}
			return RM_LevelSolve.PondSurfaceHeight(b.Hist, water);
		}

		/// <summary>The body's capacity in dL (long.MaxValue for limitless).</summary>
		public static long Capacity(RM_LevelBody b)
		{
			if (b.Limitless)
			{
				return long.MaxValue;
			}
			return b.Hist == null ? 0 : RM_LevelSolve.PondCapacity(b.Hist);
		}

		/// <summary>Largest x in [0, max] that leaves the source at or above both the receiver and <paramref name="floor"/>.</summary>
		public static long Equilibrium(RM_LevelBody from, long wf, RM_LevelBody to, long wt, double floor, long max)
		{
			bool Ok(long x)
			{
				double sf = Surface(from, from.Limitless ? wf : wf - x);
				double st = Surface(to, to.Limitless ? wt : wt + x);
				return sf >= st && sf >= floor;
			}
			if (max <= 0 || !Ok(0))
			{
				return 0;
			}
			if (Ok(max))
			{
				return max;
			}
			long lo = 0, hi = max;   // Ok(lo), !Ok(hi)
			while (hi - lo > 1)
			{
				long mid = lo + (hi - lo) / 2;
				if (Ok(mid))
				{
					lo = mid;
				}
				else
				{
					hi = mid;
				}
			}
			return lo;
		}

		/// <summary>One cycle. Updates <paramref name="bodies"/>' Water and Fluid in place, advances <paramref name="cursor"/>,
		/// and returns the moves in the order they were planned (the caller applies them in that order). <paramref name="state"/>
		/// (optional, one per link) says what each visited link did. <paramref name="limitlessNet"/> gains what limitless bodies
		/// received minus what they gave (the explicit exchange the conservation check accounts for).</summary>
		public static List<RM_LevelMove> Plan(IList<RM_LevelBody> bodies, IList<RM_LevelLink> links, long ratePerLink, int maxLinks,
			ref int cursor, RM_LevelLinkState[] state, ref long limitlessNet)
		{
			var moves = new List<RM_LevelMove>();
			int n = links.Count;
			if (n == 0 || ratePerLink <= 0 || maxLinks <= 0)
			{
				return moves;
			}
			int visit = Math.Min(n, maxLinks);
			int every = (n + visit - 1) / visit;
			long rate = ratePerLink * Math.Min(every, MaxCatchUp);
			if (cursor < 0 || cursor >= n)
			{
				cursor = 0;
			}
			if (state != null)
			{
				for (int i = 0; i < state.Length; i++)
				{
					state[i] = RM_LevelLinkState.Skipped;
				}
			}
			for (int k = 0; k < visit; k++)
			{
				int li = (cursor + k) % n;
				RM_LevelLink l = links[li];
				RM_LevelLinkState s = Step(bodies, l, li, rate, moves, ref limitlessNet);
				if (state != null && li < state.Length)
				{
					state[li] = s;
				}
			}
			cursor = (cursor + visit) % n;
			return moves;
		}

		private static RM_LevelLinkState Step(IList<RM_LevelBody> bodies, RM_LevelLink l, int li, long rate, List<RM_LevelMove> moves,
			ref long limitlessNet)
		{
			if (l.A < 0 || l.B < 0 || l.A >= bodies.Count || l.B >= bodies.Count)
			{
				return RM_LevelLinkState.Skipped;
			}
			RM_LevelBody a = bodies[l.A], b = bodies[l.B];
			if (l.A == l.B || a.Key == b.Key)
			{
				return RM_LevelLinkState.SameBody;
			}
			if (a.Limitless && b.Limitless)
			{
				return RM_LevelLinkState.Level;
			}
			double sa = Surface(a, a.Water), sb = Surface(b, b.Water);
			if (Math.Abs(sa - sb) < LevelTolerance)
			{
				return RM_LevelLinkState.Level;
			}
			bool aHigh = sa > sb;
			int fi = aHigh ? l.A : l.B, ti = aHigh ? l.B : l.A;
			RM_LevelBody from = bodies[fi], to = bodies[ti];
			double floor = aHigh ? l.FloorA : l.FloorB;
			long take = aHigh ? l.TakeA : l.TakeB;
			long room = aHigh ? l.RoomB : l.RoomA;
			if (from.Fluid == null || (!from.Limitless && from.Water <= 0))
			{
				return RM_LevelLinkState.IntakeExposed;
			}
			if (to.Fluid != null && !ReferenceEquals(to.Fluid, from.Fluid) && !Equals(to.Fluid, from.Fluid))
			{
				return RM_LevelLinkState.DifferentLiquids;
			}
			if (Math.Max(aHigh ? sa : sb, 0.0) <= floor && !from.Limitless)
			{
				return RM_LevelLinkState.IntakeExposed;
			}
			long max = rate;
			if (!from.Limitless)
			{
				max = Math.Min(max, from.Water);
			}
			if (!to.Limitless)
			{
				max = Math.Min(max, Capacity(to) - to.Water);
			}
			max = Math.Min(max, Math.Max(0, take));
			max = Math.Min(max, Math.Max(0, room));
			if (max <= 0)
			{
				return (!to.Limitless && Capacity(to) - to.Water <= 0) || room <= 0 ? RM_LevelLinkState.Full : RM_LevelLinkState.IntakeExposed;
			}
			// the equilibrium is searched without the rate cap, so the half-way rule is about the true gap, not the rate
			long eqMax = long.MaxValue;
			if (!from.Limitless)
			{
				eqMax = from.Water;
			}
			if (!to.Limitless)
			{
				eqMax = Math.Min(eqMax, Capacity(to) - to.Water);
			}
			if (eqMax == long.MaxValue)
			{
				eqMax = long.MaxValue / 4;
			}
			long eq = Equilibrium(from, from.Water, to, to.Water, floor, eqMax);
			long half = (eq + 1) / 2;
			long x = Math.Min(max, half);
			if (x <= 0)
			{
				return eq <= 0 && Surface(from, from.Water) <= floor ? RM_LevelLinkState.IntakeExposed : RM_LevelLinkState.Level;
			}
			if (!from.Limitless)
			{
				from.Water -= x;
			}
			else
			{
				limitlessNet -= x;
			}
			if (!to.Limitless)
			{
				to.Water += x;
			}
			else
			{
				limitlessNet += x;
			}
			if (to.Fluid == null)
			{
				to.Fluid = from.Fluid;
			}
			moves.Add(new RM_LevelMove { Link = li, From = fi, To = ti, Dl = x });
			return RM_LevelLinkState.Flowing;
		}

		/// <summary>Σ water over the finite bodies (the conserved quantity, with the limitless net).</summary>
		public static long FiniteTotal(IList<RM_LevelBody> bodies)
		{
			long s = 0;
			foreach (RM_LevelBody b in bodies)
			{
				if (!b.Limitless)
				{
					s += b.Water;
				}
			}
			return s;
		}

		/// <summary>Potential energy of the finite bodies (Σ over each body of the integral of surface over volume, in coarse
		/// steps of the histogram's bands): non-increasing under any cycle. Used by the selftest as the no-oscillation witness.</summary>
		public static double Energy(IList<RM_LevelBody> bodies)
		{
			double e = 0.0;
			foreach (RM_LevelBody b in bodies)
			{
				if (b.Limitless || b.Hist == null || b.Hist.Length <= 1)
				{
					continue;
				}
				// water laid band by band from the deepest: each dL at height h contributes h (the centre of its layer)
				long left = b.Water;
				int mx = b.Hist.Length - 1;
				for (int band = mx; band >= 1 && left > 0; band--)
				{
					long cap = (long)RM_LevelSolve.U * b.Hist[band];
					if (cap <= 0)
					{
						continue;
					}
					long put = Math.Min(left, cap);
					double bottom = -(double)band * RM_LevelSolve.U;
					double top = bottom + put / (double)b.Hist[band];
					e += put * (bottom + top) / 2.0;
					left -= put;
				}
			}
			return e;
		}
	}
}
