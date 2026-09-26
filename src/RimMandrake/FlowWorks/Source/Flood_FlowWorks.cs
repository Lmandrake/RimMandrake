using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>A canal-fed release: an ethereal driver Thing that walks a
	/// fluid outward from its seed cell, one tile per <c>ticksPerTile</c>,
	/// until its volume runs out.
	///
	/// ⚠️ DLC-FREE BY CONSTRUCTION (FLOWWORKS_BUILD_PROGRAM_1 Phase 3).
	/// This class used to subclass <c>RimWorld.Flood</c>. MEASURED against the
	/// 1.6 assembly: <c>Flood</c> is Odyssey CONTENT — <c>Flood.SpawnSetup</c>
	/// opens with <c>if (!ModLister.CheckOdyssey("Flood")) return;</c>
	/// (RimWorld/Flood.cs:71), so without the DLC a subclass spawns, subscribes
	/// to nothing, and never spreads. That single inheritance edge is what made
	/// the whole merged mod hard-require Odyssey, which Pits/ManyWaters/
	/// LiquidTypes never did.
	///
	/// The temp-terrain ENGINE it used underneath is Core and stays:
	/// <c>Map.tempTerrain</c> is constructed unconditionally (Verse/Map.cs:585),
	/// <c>TempTerrainManager.QueueRemoveTerrain</c> and the removal loop in
	/// <c>Tick()</c> carry no DLC gate (RimWorld/TempTerrainManager.cs:44-68 —
	/// the only <c>ModsConfig.OdysseyActive</c> checks in that class guard the
	/// ice <c>FreezeManager</c>), and <c>TerrainGrid.SetTempTerrain</c>
	/// (Verse/TerrainGrid.cs:396) refuses only a non-<c>temporary</c> def, never
	/// a DLC-less game. So the spread walk is reimplemented here over Core
	/// members and the recede policy is unchanged: SetTempTerrain +
	/// QueueRemoveTerrain.
	///
	/// The fluid is laid on the map's TEMPORARY terrain layer and queued for
	/// removal: a release is destructive while it stands but RECOVERABLE --
	/// whatever the cell already was is kept underneath and comes back when the
	/// fluid drains.
	///
	/// 🔑 The channel gate is now an ELIGIBILITY test rather than a refusal at
	/// placement. Vanilla's spread pair (CanFloodSpreadInto /
	/// CanFloodPotentiallySpreadInto) was private and non-virtual, so the old
	/// subclass could only let the walk wander across open ground and decline to
	/// write there -- and then needed a refused-cell counter to notice it was
	/// stuck. Owning the walk removes both: a cell the channel refuses is never
	/// a candidate, so the release cannot wander and the counter is gone.</summary>
	public class Flood_FlowWorks : Thing
	{
		private FluidDef fluidDef;

		private float remainingVolume;

		/// <summary>Tiles this release expects to place; fixes its expand rate,
		/// its recede stagger and its expiry. Set once at spawn, then scribed.</summary>
		private int estimatedFloodedTiles;

		private int floodedTileCount;

		/// <summary>Cells this release has laid fluid on. Scribed; also the
		/// dedupe set, rehydrated into <see cref="placedLookup"/> on load.</summary>
		private List<IntVec3> placedCells = new List<IntVec3>();

		/// <summary>Cells whose cardinal neighbours may still be floodable. The
		/// seed cell starts here and is never itself flooded -- same shape as
		/// vanilla's initial-cell set, which seeds from river cells and floods
		/// outward from them.</summary>
		private List<IntVec3> frontier = new List<IntVec3>();

		private readonly HashSet<IntVec3> placedLookup = new HashSet<IntVec3>();

		/// <summary>Only reached by a flood whose fluidDef went missing; a real
		/// one is destroyed on the next tick before this ever divides anything.</summary>
		private const int FallbackTicksPerTile = 60;

		/// <summary>Ticks per flooded tile -- the fluid's own flow rate, and
		/// directly the expand interval now that this class owns its own walk.
		///
		/// Fixed 2026-09-02 (owner ruling on FLUID_CANAL_FLOOD_TUNING_GAPS_1,
		/// finding 3): rate used to be an ACCIDENT of MaxFloodDurationTicks,
		/// because base Flood computed ExpandIntervalTicks = MaxFloodDurationTicks
		/// / estimatedFloodedTiles. Rate is a real per-fluid field and the
		/// duration is DERIVED from it, not the other way round.</summary>
		private int TicksPerTile => (fluidDef != null) ? Mathf.Max(1, fluidDef.ticksPerTile) : FallbackTicksPerTile;

		/// <summary>How long the whole release takes to finish spreading: one
		/// tile per TicksPerTile, for every tile it can pay for.</summary>
		private int FloodingTicks => TicksPerTile * Mathf.Max(1, estimatedFloodedTiles);

		/// <summary>Tiles this release can actually pay for. Vanilla estimated
		/// (seed cells x FloodWidthRange.max), which for a single-seeded canal
		/// release is 12 regardless of how much fluid the source holds.</summary>
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
		/// keep ticking into every save. FloodingTicks is exactly the time needed
		/// to place every tile the release can pay for; an equal grace on top
		/// covers cells that only open up late (a pawn digging through, a wall
		/// coming down), which is the sole legitimate reason a healthy flood runs
		/// past its own budget.</summary>
		private int ExpiryTick => spawnedTick + 2 * FloodingTicks;

		/// <summary>Exposed for the bridge debug-report surface.</summary>
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
			Scribe_Values.Look(ref estimatedFloodedTiles, "estimatedFloodedTiles", 0);
			Scribe_Values.Look(ref floodedTileCount, "floodedTileCount", 0);
			Scribe_Collections.Look(ref placedCells, "placedCells", LookMode.Value);
			Scribe_Collections.Look(ref frontier, "frontier", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				if (placedCells == null)
				{
					placedCells = new List<IntVec3>();
				}
				if (frontier == null)
				{
					frontier = new List<IntVec3>();
				}
				placedLookup.Clear();
				for (int i = 0; i < placedCells.Count; i++)
				{
					placedLookup.Add(placedCells[i]);
				}
			}
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (respawningAfterLoad || !Spawned)
			{
				// estimatedFloodedTiles, the frontier and the placed set are all
				// scribed, so a reload keeps exactly what this branch computed.
				return;
			}
			estimatedFloodedTiles = PayableTiles;
			placedCells.Clear();
			placedLookup.Clear();
			frontier.Clear();
			frontier.Add(Position);
		}

		protected override void Tick()
		{
			// Fixed 2026-09-02 (opus code review): a fluidDef that vanished (a
			// removed mod, a save-compat gap) silently destroyed this flood every
			// tick with nothing in the log -- indistinguishable from ordinary
			// volume exhaustion. Only log the genuinely-unexpected case.
			if (fluidDef == null || fluidDef.floodTerrain == null)
			{
				Log.ErrorOnce("[RimMandrake.FlowWorks] a Flood_FlowWorks has no fluidDef or no " +
					"floodTerrain (a removed mod's FluidDef?) -- destroying.", thingIDNumber ^ 0x3);
				Destroy();
				return;
			}
			if (remainingVolume <= 0f)
			{
				// SUMP_TAR_HYDROLOGY_1 ruling 3: a release that spent its whole
				// reservoir is the "self-limits" case the ruling names -- cool
				// its own outer edge before it goes.
				CoolFrontToGlass();
				Destroy();
				return;
			}
			// Fixed 2026-09-02 (FLUID_CANAL_FLOOD_TUNING_GAPS_1 finding 2): a
			// flood walled in before its volume ran out ticked forever and
			// scribed into every save. Every tile it already placed is already
			// queued for removal, so an expired flood still drains correctly;
			// nothing leaks.
			//
			// Deliberately NOT cooled: a release reaching this branch is
			// provably STUCK (still had volume left, still had frontier left,
			// and ran out the clock anyway), not a healthy release that spread
			// itself out -- ruling 3's "self-limits" language describes the
			// other two Destroy() paths in this method, not this one.
			if (Find.TickManager.TicksGame > ExpiryTick)
			{
				Destroy();
				return;
			}
			// Nowhere left to grow from at all: provably finished or provably
			// walled in, and either way there is nothing for a later tick to do.
			// This IS the "walls itself in" half of ruling 3's self-limiting case.
			if (frontier.Count == 0)
			{
				CoolFrontToGlass();
				Destroy();
				return;
			}
			if (!this.IsHashIntervalTick(TicksPerTile))
			{
				return;
			}
			SpreadOneTile();
		}

		/// <summary>One tile per expand interval, exactly as the base engine did.
		/// A frontier cell with no floodable neighbour left is dropped rather
		/// than re-examined every interval, so the walk cost falls as the
		/// release closes out.</summary>
		private void SpreadOneTile()
		{
			Map map = Map;
			if (map == null)
			{
				return;
			}
			// §4's "biggest gap", closed. Liquid may only enter a cell that has
			// been excavated, or one already part of a liquid body -- the same
			// test, because a natural body reads through as SUPERDEEP. With the
			// gate consulted here, a refused cell is never a candidate, so the
			// release cannot wander across open ground at all.
			RM_MapComponent_Excavation excavation = RimMandrakeFlowWorksSettings.channelConfinementEnabled
				? map.GetComponent<RM_MapComponent_Excavation>()
				: null;

			int attempts = frontier.Count;
			while (attempts-- > 0 && frontier.Count > 0)
			{
				int pick = Rand.Range(0, frontier.Count);
				IntVec3 from = frontier[pick];
				IntVec3 target = IntVec3.Invalid;
				int seen = 0;
				for (int i = 0; i < 4; i++)
				{
					IntVec3 n = from + GenAdj.CardinalDirections[i];
					if (!CanFloodInto(map, n, excavation))
					{
						continue;
					}
					// Reservoir sample: every eligible neighbour equally likely,
					// in one pass and with no allocation.
					seen++;
					if (Rand.Range(0, seen) == 0)
					{
						target = n;
					}
				}
				if (!target.IsValid)
				{
					frontier.RemoveAt(pick);
					continue;
				}
				PlaceFluid(map, target);
				return;
			}
		}

		/// <summary>Vanilla's own spread gating (CanFloodSpreadInto, which was
		/// private on the base class), plus this mod's channel confinement.</summary>
		private bool CanFloodInto(Map map, IntVec3 c, RM_MapComponent_Excavation excavation)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			if (placedLookup.Contains(c))
			{
				return false;
			}
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			if (t == null || t.IsWater)
			{
				return false;
			}
			if (map.terrainGrid.FoundationAt(c) != null)
			{
				return false;
			}
			if (c.GetEdifice(map) != null)
			{
				return false;
			}
			if (excavation != null && !excavation.CanLiquidEnter(c))
			{
				return false;
			}
			return true;
		}

		/// <summary>The recede policy, unchanged and Core-only (owner ruling
		/// 2026-09-02, "floods must become recoverable"): SetTerrain wrote the
		/// fluid into the PERMANENT top layer -- any constructed floor gone for
		/// good, and the cell unre-diggable forever because Designator_DigCanal
		/// refuses water. SetTempTerrain writes the temp layer instead: the floor
		/// (or the dug channel) stays untouched underneath and TerrainAt reports
		/// it again the moment the queued removal fires.
		///
		/// Deliberately NO tempTerrain.destroysFloors on the flood terrains --
		/// that flag is not "recoverable destruction", it MOVES the floor out of
		/// underGrid permanently (TerrainGrid.SetTempTerrain, Verse/TerrainGrid.cs:418)
		/// and RemoveTempTerrain never puts it back, which is the exact damage
		/// this ruling removes.</summary>
		private void PlaceFluid(Map map, IntVec3 c)
		{
			int recedeStagger = Mathf.Max(0, estimatedFloodedTiles - floodedTileCount);
			map.terrainGrid.SetTempTerrain(c, fluidDef.floodTerrain);
			map.tempTerrain.QueueRemoveTerrain(c, spawnedTick + FloodingTicks + fluidDef.floodedTicks + recedeStagger);
			placedCells.Add(c);
			placedLookup.Add(c);
			frontier.Add(c);
			floodedTileCount++;
			remainingVolume -= fluidDef.volumePerTile;
		}

		/// <summary>SUMP_TAR_HYDROLOGY_1 ruling 3. Writes <see
		/// cref="FluidDef.coolsToGlassEdge"/> onto the PERMANENT layer of
		/// every FRONT cell this release ever placed -- a placed cell
		/// bordering at least one cell the release never reached. Called
		/// only from the two Tick() branches that are a genuinely
		/// self-limiting finish (see their own comments); a no-op when the
		/// fluid carries no glass terrain at all (every fluid but tar,
		/// today), so this changes nothing about water, brine, propane,
		/// chemfuel or the slimes.</summary>
		private void CoolFrontToGlass()
		{
			if (fluidDef == null || fluidDef.coolsToGlassEdge == null)
			{
				return;
			}
			Map map = Map;
			if (map == null)
			{
				return;
			}
			int cooled = 0;
			for (int i = 0; i < placedCells.Count; i++)
			{
				IntVec3 c = placedCells[i];
				if (!IsFrontCell(c))
				{
					continue;
				}
				map.terrainGrid.SetTerrain(c, fluidDef.coolsToGlassEdge);
				cooled++;
			}
			if (cooled > 0)
			{
				Log.Message("[RimMandrake.FlowWorks] " + fluidDef.defName + " release cooled " + cooled
					+ " front cell(s) to " + fluidDef.coolsToGlassEdge.defName + " at " + Position + ".");
			}
		}

		/// <summary>A placed cell is a FRONT cell if any of its 4 cardinal
		/// neighbours is not itself placed -- the release's own outer rim at
		/// whatever moment it stopped growing, map-edge cells included (an
		/// out-of-bounds neighbour is never in <see cref="placedLookup"/>
		/// either, so a cell against the map edge always reads as a front
		/// cell). An interior cell, fully surrounded by other placed cells,
		/// is never a front cell no matter how the release ends.</summary>
		private bool IsFrontCell(IntVec3 c)
		{
			for (int i = 0; i < 4; i++)
			{
				if (!placedLookup.Contains(c + GenAdj.CardinalDirections[i]))
				{
					return true;
				}
			}
			return false;
		}
	}
}
