using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class GeneratePawns_Patch
{
	private static bool runningGroupMaker;

	private static Pawn lastTouchedPawn;

	[HarmonyPostfix]
	[HarmonyPatch(typeof(PawnGenerator), "GeneratePawn", new Type[]
	{
		typeof(PawnKindDef),
		typeof(Faction),
		typeof(PlanetTile)
	})]
	public static void GeneratePawnPostfix(ref Pawn __result, PawnKindDef kindDef, Faction faction)
	{
		if (__result != null && !runningGroupMaker && lastTouchedPawn != __result)
		{
			lastTouchedPawn = __result;
			ModifyGeneratedPawn(changed: false, ref __result, singlePawn: true);
		}
	}

	[HarmonyPostfix]
	[HarmonyPatch(typeof(PawnGenerator), "GeneratePawn", new Type[] { typeof(PawnGenerationRequest) })]
	public static void GeneratePawnPostfix(ref Pawn __result, PawnGenerationRequest request)
	{
		if (__result != null && !runningGroupMaker && lastTouchedPawn != __result)
		{
			lastTouchedPawn = __result;
			ModifyGeneratedPawn(changed: false, ref __result, singlePawn: true);
		}
	}

	[HarmonyPostfix]
	[HarmonyPatch(typeof(PawnGroupMakerUtility), "GeneratePawns")]
	public static void GeneratePawnsPatch(PawnGroupMakerParms parms, bool warnOnZeroResults, ref IEnumerable<Pawn> __result)
	{
		runningGroupMaker = true;
		try
		{
			bool flag = false;
			List<Pawn> list = __result.ToList();
			for (int num = list.Count - 1; num >= 0; num--)
			{
				Pawn member = list[num];
				if (member != null && lastTouchedPawn != member)
				{
					lastTouchedPawn = member;
					flag = ModifyGeneratedPawn(flag, ref member);
				}
			}
			if (flag)
			{
				__result = list;
			}
		}
		finally
		{
			runningGroupMaker = false;
		}
	}

	private static bool ModifyGeneratedPawn(bool changed, ref Pawn member, bool singlePawn = false)
	{
		try
		{
			if (HumanoidPawnScaler.GetCache(member, forceRefresh: true) != null)
			{
				changed = true;
				try
				{
					member = TryModifyPawn(member, singlePawn);
				}
				catch (Exception ex)
				{
					Log.Warning($"BigAndSmall (GeneratePawns): Failed the TryModifyPawn for {member.Name} ({((Entity)member).Label}): + {ex.Message}\n{ex.StackTrace}");
				}
				try
				{
					RemoveInvalidThings(member);
				}
				catch (Exception ex2)
				{
					Log.Warning($"BigAndSmall (GeneratePawns): Failed to remove invalid apparel for {member.Name} ({((Entity)member).Label}): + {ex2.Message}\n{ex2.StackTrace}");
				}
			}
		}
		catch (Exception ex3)
		{
			Log.Warning($"BigAndSmall (GeneratePawns): Failed to pregenerate pawn cache for {member.Name} ({((Entity)member).Label}): {ex3.Message}\n{ex3.StackTrace}");
		}
		try
		{
			changed = GeneratePilots(changed, member);
		}
		catch (Exception ex4)
		{
			Log.Error(string.Format("BigAndSmall: Error in {0} generating pilot for {1}:\n{2}\n{3}", "ModifyGeneratedPawn", member.Name, ex4.Message, ex4.StackTrace));
		}
		return changed;
	}

	private static bool GeneratePilots(bool changed, Pawn member)
	{
		object obj;
		if (member == null)
		{
			obj = null;
		}
		else
		{
			PawnKindDef kindDef = member.kindDef;
			obj = ((kindDef != null) ? ((Def)kindDef).GetModExtension<PilotExtension>() : null);
		}
		PilotExtension pilotExtension2 = (PilotExtension)obj;
		if (pilotExtension2 != null)
		{
			changed = GeneratePilot(changed, member, pilotExtension2);
		}
		else
		{
			object obj2;
			if (member == null)
			{
				obj2 = null;
			}
			else
			{
				Pawn_GeneTracker genes = member.genes;
				if (genes == null)
				{
					obj2 = null;
				}
				else
				{
					XenotypeDef xenotype = genes.Xenotype;
					obj2 = ((xenotype != null) ? ((Def)xenotype).GetModExtension<PilotExtension>() : null);
				}
			}
			PilotExtension pilotExtension3 = (PilotExtension)obj2;
			if (pilotExtension3 != null)
			{
				changed = GeneratePilot(changed, member, pilotExtension3);
			}
		}
		return changed;
		static bool GeneratePilot(bool changed, Pawn member, PilotExtension pilotExtension)
		{
			try
			{
				pilotExtension.GeneratePilot(member);
				changed = true;
			}
			catch (Exception ex)
			{
				Log.Error($"BigAndSmall: Error generating pilot for {member.Name}: {ex.Message}\n{ex.StackTrace}");
			}
			return changed;
		}
	}

	private static Pawn TryModifyPawn(Pawn member, bool singlePawn = false)
	{
		if (member.kindDef == null)
		{
			return member;
		}
		foreach (PawnKindExtension item in member.kindDef.ExtensionsOnDef<PawnKindExtension, PawnKindDef>((List<Type>)null, (List<Type>)null, doSort: true))
		{
			member = item.Execute(member, singlePawn);
		}
		return TryModifyHumanlike(member);
	}

	private static Pawn TryModifyHumanlike(Pawn member)
	{
		if (member != null)
		{
			RaceProperties raceProps = member.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) == true)
			{
				Pawn_GeneTracker genes = member.genes;
				if (((genes != null) ? genes.Xenotype : null) == null)
				{
					return member;
				}
				XenotypeExtension modExtension = ((Def)member.genes.Xenotype).GetModExtension<XenotypeExtension>();
				if (modExtension != null && modExtension.setRace != null)
				{
					try
					{
						member.SwapThingDef(modExtension.setRace, state: true, -100);
					}
					catch (Exception ex)
					{
						Log.Error($"BigAndSmall: Error swapping thingdef for {((member != null) ? member.Name : null)}: {ex.Message}. Skipping.");
					}
				}
				TrySetInfiltrator(member);
				return member;
			}
		}
		return member;
	}

	private static void TrySetInfiltrator(Pawn member)
	{
		if (Faction.OfPlayerSilentFail == null || (((Thing)(member?)).def).IsHumanlikeAnimal())
		{
			return;
		}
		float inflitratorChance = BigSmallMod.settings.inflitratorChance;
		if (Rand.Chance(0.1f))
		{
			inflitratorChance = Mathf.Min(inflitratorChance * Rand.Range(1f, 10f), 1f - (1f - inflitratorChance) / 2f);
		}
		bool flag = Rand.Chance(BigSmallMod.settings.inflitratorChance);
		if (member != null)
		{
			Pawn_AgeTracker ageTracker = member.ageTracker;
			if (((ageTracker != null) ? new int?(ageTracker.AgeBiologicalYears) : ((int?)null)) < 3)
			{
				return;
			}
		}
		bool flag2 = member != null && FactionUtility.HostileTo(((Thing)member).Faction, Faction.OfPlayerSilentFail) && BigSmallMod.settings.inflitratorRaidChance > BigAndSmallCache.globalRandNum;
		if (!(flag || flag2) || member.IsMutant)
		{
			return;
		}
		try
		{
			Pawn_GeneTracker genes = member.genes;
			bool flag3 = ((genes != null && genes.Xenotype?.inheritable == true) || member.genes.Xenotype == XenotypeDefOf.Baseliner) && ((Thing)member).def == ThingDefOf.Human;
			int seed = (flag2 ? ((int)(BigAndSmallCache.globalRandNum * 10000f)) : Rand.Range(0, 1000000));
			var (val, infiltratorData) = GlobalSettings.GetRandomInfiltratorReplacementXenotype(member, seed, !flag3, !flag);
			if (val == null)
			{
				return;
			}
			XenotypeDef xenotype = member.genes.Xenotype;
			member.genes.SetXenotype(val);
			member.TrySwapToXenotypeThingDef();
			if (infiltratorData.disguised && xenotype != null)
			{
				member.genes.iconDef = null;
				member.genes.SetXenotypeDirect(xenotype);
			}
			if (infiltratorData.ideologyOf == null || !ModsConfig.IdeologyActive)
			{
				return;
			}
			Faction val2 = Find.FactionManager.AllFactions.Where((Faction x) => x.def == infiltratorData.ideologyOf).FirstOrDefault();
			if (val2 != null)
			{
				Pawn_IdeoTracker ideo = member.ideo;
				if (ideo != null)
				{
					ideo.SetIdeo(val2.ideos.PrimaryIdeo);
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error($"BigAndSmall: Error swapping {((member != null) ? member.Name : null)} to infiltrator: {ex.Message}. Skipping.");
		}
	}

	private static void RemoveInvalidThings(Pawn member)
	{
		if (member == null)
		{
			return;
		}
		RaceProperties raceProps = member.RaceProps;
		if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) != true)
		{
			return;
		}
		foreach (Apparel item in member.apparel.WornApparel.ToList())
		{
			string cantReason = "";
			if (!CanEquipPatches.CanEquipThing(__result: true, ((Thing)item).def, member, ref cantReason))
			{
				member.apparel.Remove(item);
			}
		}
		foreach (ThingWithComps item2 in member.equipment.AllEquipmentListForReading.ToList())
		{
			string cantReason2 = "";
			if (!CanEquipPatches.CanEquipThing(__result: true, ((Thing)item2).def, member, ref cantReason2))
			{
				member.equipment.Remove(item2);
			}
		}
	}
}
