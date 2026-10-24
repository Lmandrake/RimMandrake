using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE. Owner 2026-10-24: "you can see the spi[k]es aren't right. They should not be
	/// showing drawn over the paler walls, right? And I needed deeper water to test the spikes. They should be shown as
	/// submerged rapidly."
	///
	/// The spikes used to be one 1x1 sprite at Building altitude, so the stakes covered the pit's far-wall face, its side
	/// bevels and its black outline (RM_ExcavationWalls, drawn at TerrainScatter). Now Building_RM_Spikes lays the
	/// variant's own stakes (RM_SpikeStakes, cut from the owner-accepted PNGs) inside FloorRect: the part of the cell the
	/// walls leave as floor. Water fades them out (SubmergedAlpha): 1 dry, 0.25 at 0.5 m, gone at SubmergeMetres.
	/// Verse-free: the C# SelfTest (SpikeDrawChecks) and the offline scene (Tools/fw_scenes_spikes.py) both run this
	/// math; the Python mirror is held to it by the parity fixture in SpikeDrawChecks.
	/// </summary>
	public static class RM_SpikeDrawMath
	{
		/// <summary>Clear gap (cells) kept between a stake and the floor's edge.</summary>
		public const float Margin = 0.01f;

		/// <summary>Water depth (m) at which the stakes are no longer drawn. A stake is ~0.15-0.18 cell tall.</summary>
		public const float SubmergeMetres = 1.0f;

		/// <summary>Stake opacity under <paramref name="fillLevels"/> of standing liquid (RM_MapComponent_Excavation.FillAt):
		/// (1 - m / SubmergeMetres)^2, so it falls fast: 1 dry, 0.25 at one level (0.5 m), 0 from two levels (1 m).</summary>
		public static float SubmergedAlpha(int fillLevels)
		{
			if (fillLevels <= 0) return 1f;
			float t = 1f - fillLevels * RM_Volume.MetresPerLevel / SubmergeMetres;
			return t <= 0f ? 0f : t * t;
		}

		/// <summary>The visible floor of a dug cell in cell-local coordinates (x east, z north, 0..1), from the same tables
		/// RM_ExcavationWalls draws with. Neighbour levels are RM_ExcavationWalls.NeighbourLevel's (off-map / natural
		/// liquid = level). The DRY faces are used (fill 0): water hides a face's foot, but the stakes stand on the floor
		/// below it, so they keep clear of the whole face at any fill. <paramref name="faces"/> =
		/// excavationWallFacesEnabled (off: the walls layer draws nothing, outline included); <paramref name="outline"/> =
		/// pitOutlineEnabled.</summary>
		public static void FloorRect(int d, int north, int south, int west, int east, bool faces, bool outline,
			out float x0, out float z0, out float x1, out float z1)
		{
			bool lines = faces && outline;
			float top = 0f, left = 0f, right = 0f, bottom = 0f;
			if (faces)
			{
				top = RM_WallFaceMath.NorthFaceHeight(RM_WallFaceMath.ExposedDrop(d, north, 0));
				left = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(d, west, 0));
				right = RM_WallFaceMath.SideFaceWidth(RM_WallFaceMath.ExposedDrop(d, east, 0));
			}
			if (lines)
			{
				if (d - north > 0) top = Math.Max(top, RM_WallFaceMath.RimLine);
				if (d - west > 0) left = Math.Max(left, RM_WallFaceMath.SideLine);
				if (d - east > 0) right = Math.Max(right, RM_WallFaceMath.SideLine);
				if (d - south > 0) bottom = RM_WallFaceMath.SouthLining(d - south);
			}
			x0 = left;
			x1 = 1f - right;
			z0 = bottom;
			z1 = 1f - top;
		}

		/// <summary>A deterministic 32-bit mix of (seed, k). Mirrored bit for bit in Tools/fw_scenes_spikes.py.</summary>
		public static uint Hash(int seed, int k)
		{
			unchecked
			{
				uint x = (uint)seed * 0x9E3779B1u + (uint)k * 0x85EBCA77u;
				x ^= x >> 15;
				x *= 0x2C1B3C6Du;
				x ^= x >> 12;
				x *= 0x297A2D39u;
				x ^= x >> 15;
				return x;
			}
		}

		/// <summary>Floats per laid stake in Layout's output: x, z, w, h (cell-local), u0, v0, u1, v1.</summary>
		public const int Out = 8;

		/// <summary>Lays variant <paramref name="variant"/>'s stakes over the rect at its own density (a staggered grid at
		/// RM_SpikeStakes.Pitch, each slot a hashed stake jittered by up to a quarter pitch), scaled down only if the rect
		/// is smaller than the tallest / widest stake. Every quad lies inside the rect less Margin. Output is sorted far
		/// (north) first so nearer stakes overlap farther ones. Returns the stake count (0 for a rect too small).</summary>
		public static int Layout(int variant, int seed, float x0, float z0, float x1, float z1, List<float> outQuads)
		{
			outQuads.Clear();
			float[] lib = RM_SpikeStakes.Stakes[variant];
			int n = lib.Length / RM_SpikeStakes.Stride;
			float wmax = 0f, hmax = 0f;
			for (int i = 0; i < n; i++)
			{
				wmax = Math.Max(wmax, lib[i * RM_SpikeStakes.Stride]);
				hmax = Math.Max(hmax, lib[i * RM_SpikeStakes.Stride + 1]);
			}
			float fw = x1 - x0 - 2f * Margin, fh = z1 - z0 - 2f * Margin;
			if (n == 0 || fw <= 0f || fh <= 0f) return 0;
			float s = Math.Min(1f, Math.Min(fh / hmax, fw / wmax));
			float px = RM_SpikeStakes.Pitch[variant, 0] * s, pz = RM_SpikeStakes.Pitch[variant, 1] * s;
			float lo = x0 + Margin, hi = x1 - Margin, bot = z0 + Margin, topz = z1 - Margin;
			int k = 0;
			var rows = new List<float[]>();
			for (int r = 0; bot + r * pz <= topz - hmax * s * 0.5f; r++)
			{
				float zb = bot + r * pz;
				float x00 = lo + ((r & 1) == 1 ? px * 0.5f : 0f);
				for (int col = 0; x00 + col * px <= hi; col++, k++)
				{
					float xc = x00 + col * px;
					uint h = Hash(seed, k);
					int j = (int)(h % (uint)n) * RM_SpikeStakes.Stride;
					float w = lib[j] * s, ht = lib[j + 1] * s;
					float jx = (((h >> 8) & 0xFF) / 255f - 0.5f) * 0.5f * px;
					float jz = (((h >> 16) & 0xFF) / 255f - 0.5f) * 0.5f * pz;
					float x = Clamp(xc + jx - w * 0.5f, lo, hi - w);
					float z = Clamp(zb + jz, bot, topz - ht);
					rows.Add(new[] { x, z, w, ht, lib[j + 2], lib[j + 3], lib[j + 4], lib[j + 5], k });
				}
			}
			rows.Sort((a, b) => a[1] != b[1] ? b[1].CompareTo(a[1]) : a[8].CompareTo(b[8]));
			foreach (float[] q in rows)
			{
				for (int i = 0; i < Out; i++) outQuads.Add(q[i]);
			}
			return rows.Count;
		}

		private static float Clamp(float v, float lo, float hi) => v < lo ? lo : (v > hi ? hi : v);

		/// <summary>The variant index (into RM_SpikeStakes.Variants) a texture name like "RM_Spikes_b" names, or -1.</summary>
		public static int VariantOf(string textureName)
		{
			if (string.IsNullOrEmpty(textureName) || textureName.Length < 2 || textureName[textureName.Length - 2] != '_') return -1;
			return RM_SpikeStakes.Variants.IndexOf(textureName[textureName.Length - 1]);
		}
	}
}
