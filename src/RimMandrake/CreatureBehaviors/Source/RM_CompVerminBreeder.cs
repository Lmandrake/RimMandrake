using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. A lord-free, population-capped breeder: spawns an
	/// adjacent copy of the parent pawn on an interval, so long as
	/// RM_MapComponent_VerminPopulation says the race's group hasn't hit its
	/// hard cap on this map. Population caps are enforced here; the resulting
	/// "meanness" curve (aggression/gnaw damage/gnaw frequency) is read
	/// elsewhere (RM_JobGiver_GnawTargets, RM_JobDriver_Gnaw) from the same
	/// MapComponent, so the two halves of "nuisance unless there are many"
	/// stay in sync without this comp needing to know about them.
	///
	/// NOT vanilla CompSpawnerPawn: RimSage-verified
	/// (CompSpawnerPawn.TrySpawnPawn) that comp always creates or joins a Lord
	/// via Activator.CreateInstance(lordJobType, SpawnedPawnParams) — a Lord
	/// would own the spawned vermin's AI and fight this mod's own
	/// think-tree-driven behavior. This comp borrows CompSpawnerPawn's
	/// interval/radius fields verbatim and drops the lord entirely; spawned
	/// pawns are ordinary wild animals of the same kind, thinking for
	/// themselves from tick one.
	/// </summary>
	public class RM_CompVerminBreeder : ThingComp
	{
		private int nextSpawnTick = -1;

		private RM_CompProperties_VerminBreeder Props => (RM_CompProperties_VerminBreeder)props;

		private Pawn Parent => (Pawn)parent;

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
			if (!parent.Spawned || Parent.Dead)
			{
				return;
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
			nextSpawnTick = Find.TickManager.TicksGame + (int)(Props.pawnSpawnIntervalDays.RandomInRange * 60000f);
		}

		private void TrySpawn()
		{
			Map map = parent.Map;
			RM_MapComponent_VerminPopulation population = map.GetComponent<RM_MapComponent_VerminPopulation>();
			if (population != null && population.AtHardCap(Parent))
			{
				return;
			}
			if (!CellFinder.TryFindRandomCellNear(parent.Position, map, Props.pawnSpawnRadius,
				(IntVec3 c) => c.Standable(map) && map.reachability.CanReach(parent.Position, c, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)),
				out IntVec3 spawnCell))
			{
				return;
			}
			PawnGenerationRequest request = new PawnGenerationRequest(Parent.kindDef, Parent.Faction, fixedBiologicalAge: 0.4f, fixedChronologicalAge: 0.4f);
			Pawn child = PawnGenerator.GeneratePawn(request);
			GenSpawn.Spawn(child, spawnCell, map);
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref nextSpawnTick, "nextSpawnTick", -1);
		}
	}
}
