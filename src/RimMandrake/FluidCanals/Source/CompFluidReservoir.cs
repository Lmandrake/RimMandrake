using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>A deep-source fluid feed. Sits inert until a dug canal
	/// (RM_Channel_Empty terrain) opens adjacent to it, at which point it
	/// PRIMES on that cell and starts two independent recurring releases --
	/// owner ruling 2026-09-04 (canon_reintegration_plan.md sec G8, "Fluid
	/// canal refill"): BOTH a steady drip AND periodic re-flood events, not
	/// either/or. "A steady drip baseline (the reservoir breathes) AND
	/// periodic re-flood events (water arriving as an occasion) ... the drip
	/// carries the simulation, the flood carries the drama."
	///
	/// This supersedes the original one-shot/finite design (spend-whole-
	/// volume-once-then-self-destroy): a primed reservoir never runs dry --
	/// it is a rate (Props.dripVolume/dripIntervalTicks and
	/// Props.reFloodVolume/reFloodIntervalTicks), not a stock, matching the
	/// ruling's own framing ("scarcity is rate, not stock").</summary>
	public class CompFluidReservoir : ThingComp
	{
		private bool primed;

		private IntVec3 seedCell = IntVec3.Invalid;

		private int nextDripTick = -1;

		private int nextReFloodTick = -1;

		// Exposed for the bridge debug-report surface.
		public bool Primed => primed;

		public IntVec3 SeedCell => seedCell;

		public int NextDripTick => nextDripTick;

		public int NextReFloodTick => nextReFloodTick;

		public CompProperties_FluidReservoir Props => (CompProperties_FluidReservoir)props;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref primed, "primed", false);
			Scribe_Values.Look(ref seedCell, "seedCell", IntVec3.Invalid);
			Scribe_Values.Look(ref nextDripTick, "nextDripTick", -1);
			Scribe_Values.Look(ref nextReFloodTick, "nextReFloodTick", -1);
		}

		/// <summary>Called by JobDriver_DigCanal.DoEffect the instant a canal
		/// cell is carved. Scans the map's spawned CompFluidReservoirs for one
		/// adjacent (8-way) to the new cell and not yet primed.</summary>
		public static void Notify_CanalCellOpened(Map map, IntVec3 cell)
		{
			// map.listerThings.AllThings is the LIVE backing list; Prime()
			// below spawns a new Flood_FluidCanal onto this same map, which
			// would mutate that exact list mid-enumeration. .ToList() snapshots
			// it first (2026-09-02 fix, still needed).
			foreach (Thing thing in map.listerThings.AllThings.ToList())
			{
				CompFluidReservoir comp = thing.TryGetComp<CompFluidReservoir>();
				if (comp == null || comp.primed)
				{
					continue;
				}
				// OccupiedRect().ExpandedBy(1) covers the whole building plus its
				// 8-way border, matching what "adjacent to a dug cell" should mean
				// regardless of building size (2026-09-02 fix, still needed).
				if (thing.OccupiedRect().ExpandedBy(1).Contains(cell))
				{
					comp.Prime(cell);
				}
			}
		}

		private void Prime(IntVec3 cell)
		{
			if (primed)
			{
				return;
			}
			if (!ValidateFluidDef())
			{
				return;
			}
			primed = true;
			seedCell = cell;
			int ticksNow = Find.TickManager.TicksGame;
			nextDripTick = ticksNow + Mathf.Max(1, Props.dripIntervalTicks);
			nextReFloodTick = ticksNow + Mathf.Max(1, Props.reFloodIntervalTicks);
			// The moment of opening a canal still pays off at once -- fire the
			// first re-flood immediately (the engine's original one-shot
			// behavior), rather than making the player wait a full cadence for
			// the first drop of water.
			SpawnFlood(Props.reFloodVolume);
		}

		public override void CompTickRare()
		{
			base.CompTickRare();
			if (!primed || !parent.Spawned)
			{
				return;
			}
			int ticksNow = Find.TickManager.TicksGame;
			if (ticksNow >= nextDripTick)
			{
				SpawnFlood(Props.dripVolume);
				nextDripTick = ticksNow + Mathf.Max(1, Props.dripIntervalTicks);
			}
			if (ticksNow >= nextReFloodTick)
			{
				SpawnFlood(Props.reFloodVolume);
				nextReFloodTick = ticksNow + Mathf.Max(1, Props.reFloodIntervalTicks);
			}
		}

		/// <summary>Logs the same three misconfiguration cases TrySpend used to
		/// check inline (2026-09-02 opus code review), now shared between Prime
		/// and every recurring SpawnFlood call.</summary>
		private bool ValidateFluidDef()
		{
			if (Props.fluidDef == null)
			{
				Log.ErrorOnce("[RimMandrake.FluidCanals] " + parent.def.defName +
					"'s CompProperties_FluidReservoir has no fluidDef set.", parent.thingIDNumber ^ 0x1);
				return false;
			}
			if (Props.fluidDef.floodTerrain == null)
			{
				Log.ErrorOnce("[RimMandrake.FluidCanals] " + Props.fluidDef.defName +
					" has no floodTerrain set.", parent.thingIDNumber ^ 0x2);
				return false;
			}
			// TerrainGrid.SetTempTerrain hard-refuses a terrain without
			// <temporary>true</temporary>, so this fluid would spend every
			// release flooding precisely nothing.
			if (!Props.fluidDef.floodTerrain.temporary)
			{
				Log.ErrorOnce("[RimMandrake.FluidCanals] " + Props.fluidDef.defName + "'s floodTerrain " +
					Props.fluidDef.floodTerrain.defName + " is not temporary -- it can never be flooded onto a cell.",
					parent.thingIDNumber ^ 0x4);
				return false;
			}
			return true;
		}

		private void SpawnFlood(float volume)
		{
			if (volume <= 0f || !ValidateFluidDef())
			{
				return;
			}
			if (!seedCell.IsValid || parent.Map == null || !seedCell.InBounds(parent.Map))
			{
				return;
			}
			// A drip/re-flood arriving while the previous release at this same
			// seed cell is still spreading would stack two Flood_FluidCanal
			// drivers on one cell. Both are harmless individually (ethereal,
			// no collision), but skipping this cycle when one is still live is
			// simpler than tracking a reference, and self-heals on the next
			// CompTickRare -- the cadence just slips by up to 250 ticks, never
			// drops a release outright.
			if (FloodActiveAt(seedCell))
			{
				return;
			}
			Flood_FluidCanal flood = (Flood_FluidCanal)ThingMaker.MakeThing(RimMandrakeFluidCanals_DefOf.RM_FluidCanalFlood);
			flood.Configure(Props.fluidDef, volume);
			GenSpawn.Spawn(flood, seedCell, parent.Map);
		}

		private bool FloodActiveAt(IntVec3 cell)
		{
			List<Thing> here = cell.GetThingList(parent.Map);
			for (int i = 0; i < here.Count; i++)
			{
				if (here[i] is Flood_FluidCanal flood && flood.Spawned)
				{
					return true;
				}
			}
			return false;
		}
	}
}
