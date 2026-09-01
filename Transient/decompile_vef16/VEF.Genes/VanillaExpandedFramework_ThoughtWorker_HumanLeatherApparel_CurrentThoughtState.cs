using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(ThoughtWorker_HumanLeatherApparel), "CurrentThoughtState")]
public class VanillaExpandedFramework_ThoughtWorker_HumanLeatherApparel_CurrentThoughtState
{
	public static void Postfix(Pawn p, ref ThoughtState __result)
	{
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		if (((ThoughtState)(ref __result)).StageIndex >= 4 || !StaticCollectionsClass.defs_treated_as_human_leather.TryGetValue((Thing)(object)p, out var value))
		{
			return;
		}
		int num = ((ThoughtState)(ref __result)).StageIndex;
		if (num < 0)
		{
			num = 0;
		}
		string text = ((ThoughtState)(ref __result)).Reason;
		foreach (Apparel item in p.apparel.WornApparel)
		{
			if (((Thing)item).Stuff != null && value.Contains(((Thing)item).Stuff))
			{
				if (text == null)
				{
					text = ((Def)((Thing)item).def).label;
				}
				num++;
			}
		}
		ThoughtState val = ((num >= 5) ? ThoughtState.ActiveAtStage(4, text) : ((num != 0) ? ThoughtState.ActiveAtStage(num - 1, text) : ThoughtState.Inactive));
		__result = val;
	}
}
