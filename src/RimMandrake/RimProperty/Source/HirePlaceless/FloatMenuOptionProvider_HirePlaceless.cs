using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.Property;

namespace RimMandrake.HirePlaceless
{
    /// <summary>
    /// SETTLEMENT_VERBS_WAVE_1, social-fabric pass (fourth and final v1 verb
    /// family). Spec item 9: "social fabric (rumors as intel, sabacc, hiring
    /// the placeless, bribes and bought rounds as propagation dampers)."
    /// This pass scopes to ONE: hiring the placeless. Rumors-as-intel and
    /// bribes-as-propagation-dampers both need a NEW read/write surface on
    /// FactionRecord (a suspicion query or a witness-entry damper) that does
    /// not exist yet — real fabric work, not a float-menu wrapper. Sabacc is
    /// a whole minigame (cards, stakes, a UI loop), not a right-click order
    /// at all. Hiring is the one sub-mechanic that reuses the fabric AS-IS,
    /// with zero new engine code — same discipline every prior pass in this
    /// item applied ("pick the ONE well-scoped mechanic the spec most
    /// clearly supports with existing fabric").
    ///
    /// Same right-click float-menu-order shape as every other verb this item
    /// built (SalvageClaim/WalkableCommerce/Pickpocket) — needs a selected
    /// acting pawn AND a clicked target; no JobDriver, the whole transaction
    /// runs instantly from this option's own delegate. FloatMenuMakerMap.
    /// Init() auto-registers every non-abstract FloatMenuOptionProvider via
    /// reflection, so no Harmony hook or registration call is needed here
    /// either.
    ///
    /// "Fabric already implements the RESULT" check (this pass's own brief,
    /// step 2), and the fit here is the cleanest of the four verbs built so
    /// far: WalkableCommerce's own doc comment flagged exactly this gap when
    /// it scoped itself OUT — "a live Pawn is hiring/indenture — social-
    /// fabric/crime-suite territory, out of this pass" — pointing straight
    /// at TakingAct.Buy's existing case (RecordTransfer(...,
    /// ClaimBasis.Purchased, 1f, ...), WasAuthorized = true unconditionally,
    /// "a completed sale is legitimate by definition"). TakingEvent.Thing is
    /// a plain Verse.Thing field; Pawn IS a Thing, so firing Buy against a
    /// target Pawn needs no new field, no new TakingAct case, no new
    /// ClaimBasis — the fabric doesn't know or care that this "merchandise"
    /// happens to be a person. This mod builds only the gate + the fee.
    ///
    /// Where this DIFFERS from BuyMerchandise, deliberately, and why that
    /// difference IS the verb: BuyMerchandise requires a *resolved* prior
    /// claim (an unclaimed item has no seller). Hiring the PLACELESS is the
    /// mirror image — it requires the ABSENCE of any resolved claim, virtual
    /// or recorded (<see cref="ClaimEngine.ResolveClaim"/>), same as
    /// PaySalvageClaim's own unclaimed-wreck case but for a living target.
    /// A Pawn with Faction == null and no possessor/territorial claim
    /// resolves to exactly that ("placeless" — ClaimEngine.FindPossessor
    /// only fires for a Thing held in someone's equipment/apparel/inventory/
    /// carry tracker, which a spawned map Pawn never is of itself, and
    /// ResolveVirtualClaim's Commons fallback reads thing.Faction, which is
    /// null here) — verified by reading ClaimEngine before writing this, not
    /// assumed. A factioned pawn, a prisoner, or a pawn someone else already
    /// hired (a still-resolving Purchased record) is out of scope: that's
    /// defection, capture, or poaching, not this verb.
    /// </summary>
    public class FloatMenuOptionProvider_HirePlaceless : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool RequiresManipulation => true;

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            if (!PropertySettings.hirePlacelessEnabled) return null;

            Pawn actor = context.FirstSelectedPawn;

            if (!(clickedThing is Pawn targetPawn)) return null;
            if (targetPawn == actor) return null;
            if (!targetPawn.Spawned) return null;

            // Downed is the claim-fee gizmo's own droid case (spec item 1's
            // "the powered-down droid") — hiring implies an active hand, not
            // a salvage. Keeps the two verbs from ever offering on the same
            // target at once.
            if (targetPawn.Downed) return null;

            // Mid-fight isn't a hiring conversation — same reasoning
            // Pickpocket's own HostileTo gate already applies to this
            // family's other verb.
            if (targetPawn.HostileTo(actor)) return null;

            // "Placeless" means no home faction at all — a colonist, guest,
            // or prisoner already belongs somewhere and hiring them is a
            // different transaction (defection, ransom, recruitment) this
            // verb does not build.
            if (targetPawn.Faction != null) return null;
            if (targetPawn.IsPrisoner) return null;

            // A person, or a masterless droid wandering with nobody to
            // answer to (spec item 3's own "powered-down droid" precedent
            // for this family extends naturally to an ACTIVE one here,
            // since Downed already routes a broken droid to the other
            // verb).
            if (targetPawn.RaceProps == null || !(targetPawn.RaceProps.Humanlike || targetPawn.RaceProps.IsMechanoid)) return null;

            int tick = Find.TickManager.TicksGame;

            // The placeless test itself: nobody — virtual or recorded —
            // currently resolves as this pawn's claimant. If someone else
            // already hired them (a still-resolving Purchased record) this
            // returns that claim and correctly blocks a second hire.
            if (ClaimEngine.ResolveClaim(targetPawn, tick).HasValue) return null;

            int fee = HirePlacelessUtility.ComputeHireFeeSilver();

            if (!actor.CanReach(targetPawn, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot hire " + targetPawn.LabelShort + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }

            int carried = HirePlacelessUtility.CountSilverInInventory(actor);
            if (carried < fee)
            {
                return new FloatMenuOption(
                    "Cannot hire " + targetPawn.LabelShort
                    + ": not enough silver (need " + fee + ", have " + carried + ")", null);
            }

            ClaimantRef actorRef = ClaimantRef.OfPawn(actor);

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Hire " + targetPawn.LabelShort + " (" + fee + " silver)",
                delegate
                {
                    HirePlacelessUtility.RemoveSilverFromInventory(actor, fee);
                    // PropertyEngine.Fire's existing Buy case already fully
                    // implements the result — see this class's own doc
                    // comment. No job, no schedule, no following behavior:
                    // same "the point is the provenance RECORD, not a
                    // physical/behavioral move" v1 simplification
                    // WalkableCommerce and PaySalvageClaim both already
                    // apply to their own targets.
                    PropertyEngine.Fire(new TakingEvent(targetPawn, actorRef, TakingAct.Buy, tick));
                }), actor, targetPawn);
        }
    }
}
