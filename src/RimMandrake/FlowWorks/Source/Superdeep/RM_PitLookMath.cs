using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>PIT_LOOK_TREATMENTS: the numbers of the pit's depth look (see RM_PitLook.cs for the three treatments). Verse-free,
	/// self-tested (SelfTest/PitLookChecks.cs).</summary>
	public static class RM_PitLookMath
	{
		public const int Bevel = 0, Oblique = 1, Well = 2;

		/// <summary>Far-face height (cells) for an exposed drop of <paramref name="drop"/> notches in an opening
		/// <paramref name="run"/> cells deep north to south: the drop at the sink's own scale (<paramref name="perLevel"/> a
		/// notch), eased into the room the opening has once <paramref name="minFloor"/> of floor is kept at the near lip:
		/// room x (1 - e^(-drop x perLevel / room)). Shallow cuts keep about their true height; deep ones compress, and every
		/// deeper drop still hangs lower (a 2-row pit: 2 m 1.01, 4 m 1.35, 8 m 1.71), so 4 m and 8 m stay apart where a hard
		/// cap made them one look.</summary>
		public static float ObliqueFace(int drop, float run, float perLevel, float minFloor)
		{
			if (drop <= 0 || !(perLevel > 0f) || !(run > 0f))
			{
				return 0f;
			}
			float room = run - minFloor;
			if (room < 0.25f * run)
			{
				room = 0.25f * run;
			}
			return room * (1f - (float)Math.Exp(-drop * perLevel / room));
		}

		/// <summary>0..1 darkness laid over a dry floor of depth <paramref name="depth"/> notches: the light that reaches the
		/// bottom falls with depth. 0.5 m 0.12, 1 m 0.24, 1.5 m 0.34, 2 m 0.42, 4 m 0.58, 8 m 0.70.</summary>
		public static float FloorDark(int depth, int mode)
		{
			if (depth <= 0)
			{
				return 0f;
			}
			float d = depth <= 4 ? 0.12f * depth - 0.006f * depth * depth : 0.42f + 0.16f * (float)(Math.Log(depth / 4.0) / Math.Log(2.0));
			if (mode == Well)
			{
				d *= 1.25f;
			}
			return d > 0.82f ? 0.82f : d;
		}

		/// <summary>How much darker an occupant is drawn standing on a dry floor of depth <paramref name="depth"/> (0..1):
		/// about two thirds of the floor's own darkening, so he stays readable against it.</summary>
		public static float OccupantShade(int depth, int mode)
		{
			if (mode == Bevel || depth <= 0)
			{
				return 0f;
			}
			return FloorDark(depth, mode) * (mode == Well ? 0.75f : 0.6f);
		}

		/// <summary>The SHADOW WELL's perspective: an occupant drawn smaller the deeper he stands, no smaller past 4 m
		/// (1 at the surface, 0.94 at 1 m, 0.86 at 2 m, 0.74 at 4 m and deeper).</summary>
		public static float OccupantScale(int depth, int mode)
		{
			if (mode != Well || depth <= 0)
			{
				return 1f;
			}
			int d = depth > 8 ? 8 : depth;
			return 1f - 0.0325f * d;
		}

		/// <summary>Width (cells) of the soft shade inside a side wall, or all four walls in the well: grows with the drop.</summary>
		public static float WallShadeWidth(int drop, int mode)
		{
			if (drop <= 0)
			{
				return 0f;
			}
			int d = drop > 8 ? 8 : drop;
			float w = mode == Well ? 0.10f + 0.05f * d : 0.08f + 0.025f * d;
			return w > 0.5f ? 0.5f : w;
		}

		/// <summary>The depth in metres of strata line <paramref name="k"/> (1-based): one every metre, two notches.</summary>
		public static int StrataLineNotches(int k) => 2 * k;
	}
}
