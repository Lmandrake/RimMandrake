using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.ShipVermin
{
	/// <summary>
	/// WRECKAGE_VERMIN_SPAWN_1. The generic "vermin nest under the wreckage"
	/// engine — owner ruling, 2026-09-12, verbatim: "Yes vermin should be able
	/// to spawn from wreckage," confirming fall_line.md's frozen design line
	/// ("Ship vermin nests under the larger hulls, living on what falls") as a
	/// build requirement.
	///
	/// Deliberately NOT RM_CompVerminBreeder: that comp lives on an existing
	/// LIVE PAWN and spawns a copy of itself, so it needs no species list. This
	/// comp lives on wreckage — a building, never a pawn — so there is no
	/// "itself" to copy; the species spawned is picked from
	/// ShipVerminSettings' player-configured roster instead. Both comps read
	/// the same RM_MapComponent_VerminPopulation group-tag pool
	/// (RM_MapComponent_VerminPopulation.GetPopulation(string)), so a nest and
	/// a breeding population press against ONE shared pressure ceiling rather
	/// than two independent ones.
	///
	/// Which ThingDefs actually carry this comp is deliberately NOT decided
	/// here: this mod (mandrake.rm.shipvermin, RimMandrake tier) is the engine
	/// only. A campaign's own patch layer (e.g. RimUtinni) decides which of
	/// its own wreck/hulk/ruin defs this attaches to — see the item's own
	/// "mechanism is generic; wreck-def wiring is campaign-specific" split.
	/// </summary>
	public class RM_CompVerminNest : ThingComp
	{
		private int nextSpawnTick = -1;

		private RM_CompProperties_VerminNest Props => (RM_CompProperties_VerminNest)props;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (nextSpawnTick < 0)
			{
				CalculateNextSpawnTick();
			}
		}

		public override void CompTick()
		{
			base.CompTick();
			if (!parent.Spawned)
			{
				return;
			}
			if (!ShipVerminSettings.wreckSpawningEnabled)
			{
				return; // mod option: wreck-anchored nests disabled entirely
			}
			if (Find.TickManager.TicksGame < nextSpawnTick)
			{
				return;
			}
			TrySpawn();
			CalculateNextSpawnTick();
		}

		private void CalculateNextSpawnTick()
		{
			float mult = Mathf.Max(0.01f, ShipVerminSettings.wreckSpawnRateMultiplier);
			int intervalTicks = Mathf.Max(1, Mathf.RoundToInt(Props.nestSpawnIntervalDays.RandomInRange * 60000f / mult));
			nextSpawnTick = Find.TickManager.TicksGame + intervalTicks;
		}

		private void TrySpawn()
		{
			Map map = parent.Map;
			if (map == null)
			{
				return;
			}

			RM_MapComponent_VerminPopulation population = map.GetComponent<RM_MapComponent_VerminPopulation>();
			if (population != null && population.GetPopulation(Props.populationGroupTag) >= Props.populationHardCap)
			{
				return; // at the shared "nuisance unless there are many" hard cap — same gate RM_CompVerminBreeder respects
			}

			PawnKindDef kind = ShipVerminSettings.PickEnabledNestSpecies();
			if (kind == null)
			{
				return; // nothing enabled, or nothing enabled is actually installed
			}

			if (!CellFinder.TryFindRandomCellNear(parent.Position, map, Props.nestSpawnRadius,
				(IntVec3 c) => c.Standable(map) && map.reachability.CanReach(parent.Position, c, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)),
				out IntVec3 spawnCell))
			{
				return;
			}

			PawnGenerationRequest request = new PawnGenerationRequest(kind, null, fixedBiologicalAge: 0.6f, fixedChronologicalAge: 0.6f);
			Pawn pawn = PawnGenerator.GeneratePawn(request);
			GenSpawn.Spawn(pawn, spawnCell, map);
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref nextSpawnTick, "nextSpawnTick", -1);
		}
	}
}
