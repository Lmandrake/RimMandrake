using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // WATER_TRUCE_RETRIBUTION_1. "First GUILTY hit in truce radius turns
    // wildlife on the aggressor FACTION" — never on everyone, never on the
    // player unless the player IS the aggressor. Subclassing
    // MentalState_Manhunter (rather than writing a fresh MentalState + a new
    // ThinkTree insertion) is deliberate: ThinkNode_ConditionalMentalStateClass
    // (SubTrees_Misc.xml, the vanilla Animal main tree) gates its aggro
    // JobGiver_Manhunter branch on `stateClass.IsInstanceOfType(mentalState)`
    // against typeof(MentalState_Manhunter) — a subclass satisfies that check,
    // so every animal in the game already runs the full manhunter
    // attack/pursue job logic the instant this state is active, with zero
    // ThinkTree or Harmony work of our own. The only thing worth overriding
    // is WHO counts as hostile.
    //
    // MentalState_Manhunter.ForceHostileTo already special-cases roaming
    // caravan animals and non-humanlike/non-mechanoid factions; this override
    // replaces that entirely rather than narrowing it, because "hostile to
    // literally everyone whose faction isn't null" is exactly the behavior
    // the design rules out (weeping_stones.md §6, the ambush ban; the item's
    // own "no dont-fight-back needed" — a defending, non-guilty colonist must
    // never be forced-hostile by this state).
    //
    // The target is a FACTION, not a pawn — the instigator of a guilty hit
    // is not always a Pawn (a turret is a legitimate instigator), so this
    // carries its own targetFaction rather than reusing MentalState's
    // causedByPawn (which RM_MapComponent_WaterTruce also still passes, as
    // otherPawn, purely for the base class's own bookkeeping/inspection
    // string — it is never read by the overrides below). Scribe-saved like
    // any other reference field; if the aggressor faction is somehow gone on
    // load (should not happen — Faction, unlike a Pawn, is never destroyed),
    // ForceHostileTo just returns false and the animal falls back to
    // ordinary AI rather than erroring.
    public class RM_MentalState_WaterTruceRetribution : MentalState_Manhunter
    {
        public Faction targetFaction;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref targetFaction, "targetFaction");
        }

        public override bool ForceHostileTo(Thing t)
        {
            return targetFaction != null && t != null && t.Faction == targetFaction;
        }

        public override bool ForceHostileTo(Faction f)
        {
            return targetFaction != null && f == targetFaction;
        }
    }
}
