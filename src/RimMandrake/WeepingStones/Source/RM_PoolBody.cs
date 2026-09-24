using Verse;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 2. Ring-density READ state for one stocked
	/// pool (spec §3's READ verb): "Ring density on the water IS the stock
	/// gauge — art states, no inspector-diving." No overlay art ships this
	/// wave (owed, see the item's ledger note) — the state is exposed via the
	/// zone's inspect string in the meantime, same information, plainer
	/// presentation.
	/// </summary>
	public enum RM_PoolStockState
	{
		/// <summary>Murrin rings are up, no vhorrin, population healthy relative to footprint.</summary>
		Healthy,

		/// <summary>Population present but thin relative to the pen's footprint — hungry or predated (spec §3).</summary>
		Thin,

		/// <summary>No rings at all — the dead-oasis image as farm telemetry (spec §3's READ row, §10b).</summary>
		Silent,

		/// <summary>One wide slow ring doing all the surfacing — a live RM_Vhorrin occupies the pen.
		/// This wave only DETECTS the state (a vhorrin already present is read correctly); nothing
		/// yet SPAWNS one — the OVERDRAW-to-emergence trigger is next wave's job (see the item's
		/// ledger note).</summary>
		Vhorrin,
	}

	/// <summary>
	/// One stocked pool's bookkeeping — the per-pool-body record the spec calls the
	/// "honest hard part" (§3's build table: "contiguous water bodies identified,
	/// tracked across terrain edits, scribed"). Pattern stolen from
	/// <c>RimMandrake.FlowWorks.RM_LiquidBody</c> per the item's own instruction: a
	/// sticky id assigned once, scribed state, one owner (<see cref="RM_MapComponent_PoolStock"/>)
	/// doing the bookkeeping rather than the zone re-deriving it every read.
	///
	/// UNLIKE RM_LiquidBody, this body's footprint is never flood-filled from raw
	/// terrain — the footprint IS the player-drawn <see cref="RM_Zone_PoolPen"/> (spec
	/// §3: "an Area/zone designator, not a building"), so "first contact" here is
	/// "the zone was registered", not a BFS over the map. <see cref="zoneId"/> is the
	/// join key back to that zone; the live <c>Zone</c> object itself is never scribed
	/// (zones already scribe themselves via the map's ZoneManager).
	/// </summary>
	public class RM_PoolBody : IExposable
	{
		public int id;

		/// <summary>Join key to the RM_Zone_PoolPen this body tracks. -1 means orphaned
		/// (its zone was deleted without going through Notify_ZoneRemoved) and the body
		/// is pruned on the next FinalizeInit/Pulse that notices.</summary>
		public int zoneId = -1;

		/// <summary>Live pool-fauna pawns standing in the pen's cells, as of the last
		/// pulse — the population half of the READ gauge.</summary>
		public float population;

		public RM_PoolStockState state = RM_PoolStockState.Silent;

		public RM_PoolBody()
		{
		}

		public RM_PoolBody(int id)
		{
			this.id = id;
		}

		public void ExposeData()
		{
			Scribe_Values.Look(ref id, "id", 0);
			Scribe_Values.Look(ref zoneId, "zoneId", -1);
			Scribe_Values.Look(ref population, "population", 0f);
			Scribe_Values.Look(ref state, "state", RM_PoolStockState.Silent);
		}

		/// <summary>The inspect line the zone's GetInspectString appends — same
		/// "say the mechanism out loud" precedent as RM_LiquidBody.StockReport().</summary>
		public string StockReport()
		{
			switch (state)
			{
				case RM_PoolStockState.Silent:
					return "No rings — the pool reads silent.";
				case RM_PoolStockState.Thin:
					return "Rings are thin: " + population.ToString("F0") + " stock.";
				case RM_PoolStockState.Vhorrin:
					return "One wide slow ring. Something has taken over this pen.";
				default:
					return "Rings are up: " + population.ToString("F0") + " stock.";
			}
		}
	}
}
