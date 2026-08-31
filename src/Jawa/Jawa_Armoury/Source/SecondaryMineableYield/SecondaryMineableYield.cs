using System;
using HarmonyLib;
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
        ModExtension_SecondaryMineableYield modExtension = __instance.def.GetModExtension<ModExtension_SecondaryMineableYield>();
        if (modExtension == null || Rand.Value > modExtension.mineableDropChance)
        {
            return;
        }
        float remaining = modExtension.GetWeightSum;
        float roll = Rand.Value * remaining;
        SecondaryYieldEntry chosen = null;
        foreach (SecondaryYieldEntry entry in modExtension.entries)
        {
            remaining -= entry.randomWeight;
            if (remaining < roll)
            {
                chosen = entry;
                break;
            }
        }
        if (chosen == null)
        {
            return;
        }
        int count = Mathf.Max(1, chosen.EffectiveMineableYield);
        if (chosen.mineableYieldWasteable)
        {
            count = Mathf.Max(1, GenMath.RoundRandom(count * ___yieldPct));
        }
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
        if (!absorbed && __instance.def.building.mineableThing == null && dinfo.Def == DamageDefOf.Mining && dinfo.Instigator != null && dinfo.Instigator is Pawn instigator)
        {
            ModExtension_SecondaryMineableYield modExtension = __instance.def.GetModExtension<ModExtension_SecondaryMineableYield>();
            if (modExtension != null && !modExtension.entries.NullOrEmpty())
            {
                __instance.Notify_TookMiningDamage(GenMath.RoundRandom(dinfo.Amount), instigator);
            }
        }
    }
}
