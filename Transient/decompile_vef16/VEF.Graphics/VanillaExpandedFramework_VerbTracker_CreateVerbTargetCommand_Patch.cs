using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

[HarmonyPatch(typeof(VerbTracker), "CreateVerbTargetCommand")]
public static class VanillaExpandedFramework_VerbTracker_CreateVerbTargetCommand_Patch
{
	public static void Postfix(ref Command_VerbTarget __result, Thing ownerThing, Verb verb)
	{
		CompGraphicCustomization compGraphicCustomization = ThingCompUtility.TryGetComp<CompGraphicCustomization>(ownerThing);
		if (compGraphicCustomization != null)
		{
			((Command)__result).icon = (Texture)(object)compGraphicCustomization.Texture;
		}
	}
}
