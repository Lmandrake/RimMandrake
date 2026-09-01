using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(ThoughtWorker_Pretty), "CurrentSocialStateInternal", new Type[]
{
	typeof(Pawn),
	typeof(Pawn)
})]
public static class CurrentSocialStateInternal_Patch
{
	public static void Postfix(ref ThoughtState __result, Pawn pawn, Pawn other)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		if (!other.RaceProps.Humanlike || !RelationsUtility.PawnsKnowEachOther(pawn, other))
		{
			__result = ThoughtState.op_Implicit(false);
			return;
		}
		if (RelationsUtility.IsDisfigured(other, pawn, false))
		{
			__result = ThoughtState.op_Implicit(false);
			return;
		}
		if (PawnUtility.IsBiologicallyOrArtificiallyBlind(pawn))
		{
			__result = ThoughtState.op_Implicit(false);
			return;
		}
		try
		{
			float statValue = StatExtension.GetStatValue((Thing)(object)other, StatDefOf.PawnBeauty, true, -1);
			if (statValue >= 4f)
			{
				__result = ThoughtState.ActiveAtStage(3);
			}
			else if (statValue >= 3f)
			{
				__result = ThoughtState.ActiveAtStage(2);
			}
			else if (statValue >= 2f)
			{
				__result = ThoughtState.ActiveAtStage(1);
			}
			else if (statValue >= 1f)
			{
				__result = ThoughtState.ActiveAtStage(0);
			}
		}
		catch
		{
		}
	}
}
