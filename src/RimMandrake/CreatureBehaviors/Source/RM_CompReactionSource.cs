using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// REACTION_MECHANISM_GENERALISE_1 step 1. The generalised trigger: same
	/// shape as RM_CompPlantAlarm (damage-or-public-trigger, a cooldown, a
	/// content-blind comp that names no species) but building a first-class
	/// RM_ReactionEvent with a SHARED budget and handing it to a pluggable
	/// propagation rule and then a pluggable response rule, instead of
	/// hardcoding "wake nearby responders to Manhunter" the way the shipped
	/// comp does.
	///
	/// ⛔ This does NOT replace RM_CompPlantAlarm and nothing here migrates the
	/// Rot's guardian groves onto this path — that migration is
	/// REACTION_MECHANISM_GENERALISE_1's own step 4, explicitly out of this
	/// pass's scope, and the item warns doing it early risks a live-content
	/// regression. RM_CompPlantAlarm keeps shipping unchanged.
	///
	/// First consumer: RM_SkerrelGall (GREENTIDE_WASP_SWARM_1), with
	/// propagation none and response RM_ReactionResponseRule_SpawnPawns.
	/// </summary>
	public class RM_CompReactionSource : ThingComp
	{
		private int lastTriggerTick = -999999;

		public RM_CompProperties_ReactionSource Props => (RM_CompProperties_ReactionSource)props;

		public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
		{
			base.PostPostApplyDamage(dinfo, totalDamageDealt);
			TriggerReaction(dinfo.Instigator as Pawn);
		}

		/// <summary>
		/// Public so a harvest hook (RUT_Plant_FalseFruit's own
		/// PlantCollected-style override, or a future gall equivalent) can ring
		/// this without a damage event, same as RM_CompPlantAlarm.TriggerAlarm.
		/// </summary>
		public void TriggerReaction(Pawn instigator)
		{
			if (!RM_CreatureBehaviorsSettings.reactionSourceSpawnEnabled)
			{
				return; // mod option: reaction-source spawning disabled
			}

			if (!parent.Spawned)
			{
				return;
			}

			Map map = parent.Map;
			if (map == null)
			{
				return;
			}

			int now = Find.TickManager.TicksGame;
			if (now - lastTriggerTick < Props.cooldownTicks)
			{
				return;
			}
			lastTriggerTick = now;

			float mult = Mathf.Max(0f, RM_CreatureBehaviorsSettings.reactionSourceBudgetMultiplier);
			int budget = Mathf.RoundToInt(Props.eventBudget * mult);
			if (budget <= 0)
			{
				return; // the player has turned this all the way down
			}

			RM_ReactionEvent evt = new RM_ReactionEvent(
				parent, map, parent.Position, Props.tag, instigator, budget);

			// Mark the origin itself activated before propagating: a
			// same-kind-within-radius rule (REACTION_MECHANISM_GENERALISE_1
			// step 2) recurses outward from each neighbour it wakes, and a
			// dense enough cluster can find its way back to the origin from
			// the far side. Without this the origin could be handed a
			// second Respond() call from its own propagation, silently
			// double-spending the event's shared budget on itself.
			evt.TryMarkActivated(parent);

			(Props.propagation ?? RM_ReactionPropagationRule_None.Instance).Propagate(evt, parent);

			Props.response?.Respond(evt, parent);
		}

		/// <summary>
		/// REACTION_MECHANISM_GENERALISE_1 step 2. Called by a propagation
		/// rule (never by a trigger directly) to wake THIS source as part of
		/// an event some other source already started — using the SAME
		/// shared event, never a fresh one with its own full budget. That is
		/// the difference between this and TriggerReaction: TriggerReaction
		/// mints a brand-new event with a brand-new budget (right for an
		/// independent disturbance), while this spends only what the caller
		/// already drew from the event it was handed (right for "my
		/// neighbour just woke and so do I").
		///
		/// Still respects this source's own cooldown and the mod's on/off
		/// switch — a source mid-cooldown from its own recent trigger does
		/// not re-fire just because a neighbour propagated into it — and
		/// still cascades its own propagation/response in turn, which is
		/// what lets a same-kind-within-radius rule actually spread the
		/// swarm outward hop by hop rather than reaching only the first
		/// source's own radius.
		/// </summary>
		/// <returns>true if this source actually activated (false: already handled this event, on cooldown, spawning disabled, or unspawned).</returns>
		public bool TryActivateFromPropagation(RM_ReactionEvent evt)
		{
			if (!RM_CreatureBehaviorsSettings.reactionSourceSpawnEnabled)
			{
				return false;
			}

			if (!parent.Spawned || parent.Map != evt.Map)
			{
				return false;
			}

			if (!evt.TryMarkActivated(parent))
			{
				return false; // this event already reached this source by another path
			}

			int now = Find.TickManager.TicksGame;
			if (now - lastTriggerTick < Props.cooldownTicks)
			{
				return false;
			}
			lastTriggerTick = now;

			(Props.propagation ?? RM_ReactionPropagationRule_None.Instance).Propagate(evt, parent);

			Props.response?.Respond(evt, parent);

			return true;
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref lastTriggerTick, "rmReactionSourceLastTriggerTick", -999999);
		}
	}
}
