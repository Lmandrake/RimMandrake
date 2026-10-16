using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.MapControls
{
	/// <summary>FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS (owner 2026-10-16): the Verse-free numbers behind the dev-placed
	/// flow source and flow sink, so the selftest runs the production code.
	///
	/// The rate unit is the engine's own: LEVELS PER PULSE. A level is one fill step of a dug square (a square dug to depth
	/// 4 holds 4 levels; one level = RM_Volume.UnitsPerLevel tank units); a pulse is the flow engine's step, every
	/// PulseIntervalTicks. A fractional rate carries its remainder from pulse to pulse, so 0.25 pours one level every
	/// fourth pulse. A tap that cannot deliver what falls due (the canal brims, or holds another liquid) does NOT bank it:
	/// the carry never exceeds one level, so a blocked source never bursts when the way clears.</summary>
	public static class RM_MapControlMath
	{
		/// <summary>The highest rate a gizmo or the bridge may set, in levels per pulse.</summary>
		public const float MaxRatePerPulse = 20f;

		/// <summary>The rate presets the gizmo offers (levels per pulse).</summary>
		public static readonly float[] RatePresets = { 0.1f, 0.25f, 0.5f, 1f, 2f, 4f, 8f, 16f };

		/// <summary>A sane rate: NaN and negatives read 0, the top is <see cref="MaxRatePerPulse"/>.</summary>
		public static float ClampRate(float rate)
		{
			if (float.IsNaN(rate) || rate <= 0f)
			{
				return 0f;
			}
			return rate > MaxRatePerPulse ? MaxRatePerPulse : rate;
		}

		/// <summary>Whole levels due this pulse at <paramref name="ratePerPulse"/>, given the fractional
		/// <paramref name="carry"/> left by earlier pulses (updated in place, always in [0, 1)). Every level that falls due
		/// is taken off the carry whether or not it is delivered: undelivered levels are dropped, never banked.</summary>
		public static int Due(ref float carry, float ratePerPulse)
		{
			if (float.IsNaN(carry) || carry < 0f || carry >= 1f)
			{
				carry = 0f;
			}
			carry += ClampRate(ratePerPulse);
			// The epsilon makes 10 x 0.1 come to one level, not 0.99999.
			int due = (int)Math.Floor(carry + 1e-4f);
			carry -= due;
			if (carry < 0f)
			{
				carry = 0f;
			}
			return due;
		}

		/// <summary>Where a source pours its next level: the candidate with the LOWEST surface (fill - dug depth), the
		/// first in reach order on a tie (own square first, then N, E, S, W). -1 when there is no candidate.</summary>
		public static int PickPourTarget(IList<int> surfaces)
		{
			int best = -1;
			for (int i = 0; i < surfaces.Count; i++)
			{
				if (best < 0 || surfaces[i] < surfaces[best])
				{
					best = i;
				}
			}
			return best;
		}

		/// <summary>Where a sink takes its next level: the candidate holding the MOST levels (fill &gt; 0), the first in
		/// reach order on a tie. -1 when every candidate is dry.</summary>
		public static int PickDrainTarget(IList<int> fills)
		{
			int best = -1;
			for (int i = 0; i < fills.Count; i++)
			{
				if (fills[i] > 0 && (best < 0 || fills[i] > fills[best]))
				{
					best = i;
				}
			}
			return best;
		}

		/// <summary>The same rate per in-game hour (2500 ticks), for the label. Pulse ticks below 1 read as 1.</summary>
		public static float PerHour(float ratePerPulse, int pulseTicks)
		{
			return ClampRate(ratePerPulse) * 2500f / Math.Max(1, pulseTicks);
		}

		/// <summary>The rate as the inspect pane and gizmo print it.</summary>
		public static string RateLabel(float ratePerPulse, int pulseTicks)
		{
			float r = ClampRate(ratePerPulse);
			return r.ToString("0.##", System.Globalization.CultureInfo.InvariantCulture) + " level(s) per pulse (about "
				+ PerHour(r, pulseTicks).ToString("0.#", System.Globalization.CultureInfo.InvariantCulture) + " per hour)";
		}
	}
}
