using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace Droidworks
{
    /// <summary>
    /// DROIDWORKS_WIPE_AND_SPIKE_1. Memory wipe, per design/Jawa/droid_system_spec.md
    /// section 3 ("embodied software"): wipe RANDOMIZES traits rather than clearing
    /// them, clears relations and social memories, sets faction to player, and
    /// deliberately does NOT touch skills - BENCH's own words, "embodied software -
    /// skills live in the body." Whole-pawn recipe, no race restriction (same v0
    /// precedent Recipe_RebootDroid.cs/Recipe_RestrainingBolt already set - always
    /// eligible, GetPartsToApplyOn always yields the single whole-pawn null part).
    ///
    /// Trait randomization reuses vanilla's OWN trait-rolling mechanism rather than
    /// hand-rolling one that would drift from exclusivity groups and degree ranges:
    /// the SAME count of traits is re-rolled via the public
    /// Verse.PawnGenerator.GenerateTraitsFor(pawn, count) - the exact method
    /// PawnGenerator.GenerateTraits itself calls at growth moments - which already
    /// checks TraitDef.ConflictsWith, disabledWorkTags/disabledWorkTypes,
    /// forcedPassions, gender-specific commonality and RandomTraitDegree. Traits are
    /// removed/added through TraitSet.RemoveTrait/GainTrait (not direct list
    /// mutation) so every downstream side effect - Notify_DisabledWorkTypesChanged,
    /// mood recalculation, ability grants/revokes, graphics-dirty - fires exactly as
    /// it would for a freshly generated pawn.
    ///
    /// Social-memory clearing copies the exact idiom Anomaly's own memory-wipe
    /// mechanism uses (Verse.AI.Group.PsychicRitualToil_Brainwipe.ApplyOutcome,
    /// read via RimSage): filter the pawn's Thought_Memory list by "is
    /// ISocialThought", then MemoryThoughtHandler.RemoveMemory each - the
    /// vanilla-recognized definition of "a social memory" (Thought_MemorySocial and
    /// its siblings implement ISocialThought). Relations use
    /// Pawn_RelationsTracker.ClearAllRelations() directly rather than the
    /// non-blood-only variant - droids carry no blood relations, so the distinction
    /// buys nothing here and a full clear matches "clears relations" verbatim.
    ///
    /// Idiosyncrasy hediffs: NONE EXIST YET. design/Jawa/droid_system_spec.md
    /// sections 4 and 11 (the behavior triad; "EXPERIENCED" idiosyncrasies accreted
    /// over service) are explicitly "deliberately unengineered until played" - there
    /// is no idiosyncrasy HediffDef or system anywhere in this codebase to zero
    /// (confirmed: a full-source RimSage search for "idiosyncrasy" returns zero
    /// hits). This step is a documented no-op, not a placeholder invented to look
    /// complete - see ApplyOnPawn's own comment at the call site.
    /// </summary>
    public class Recipe_DWMemoryWipe : Recipe_Surgery
    {
        public override IEnumerable<BodyPartRecord> GetPartsToApplyOn(Pawn pawn, RecipeDef recipe)
        {
            yield return null;
        }

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            RandomizeTraits(pawn);
            ClearRelationsAndSocialMemories(pawn);

            // No idiosyncrasy hediffs exist yet to zero - see class header. When the
            // behavior triad's "EXPERIENCED" tier lands as real hediffs, this is
            // where they get cleared.

            pawn.SetFaction(Faction.OfPlayer, billDoer);

            // Deliberately NOT touching pawn.skills - v0 scope, embodied software.
        }

        private static void RandomizeTraits(Pawn pawn)
        {
            if (pawn.story?.traits == null) return;

            List<Trait> existing = pawn.story.traits.allTraits.ToList();
            int count = existing.Count;
            foreach (Trait trait in existing)
            {
                pawn.story.traits.RemoveTrait(trait);
            }
            if (count <= 0) return;

            List<Trait> fresh = PawnGenerator.GenerateTraitsFor(pawn, count);
            foreach (Trait trait in fresh)
            {
                pawn.story.traits.GainTrait(trait);
            }
        }

        private static void ClearRelationsAndSocialMemories(Pawn pawn)
        {
            pawn.relations?.ClearAllRelations();

            MemoryThoughtHandler memories = pawn.needs?.mood?.thoughts?.memories;
            if (memories == null) return;

            List<Thought_Memory> social = memories.Memories.Where(m => m is ISocialThought).ToList();
            foreach (Thought_Memory memory in social)
            {
                memories.RemoveMemory(memory);
            }
        }
    }
}
