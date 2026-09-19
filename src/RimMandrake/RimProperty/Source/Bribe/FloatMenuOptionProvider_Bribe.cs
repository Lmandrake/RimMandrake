using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.Property;

namespace RimMandrake.Bribe
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, social-fabric pass — fifth verb built for
    /// this item overall, and the SECOND social-fabric sub-mechanic (after
    /// Hiring the Placeless). Spec item 9: "social fabric (rumors as intel,
    /// sabacc, hiring the placeless, bribes and bought rounds as propagation
    /// dampers)." This pass builds the bribe/bought-round half.
    ///
    /// Per this item's 2026-09-18 note (social-fabric pass): rumors-as-intel
    /// and bribes both need a genuinely NEW read/write surface on
    /// FactionRecord that didn't exist before that pass — unlike hiring,
    /// which reused the fabric completely as-is. Bribes needed only the
    /// WRITE half (FactionRecord.DampenSuspicion, added this pass) and is
    /// explicitly NOT blocked by the module-boundary tension flagged
    /// against rumors-as-intel ("Verbs ... must not know perception
    /// outcomes"): this verb never READS GetSuspicion/
    /// HasAnyPropagatedKnowledge to decide whether to offer itself, or to
    /// report back whether the bribe "worked" — it always fires the same
    /// silent write regardless of what the ledger actually holds, so no
    /// perception outcome is ever exposed to the verb code or the player.
    /// Spec item 6's "No meter, no indicator, ever" holds.
    ///
    /// Same right-click float-menu-order shape as every other verb this item
    /// built — needs a selected acting pawn AND a clicked target Pawn; no
    /// JobDriver, the whole transaction runs instantly from this option's
    /// own delegate. FloatMenuMakerMap.Init() auto-registers every
    /// non-abstract FloatMenuOptionProvider via reflection, so no Harmony
    /// hook or registration call is needed here either.
    ///
    /// Unlike every prior verb in this item, this one does NOT go through
    /// PropertyEngine.Fire/TakingEvent at all — there is no Thing being
    /// taken, bought or claimed here, so no existing TakingAct fits. It
    /// calls the new PropertyEngine.DampenSuspicion direct-write entry point
    /// instead, the same "direct provenance write, no spine, no perception
    /// roll" shape RecordGift/RecordInheritance already use for their own
    /// non-adversarial transfers.
    /// </summary>
    public class FloatMenuOptionProvider_Bribe : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!PropertySettings.bribeEnabled) return null;

            Pawn actor = context.FirstSelectedPawn;

            if (!(clickedThing is Pawn targetPawn)) return null;
            if (targetPawn == actor) return null;
            if (!targetPawn.Spawned) return null;

            // A bribe/bought-round is a payment to a FACTION's own people to
            // cool off what they've told their own faction — a faction-less
            // pawn (Hiring the Placeless's own territory) or a member of the
            // actor's own faction has no separate faction record to dampen
            // against here.
            if (targetPawn.Faction == null) return null;
            if (targetPawn.Faction == actor.Faction) return null;

            // Downed is the claim-fee gizmo's own droid case; a prisoner
            // already belongs to the player, not their home faction's social
            // fabric — same reasoning HirePlaceless's own gates apply to
            // their respective target kinds.
            if (targetPawn.Downed) return null;
            if (targetPawn.IsPrisoner) return null;

            // Mid-fight isn't a round of drinks — same HostileTo gate every
            // other social/crime verb in this item already applies.
            if (targetPawn.HostileTo(actor)) return null;

            // A bought round is a conversation, not a transaction a
            // mechanoid can have — unlike Hiring the Placeless, which
            // deliberately includes an active droid as a legitimate hire
            // target, this verb is humanlike-only.
            if (targetPawn.RaceProps == null || !targetPawn.RaceProps.Humanlike) return null;

            int tick = Find.TickManager.TicksGame;
            int fee = BribeUtility.ComputeBribeFeeSilver();

            if (!actor.CanReach(targetPawn, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot buy " + targetPawn.LabelShort + " a round: " + "NoPath".Translate().CapitalizeFirst(), null);
            }

            int carried = BribeUtility.CountSilverInInventory(actor);
            if (carried < fee)
            {
                return new FloatMenuOption(
                    "Cannot buy " + targetPawn.LabelShort
                    + " a round: not enough silver (need " + fee + ", have " + carried + ")", null);
            }

            Faction targetFaction = targetPawn.Faction;
            float dampenFraction = PropertySettings.bribeDampenFraction;

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Buy " + targetPawn.LabelShort + " a round (" + fee + " silver)",
                delegate
                {
                    BribeUtility.RemoveSilverFromInventory(actor, fee);
                    // No TakingEvent, no PropertyEngine.Fire — see this
                    // class's own doc comment. Fires unconditionally,
                    // whether or not the faction's record currently holds
                    // anything against the actor at all (module boundary:
                    // the verb never reads GetSuspicion to decide).
                    PropertyEngine.DampenSuspicion(targetFaction, ClaimantRef.OfPawn(actor), dampenFraction, tick);
                }), actor, targetPawn);
        }
    }
}
