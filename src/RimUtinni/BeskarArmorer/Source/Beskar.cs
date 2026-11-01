// BESKAR_ARMORER_QUEST_1 spec 5.1: what counts as beskar, and the startup work that needs loaded defs.
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.BeskarArmorer
{
    /// <summary>Marks a ThingDef as a beskar material. Added by Patches/RM_BeskarMaterials.xml.</summary>
    public class RM_BeskarMaterial : DefModExtension { }

    public static class BeskarUtil
    {
        public static bool IsMaterial(ThingDef d) { return d != null && d.GetModExtension<RM_BeskarMaterial>() != null; }

        private static bool CostNamesBeskar(ThingDef d)
        {
            if (d?.costList == null) return false;
            for (int i = 0; i < d.costList.Count; i++) if (IsMaterial(d.costList[i].thingDef)) return true;
            return false;
        }

        /// <summary>The def alone: a beskar material, or gear whose cost list names one. Stuff is per thing: see Carries.</summary>
        public static bool DefCarries(ThingDef d) { return IsMaterial(d) || CostNamesBeskar(d); }

        public static bool Carries(Thing t) { return t != null && (DefCarries(t.def) || IsMaterial(t.Stuff)); }

        public static int Mass(Thing t)
        {
            if (t == null) return 0;
            IEnumerable<KeyValuePair<bool, int>> cost = t.def.costList?.Select(c => new KeyValuePair<bool, int>(IsMaterial(c.thingDef), c.count));
            return ArmorerKernel.BeskarMass(IsMaterial(t.def), t.stackCount, cost, IsMaterial(t.Stuff), t.Stuff != null ? t.def.CostStuffCount : 0);
        }
    }

    [DefOf]
    public static class ArmorerDefOf
    {
        public static ThingDef RM_ArmorerForge;
        public static ThingDef KOTOR_IngotBeskar;
        public static WorldObjectDef RM_ArmorerCovert;
        public static FactionDef RM_TribeOfTheArmorer;
        public static PawnKindDef RM_TheArmorer;
        public static PawnKindDef RM_CovertSworn;
        public static HediffDef RM_ArmorerOfTheTribe;
        public static HediffDef RM_CovertSwornMark;
        public static QuestScriptDef RM_Quest_ArmorerDebt;
        public static QuestScriptDef RM_Quest_ImperialPrisonBreak;
        public static IncidentDef RM_BlackstarPrisonBreakOffer;
        public static RecipeDef RM_Recipe_ArmorerMeltBeskar;
        public static SitePartDef RM_ImperialDetentionPost;
        public static WorkGiverDef RM_DoBillsArmorerForge;
        static ArmorerDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(ArmorerDefOf)); }
    }

    [StaticConstructorOnStartup]
    public static class ArmorerStartup
    {
        public static int GeneratedRecipes;

        static ArmorerStartup()
        {
            Harmony h = new Harmony("mandrake.rut.beskararmorer");
            PatchApplier.Apply(h, typeof(ArmorerStartup).Assembly, "BeskarArmorer", "RimMandrake.Utinni.BeskarArmorer");
            Patch_ArmourySmeltAmounts.TryApply(h);
            GenerateRecipes();
            ApplySettings();
        }

        public static void ApplySettings()
        {
            ArmorerDefOf.RM_BlackstarPrisonBreakOffer.earliestDay = BeskarArmorerSettings.prisonBreakEarliestDay;
            ArmorerDefOf.RM_BlackstarPrisonBreakOffer.minRefireDays = BeskarArmorerSettings.prisonBreakRefireDays;
        }

        private static IEnumerable<ThingDef> MeltInputs()
        {
            ThingDef ingot = ArmorerDefOf.KOTOR_IngotBeskar;
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d == ingot) continue;                                         // already melted: the tribute is taken once
                if (d.category != ThingCategory.Item) continue;
                if (BeskarUtil.DefCarries(d)) yield return d;
                else if ((d.IsApparel || d.IsWeapon) && d.MadeFromStuff && ingot.stuffProps != null && ingot.stuffProps.CanMake(d)) yield return d;
            }
        }

        /// <summary>Spec 2.2: the melt recipe's filter, and one RM_Reforge_ recipe per beskar product. Runs after every def is loaded,
        /// which is why it is not XML: the list is whatever gear this mod list holds.</summary>
        private static void GenerateRecipes()
        {
            ThingDef ingot = ArmorerDefOf.KOTOR_IngotBeskar;
            RecipeDef melt = ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar;
            foreach (ThingDef d in MeltInputs())
            {
                melt.fixedIngredientFilter.SetAllow(d, true);
                melt.ingredients[0].filter.SetAllow(d, true);
                melt.defaultIngredientFilter?.SetAllow(d, true);
            }
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading.ToList())
            {
                if (!(d.IsApparel || d.IsWeapon) || d.category != ThingCategory.Item) continue;
                int cost = d.costList == null ? 0 : d.costList.Where(c => BeskarUtil.IsMaterial(c.thingDef)).Sum(c => c.count);
                bool stuffed = cost == 0 && d.MadeFromStuff && d.CostStuffCount > 0 && ingot.stuffProps != null && ingot.stuffProps.CanMake(d);
                if (cost == 0 && !stuffed) continue;
                RecipeDef r = MakeReforge(d, stuffed ? d.CostStuffCount : cost, stuffed, ingot);
                DefGenerator.AddImpliedDef(r);
                r.ResolveReferences();
                GeneratedRecipes++;
            }
            AccessTools.Field(typeof(ThingDef), "allRecipesCached").SetValue(ArmorerDefOf.RM_ArmorerForge, null);
            Log.Message("[BeskarArmorer] generated " + GeneratedRecipes + " reforge recipes; melt takes "
                + melt.fixedIngredientFilter.AllowedDefCount + " defs");
        }

        private static RecipeDef MakeReforge(ThingDef product, int count, bool stuffed, ThingDef ingot)
        {
            RecipeDef melt = ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar;
            IngredientCount ing = new IngredientCount();
            ing.filter.SetAllow(ingot, true);
            ing.SetBaseCount(count);
            ThingFilter fix = new ThingFilter();
            fix.SetAllow(ingot, true);
            return new RecipeDef
            {
                defName = "RM_Reforge_" + product.defName,
                label = "reforge " + product.label,
                description = "The Armorer reforges " + count + " beskar into " + product.label + ".",
                jobString = "Reforging " + product.label + ".",
                modContentPack = melt.modContentPack,
                workAmount = product.IsApparel ? 45000f : 22000f,
                workSpeedStat = melt.workSpeedStat,
                workSkill = SkillDefOf.Crafting,
                effectWorking = melt.effectWorking,
                soundWorking = melt.soundWorking,
                ingredients = new List<IngredientCount> { ing },
                fixedIngredientFilter = fix,
                productHasIngredientStuff = stuffed,
                products = new List<ThingDefCountClass> { new ThingDefCountClass(product, 1) },
                recipeUsers = new List<ThingDef> { ArmorerDefOf.RM_ArmorerForge },
            };
        }
    }
}
