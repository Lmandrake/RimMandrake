using System.Collections.Generic;
using System.Reflection;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_PIT_SOLVENT_1: the slime pit's solvent recipes are ordinary RecipeDefs
    // (Defs/ThingDefs_Buildings/SlimePitSolvent.xml). This applies the Mod Settings switch: off =>
    // the recipes are removed from RM_SlimePit's recipeUsers and its recipe cache is rebuilt, so
    // the bench offers only the original slime-to-meal bill. Existing bills of a removed recipe
    // stay in the list but cannot be started (RecipeDef no longer a user of the bench).
    [StaticConstructorOnStartup]
    public static class PitSolvent
    {
        static readonly string[] Recipes = { "RM_Render_Toxipotato", "RM_Render_TwistedMeat" };

        static PitSolvent()
        {
            Apply();
        }

        public static void Apply()
        {
            ThingDef pit = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SlimePit");
            if (pit == null) return;
            foreach (string name in Recipes)
            {
                RecipeDef r = DefDatabase<RecipeDef>.GetNamedSilentFail(name);
                if (r == null) continue;
                if (r.recipeUsers == null) r.recipeUsers = new List<ThingDef>();
                bool has = r.recipeUsers.Contains(pit);
                if (SlimeSettings.pitSolvent && !has) r.recipeUsers.Add(pit);
                else if (!SlimeSettings.pitSolvent && has) r.recipeUsers.Remove(pit);
            }
            FieldInfo cache = typeof(ThingDef).GetField("allRecipesCached", BindingFlags.NonPublic | BindingFlags.Instance);
            if (cache != null) cache.SetValue(pit, null);
        }
    }
}
