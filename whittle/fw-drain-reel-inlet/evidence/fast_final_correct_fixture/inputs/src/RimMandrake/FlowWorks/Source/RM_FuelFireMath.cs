using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>How a burnable liquid burns once its settings are applied (<see cref="RM_FuelFireMath.Classify"/>).</summary>
	public enum RM_FuelBurn
	{
		/// <summary>Tar and oil: a creeping front and a level a day (ruling 7).</summary>
		Ordinary,
		/// <summary>Chemfuel: a moat of gasoline. Fast front, big flames, a heat wave and a burn-down in seconds.</summary>
		Inferno,
		/// <summary>Astrofuel: the whole connected body goes up as one rippling chain of blasts.</summary>
		Detonation
	}

	/// <summary>
	/// CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL — the Verse-free arithmetic of the two fuel fires, so the C# SelfTest drives the
	/// production numbers (FuelFireChecks). Owner, by card 2026-10-15: chemfuel is "a powerful, intense fire that should feel
	/// like you lit a moat of gasoline ... huge flames tremendous heat that ignites anything else nearby and burns the
	/// Chemfuel down rapidly"; astrofuel is "a massive explosion that burns all of it up almost instantly ... An ultimate
	/// spatially continuous bomb with shockwaves and intense heat". Every number here is PROVISIONAL (auto-decided
	/// 2026-10-15) and scaled by a Mod Settings dial.
	/// </summary>
	public static class RM_FuelFireMath
	{
		// ── which fire ──────────────────────────────────────────────────────

		/// <summary>The authored kind with the two settings applied. Inferno off: chemfuel burns like oil (ordinary).
		/// Detonation off: astrofuel still burns, as an inferno while that is on, else ordinary.</summary>
		public static RM_FuelBurn Classify(bool authoredInferno, bool authoredDetonation, bool infernoOn, bool detonationOn)
		{
			if (authoredDetonation)
			{
				return detonationOn ? RM_FuelBurn.Detonation : infernoOn ? RM_FuelBurn.Inferno : RM_FuelBurn.Ordinary;
			}
			if (authoredInferno)
			{
				return infernoOn ? RM_FuelBurn.Inferno : RM_FuelBurn.Ordinary;
			}
			return RM_FuelBurn.Ordinary;
		}

		// ── chemfuel: the inferno ───────────────────────────────────────────

		/// <summary>Ticks for a lit chemfuel channel cell to lose one fill level at burn rate 1: 300 ticks (5 s), so a brimming
		/// 4-level cell is gone in 20 s and a superdeep one well inside a minute. A rate, like ruling 7, only ~200x faster.</summary>
		public const int InfernoTicksPerLevel = 300;

		public static int InfernoTicksPerLevelAt(float burnRate)
		{
			float r = burnRate < 0.05f ? 0.05f : burnRate;
			return Math.Max(1, (int)Math.Round(InfernoTicksPerLevel / r));
		}

		/// <summary>The front's step multiplier for an inferno: the global front speed times the chemfuel spread dial.</summary>
		public static float InfernoFrontSpeed(float globalFrontSpeed, float spreadSpeed)
		{
			float g = globalFrontSpeed <= 0.01f ? 0.01f : globalFrontSpeed;
			float s = spreadSpeed <= 0.01f ? 0.01f : spreadSpeed;
			return g * s;
		}

		/// <summary>Heat pushed per lit cell per effects check (60 ticks). Ordinary liquid fire pushes 60; an inferno pushes
		/// eight times that at intensity 1 — a moat that turns the air beside it into an oven.</summary>
		public static float InfernoHeatPerCheck(float intensity)
		{
			return 480f * Clamp(intensity, 0.1f, 5f);
		}

		/// <summary>How far past the moat the flames reach things that burn: 2.9 cells at intensity 1 (a 3-cell halo),
		/// clamped to 1.5..7.9.</summary>
		public static float InfernoIgniteRadius(float intensity)
		{
			return Clamp(2.9f * intensity, 1.5f, 7.9f);
		}

		/// <summary>Size of the vanilla Fire the inferno starts on a flammable thing in that halo.</summary>
		public static float InfernoSpawnedFireSize(float intensity)
		{
			return Clamp(0.6f * intensity, 0.2f, 1.75f);
		}

		/// <summary>Halo cells tried per lit cell per effects check, and the most tried in one check over the whole map, so a
		/// 1000-cell lake of chemfuel stays one bounded walk.</summary>
		public const int InfernoHaloTriesPerCell = 3;
		public const int InfernoHaloTriesPerCheck = 360;

		/// <summary>A pawn standing in burning chemfuel catches almost surely; one beside the moat (within 1.5) often.</summary>
		public const float InfernoAttachInCell = 0.9f;
		public const float InfernoAttachBeside = 0.3f;

		/// <summary>Lit cells at which an inferno counts as a LARGE fire (the Utinni layer's "come and look" signal).</summary>
		public const int LargeInfernoCells = 40;

		// ── astrofuel: the detonation ───────────────────────────────────────

		/// <summary>Ticks between rings of the blast (one ring = one cell of graph distance from where it was lit): 1 tick,
		/// so a 60-cell channel is gone in 1 s and a 200-cell moat in ~3 s, and it reads as a shockwave running down it,
		/// never as one flash.</summary>
		public const int DetonationTicksPerRing = 1;

		/// <summary>Per-tick budgets: vanilla explosions started, and cells emptied. A body bigger than these just takes more
		/// ticks; the game never freezes on one tick.</summary>
		public const int MaxBlastsPerTick = 4;
		public const int MaxCellsConsumedPerTick = 400;

		/// <summary>Most explosions one detonation may spawn; past it the anchors spread out (spacing grows) instead.</summary>
		public const int MaxBlastsPerDetonation = 240;

		/// <summary>Most cells one detonation walks; the rest of a bigger body is lit by the blasts at its edge and goes up as
		/// the next detonation.</summary>
		public const int MaxDetonationCells = 20000;

		/// <summary>Spacing between blast anchors (Chebyshev cells): every cell lies within one blast's radius.</summary>
		public const int BaseBlastSpacing = 3;

		public static float BlastRadius(float scale)
		{
			return Clamp(3.9f * (float)Math.Sqrt(Clamp(scale, 0.1f, 4f)), 1.9f, 7.9f);
		}

		/// <summary>The radius actually used: the dial's radius, grown with the anchor spacing on a body so big that the blast
		/// cap spread the anchors out (so the blasts still touch), never past 7.9.</summary>
		public static float BlastRadiusFor(float scale, int spacing)
		{
			return Clamp(Math.Max(BlastRadius(scale), spacing * 0.8f), 1.9f, 7.9f);
		}

		/// <summary>Bomb damage per blast: vanilla's Bomb default (50) times the dial.</summary>
		public static int BlastDamage(int bombDefault, float scale)
		{
			return Math.Max(1, (int)Math.Round(bombDefault * Clamp(scale, 0.1f, 4f)));
		}

		/// <summary>Heat pushed per emptied cell — "intense heat" (a vanilla fire pushes ~10-20 per check).</summary>
		public static float DetonationHeatPerCell(float scale)
		{
			return 220f * Clamp(scale, 0.1f, 4f);
		}

		/// <summary>Knockback: pawns this close to a blast are thrown this many cells (and staggered) a few ticks after it,
		/// once its damage has landed. At most this many per blast.</summary>
		public const int KnockbackCells = 3;
		public const int KnockbackDelayTicks = 6;
		public const int KnockbackPerBlast = 6;
		public const int StaggerTicks = 120;

		/// <summary>The schedule of one detonation, over a body already walked breadth-first from where it was lit.
		/// <paramref name="ring"/>[k] is cell k's graph distance; x/z its position; cells in BFS order (ring never decreases).
		/// Fills <paramref name="consumeTick"/> (offset from the light) for every cell and <paramref name="blastTick"/>
		/// (-1 = no blast) so that: every cell is emptied exactly once; no tick empties more than maxCellsPerTick cells or
		/// starts more than maxBlastsPerTick blasts; at most maxBlasts blasts in all; every cell lies within
		/// <c>spacing</c> (Chebyshev) of an anchor. Returns the spacing used.</summary>
		public static int PlanDetonation(int[] ring, int[] x, int[] z, int ticksPerRing, int maxCellsPerTick, int maxBlastsPerTick,
			int maxBlasts, int baseSpacing, int[] consumeTick, int[] blastTick)
		{
			int n = ring.Length;
			// consume: ring time, pushed later while a tick is full (BFS order keeps it monotone)
			int tick = -1, used = 0;
			for (int k = 0; k < n; k++)
			{
				int want = Math.Max(0, ring[k] * Math.Max(1, ticksPerRing));
				if (want > tick)
				{
					tick = want;
					used = 0;
				}
				if (used >= Math.Max(1, maxCellsPerTick))
				{
					tick++;
					used = 0;
				}
				consumeTick[k] = tick;
				used++;
			}
			// anchors: greedy cover in BFS order with a bucket grid; widen the spacing until the count fits
			int spacing = Math.Max(1, baseSpacing);
			bool[] anchor = new bool[n];
			while (true)
			{
				int count = ChooseAnchors(x, z, spacing, anchor);
				if (count <= Math.Max(1, maxBlasts) || spacing >= 64)
				{
					break;
				}
				spacing++;
			}
			// blast ticks: at the anchor's own consume tick, pushed later while a tick has its quota
			// (anchors come in BFS order, so their consume ticks never decrease and one cursor suffices)
			int quota = Math.Max(1, maxBlastsPerTick);
			int cursor = -1, inCursor = 0;
			for (int k = 0; k < n; k++)
			{
				if (!anchor[k])
				{
					blastTick[k] = -1;
					continue;
				}
				if (consumeTick[k] > cursor)
				{
					cursor = consumeTick[k];
					inCursor = 0;
				}
				else if (inCursor >= quota)
				{
					cursor++;
					inCursor = 0;
				}
				blastTick[k] = cursor;
				inCursor++;
			}
			return spacing;
		}

		/// <summary>Greedy anchors: a cell is an anchor unless an earlier anchor lies within spacing-1 (Chebyshev). Bucketed by
		/// spacing so each test reads 9 buckets. Returns the count.</summary>
		public static int ChooseAnchors(int[] x, int[] z, int spacing, bool[] anchor)
		{
			int n = x.Length;
			int s = Math.Max(1, spacing);
			Dictionary<long, List<int>> buckets = new Dictionary<long, List<int>>();
			int count = 0;
			for (int k = 0; k < n; k++)
			{
				int bx = FloorDiv(x[k], s), bz = FloorDiv(z[k], s);
				bool near = false;
				for (int dx = -1; dx <= 1 && !near; dx++)
				{
					for (int dz = -1; dz <= 1 && !near; dz++)
					{
						if (!buckets.TryGetValue(Key(bx + dx, bz + dz), out List<int> l))
						{
							continue;
						}
						foreach (int a in l)
						{
							if (Math.Max(Math.Abs(x[a] - x[k]), Math.Abs(z[a] - z[k])) < s)
							{
								near = true;
								break;
							}
						}
					}
				}
				anchor[k] = !near;
				if (!near)
				{
					long key = Key(bx, bz);
					if (!buckets.TryGetValue(key, out List<int> own))
					{
						own = new List<int>();
						buckets[key] = own;
					}
					own.Add(k);
					count++;
				}
			}
			return count;
		}

		private static long Key(int bx, int bz)
		{
			return ((long)bx << 32) ^ (uint)bz;
		}

		private static int FloorDiv(int a, int b)
		{
			return a >= 0 ? a / b : -((-a + b - 1) / b);
		}

		private static float Clamp(float v, float lo, float hi)
		{
			return v < lo ? lo : v > hi ? hi : v;
		}
	}
}
