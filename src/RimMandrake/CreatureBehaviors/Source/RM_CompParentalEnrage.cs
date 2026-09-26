using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHRUBLAND_GIANT_ENRAGE_1. The trigger half of "giant with young": rides
	/// on EVERY pawn of the race, but only does work while the pawn it rides on
	/// is still a juvenile. An adult carrier is inert — it is the thing that
	/// gets ROUSED, never the thing that scans.
	///
	/// Cost shape, which is the thing the item asked to be surveyed before
	/// anything was written:
	///   * The frequent half is a bounded RADIAL scan (GenRadial.
	///     RadialDistinctThingsAround) of triggerRadius cells around the calf,
	///     at CompTickRare — 250 ticks, ~80 cells at the shipped radius of 5.
	///     Never a per-tick scan, never a full-map scan.
	///   * The wider half — finding the adult that answers — walks
	///     mapPawns.AllPawnsSpawned once, and ONLY after an intruder has
	///     actually been found, which is rare. Paying a map-wide walk on the
	///     rare branch is much cheaper than a radial sweep of
	///     guardianSearchRadius (30 cells ≈ 2800) on the common one.
	///
	/// See RM_ParentalEnrageExtension for the mechanism and the measured engine
	/// facts it rests on.
	/// </summary>
	public class RM_CompParentalEnrage : ThingComp
	{
		private int lastTriggerTick = -999999;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref lastTriggerTick, "rmLastParentalEnrageTick", -999999);
		}

		public override void CompTickRare()
		{
			base.CompTickRare();

			if (!RM_CreatureBehaviorsSettings.parentalEnrageEnabled)
			{
				return;
			}

			if (!(parent is Pawn young) || !young.Spawned || young.Dead || young.Map == null)
			{
				return;
			}

			RM_ParentalEnrageExtension ext = young.def.GetModExtension<RM_ParentalEnrageExtension>();
			if (ext == null || ext.enrageState == null || ext.triggerRadius <= 0f)
			{
				return;
			}

			int now = Find.TickManager.TicksGame;

			if (ext.GuardsThings)
			{
				// Item-guard mode: no young/adult split at all — every pawn
				// carrying the comp is its own guardian and its own scanner.
				// "young" above is just this comp's carrier in this mode.
				if (now - lastTriggerTick < ext.cooldownTicks)
				{
					return;
				}

				Thing guardedThing = FindGuardedThing(young, ext);
				if (guardedThing == null)
				{
					return; // nothing of this comp's watch list is nearby
				}

				Pawn thingIntruder = FindIntruderNear(guardedThing.Position, young.Map, young, ext);
				if (thingIntruder == null)
				{
					return;
				}

				TryEnrageForThing(young, guardedThing, thingIntruder, ext, now);
				return;
			}

			if (!IsYoung(young, ext))
			{
				return; // adults carry the comp and do nothing with it
			}

			if (now - lastTriggerTick < ext.cooldownTicks)
			{
				return;
			}

			Pawn intruder = FindIntruder(young, ext);
			if (intruder == null)
			{
				return;
			}

			Pawn guardian = FindGuardian(young, ext, intruder);
			if (guardian == null)
			{
				return; // a calf genuinely alone is simply undefended
			}

			TryEnrage(guardian, young, intruder, ext, now);
		}

		/// <summary>
		/// Item-guard mode: the nearest spawned Thing of one of
		/// ext.guardedThingDefNames within ext.guardianSearchRadius of this
		/// pawn, or null. Cheap in practice — a map carries at most a
		/// handful of fruit at once.
		/// </summary>
		private static Thing FindGuardedThing(Pawn guardian, RM_ParentalEnrageExtension ext)
		{
			Map map = guardian.Map;
			float radiusSq = ext.guardianSearchRadius * ext.guardianSearchRadius;

			Thing best = null;
			float bestDistSq = float.MaxValue;

			for (int d = 0; d < ext.guardedThingDefNames.Count; d++)
			{
				ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(ext.guardedThingDefNames[d]);
				if (def == null)
				{
					continue;
				}
				List<Thing> things = map.listerThings.ThingsOfDef(def);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					if (t == null || t.Destroyed || !t.Spawned)
					{
						continue;
					}
					float distSq = (t.Position - guardian.Position).LengthHorizontalSquared;
					if (distSq > radiusSq || distSq >= bestDistSq)
					{
						continue;
					}
					bestDistSq = distSq;
					best = t;
				}
			}

			return best;
		}

		/// <summary>
		/// Same exemption rules as FindIntruder, centered on an arbitrary
		/// cell (the guarded thing's position) instead of a young pawn's own
		/// position.
		/// </summary>
		private static Pawn FindIntruderNear(IntVec3 center, Map map, Pawn self, RM_ParentalEnrageExtension ext)
		{
			float radius = System.Math.Min(ext.triggerRadius, GenRadial.MaxRadialPatternRadius - 1f);

			Pawn best = null;
			float bestDistSq = float.MaxValue;

			foreach (Thing thing in GenRadial.RadialDistinctThingsAround(center, map, radius, useCenter: true))
			{
				if (!(thing is Pawn candidate) || candidate == self)
				{
					continue;
				}

				if (candidate.Dead || candidate.Downed || !candidate.Spawned)
				{
					continue;
				}

				if (ext.exemptSameRace && candidate.def == self.def)
				{
					continue;
				}

				if (ext.exemptSameFaction && candidate.Faction != null && candidate.Faction == self.Faction)
				{
					continue;
				}

				if (ext.onlyToolUserOrHumanlikeTriggers
				    && (candidate.RaceProps == null || (int)candidate.RaceProps.intelligence < (int)Intelligence.ToolUser))
				{
					continue;
				}

				if (candidate.IsPsychologicallyInvisible())
				{
					continue;
				}

				if (ext.requireLineOfSight
				    && !GenSight.LineOfSight(center, candidate.Position, map, skipFirstCell: true))
				{
					continue;
				}

				float distSq = (candidate.Position - center).LengthHorizontalSquared;
				if (distSq < bestDistSq)
				{
					bestDistSq = distSq;
					best = candidate;
				}
			}

			return best;
		}

		private void TryEnrageForThing(Pawn guardian, Thing guardedThing, Pawn intruder,
			RM_ParentalEnrageExtension ext, int now)
		{
			if (guardian.mindState == null || guardian.mindState.mentalStateHandler == null)
			{
				return;
			}

			string reason = intruder.LabelShortCap + " came too close to " + guardedThing.LabelShort + ".";

			bool started = guardian.mindState.mentalStateHandler.TryStartMentalState(
				ext.enrageState,
				reason,
				forced: true,
				forceWake: true,
				causedByMood: false,
				otherPawn: intruder);

			if (!started)
			{
				return;
			}

			if (guardian.MentalState is RM_MentalState_ParentalEnrage state)
			{
				state.guardedThing = guardedThing;
				state.disengageRadius = ext.triggerRadius * 2f;
				state.forceRecoverAfterTicks = ext.enrageDurationTicks;
			}

			lastTriggerTick = now;
		}

		/// <summary>
		/// "Young" is every life stage the race declares except its last, so
		/// no life stage has to be named here and any ordinary
		/// baby/juvenile/adult ladder works unchanged. youngLifeStageMaxIndex
		/// overrides it for a race with a stranger ladder.
		/// </summary>
		private static bool IsYoung(Pawn pawn, RM_ParentalEnrageExtension ext)
		{
			if (pawn.RaceProps == null || pawn.RaceProps.lifeStageAges == null || pawn.ageTracker == null)
			{
				return false;
			}

			int lastIndex = pawn.RaceProps.lifeStageAges.Count - 1;
			if (lastIndex < 1)
			{
				return false; // a race with one life stage has no "young"
			}

			int maxYoungIndex = ext.youngLifeStageMaxIndex >= 0
				? ext.youngLifeStageMaxIndex
				: lastIndex - 1;

			return pawn.ageTracker.CurLifeStageIndex <= maxYoungIndex;
		}

		private static bool IsAdult(Pawn pawn, RM_ParentalEnrageExtension ext)
		{
			return !IsYoung(pawn, ext);
		}

		/// <summary>
		/// The cheap, bounded half: the nearest pawn that counts as having
		/// approached this calf, or null.
		/// </summary>
		private static Pawn FindIntruder(Pawn young, RM_ParentalEnrageExtension ext)
		{
			Map map = young.Map;
			float radius = System.Math.Min(ext.triggerRadius, GenRadial.MaxRadialPatternRadius - 1f);

			Pawn best = null;
			float bestDistSq = float.MaxValue;

			foreach (Thing thing in GenRadial.RadialDistinctThingsAround(young.Position, map, radius, useCenter: true))
			{
				if (!(thing is Pawn candidate) || candidate == young)
				{
					continue;
				}

				if (candidate.Dead || candidate.Downed || !candidate.Spawned)
				{
					continue;
				}

				if (ext.exemptSameRace && candidate.def == young.def)
				{
					continue; // the herd walks among its own calves
				}

				if (ext.exemptSameFaction && candidate.Faction != null && candidate.Faction == young.Faction)
				{
					continue; // a tamed herd's own handlers
				}

				if (ext.onlyToolUserOrHumanlikeTriggers
				    && (candidate.RaceProps == null || (int)candidate.RaceProps.intelligence < (int)Intelligence.ToolUser))
				{
					continue;
				}

				if (candidate.IsPsychologicallyInvisible())
				{
					continue;
				}

				if (ext.requireLineOfSight
				    && !GenSight.LineOfSight(young.Position, candidate.Position, map, skipFirstCell: true))
				{
					continue;
				}

				float distSq = (candidate.Position - young.Position).LengthHorizontalSquared;
				if (distSq < bestDistSq)
				{
					bestDistSq = distSq;
					best = candidate;
				}
			}

			return best;
		}

		/// <summary>
		/// The rare, wider half: the adult of the same race that answers. A
		/// true PawnRelationDefOf.Parent relation wins over mere proximity when
		/// one exists — a calf born on this map really does know its mother
		/// (Hediff_Pregnant.DoBirthSpawn adds that relation for any flesh race)
		/// — but wildlife spawned by map gen has no relation at all, so nearest
		/// adult is the fallback that always works.
		/// </summary>
		private static Pawn FindGuardian(Pawn young, RM_ParentalEnrageExtension ext, Pawn intruder)
		{
			float radiusSq = ext.guardianSearchRadius * ext.guardianSearchRadius;

			Pawn best = null;
			float bestScore = float.MaxValue;

			IReadOnlyList<Pawn> pawns = young.Map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn candidate = pawns[i];

				if (candidate == young || candidate == intruder || candidate.def != young.def)
				{
					continue;
				}

				if (candidate.Dead || candidate.Downed || !candidate.Spawned || candidate.InMentalState)
				{
					continue;
				}

				if (!IsAdult(candidate, ext))
				{
					continue; // another calf cannot answer for this one
				}

				float distSq = (candidate.Position - young.Position).LengthHorizontalSquared;
				if (distSq > radiusSq)
				{
					continue;
				}

				// Distance is the score; a real parent gets to cheat it.
				float score = distSq;
				if (ext.preferTrueParent
				    && young.relations != null
				    && young.relations.DirectRelationExists(PawnRelationDefOf.Parent, candidate))
				{
					score = -1f;
				}

				if (score < bestScore)
				{
					bestScore = score;
					best = candidate;
				}
			}

			return best;
		}

		private void TryEnrage(Pawn guardian, Pawn young, Pawn intruder,
			RM_ParentalEnrageExtension ext, int now)
		{
			if (guardian.mindState == null || guardian.mindState.mentalStateHandler == null)
			{
				return;
			}

			string reason = intruder.LabelShortCap + " came too close to " + young.LabelShort + ".";

			// forced + forceWake: the ruling is "no warning is given", and a
			// dozing giant still answers. forced also bypasses
			// MentalStateWorker.StateCanOccur, which has nothing useful to say
			// about a wild animal.
			bool started = guardian.mindState.mentalStateHandler.TryStartMentalState(
				ext.enrageState,
				reason,
				forced: true,
				forceWake: true,
				causedByMood: false,
				otherPawn: intruder);

			if (!started)
			{
				return;
			}

			if (guardian.MentalState is RM_MentalState_ParentalEnrage state)
			{
				state.guardedYoung = young;
				state.disengageRadius = ext.triggerRadius * 2f;
				// Vanilla's own time-box: MentalState.MentalStateTick already
				// ends the state once age >= forceRecoverAfterTicks, so this
				// needs no timer of its own.
				state.forceRecoverAfterTicks = ext.enrageDurationTicks;
			}

			// Cooldown is recorded on the CALF (this comp's own carrier), so
			// one intruder standing in a nursery cannot rouse the whole herd
			// every rare tick.
			lastTriggerTick = now;
		}
	}
}
