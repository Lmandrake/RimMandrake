namespace RimMandrake.FlowWorks.Quarry
{
	/// <summary>FLOWWORKS_QUARRY_DIGGING_1, river half — the Verse-free numbers of sluice mining and panning
	/// (selftested in Source/SelfTest). Design: design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md
	/// §2b–2c. Every value is PROVISIONAL (design defaults), for the mineral registry's review sheet to set.</summary>
	public static class RM_PlacerMath
	{
		/// <summary>A RimWorld year: 60 days of 60,000 ticks. The stock regrows to full once a year.</summary>
		public const int TicksPerYear = 3600000;

		/// <summary>One sluice roll per in-game day.</summary>
		public const int SluiceIntervalTicks = 60000;

		/// <summary>Expected units a sluice washes out per day on an ordinary river at multiplier 1.</summary>
		public const float SluicePerDay = 1.2f;

		/// <summary>A panning session: ~2 in-game hours of work at MiningSpeed 1.</summary>
		public const int PanSessionTicks = 5000;

		/// <summary>Chance a session finds anything, at skill factor 1 and multiplier 1 ("mostly nothing").</summary>
		public const float PanHitChance = 0.125f;

		public const int PanMin = 1;
		public const int PanMax = 3;

		/// <summary>The river's stock ceiling: <paramref name="percent"/> % of the placer units the land holds.</summary>
		public static float StockCap(float placerUnits, float percent)
		{
			if (placerUnits <= 0f || percent <= 0f) return 0f;
			return placerUnits * percent / 100f;
		}

		/// <summary>Linear regrowth: a full cap per year, never past the cap.</summary>
		public static float Regrow(float stock, float cap, int ticks)
		{
			if (cap <= 0f) return 0f;
			if (stock < 0f) stock = 0f;
			if (ticks > 0) stock += cap * ticks / TicksPerYear;
			return stock > cap ? cap : stock;
		}

		/// <summary>What the current gives a sluice: only the shallow edge lane (1) washes gravel. Still water
		/// (0), and the chest-deep centre (2, where the PlaceWorker never lets one stand), give nothing.</summary>
		public static float LaneRate(int lane)
		{
			return lane == 1 ? 1f : 0f;
		}

		/// <summary>One day's sluice yield before the stock is consulted: expected
		/// SluicePerDay × size × multiplier × lane, rounded by the roll.</summary>
		public static int SluiceYield(float roll01, int lane, float sizeFactor, float multiplier)
		{
			if (roll01 < 0f) roll01 = 0f;
			if (roll01 >= 1f) roll01 = 0.9999f;
			float e = SluicePerDay * LaneRate(lane) * (sizeFactor < 0f ? 0f : sizeFactor) * (multiplier < 0f ? 0f : multiplier);
			if (e <= 0f) return 0;
			return (int)(e + roll01);
		}

		/// <summary>Mining skill 0 ≈ 40%, skill 20 ≈ 160%, linear.</summary>
		public static float PanSkillFactor(int skill)
		{
			if (skill < 0) skill = 0;
			if (skill > 20) skill = 20;
			return 0.4f + 0.06f * skill;
		}

		/// <summary>Session length in ticks for a pawn's MiningSpeed (floored so a crippled pawn still finishes).</summary>
		public static int PanTicks(float miningSpeed)
		{
			if (miningSpeed < 0.1f) miningSpeed = 0.1f;
			return (int)(PanSessionTicks / miningSpeed);
		}

		/// <summary>One session: 0 most of the time, else 1–3 units.</summary>
		public static int PanSession(float hitRoll01, float sizeRoll01, int skill, float multiplier)
		{
			float p = PanHitChance * PanSkillFactor(skill) * (multiplier < 0f ? 0f : multiplier);
			if (p > 1f) p = 1f;
			if (hitRoll01 >= p) return 0;
			if (sizeRoll01 < 0f) sizeRoll01 = 0f;
			if (sizeRoll01 >= 1f) sizeRoll01 = 0.9999f;
			return PanMin + (int)(sizeRoll01 * (PanMax - PanMin + 1));
		}

		/// <summary>Sluices and panners share one stock: a take never exceeds what is left (whole units).</summary>
		public static int Take(float stock, int want)
		{
			if (want <= 0 || stock < 1f) return 0;
			int have = (int)stock;
			return want < have ? want : have;
		}
	}
}
