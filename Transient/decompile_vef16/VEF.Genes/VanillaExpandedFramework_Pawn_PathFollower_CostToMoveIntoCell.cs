using System;
using System.Collections.Generic;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn_PathFollower), "CostToMoveIntoCell", new Type[]
{
	typeof(Pawn),
	typeof(IntVec3)
})]
[HarmonyPatchCategory("MoveSpeedFactorByTerrainTag")]
public class VanillaExpandedFramework_Pawn_PathFollower_CostToMoveIntoCell
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Expected O, but got Unknown
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Expected O, but got Unknown
		CodeMatcher val = new CodeMatcher(instructions, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
		{
			CodeMatch.LoadsLocal(false, (string)null),
			CodeMatch.LoadsField(AccessToolsExtensions.DeclaredField(typeof(TerrainDef), "tags"), false),
			CodeMatch.Branches((string)null)
		}).Insert((CodeInstruction[])(object)new CodeInstruction[4]
		{
			CodeInstruction.LoadArgument(0, false),
			CodeInstruction.LoadLocal(3, false),
			CodeInstruction.LoadLocal(0, true),
			new CodeInstruction(OpCodes.Call, (object)AccessToolsExtensions.DeclaredMethod(typeof(VanillaExpandedFramework_Pawn_PathFollower_CostToMoveIntoCell), "ModifySpeedFactorForPawn", (Type[])null, (Type[])null))
		});
		return val.Instructions();
	}

	public static void ModifySpeedFactorForPawn(Pawn pawn, TerrainDef terrain, ref float speed)
	{
		if (terrain != null && !GenList.NullOrEmpty<string>((IList<string>)terrain.tags) && StaticCollectionsClass.moveSpeedFactorByTerrainTag_gene_pawns.TryGetValue((Thing)(object)pawn, out var value))
		{
			value.ApplySpeed(terrain.tags, ref speed);
		}
	}
}
