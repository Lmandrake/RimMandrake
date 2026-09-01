using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;

namespace VEF.Graphics;

[HarmonyPatch(typeof(OverlayDrawer), "DrawAllOverlays")]
public static class OverlayDrawer_DrawAllOverlays_Patch
{
	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		MethodInfo nonLastRenderMethod = AccessToolsExtensions.DeclaredMethod(typeof(OverlayDrawer), "RenderRechargineOverlay", (Type[])null, (Type[])null);
		MethodInfo ourRenderMethod = AccessToolsExtensions.DeclaredMethod(typeof(CustomOverlayDrawer), "RenderCustomOverlays", (Type[])null, (Type[])null);
		bool isLastOverlayRender = false;
		foreach (CodeInstruction ci in instr)
		{
			if (isLastOverlayRender)
			{
				isLastOverlayRender = false;
				yield return CodeInstructionExtensions.MoveLabelsFrom(CodeInstruction.LoadArgument(0, false), ci);
				yield return CodeInstruction.LoadLocal(4, false);
				yield return CodeInstruction.LoadLocal(5, false);
				yield return new CodeInstruction(OpCodes.Call, (object)ourRenderMethod);
			}
			else if (CodeInstructionExtensions.Calls(ci, nonLastRenderMethod))
			{
				isLastOverlayRender = true;
			}
			yield return ci;
		}
	}
}
