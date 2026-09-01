using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(PawnComponentsUtility), "CreateInitialComponents")]
public static class VanillaExpandedFramework_PawnComponentsUtility_CreateInitialComponents_Patch
{
	public static void Postfix(Pawn pawn)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Expected O, but got Unknown
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Expected O, but got Unknown
		if (pawn?.kindDef?.skills != null)
		{
			if (pawn.skills == null)
			{
				pawn.skills = new Pawn_SkillTracker(pawn);
			}
			if (pawn.story == null)
			{
				pawn.story = new Pawn_StoryTracker(pawn);
			}
			_ = pawn.RaceProps.Humanlike;
		}
	}
}
