using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.Pawns;
using VEF.Things;
using Verse;

namespace VEF.Apparels;

public static class Patch_PawnApparelGenerator
{
	public static class PossibleApparelSet
	{
		public static class manual_CoatButNoShirt
		{
			public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
			{
				List<CodeInstruction> instructionList = instructions.ToList();
				FieldInfo apparelLayerDefOfShellInfo = AccessTools.Field(typeof(ApparelLayerDefOf), "Shell");
				FieldInfo apparelLayerDefOfOuterShellInfo = AccessTools.Field(typeof(ApparelLayerDefOf), "VFEC_OuterShell");
				for (int i = 0; i < instructionList.Count; i++)
				{
					CodeInstruction instruction = instructionList[i];
					if (instruction.opcode == OpCodes.Beq_S)
					{
						CodeInstruction val = instructionList[i - 1];
						if (val.opcode == OpCodes.Ldsfld && CodeInstructionExtensions.OperandIs(val, (MemberInfo)apparelLayerDefOfShellInfo))
						{
							yield return instruction;
							yield return instructionList[i - 2];
							yield return new CodeInstruction(OpCodes.Ldsfld, (object)apparelLayerDefOfOuterShellInfo);
							instruction = instruction.Clone();
						}
					}
					yield return instruction;
				}
			}
		}
	}

	public static void GenerateStartingApparelFor_Postfix(Pawn pawn)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		if (pawn.apparel == null || ((Thing)pawn).Faction == null || !(pawn.kindDef.apparelColor == Color.white))
		{
			return;
		}
		PawnKindDefExtension pawnKindDefExtension = PawnKindDefExtension.Get((Def)(object)pawn.kindDef);
		List<Apparel> wornApparel = pawn.apparel.WornApparel;
		for (int i = 0; i < wornApparel.Count; i++)
		{
			Apparel val = wornApparel[i];
			ThingDefExtension modExtension = ((Def)((Thing)val).def).GetModExtension<ThingDefExtension>();
			if (modExtension != null && !GenList.NullOrEmpty<PawnKindDef>((IList<PawnKindDef>)modExtension.useFactionColourForPawnKinds) && modExtension.useFactionColourForPawnKinds.Contains(pawn.kindDef))
			{
				CompColorableUtility.SetColor((Thing)(object)val, ((Thing)pawn).Faction.Color, true);
				continue;
			}
			ApparelProperties apparel = ((Thing)val).def.apparel;
			List<Pair<BodyPartGroupDef, ApparelLayerDef>> factionColourApparelWithPartAndLayersList = pawnKindDefExtension.FactionColourApparelWithPartAndLayersList;
			for (int j = 0; j < factionColourApparelWithPartAndLayersList.Count; j++)
			{
				Pair<BodyPartGroupDef, ApparelLayerDef> val2 = factionColourApparelWithPartAndLayersList[j];
				if (apparel.bodyPartGroups.Contains(val2.First) && apparel.layers.Contains(val2.Second))
				{
					CompColorableUtility.SetColor((Thing)(object)val, ((Thing)pawn).Faction.Color, true);
					break;
				}
			}
		}
	}
}
