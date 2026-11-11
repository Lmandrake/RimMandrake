using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>EXCAVATION_LOAD_SANITY_REPAIR_1 (FL-3). Verse-free so the selftest compiles the production file.
	/// The D/F primitive (RM_ExcavationDepth): 0 &lt;= F &lt;= D &lt;= the 20 m ceiling (RM_DigDepthMath.MaxDigCeiling, never the cap setting), and a fluid key is 0 (none) or
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

		/// <summary>WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES: a cell's part-notch (decilitres below one whole notch of
		/// <paramref name="unit"/>) must be under one notch, zero on an undug cell, and zero on a brim-full one (water never stands
		/// above the brim). Returns the cells repaired. Null or mismatched grids are skipped.</summary>
		public static int RepairPart(byte[] depth, byte[] fill, ushort[] part, int unit)
		{
			int n = 0;
			if (depth == null || fill == null || part == null || part.Length != depth.Length || fill.Length != depth.Length)
			{
				return 0;
			}
			for (int i = 0; i < depth.Length; i++)
			{
				if (part[i] == 0)
				{
					continue;
				}
				if (part[i] >= unit || depth[i] == 0 || fill[i] >= depth[i])
				{
					part[i] = 0;
					n++;
				}
			}
			return n;
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

		/// <summary>The most palette entries a byte grid holds (key 0 = none, 255 kept spare).</summary>
		public const int MaxPaletteKeys = 254;

		/// <summary>FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO (FlowWorks P7, GPT G3.6): the key for <paramref name="fluid"/>,
		/// allocating one if it is new. A full palette is first compacted IN THE RUNNING SESSION (entries no cell
		/// references are dropped and the grid remapped, the same rule as the load repair), so a long session never
		/// runs out while a key is free. Returns 0 for a null fluid, and 0 for a real fluid only when every key is in
		/// use by a cell: the caller must then REFUSE the write (key 0 would read as dry and be re-stamped as the
		/// map's ActiveFluid, silently changing the liquid's identity). <paramref name="dropped"/> = entries compacted.</summary>
		public static byte AllocateKey<T>(System.Collections.Generic.List<T> palette, byte[] grid, T fluid, int cap, out int dropped)
			where T : class
		{
			dropped = 0;
			if (fluid == null)
			{
				return 0;
			}
			int i = palette.IndexOf(fluid);
			if (i >= 0)
			{
				return (byte)(i + 1);
			}
			if (cap > MaxPaletteKeys)
			{
				cap = MaxPaletteKeys;
			}
			if (palette.Count >= cap)
			{
				bool[] used = KeysInUse(grid, palette.Count);
				byte[] remap;
				int newCount = BuildCompaction(used, out remap);
				if (newCount < palette.Count)
				{
					System.Collections.Generic.List<T> compact = new System.Collections.Generic.List<T>(newCount);
					for (int k = 1; k < used.Length; k++)
					{
						if (used[k])
						{
							compact.Add(palette[k - 1]);
						}
					}
					ApplyRemap(grid, remap);
					dropped = palette.Count - newCount;
					palette.Clear();
					palette.AddRange(compact);
				}
				if (palette.Count >= cap)
				{
					return 0;
				}
			}
			palette.Add(fluid);
			return (byte)palette.Count;
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
