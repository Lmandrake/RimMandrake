using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
	// MAPGEN_SCATTER_NRE_1 — GenStep_ScatterThings with filth that cannot NRE.
	//
	// The vanilla defect, read from the decompiled 1.6 engine (RimSage,
	// Verse/GenStep_ScatterThings.ScatterAt): for an ITEM thingDef the thing is
	// placed with GenPlace.TryPlaceThing(..., ThingPlaceMode.Near, ...) and the
	// return value is ignored. TryFindPlaceSpotNear fails SILENTLY (no log) when
	// no cell in its radial search is usable — e.g. a chunk (saveCompressible)
	// already on every walkable cell of a small pocket, which a clusterSize-10
	// scatter can fill by itself. The thing is then never spawned, but the
	// filth block still runs `item2.InBounds(thing.Map)` with thing.Map == null:
	// NullReferenceException at ScatterAt IL 0x13f, which ends the whole step
	// (every later chunk of that scatter is lost on that map).
	//
	// This subclass lets the base class place the thing with filth switched
	// off, then lays the filth itself only around a thing that really spawned.
	// Same fields, same rolls (filthExpandBy / filthChance), no Harmony.
	public class RUT_GenStep_ScatterThingsPlacedFilth : GenStep_ScatterThings
	{
		// The thing base.ScatterAt is about to place, captured from GenerateThing (called exactly once per
		// ScatterAt, 1.6). Holding the reference itself, not a ListerThings delta, also covers a minified
		// thing (listed under MinifiedThing, not thingDef). Map generation is single-threaded.
		[Unsaved(false)]
		private Thing generated;

		protected override Thing GenerateThing()
		{
			generated = base.GenerateThing();
			return generated;
		}

		protected override void ScatterAt(IntVec3 loc, Map map, GenStepParams parms, int stackCount = 1)
		{
			ThingDef filth = filthDef;
			if (filth == null)
			{
				base.ScatterAt(loc, map, parms, stackCount);
				return;
			}

			generated = null;
			filthDef = null;
			try
			{
				base.ScatterAt(loc, map, parms, stackCount);
			}
			finally
			{
				filthDef = filth;
			}

			// A failed placement leaves the thing unspawned (Map == null): no filth. An item that merged into an
			// existing stack is destroyed, not spawned: no filth either (the vanilla filth block would NRE there).
			Thing placed = generated;
			generated = null;
			if (placed == null || !placed.Spawned || placed.Map != map)
			{
				return;
			}
			foreach (IntVec3 c in placed.OccupiedRect().ExpandedBy(filthExpandBy))
			{
				if (Rand.Chance(filthChance) && c.InBounds(map))
				{
					FilthMaker.TryMakeFilth(c, map, filth);
				}
			}
		}
	}
}
