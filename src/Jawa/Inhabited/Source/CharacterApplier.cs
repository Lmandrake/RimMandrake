using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace Inhabited
{
    /// <summary>
    /// Makes a generated pawn into one of the 269 authored people.
    ///
    /// ⭐ WHAT IT APPLIES, and the list is short on purpose: the NAME and the
    /// TRAITS. Those are the two things the prose actually carries as data, and
    /// they are also the two that do the work — a name worth saying is the single
    /// strongest predictor that a player will remember somebody, and the trouble
    /// trait is the thing they will later narrate as the reason.
    ///
    /// ⛔ WHAT IT DOES NOT APPLY, AND MUST NOT GUESS: xenotype, pawnKind, apparel
    /// and skills. The prose does not carry them, DECIDE owes them, and a guessed
    /// xenotype ships a wrong-looking person into a world that is built once and
    /// frozen. `childhood` and `adult` stay authored TEXT rather than becoming
    /// BackstoryDefs, for the same reason — a backstory carries skill gains and
    /// work disables, which nobody has decided.
    ///
    /// ⚠️ Traits are REPLACED, not added to. A generated pawn arrives with rolled
    /// traits, and leaving them would let a character written as `Ascetic` also be
    /// `Greedy` — the hook and the traits must agree, and a hook the mechanics do
    /// not back is a lie the player will catch.
    /// </summary>
    public static class CharacterApplier
    {
        /// <summary>Every authored person, by defName. Resolved on first use.</summary>
        public static IEnumerable<CharacterDef> All => DefDatabase<CharacterDef>.AllDefs;

        /// <summary>
        /// Turn <paramref name="pawn"/> into <paramref name="character"/>.
        /// Returns false and says why if it could not.
        /// </summary>
        public static bool ApplyTo(Pawn pawn, CharacterDef character)
        {
            if (pawn == null || character == null)
            {
                return false;
            }

            if (!character.label.NullOrEmpty())
            {
                // FromString handles "Chief Ghekk Ubb-Ubb" and "Sixty-One" alike;
                // a single-word name becomes a nick, which is what we want for a
                // droid called Tuesday.
                pawn.Name = NameTriple.FromString(character.label);
            }

            if (pawn.story?.traits != null && character.traits.Count > 0)
            {
                List<Trait> existing = new List<Trait>(pawn.story.traits.allTraits);
                for (int i = 0; i < existing.Count; i++)
                {
                    pawn.story.traits.RemoveTrait(existing[i]);
                }
                for (int i = 0; i < character.traits.Count; i++)
                {
                    CharacterTrait t = character.traits[i];
                    if (t?.def == null || pawn.story.traits.HasTrait(t.def))
                    {
                        continue;
                    }

                    // ⛔ DO NOT LET AN AUTHORING MISTAKE BUILD AN IMPOSSIBLE PAWN.
                    // TraitSet.GainTrait checks no conflicts and enforces no cap,
                    // and suppressConflicts:true here would mean a character
                    // authored Kind AND Psychopath simply becomes both -- something
                    // no vanilla pawn generation could ever produce, and which the
                    // player would read as a bug in the game rather than in us.
                    // The first trait wins and the second is refused, loudly. We do
                    // NOT pick a winner on the author's behalf beyond that: the real
                    // fix is in the cast file, and CharacterDef.ConfigErrors already
                    // names the pair at load.
                    Trait blocker = null;
                    List<Trait> held = pawn.story.traits.allTraits;
                    for (int j = 0; j < held.Count; j++)
                    {
                        if (held[j]?.def != null && held[j].def.ConflictsWith(t.def))
                        {
                            blocker = held[j];
                            break;
                        }
                    }
                    if (blocker != null)
                    {
                        Log.Warning("[Inhabited] " + character.defName + " (" + character.label
                                    + ") authors " + t.def.defName + " alongside "
                                    + blocker.def.defName + ", which conflict. "
                                    + t.def.defName + " was NOT applied. Fix the cast file.");
                        continue;
                    }
                    pawn.story.traits.GainTrait(new Trait(t.def, t.degree));
                }
            }

            if (character.gender.HasValue && pawn.gender != character.gender.Value)
            {
                pawn.gender = character.gender.Value;
            }

            return true;
        }

        /// <summary>
        /// Generate a pawn and make it this person. `fallbackKind` supplies the
        /// body the prose does not name; when DECIDE answers the pawnKind field
        /// this reads it from the def instead.
        /// </summary>
        public static Pawn Spawn(CharacterDef character, Faction faction, PawnKindDef fallbackKind,
            PlanetTile tile)
        {
            if (character == null)
            {
                return null;
            }
            PawnKindDef kind = character.pawnKind ?? fallbackKind ?? PawnKindDefOf.Villager;
            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                kind,
                faction,
                PawnGenerationContext.NonPlayer,
                tile,
                forceGenerateNewPawn: true,
                allowDead: false,
                allowDowned: false,
                canGeneratePawnRelations: true,
                mustBeCapableOfViolence: false,
                colonistRelationChanceFactor: 1f,
                forceAddFreeWarmLayerIfNeeded: false,
                allowGay: true,
                allowPregnant: false,
                allowFood: true,
                allowAddictions: true,
                inhabitant: true,
                certainlyBeenInCryptosleep: false,
                forceRedressWorldPawnIfFormerColonist: false,
                worldPawnFactionDoesntMatter: false,
                biocodeWeaponChance: 0f,
                biocodeApparelChance: 0f,
                extraPawnForExtraRelationChance: null,
                relationWithExtraPawnChanceFactor: 1f,
                validatorPreGear: null,
                validatorPostGear: null,
                forcedTraits: null,
                prohibitedTraits: null,
                minChanceToRedressWorldPawn: null,
                fixedBiologicalAge: character.age >= 0 ? (float?)character.age : null,
                fixedChronologicalAge: character.age >= 0 ? (float?)character.age : null,
                fixedGender: character.gender));
            if (pawn == null)
            {
                return null;
            }
            ApplyTo(pawn, character);
            return pawn;
        }

        public static CharacterDef ByDefName(string defName)
        {
            return DefDatabase<CharacterDef>.GetNamedSilentFail(defName);
        }
    }
}
