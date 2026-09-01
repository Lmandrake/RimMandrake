using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Memes;

[HarmonyPatch(typeof(Dialog_ChooseMemes))]
[HarmonyPatch("GetFirstIncompatibleMemePair")]
public static class VanillaExpandedFramework_Dialog_ChooseMemes_GetFirstIncompatibleMemePair_Patch
{
	[HarmonyPostfix]
	public static void DetectIfRequiredMeme(ref List<MemeDef> ___newMemes, ref Pair<MemeDef, MemeDef> __result)
	{
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		List<MemeDef> memesTemp = ___newMemes;
		for (int i = 0; i < ___newMemes.Count; i++)
		{
			ExtendedMemeProperties modExtension = ((Def)___newMemes[i]).GetModExtension<ExtendedMemeProperties>();
			if (modExtension == null || modExtension.neededMeme == null)
			{
				continue;
			}
			foreach (MemeDef item in DefDatabase<MemeDef>.AllDefsListForReading.Where((MemeDef k) => (int)k.category == 1 && memesTemp.Contains(k)).ToList())
			{
				if (((Def)___newMemes[i]).GetModExtension<ExtendedMemeProperties>().neededMeme != ((Def)item).defName)
				{
					__result = new Pair<MemeDef, MemeDef>(___newMemes[i], item);
				}
			}
		}
	}
}
