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

		private int burstTick = -1;

		private bool burstDone;

		private RM_CompProperties_VerminNest Props => (RM_CompProperties_VerminNest)props;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (nextSpawnTick < 0)
			{
				CalculateNextSpawnTick();
			}
			if (RM_VerminKernel.BurstShouldSchedule(respawningAfterLoad, burstDone, burstTick, Props.initialBurst.max))
			{
				burstTick = Find.TickManager.TicksGame + Props.initialBurstDelayTicks.RandomInRange;
			}
		}

		public override void CompTick()
		{
			base.CompTick();
			// mod option wreckSpawningEnabled: wreck-anchored nests disabled entirely
			RM_VerminKernel.NestStep step = RM_VerminKernel.Step(parent.Spawned, ShipVerminSettings.wreckSpawningEnabled,
				burstDone, burstTick, nextSpawnTick, Find.TickManager.TicksGame);
			if (step.Burst)
			{
				burstDone = true;
				SpawnBurst(Props.initialBurst.RandomInRange, sendLetter: true);
			}
			if (!step.Attempt)
			{
				return;
			}
			AttemptSpawn(verbose: false);
			CalculateNextSpawnTick();
		}

		private void CalculateNextSpawnTick()
		{
			int intervalTicks = RM_VerminKernel.NestIntervalTicks(Props.nestSpawnIntervalDays.RandomInRange, ShipVerminSettings.wreckSpawnRateMultiplier);
			nextSpawnTick = Find.TickManager.TicksGame + intervalTicks;
		}

		/// <summary>
		/// WRECKAGE_VERMIN_SPAWN_1 re-block debug hook. The ordinary CompTick
		/// path called this and observed zero spawns after 263,701+ ticks with
		/// every precondition looking clear by code inspection, with no log
		/// line distinguishing which branch actually refused. This method is
		/// the single source of truth for every early-return in the spawn
		/// attempt, returns a human-readable reason string for each one, and
		/// is called both from CompTick (silently, verbose:false — production
		/// behaviour is unchanged) and from RM_ShipVerminDebugActions (verbose:true,
		/// logged) so the failing branch can be read directly instead of
		/// inferred from silence.
		/// </summary>
		public string AttemptSpawn(bool verbose)
		{
			Map map = parent.Map;
			if (map == null)
			{
				return Report(verbose, "no Map (parent not on a map)");
			}

			RM_MapComponent_VerminPopulation population = map.GetComponent<RM_MapComponent_VerminPopulation>();
			int currentPop = population?.GetPopulation(Props.populationGroupTag) ?? 0;
			if (RM_VerminKernel.SpawnRefusal(true, population != null, currentPop, Props.populationHardCap, true, true, true) == RM_VerminKernel.Refusal.PopulationCap)
			{
				// at the shared "nuisance unless there are many" hard cap — same gate RM_CompVerminBreeder respects
				return Report(verbose, $"population cap reached ({currentPop}/{Props.populationHardCap}, tag '{Props.populationGroupTag}')");
			}

			PawnKindDef kind = ShipVerminSettings.PickNestSpecies(Props.speciesWeights);
			if (kind == null)
			{
				// nothing enabled, or nothing enabled is actually installed
				return Report(verbose, "PickEnabledNestSpecies() returned null (nothing enabled+installed)");
			}

			bool foundCell = CellFinder.TryFindRandomCellNear(parent.Position, map, Props.nestSpawnRadius,
				(IntVec3 c) => c.Standable(map) && map.reachability.CanReach(parent.Position, c, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)),
				out IntVec3 spawnCell);
			if (!foundCell)
			{
				return Report(verbose, $"TryFindRandomCellNear found no cell within radius {Props.nestSpawnRadius} of {parent.Position} " +
					$"passing (Standable && CanReach) — species would have been {kind.defName}");
			}

			PawnGenerationRequest request = new PawnGenerationRequest(kind, null, fixedBiologicalAge: 0.6f, fixedChronologicalAge: 0.6f);
			Pawn pawn = PawnGenerator.GeneratePawn(request);
			if (pawn == null)
			{
				return Report(verbose, $"PawnGenerator.GeneratePawn returned null for {kind.defName}");
			}
			GenSpawn.Spawn(pawn, spawnCell, map);
			return Report(verbose, $"SPAWNED {kind.defName} ({pawn.ThingID}) at {spawnCell}, nest at {parent.Position}", success: true);
		}

		/// <summary>FALL_LINE_ARRIVAL_MECHANISM_1: spawn up to <paramref name="count"/> nest species at once
		/// (each through AttemptSpawn, so the population cap and the settings roster still hold), then
		/// send the props' burst letter if anything came out. Returns how many spawned.</summary>
		public int SpawnBurst(int count, bool sendLetter)
		{
			int spawned = 0;
			for (int i = 0; i < count; i++)
			{
				if (AttemptSpawn(verbose: false).StartsWith("SPAWNED"))
				{
					spawned++;
				}
			}
			if (spawned > 0 && sendLetter && !Props.burstLetterLabel.NullOrEmpty() && parent.Spawned)
			{
				Find.LetterStack.ReceiveLetter(Props.burstLetterLabel, Props.burstLetterText ?? "",
					LetterDefOf.NeutralEvent, new LookTargets(parent));
			}
			return spawned;
		}

		private string Report(bool verbose, string reason, bool success = false)
		{
			if (verbose)
			{
				if (success)
				{
					Log.Message("[RM_CompVerminNest] " + reason);
				}
				else
				{
					Log.Message("[RM_CompVerminNest] spawn attempt refused: " + reason);
				}
			}
			return reason;
		}

		/// <summary>Debug-hook accessor — ticks remaining until the next scheduled attempt.</summary>
		public int DebugTicksUntilNextSpawn()
		{
			return nextSpawnTick - Find.TickManager.TicksGame;
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref nextSpawnTick, "nextSpawnTick", -1);
			Scribe_Values.Look(ref burstTick, "burstTick", -1);
			Scribe_Values.Look(ref burstDone, "burstDone", false);
		}
	}
}
