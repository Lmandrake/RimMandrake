using System;
using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.StarWars.Armoury;
using RimWorld;
using UnityEngine;
using Verse;

namespace SecondaryMineableYield;

[StaticConstructorOnStartup]
public class SecondaryMineableYield
{
    static SecondaryMineableYield()
    {
        Log.Message("[SecondaryMineableYield] Now active");
        Harmony harmony = new Harmony("kaitorisenkou.SecondaryMineableYield");
        harmony.Patch(
            AccessTools.Method(typeof(Mineable), "TrySpawnYield", new Type[] { typeof(Map), typeof(bool), typeof(Pawn) }),
            postfix: new HarmonyMethod(typeof(SecondaryMineableYield), nameof(Patch_TrySpawnYield)));
        harmony.Patch(
            AccessTools.Method(typeof(Mineable), "PreApplyDamage"),
            postfix: new HarmonyMethod(typeof(SecondaryMineableYield), nameof(Patch_PreApplyDamage)));
        Log.Message("[SecondaryMineableYield] Harmony patch complete!");
    }

    public static void Patch_TrySpawnYield(Mineable __instance, float ___yieldPct, Map map, Pawn pawn)
    {
        if (!RSW_ArmourySettings.secondaryYieldEnabled)
        {
            return;
        }
        ModExtension_SecondaryMineableYield modExtension = __instance.def.GetModExtension<ModExtension_SecondaryMineableYield>();
        if (modExtension == null || !RSW_YieldKernel.Drops(Rand.Value, modExtension.mineableDropChance, RSW_ArmourySettings.secondaryYieldChance))
        {
            return;
        }
        List<float> weights = new List<float>(modExtension.entries.Count);
        foreach (SecondaryYieldEntry entry in modExtension.entries)
        {
            weights.Add(entry.randomWeight);
        }
        int pick = RSW_YieldKernel.Pick(weights, Rand.Value);
        if (pick < 0)
        {
            return;
        }
        SecondaryYieldEntry chosen = modExtension.entries[pick];
        int count = RSW_YieldKernel.Count(chosen.EffectiveMineableYield, RSW_ArmourySettings.secondaryYieldAmount, chosen.mineableYieldWasteable, ___yieldPct, GenMath.RoundRandom);
        Thing thing = ThingMaker.MakeThing(chosen.mineableThing);
        thing.stackCount = count;
        GenPlace.TryPlaceThing(thing, __instance.Position, map, ThingPlaceMode.Near, delegate(Thing t, int i)
        {
            if (pawn != null && pawn.Faction != Faction.OfPlayer && t.def.EverHaulable && !t.def.designateHaulable)
            {
                ForbidUtility.SetForbidden(t, true, false);
            }
        });
    }

    public static void Patch_PreApplyDamage(Mineable __instance, DamageInfo dinfo, bool absorbed)
    {
        ModExtension_SecondaryMineableYield modExtension = __instance.def.GetModExtension<ModExtension_SecondaryMineableYield>();
        Pawn instigator = dinfo.Instigator as Pawn;
        if (RSW_YieldKernel.CreditsMiner(RSW_ArmourySettings.secondaryYieldEnabled, absorbed, __instance.def.building.mineableThing != null,
            dinfo.Def == DamageDefOf.Mining, instigator != null, modExtension != null && !modExtension.entries.NullOrEmpty()))
        {
            __instance.Notify_TookMiningDamage(GenMath.RoundRandom(dinfo.Amount), instigator);
        }
    }
}
