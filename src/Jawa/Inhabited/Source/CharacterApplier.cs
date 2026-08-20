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
                    pawn.story.traits.GainTrait(new Trait(t.def, t.degree), suppressConflicts: true);
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
