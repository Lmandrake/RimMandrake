using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HarmonyPatch(typeof(JobDriver_ConstructFinishFrame), "MakeNewToils")]
public static class VanillaExpandedFramework_JobDriver_ConstructFinishFrame_MakeNewToils_Patch
{
	public static IEnumerable<Toil> Postfix(IEnumerable<Toil> __result, JobDriver_ConstructFinishFrame __instance)
	{
		foreach (Toil toil in __result)
		{
			yield return toil;
			if (!(toil.debugName == "MakeNewToils") || toil.activeSkill == null)
			{
				continue;
			}
			toil.activeSkill = delegate
			{
				//IL_000c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0011: Unknown result type (might be due to invalid IL or missing references)
				LocalTargetInfo target = ((JobDriver)__instance).job.GetTarget((TargetIndex)1);
				Thing thing = ((LocalTargetInfo)(ref target)).Thing;
				object obj;
				if (thing == null)
				{
					obj = null;
				}
				else
				{
					ThingDef def = thing.def;
					if (def == null)
					{
						obj = null;
					}
					else
					{
						BuildableDef entityDefToBuild = def.entityDefToBuild;
						obj = ((entityDefToBuild != null) ? ((Def)entityDefToBuild).GetModExtension<ThingDefExtension>() : null);
					}
				}
				ThingDefExtension thingDefExtension = (ThingDefExtension)obj;
				return (thingDefExtension?.constructionSkillRequirement != null) ? thingDefExtension.constructionSkillRequirement.skill : SkillDefOf.Construction;
			};
		}
	}
}
