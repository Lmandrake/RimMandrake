using System.Linq;
using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>A finite source of one fluid. Sits inert until a dug canal
	/// (RM_Channel_Empty terrain) opens adjacent to it, at which point it
	/// spends its whole volume spawning ONE Flood_FluidCanal seeded there --
	/// a single committed release, not a continuous drip (matches the design
	/// doc's "volume is finite per pit, not a free lever" framing).</summary>
	public class CompFluidReservoir : ThingComp
	{
		private bool spent;

		// Exposed 2026-09-02 (opus code review) for the bridge debug-report
		// surface -- the only genuine per-instance runtime state this comp
		// carries; Props is shared immutable XML config and never changes.
		public bool Spent => spent;

		public CompProperties_FluidReservoir Props => (CompProperties_FluidReservoir)props;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref spent, "spent", false);
		}

		/// <summary>Called by JobDriver_DigCanal.DoEffect the instant a canal
		/// cell is carved. Scans the map's spawned CompFluidReservoirs for one
		/// adjacent (8-way) to the new cell and not yet spent.</summary>
		public static void Notify_CanalCellOpened(Map map, IntVec3 cell)
		{
			// Fixed 2026-09-02 (opus code review): map.listerThings.AllThings is
			// the LIVE backing list, not a copy. TrySpend below spawns a new
			// Flood_FluidCanal onto this same map, which mutates that exact list
			// mid-enumeration -- InvalidOperationException, on the only path that
			// does anything in this whole mod. .ToList() snapshots it first.
			//
			// Also fixed: the adjacency check used thing.Position (the building's
			// origin cell only), so a multi-cell reservoir would never trigger
			// from most of its own footprint. OccupiedRect().ExpandedBy(1) covers
			// the whole building plus its 8-way border, matching what "adjacent
			// to a dug cell" should mean regardless of building size.
			foreach (Thing thing in map.listerThings.AllThings.ToList())
			{
				CompFluidReservoir comp = thing.TryGetComp<CompFluidReservoir>();
				if (comp == null || comp.spent)
				{
					continue;
				}
				if (thing.OccupiedRect().ExpandedBy(1).Contains(cell))
				{
					comp.TrySpend(cell);
				}
			}
		}

		private void TrySpend(IntVec3 seedCell)
		{
			if (spent)
			{
				return;
			}
			// Fixed 2026-09-02 (opus code review): a misconfigured fluidDef (typo'd
			// XML reference, or one missing floodTerrain) left this inert forever
			// with nothing in the log -- indistinguishable from "the notify never
			// fired", the exact failure mode this mod's own live verification
			// needs to be able to tell apart.
			if (Props.fluidDef == null)
			{
				Log.ErrorOnce("[RimMandrake.FluidCanals] " + parent.def.defName +
					"'s CompProperties_FluidReservoir has no fluidDef set.", parent.thingIDNumber ^ 0x1);
				return;
			}
			if (Props.fluidDef.floodTerrain == null)
			{
				Log.ErrorOnce("[RimMandrake.FluidCanals] " + Props.fluidDef.defName +
					" has no floodTerrain set.", parent.thingIDNumber ^ 0x2);
				return;
			}
			// TerrainGrid.SetTempTerrain hard-refuses a terrain without
			// <temporary>true</temporary>, so this fluid would spend the whole
			// reservoir flooding precisely nothing. FluidDef.ConfigErrors says so
			// at load; this says so at the moment of use, where a live test looks.
			if (!Props.fluidDef.floodTerrain.temporary)
			{
				Log.ErrorOnce("[RimMandrake.FluidCanals] " + Props.fluidDef.defName + "'s floodTerrain " +
					Props.fluidDef.floodTerrain.defName + " is not temporary -- it can never be flooded onto a cell.",
					parent.thingIDNumber ^ 0x4);
				return;
			}
			spent = true;
			Flood_FluidCanal flood = (Flood_FluidCanal)ThingMaker.MakeThing(RimMandrakeFluidCanals_DefOf.RM_FluidCanalFlood);
			flood.Configure(Props.fluidDef, Props.volume);
			GenSpawn.Spawn(flood, seedCell, parent.Map);
		}
	}
}
