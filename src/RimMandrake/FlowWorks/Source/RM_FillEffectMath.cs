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


		/// <summary>Fraction of the cell's depth that is liquid, 0..1. <paramref name="fill"/> is in notches and may be fractional
		/// (LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD: the cell's decilitres ÷ a notch, so a 4.5 cm sheet counts as 0.09).</summary>
		public static float FillFraction(float fill, int depth)
		{
			if (fill <= 0 || depth <= 0)
			{
				return 0f;
			}
			return fill >= depth ? 1f : (float)fill / depth;
		}

		/// <summary>Toxic buildup added per check by a poison fluid: its per-day rate at brim, times the fill
		/// fraction, reduced by the pawn's toxic environment resistance. Any depth: standing in it is enough.</summary>
		public static float ToxinPerCheck(float fill, int depth, float toxicPerDayAtBrim, float resistance, bool flying)
		{
			if (flying || fill <= 0 || toxicPerDayAtBrim <= 0f)
			{
				return 0f;
			}
			float r = resistance < 0f ? 0f : (resistance > 1f ? 1f : resistance);
			return toxicPerDayAtBrim * FillFraction(fill, depth) * (1f - r) * IntervalTicks / 60000f;
		}
	}

	/// <summary>FLOWWORKS_REVIEW_LOOKS_ROUND_1 items 7 and 10 — Verse-free numbers for liquid bubbles and for seeing a
	/// cut's floor through clear liquid.</summary>
	public static class RM_LiquidLookMath
	{
		/// <summary>Most bubbles one sample may throw in a tick (bounds the cost at any zoom).</summary>
		public const int MaxBubblesPerSample = 4;

		/// <summary>Bubbles one sampled cell throws this tick: it stands for <paramref name="cellsRepresented"/> cells in
		/// view, each throwing <paramref name="perCellPerSecond"/> x <paramref name="density"/> a second (60 ticks).
		/// The fractional part is rolled with <paramref name="roll"/> (0..1).</summary>
		public static int BubblesThisTick(float perCellPerSecond, float density, float cellsRepresented, float roll)
		{
			if (!(perCellPerSecond > 0f) || !(density > 0f) || !(cellsRepresented > 0f))
			{
				return 0;
			}
			float expected = perCellPerSecond * density * cellsRepresented / 60f;
			int n = (int)Math.Floor(expected);
			if (roll < expected - n)
			{
				n++;
			}
			return n > MaxBubblesPerSample ? MaxBubblesPerSample : n;
		}
	}
}
