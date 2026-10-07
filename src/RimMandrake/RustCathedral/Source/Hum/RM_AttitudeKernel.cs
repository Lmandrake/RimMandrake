using System;
using System.Collections.Generic;

namespace RimMandrake.RustCathedral.Hum
{
	/// <summary>
	/// The Cathedral hum-mood arithmetic (RM_MapComponent_BiomeAttitude's slow standing layer and fast irritation
	/// layer), with no Verse or UnityEngine type in it so the offline fuzz (Source/SelfTest/AttitudeFuzz.cs,
	/// `python3 src/RimMandrake/Utils/selftest_rustcathedral_attitude_fuzz.py`) compiles THIS file and drives the
	/// code the game runs. The component keeps the state and the engine calls; every number it computes comes from here.
	/// If a `using Verse;` lands in this file the selftest build breaks, which is the guard rail working.
	/// </summary>
	public static class RM_AttitudeKernel
	{
		public const int StandingMin = -100;
		public const int StandingMax = 100;
		public const float CompositeMax = 100f;

		static int ClampInt(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }
		static float ClampF(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

		/// <summary>Where a map's standing begins: the def's start value held inside [-100, 100].</summary>
		public static int StandingStartValue(int standingStart) { return ClampInt(standingStart, StandingMin, StandingMax); }

		/// <summary>Standing moved by delta (negative = offence), held inside [-100, 100].</summary>
		public static int StandingAfter(int standing, int delta) { return ClampInt(standing + delta, StandingMin, StandingMax); }

		/// <summary>Irritation bumped by amount; never below zero.</summary>
		public static float IrritationAfter(float irritation, float amount) { return Math.Max(0f, irritation + amount); }

		/// <summary>composite = irritation - standing * weight, held inside [0, 100].</summary>
		public static float Composite(float irritation, int standing, float goodwillCompositeWeight)
		{
			return ClampF(irritation - standing * goodwillCompositeWeight, 0f, CompositeMax);
		}

		/// <summary>
		/// The band for a composite: the highest ascending threshold met. Escalation is immediate; a lower band only
		/// takes effect once the composite has fallen <paramref name="hysteresisMargin"/> below the threshold that put
		/// us in the previous band. <paramref name="currentBand"/> is -1 when uninitialised (treated as band 0).
		/// </summary>
		public static int BandFor(float composite, int currentBand, IList<float> thresholds, float hysteresisMargin)
		{
			int previousBand = currentBand < 0 ? 0 : currentBand;
			int rawBand = 0;
			for (int i = 0; i < thresholds.Count; i++)
			{
				if (composite >= thresholds[i])
				{
					rawBand = i + 1;
				}
			}

			if (rawBand >= previousBand)
			{
				return rawBand;
			}

			int thresholdIndexForPreviousBand = previousBand - 1;
			if (thresholdIndexForPreviousBand < 0 || thresholdIndexForPreviousBand >= thresholds.Count)
			{
				return rawBand;
			}
			float holdLine = thresholds[thresholdIndexForPreviousBand] - hysteresisMargin;
			return composite < holdLine ? rawBand : previousBand;
		}

		/// <summary>The band the stage lets the hum show: the raw band held inside [0, ceiling].</summary>
		public static int ClampToCeiling(int rawBand, int ceiling) { return ClampInt(rawBand, 0, ceiling); }

		/// <summary>While a line-cycle rolls the hum drops one band; band 0 and the (silent) worst band stay put.</summary>
		public static int DroppedBand(int band, int worstBand)
		{
			if (band <= 0 || band >= worstBand)
			{
				return band;
			}
			return band - 1;
		}

		/// <summary>Hum layers to play: none at the worst band, otherwise band + 1 up to the layer list, one fewer in a line-cycle drop.</summary>
		public static int DesiredLayers(int band, int worstBand, int layerCount, bool lineCycleDrop)
		{
			if (band >= worstBand)
			{
				return 0;
			}
			int desired = ClampInt(band + 1, 0, layerCount);
			if (lineCycleDrop)
			{
				desired = Math.Max(0, desired - 1);
			}
			return desired;
		}

		/// <summary>One decay step: irritation halves every half-life; dust below 0.05 is dropped.</summary>
		public static float DecayedIrritation(float irritation, float halfLifeDaysBase, float rateMultiplier, float stageMultiplier, float intervalTicks, float ticksPerDay)
		{
			if (irritation <= 0f)
			{
				return irritation;
			}
			float halfLifeDays = Math.Max(0.01f, halfLifeDaysBase / Math.Max(0.01f, rateMultiplier * stageMultiplier));
			float halfLifeTicks = halfLifeDays * ticksPerDay;
			float decayFactor = (float)Math.Pow(0.5f, intervalTicks / halfLifeTicks);
			irritation *= decayFactor;
			if (irritation < 0.05f)
			{
				irritation = 0f;
			}
			return irritation;
		}

		/// <summary>
		/// One worst-band drain attempt (the caller has checked the band and the setting). Returns the standing delta to
		/// apply (0 for none) and updates the three bookkeeping fields: the day window rolls after a day, at most
		/// <paramref name="capPerDay"/> (negative) is drained per window, and at most one drain per interval.
		/// </summary>
		public static int DrainDelta(int nowTick, ref int dayAnchorTick, ref int drainedToday, ref int lastDrainTick,
			int intervalTicks, int tickAmount, int capPerDay, int ticksPerDay)
		{
			if (nowTick - dayAnchorTick >= ticksPerDay)
			{
				dayAnchorTick = nowTick;
				drainedToday = 0;
			}
			if (drainedToday <= capPerDay)
			{
				return 0;
			}
			if (nowTick - lastDrainTick < intervalTicks)
			{
				return 0;
			}
			lastDrainTick = nowTick;

			int amount = tickAmount;
			int remainingBudget = capPerDay - drainedToday;
			if (amount < remainingBudget)
			{
				amount = remainingBudget;
			}
			if (amount >= 0)
			{
				return 0;
			}
			drainedToday += amount;
			return amount;
		}
	}
}
