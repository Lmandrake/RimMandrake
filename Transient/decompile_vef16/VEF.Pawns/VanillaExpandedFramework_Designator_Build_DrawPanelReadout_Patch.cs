using System;
using System.Collections.Generic;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(Designator_Build), "DrawPanelReadout")]
public static class VanillaExpandedFramework_Designator_Build_DrawPanelReadout_Patch
{
	public delegate void DrawSkillRequirement(Designator_Build __instance, SkillDef skillDef, int requirement, float width, ref float curY);

	public static readonly DrawSkillRequirement drawSkillRequirement = AccessTools.MethodDelegate<DrawSkillRequirement>(AccessTools.Method(typeof(Designator_Build), "DrawSkillRequirement", (Type[])null, (Type[])null), (object)null, true, (Type[])null);

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		bool patched = false;
		foreach (CodeInstruction instruction in codeInstructions)
		{
			yield return instruction;
			if (!patched && instruction.opcode == OpCodes.Stloc_3)
			{
				patched = true;
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloca_S, (object)3);
				yield return new CodeInstruction(OpCodes.Ldarg_2, (object)null);
				yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_Designator_Build_DrawPanelReadout_Patch), "DrawSkillRequirementIfNeeded", (Type[])null, (Type[])null));
			}
		}
	}

	public static void DrawSkillRequirementIfNeeded(Designator_Build instance, ref bool flag, float width, ref float curY)
	{
		BuildableDef placingDef = ((Designator_Place)instance).PlacingDef;
		ThingDefExtension thingDefExtension = ((placingDef != null) ? ((Def)placingDef).GetModExtension<ThingDefExtension>() : null);
		if (thingDefExtension?.constructionSkillRequirement == null)
		{
			return;
		}
		drawSkillRequirement(instance, thingDefExtension.constructionSkillRequirement.skill, thingDefExtension.constructionSkillRequirement.level, width, ref curY);
		foreach (Pawn freeColonist in Find.CurrentMap.mapPawns.FreeColonists)
		{
			if (freeColonist.skills.GetSkill(thingDefExtension.constructionSkillRequirement.skill).Level >= thingDefExtension.constructionSkillRequirement.level)
			{
				flag = true;
				break;
			}
		}
	}
}
