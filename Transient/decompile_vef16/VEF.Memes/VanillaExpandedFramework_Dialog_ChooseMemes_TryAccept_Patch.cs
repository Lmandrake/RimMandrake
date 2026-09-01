using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Memes;

[HarmonyPatch(typeof(Dialog_ChooseMemes))]
[HarmonyPatch("TryAccept")]
public static class VanillaExpandedFramework_Dialog_ChooseMemes_TryAccept_Patch
{
	[HarmonyPrefix]
	public static bool DetectIfPairedMeme(ref List<MemeDef> ___newMemes)
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		for (int i = 0; i < ___newMemes.Count; i++)
		{
			ExtendedMemeProperties modExtension = ((Def)___newMemes[i]).GetModExtension<ExtendedMemeProperties>();
			if (modExtension == null || modExtension.requiredMemes == null)
			{
				continue;
			}
			bool flag = false;
			List<string> list = new List<string>();
			foreach (string requiredMeme in modExtension.requiredMemes)
			{
				MemeDef namedSilentFail = DefDatabase<MemeDef>.GetNamedSilentFail(requiredMeme);
				if (namedSilentFail != null)
				{
					list.Add(TaggedString.op_Implicit(((Def)namedSilentFail).LabelCap));
					if (___newMemes.Contains(namedSilentFail))
					{
						flag = true;
					}
				}
			}
			if (!flag)
			{
				string text = string.Join(", ", list);
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VME_MessageNeedsThePairedMeme", NamedArgument.op_Implicit(((Def)___newMemes[i]).label), NamedArgument.op_Implicit(text))), MessageTypeDefOf.RejectInput, false);
				return false;
			}
		}
		return true;
	}
}
