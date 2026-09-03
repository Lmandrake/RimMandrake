using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>A canal-fed flood. Subclasses vanilla's own Flood (Odyssey) --
	/// the cellular open-ground spread engine SeasonalFlood/TorrentialRainFlood
	/// already use -- rather than writing a parallel spread tick from scratch.
	/// Spreads from its seed cell across open, non-water, non-edifice ground
	/// (vanilla's own gating, not channel-constrained) until its volume, set
	/// by the CompFluidReservoir that spawned it, runs out.
	///
	/// The fluid is laid on the map's TEMPORARY terrain layer and queued for
	/// removal, exactly as SeasonalFlood does: a release is destructive while
	/// it stands but RECOVERABLE -- whatever the cell already was is kept
	/// underneath and comes back when the fluid drains.</summary>
	public class Flood_FluidCanal : Flood
	{
		private FluidDef fluidDef;

		private float remainingVolume;

		/// <summary>Only reached by a flood whose fluidDef went missing; a real
		/// one is destroyed on the next tick before this ever divides anything.</summary>
		private const int FallbackTicksPerTile = 60;

		/// <summary>Ticks per flooded tile -- the fluid's own flow rate.
		///
		/// Fixed 2026-09-02 (owner ruling on FLUID_CANAL_FLOOD_TUNING_GAPS_1,
		/// finding 3): rate used to be an ACCIDENT of MaxFloodDurationTicks.
		/// Base Flood computes ExpandIntervalTicks = MaxFloodDurationTicks /
		/// estimatedFloodedTiles, so the old flat 30000 against a 12-tile
		/// estimate meant one tile per 2500 ticks -- an in-game HOUR per tile,
		/// and a 60-volume reservoir taking ~2.5 in-game days to spend. Rate is
		/// now a real per-fluid field and MaxFloodDurationTicks is DERIVED from
		/// it, so the base class's own division returns exactly ticksPerTile
		/// and MaxFloodDurationTicks becomes a genuine duration again.</summary>
		private int TicksPerTile => (fluidDef != null) ? Mathf.Max(1, fluidDef.ticksPerTile) : FallbackTicksPerTile;

		protected override int MaxFloodDurationTicks => TicksPerTile * Mathf.Max(1, estimatedFloodedTiles);

		/// <summary>Tiles this release can actually pay for. Base Flood estimates
		/// (seed cells x FloodWidthRange.max), which for a single-seeded canal
		/// release is 12 regardless of how much fluid the reservoir holds.</summary>
		private int PayableTiles
		{
			get
			{
				if (fluidDef == null || fluidDef.volumePerTile <= 0f)
				{
					return 1;
				}
				return Mathf.Max(1, Mathf.CeilToInt(remainingVolume / fluidDef.volumePerTile));
			}
		}

		/// <summary>Past this the flood is done or provably stuck, and must not
		/// keep ticking into every save. FloodingTicks is now exactly the time
		/// needed to place every tile the reservoir can pay for; an equal grace
		/// on top covers cells that only open up late (a pawn digging through,
		/// a wall coming down), which is the sole legitimate reason a healthy
		/// flood runs past its own budget.</summary>
		private int ExpiryTick => spawnedTick + 2 * FloodingTicks;

		/// <summary>Exposed for the bridge debug-report surface -- floodedTileCount
		/// on the base class is protected.</summary>
		public int FloodedTileCount => floodedTileCount;

		public float RemainingVolume => remainingVolume;

		/// <summary>Exposed for the bridge debug-report surface: the tick this
		/// flood gives up, which is the thing finding 2's fix has to be watched
		/// against live.</summary>
		public int ExpiresAtTick => ExpiryTick;

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

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (respawningAfterLoad || !Spawned)
			{
				// Base SpawnSetup destroys the flood outright when no seed cell is
				// open; estimatedFloodedTiles is scribed, so a reload keeps the
				// value this branch already computed.
				return;
			}
			estimatedFloodedTiles = PayableTiles;
		}

		protected override void Tick()
		{
			// Fixed 2026-09-02 (opus code review): a fluidDef that vanished (a
			// removed mod, a save-compat gap) silently destroyed this flood every
			// tick with nothing in the log -- indistinguishable from ordinary
			// volume exhaustion. Only log the genuinely-unexpected case.
			if (fluidDef == null)
			{
				Log.ErrorOnce("[RimMandrake.FluidCanals] a Flood_FluidCanal has no fluidDef " +
					"(a removed mod's FluidDef?) -- destroying.", thingIDNumber ^ 0x3);
				Destroy();
				return;
			}
			if (remainingVolume <= 0f)
			{
				Destroy();
				return;
			}
			// Fixed 2026-09-02 (FLUID_CANAL_FLOOD_TUNING_GAPS_1 finding 2): base
			// Flood has no destroy path when it runs out of reachable ground --
			// noPossibleCell is private with no accessor -- so a flood walled in
			// before its volume ran out ticked forever and scribed into every
			// save. Safe to cut it off only now that MaxFloodDurationTicks is a
			// real duration (finding 3, above) rather than a rate divisor. Every
			// tile it already placed is already queued for removal, so an expired
			// flood still drains correctly; nothing leaks.
			if (Find.TickManager.TicksGame > ExpiryTick)
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
			if (fluidDef == null || fluidDef.floodTerrain == null || remainingVolume <= 0f)
			{
				return;
			}
			// Fixed 2026-09-02 (owner ruling on FLUID_CANAL_FLOOD_TUNING_GAPS_1,
			// finding 1): "floods must become recoverable, matching vanilla's
			// SeasonalFlood pattern". SetTerrain wrote the fluid into the
			// PERMANENT top layer -- any constructed floor gone for good, and the
			// cell unre-diggable forever because Designator_DigCanal refuses
			// water. SetTempTerrain writes the temp layer instead: the floor (or
			// the dug channel) stays untouched underneath and TerrainAt reports
			// it again the moment the queued removal fires.
			//
			// Deliberately NO tempTerrain.destroysFloors on the flood terrains --
			// that flag is not "recoverable destruction", it MOVES the floor out
			// of underGrid permanently (TerrainGrid.SetTempTerrain) and
			// RemoveTempTerrain never puts it back, which is the exact damage
			// this ruling removes. Vanilla's own ShallowFloodwater carries no
			// tempTerrain block for the same reason.
			int recedeStagger = Mathf.Max(0, estimatedFloodedTiles - floodedTileCount);
			Map.terrainGrid.SetTempTerrain(cell, fluidDef.floodTerrain);
			Map.tempTerrain.QueueRemoveTerrain(cell, spawnedTick + FloodingTicks + fluidDef.floodedTicks + recedeStagger);
			remainingVolume -= fluidDef.volumePerTile;
		}
	}
}
