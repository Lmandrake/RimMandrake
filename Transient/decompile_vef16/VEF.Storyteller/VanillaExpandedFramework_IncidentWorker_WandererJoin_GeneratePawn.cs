using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using VEF.Factions;
using Verse;

namespace VEF.Storyteller;

public static class VanillaExpandedFramework_IncidentWorker_WandererJoin_GeneratePawn
{
	[HarmonyPatch(typeof(IncidentWorker_WandererJoin), "GeneratePawn")]
	public static class TryExecuteWorker
	{
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
		{
			List<CodeInstruction> instructionList = instructions.ToList();
			FieldInfo defInfo = AccessTools.Field(typeof(IncidentWorker), "def");
			FieldInfo pawnKindInfo = AccessTools.Field(typeof(IncidentDef), "pawnKind");
			MethodInfo finalisedPawnKindDefInfo = AccessTools.Method(typeof(TryExecuteWorker), "FinalisedPawnKindDef", (Type[])null, (Type[])null);
			for (int i = 0; i < instructionList.Count; i++)
			{
				CodeInstruction val = instructionList[i];
				if (val.opcode == OpCodes.Ldfld && CodeInstructionExtensions.OperandIs(val, (MemberInfo)pawnKindInfo))
				{
					yield return val;
					yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
					yield return new CodeInstruction(OpCodes.Ldfld, (object)defInfo);
					val = new CodeInstruction(OpCodes.Call, (object)finalisedPawnKindDefInfo);
				}
				yield return val;
			}
		}

		private static PawnKindDef FinalisedPawnKindDef(PawnKindDef original, IncidentDef def)
		{
			if (def == IncidentDefOf.StrangerInBlackJoin)
			{
				FactionDefExtension factionDefExtension = FactionDefExtension.Get((Def)(object)Faction.OfPlayer.def);
				if (factionDefExtension.strangerInBlackReplacement != null)
				{
					return factionDefExtension.strangerInBlackReplacement;
				}
			}
			return original;
		}
	}
}
