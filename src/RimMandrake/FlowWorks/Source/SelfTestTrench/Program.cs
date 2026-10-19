using System;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.TrenchSelfTest
{
	/// <summary>TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT L1 rows: the arithmetic the game's trench cover runs.</summary>
	public static class Program
	{
		private static int fails;

		private static void Check(bool ok, string name)
		{
			Console.WriteLine((ok ? "PASS  " : "FAIL  ") + name);
			if (!ok)
			{
				fails++;
			}
		}

		private static bool Near(float a, float b, float tol = 0.005f) => Math.Abs(a - b) <= tol;

		/// <summary>An east-west trench one square wide along z = 0, <paramref name="notches"/> deep, on a 41×41 map
		/// centred on (0, 0); everything else undug.</summary>
		private static Func<int, int, int> Trench(int notches)
		{
			return (x, z) => Math.Abs(x) > 20 || Math.Abs(z) > 20 ? -1 : (z == 0 ? notches : 0);
		}

		public static int Main()
		{
			float person = RM_TrenchCoverMath.HeightMetres(1f);
			Check(Near(person, 1.7f, 1e-4f), "a person (body size 1) is 1.7 m");

			// §4 table, for a 1.7 m person at 0.5 / 1 / 1.5 m.
			Check(Near(RM_TrenchCoverMath.WallBlock(0.5f, person, 1f), 0.22f), "0.5 m wall blocks 0.22");
			Check(Near(RM_TrenchCoverMath.WallBlock(1.0f, person, 1f), 0.44f), "1 m wall blocks 0.44 (just under sandbags 0.55)");
			Check(Near(RM_TrenchCoverMath.WallBlock(1.5f, person, 1f), 0.66f), "1.5 m wall blocks 0.66 (between sandbags and a wall)");
			Check(RM_TrenchCoverMath.WallBlock(0.2f, person, 1f) == 0f, "under 0.25 m is no wall");
			Check(Near(RM_TrenchCoverMath.WallBlock(5f, person, 1f), 0.75f, 1e-5f), "over person height caps at a full wall, 0.75");
			float muff = RM_TrenchCoverMath.WallBlock(1.0f, RM_TrenchCoverMath.HeightMetres(2.4f), 1f);
			Check(Near(muff, 0.285f), "a muffalo (2.4) in 1 m gets about 0.29, design §4 rounds 0.285 (got " + muff.ToString("F3") + ")");
			Check(Near(RM_TrenchCoverMath.WallBlock(1.0f, person, 0.5f), 0.22f), "strength 0.5 halves it");

			// Square-on: shooter 10 squares north of a pawn in a 1 m trench.
			float on = RM_TrenchCoverMath.TrenchBlock(Trench(2), 0, 0, 0, 10, person, 1f);
			Check(Near(on, 0.44f), "1 m trench, shooter 10 off square-on: 0.44 (got " + on.ToString("F3") + ")");
			float on15 = RM_TrenchCoverMath.TrenchBlock(Trench(3), 0, 0, 0, -10, person, 1f);
			Check(Near(on15, 0.66f), "1.5 m trench, shooter from the other side: 0.66 (got " + on15.ToString("F3") + ")");

			// Enfilade: along the trench axis.
			Check(RM_TrenchCoverMath.TrenchBlock(Trench(2), 0, 0, 10, 0, person, 1f) == 0f, "enfilade: shot along the trench gets 0");
			Check(RM_TrenchCoverMath.TrenchBlock(Trench(2), 0, 0, -12, 0, person, 1f) == 0f, "enfilade from the other end gets 0");

			// Lip shooters: on the wall square nothing; one square back a third (vanilla's distance falloff).
			Check(RM_TrenchCoverMath.TrenchBlock(Trench(2), 0, 0, 0, 1, person, 1f) == 0f, "shooter standing on the wall square: 0");
			float lip = RM_TrenchCoverMath.TrenchBlock(Trench(2), 0, 0, 0, 2, person, 1f);
			Check(Near(lip, 0.441f * 0.3333f), "shooter one back from the lip: x0.333 (got " + lip.ToString("F3") + ")");
			float lip2 = RM_TrenchCoverMath.TrenchBlock(Trench(2), 0, 0, 0, 3, person, 1f);
			Check(Near(lip2, 0.441f * 0.66666f), "two back: x0.667");

			// Angle falloff: a shooter 30° off square-on (bearing 30°) gets the ×0.6 row from the north wall.
			float ang = RM_TrenchCoverMath.AdjustedBlock(0, 0, 0, 1, 6, 10, 0.5f);
			Check(Near(ang, 0.3f, 1e-4f), "angle 31° -> x0.6 (got " + ang.ToString("F3") + ")");
			Check(RM_TrenchCoverMath.AdjustedBlock(0, 0, 0, 1, 10, 0, 0.5f) == 0f, "angle 90° -> none");

			// Basin floor: a 9×9 dug basin, pawn in the middle: neighbours level, no cover.
			Func<int, int, int> basin = (x, z) => Math.Abs(x) <= 4 && Math.Abs(z) <= 4 ? 2 : 0;
			Check(RM_TrenchCoverMath.TrenchBlock(basin, 0, 0, 0, 10, person, 1f) == 0f, "basin floor: level neighbours, 0");
			Check(Near(RM_TrenchCoverMath.TrenchBlock(basin, 0, 4, 0, 10, person, 1f), 0.44f), "basin's wall side facing the shooter: 0.44");

			// Pit cover reads ground: a covered target square is not a hole.
			Check(RM_TrenchCoverMath.GroundDepth(4, true) == 0 && RM_TrenchCoverMath.GroundDepth(4, false) == 4, "intact pit cover reads 0");
			Func<int, int, int> covered = (x, z) => RM_TrenchCoverMath.GroundDepth(z == 0 ? 2 : 0, x == 0 && z == 0);
			Check(RM_TrenchCoverMath.TrenchBlock(covered, 0, 0, 0, 10, person, 1f) == 0f, "pawn on a covered square: 0");

			// Natural water: not dug and no dry bed -> HollowDepth 0 -> no trench.
			Func<int, int, int> lake = (x, z) => RM_Volume.HollowDepth(0, 0, true);
			Check(RM_TrenchCoverMath.TrenchBlock(lake, 0, 0, 0, 10, person, 1f) == 0f, "natural water reads 0");

			// Stacking with sandbags on the lip, and the cap.
			float stacked = RM_TrenchCoverMath.Combine(0.55f, 0.441f, 0.9f);
			Check(Near(stacked, 0.75f), "sandbags 0.55 + 1 m trench -> 0.75 (got " + stacked.ToString("F3") + ")");
			Check(Near(RM_TrenchCoverMath.Combine(0.55f, 0.441f, 0.7f), 0.7f, 1e-5f), "cap 0.7 holds the stack at 0.7");
			Check(Near(RM_TrenchCoverMath.Combine(0.95f, 0.441f, 0.9f), 0.95f, 1e-5f), "cap never lowers vanilla cover");
			Check(RM_TrenchCoverMath.Combine(0.3f, 0f, 0.9f) == 0.3f, "no trench: vanilla untouched");

			// The HitReportFor fold: aim x (1 - vanilla) x factor == aim x (1 - combined).
			float f = RM_TrenchCoverMath.PassFactor(0.55f, stacked);
			Check(Near(0.8f * (1f - 0.55f) * f, 0.8f * (1f - stacked), 1e-5f), "fold keeps the hit chance exact");
			Check(Near(RM_TrenchCoverMath.PassFactor(0f, 0.441f), 0.559f, 1e-4f), "fold with no vanilla cover: x0.559");
			Check(RM_TrenchCoverMath.PassFactor(0.4f, 0.4f) == 1f, "no trench share: factor 1");

			Console.WriteLine();
			Console.WriteLine(fails == 0 ? "PASS: 0 failure(s)" : "FAIL: " + fails + " failure(s)");
			return fails == 0 ? 0 : 1;
		}
	}
}
