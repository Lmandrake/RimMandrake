using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Miasma
{
	/// <summary>
	/// MIASMA_SCUTTLER_PREDATION_1. Wires the five RM_Miasma_Predators.xml
	/// carnivorous plants to actually kill the arthropod-floor scuttlers
	/// named in Props.preyDefNames within Props.huntRadius, restricted to
	/// wild (unfactioned) pawns of exactly those defNames — never a
	/// colonist or a tame animal, per this biome's own owner ruling
	/// (RM_Miasma_Predators.xml's header).
	///
	/// Killing the prey via Pawn.Kill is the whole "population accounting"
	/// story: RM_MapComponent_VerminPopulation (mandrake.rm.creaturebehaviors)
	/// recomputes its counts from map.mapPawns.AllPawnsSpawned every 250
	/// ticks, so a dead scuttler simply stops being counted — no separate
	/// pool-decrement call is needed or exists.
	///
	/// Plant never overrides Tick(), only TickLong() (RimSage-verified against
	/// decompiled 1.6 source) — ThingWithComps.TickLong() is what calls
	/// CompTickLong() on each comp, so this overrides that, not CompTick(),
	/// and needs no manual interval throttle: the engine's own Long ticker
	/// already gates the cadence.
	///
	/// Prey scan reuses this codebase's own established idiom
	/// (RM_CompVerminBreeder.FoodExistsNearby, CreatureBehaviors): one
	/// listerThings.ThingsOfDef(def) call per named prey def, filtered by
	/// distance — cheap at this scale, no new scanning idiom introduced.
	///
	/// Tell: a floating mote text at the kill site (same plain-string idiom
	/// already used elsewhere in this mod family, e.g. GeneSeeker.cs's
	/// "Entry retrieved"/Slimification.cs's "Entry recorded") — real,
	/// visible, in-world evidence a kill happened. The five plants' own
	/// unique per-species tells (cloudy vessel, closed blades, scuttler-free
	/// mud) are prose targets for a future ART/graphic-state pass, not built
	/// here — this comp gives every one of them the same readable signal in
	/// the meantime, which is what this item's criteria actually asks for.
	/// </summary>
	public class RM_CompPlantPredator : ThingComp
	{
		private RM_CompProperties_PlantPredator Props => (RM_CompProperties_PlantPredator)props;

		public override void CompTickLong()
		{
			base.CompTickLong();
			if (!RM_MiasmaSettings.plantPredationEnabled || !parent.Spawned || Props.preyDefNames.NullOrEmpty())
			{
				return;
			}

			Map map = parent.Map;
			float radiusSq = Props.huntRadius * Props.huntRadius;
			Pawn nearest = null;
			float nearestDistSq = radiusSq;

			for (int d = 0; d < Props.preyDefNames.Count; d++)
			{
				ThingDef preyDef = DefDatabase<ThingDef>.GetNamedSilentFail(Props.preyDefNames[d]);
				if (preyDef == null)
				{
					continue;
				}

				List<Thing> things = map.listerThings.ThingsOfDef(preyDef);
				for (int i = 0; i < things.Count; i++)
				{
					if (!(things[i] is Pawn candidate) || !candidate.Spawned || candidate.Destroyed || candidate.Dead)
					{
						continue;
					}
					if (candidate.Faction != null)
					{
						continue; // never a tamed/factioned animal, wild scuttlers only
					}

					float distSq = (candidate.Position - parent.Position).LengthHorizontalSquared;
					if (distSq <= nearestDistSq)
					{
						nearest = candidate;
						nearestDistSq = distSq;
					}
				}
			}

			if (nearest == null)
			{
				return;
			}

			Vector3 killLoc = nearest.DrawPos;
			nearest.Kill(null);
			MoteMaker.ThrowText(killLoc, map, parent.LabelCap + " feeds", 3f);
		}
	}
}
