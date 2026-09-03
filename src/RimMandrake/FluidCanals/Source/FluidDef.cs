using System.Collections.Generic;
using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>
	/// What a canal carries once it reaches something wet. The terrain it
	/// floods into already carries whatever behavior it needs (flammability,
	/// extinguishing, pathCost) -- this def only says WHICH terrain, how fast
	/// a reservoir spends itself filling it, and how long the fluid stands
	/// before draining back off.
	/// </summary>
	public class FluidDef : Def
	{
		/// <summary>Terrain a flooded cell becomes. MUST be a temporary terrain
		/// (<c>&lt;temporary&gt;true&lt;/temporary&gt;</c>): a release is laid on
		/// the map's TEMP terrain layer, above whatever the cell already was, so
		/// a dug channel or a constructed floor underneath survives intact and
		/// comes back when the fluid drains. Reuse a real vanilla temporary
		/// terrain where one already has the right behavior (ShallowFloodwater
		/// for water) rather than authoring a parallel one.</summary>
		public TerrainDef floodTerrain;

		/// <summary>Reservoir volume consumed per flooded tile. Lower = a
		/// given reservoir reaches further before running dry.</summary>
		public float volumePerTile = 1f;

		/// <summary>Ticks between one flooded tile and the next: the fluid's own
		/// flow RATE, independent of how much of it a reservoir holds. 60 (one
		/// in-game minute per tile) reads as water running down a channel and
		/// sits in the same band vanilla's own Flood engine works out to on a
		/// real map; a viscous fluid (tar, ooze) sets this far higher.</summary>
		public int ticksPerTile = 60;

		/// <summary>Ticks the fluid stands on a cell after the whole release has
		/// finished spreading, before the map's temp-terrain manager drains it
		/// and hands the cell back. Default is the midpoint of vanilla
		/// SeasonalFlood's own 240000-360000 flooded range.</summary>
		public int floodedTicks = 300000;

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string error in base.ConfigErrors())
			{
				yield return error;
			}
			if (floodTerrain == null)
			{
				yield return "floodTerrain is null -- a fluid with nothing to flood into can never do anything.";
			}
			else if (!floodTerrain.temporary)
			{
				yield return "floodTerrain " + floodTerrain.defName + " is not temporary. TerrainGrid.SetTempTerrain " +
					"refuses any terrain without <temporary>true</temporary>, so this fluid would flood nothing at all.";
			}
			if (volumePerTile <= 0f)
			{
				yield return "volumePerTile must be > 0 -- a reservoir spending 0 per tile never runs dry.";
			}
			if (ticksPerTile < 1)
			{
				yield return "ticksPerTile must be >= 1 (it is the flood's expand interval; 0 divides by zero).";
			}
			if (floodedTicks < 1)
			{
				yield return "floodedTicks must be >= 1.";
			}
		}
	}
}
