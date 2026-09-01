using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(ThoughtWorker_Ugly), "CurrentSocialStateInternal", new Type[]
{
	typeof(Pawn),
	typeof(Pawn)
})]
public static class ThoughtWorker_Ugly_Patch
{
	public static void Postfix(ref ThoughtState __result, Pawn pawn, Pawn other)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		if (!other.RaceProps.Humanlike || !RelationsUtility.PawnsKnowEachOther(pawn, other))
		{
			__result = ThoughtState.op_Implicit(false);
			return;
		}
		if (PawnUtility.IsBiologicallyOrArtificiallyBlind(pawn))
		{
			__result = ThoughtState.op_Implicit(false);
			return;
		}
		if (pawn.story.traits.HasTrait(TraitDefOf.Kind))
		{
			__result = ThoughtState.op_Implicit(false);
			return;
		}
		try
		{
			float statValue = StatExtension.GetStatValue((Thing)(object)other, StatDefOf.PawnBeauty, true, -1);
			if (statValue <= -4f)
			{
				__result = ThoughtState.ActiveAtStage(3);
			}
			else if (statValue <= -3f)
			{
				__result = ThoughtState.ActiveAtStage(2);
			}
			else if (statValue <= -2f)
			{
				__result = ThoughtState.ActiveAtStage(1);
			}
			else if (statValue <= -1f)
			{
				__result = ThoughtState.ActiveAtStage(0);
			}
		}
		catch
		{
		}
	}
}
