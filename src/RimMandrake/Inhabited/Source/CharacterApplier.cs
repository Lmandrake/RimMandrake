using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Makes a generated pawn into one of the 294 authored people.
    ///
    /// ⭐ WHAT IT APPLIES: the NAME, the TRAITS, the GENDER, and the kit the prose
    /// earns — `weapon`, `apparel`, `skills`, and the CARRIED half of `items`. The
    /// name and the trouble trait still do most of the work (a name worth saying is
    /// the strongest single predictor that a player remembers somebody), but the
    /// kit is authored data with a defined meaning, and parsing it and then
    /// throwing it away was a lie CharacterDef told about this file.
    ///
    /// ⚠️ `skills` are OUTLIERS ONLY — an absent skill means "ordinary", not
    /// "unknown", so what is named is SET and everything else keeps the level
    /// generation rolled.
    ///
    /// ⛔ WHAT IT STILL DOES NOT APPLY, and neither claims to:
    ///
    ///   * `xenotype` and `pawnKind` — the prose does not carry them, DECIDE owes
    ///     them, and a guessed xenotype ships a wrong-looking person into a world
    ///     that is built once and frozen. Both fields are empty by design.
    ///   * The INSTALLED half of `items`. `items` mixes carried goods (Beer,
    ///     Ambrosia, a Drum) with bionics (BionicLeg, BionicArm, BionicJaw) and the
    ///     prose does not distinguish. Carried is done here; installing a bionic
    ///     means resolving a ThingDef to a RecipeDef and then to a BodyPartRecord
    ///     on this particular body, which is a feature with its own failure modes
    ///     and needs a live check — INHABITED_AUTHORED_BIONICS_INSTALL_1. Until
    ///     then `isTechHediff` entries are skipped, knowingly.
    ///   * `childhood` and `adult`, which stay authored TEXT rather than becoming
    ///     BackstoryDefs — a backstory carries skill gains and work disables, which
    ///     nobody has decided.
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
                        Log.Warning("[RimMandrake.Inhabited] " + character.defName + " (" + character.label
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

            ApplySkills(pawn, character);
            ApplyWeapon(pawn, character);
            ApplyApparel(pawn, character);
            ApplyCarriedItems(pawn, character);

            return true;
        }

        /// <summary>
        /// The authored skill levels, and ONLY those. 8 is average and is never
        /// written, so a skill absent from the def keeps whatever generation rolled
        /// for it rather than being flattened to a default.
        /// </summary>
        private static void ApplySkills(Pawn pawn, CharacterDef character)
        {
            if (pawn.skills == null || character.skills.NullOrEmpty())
            {
                return;
            }
            for (int i = 0; i < character.skills.Count; i++)
            {
                SkillGain gain = character.skills[i];
                if (gain?.skill == null)
                {
                    continue;
                }
                SkillRecord record = pawn.skills.GetSkill(gain.skill);

                // A skill the backstory disables reads 0 whatever is written into
                // it, so setting one would only look like it worked.
                if (record == null || record.TotallyDisabled)
                {
                    continue;
                }
                record.Level = gain.amount;
                record.xpSinceLastLevel = 0f;
            }
        }

        /// <summary>Their one signature weapon, replacing whatever was rolled.</summary>
        private static void ApplyWeapon(Pawn pawn, CharacterDef character)
        {
            if (character.weapon == null || pawn.equipment == null)
            {
                return;
            }
            if (!character.weapon.IsWeapon)
            {
                Log.Warning("[RimMandrake.Inhabited] " + character.defName + " (" + character.label
                            + ") authors " + character.weapon.defName
                            + " as a weapon, but it is not one. Fix the cast file.");
                return;
            }

            // Destroy first. Pawn_EquipmentTracker.AddEquipment does not replace a
            // primary -- it logs an error and drops the new one on the floor -- and
            // generation has usually already armed this pawn.
            pawn.equipment.DestroyAllEquipment();
            if (!(ThingMaker.MakeThing(character.weapon, GenStuff.DefaultStuffFor(character.weapon))
                    is ThingWithComps weapon))
            {
                return;
            }
            pawn.equipment.AddEquipment(weapon);
        }

        /// <summary>What they wear, on top of what generation dressed them in.</summary>
        private static void ApplyApparel(Pawn pawn, CharacterDef character)
        {
            if (pawn.apparel == null || character.apparel.NullOrEmpty())
            {
                return;
            }
            for (int i = 0; i < character.apparel.Count; i++)
            {
                ThingDef def = character.apparel[i];
                if (def == null || !def.IsApparel)
                {
                    continue;
                }
                if (!ApparelUtility.HasPartsToWear(pawn, def))
                {
                    // Pawn_ApparelTracker.Wear checks this itself and warns, but it
                    // can only name the pawn. Name the CHARACTER, which is what an
                    // author has to go and fix.
                    Log.Warning("[RimMandrake.Inhabited] " + character.defName + " (" + character.label
                                + ") authors " + def.defName
                                + ", which this body has no parts to wear.");
                    continue;
                }
                if (!(ThingMaker.MakeThing(def, GenStuff.DefaultStuffFor(def)) is Apparel apparel))
                {
                    continue;
                }

                // Nothing is dropped: this pawn is generated off-map, into a roster,
                // and has no floor to drop a replaced garment onto.
                pawn.apparel.Wear(apparel, dropReplacedApparel: false);
            }
        }

        /// <summary>
        /// The carried half of `items`. ⛔ `isTechHediff` entries -- the bionics --
        /// are SKIPPED, not carried in a pocket: see the class comment and
        /// INHABITED_AUTHORED_BIONICS_INSTALL_1.
        /// </summary>
        private static void ApplyCarriedItems(Pawn pawn, CharacterDef character)
        {
            if (pawn.inventory == null || character.items.NullOrEmpty())
            {
                return;
            }
            for (int i = 0; i < character.items.Count; i++)
            {
                ThingDef def = character.items[i];
                if (def == null || def.isTechHediff)
                {
                    continue;
                }
                Thing item = ThingMaker.MakeThing(def, GenStuff.DefaultStuffFor(def));
                if (item == null)
                {
                    continue;
                }
                if (!pawn.inventory.innerContainer.TryAdd(item))
                {
                    item.Destroy();
                }
            }
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
