// BESKAR_ARMORER_QUEST_1 spec 5.2 and the harm watcher (2.3). Every patch tests modEnabled, so the whole mod off changes nothing.
using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.BeskarArmorer
{
    internal static class BillGate
    {
        public static bool AtForge(Bill bill) { return bill?.billStack?.billGiver is Thing t && t.def == ArmorerDefOf.RM_ArmorerForge; }

        // Smelting or burning makes nothing OF the beskar, so it is no reforge; L6 needs the smelter open.
        public static bool SmeltsOrDestroys(RecipeDef r)
        {
            return r != null && ((r.specialProducts != null && r.specialProducts.Contains(SpecialProductType.Smelted)) || r.products.NullOrEmpty());
        }
    }

    [HarmonyPatch(typeof(Bill), nameof(Bill.IsFixedOrAllowedIngredient), new[] { typeof(Thing) })]
    [PatchFeature("No colony bill consumes beskar", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.modEnabled))]
    internal static class Patch_Bill_Ingredient_Thing
    {
        internal static void Postfix(Bill __instance, Thing thing, ref bool __result)
        {
            if (!__result) return;
            __result = ArmorerKernel.BillMayConsume(BeskarArmorerSettings.modEnabled, BeskarUtil.Carries(thing), BillGate.AtForge(__instance), BillGate.SmeltsOrDestroys(__instance.recipe));
            // a Metallic gear def passes the melt filter whatever it is made of: at her forge the melt takes only what carries beskar
            if (__result && BeskarArmorerSettings.modEnabled && __instance.recipe == ArmorerDefOf.RM_Recipe_ArmorerMeltBeskar && !BeskarUtil.Carries(thing)) __result = false;
        }
    }

    [HarmonyPatch(typeof(Bill), nameof(Bill.IsFixedOrAllowedIngredient), new[] { typeof(ThingDef) })]
    [PatchFeature("No colony bill consumes beskar", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.modEnabled))]
    internal static class Patch_Bill_Ingredient_Def
    {
        internal static void Postfix(Bill __instance, ThingDef def, ref bool __result)
        {
            if (!__result) return;
            __result = ArmorerKernel.BillMayConsume(BeskarArmorerSettings.modEnabled, BeskarUtil.DefCarries(def), BillGate.AtForge(__instance), BillGate.SmeltsOrDestroys(__instance.recipe));
        }
    }

    [HarmonyPatch(typeof(Bill), nameof(Bill.PawnAllowedToStartAnew))]
    [PatchFeature("Only the Armorer works her forge", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.modEnabled))]
    internal static class Patch_Bill_PawnAllowed
    {
        internal static void Postfix(Bill __instance, Pawn p, ref bool __result)
        {
            if (!__result) return;
            __result = ArmorerKernel.MayWorkForge(BeskarArmorerSettings.modEnabled, BillGate.AtForge(__instance), p.health.hediffSet.HasHediff(ArmorerDefOf.RM_ArmorerOfTheTribe));
        }
    }

    /// <summary>Spec 5.2 patch 3. Runs last so it sees whatever earlier postfixes left. No RimWorld class overrides SmeltProducts
    /// (decompiled 1.6, grep of the whole assembly, 2026-11-01), so base always runs.</summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.SmeltProducts))]
    [PatchFeature("Smelting beskar yields steel and slag", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.modEnabled))]
    internal static class Patch_Thing_SmeltProducts
    {
        [HarmonyPriority(Priority.Last)]
        internal static IEnumerable<Thing> Postfix(IEnumerable<Thing> __result, Thing __instance)
        {
            bool on = BeskarArmorerSettings.modEnabled;
            foreach (Thing t in __result)
            {
                if (on && BeskarUtil.IsMaterial(t?.def)) continue;
                yield return t;
            }
            if (!on) yield break;
            int mass = BeskarUtil.Mass(__instance);
            int steelCount = ArmorerKernel.SmeltSteel(mass, BeskarArmorerSettings.smeltSteelRatio);
            if (steelCount > 0)
            {
                Thing steel = ThingMaker.MakeThing(ThingDefOf.Steel);
                steel.stackCount = steelCount;
                yield return steel;
            }
            for (int i = 0; i < ArmorerKernel.SmeltSlag(mass); i++) yield return ThingMaker.MakeThing(ThingDefOf.ChunkSlagSteel);
        }
    }

    /// <summary>The Armoury's own beskar smelt (CANON_MATERIALS_BUILD_1 L7, RSW_BeskarSmelt) adds its provisional amounts on the
    /// same seam. With this mod on, those amounts stand down so the owner's ceil(n/3) plus one slag is the only yield: its
    /// BeskarInCost is the one input to those amounts and nothing else calls it. Applied by name: the Armoury is not a compile
    /// reference, and with this mod off the Armoury's behaviour is untouched.</summary>
    internal static class Patch_ArmourySmeltAmounts
    {
        public static void TryApply(Harmony h)
        {
            System.Reflection.MethodInfo m = AccessTools.Method("RimMandrake.StarWars.Armoury.CanonMaterials.RSW_BeskarSmelt:BeskarInCost");
            if (m == null) { Log.Warning("[BeskarArmorer] the Armoury's smelt seam is missing; its yield is not stood down"); return; }
            h.Patch(m, prefix: new HarmonyMethod(typeof(Patch_ArmourySmeltAmounts), nameof(Prefix)));
        }

        internal static bool Prefix(ref int __result)
        {
            if (!BeskarArmorerSettings.modEnabled) return true;
            __result = 0;
            return false;
        }
    }

    /// <summary>Route 1 trigger (spec 3.1), a postfix of its own so RaidRedesigner's stays untouched and either mod can be off.</summary>
    [HarmonyPatch(typeof(GenGuest), nameof(GenGuest.PrisonerRelease))]
    [PatchFeature("Freeing a Mandalorian starts the debt quest", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.routeOneEnabled))]
    internal static class Patch_PrisonerRelease
    {
        internal static void Prefix(Pawn p, out bool __state) { __state = p != null && p.IsPrisonerOfColony; }

        internal static void Postfix(Pawn p, bool __state)
        {
            if (p == null || !BeskarArmorerSettings.modEnabled) return;
            Current.Game.GetComponent<RM_ArmorerState>()?.TryStartRouteOne(p, __state);
        }
    }

    /// <summary>The harm watcher, spec 2.3. The map is read before the damage: a destroyed building has none after.</summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.TakeDamage))]
    [PatchFeature("Harming the Armorer loses the covert", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.modEnabled))]
    internal static class Patch_Thing_TakeDamage
    {
        internal static void Prefix(Thing __instance, out Map __state) { __state = __instance.MapHeld; }

        internal static void Postfix(Thing __instance, DamageInfo dinfo, Map __state)
        {
            if (!BeskarArmorerSettings.modEnabled || dinfo.Instigator?.Faction != Faction.OfPlayer) return;
            RM_ArmorerCovert covert = RM_ArmorerState.Covert;
            if (covert == null || covert.lost) return;
            bool castMember = __instance is Pawn p && covert.cast.Contains(p);
            bool building = __instance is Building && __instance.Faction != Faction.OfPlayer && covert.HasMap && __state == covert.Map;
            if (castMember || building) RM_ArmorerState.Harm("damage to " + __instance.LabelShort);
        }
    }

    [HarmonyPatch(typeof(Pawn_GuestTracker), nameof(Pawn_GuestTracker.CapturedBy))]
    [PatchFeature("Harming the Armorer loses the covert", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.modEnabled))]
    internal static class Patch_CapturedBy
    {
        internal static void Postfix(Pawn ___pawn, Faction by)
        {
            RM_ArmorerCovert covert = RM_ArmorerState.Covert;
            if (BeskarArmorerSettings.modEnabled && by == Faction.OfPlayer && covert != null && !covert.lost && covert.cast.Contains(___pawn))
                RM_ArmorerState.Harm("capture of " + ___pawn.LabelShort);
        }
    }

    [HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
    [PatchFeature("Harming the Armorer loses the covert", typeof(BeskarArmorerSettings), nameof(BeskarArmorerSettings.modEnabled))]
    internal static class Patch_Pawn_Kill
    {
        internal static void Postfix(Pawn __instance)
        {
            RM_ArmorerCovert covert = RM_ArmorerState.Covert;
            if (BeskarArmorerSettings.modEnabled && covert != null && !covert.lost && covert.cast.Contains(__instance)
                && covert.HasMap && covert.Map.mapPawns.FreeColonistsSpawnedCount > 0)
                RM_ArmorerState.Harm("death of " + __instance.LabelShort);
        }
    }
}
