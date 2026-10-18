using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE (plan P7 of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG). Owner R7 (2026-10-17, by card):
	/// <i>"The four rules keyed to 2 m deep (drowning, fall damage, spikes, shooting) → relative to the height difference."</i>
	/// The FORMS are the plan's veto-able defaults V2-V6 (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md` §3,
	/// card `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES`). Verse-free on purpose: Source/SelfTest compiles THIS file.
	///
	/// Depths are in NOTCHES (0.5 m, <see cref="RM_Volume.MetresPerNotch"/>), 0 = undug ground, larger = deeper. A height
	/// difference is a difference of notches; nothing here reads an absolute depth except as one end of a difference.
	/// </summary>
	public static class RM_RelativeRulesMath
	{
		public const float MetresPerNotch = RM_Volume.MetresPerNotch;

		/// <summary>Metres to whole notches, rounded to the nearest half-metre, never below <paramref name="min"/>.</summary>
		public static int Notches(float metres, int min = 1)
		{
			if (float.IsNaN(metres) || float.IsInfinity(metres))
			{
				return min;
			}
			int n = (int)Math.Round(metres / MetresPerNotch, MidpointRounding.AwayFromZero);
			return n < min ? min : n;
		}

		// ── V4 spikes (and the pit cover): a sheer drop to a neighbour ──────────────────────────────────────────

		private static readonly int[] Dx8 = { 0, 1, 0, -1, 1, 1, -1, -1 };
		private static readonly int[] Dz8 = { 1, 0, -1, 0, 1, -1, -1, 1 };

		/// <summary>The tallest wall standing over this cell: the most notches any of its 8 neighbours is HIGHER (shallower) than
		/// it. 0 on flat ground or at the top of a wall. <paramref name="depthAt"/> answers -1 out of bounds (skipped).</summary>
		public static int TallestWallOver(Func<int, int, int> depthAt, int x, int z)
		{
			int here = depthAt(x, z);
			if (here <= 0)
			{
				return 0;
			}
			int best = 0;
			for (int k = 0; k < 8; k++)
			{
				int n = depthAt(x + Dx8[k], z + Dz8[k]);
				if (n < 0)
				{
					continue;
				}
				int rise = here - n;
				if (rise > best)
				{
					best = rise;
				}
			}
			return best;
		}

		/// <summary>V4 (owner R7, relative): spikes stand on any cell with a sheer drop of <paramref name="minDropNotches"/> (2 m
		/// shipped) or more to a neighbour, at ANY absolute depth: the 2 m floor of a pit, the 7 m core under a 4 m ledge (3 m
		/// drop), never a gentle 0.5 m staircase however deep it goes.</summary>
		public static bool SheerDropAt(Func<int, int, int> depthAt, int x, int z, int minDropNotches)
		{
			return TallestWallOver(depthAt, x, z) >= Math.Max(1, minDropNotches);
		}

		// ── V3 falls: by metres fallen ────────────────────────────────────────────────────────────────────────

		/// <summary>The fall size every multiplier is relative to: today's full fall, a 2 m drop.</summary>
		public const float FallReferenceMetres = 2f;

		/// <summary>V3 default: +50 % of the 2 m fall for every metre past 2 m.</summary>
		public const float DefaultFallPerMetrePast = 0.5f;

		/// <summary>V3 default: never more than 4× the 2 m fall (reached at 8 m).</summary>
		public const float DefaultFallCap = 4f;

		/// <summary>V3 (owner R7): the fall's damage as a multiple of today's 2 m fall, by METRES FALLEN (never by the cell's
		/// depth, never by the dig cap). Up to 2 m: today's relative scale, linear (0.5 m = 0.25, 2 m = 1). Past 2 m: +
		/// <paramref name="perMetrePast"/> a metre, capped at <paramref name="cap"/> (shipped 0.5 and 4: 3 m = 1.5, 7 m = 3.5,
		/// 8 m = 4, 20 m = 4). Blunt damage through the normal pipeline; never instant death (the caller deals it).</summary>
		public static float FallScale(float metresFallen, float perMetrePast = DefaultFallPerMetrePast, float cap = DefaultFallCap)
		{
			if (!(metresFallen > 0f))
			{
				return 0f;
			}
			if (metresFallen <= FallReferenceMetres)
			{
				return metresFallen / FallReferenceMetres;
			}
			float c = cap < 1f || float.IsNaN(cap) ? 1f : cap;
			float s = 1f + Math.Max(0f, perMetrePast) * (metresFallen - FallReferenceMetres);
			return s > c ? c : s;
		}

		/// <summary>The same for a drop in notches.</summary>
		public static float FallScaleNotches(int dropNotches, float perMetrePast = DefaultFallPerMetrePast, float cap = DefaultFallCap)
		{
			return FallScale(dropNotches * MetresPerNotch, perMetrePast, cap);
		}

		// ── V2 drowning: water against the creature's height ────────────────────────────────────────────────

		/// <summary>Creature height H in metres by climb band (RM_PitTrapMath.ClimbLimit with no climber/leaper bonus): small (K 1:
		/// rat, cat, dog, child), person (K 2), large (K 3: muffalo, bear), huge (K 4: thrumbo). PROVISIONAL. One size system for
		/// climbing and for water, so a creature that is "large" for the wall is "large" for the water. A person's 1.75 m puts
		/// the head under at 1.575 m: the old "2 m and deeper" band (anything past the 1.5 m chest notch). A rat's 0.5 m puts its
		/// head under at 0.45 m (play doc §2.4: "for a rat, 0.5 m is already over its head").</summary>
		public static readonly float[] HeightByBand = { 0f, 0.5f, 1.75f, 2.5f, 3.5f };

		public static float HeightMetres(int sizeBand)
		{
			int b = sizeBand < 1 ? 1 : (sizeBand >= HeightByBand.Length ? HeightByBand.Length - 1 : sizeBand);
			return HeightByBand[b];
		}

		/// <summary>V2 defaults: the head goes under at 0.9 H standing, 0.2 H lying down (downed, asleep, in bed).</summary>
		public const float DefaultHeadFraction = 0.9f;

		public const float DefaultLyingFraction = 0.2f;

		/// <summary>The water depth, in metres, at which this creature's head is under.</summary>
		public static float HeadUnderMetres(float heightMetres, bool lying, float headFraction = DefaultHeadFraction,
			float lyingFraction = DefaultLyingFraction)
		{
			float f = lying ? lyingFraction : headFraction;
			if (!(f > 0f))
			{
				f = lying ? DefaultLyingFraction : DefaultHeadFraction;
			}
			return heightMetres * f;
		}

		/// <summary>Does water of this depth (metres above the creature's floor) cover its head? Strictly over: a person stands in
		/// exactly 1.5 m of water with its head clear.</summary>
		public static bool HeadUnder(float waterMetres, float heightMetres, bool lying, float headFraction = DefaultHeadFraction,
			float lyingFraction = DefaultLyingFraction)
		{
			return waterMetres > HeadUnderMetres(heightMetres, lying, headFraction, lyingFraction) + 1e-4f;
		}

		/// <summary>A neighbour the creature can get to and stand in with its head clear: a walkable step (|Δ| within its climb
		/// limit, or a ramp/ladder joining) into water under its head (standing). Δ in notches.</summary>
		public static bool ExitInReach(int fromD, int toD, int climbLimit, bool joined, float waterThereMetres, float heightMetres,
			float headFraction = DefaultHeadFraction)
		{
			if (!joined && Math.Abs(fromD - toD) > Math.Max(1, climbLimit))
			{
				return false;
			}
			return !HeadUnder(waterThereMetres, heightMetres, false, headFraction);
		}

		/// <summary>PROVISIONAL: water over the head drowns a non-swimmer in about one in-game hour (severity 1 = death; 24 a day =
		/// 0.1 a 250-tick check).</summary>
		public const float DrowningPerDay = 24f;

		/// <summary>Ticks between drowning checks (= RM_FillEffectMath.IntervalTicks, the fill-effects pass that applies it).</summary>
		public const int DrowningCheckTicks = 250;

		/// <summary>One drowning rule for pits AND (P12, DEEP_WATER_BUILD_SWIM_OR_SINK) lakes: severity added per check (1 =
		/// death). Zero unless the head is under, the creature keeps no head above water (<paramref name="keepsHeadUp"/>: a
		/// swimmer today; P12 plugs swim ability and exhaustion in there), is not flying, and (unless it is lying down: a downed
		/// pawn reaches nothing) has no exit in reach. When it drowns it drowns at the brim rate: a pit 1 cm over the head and a
		/// lake 10 m deep are the same to a head under water. "One litre in a 7 m pit cannot drown its occupant."</summary>
		public static float DrowningPerCheck(bool headUnder, bool lying, bool keepsHeadUp, bool flying, bool exitInReach,
			float rateMultiplier)
		{
			if (!headUnder || keepsHeadUp || flying || (!lying && exitInReach))
			{
				return 0f;
			}
			return DrowningPerDay * Math.Max(0f, rateMultiplier) * DrowningCheckTicks / 60000f;
		}

		// ── V5 shooting: blocked across a cliff edge ───────────────────────────────────────────────────────────

		/// <summary>V5 (owner R7, relative; ruling 23 restated by height difference). A shot is blocked when some square strictly
		/// BETWEEN the two ends stands at least <paramref name="cliffNotches"/> (2 m shipped: more than a person's height)
		/// above the LOWER end. So, across a cliff edge, the one below shoots only those standing at the edge above (no higher
		/// square between them) and the one above shoots down only from the edge; two pawns on one basin floor, or two on the
		/// surface across a pit, fight normally. Adjacent squares always may (nothing between). The line is a Bresenham walk,
		/// run only when the lower end is at least a cliff deep (the early-out every flat map takes). depthAt: notches, an
		/// intact cover reading as ground (0).</summary>
		public static bool ShotBlocked(Func<int, int, int> depthAt, int sx, int sz, int tx, int tz, int cliffNotches)
		{
			int cliff = Math.Max(1, cliffNotches);
			int ds = depthAt(sx, sz);
			int dt = depthAt(tx, tz);
			int lower = ds > dt ? ds : dt;
			if (lower < cliff)
			{
				return false; // nothing on this map can stand a cliff above a floor shallower than a cliff
			}
			int adx = Math.Abs(tx - sx), adz = Math.Abs(tz - sz);
			if (adx <= 1 && adz <= 1)
			{
				return false;
			}
			int stepX = tx > sx ? 1 : -1, stepZ = tz > sz ? 1 : -1;
			int err = adx - adz;
			int x = sx, z = sz;
			int limit = adx + adz + 2;
			for (int guard = 0; guard < limit; guard++)
			{
				int e2 = 2 * err;
				if (e2 > -adz)
				{
					err -= adz;
					x += stepX;
				}
				if (e2 < adx)
				{
					err += adx;
					z += stepZ;
				}
				if (x == tx && z == tz)
				{
					return false;
				}
				if (lower - depthAt(x, z) >= cliff)
				{
					return true;
				}
			}
			return false;
		}

		// ── V6 pit rooms ────────────────────────────────────────────────────────────────────────────────────

		/// <summary>A pit room is a person-band pocket whose floor is at least <paramref name="minDepthNotches"/> down: the
		/// setting pitRoomMinDepthMetres, 3.0 m (6) shipped for a person (PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER, owner card
		/// 2026-10-18), 0 = any depth.</summary>
		public static bool PitRoomCell(bool personPocket, int dugDepth, int minDepthNotches)
		{
			return personPocket && dugDepth > 0 && dugDepth >= minDepthNotches;
		}

		// ── the free-fall step price (RM_PitTrapMath.DryStepBaseCost) ───────────────────────────────────────────

		/// <summary>A dry walked step DOWN is priced as a fall (free) when the drop itself is a sheer
		/// <paramref name="fallNotches"/> or more (2 m), never because the destination is deep (a 4 m ledge to a 7 m core is a
		/// 3 m fall; a 2 m floor to a 2.5 m floor is a half-metre climb).</summary>
		public static bool StepIsAFall(int fromD, int toD, int fallNotches)
		{
			return toD - fromD >= Math.Max(1, fallNotches);
		}
	}
}
