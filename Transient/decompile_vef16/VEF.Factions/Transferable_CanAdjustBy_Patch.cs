using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(Transferable), "CanAdjustBy")]
public static class Transferable_CanAdjustBy_Patch
{
	public static Transferable curTransferable;

	public static void Postfix(Transferable __instance)
	{
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		if (curTransferable == __instance || !Find.WindowStack.IsOpen<Dialog_Trade>() || __instance.CountToTransferToDestination <= 0 || TradeSession.trader == null)
		{
			return;
		}
		foreach (ContrabandDef item in DefDatabase<ContrabandDef>.AllDefs.Where((ContrabandDef iid) => !iid.factions.Contains(TradeSession.trader.Faction.def)))
		{
			if (!item.IsThingContraband(__instance.AnyThing, out var _, out var _, out var _))
			{
				continue;
			}
			curTransferable = __instance;
			if (TradeSession.giftMode)
			{
				foreach (TaggedString contrabandWarningMessage in __instance.AnyThing.GetContrabandWarningMessages(isGifting: true))
				{
					Messages.Message(TaggedString.op_Implicit(contrabandWarningMessage), MessageTypeDefOf.CautionInput, true);
				}
				continue;
			}
			foreach (TaggedString contrabandWarningMessage2 in __instance.AnyThing.GetContrabandWarningMessages(isGifting: false))
			{
				Messages.Message(TaggedString.op_Implicit(contrabandWarningMessage2), MessageTypeDefOf.CautionInput, true);
			}
		}
	}
}
