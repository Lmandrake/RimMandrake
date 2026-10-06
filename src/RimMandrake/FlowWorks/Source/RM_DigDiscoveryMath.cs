namespace RimMandrake.FlowWorks
{
	/// <summary>FLOWWORKS_QUARRY_DIGGING_1 — the Verse-free numbers of canal-dig discovery (selftested).
	/// Every value is PROVISIONAL (design §2a defaults), for the registry review sheet to set.</summary>
	public static class RM_DigDiscoveryMath
	{
		/// <summary>1.5% per cell-level cut at multiplier 1.</summary>
		public const float BaseChance = 0.015f;

		/// <summary>Of a deep cut over a deep deposit, the share of finds that are the deposit itself.</summary>
		public const float DeepShare = 0.5f;

		public const int LumpMin = 10;
		public const int LumpMax = 25;

		public static float Chance(float multiplier)
		{
			float c = BaseChance * (multiplier < 0f ? 0f : multiplier);
			return c > 1f ? 1f : c;
		}

		/// <summary>The exploit guard: a cut rolls only when it goes deeper than that cell ever rolled.</summary>
		public static bool RollsAt(int rolledDepth, int newDepth)
		{
			return newDepth > rolledDepth;
		}

		/// <summary>Owner card: deep and superdeep cuts can reach deep-drill minerals.</summary>
		public static bool ReachesDeep(int depth)
		{
			return depth >= 3;
		}

		/// <summary>10–25 units from a uniform roll in [0,1), clamped to the stack limit.</summary>
		public static int LumpSize(float roll01, int stackLimit)
		{
			if (roll01 < 0f) roll01 = 0f;
			if (roll01 >= 1f) roll01 = 0.9999f;
			int n = LumpMin + (int)(roll01 * (LumpMax - LumpMin + 1));
			if (stackLimit > 0 && n > stackLimit) n = stackLimit;
			return n < 1 ? 1 : n;
		}

		/// <summary>The per-map loose budget: <paramref name="percent"/> % of the units in the map's resource rock.</summary>
		public static float Budget(float rockUnits, float percent)
		{
			if (rockUnits <= 0f || percent <= 0f) return 0f;
			return rockUnits * percent / 100f;
		}
	}
}
