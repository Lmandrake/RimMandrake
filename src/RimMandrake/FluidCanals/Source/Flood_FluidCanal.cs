using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>A canal-fed flood. Subclasses vanilla's own Flood (Odyssey) --
	/// the cellular open-ground spread engine SeasonalFlood/TorrentialRainFlood
	/// already use -- rather than writing a parallel spread tick from scratch.
	/// Spreads from its seed cell across open, non-water, non-edifice ground
	/// (vanilla's own gating, not channel-constrained) until its volume, set
	/// by the CompFluidReservoir that spawned it, runs out.</summary>
	public class Flood_FluidCanal : Flood
	{
		private FluidDef fluidDef;

		private float remainingVolume;

		protected override int MaxFloodDurationTicks => 30000;

		/// <summary>Exposed for the bridge debug-report surface -- floodedTileCount
		/// on the base class is protected.</summary>
		public int FloodedTileCount => floodedTileCount;

		public float RemainingVolume => remainingVolume;

		public void Configure(FluidDef fluid, float volume)
		{
			fluidDef = fluid;
			remainingVolume = volume;
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Defs.Look(ref fluidDef, "fluidDef");
			Scribe_Values.Look(ref remainingVolume, "remainingVolume", 0f);
		}

		protected override void Tick()
		{
			if (fluidDef == null || remainingVolume <= 0f)
			{
				Destroy();
				return;
			}
			base.Tick();
		}

		protected override IEnumerable<(IntVec3, int)> GetInitialCells(Map map)
		{
			yield return (Position, FloodWidthRange.RandomInRange);
		}

		protected override void SpreadFlood(IntVec3 cell, TerrainDef sourceTerrain)
		{
			if (fluidDef == null || remainingVolume <= 0f)
			{
				return;
			}
			Map.terrainGrid.SetTerrain(cell, fluidDef.fullTerrain);
			remainingVolume -= fluidDef.volumePerTile;
		}
	}
}
