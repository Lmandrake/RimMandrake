using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT step 1 (design/RimMandrake/canal_cover_design_2026-10-17.md §3-§4): the
	/// pure arithmetic of trench cover. No Verse, no Unity: compiled straight into the offline selftest
	/// (Source/SelfTestTrench), so the numbers the game uses are the numbers the test checks.
	///
	/// A pawn standing in a dug square is covered by every neighbour whose ground is HIGHER than its own floor, read the way
	/// vanilla reads a sandbag in that neighbour (Verse/CoverUtility.cs, TryFindAdjustedCoverInCell, 1.6): angle falloff
	/// (×1.75 for a diagonal neighbour; under 15° full, then ×0.8/×0.6/×0.4/×0.2, none from 65°), distance falloff from the
	/// shooter to the wall square (under 1.9 ×0.3333, under 2.9 ×0.66666), the shooter's own square skipped, combined
	/// num += (1 − num) × block. The wall's base block is 0.75 × clamp(h / H, 0, 1) × strength (owner Q3: waist-deep a bit
	/// under sandbags' 0.55, chest-deep a bit over). Depth comes in NOTCHES (0.5 m each) until P4 lands metres.
	/// </summary>
	public static class RM_TrenchCoverMath
	{
		/// <summary>A full wall's block chance: vanilla's CoverUtility.CoverPercent_Corner / a Full-fillage Thing.</summary>
		public const float FullWallBlock = 0.75f;

		/// <summary>Under this a step is no wall worth the name (§4 table, the under-25 cm row).</summary>
		public const float MinWallMetres = 0.25f;

		/// <summary>A person (body size 1) is about 1.7 m; H scales with sqrt(body size) (relative climb design §8.2).</summary>
		public const float PersonHeightMetres = 1.7f;

		public const float DefaultStrength = 1f;

		public const float DefaultCap = 0.9f;

		public const float MetresPerNotch = RM_Volume.MetresPerNotch;

		/// <summary>The height H of a creature of this body size, in metres.</summary>
		public static float HeightMetres(float bodySize)
		{
			if (float.IsNaN(bodySize) || bodySize <= 0.01f)
			{
				bodySize = 0.01f;
			}
			return PersonHeightMetres * (float)Math.Sqrt(bodySize);
		}

		/// <summary>One wall square's base block chance before angle and distance: 0.75 × clamp(h/H, 0, 1) × strength.</summary>
		public static float WallBlock(float wallMetres, float heightMetres, float strength)
		{
			if (!(wallMetres >= MinWallMetres) || !(heightMetres > 0f) || !(strength > 0f))
			{
				return 0f;
			}
			float r = wallMetres / heightMetres;
			if (r > 1f)
			{
				r = 1f;
			}
			float b = FullWallBlock * r * strength;
			return b > 1f ? 1f : b;
		}

		/// <summary>Vanilla's IntVec3.AngleFlat: the compass bearing of (dx, dz) in degrees, 0 = +z, 0 for the zero vector.</summary>
		public static float AngleFlat(int dx, int dz)
		{
			if (dx == 0 && dz == 0)
			{
				return 0f;
			}
			double a = Math.Atan2(dx, dz) * 180.0 / Math.PI;
			return (float)(a < 0 ? a + 360.0 : a);
		}

		/// <summary>Vanilla's GenGeo.AngleDifferenceBetween: the smaller angle between two bearings, 0..180.</summary>
		public static float AngleDifference(float a, float b)
		{
			float d = Math.Abs(a - b) % 360f;
			return d > 180f ? 360f - d : d;
		}

		/// <summary>Vanilla's angle falloff (diagonal already folded in as ×1.75 by the caller); 0 = no cover at all.</summary>
		public static float AngleFactor(float angle)
		{
			if (angle < 15f)
			{
				return 1f;
			}
			if (angle < 27f)
			{
				return 0.8f;
			}
			if (angle < 40f)
			{
				return 0.6f;
			}
			if (angle < 52f)
			{
				return 0.4f;
			}
			return angle < 65f ? 0.2f : 0f;
		}

		/// <summary>Vanilla's distance falloff: a shooter close to the cover square sees past it.</summary>
		public static float DistanceFactor(float shooterToWall)
		{
			if (shooterToWall < 1.9f)
			{
				return 0.3333f;
			}
			return shooterToWall < 2.9f ? 0.66666f : 1f;
		}

		/// <summary>One neighbour's adjusted block, exactly vanilla's TryFindAdjustedCoverInCell with the wall's base block in
		/// place of the cover Thing's. 0 when the shooter stands on the target or on the wall square.</summary>
		public static float AdjustedBlock(int tx, int tz, int nx, int nz, int sx, int sz, float baseBlock)
		{
			if (baseBlock <= 0f || (sx == tx && sz == tz) || (sx == nx && sz == nz))
			{
				return 0f;
			}
			float angle = AngleDifference(AngleFlat(nx - tx, nz - tz), AngleFlat(sx - tx, sz - tz));
			if (nx != tx && nz != tz)
			{
				angle *= 1.75f;
			}
			float f = AngleFactor(angle);
			if (f <= 0f)
			{
				return 0f;
			}
			float ddx = sx - nx, ddz = sz - nz;
			return baseBlock * f * DistanceFactor((float)Math.Sqrt(ddx * ddx + ddz * ddz));
		}

		// Vanilla GenAdj.AdjacentCells order (the order does not change the combined product).
		private static readonly int[] Dx8 = { 0, 1, 1, 1, 0, -1, -1, -1 };
		private static readonly int[] Dz8 = { 1, 1, 0, -1, -1, -1, 0, 1 };

		/// <summary>The combined trench block chance for a target standing at (tx, tz) shot from (sx, sz).
		/// <paramref name="depthAt"/> answers a square's ground depth in notches (dug or dry-bed hollow, an intact pit cover
		/// read as 0, natural water 0) and -1 out of bounds. 0 when the target's own square is not below a neighbour.</summary>
		public static float TrenchBlock(Func<int, int, int> depthAt, int tx, int tz, int sx, int sz, float heightMetres,
			float strength)
		{
			int own = depthAt(tx, tz);
			if (own <= 0)
			{
				return 0f;
			}
			float num = 0f;
			for (int i = 0; i < 8; i++)
			{
				int nx = tx + Dx8[i], nz = tz + Dz8[i];
				int n = depthAt(nx, nz);
				if (n < 0 || n >= own)
				{
					continue;
				}
				float b = AdjustedBlock(tx, tz, nx, nz, sx, sz, WallBlock((own - n) * MetresPerNotch, heightMetres, strength));
				num += (1f - num) * b;
			}
			return num;
		}

		/// <summary>The square depth trench cover reads: the hollow depth, an intact pit cover read as ground (0).</summary>
		public static int GroundDepth(int hollowNotches, bool intactCover)
		{
			return intactCover || hollowNotches < 0 ? 0 : hollowNotches;
		}

		/// <summary>Vanilla cover and trench cover stacked by vanilla's own rule, 1 − (1 − v)(1 − t), capped by the
		/// "trench plus sandbags" setting; never below vanilla's own value (the cap limits only what the trench adds).</summary>
		public static float Combine(float vanilla, float trench, float cap)
		{
			if (!(trench > 0f))
			{
				return vanilla;
			}
			float c = 1f - (1f - vanilla) * (1f - trench);
			if (c > cap)
			{
				c = cap;
			}
			return c < vanilla ? vanilla : c;
		}

		/// <summary>The trench's share of a combined block, as a factor on hit chance: (1 − combined) / (1 − vanilla).
		/// HitReportFor puts vanilla's block back in the cover field and folds this in, so a trench "miss" flies wild
		/// instead of at a cover Thing that does not exist (design §2, the null-cover trap).</summary>
		public static float PassFactor(float vanilla, float combined)
		{
			if (!(combined > vanilla) || vanilla >= 1f)
			{
				return 1f;
			}
			float f = (1f - combined) / (1f - vanilla);
			return f < 0f ? 0f : (f > 1f ? 1f : f);
		}
	}
}
