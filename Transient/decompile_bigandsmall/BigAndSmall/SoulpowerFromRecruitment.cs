using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public class SoulpowerFromRecruitment
{
	[HarmonyPatch(typeof(RecruitUtility), "Recruit")]
	[HarmonyPostfix]
	public static void DoRecruit(Pawn pawn, Faction faction, Pawn recruiter)
	{
		if (recruiter != null)
		{
			try
			{
				TryApply(pawn, recruiter);
			}
			catch (Exception ex)
			{
				Log.Error($"Error when checking for soul-on-recruit: {ex}\n{ex.StackTrace}");
			}
		}
	}

	public static void TryApply(Pawn pawn, Pawn recruiter)
	{
		IEnumerable<SiphonSoul> enumerable = from x in recruiter.GetAllPawnExtensions()
			select x.siphonSoul into x
			where x != null && x.type == SiphonType.Influence
			select x;
		if (enumerable.Any())
		{
			SiphonSoul parms = enumerable.FuseAll(SiphonType.Influence);
			Soul.GetOrAddSoulCollector(recruiter).AddPawnSoul(pawn, parms, verbose: true);
		}
	}
}
