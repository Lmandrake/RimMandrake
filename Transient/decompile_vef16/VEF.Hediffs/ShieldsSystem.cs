using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using VEF.CacheClearing;
using Verse;

namespace VEF.Hediffs;

public static class ShieldsSystem
{
	public static Dictionary<Pawn, List<HediffComp_Draw>> HediffDrawsByPawn;

	private static bool drawPatchesApplied;

	private static bool shieldPatchesApplied;

	private static HarmonyMethod MyMethod(this string name)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Expected O, but got Unknown
		return new HarmonyMethod(typeof(ShieldsSystem), name, (Type[])null);
	}

	static ShieldsSystem()
	{
		HediffDrawsByPawn = new Dictionary<Pawn, List<HediffComp_Draw>>();
		ClearCaches.clearCacheTypes.Add(typeof(ShieldsSystem));
	}

	public static void ApplyDrawPatches()
	{
		if (!drawPatchesApplied)
		{
			drawPatchesApplied = true;
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "SpawnSetup", (Type[])null, (Type[])null), (HarmonyMethod)null, "OnPawnSpawn".MyMethod(), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "DeSpawn", (Type[])null, (Type[])null), (HarmonyMethod)null, "OnPawnDespawn".MyMethod(), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "DrawAt", (Type[])null, (Type[])null), (HarmonyMethod)null, "PawnPostDrawAt".MyMethod(), (HarmonyMethod)null, (HarmonyMethod)null);
		}
	}

	public static void ApplyShieldPatches()
	{
		if (!shieldPatchesApplied)
		{
			shieldPatchesApplied = true;
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(ThingWithComps), "PreApplyDamage", (Type[])null, (Type[])null), (HarmonyMethod)null, "PostPreApplyDamage".MyMethod(), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(Verb), "CanHitTarget", (Type[])null, (Type[])null), (HarmonyMethod)null, "CanHitTargetFrom_Postfix".MyMethod(), (HarmonyMethod)null, (HarmonyMethod)null);
		}
	}

	public static void OnPawnSpawn(Pawn __instance)
	{
		if (HediffDrawsByPawn.ContainsKey(__instance))
		{
			HediffDrawsByPawn.Remove(__instance);
		}
		HediffDrawsByPawn.Add(__instance, __instance.health.hediffSet.hediffs.OfType<HediffWithComps>().SelectMany((HediffWithComps hediff) => hediff.comps).OfType<HediffComp_Draw>()
			.ToList());
	}

	public static void OnPawnDespawn(Pawn __instance)
	{
		HediffDrawsByPawn.Remove(__instance);
	}

	public static void PawnPostDrawAt(Pawn __instance, Vector3 drawLoc)
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		if (HediffDrawsByPawn.TryGetValue(__instance, out var value))
		{
			for (int i = 0; i < value.Count; i++)
			{
				value[i].DrawAt(drawLoc);
			}
		}
	}

	public static void PostPreApplyDamage(ThingWithComps __instance, ref DamageInfo dinfo, ref bool absorbed)
	{
		if (absorbed)
		{
			return;
		}
		Pawn val = (Pawn)(object)((__instance is Pawn) ? __instance : null);
		if (val == null)
		{
			return;
		}
		foreach (HediffComp_Shield item in val.health.hediffSet.hediffs.OfType<HediffWithComps>().SelectMany((HediffWithComps hediff) => hediff.comps).OfType<HediffComp_Shield>())
		{
			item.PreApplyDamage(ref dinfo, ref absorbed);
			if (absorbed)
			{
				break;
			}
		}
	}

	public static void CanHitTargetFrom_Postfix(Verb __instance, ref bool __result)
	{
		if (__result && __instance.CasterIsPawn)
		{
			Pawn casterPawn = __instance.CasterPawn;
			if (casterPawn != null && casterPawn.health.hediffSet.hediffs.OfType<HediffWithComps>().SelectMany((HediffWithComps hediff) => hediff.comps).OfType<HediffComp_Shield>()
				.Any((HediffComp_Shield shield) => !shield.AllowVerbCast(__instance)))
			{
				__result = false;
			}
		}
	}
}
