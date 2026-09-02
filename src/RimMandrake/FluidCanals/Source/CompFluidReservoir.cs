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
			foreach (Thing thing in map.listerThings.AllThings)
			{
				CompFluidReservoir comp = thing.TryGetComp<CompFluidReservoir>();
				if (comp == null || comp.spent)
				{
					continue;
				}
				if (thing.Position.DistanceToSquared(cell) <= 2)
				{
					comp.TrySpend(cell);
				}
			}
		}

		private void TrySpend(IntVec3 seedCell)
		{
			if (spent || Props.fluidDef == null || Props.fluidDef.fullTerrain == null)
			{
				return;
			}
			spent = true;
			Flood_FluidCanal flood = (Flood_FluidCanal)ThingMaker.MakeThing(RimMandrakeFluidCanals_DefOf.RM_FluidCanalFlood);
			flood.Configure(Props.fluidDef, Props.volume);
			GenSpawn.Spawn(flood, seedCell, parent.Map);
		}
	}
}
