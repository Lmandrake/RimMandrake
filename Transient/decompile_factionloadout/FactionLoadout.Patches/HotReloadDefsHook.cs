using System;
using HarmonyLib;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PlayDataLoader), "HotReloadDefs")]
public static class HotReloadDefsHook
{
	public static void Postfix()
	{
		LongEventHandler.QueueLongEvent((Action)ModCore.ReapplyAfterHotReload, "FactionLoadout_ReapplyingLoadingText", false, (Action<Exception>)null, true, false, (Action)null);
	}
}
