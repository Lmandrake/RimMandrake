using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Webwork
{
	public class RM_CompProperties_EggClutchRelay : CompProperties
	{
		// S6 ruling 4 (owner, question card, 2026-09-24, sitting §4a): "a
		// living nest re-lays every 20-30 days" — the sitting's own range,
		// carried verbatim; the days themselves are the owner's ruled
		// number, not guessed.
		public FloatRange relayIntervalDays = new FloatRange(20f, 30f);

		public IntRange clutchesPerRelay = new IntRange(1, 2);

		public int clutchSearchRadius = 4;

		public string eggClutchDefName = "RM_Webwork_EggClutch";

		public string motherRaceDefName = "RM_Ollathrix";

		public RM_CompProperties_EggClutchRelay()
		{
			compClass = typeof(RM_CompEggClutchRelay);
		}
	}

	/// <summary>
	/// WEBWORK_NEST_EGG_ECONOMY_1, S6 ruling 4. Attached to
	/// RM_Webwork_NestWall (the mother's guardian structure), not to the
	/// clutch itself: sitting §4a's "RM_Webwork_EggClutch respawns at the
	/// nest every 20-30 days while any RM_Ollathrix is alive on the map"
	/// describes the CLUTCH regrowing after it is mined out, which this
	/// realises as "the wall re-seeds a fresh clutch nearby once the local
	/// supply is exhausted" — the wall is the one part of the nest that
	/// never gets consumed by harvesting, so it is the natural home for the
	/// timer. Same nextTick/CalculateNextTick/Scribe shape as
	/// RM_CompVerminBreeder (CreatureBehaviors) — this comp does not touch
	/// that file, it only mirrors its established idiom.
	///
	/// "A map with no mother is a map with a dying nest" (§4a): MotherAlive
	/// reads map.mapPawns directly rather than a population-cap
	/// MapComponent — there is no population cap here, eggs are not pawns,
	/// and §4a's own closing sentence ("the eggs are hers... self-predation
	/// is why the clutch count never becomes a population count") rules that
	/// out on purpose.
	///
	/// Deliberately does NOT wire RM_CompSenseWebNode
	/// (mandrake.rm.creaturebehaviors, already a hard modDependency of this
	/// mod for RM_Webwork_SunScald) even though it would be a one-line
	/// addition: the "what rings" convergence AI
	/// (RM_JobGiver_SenseWebConverge) that would consume that registration is
	/// unbuilt, so wiring the registration alone would be dead bookkeeping.
	/// Owed to WEBWORK_MECHANICS_1/WEBWORK_WEB_STRUCTURES_1, the same split
	/// RM_Ollathrix.xml's own header already draws.
	/// </summary>
	public class RM_CompEggClutchRelay : ThingComp
	{
		private int nextRelayTick = -1;

		private RM_CompProperties_EggClutchRelay Props => (RM_CompProperties_EggClutchRelay)props;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			if (nextRelayTick < 0)
			{
				CalculateNextRelayTick();
			}
		}

		// The nest wall is tickerType Normal (its dormancy/spawner comps need it), and a Normal
		// building never calls CompTickRare, so this runs from CompTick on the rare cadence
		// (TICKER_NEVER_FIRES_FIX_1).
		public override void CompTick()
		{
			base.CompTick();
			if (!parent.Spawned || !parent.IsHashIntervalTick(GenTicks.TickRareInterval))
			{
				return;
			}
			int now = Find.TickManager.TicksGame;
			if (now < nextRelayTick)
			{
				return;
			}
			ThingDef clutchDef = DefDatabase<ThingDef>.GetNamedSilentFail(Props.eggClutchDefName);
			RelayPlan plan = RM_EggRelayKernel.Plan(now, nextRelayTick, MotherAlive(parent.Map), clutchDef != null,
				clutchDef != null && ExistingClutchNearby(parent.Map, clutchDef));
			if (plan == RelayPlan.DyingNest)
			{
				// A dying nest (§4a): no relay fires, but we keep checking
				// on the ordinary interval rather than latching dead
				// forever — a fresh Ollathrix wandering onto the map (or
				// one this same wall respawns) revives the clutch on its
				// own next check.
				return;
			}
			if (plan == RelayPlan.Place)
			{
				TryRelay();
			}
			CalculateNextRelayTick();
		}

		private bool MotherAlive(Map map)
		{
			if (map == null)
			{
				return false;
			}
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p != null && !p.Dead && p.def != null && p.def.defName == Props.motherRaceDefName)
				{
					return true;
				}
			}
			return false;
		}

		private void TryRelay()
		{
			ThingDef clutchDef = DefDatabase<ThingDef>.GetNamedSilentFail(Props.eggClutchDefName);
			if (clutchDef == null || parent.Map == null)
			{
				return;
			}
			Map map = parent.Map;

			int toPlace = Props.clutchesPerRelay.RandomInRange;
			for (int i = 0; i < toPlace; i++)
			{
				if (!CellFinder.TryFindRandomCellNear(parent.Position, map, Props.clutchSearchRadius,
					(IntVec3 c) => c.Standable(map) && c.GetFirstBuilding(map) == null,
					out IntVec3 cell))
				{
					continue;
				}
				GenSpawn.Spawn(ThingMaker.MakeThing(clutchDef), cell, map);
			}
		}

		private bool ExistingClutchNearby(Map map, ThingDef clutchDef)
		{
			List<Thing> things = map.listerThings.ThingsOfDef(clutchDef);
			for (int i = 0; i < things.Count; i++)
			{
				Thing t = things[i];
				if (t != null && t.Spawned && RM_EggRelayKernel.ClutchNearby(t.Position.x - parent.Position.x, t.Position.z - parent.Position.z, Props.clutchSearchRadius))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Proof hooks (RM_WebworkProof): ticks until the next relay check, a re-roll, and a check forced now.</summary>
		public int TicksToNextRelay => nextRelayTick - Find.TickManager.TicksGame;

		public void ProofReroll() => CalculateNextRelayTick();

		public void ProofCheckNow()
		{
			nextRelayTick = Find.TickManager.TicksGame;
			CompTickRare();
		}

		private void CalculateNextRelayTick()
		{
			int intervalTicks = RM_EggRelayKernel.IntervalTicks(Props.relayIntervalDays.RandomInRange, RM_WebworkSettings.eggRelayIntervalMultiplier);
			nextRelayTick = Find.TickManager.TicksGame + intervalTicks;
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref nextRelayTick, "nextRelayTick", -1);
		}
	}
}
