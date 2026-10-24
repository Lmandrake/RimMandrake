// SPRINKLER_SPRAY_REDRAW_REAL_THROW (owner 2026-10-23: "animated water leaving sprinkler is pretty dorky: just a blue burst
// ring around it, should be much more realistic and portray the actual water throw affected (radius)").
// Pure, Verse-free: compiled into the SelfTest console app as well as the mod.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>One droplet of a rotor step: it lands at (landX, landZ) cells from the head's cell centre, inside watered cell
	/// number <see cref="cell"/> of the list the plan was made from, and flies <see cref="RM_SprayPlan.BandTicks"/>[band].</summary>
	public struct RM_SprayDrop
	{
		public int cell;
		public float landX, landZ;
		public int band;
	}

	/// <summary>
	/// The spray a head draws is planned from the SAME cells its pulse wetted (CompRM_SprinklerBase.sprayCells), so the picture
	/// cannot disagree with the ground: droplets land in those cells and nowhere else.
	///
	/// A rotor: a jet sweeps a full turn every <see cref="RevolutionTicks"/>. At each of <see cref="Steps"/> steps the jet points
	/// along a ray from the head's cell centre, and one droplet lands in every watered cell that ray crosses, at a fixed scatter along
	/// the ray's run through the cell (RunFraction; pulled <see cref="CellMargin"/> inside its edges). A watered cell no sampled ray crosses
	/// (none at the shipped radii; the guard keeps the promise for any cell list) gets a droplet at its centre on the step nearest
	/// its bearing. So over one turn the landing cells are exactly the watered cells, each at least once.
	///
	/// Throw: a droplet's flight time grows with its distance (ballistic: time ~ sqrt(range)), in four bands so each band is one
	/// FleckDef whose fixed archDuration equals that flight time and whose archHeight lifts it higher the further it goes
	/// (RimWorld's FleckThrown draws height = archHeight * InverseParabola(age / archDuration), so it touches down at landing).
	/// </summary>
	public static class RM_SprayPlan
	{
		public const int RevolutionTicks = 240;
		public const int StepTicks = 4;
		public const int Steps = RevolutionTicks / StepTicks;

		/// <summary>How far inside its cell's edges a landing point is kept (cells).</summary>
		public const float CellMargin = 0.15f;

		/// <summary>Band b holds landings with distance &lt; BandUpper[b] (cells); the last band is open.</summary>
		public static readonly float[] BandUpper = { 1f, 2f, 3f, float.MaxValue };

		/// <summary>Flight time per band, game ticks (60 per second): 0.37 s * sqrt(band middle distance 0.5/1.5/2.5/3.5).</summary>
		public static readonly int[] BandTicks = { 16, 27, 35, 42 };

		/// <summary>Arch height per band, cells: 0.15 per cell of band middle distance plus 0.1.</summary>
		public static readonly float[] BandArch = { 0.18f, 0.33f, 0.48f, 0.63f };

		/// <summary>The band's FleckDef (Defs/Sprinklers/RM_Sprinklers.xml).</summary>
		public static string BandDefName(int band) => "RM_Fleck_SprinklerDrop_" + band;

		public static int BandOf(float distance)
		{
			for (int b = 0; b < BandUpper.Length; b++) if (distance < BandUpper[b]) return b;
			return BandUpper.Length - 1;
		}

		/// <summary>The jet's bearing at step <paramref name="step"/> (radians, x east, z north). Half a step off the axes so
		/// a ray never runs exactly along a cell edge.</summary>
		public static double Bearing(int step) => 2.0 * Math.PI * (step + 0.5) / Steps;

		/// <summary>The rotor step at game tick <paramref name="tick"/> for a head whose phase is <paramref name="phase"/>; -1 when
		/// this tick fires no step.</summary>
		public static int StepAt(int tick, int phase)
		{
			int t = tick + phase;
			if (t < 0) t = -t;
			if (t % StepTicks != 0) return -1;
			return (t / StepTicks) % Steps;
		}

		/// <summary>Per step, the droplets of one turn over watered cells given as offsets (dx east, dz north) from the head's
		/// cell. Entry s is never null.</summary>
		public static List<RM_SprayDrop>[] Plan(IList<int> dx, IList<int> dz)
		{
			var plan = new List<RM_SprayDrop>[Steps];
			for (int s = 0; s < Steps; s++) plan[s] = new List<RM_SprayDrop>();
			int n = Math.Min(dx?.Count ?? 0, dz?.Count ?? 0);
			if (n == 0) return plan;
			var hit = new bool[n];
			for (int s = 0; s < Steps; s++)
			{
				double a = Bearing(s);
				double ux = Math.Cos(a), uz = Math.Sin(a);
				for (int i = 0; i < n; i++)
				{
					if (!RayThroughCell(ux, uz, dx[i], dz[i], out double t0, out double t1)) continue;
					double t = t0 + (t1 - t0) * RunFraction(s, i);
					Add(plan[s], i, dx[i], dz[i], (float)(ux * t), (float)(uz * t));
					hit[i] = true;
				}
			}
			for (int i = 0; i < n; i++)
			{
				if (hit[i]) continue;
				double bearing = Math.Atan2(dz[i], dx[i]);
				if (bearing < 0) bearing += 2.0 * Math.PI;
				int s = ((int)Math.Round(bearing / (2.0 * Math.PI) * Steps - 0.5) % Steps + Steps) % Steps;
				Add(plan[s], i, dx[i], dz[i], dx[i], dz[i]);
			}
			return plan;
		}

		/// <summary>Where along its run through a cell a droplet lands: a fixed scatter in [0.2, 0.8] per (step, cell), so the
		/// landings do not all sit on the run's middle (which draws rings of dots); deterministic, so the plan is testable.</summary>
		public static double RunFraction(int step, int cell)
		{
			uint h = (uint)(step * 73856093) ^ (uint)(cell * 19349663);
			h ^= h >> 13; h *= 0x5bd1e995; h ^= h >> 15;
			return 0.2 + 0.6 * (h & 0xFFFF) / 65535.0;
		}

		private static void Add(List<RM_SprayDrop> step, int i, int cx, int cz, float x, float z)
		{
			float lo = 0.5f - CellMargin;
			x = Math.Max(cx - lo, Math.Min(cx + lo, x));
			z = Math.Max(cz - lo, Math.Min(cz + lo, z));
			step.Add(new RM_SprayDrop { cell = i, landX = x, landZ = z, band = BandOf((float)Math.Sqrt(x * x + z * z)) });
		}

		/// <summary>The ray from the origin along unit (ux, uz), t &gt;= 0, against the unit cell centred on (cx, cz): the run
		/// [t0, t1] inside it. False when it misses or only grazes a corner.</summary>
		public static bool RayThroughCell(double ux, double uz, int cx, int cz, out double t0, out double t1)
		{
			t0 = 0.0; t1 = double.MaxValue;
			if (!Slab(ux, cx, ref t0, ref t1) || !Slab(uz, cz, ref t0, ref t1)) return false;
			return t1 - t0 > 1e-4;
		}

		private static bool Slab(double u, int c, ref double t0, ref double t1)
		{
			double lo = c - 0.5, hi = c + 0.5;
			if (Math.Abs(u) < 1e-12) return lo <= 0.0 && 0.0 <= hi;
			double a = lo / u, b = hi / u;
			if (a > b) { double k = a; a = b; b = k; }
			t0 = Math.Max(t0, a);
			t1 = Math.Min(t1, b);
			return t1 > t0;
		}

		/// <summary>The constant ground velocity (cells per second) that carries a droplet from the nozzle (sx, sz) to its landing
		/// point (lx, lz) in exactly <paramref name="ticks"/> game ticks.</summary>
		public static void Velocity(float sx, float sz, float lx, float lz, int ticks, out float vx, out float vz)
		{
			float secs = ticks / 60f;
			vx = (lx - sx) / secs;
			vz = (lz - sz) / secs;
		}

		/// <summary>The fleck's solid time so that its life (fadeIn + solid + fadeOut) is half a tick short of the flight: a
		/// game-time fleck checks EndOfLife BEFORE it ages one tick and moves, so it still makes the landing tick's step (life &gt;
		/// (ticks - 1) / 60) and is removed on the next (life &lt;= ticks / 60), never sliding past its landing point.</summary>
		public static float SolidSeconds(int ticks, float fadeIn, float fadeOut) => Math.Max(0f, (ticks - 0.5f) / 60f - fadeIn - fadeOut);
	}
}
