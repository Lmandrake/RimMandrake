using HarmonyLib;
using Verse;

namespace VEF.Sounds;

[HarmonyPatch(typeof(DebugWindowsOpener))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public class VanillaExpandedFramework_DebugWindowsOpener_DevToolStarterOnGUI_Patch
{
	[HarmonyPrefix]
	public static void Prefix()
	{
		if (Restart.VFE_Dev_Restart.KeyDownEvent)
		{
			GenCommandLine.Restart();
		}
	}
}
