using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class NotifyGenesChanges
{
	[HarmonyPatch(typeof(Pawn_GeneTracker), "Notify_GenesChanged")]
	[HarmonyPostfix]
	public static void Notify_GenesChanged_Postfix(GeneDef addedOrRemovedGene, Pawn_GeneTracker __instance)
	{
		if (__instance?.pawn != null)
		{
			HumanoidPawnScaler.GetInvalidateLater(__instance.pawn, 1);
			GenderMethods.UpdatePawnHairAndHeads(__instance.pawn);
			object obj;
			if (__instance == null)
			{
				obj = null;
			}
			else
			{
				Pawn pawn = __instance.pawn;
				obj = ((pawn == null) ? null : pawn.Drawer?.renderer);
			}
			if (obj != null && ((Thing)__instance.pawn).Spawned)
			{
				__instance.pawn.Drawer.renderer.SetAllGraphicsDirty();
			}
			HumanoidPawnScaler.GetInvalidateLater(__instance.pawn, 1);
		}
	}

	[HarmonyPatch(typeof(Gene), "OverrideBy")]
	[HarmonyPrefix]
	public static void Gene_OverrideBy_Patch(Gene __instance, Gene overriddenBy)
	{
		if (!BigSmall.performScaleCalculations || overriddenBy == __instance.overriddenByGene || (overriddenBy != null && __instance.overriddenByGene != null))
		{
			return;
		}
		bool disabled = overriddenBy != null;
		if (__instance != null && __instance.pawn != null && ((Thing)__instance.pawn).Spawned)
		{
			GeneEffectManager.GainOrRemovePassion(disabled, __instance);
			GeneEffectManager.GainOrRemoveAbilities(disabled, __instance);
			GeneEffectManager.ApplyForcedTraits(disabled, __instance);
			if (__instance?.pawn != null)
			{
				HumanoidPawnScaler.GetCache(__instance.pawn, forceRefresh: false, canRegenerate: true, 1);
			}
		}
	}

	[HarmonyPatch(typeof(Gene), "PostRemove")]
	[HarmonyPostfix]
	public static void Gene_PostRemovePatch(Gene __instance)
	{
		if (PawnGenerator.IsBeingGenerated(__instance.pawn) || !__instance.Active)
		{
			return;
		}
		HumanoidPawnScaler.GetInvalidateLater(__instance.pawn);
		if (__instance.Active)
		{
			GeneRequestThingSwap(__instance, state: false);
		}
		List<PawnExtension> list = __instance.def.ExtensionsOnDef<PawnExtension, GeneDef>((List<Type>)null, (List<Type>)null, doSort: true);
		if (!GenList.NullOrEmpty<PawnExtension>((IList<PawnExtension>)list))
		{
			return;
		}
		Pawn pawn = __instance.pawn;
		if (!GenCollection.Any<Gene>(pawn.genes.GenesListForReading, (Predicate<Gene>)((Gene x) => x.def == __instance.def && x != __instance)))
		{
			foreach (GeneDef geneDef in list.Where((PawnExtension x) => x.hiddenGenes != null).SelectMany((PawnExtension x) => x.hiddenGenes))
			{
				foreach (Gene item in pawn.genes.GenesListForReading.Where((Gene x) => x.def == geneDef).ToList())
				{
					pawn.genes.RemoveGene(item);
				}
			}
		}
		HumanoidPawnScaler.GetInvalidateLater(__instance.pawn);
	}

	[HarmonyPatch(typeof(Gene), "PostAdd")]
	[HarmonyPostfix]
	public static void Gene_PostAddPatch(Gene __instance)
	{
		Pawn val = __instance?.pawn;
		if (val?.genes == null)
		{
			return;
		}
		HumanoidPawnScaler.GetInvalidateLater(__instance.pawn);
		bool flag = false;
		List<PawnExtension> list = __instance.def.ExtensionsOnDef<PawnExtension, GeneDef>((List<Type>)null, (List<Type>)null, doSort: true);
		bool flag2 = GenCollection.Any<Gene>(val.genes.Xenogenes, (Predicate<Gene>)((Gene x) => x == __instance));
		foreach (GeneDef item in list.SelectMany((PawnExtension x) => x.hiddenGenes))
		{
			val.genes.AddGene(item, flag2);
		}
		if (GenCollection.Any<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension x) => x.FrequentUpdate)))
		{
			flag = true;
		}
		if (__instance.Active)
		{
			GeneRequestThingSwap(__instance, state: true);
		}
		if (flag)
		{
			BigAndSmallCache.frequentUpdateGenes[__instance] = true;
		}
		HumanoidPawnScaler.GetInvalidateLater(__instance.pawn);
	}

	public static void GeneRequestThingSwap(Gene gene, bool state)
	{
		List<PawnExtension> allPawnExtensionsOnGene = gene.def.GetAllPawnExtensionsOnGene();
		if (GenCollection.Any<PawnExtension>(allPawnExtensionsOnGene, (Predicate<PawnExtension>)((PawnExtension x) => x.thingDefSwap != null)))
		{
			ThingDef swapTarget = (from x in allPawnExtensionsOnGene
				where x.thingDefSwap != null
				select x.thingDefSwap).First();
			gene.pawn.SwapThingDef(swapTarget, state, 0, force: false, gene);
		}
	}

	[HarmonyPatch(typeof(Gene), "ExposeData")]
	[HarmonyPostfix]
	public static void Gene_ExposeDataPatch(Gene __instance)
	{
		if (__instance?.pawn != null && GenCollection.Any<PawnExtension>(__instance.def.GetAllPawnExtensionsOnGene(), (Predicate<PawnExtension>)((PawnExtension x) => x.FrequentUpdate)))
		{
			BigAndSmallCache.frequentUpdateGenes[__instance] = ((__instance != null) ? new bool?(__instance.Active) : ((bool?)null));
		}
	}
}
