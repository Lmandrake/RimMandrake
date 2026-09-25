using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// REACTION_MECHANISM_GENERALISE_1 step 1 / GREENTIDE_WASP_SWARM_1. The
	/// spawn response's "lose interest and go home" half — the same shape as
	/// this assembly's own RM_MentalState_ParentalEnrage (SHRUBLAND_GIANT_ENRAGE_1),
	/// generalised from "anchored on a guarded pawn" to "anchored on a cell",
	/// which is what a gall (not a pawn) needs.
	///
	/// Reusing that class's own measured engine fact rather than re-deriving
	/// it: MentalStateNonCritical dispatches manhunting through
	/// ThinkNode_ConditionalMentalStateClass, whose Satisfied() is an
	/// IsInstanceOfType check, not a def-identity check — so a MentalState_Manhunter
	/// SUBCLASS inherits JobGiver_Manhunter's whole chase-and-melee behaviour
	/// with no think-tree patch anywhere (MEASURED 2026-09-20 against the
	/// decompiled 1.6 engine, Verse/AI/ThinkNode_ConditionalMentalStateClass.cs).
	///
	/// Scope, exactly like its sibling: ForceHostileTo(Thing) answers true for
	/// the ONE pawn that disturbed the source (evt.Instigator, carried onto the
	/// spawned wasp as causedByPawn), never a map-wide manhunter flip, and
	/// ForceHostileTo(Faction) never flips faction-level hostility.
	///
	/// The difference from ParentalEnrage: the anchor is a CELL (the gall's
	/// last known position), not a pawn that might wander off, because a gall
	/// is a small stationary Thing that may already be destroyed by the time
	/// the wasps it spawned are deciding whether to keep chasing. "Survivable
	/// by withdrawing" (GREENTIDE_WASP_SWARM_1's own requirement) is exactly
	/// what disengaging on distance-from-anchor gives for free, without
	/// needing the general reaction-suppression mechanism the item defers to
	/// a later step.
	/// </summary>
	public class RM_MentalState_ScopedAggression : MentalState_Manhunter
	{
		/// <summary>Where the disturbance that spawned this pawn happened. Set by the response rule at spawn time.</summary>
		public IntVec3 anchorCell;

		/// <summary>Once the target is this many cells from anchorCell, this pawn stops caring. Set by the response rule from its own config.</summary>
		public float disengageRadius = 20f;

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref anchorCell, "anchorCell");
			Scribe_Values.Look(ref disengageRadius, "disengageRadius", 20f);
		}

		/// <summary>Hostile to the one pawn that caused this, and nothing else — degrades to harmless if there is no target.</summary>
		public override bool ForceHostileTo(Thing t)
		{
			return t != null && causedByPawn != null && t == causedByPawn;
		}

		/// <summary>Never a faction-level flip.</summary>
		public override bool ForceHostileTo(Faction f)
		{
			return false;
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

		/// <summary>Same 30-tick cadence vanilla MentalState uses for its own recovery roll, so this costs nothing extra.</summary>
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

			if (target.Downed)
			{
				return true;
			}

			if (pawn.Map == null || target.Map != pawn.Map)
			{
				return true;
			}

			float radiusSq = disengageRadius * disengageRadius;
			return (target.Position - anchorCell).LengthHorizontalSquared > radiusSq;
		}
	}
}
