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

		// ── FLOW_CONTROLS_BUILD_EIGHT_QUIET_PEBBLES: the further controls' numbers ─────────────────────────────

		/// <summary>The fill fractions the level holder's gizmo offers.</summary>
		public static readonly float[] SetpointPresets = { 0f, 0.25f, 0.5f, 0.75f, 1f };

		/// <summary>Level holder: how many levels to pour (+) or take (-) so <paramref name="held"/> levels out of
		/// <paramref name="capacity"/> come to the set fraction (rounded to the nearest level). 0 when already there or
		/// there is no room at all. NaN and out-of-range setpoints clamp to [0, 1].</summary>
		public static int LevelHolderNeed(int held, int capacity, float setpoint)
		{
			if (capacity <= 0)
			{
				return 0;
			}
			float sp = float.IsNaN(setpoint) ? 0f : (setpoint < 0f ? 0f : (setpoint > 1f ? 1f : setpoint));
			int target = (int)Math.Round(sp * capacity, MidpointRounding.AwayFromZero);
			return target - held;
		}

		/// <summary>Timer switch modes.</summary>
		public const int TimerByHours = 0;
		public const int TimerByPeriod = 1;

		/// <summary>Timer switch: is it ON now? By hours: on from <paramref name="startHour"/> (inclusive) to
		/// <paramref name="endHour"/> (exclusive) of the local day, wrapping past midnight when start &gt; end; start ==
		/// end is on all day. By period: on for the first <paramref name="onHours"/> of every
		/// <paramref name="periodHours"/>, counted from game tick 0 (2500 ticks an hour). <paramref name="invert"/> flips
		/// the answer.</summary>
		public static bool TimerOn(int mode, float hourOfDay, int startHour, int endHour, long ticksGame, float periodHours,
			float onHours, bool invert)
		{
			bool on;
			if (mode == TimerByPeriod)
			{
				float period = float.IsNaN(periodHours) || periodHours < 0.1f ? 0.1f : periodHours;
				double phase = (ticksGame / 2500.0) % period;
				if (phase < 0)
				{
					phase += period;
				}
				on = phase < onHours;
			}
			else
			{
				int s = ((startHour % 24) + 24) % 24;
				int e = ((endHour % 24) + 24) % 24;
				float h = hourOfDay < 0f ? 0f : hourOfDay;
				on = s == e || (s < e ? (h >= s && h < e) : (h >= s || h < e));
			}
			return on != invert;
		}

		/// <summary>Map-edge setter modes, one per edge (index 0 north, 1 east, 2 south, 3 west).</summary>
		public const int EdgeAuto = 0;
		public const int EdgeSealed = 1;
		public const int EdgeDrain = 2;

		public static string EdgeModeLabel(int mode)
		{
			return mode == EdgeSealed ? "sealed" : (mode == EdgeDrain ? "drain" : "automatic");
		}

		/// <summary>Is a dug square near the edges flagged here a map-edge sink? Any DRAIN edge it is near makes it one
		/// (even with the automatic edge sinks switched off); otherwise any AUTOMATIC edge it is near leaves the
		/// automatic rule (<paramref name="autoRule"/>) to decide; near only SEALED edges, it is not. Not near any edge:
		/// false. <paramref name="modes"/> null = every edge automatic.</summary>
		public static bool EdgeSink(int[] modes, bool nearN, bool nearE, bool nearS, bool nearW, bool autoRule)
		{
			if (!(nearN || nearE || nearS || nearW))
			{
				return false;
			}
			if (modes == null)
			{
				return autoRule;
			}
			bool[] near = { nearN, nearE, nearS, nearW };
			bool anyAuto = false;
			for (int i = 0; i < 4; i++)
			{
				if (!near[i])
				{
					continue;
				}
				int m = modes.Length > i ? modes[i] : EdgeAuto;
				if (m == EdgeDrain)
				{
					return true;
				}
				if (m != EdgeSealed)
				{
					anyAuto = true;
				}
			}
			return anyAuto && autoRule;
		}

		/// <summary>A natural body's edge contact as the setter rules it: <paramref name="touchesOpenEdge"/> = it touches
		/// an edge that is not sealed (the automatic size rule then applies); <paramref name="touchesDrainEdge"/> = it
		/// touches a drain edge (limitless whatever its size). Inputs: which edges its footprint touches.</summary>
		public static void BodyEdges(int[] modes, bool touchN, bool touchE, bool touchS, bool touchW,
			out bool touchesOpenEdge, out bool touchesDrainEdge)
		{
			bool[] touch = { touchN, touchE, touchS, touchW };
			touchesOpenEdge = false;
			touchesDrainEdge = false;
			for (int i = 0; i < 4; i++)
			{
				if (!touch[i])
				{
					continue;
				}
				int m = modes != null && modes.Length > i ? modes[i] : EdgeAuto;
				if (m == EdgeDrain)
				{
					touchesDrainEdge = true;
					touchesOpenEdge = true;
				}
				else if (m == EdgeAuto)
				{
					touchesOpenEdge = true;
				}
			}
		}

		/// <summary>The temperatures the thermostat's gizmo offers (C).</summary>
		public static readonly float[] ThermostatPresets = { -20f, -5f, 0f, 10f, 21f, 40f, 60f, 90f, 100f };

		/// <summary>The radii the radius-reaching controls offer (cells).</summary>
		public static readonly float[] RadiusPresets = { 1.5f, 3f, 5f, 8f, 12f };

		// Mirrors RM_LiquidHeatMath (kept Verse-free and self-contained here so the SelfTest compiles this file alone):
		// hot 3 / cold 2 energy per level per second, a 250-tick interval, a per-room cap of 8 x 21 per second.
		public const float ThermoHotPerLevelPerSecond = 3f;
		public const float ThermoColdPerLevelPerSecond = 2f;
		public const float ThermoSecondsPerInterval = 250 / 60f;
		public const float ThermoMaxRoomPerSecond = 8f * 21f;

		/// <summary>Liquid thermostat: the heat (+) or chill (-) one room takes this 250-tick interval from
		/// <paramref name="levels"/> levels of liquid the thermostat holds at <paramref name="targetC"/>. Liquid warmer
		/// than the room warms it, colder chills it, at the liquid-heat rates, capped per room, and never past the target
		/// (so the room settles AT the set temperature). 0 for no liquid, an empty room, or strength 0.</summary>
		public static float ThermostatEnergy(int levels, float roomTempC, int roomCells, float targetC, float strength)
		{
			if (levels <= 0 || roomCells <= 0 || !(strength > 0f) || float.IsNaN(targetC) || float.IsNaN(roomTempC))
			{
				return 0f;
			}
			float diff = targetC - roomTempC;
			if (diff == 0f)
			{
				return 0f;
			}
			float per = diff > 0f ? ThermoHotPerLevelPerSecond : -ThermoColdPerLevelPerSecond;
			float e = per * levels * ThermoSecondsPerInterval * strength;
			float cap = ThermoMaxRoomPerSecond * ThermoSecondsPerInterval * strength;
			float room = diff * roomCells;
			if (diff > 0f)
			{
				return Math.Min(Math.Min(e, cap), room);
			}
			return Math.Max(Math.Max(e, -cap), room);
		}

		/// <summary>Flow meter: a level change over <paramref name="ticks"/> as levels per day (60000 ticks). 0 when no
		/// time has passed.</summary>
		public static float PerDay(float deltaLevels, int ticks)
		{
			return ticks <= 0 ? 0f : deltaLevels * 60000f / ticks;
		}
	}
}
