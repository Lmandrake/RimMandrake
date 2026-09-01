using System.Collections.Generic;
using System.Linq;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class OverrideAllConflictingTranspiler
{
	public static Gene IsOverridenBy(Gene gene)
	{
		if (GeneCache.globalCache.TryGetValue(gene, out var value))
		{
			return value.OverridenBy();
		}
		GeneCache.globalCache[gene] = new GeneCache(gene);
		return null;
	}

	[HarmonyPatch(typeof(Gene), "OverrideBy")]
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> Transpile(IEnumerable<CodeInstruction> instructions, ILGenerator il)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Expected O, but got Unknown
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Expected O, but got Unknown
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Expected O, but got Unknown
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Expected O, but got Unknown
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Expected O, but got Unknown
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Expected O, but got Unknown
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Expected O, but got Unknown
		List<CodeInstruction> list = new List<CodeInstruction>(instructions);
		Label label = il.DefineLabel();
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i].opcode == OpCodes.Ret)
			{
				List<CodeInstruction> list2 = new List<CodeInstruction>();
				list2.Add(new CodeInstruction(OpCodes.Ldarg_1, (object)null));
				list2.Add(new CodeInstruction(OpCodes.Brtrue_S, (object)label));
				list2.Add(new CodeInstruction(OpCodes.Ldarg_0, (object)null));
				list2.Add(new CodeInstruction(OpCodes.Ldarg_0, (object)null));
				list2.Add(new CodeInstruction(OpCodes.Call, (object)typeof(OverrideAllConflictingTranspiler).GetMethod("IsOverridenBy")));
				list2.Add(new CodeInstruction(OpCodes.Stfld, (object)typeof(Gene).GetField("overriddenByGene")));
				list2.Add(CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Nop, (object)null), new Label[1] { label }));
				List<CodeInstruction> collection = list2;
				list.InsertRange(i, collection);
				break;
			}
		}
		return list.AsEnumerable();
	}
}
