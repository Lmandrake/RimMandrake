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

		/// <summary>sourceCells * canalCellsPerSourceCell * volumePerTile.</summary>
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

		public RM_LiquidBody()
		{
		}

		public RM_LiquidBody(int id)
		{
			this.id = id;
		}

		public int ActiveCellCount => cells.Count - receded.Count;

		/// <summary>What one cell of footprint is worth in fill-units. The 5:1
		/// budget read backwards, and the number recession compares against.</summary>
		public float PerCellVolume => cells.Count > 0 ? capacity / cells.Count : 0f;

		public void ExposeData()
		{
			Scribe_Values.Look(ref id, "id", 0);
			Scribe_Values.Look(ref limitless, "limitless", false);
			Scribe_Values.Look(ref stock, "stock", 0f);
			Scribe_Values.Look(ref capacity, "capacity", 0f);
			Scribe_Values.Look(ref truncated, "truncated", false);
			Scribe_Collections.Look(ref cells, "cells", LookMode.Value);
			Scribe_Collections.Look(ref receded, "receded", LookMode.Value);
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

		/// <summary>The inspect line §5 asks for, and it says the throughput
		/// argument out loud rather than making the player infer it.</summary>
		public string StockReport()
		{
			if (limitless)
			{
				return "limitless — the off-map continuation is the reservoir. "
					+ "Supply is still capped per shoreline cell you dig to.";
			}
			return stock.ToString("F0") + " / " + capacity.ToString("F0") + " fill-units";
		}
	}
}
