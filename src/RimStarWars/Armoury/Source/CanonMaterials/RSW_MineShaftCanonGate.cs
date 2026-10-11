// CANON_MATERIALS_BUILD_1 L1/L7: Mines 2.0 (Cain.Mineshaft) must not sell a mine shaft for a material the canon design makes
// salvage-only (beskar, durasteel), never-mined (plasteel), or asteroid-only (doonium ore).
//
// Read from the installed mod's 1.6 source (workshop 2503894706, read-only): CreateRecipeDefs.Generate builds one RecipeDef per
// def that is mineable with a mineableThing and isResourceRock, whatever its scatter commonality; MinesAutomatedExtension.OnStartup
// adds one per def carrying a MineableSettings extension (LK's Outer Rim compat puts one on OuterRim_Beskar). Both run from
// [StaticConstructorOnStartup] and add to the DefDatabase in code, so an XML patch cannot reach them, and the mod's own
// "PatchOperationRemove means never create" reader only looks at Mines 2.0's own Patches folder.
//
// No Harmony: this forces both Mines constructors (idempotent: MineRecipes.EnsureBaseRecipesGenerated runs once; a class
// constructor runs once), then clears recipeUsers on every Mines recipe whose product is banned and drops the mine's cached
// recipe list, the same field Mines itself resets. The RecipeDefs stay in the DefDatabase so a save or the Mines settings
// window that names one still resolves. Keyed by PRODUCT, so a second rock or an extension recipe for the same material is caught.
// Not covered: a "custom resource" a player adds by hand in the Mines settings window during play.
// Proof: prove_canon_materials.py (L1 mine shafts) and the Armoury fuzz family `materials`.
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.CompilerServices;
using Verse;

namespace RimMandrake.StarWars.Armoury
{
    [StaticConstructorOnStartup]
    public static class RSW_MineShaftCanonGate
    {
        static RSW_MineShaftCanonGate()
        {
            Apply();
        }

        public static int Apply()
        {
            if (!RSW_ArmourySettings.mineShaftCanonGateEnabled) return 0;
            var baseGen = GenTypes.GetTypeInAnyAssembly("MinesAutomated.CreateRecipeDefs");
            if (baseGen == null) return 0;
            RuntimeHelpers.RunClassConstructor(baseGen.TypeHandle);
            var ext = GenTypes.GetTypeInAnyAssembly("MinesAutomatedExtension.OnStartup");
            if (ext != null) RuntimeHelpers.RunClassConstructor(ext.TypeHandle);

            var unlisted = new List<string>();
            var products = new List<string>();
            foreach (RecipeDef r in DefDatabase<RecipeDef>.AllDefsListForReading)
            {
                if (!RSW_MaterialsKernel.IsMineShaftRecipe(r.defName) || r.products == null) continue;
                products.Clear();
                foreach (ThingDefCountClass p in r.products) products.Add(p.thingDef?.defName);
                if (!RSW_MaterialsKernel.UnlistMineShaft(true, r.defName, products)) continue;
                r.recipeUsers?.Clear();
                unlisted.Add(r.defName);
            }
            if (unlisted.Count == 0) return 0;
            ThingDef mine = DefDatabase<ThingDef>.GetNamedSilentFail("MinesAutomated_ThingDef_Mine");
            FieldInfo cache = typeof(ThingDef).GetField("allRecipesCached", BindingFlags.Instance | BindingFlags.NonPublic);
            if (mine != null && cache != null) cache.SetValue(mine, null);
            Log.Message("[RSW Armoury] canon materials: unlisted " + unlisted.Count + " Mines 2.0 shaft recipe(s): " + string.Join(", ", unlisted));
            return unlisted.Count;
        }
    }
}
