using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

[HarmonyPatch]
public static class RoosCrushedPelvis_Patch
{
	/// <summary>
	/// For the sake of... consistency? Adds Roos Crushed Pelvis behaviour to giants as well.
	/// </summary>
	[HarmonyPatch(typeof(JobDriver_Lovin), "MakeNewToils")]
	[HarmonyPostfix]
	public static void MakeNewToils_Postfix(ref JobDriver_Lovin __instance, ref TargetIndex ___PartnerInd)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			JobDriver_Lovin obj = __instance;
			LocalTargetInfo? obj2;
			if (obj == null)
			{
				obj2 = null;
			}
			else
			{
				Job job = ((JobDriver)obj).job;
				obj2 = ((job != null) ? new LocalTargetInfo?(job.GetTarget(___PartnerInd)) : ((LocalTargetInfo?)null));
			}
			LocalTargetInfo? val = obj2;
			if (!val.HasValue)
			{
				return;
			}
			LocalTargetInfo valueOrDefault = val.GetValueOrDefault();
			Pawn pawn = ((LocalTargetInfo)(ref valueOrDefault)).Pawn;
			if (pawn == null || pawn.story == null || ((JobDriver)__instance).pawn?.story == null)
			{
				return;
			}
			IEnumerable<Trait> enumerable = pawn.story.traits.allTraits.Where((Trait x) => ((Def)x.def).defName == "BS_Giant");
			TraitSet traits = pawn.story.traits;
			bool flag = traits != null && traits.HasTrait(TraitDefOf.Kind);
			if (!flag && BSDefs.BS_Gentle != null)
			{
				TraitSet traits2 = pawn.story.traits;
				flag = traits2 != null && traits2.HasTrait(BSDefs.BS_Gentle);
			}
			if (enumerable == null || !enumerable.Any() || flag)
			{
				return;
			}
			List<ThoughtDef> allDefsListForReading = DefDatabase<ThoughtDef>.AllDefsListForReading;
			ThoughtDef val2 = allDefsListForReading.Find((ThoughtDef x) => ((Def)x).defName == "RBM_CrushedMasochist");
			ThoughtDef val3 = allDefsListForReading.Find((ThoughtDef x) => ((Def)x).defName == "RBM_Crushed");
			if (val2 != null)
			{
				TraitSet traits3 = ((JobDriver)__instance).pawn.story.traits;
				if (traits3 != null && traits3.HasTrait(BSDefs.Masochist))
				{
					Pawn_NeedsTracker needs = ((JobDriver)__instance).pawn.needs;
					if (needs == null)
					{
						return;
					}
					Need_Mood mood = needs.mood;
					if (mood != null)
					{
						ThoughtHandler thoughts = mood.thoughts;
						if (thoughts != null)
						{
							thoughts.memories.TryGainMemory(val2, (Pawn)null, (Precept)null);
						}
					}
					return;
				}
			}
			if (val3 == null)
			{
				return;
			}
			Pawn_NeedsTracker needs2 = ((JobDriver)__instance).pawn.needs;
			if (needs2 == null)
			{
				return;
			}
			Need_Mood mood2 = needs2.mood;
			if (mood2 != null)
			{
				ThoughtHandler thoughts2 = mood2.thoughts;
				if (thoughts2 != null)
				{
					thoughts2.memories.TryGainMemory(val3, (Pawn)null, (Precept)null);
				}
			}
		}
		catch (Exception ex)
		{
			Log.Warning(ex.Message + "\n" + ex.StackTrace);
		}
	}
}
