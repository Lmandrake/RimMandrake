using UnityEngine;
using Verse;

namespace RimMandrake.WeepingStones
{
	/// <summary>
	/// STOCKED_POOL_BUILD_1, wave 2. The husbandry pen (spec §3, "Pens and pool
	/// zones"): "A stocked pool is a designated zone over contiguous pool-water
	/// cells (an Area/zone designator, not a building)." Deliberately thin — this
	/// class is only the player-drawn footprint, same shape as vanilla
	/// Zone_Growing/Zone_Stockpile; <see cref="RM_MapComponent_PoolStock"/> owns
	/// every bit of the state that footprint carries (population, ring-read
	/// state), so a save that loses this zone's C# still degrades to inert data
	/// rather than corrupting anything.
	/// </summary>
	public class RM_Zone_PoolPen : Zone
	{
		public RM_Zone_PoolPen()
		{
		}

		public RM_Zone_PoolPen(ZoneManager zoneManager)
			: base("Pool pen", zoneManager)
		{
		}

		/// <summary>A muddy teal, distinct from vanilla's growing/stockpile/fishing
		/// palette (ZoneColorUtility has no dedicated "next pool color" cycle, so
		/// this is a single fixed color rather than borrowing another zone type's
		/// rotation).</summary>
		protected override Color NextZoneColor => new Color(0.25f, 0.55f, 0.5f);

		public override void PostRegister()
		{
			base.PostRegister();
			NotifyStock();
		}

		public override void PostDeregister()
		{
			Map?.GetComponent<RM_MapComponent_PoolStock>()?.Notify_ZoneRemoved(this);
			base.PostDeregister();
		}

		public override void AddCell(IntVec3 c)
		{
			base.AddCell(c);
			NotifyStock();
		}

		public override void RemoveCell(IntVec3 c)
		{
			base.RemoveCell(c);
			NotifyStock();
		}

		private void NotifyStock()
		{
			Map?.GetComponent<RM_MapComponent_PoolStock>()?.Notify_ZoneChanged(this);
		}

		public override string GetInspectString()
		{
			string baseString = base.GetInspectString();
			RM_PoolBody body = Map?.GetComponent<RM_MapComponent_PoolStock>()?.BodyFor(this);
			if (body == null)
			{
				return baseString;
			}
			return baseString + "\n" + body.StockReport();
		}
	}
}
