using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks
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
		/// comes back when the fluid drains. It must be a def this mod (or a
		/// client) ships: the base game's temporary water terrains all live in
		/// Data/Odyssey, and naming one hard-requires the DLC.</summary>
		public TerrainDef floodTerrain;

		/// <summary>Ruling 5's tier 2 of 3 — half full, read as chest-deep.
		/// <see cref="floodTerrain"/> is tier 1 (trace/shallow), so only the
		/// upper rungs need naming. Must be temporary, same as tier 1.</summary>
		public TerrainDef fillTerrainHalf;

		/// <summary>Ruling 5's tier 3 of 3 — brimming, read as deep. Ruling 26:
		/// fill never captures, so this stays passable however costly.</summary>
		public TerrainDef fillTerrainBrim;

		/// <summary>A flooded SUPERDEEP cell. Separate from
		/// <see cref="fillTerrainBrim"/> because the temp layer wins in
		/// TerrainAt: a passable fill over an impassable SUPERDEEP excavation
		/// would make the hole walkable the moment it filled. Falls back to
		/// the brim terrain when unset, which is the correct behaviour once
		/// program 2 ships fall-in capture and ladders.</summary>
		public TerrainDef fillTerrainSuperdeep;

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

		// ── PHASE 4: stock, recession and refill ──────────────────────────

		/// <summary>The 5:1 budget (§5). Each cell of a natural body supplies at
		/// most this many canal cells' worth of fill, so
		/// <c>capacity = sourceCells * canalCellsPerSourceCell * volumePerTile</c>.
		/// The rule is per source CELL on purpose: a body's throughput is bounded
		/// by how much of it a canal actually touches, independently of how big
		/// the body is. That, not a magic number, is the answer to "can I drain
		/// the ocean?".</summary>
		public float canalCellsPerSourceCell = 5f;

		/// <summary>Ruling 2's seepage baseline: fill-units a LIMITED body regains
		/// per source cell per in-game day with no weather at all. Tuned so a
		/// one-cell seep takes multiple seasons to refill the five canal cells it
		/// can support — "slow and certain", never random.</summary>
		public float groundOozePerSourceCellPerDay = 0.13f;

		/// <summary>Multiplier on <see cref="groundOozePerSourceCellPerDay"/> at a
		/// rain rate of 1. Rain is the fast lane; seepage is the floor.</summary>
		public float rainRefillFactor = 3f;

		/// <summary>What a receded cell of a NATURAL body becomes. A natural lake
		/// cell is not temporary terrain, so RemoveTempTerrain cannot dry it and
		/// the engine must write a dry terrain directly — which is exactly why
		/// the original terrain is recorded first and restored on refill. Mud,
		/// not soil: exposed lakebed should read raw (§18).</summary>
		public TerrainDef recededTerrain;

		/// <summary>The terrain that expresses a fill tier on a cell of depth
		/// <paramref name="depth"/>. Tier 0 is dry and returns null.</summary>
		public TerrainDef FillTerrainFor(int tier, byte depth)
		{
			if (tier <= 0)
			{
				return null;
			}
			if (depth >= RM_ExcavationDepth.Superdeep)
			{
				return fillTerrainSuperdeep ?? fillTerrainBrim ?? floodTerrain;
			}
			if (tier == 1)
			{
				return floodTerrain;
			}
			if (tier == 2)
			{
				return fillTerrainHalf ?? floodTerrain;
			}
			return fillTerrainBrim ?? fillTerrainHalf ?? floodTerrain;
		}

		/// <summary>True if this terrain is one THIS fluid's engine placed, so
		/// the engine never strips a temp terrain some other system owns.</summary>
		public bool OwnsFillTerrain(TerrainDef terrain)
		{
			if (terrain == null)
			{
				return false;
			}
			return terrain == floodTerrain || terrain == fillTerrainHalf
				|| terrain == fillTerrainBrim || terrain == fillTerrainSuperdeep;
		}

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
			foreach (TerrainDef tier in new[] { fillTerrainHalf, fillTerrainBrim, fillTerrainSuperdeep })
			{
				if (tier != null && !tier.temporary)
				{
					yield return "fill tier terrain " + tier.defName + " is not temporary. " +
						"TerrainGrid.SetTempTerrain refuses any terrain without <temporary>true</temporary>, " +
						"so this tier would render nothing and the cell would read as dry at full.";
				}
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
			if (canalCellsPerSourceCell <= 0f)
			{
				yield return "canalCellsPerSourceCell must be > 0 -- a source cell that supplies zero "
					+ "canal cells gives every limited body a capacity of nothing, and no canal ever fills.";
			}
			if (groundOozePerSourceCellPerDay < 0f)
			{
				yield return "groundOozePerSourceCellPerDay must be >= 0 -- a negative seepage drains a "
					+ "body that nothing is drawing from.";
			}
		}
	}
}
