using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
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
    ///
    /// ── DROIDWORKS_WIPE_SEVERITY_1 (packet B10) ──────────────────────────────
    /// Owner ruling 7, verbatim: "Wipes: 7-day debuff + service-record reset, and
    /// make it REALLY severe. Like it bumps into walls, learns how to use its body,
    /// and frequently forgets what it was doing during that week. Frequently also
    /// adds a permanent hardware quirk that cannot be reset but only accrete
    /// further." Three additions here, all AFTER the trait randomization above:
    ///
    ///  1. RSW_DW_RecentlyWiped, a 7-day hediff (severity 1 -> 0 at -1/7 per day)
    ///     whose stages ramp Moving/Manipulation and whose HediffComp_DWWipeStumble
    ///     interrupts jobs and blunders the droid into things.
    ///  2. SERVICE-RECORD RESET, done against vanilla's OWN service record:
    ///     Pawn_RecordsTracker - kills, damage taken, time as a colonist, distance
    ///     walked, every RecordDef - which is the pawn's history the player can
    ///     actually read, in the bio tab's Records page. There is NO Droidworks
    ///     CompServiceRecord to reset: a repo-wide grep for "ServiceRecord"
    ///     (2026-09-08) returns zero C# hits, and the droid-specific one is
    ///     DROIDWORKS_SERVICE_RECORD_DRIFT_1 (packet E2), unbuilt. This packet
    ///     deliberately does NOT stub E2's system - it resets the record that
    ///     already exists.
    ///  3. A permanent hardware quirk, QuirkChance of the time
    ///     (DroidworksHardwareQuirks). Never removed by anything: RandomizeTraits
    ///     below skips any trait the quirk pool claims, so wiping a droid twice
    ///     ACCRETES a second quirk rather than replacing the first.
    /// </summary>
    public class Recipe_DWMemoryWipe : Recipe_Surgery
    {
        /// <summary>
        /// Chance a wipe leaves a permanent hardware quirk. Ruling 7 says
        /// "frequently", not "always" - FOUNDRY's own number for that word, and
        /// deliberately under 1.0 so a wipe is a gamble rather than a counter.
        /// </summary>
        public const float QuirkChance = 0.6f;

        /// Cached reflection handle on Pawn_RecordsTracker's private DefMap.
        /// There is no public API that zeroes a record: AddTo Log.Errors on any
        /// RecordType.Time def (which is most of the service record - time as
        /// colonist, time in combat), and there is no Clear/SetTo at all. The
        /// DefMap it holds has a public SetAll, so reaching the field is the
        /// whole of the trick. Harmony is already a reference of this assembly.
        ///
        /// Resolved lazily, NOT in a static initializer: this type is
        /// constructed by the def loader as RSW_DW_MemoryWipe's workerClass, and
        /// a throwing type initializer there would take the whole recipe out
        /// rather than just the record reset.
        private static System.Reflection.FieldInfo recordsField;
        private static bool recordsFieldResolved;

        private static System.Reflection.FieldInfo RecordsField
        {
            get
            {
                if (!recordsFieldResolved)
                {
                    recordsFieldResolved = true;
                    recordsField = HarmonyLib.AccessTools.Field(
                        typeof(Pawn_RecordsTracker), "records");
                    if (recordsField == null)
                    {
                        Log.Warning("[Droidworks] Pawn_RecordsTracker.records not found - "
                                    + "memory wipe will not reset the service record.");
                    }
                }
                return recordsField;
            }
        }

        public override IEnumerable<BodyPartRecord> GetPartsToApplyOn(Pawn pawn, RecipeDef recipe)
        {
            yield return null;
        }

        public override void ApplyOnPawn(Pawn pawn, BodyPartRecord part, Pawn billDoer,
                                         List<Thing> ingredients, Bill bill)
        {
            RandomizeTraits(pawn);
            ClearRelationsAndSocialMemories(pawn);
            ResetServiceRecord(pawn);

            // No idiosyncrasy hediffs exist yet to zero - see class header. When the
            // behavior triad's "EXPERIENCED" tier lands as real hediffs, this is
            // where they get cleared.

            // B10: the 7-day relearning debuff. Added after the trait work so
            // nothing above can strip it. Wiping a droid that is STILL wiped
            // restarts the seven days at full severity rather than doing nothing
            // - a second wipe is not a way to shorten the first.
            if (pawn.health != null)
            {
                Hediff wiped = pawn.health.hediffSet
                    .GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_RecentlyWiped);
                if (wiped != null) wiped.Severity = 1f;
                else pawn.health.AddHediff(DroidworksDefOf.RSW_DW_RecentlyWiped);
            }

            // B10: the permanent quirk. Accretes - a droid wiped three times can
            // carry three quirks, and no recipe in this mod ever takes one back.
            if (Rand.Chance(QuirkChance))
            {
                DroidworksHardwareQuirks.TryGainRandomQuirk(pawn);
            }

            pawn.SetFaction(Faction.OfPlayer, billDoer);

            // Deliberately NOT touching pawn.skills - v0 scope, embodied software.
        }

        private static void RandomizeTraits(Pawn pawn)
        {
            if (pawn.story?.traits == null) return;

            // B10: hardware quirks are excluded from BOTH halves - they are not
            // removed, and they are not counted, so the pawn gets back exactly as
            // many ordinary traits as it lost and keeps every quirk on top.
            List<Trait> existing = pawn.story.traits.allTraits
                .Where(t => !DroidworksHardwareQuirks.IsQuirk(t)).ToList();
            int count = existing.Count;
            foreach (Trait trait in existing)
            {
                pawn.story.traits.RemoveTrait(trait);
            }
            if (count <= 0) return;

            // Quirk TraitDefs carry commonality 0, so GenerateTraitsFor's
            // RandomElementByWeight can never roll one back in here either.
            List<Trait> fresh = PawnGenerator.GenerateTraitsFor(pawn, count);
            foreach (Trait trait in fresh)
            {
                pawn.story.traits.GainTrait(trait);
            }
        }

        /// <summary>
        /// Zeroes every RecordDef on the pawn - the service record the player can
        /// read in the bio tab. See the class header for why this is vanilla's
        /// Pawn_RecordsTracker and not a Droidworks comp.
        /// </summary>
        private static void ResetServiceRecord(Pawn pawn)
        {
            if (pawn.records == null || RecordsField == null) return;
            (RecordsField.GetValue(pawn.records) as DefMap<RecordDef, float>)?.SetAll(0f);
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
