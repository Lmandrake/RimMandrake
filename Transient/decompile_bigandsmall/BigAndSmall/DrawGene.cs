using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(GeneUIUtility), "DrawGeneBasics")]
public static class DrawGene
{
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Expected O, but got Unknown
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Expected O, but got Unknown
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Expected O, but got Unknown
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Expected O, but got Unknown
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Expected O, but got Unknown
		bool flag = false;
		List<CodeInstruction> list = instructions.ToList();
		for (int i = 1; i < list.Count; i++)
		{
			_ = list[i];
			if (!flag && i > 3 && i < list.Count - 2 && CodeInstructionExtensions.IsLdloc(list[i], (LocalBuilder)null) && list[i].operand is LocalBuilder { LocalIndex: 4 } && list[i + 1].opcode == OpCodes.Callvirt && CodeInstructionExtensions.OperandIs(list[i + 1], (MemberInfo)typeof(CachedTexture).GetMethod("get_Texture")))
			{
				flag = true;
				List<CodeInstruction> collection = new List<CodeInstruction>(3)
				{
					new CodeInstruction(OpCodes.Ldarg_0, (object)null),
					new CodeInstruction(OpCodes.Ldarg_2, (object)null),
					new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(DrawGene), "GetGeneBackground", (Type[])null, (Type[])null))
				};
				list.InsertRange(i + 1, collection);
			}
			if (list[i].opcode == OpCodes.Callvirt && CodeInstructionExtensions.OperandIs(list[i], (MemberInfo)typeof(Def).GetMethod("get_LabelCap")))
			{
				List<CodeInstruction> collection2 = new List<CodeInstruction>(2)
				{
					new CodeInstruction(OpCodes.Ldarg_0, (object)null),
					new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(DrawGene), "GetCustomLabel", (Type[])null, (Type[])null))
				};
				list.InsertRange(i + 1, collection2);
			}
		}
		return list;
	}

	public static CachedTexture GetGeneBackground(CachedTexture previous, GeneDef gene, GeneType geneType)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		if (GeneDefPatcher.customGeneBackgrounds.TryGetValue(gene, out var value))
		{
			return value.GetCachedTexture(geneType, previous, DrawGeneSection.pCache);
		}
		return previous;
	}

	public static TaggedString GetCustomLabel(TaggedString label, GeneDef gene)
	{
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		if (!((TaggedString)(ref label)).NullOrEmpty() && DefAltNamer.AllGeneRenames.TryGetValue(gene, out var value) && DrawGeneSection.pCache != null)
		{
			if (DrawGeneSection.pCache.isMechanical)
			{
				string labelMechanoid = value.labelMechanoid;
				if (labelMechanoid != null)
				{
					return TaggedString.op_Implicit(GenText.CapitalizeFirst(labelMechanoid));
				}
			}
			if (DrawGeneSection.pCache.isBloodFeeder)
			{
				string labelBloodfeeder = value.labelBloodfeeder;
				if (labelBloodfeeder != null)
				{
					return TaggedString.op_Implicit(GenText.CapitalizeFirst(labelBloodfeeder));
				}
			}
		}
		return label;
	}
}
