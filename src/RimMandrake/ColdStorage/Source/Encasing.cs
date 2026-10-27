using System.Collections.Generic;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ColdStorage
{
    // Encasing (COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS; design/RimStarWars/cold_storage_line_2026-10-26.md §4.3):
    // a recipe that freezes its food ingredients INTO the product, and a recipe that gives them back. The product holds
    // the real items (CompEncased), so whatever went in - quality, ingredients, rot progress - comes out unchanged. Held
    // items are never ticked, so nothing in a pack rots or deteriorates. Generic engine, no setting words: Star Wars
    // Cuisine's carbon-freezing press is the first user.

    public enum EncaseMode
    {
        /// <summary>The recipe's food ingredients go inside its first product that has a CompEncased.</summary>
        Encase,

        /// <summary>The recipe's encased ingredients give back what they hold as the products.</summary>
        Release,
    }

    /// <summary>On a RecipeDef whose workerClass is <see cref="RecipeWorker_Encase"/>.</summary>
    public class ColdStorageEncaseExtension : DefModExtension
    {
        public EncaseMode mode = EncaseMode.Encase;

        /// <summary>Release only: a meal released may come out as this instead (same count, same ingredients).</summary>
        public ThingDef shockedMealInto;

        /// <summary>Release only: the chance per meal of <see cref="shockedMealInto"/>.</summary>
        public float shockChance = 0.05f;

        /// <summary>Optional "Namespace.Type:field" naming a public static float that overrides
        /// <see cref="shockChance"/> live (a Mod Settings slider in the mod that owns the recipe).</summary>
        public string shockChanceSettingField;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (!shockChanceSettingField.NullOrEmpty() && !ColdStorageKernel.SplitSettingRef(shockChanceSettingField, out _, out _))
            {
                yield return "shockChanceSettingField must read Namespace.Type:field, got " + shockChanceSettingField;
            }
            if (mode == EncaseMode.Encase && shockedMealInto != null)
            {
                yield return "shockedMealInto applies to mode Release only";
            }
            if (shockedMealInto != null && (shockedMealInto.ingestible == null || !shockedMealInto.ingestible.IsMeal))
            {
                yield return "shockedMealInto " + shockedMealInto.defName + " is not a meal";
            }
        }

        public float LiveShockChance()
        {
            System.Reflection.FieldInfo f = ColdStorageGates.Field(shockChanceSettingField);
            float c = f != null && f.FieldType == typeof(float) ? (float)f.GetValue(null) : shockChance;
            return ColdStorageKernel.Clamp01(c);
        }
    }

    public class CompProperties_Encased : CompProperties
    {
        public CompProperties_Encased()
        {
            compClass = typeof(CompEncased);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (parentDef.stackLimit != 1)
            {
                yield return "an encased item holds its own contents, so its stackLimit must be 1 (got " + parentDef.stackLimit + ")";
            }
        }
    }

    /// <summary>An item that holds other items, frozen: never ticked, so never rotting, until a Release recipe opens it.
    /// Its market value and mass include what it holds (StatPart_EncasedContents); colony wealth counts the item once
    /// (Patch_WealthWatcher_WealthItemsFilter).</summary>
    public class CompEncased : ThingComp, IThingHolder
    {
        private ThingOwner<Thing> contents;

        public ThingOwner<Thing> Contents
        {
            get
            {
                if (contents == null)
                {
                    contents = new ThingOwner<Thing>(this, false, LookMode.Deep);
                }
                return contents;
            }
        }

        public bool Empty => contents == null || contents.Count == 0;

        public ThingOwner GetDirectlyHeldThings()
        {
            return Contents;
        }

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Deep.Look(ref contents, "encased", this);
        }

        public override bool AllowStackWith(Thing other)
        {
            return false;
        }

        public override void PostDestroy(DestroyMode mode, Map previousMap)
        {
            base.PostDestroy(mode, previousMap);
            contents?.ClearAndDestroyContents();
        }

        /// <summary>Sum of value-per-unit times count over the contents, for one stat.</summary>
        public float ContentsSum(StatDef stat)
        {
            if (Empty)
            {
                return 0f;
            }
            float[] unit = new float[contents.Count];
            int[] count = new int[contents.Count];
            for (int i = 0; i < contents.Count; i++)
            {
                unit[i] = contents[i].GetStatValue(stat);
                count[i] = contents[i].stackCount;
            }
            return ColdStorageKernel.StackSum(unit, count);
        }

        public override string TransformLabel(string label)
        {
            return Empty ? label + " (" + "RM_ColdStorage_EncasedEmpty".Translate() + ")" : label;
        }

        public override string CompInspectStringExtra()
        {
            if (Empty)
            {
                return "RM_ColdStorage_EncasedNothing".Translate();
            }
            StringBuilder sb = new StringBuilder();
            foreach (Thing t in contents)
            {
                if (sb.Length > 0)
                {
                    sb.Append(", ");
                }
                sb.Append(t.LabelCap);
            }
            return "RM_ColdStorage_EncasedHolds".Translate(sb.ToString());
        }

        public static CompEncased Of(Thing thing)
        {
            return (thing as ThingWithComps)?.GetComp<CompEncased>();
        }

        /// <summary>Whether <paramref name="thing"/> is held inside an encased item right now.</summary>
        public static bool IsEncased(Thing thing)
        {
            return thing?.holdingOwner?.Owner is CompEncased;
        }

        /// <summary>Move <paramref name="thing"/> inside: off the map if spawned, out of any container if held.</summary>
        public void Take(Thing thing)
        {
            if (thing == null || thing.Destroyed)
            {
                return;
            }
            if (thing.Spawned)
            {
                thing.DeSpawn();
            }
            else if (thing.holdingOwner != null)
            {
                thing.holdingOwner.Remove(thing);
            }
            Contents.TryAdd(thing, true);
        }
    }

    /// <summary>Consumes the ingredients of an encase or release recipe, except those now held inside a product (and
    /// those absorbed into a stack already held there).</summary>
    public class RecipeWorker_Encase : RecipeWorker
    {
        public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)
        {
            if (ingredient == null || ingredient.Destroyed || CompEncased.IsEncased(ingredient))
            {
                return;
            }
            base.ConsumeIngredient(ingredient, recipe, map);
        }
    }

    /// <summary>On MarketValue and Mass: an encased item adds what it holds.</summary>
    public class StatPart_EncasedContents : StatPart
    {
        public override void TransformValue(StatRequest req, ref float val)
        {
            if (TryGetValue(req, out float add))
            {
                val += add;
            }
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!TryGetValue(req, out float add))
            {
                return null;
            }
            string shown = parentStat == StatDefOf.Mass ? add.ToStringMassOffset() : add.ToStringMoneyOffset();
            return "RM_ColdStorage_EncasedStat".Translate() + ": " + shown;
        }

        private bool TryGetValue(StatRequest req, out float value)
        {
            value = 0f;
            CompEncased c = req.HasThing ? CompEncased.Of(req.Thing) : null;
            if (c == null || c.Empty)
            {
                return false;
            }
            value = c.ContentsSum(parentStat);
            return true;
        }
    }

    /// <summary>Colony wealth already counts an encased item at its full value (the StatPart above); its contents
    /// must not be counted a second time through the holder tree.</summary>
    [HarmonyPatch(typeof(WealthWatcher), nameof(WealthWatcher.WealthItemsFilter))]
    [PatchFeature("Encased goods count once in wealth")]
    internal static class Patch_WealthWatcher_WealthItemsFilter
    {
        private static void Postfix(IThingHolder x, ref bool __result)
        {
            if (__result && x is CompEncased)
            {
                __result = false;
            }
        }
    }

    /// <summary>
    /// Products of a recipe with a <see cref="ColdStorageEncaseExtension"/>. Encase: the food ingredients go inside the
    /// first product able to hold them. Release: each encased ingredient's contents are the products; meals may come
    /// out as <see cref="ColdStorageEncaseExtension.shockedMealInto"/>. Runs while Toils_Recipe lists the products,
    /// before it consumes the ingredients (RecipeWorker_Encase leaves the encased ones alone).
    /// </summary>
    [HarmonyPatch(typeof(GenRecipe), nameof(GenRecipe.MakeRecipeProducts))]
    [PatchFeature("Encasing recipes (carbon freezing)")]
    internal static class Patch_GenRecipe_MakeRecipeProducts_Encase
    {
        private static IEnumerable<Thing> Postfix(IEnumerable<Thing> __result, RecipeDef recipeDef, Pawn worker, List<Thing> ingredients)
        {
            ColdStorageEncaseExtension ext = recipeDef?.GetModExtension<ColdStorageEncaseExtension>();
            if (ext == null || ingredients == null)
            {
                foreach (Thing t in __result)
                {
                    yield return t;
                }
                yield break;
            }
            if (ext.mode == EncaseMode.Encase)
            {
                CompEncased into = null;
                List<Thing> surplus = new List<Thing>();
                foreach (Thing t in __result)
                {
                    if (into == null)
                    {
                        into = CompEncased.Of(t);
                        if (into != null)
                        {
                            // The pawn may have carried whole stacks (more than the recipe counts): the pack takes
                            // exactly the recipe count of each ingredient line, the surplus comes back as products.
                            int[] budget = recipeDef.ingredients.Select(ic => (int)ic.GetBaseCount()).ToArray();
                            foreach (Thing ing in ingredients.ToList())
                            {
                                if (ing != null && !ing.Destroyed && ing.def.IsIngestible && CompEncased.Of(ing) == null)
                                {
                                    int line = recipeDef.ingredients.FindIndex(ic => ic.filter.Allows(ing));
                                    int take = line < 0 ? ing.stackCount : ColdStorageKernel.TakeWithinBudget(ing.stackCount, budget[line]);
                                    if (line >= 0)
                                    {
                                        budget[line] -= take;
                                    }
                                    if (take <= 0)
                                    {
                                        // None of this stack goes in: it must leave the ingredient list, or Toils_Recipe's
                                        // ConsumeIngredients (run on this same list after the products are listed) destroys it.
                                        // A stack still on the bench stays where it is; only an unspawned one is placed as a
                                        // product (placing a spawned or destroyed thing is an error and lost the meal).
                                        ingredients.Remove(ing);
                                        if (!ing.Spawned && ing.holdingOwner == null)
                                        {
                                            surplus.Add(ing);
                                        }
                                        continue;
                                    }
                                    if (take < ing.stackCount)
                                    {
                                        surplus.Add(ing.SplitOff(ing.stackCount - take));
                                    }
                                    into.Take(ing);
                                }
                            }
                        }
                    }
                    yield return t;
                }
                foreach (Thing extra in surplus)
                {
                    yield return extra;
                }
                yield break;
            }
            // Release: vanilla products (normally none) pass through, then each pack's contents.
            foreach (Thing t in __result)
            {
                yield return t;
            }
            float chance = ext.shockedMealInto == null ? 0f : ext.LiveShockChance();
            int shocked = 0;
            foreach (Thing ing in ingredients)
            {
                CompEncased pack = CompEncased.Of(ing);
                if (pack == null || pack.Empty)
                {
                    continue;
                }
                foreach (Thing held in pack.Contents.ToList())
                {
                    pack.Contents.Remove(held);
                    if (chance > 0f && held.def.ingestible != null && held.def.ingestible.IsMeal && held.def != ext.shockedMealInto)
                    {
                        // capped at one burnt stack: Shock makes a single stack, so a held stack larger than the burnt
                        // def's stackLimit (a stack-size mod) would otherwise lose the meals above it
                        int n = Mathf.Min(ColdStorageKernel.ShockedCount(held.stackCount, chance, () => Rand.Value),
                            ext.shockedMealInto.stackLimit);
                        if (n > 0)
                        {
                            shocked += n;
                            Thing part = n >= held.stackCount ? held : held.SplitOff(n);
                            Thing burnt = Shock(part, ext.shockedMealInto);
                            if (part != held)
                            {
                                yield return held;
                            }
                            yield return burnt;
                            continue;
                        }
                    }
                    yield return held;
                }
            }
            if (shocked > 0 && worker != null && PawnUtility.ShouldSendNotificationAbout(worker))
            {
                Messages.Message("RM_ColdStorage_ReleaseShocked".Translate(shocked, ext.shockedMealInto.label),
                    worker, MessageTypeDefOf.NegativeEvent);
            }
        }

        /// <summary>The same count of <paramref name="into"/>, keeping what the meal was made from.</summary>
        private static Thing Shock(Thing meal, ThingDef into)
        {
            Thing made = ThingMaker.MakeThing(into);
            made.stackCount = Mathf.Min(meal.stackCount, into.stackLimit);
            CompIngredients was = meal.TryGetComp<CompIngredients>();
            CompIngredients now = made.TryGetComp<CompIngredients>();
            if (was != null && now != null)
            {
                foreach (ThingDef d in was.ingredients)
                {
                    now.RegisterIngredient(d);
                }
            }
            meal.Destroy();
            return made;
        }
    }
}
