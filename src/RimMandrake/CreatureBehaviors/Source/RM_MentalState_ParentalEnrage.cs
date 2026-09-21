using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHRUBLAND_GIANT_ENRAGE_1. The scoped, time-boxed rage a giant drops into
	/// when something walks up to its young. See RM_ParentalEnrageExtension for
	/// the whole mechanism and why it is shaped this way.
	///
	/// This derives from vanilla MentalState_Manhunter for ONE measured reason:
	/// ThinkTreeDef MentalStateNonCritical dispatches manhunting through
	/// ThinkNode_ConditionalMentalStateClass, whose Satisfied() is
	/// `stateClass.IsInstanceOfType(mentalState)` — an instance check, not the
	/// def-identity check its sibling ThinkNode_ConditionalMentalState does. So
	/// a SUBCLASS is routed straight into JobGiver_Manhunter's chase-and-melee
	/// behaviour and NO think-tree patch is needed anywhere. (MEASURED against
	/// the decompiled 1.6 engine, 2026-09-20: Verse/AI/
	/// ThinkNode_ConditionalMentalStateClass.cs l.19.)
	///
	/// What it changes from its parent is the SCOPE, and only the scope:
	///
	///   * MentalState_Manhunter.ForceHostileTo(Thing) answers true for every
	///     humanlike and every humanlike faction on the map, which is a real
	///     manhunter. This answers true for exactly ONE pawn — the one that
	///     walked up to the calf. GenHostility.HostileTo consults
	///     ForceHostileTo before it ever reaches faction logic, so
	///     JobGiver_Manhunter's own AttackTargetFinder.BestAttackTarget pass
	///     (which filters on searcher.HostileTo(thing)) finds that pawn and
	///     nobody else. Nothing else on the map is touched.
	///
	///   * ForceHostileTo(Faction) answers false, so the rage NEVER flips
	///     faction-level hostility. The intruder still sees the giant as
	///     hostile and may fight back, because GenHostility.HostileTo's
	///     Thing-vs-Thing overload asks BOTH pawns' mental states — the
	///     symmetry is free and correct. Their colony does not go to war with
	///     the wildlife over it.
	///
	/// The time-box is vanilla's own MentalState.forceRecoverAfterTicks, set by
	/// RM_CompParentalEnrage from the extension. On top of that this recovers
	/// the moment the intruder is gone, dead, downed or has simply walked back
	/// out of range — back off and the giant goes back to grazing, which is the
	/// other half of "approach is attack".
	/// </summary>
	public class RM_MentalState_ParentalEnrage : MentalState_Manhunter
	{
		/// <summary>
		/// The young this rage is being fought over. Held for the inspect line
		/// and for the "is the calf still here" recovery check; the rage is
		/// aimed at causedByPawn, not at this.
		/// </summary>
		public Pawn guardedYoung;

		/// <summary>
		/// Once the intruder is this many cells away from the guarded young,
		/// the giant stops caring. Set by RM_CompParentalEnrage from the
		/// extension's triggerRadius; the fallback only matters for a state
		/// started by something other than that comp.
		/// </summary>
		public float disengageRadius = 12f;

		/// <summary>The one pawn this rage is aimed at.</summary>
		public Pawn Target => causedByPawn;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_References.Look(ref guardedYoung, "guardedYoung");
			Scribe_Values.Look(ref disengageRadius, "disengageRadius", 12f);
		}

		/// <summary>
		/// The whole point of this class. Hostile to the intruder alone — and
		/// to nothing at all if there is no intruder, so a mis-started state
		/// degrades to harmless rather than to a map-wide manhunter.
		/// </summary>
		public override bool ForceHostileTo(Thing t)
		{
			return t != null && causedByPawn != null && t == causedByPawn;
		}

		/// <summary>Never a faction-level flip. See the class header.</summary>
		public override bool ForceHostileTo(Faction f)
		{
			return false;
		}

		public override string InspectLine
		{
			get
			{
				if (guardedYoung != null)
				{
					return def.baseInspectLine + ": " + guardedYoung.LabelShort;
				}

				return def.baseInspectLine;
			}
		}

		public override void MentalStateTick(int delta)
		{
			if (ShouldDisengage(delta))
			{
				RecoverFromState();
				return; // base would tick a state the pawn no longer holds
			}

			base.MentalStateTick(delta);
		}

		/// <summary>
		/// Back off and it ends. Checked on the same 30-tick cadence vanilla
		/// MentalState uses for its own recovery roll, so this costs nothing
		/// extra.
		/// </summary>
		private bool ShouldDisengage(int delta)
		{
			if (!pawn.IsHashIntervalTick(30, delta))
			{
				return false;
			}

			Pawn target = causedByPawn;
			if (target == null || target.Dead || target.Destroyed || !target.Spawned)
			{
				return true;
			}

			// Downed is enough: the trespasser has stopped being an approach.
			if (target.Downed)
			{
				return true;
			}

			if (pawn.Map == null || target.Map != pawn.Map)
			{
				return true;
			}

			// The calf is what is being defended. Once it is gone (grown,
			// killed, hauled away) there is nothing left to rage about.
			if (guardedYoung != null
			    && (guardedYoung.Dead || guardedYoung.Destroyed || !guardedYoung.Spawned))
			{
				return true;
			}

			// Walked away from the young again — measured from the calf, not
			// from the giant, because the giant is the one doing the chasing.
			Thing anchor = (guardedYoung != null && guardedYoung.Spawned) ? (Thing)guardedYoung : pawn;
			float radiusSq = disengageRadius * disengageRadius;
			return (target.Position - anchor.Position).LengthHorizontalSquared > radiusSq;
		}
	}
}
