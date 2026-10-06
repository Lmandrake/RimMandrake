using System;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>Pure arithmetic of a liquid converter cycle — no Verse types, so the C# selftest runs it.
	/// A converter accrues input budget every rare tick (250 ticks, 240 a day) and runs whole batches out of
	/// it; a batch eats <c>inputUnits</c> and makes <c>outputUnits</c>. Idle budget is capped so a machine
	/// left dry for a week does not burst a week's work the moment its tank is filled.</summary>
	public static class RM_ConversionMath
	{
		public const int RareTicksPerDay = 240;

		public static float BudgetPerRareTick(float inputUnitsPerDay, float tierRate, float settingsMultiplier, float environmentFactor)
		{
			if (inputUnitsPerDay <= 0f || tierRate <= 0f || settingsMultiplier <= 0f || environmentFactor <= 0f)
			{
				return 0f;
			}
			return inputUnitsPerDay * tierRate * settingsMultiplier * environmentFactor / RareTicksPerDay;
		}

		/// <summary>Whole batches runnable now: bounded by accrued budget, input on hand and output room
		/// (outputRoom &lt; 0 means unbounded — an item fallback).</summary>
		public static int Batches(float accrued, int inputUnits, int outputUnits, int inputAvailable, int outputRoom)
		{
			if (inputUnits < 1 || outputUnits < 1)
			{
				return 0;
			}
			int n = (int)Math.Floor(accrued / inputUnits + 1e-4f);
			n = Math.Min(n, inputAvailable / inputUnits);
			if (outputRoom >= 0)
			{
				n = Math.Min(n, outputRoom / outputUnits);
			}
			return Math.Max(0, n);
		}

		/// <summary>Accrued budget is never held above one batch or one rare tick's budget, whichever is larger.</summary>
		public static float CapAccrued(float accrued, int inputUnits, float perTick)
		{
			return Math.Min(accrued, Math.Max(inputUnits, perTick));
		}

		/// <summary>A solar still works in daylight only: full at sky glow 0.5 and above, nothing below.</summary>
		public static float SunFactor(float skyGlow, bool roofed)
		{
			return !roofed && skyGlow >= 0.5f ? 1f : 0f;
		}
	}
}
