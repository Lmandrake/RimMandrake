using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_FILL_EFFECTS_1, Verse-free so the selftest drives the production numbers. What the fluid in a cell
	/// does to whoever stands in it, keyed to fill (owner Q3: fluids never mix, so one cell = one fluid = one
	/// effect). All rates PROVISIONAL.
	/// </summary>
	public static class RM_FillEffectMath
	{
		public const int IntervalTicks = 250;

		/// <summary>PROVISIONAL: a brimming D=4 pit drowns a non-swimmer in about one in-game hour
		/// (severity 1 = death; 24/day at full -> 0.1 per 250-tick check).</summary>
		public const float DrowningPerDayAtBrim = 24f;

		/// <summary>Fraction of the cell's depth that is liquid, 0..1.</summary>
		public static float FillFraction(int fill, int depth)
		{
			if (fill <= 0 || depth <= 0)
			{
				return 0f;
			}
			return fill >= depth ? 1f : (float)fill / depth;
		}

		/// <summary>Drowning severity added per check: only at SUPERDEEP (D=4) with F &gt; 0, never for a swimmer
		/// or a flier (the swimming test is the pawn's swimming graphic, never an "aquatic" substring).</summary>
		public static float DrowningPerCheck(int fill, int depth, bool superdeep, bool swimmer, bool flying,
			float rateMultiplier)
		{
			if (!superdeep || swimmer || flying || fill <= 0)
			{
				return 0f;
			}
			return DrowningPerDayAtBrim * Math.Max(0f, rateMultiplier) * FillFraction(fill, depth)
				* IntervalTicks / 60000f;
		}

		/// <summary>Toxic buildup added per check by a poison fluid: its per-day rate at brim, times the fill
		/// fraction, reduced by the pawn's toxic environment resistance. Any depth: standing in it is enough.</summary>
		public static float ToxinPerCheck(int fill, int depth, float toxicPerDayAtBrim, float resistance, bool flying)
		{
			if (flying || fill <= 0 || toxicPerDayAtBrim <= 0f)
			{
				return 0f;
			}
			float r = resistance < 0f ? 0f : (resistance > 1f ? 1f : resistance);
			return toxicPerDayAtBrim * FillFraction(fill, depth) * (1f - r) * IntervalTicks / 60000f;
		}
	}
}
