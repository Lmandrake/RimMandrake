using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// One natural liquid body, classified ONCE and then never re-argued
	/// (ruling 16: <i>"a large body shouldn't be able to flap between because
	/// it can't be reduced, it's limitless once and for all"</i>).
	///
	/// A body is the contiguous run of natural liquid cells found by flood fill
	/// on FIRST CONTACT — the first time a canal actually draws from one of its
	/// cells. It is not discovered at map gen, because a lake nobody has dug to
	/// is a lake nobody is paying for.
	///
	/// LIMITLESS is a SENTINEL, not a big number (§5). The off-map continuation
	/// of an edge-touching body IS the reservoir, so conservation of mass holds
	/// without a finite ledger, and nobody has to pick, serialize or render a
	/// magic literal.
	///
	/// LIMITED bodies carry a real stock in fill-units, capped by the 5:1
	/// budget. They run down as a canal draws, recede cell by cell from the
	/// outside in when the stock no longer supports the footprint, and refill
	/// from seepage, rain and season.
	/// </summary>
	public class RM_LiquidBody : IExposable
	{
		public int id;

		/// <summary>Sticky (ruling 16). Set at formation, written to the save,
		/// and never recomputed — there is no code path anywhere in this file
		/// or its manager that assigns it a second time.</summary>
		public bool limitless;

		/// <summary>Fill-units remaining. Meaningless when
		/// <see cref="limitless"/>; a limitless body is never debited.</summary>
		public float stock;

		/// <summary>Σ bed levels of the footprint × volumePerTile × budget (POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK).</summary>
		public float capacity;

		/// <summary>The footprint AS CLASSIFIED. Cells that later recede stay in
		/// this list — they are the body's extent, not its current water — and
		/// appear in <see cref="receded"/> as well. Refill restores them in
		/// reverse order, so the body breathes in and out through the same
		/// cells rather than wandering across the map.</summary>
		public List<IntVec3> cells = new List<IntVec3>();

		/// <summary>Cells given up so far, oldest first. Recession appends;
		/// refill pops from the end.</summary>
		public List<IntVec3> receded = new List<IntVec3>();

		/// <summary>The body was so large that the flood fill hit its cap. An
		/// ocean, in other words — classified limitless on that basis and the
		/// footprint list deliberately truncated rather than holding 40,000
		/// cells in a save file.</summary>
		public bool truncated;

		/// <summary>LIQUID_BODY_FLUID_IDENTITY_1 step 1: which liquid this body is, set ONCE in FormBody from its
		/// base terrain (LiquidDef.terrainSuite -> canalFluid, fallback water) and sticky like `limitless`. Capacity,
		/// refill, recession and the source debit unit all read it (step 3).</summary>
		public FluidDef fluid;

		/// <summary>POND_CAPACITY_FIX_DOUBLING_BED / POND_ELEVATION_BUILD_LAKES_RUN_DEEP: fill-units one bed level is worth
		/// (capacity ÷ the footprint's bed sum, set at formation and by the volume migration). Capacity is always this times the
		/// beds in the footprint, so squares dug out and filled back in, in any order, give the pond back its exact size; and
		/// recession counts the stock in levels with it. 0 = a save from before the field (derived on first use).</summary>
		public float levelUnit;

		/// <summary>POND_ELEVATION_BUILD_LAKES_RUN_DEEP: a footprint bigger than this is saved packed (4 bytes a square, deflated)
		/// instead of one XML node per square; a 40,000-square lake would otherwise add ~0.6 MB of XML to every save. Smaller
		/// bodies keep the old form, so every existing save is written exactly as before.</summary>
		public const int PackFootprintOver = RM_BedMath.OceanWalkCells;

		public RM_LiquidBody()
		{
		}

		public RM_LiquidBody(int id)
		{
			this.id = id;
		}

		public int ActiveCellCount => cells.Count - receded.Count;

		/// <summary>What one cell of footprint is worth in fill-units ON AVERAGE (capacity ÷ cells). Recession compares
		/// against it only with "deepBedsEnabled" off; on, it counts levels (<see cref="levelUnit"/>, RM_BedMath's drawdown).</summary>
		public float PerCellVolume => RM_StockMath.PerCellVolume(capacity, cells.Count);

		public void ExposeData()
		{
			Scribe_Values.Look(ref id, "id", 0);
			Scribe_Values.Look(ref limitless, "limitless", false);
			Scribe_Values.Look(ref stock, "stock", 0f);
			Scribe_Values.Look(ref capacity, "capacity", 0f);
			Scribe_Values.Look(ref truncated, "truncated", false);
			Scribe_Defs.Look(ref fluid, "fluid");
			Scribe_Values.Look(ref levelUnit, "levelUnit", 0f);
			if (Scribe.mode == LoadSaveMode.Saving && cells != null && cells.Count > PackFootprintOver)
			{
				byte[] pc = Pack(cells), pr = Pack(receded);
				DataExposeUtility.LookByteArray(ref pc, "cellsPacked");
				DataExposeUtility.LookByteArray(ref pr, "recededPacked");
			}
			else
			{
				Scribe_Collections.Look(ref cells, "cells", LookMode.Value);
				Scribe_Collections.Look(ref receded, "receded", LookMode.Value);
			}
			if (Scribe.mode == LoadSaveMode.LoadingVars)
			{
				byte[] pc = null, pr = null;
				DataExposeUtility.LookByteArray(ref pc, "cellsPacked");
				DataExposeUtility.LookByteArray(ref pr, "recededPacked");
				if (pc != null)
				{
					cells = Unpack(pc);
					receded = pr != null ? Unpack(pr) : new List<IntVec3>();
				}
			}
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (cells == null)
				{
					cells = new List<IntVec3>();
				}
				if (receded == null)
				{
					receded = new List<IntVec3>();
				}
			}
		}

		/// <summary>RM_BedMath.PackXZ over a footprint list (the recession stack's order kept).</summary>
		public static byte[] Pack(List<IntVec3> list)
		{
			int n = list?.Count ?? 0;
			return RM_BedMath.PackXZ(n, k => list[k].x, k => list[k].z);
		}

		public static List<IntVec3> Unpack(byte[] b)
		{
			int n = RM_BedMath.PackedCount(b);
			var list = new List<IntVec3>(n);
			for (int k = 0; k < n; k++)
			{
				list.Add(new IntVec3(RM_BedMath.PackedX(b, k), 0, RM_BedMath.PackedZ(b, k)));
			}
			return list;
		}

		/// <summary>The inspect line §5 asks for, and it says the throughput
		/// argument out loud rather than making the player infer it.</summary>
		public string StockReport()
		{
			if (limitless)
			{
				return "limitless — the off-map continuation is the reservoir. "
					+ "Supply is still capped per shoreline cell you dig to.";
			}
			// LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: fill-units in litres (a bed level = levelUnit fill-units = 1,000 L)
			float lu = levelUnit > 0f ? levelUnit : (fluid != null && fluid.volumePerTile > 0f ? fluid.volumePerTile : 1f);
			return RM_Volume.FormatLitres(stock / lu * RM_Volume.LitresPerLevel) + " / "
				+ RM_Volume.FormatLitres(capacity / lu * RM_Volume.LitresPerLevel);
		}
	}
}
