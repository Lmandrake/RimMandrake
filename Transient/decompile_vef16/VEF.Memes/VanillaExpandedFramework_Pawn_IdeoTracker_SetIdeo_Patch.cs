using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Memes;

[HarmonyPatch(typeof(Pawn_IdeoTracker))]
[HarmonyPatch("SetIdeo")]
public static class VanillaExpandedFramework_Pawn_IdeoTracker_SetIdeo_Patch
{
	[HarmonyPostfix]
	private static void ForceTraitAndAbilities(Ideo ideo, Pawn ___pawn)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Expected O, but got Unknown
		if (ideo == null)
		{
			return;
		}
		foreach (MemeDef meme in ideo.memes)
		{
			ExtendedMemeProperties modExtension = ((Def)meme).GetModExtension<ExtendedMemeProperties>();
			if (modExtension == null)
			{
				continue;
			}
			if (modExtension.forcedTrait != null)
			{
				Trait val = new Trait(modExtension.forcedTrait, 0, true);
				Pawn_StoryTracker story = ___pawn.story;
				if (story != null)
				{
					TraitSet traits = story.traits;
					if (traits != null)
					{
						traits.GainTrait(val, false);
					}
				}
			}
			if (modExtension.abilitiesGiven == null)
			{
				continue;
			}
			foreach (AbilityDef item in modExtension.abilitiesGiven)
			{
				Pawn_AbilityTracker abilities = ___pawn.abilities;
				if (abilities != null)
				{
					abilities.GainAbility(item);
				}
			}
		}
	}
}
