using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(MemoryThoughtHandler), "TryGainMemory", new Type[]
{
	typeof(Thought_Memory),
	typeof(Pawn)
})]
public static class VanillaExpandedFramework_MemoryThoughtHandler_TryGainMemory_Patch
{
	private static void Postfix(MemoryThoughtHandler __instance, ref Thought_Memory newThought, Pawn otherPawn)
	{
		if (((Thought)newThought).pawn == null)
		{
			return;
		}
		ThoughtExtensions modExtension = ((Def)((Thought)newThought).def).GetModExtension<ThoughtExtensions>();
		if (modExtension != null && modExtension.removeThoughtsWhenAdded != null)
		{
			foreach (ThoughtDef item in modExtension.removeThoughtsWhenAdded)
			{
				__instance.pawn.needs.mood.thoughts.memories.RemoveMemoriesOfDef(item);
			}
		}
		float baseMoodEffect = ((Thought)newThought).CurStage.baseMoodEffect;
		float num = ((baseMoodEffect > 0f) ? StatExtension.GetStatValue((Thing)(object)__instance.pawn, VEFDefOf.VEF_PositiveThoughtDurationFactor, true, -1) : ((!(baseMoodEffect < 0f)) ? StatExtension.GetStatValue((Thing)(object)__instance.pawn, VEFDefOf.VEF_NeutralThoughtDurationFactor, true, -1) : StatExtension.GetStatValue((Thing)(object)__instance.pawn, VEFDefOf.VEF_NegativeThoughtDurationFactor, true, -1)));
		float num2 = num;
		newThought.durationTicksOverride = Mathf.RoundToInt((float)((Thought)newThought).DurationTicks * num2);
	}
}
