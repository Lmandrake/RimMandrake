using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>
	/// What a canal carries once it reaches something wet. The terrain it
	/// floods into already carries whatever behavior it needs (flammability,
	/// extinguishing, pathCost) -- this def only says WHICH terrain and how
	/// fast a reservoir spends itself filling it.
	/// </summary>
	public class FluidDef : Def
	{
		/// <summary>Terrain a flooded cell becomes. Reuse a real vanilla
		/// terrain where one already has the right behavior (e.g. WaterShallow
		/// for water) rather than authoring a parallel one.</summary>
		public TerrainDef fullTerrain;

		/// <summary>Reservoir volume consumed per flooded tile. Lower = a
		/// given reservoir reaches further before running dry.</summary>
		public float volumePerTile = 1f;
	}
}
