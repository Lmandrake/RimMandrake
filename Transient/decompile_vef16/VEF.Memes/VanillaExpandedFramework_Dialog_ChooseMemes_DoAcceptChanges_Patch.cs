using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Memes;

[HarmonyPatch(typeof(Dialog_ChooseMemes))]
[HarmonyPatch("DoAcceptChanges")]
public static class VanillaExpandedFramework_Dialog_ChooseMemes_DoAcceptChanges_Patch
{
	[HarmonyPostfix]
	private static void ForceTraitAndAbilitiesOnChooseMemeDialog(List<MemeDef> ___newMemes, Ideo ___ideo)
	{
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Expected O, but got Unknown
		foreach (MemeDef ___newMeme in ___newMemes)
		{
			ExtendedMemeProperties modExtension = ((Def)___newMeme).GetModExtension<ExtendedMemeProperties>();
			if (modExtension == null)
			{
				continue;
			}
			if (modExtension.forcedTrait != null)
			{
				foreach (Pawn item in PawnsFinder.AllMaps_FreeColonistsAndPrisonersSpawned)
				{
					if (item.Ideo != ___ideo)
					{
						continue;
					}
					Trait val = new Trait(modExtension.forcedTrait, 0, true);
					Pawn_StoryTracker story = item.story;
					if (story != null)
					{
						TraitSet traits = story.traits;
						if (traits != null)
						{
							traits.GainTrait(val, false);
						}
					}
				}
			}
			if (modExtension.abilitiesGiven == null)
			{
				continue;
			}
			foreach (Pawn item2 in PawnsFinder.AllMaps_FreeColonistsAndPrisonersSpawned)
			{
				if (item2.Ideo != ___ideo)
				{
					continue;
				}
				foreach (AbilityDef item3 in modExtension.abilitiesGiven)
				{
					Pawn_AbilityTracker abilities = item2.abilities;
					if (abilities != null)
					{
						abilities.GainAbility(item3);
					}
				}
			}
		}
	}
}
