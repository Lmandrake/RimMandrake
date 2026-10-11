// CANON_MATERIALS_BUILD_1 L7: smelting beskar, or anything made of it, gives lesser ores (steel and a steel slag chunk), never beskar.
//
// Why C#: Thing.SmeltProducts (decompiled 1.6, Verse/Thing.cs) returns 25% of each cost-list entry whose def is smeltable, plus the
// item def's own fixed smeltProducts. The stuff is per THING, so no XML on the item def can say "steel when made of beskar". And
// Patches/RSW_BeskarNeverReforged.xml sets both Outer Rim beskars smeltable=false (KOTOR_IngotBeskar already is), which by
// Thing.Smeltable (MadeFromStuff -> Stuff.smeltable) also made beskar-made gear unsmeltable at all. Two postfixes:
//   * Thing.Smeltable getter: beskar-made gear is smeltable again (relics stay unsmeltable, as vanilla);
//   * Thing.SmeltProducts: drops any beskar the vanilla list still yields, then adds steel at the vanilla share of the beskar
//     cost plus one slag chunk (RSW_MaterialsKernel.LesserOres; amounts PROVISIONAL).
// Fail-closed: with the patch missing or the setting off, beskar gear is simply not smeltable and nothing returns beskar.
// No Harmony-free route exists: the only engine seam is the item's virtual SmeltProducts, and a separate "melt beskar" bill
// with a RecipeWorker would still leave the vanilla smelt bills unable to take beskar gear.
// Proof: prove_canon_materials.py (L7 lesser ores) and the Armoury fuzz family `materials`.
using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Armoury.CanonMaterials
{
    [StaticConstructorOnStartup]
    public static class RSW_BeskarSmelt
    {
        static RSW_BeskarSmelt()
        {
            PatchApplier.Apply(new Harmony("mandrake.rsw.armoury.canonmaterials"), typeof(RSW_BeskarSmelt).Assembly,
                "CanonMaterials", "RimMandrake.StarWars.Armoury.CanonMaterials");
        }

        public static int BeskarInCost(Thing thing)
        {
            if (thing == null || thing.def == null) return 0;
            List<ThingDefCountClass> cost = thing.def.CostListAdjusted(thing.Stuff, false);
            int n = 0;
            if (cost == null) return 0;
            for (int i = 0; i < cost.Count; i++)
                if (cost[i].thingDef != null && RSW_MaterialsKernel.IsBeskar(cost[i].thingDef.defName)) n += cost[i].count;
            return n;
        }
    }

    [HarmonyPatch(typeof(Thing), nameof(Thing.Smeltable), MethodType.Getter)]
    [PatchFeature("Beskar smelts into lesser ores", typeof(RSW_ArmourySettings), nameof(RSW_ArmourySettings.beskarLesserOresEnabled))]
    internal static class Patch_Thing_Smeltable_Beskar
    {
        internal static void Postfix(Thing __instance, ref bool __result)
        {
            if (__result || !RSW_ArmourySettings.beskarLesserOresEnabled || __instance?.def == null) return;
            ThingDef stuff = __instance.Stuff;
            if (stuff == null || !RSW_MaterialsKernel.IsBeskar(stuff.defName)) return;
            __result = RSW_MaterialsKernel.Smeltable(false, true, __instance.IsRelic(), __instance.def.smeltable, __instance.def.MadeFromStuff, stuff.defName);
        }
    }

    [HarmonyPatch(typeof(Thing), nameof(Thing.SmeltProducts))]
    [PatchFeature("Beskar smelts into lesser ores", typeof(RSW_ArmourySettings), nameof(RSW_ArmourySettings.beskarLesserOresEnabled))]
    internal static class Patch_Thing_SmeltProducts_Beskar
    {
        internal static IEnumerable<Thing> Postfix(IEnumerable<Thing> __result, Thing __instance)
        {
            bool on = RSW_ArmourySettings.beskarLesserOresEnabled;
            foreach (Thing t in __result)
            {
                if (on && t?.def != null && RSW_MaterialsKernel.IsBeskar(t.def.defName)) continue;
                yield return t;
            }
            if (!on) yield break;
            RSW_MaterialsKernel.Lesser l = RSW_MaterialsKernel.LesserOres(RSW_BeskarSmelt.BeskarInCost(__instance), GenMath.RoundRandom);
            if (l.Steel > 0)
            {
                Thing steel = ThingMaker.MakeThing(ThingDefOf.Steel);
                steel.stackCount = l.Steel;
                yield return steel;
            }
            for (int i = 0; i < l.Slag; i++) yield return ThingMaker.MakeThing(ThingDefOf.ChunkSlagSteel);
        }
    }
}
