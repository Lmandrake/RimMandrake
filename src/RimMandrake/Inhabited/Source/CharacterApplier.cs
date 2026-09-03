using System;
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
    /// earns — `weapon`, `apparel`, `skills`, and BOTH halves of `items`: the
    /// carried goods go into the inventory and the `isTechHediff` entries are
    /// installed on the body. The name and the trouble trait still do most of the
    /// work (a name worth saying is the strongest single predictor that a player
    /// remembers somebody), but the kit is authored data with a defined meaning,
    /// and parsing it and then throwing it away was a lie CharacterDef told about
    /// this file.
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

            // ⚠️ BEFORE the weapon and the apparel, deliberately. Installing an
            // artificial part runs Pawn_HealthTracker.RestorePart on the natural
            // one first (Recipe_InstallArtificialBodyPart.ApplyOnPawn), so a part
            // this pawn was generated without comes BACK -- and both
            // ApparelUtility.HasPartsToWear and the equipment tracker's capacity
            // checks read the body as it stands when they run.
            ApplyInstalledItems(pawn, character);
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
        /// The carried half of `items`. `isTechHediff` entries are not carried in
        /// a pocket -- ApplyInstalledItems puts them in the body instead.
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
        /// RecipeWorker.ApplyOnPawn wants an ingredient list and none of the
        /// surgery workers read it when `billDoer` is null. Shared and never
        /// written to, exactly as PawnTechHediffsGenerator.emptyIngredientsList is.
        /// </summary>
        private static readonly List<Thing> NoIngredients = new List<Thing>();

        /// <summary>
        /// The INSTALLED half of `items` -- the bionics. `items` mixes carried
        /// goods (Beer, Ambrosia, a Drum) with parts (BionicArm, BionicEye,
        /// BionicJaw, BionicLeg) because the prose does not distinguish, and the
        /// split is `ThingDef.isTechHediff`, which is what `BodyPartBionicBase`
        /// and its siblings set (Core/HediffDefs/BodyParts/Hediffs_BodyParts_Base.xml).
        ///
        /// ⭐ THE PRECEDENT IS VANILLA'S OWN, and it is deliberately copied rather
        /// than invented: `PawnTechHediffsGenerator.InstallPart` is how the engine
        /// puts a bionic into a pawn who has no surgeon, no operating table, no
        /// bleeding and no recovery -- exactly our situation, since an authored
        /// character is materialised off-map into a roster. It resolves the
        /// ThingDef by asking which of the RACE'S OWN recipes takes it as an
        /// ingredient, then asks that recipe's worker which parts of THIS body it
        /// may apply to, then calls ApplyOnPawn with a null billDoer.
        ///
        /// ⚠️ Every failure here is named out loud. Nothing about this chain is
        /// guaranteed by the type system: a modded race whose ThingDef carries no
        /// surgery recipes, a body def with no Jaw, a second bionic arm on a pawn
        /// who already has two -- all of them are a silent no-op in vanilla, and
        /// the whole reason this was deferred once is that a silent no-op here is
        /// indistinguishable from working.
        /// </summary>
        private static void ApplyInstalledItems(Pawn pawn, CharacterDef character)
        {
            if (pawn.health == null || pawn.def == null || character.items.NullOrEmpty())
            {
                return;
            }
            for (int i = 0; i < character.items.Count; i++)
            {
                ThingDef def = character.items[i];
                if (def == null || !def.isTechHediff)
                {
                    continue;
                }
                InstallPart(pawn, character, def);
            }
        }

        /// <summary>
        /// Put one `isTechHediff` ThingDef into <paramref name="pawn"/>, or say
        /// why it could not go in. Modelled on PawnTechHediffsGenerator.InstallPart.
        /// </summary>
        private static void InstallPart(Pawn pawn, CharacterDef character, ThingDef partDef)
        {
            // ⭐ `pawn.def.AllRecipes` -- not `DefDatabase<RecipeDef>.AllDefs` -- is
            // what makes this race-correct: AllRecipes is the ThingDef's own
            // `recipes` plus every RecipeDef whose `recipeUsers` names it, so a
            // recipe that cannot be performed on this body is never considered.
            // InstallBionicArm's recipeUsers is <li>Human</li>, which is why a
            // droid or a modded chassis simply gets the warning below.
            //
            // `addsHediff != null` is ours, not vanilla's: RecipeDef.IsIngredient
            // is a pure ingredient-filter test and would happily match a recipe
            // that removes or replaces rather than installs, and
            // Recipe_InstallArtificialBodyPart.ApplyOnPawn dereferences
            // `recipe.addsHediff.hediffClass` unconditionally.
            List<RecipeDef> candidates = new List<RecipeDef>();
            List<RecipeDef> onThisBody = pawn.def.AllRecipes;
            for (int i = 0; i < onThisBody.Count; i++)
            {
                RecipeDef r = onThisBody[i];
                if (r?.addsHediff != null && r.IsIngredient(partDef))
                {
                    candidates.Add(r);
                }
            }

            RecipeDef chosen = null;
            BodyPartRecord chosenPart = null;
            List<BodyPartRecord> free = new List<BodyPartRecord>();
            for (int i = 0; i < candidates.Count && chosen == null; i++)
            {
                RecipeDef r = candidates[i];

                // `targetsBodyPart` defaults TRUE (RecipeDef.cs:105); the false case
                // is a whole-pawn hediff and takes a null part, as vanilla does.
                if (!r.targetsBodyPart)
                {
                    chosen = r;
                    break;
                }

                // ⭐ THIS is where "already occupied" is decided, and the engine
                // decides it, not us. Recipe_InstallArtificialBodyPart and
                // Recipe_InstallImplant both override GetPartsToApplyOn with a
                // validator that rejects a part already carrying this hediff, a
                // part whose parent is missing, and a part under an existing added
                // part. So a character authored with two bionic arms gets both
                // shoulders and one authored with three gets a warning on the
                // third -- no replace, no stacking, no bespoke occupancy test.
                free.Clear();
                foreach (BodyPartRecord p in r.Worker.GetPartsToApplyOn(pawn, r))
                {
                    free.Add(p);
                }
                if (free.Count == 0)
                {
                    continue;
                }

                // Vanilla picks at random among the valid parts and so do we: which
                // shoulder wears the bionic arm is not authored, and the pawn this
                // is being applied to was itself rolled.
                chosen = r;
                chosenPart = free.RandomElement();
            }

            if (chosen != null)
            {
                try
                {
                    // billDoer null: no surgery roll, no tale, no ideoligion event,
                    // and no violation reported. With `pawn.Map` also null -- an
                    // authored character is built off-map -- ApplyOnPawn takes its
                    // `pawn.health.RestorePart(part)` branch and nothing is spawned
                    // on any floor.
                    chosen.Worker.ApplyOnPawn(pawn, chosenPart, null, NoIngredients, null);
                }
                catch (Exception e)
                {
                    // A throw here would abort the whole cast instantiation and
                    // take a settlement's population with it. One person missing an
                    // arm is survivable; a place with nobody in it is not.
                    Log.Error("[RimMandrake.Inhabited] installing " + partDef.defName + " on "
                              + character.defName + " (" + character.label + ") via "
                              + chosen.defName + " threw: " + e);
                }
                return;
            }

            // Not every tech hediff is surgical. A mechlink or a psychic amplifier
            // is a usable item that installs itself through a comp, and vanilla
            // falls back to exactly this. None of the 294 author one today.
            CompProperties_UseEffectInstallImplant implant =
                partDef.GetCompProperties<CompProperties_UseEffectInstallImplant>();
            if (implant?.hediffDef != null)
            {
                List<BodyPartRecord> named = implant.bodyPart == null
                    ? null
                    : pawn.RaceProps.body.GetPartsWithDef(implant.bodyPart);
                pawn.health.AddHediff(implant.hediffDef, named.NullOrEmpty() ? null : named.RandomElement());
                return;
            }

            // Name the CHARACTER, because that is the file an author has to go and
            // fix, and say WHICH of the two ways it failed.
            Log.Warning("[RimMandrake.Inhabited] " + character.defName + " (" + character.label
                        + ") authors " + partDef.defName + ", which was NOT installed: "
                        + (candidates.Count == 0
                            ? "no recipe on " + pawn.def.defName + " takes it as an ingredient"
                            : "no free body part on this " + pawn.RaceProps.body.defName
                              + " body for " + candidates[0].defName)
                        + ".");
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
