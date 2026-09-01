using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

[HarmonyPatch]
public class DeathThoughtPatches
{
	[HarmonyPatch(typeof(PawnDiedOrDownedThoughtsUtility), "AppendThoughts_Relations")]
	[HarmonyPrefix]
	public static bool AppendThoughts_RelationsPrefix(Pawn victim, DamageInfo? dinfo, PawnDiedOrDownedThoughtsKind thoughtsKind, List<IndividualThoughtToAdd> outIndividualThoughts, List<ThoughtToAddToAll> outAllColonistsThoughts)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		if (victim != null && (int)thoughtsKind == 0)
		{
			BSCache cache = FastAcccess.GetCache(victim);
			if (cache != null && cache.isDrone)
			{
				try
				{
					foreach (Pawn item in PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive)
					{
						if (item != victim && item.needs != null && item.needs.mood != null && PawnUtility.ShouldGetThoughtAbout(item, victim) && (item.MentalStateDef != MentalStateDefOf.SocialFighting || ((MentalState_SocialFighting)item.MentalState).otherPawn != victim) && ((Thing)victim).Faction == Faction.OfPlayerSilentFail && victim.HostFaction != ((Thing)item).Faction && !QuestUtility.IsQuestLodger(victim) && !victim.IsMutant && !victim.IsSlave)
						{
							outIndividualThoughts.Add(new IndividualThoughtToAdd(BSDefs.BS_DroneDied, item, victim, 1f, 1f));
						}
					}
				}
				catch
				{
				}
				return false;
			}
		}
		return true;
	}

	[HarmonyPatch(typeof(MemoryThoughtHandler), "TryGainMemory", new Type[]
	{
		typeof(Thought_Memory),
		typeof(Pawn)
	})]
	[HarmonyPrefix]
	public static void TryGainMemoryPrefix(MemoryThoughtHandler __instance, Thought_Memory newThought, Pawn otherPawn = null)
	{
		Pawn val = __instance?.pawn;
		if (val != null && newThought != null && otherPawn != null)
		{
			BSCache cache = FastAcccess.GetCache(val);
			if (cache != null && cache.isDrone)
			{
				newThought.durationTicksOverride = ((Thought)newThought).DurationTicks / 5;
			}
		}
	}
}
