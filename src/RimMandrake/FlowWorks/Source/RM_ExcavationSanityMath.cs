using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>EXCAVATION_LOAD_SANITY_REPAIR_1 (FL-3). Verse-free so the selftest compiles the production file.
	/// The D/F primitive (RM_ExcavationDepth): 0 &lt;= F &lt;= D &lt;= MaxDepth, and a fluid key is 0 (none) or
	/// 1..paletteCount. Anything else in a loaded grid is repaired in place and counted.</summary>
	public static class RM_ExcavationSanityMath
	{
		public struct Report
		{
			public int depthClamped;
			public int fillClamped;
			public int fluidKeyCleared;

			public int Total => depthClamped + fillClamped + fluidKeyCleared;
		}

		/// <summary>Clamps depth to 0..maxDepth, fill to 0..depth, and clears fluid keys that point past the
		/// palette. Null or mismatched-length grids are skipped (EnsureGrids owns reallocation).</summary>
		public static Report Repair(byte[] depth, byte[] fill, byte[] fluid, int paletteCount, byte maxDepth)
		{
			Report r = default(Report);
			if (depth == null)
			{
				return r;
			}
			for (int i = 0; i < depth.Length; i++)
			{
				if (depth[i] > maxDepth)
				{
					depth[i] = maxDepth;
					r.depthClamped++;
				}
				if (fill != null && fill.Length == depth.Length && fill[i] > depth[i])
				{
					fill[i] = depth[i];
					r.fillClamped++;
				}
				if (fluid != null && fluid.Length == depth.Length && fluid[i] > paletteCount)
				{
					fluid[i] = 0;
					r.fluidKeyCleared++;
				}
			}
			return r;
		}

		/// <summary>Which 1-based palette keys are referenced by any cell. Index 0 is unused.</summary>
		public static bool[] KeysInUse(byte[] fluid, int paletteCount)
		{
			bool[] used = new bool[paletteCount + 1];
			if (fluid != null)
			{
				for (int i = 0; i < fluid.Length; i++)
				{
					int k = fluid[i];
					if (k > 0 && k <= paletteCount)
					{
						used[k] = true;
					}
				}
			}
			return used;
		}

		/// <summary>Builds the old-key to new-key remap that drops every unused key and keeps the order of the rest.
		/// remap[0] = 0; remap[old] = 0 for a dropped key. Returns the new palette size.</summary>
		public static int BuildCompaction(bool[] used, out byte[] remap)
		{
			remap = new byte[used.Length];
			int next = 0;
			for (int k = 1; k < used.Length; k++)
			{
				if (used[k])
				{
					next++;
					remap[k] = (byte)next;
				}
			}
			return next;
		}

		public static void ApplyRemap(byte[] fluid, byte[] remap)
		{
			if (fluid == null)
			{
				return;
			}
			for (int i = 0; i < fluid.Length; i++)
			{
				int k = fluid[i];
				if (k > 0)
				{
					fluid[i] = k < remap.Length ? remap[k] : (byte)0;
				}
			}
		}
	}
}
