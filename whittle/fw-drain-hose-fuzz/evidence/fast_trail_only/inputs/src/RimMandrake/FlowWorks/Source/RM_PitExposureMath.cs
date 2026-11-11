using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_TEMPERATURE_SOFTENING_1, redesigned 2026-10-11 ("exposed to the elements" on vanilla's own temperature path,
	/// design/RimMandrake/pit_exposure_to_the_elements_2026-10-11.md). Verse-free so Source/SelfTest/ compiles THIS file.
	/// Three dials: the temperature coupling of an unroofed pit room (kept until a live check shows vanilla's outdoor
	/// rule already covers it), the comfort-range narrowing an open pit costs (owner Q1, 17:25: 8 °C each way), and the
	/// resistance a prisoner loses only while the elements actually hurt (owner Q2). Each number is a Mod Setting.
	/// </summary>
	public static class RM_PitExposureMath
	{
		/// <summary>PROVISIONAL. Pit-room cells fraction at/above which a room counts as a pit room.</summary>
		public const float PitRoomFraction = 0.5f;

		/// <summary>PROVISIONAL. Guest resistance lost per interval while hurting (x the Mod Setting rate).</summary>
		public const float ResistanceLossPerInterval = 0.05f;

		/// <summary>Owner Q1 (card, 2026-10-11 17:25): an open pit narrows the comfortable range by 8 °C each way.</summary>
		public const float DefaultNarrowing = 8f;

		/// <summary>Vanilla GenTemperature.SafeTemperatureRange: the comfortable range widened by 10 °C each side.</summary>
		public const float VanillaSafeMargin = 10f;

		/// <summary>Coupling multiplier applied to the vanilla no-roof equalisation step; never weakens it.</summary>
		public static float Coupling(float multiplier)
		{
			return multiplier > 1f ? multiplier : 1f;
		}

		/// <summary>A room is a pit room when at least <see cref="PitRoomFraction"/> of its cells are dug D=4.</summary>
		public static bool IsPitRoom(int superdeepCells, int totalCells)
		{
			return totalCells > 0 && superdeepCells >= (int)Math.Ceiling(totalCells * PitRoomFraction);
		}

		/// <summary>The setting, made safe: 0..15 °C (NaN = 0). The hediff's two statOffsets are +this and -this.</summary>
		public static float Narrowing(float setting)
		{
			return float.IsNaN(setting) || setting < 0f ? 0f : (setting > 15f ? 15f : setting);
		}

		/// <summary>The safe range vanilla's Heatstroke and Hypothermia givers read, for a pawn whose comfortable range is
		/// [<paramref name="comfyMin"/>, <paramref name="comfyMax"/>] before the pit, narrowed by <paramref name="narrowing"/>
		/// (the hediff's statOffsets: ComfyTemperatureMin +n, ComfyTemperatureMax -n). Both bounds move by exactly n.</summary>
		public static void SafeRange(float comfyMin, float comfyMax, float narrowing, out float safeMin, out float safeMax)
		{
			float n = Narrowing(narrowing);
			safeMin = comfyMin + n - VanillaSafeMargin;
			safeMax = comfyMax - n + VanillaSafeMargin;
		}

		/// <summary>Owner Q2 (card, 2026-10-11 17:25): a prisoner's resistance falls only while the elements actually hurt:
		/// a vanilla Heatstroke or Hypothermia is present (active), or the pawn stands outside its safe range so one is
		/// building (rising). Merely being exposed in mild weather costs nothing.</summary>
		public static bool ElementsHurting(bool heatstrokeOrHypothermia, float ambient, float safeMin, float safeMax)
		{
			return heatstrokeOrHypothermia || ambient > safeMax || ambient < safeMin;
		}

		/// <summary>Resistance after one hurting interval, floored at 0; rate is the Mod Setting multiplier.</summary>
		public static float NextResistance(float resistance, float rateMultiplier)
		{
			float r = resistance - ResistanceLossPerInterval * (rateMultiplier > 0f ? rateMultiplier : 0f);
			return r < 0f ? 0f : r;
		}
	}
}
