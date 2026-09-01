using System;
using System.Collections.Generic;
using FactionLoadout.UISupport;
using HarmonyLib;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(OptionListingUtility))]
public static class OptionListingUtility_Patch
{
	[HarmonyPatch("DrawOptionListing")]
	[HarmonyPrefix]
	public static void DrawOptionListing_Patch(ref List<ListableOption> optList)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Expected O, but got Unknown
		if (GenCollection.Any<ListableOption>(optList, (Predicate<ListableOption>)((ListableOption opt) => opt is ListableOption_WebLink)))
		{
			optList.Add((ListableOption)new ListableOption_WebLink(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_SettingName")), (Action)delegate
			{
				Find.WindowStack.Add((Window)(object)new Dialog_FactionLoadout());
			}, Textures.TC_Link));
		}
	}
}
