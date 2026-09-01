using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch]
public static class ThingIngestingPatches
{
	public static Pawn pawn;

	public static List<ThingDef> extraHumanMeatDefs;

	private static IEnumerable<MethodBase> TargetMethods()
	{
		yield return AccessTools.DeclaredMethod(typeof(Thing), "Ingested", (Type[])null, (Type[])null);
		yield return AccessTools.DeclaredMethod(typeof(FoodUtility), "ThoughtsFromIngesting", (Type[])null, (Type[])null);
	}

	private static void Prefix(Pawn ingester, out bool __state)
	{
		if (pawn == null && ingester != null)
		{
			__state = true;
			pawn = ingester;
			StaticCollectionsClass.defs_treated_as_human_meat.TryGetValue((Thing)(object)ingester, out extraHumanMeatDefs);
		}
		else
		{
			__state = false;
		}
	}

	private static void Finalizer(bool __state)
	{
		if (__state)
		{
			pawn = null;
			extraHumanMeatDefs = null;
		}
	}
}
