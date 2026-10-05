using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_TEMPERATURE_SOFTENING_1 — the arithmetic, Verse-free so Source/SelfTest/ compiles THIS file.
	/// Two independent dials ([H]): the temperature coupling of an unroofed pit room, and the exposure
	/// that wears a prisoner's resistance down. 🔴 Every constant here is PROVISIONAL (the item says
	/// numbers go to the owner as a proposal); each is a Mod Setting.
	/// </summary>
	public static class RM_PitExposureMath
	{
		/// <summary>PROVISIONAL. Pit-room cells fraction at/above which a room counts as a pit room.</summary>
		public const float PitRoomFraction = 0.5f;

		/// <summary>PROVISIONAL. RM_PitExposure severity gained per exposure interval (250 ticks): ~0 -> 1 in ~21 h.</summary>
		public const float SeverityGainPerInterval = 0.012f;

		/// <summary>PROVISIONAL. Severity shed per interval once sheltered.</summary>
		public const float SeverityDecayPerInterval = 0.03f;

		/// <summary>PROVISIONAL. Guest resistance lost per interval while exposed (x the Mod Setting rate).</summary>
		public const float ResistanceLossPerInterval = 0.05f;

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

		public static float NextSeverity(float current, bool exposed)
		{
			float s = exposed ? current + SeverityGainPerInterval : current - SeverityDecayPerInterval;
			return s < 0f ? 0f : (s > 1f ? 1f : s);
		}

		/// <summary>Resistance after one exposed interval, floored at 0; rate is the Mod Setting multiplier.</summary>
		public static float NextResistance(float resistance, float rateMultiplier)
		{
			float r = resistance - ResistanceLossPerInterval * (rateMultiplier > 0f ? rateMultiplier : 0f);
			return r < 0f ? 0f : r;
		}
	}
}
