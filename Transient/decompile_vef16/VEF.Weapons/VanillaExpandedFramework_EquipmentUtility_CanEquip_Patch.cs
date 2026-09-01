using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_EquipmentUtility_CanEquip_Patch
{
	public static void Postfix(ref bool __result, Thing thing, Pawn pawn, ref string cantReason, bool checkBonded = true)
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		if (__result)
		{
			HeavyWeapon modExtension = ((Def)thing.def).GetModExtension<HeavyWeapon>();
			if (modExtension != null && modExtension.isHeavy && !CanEquip(thing, pawn, modExtension))
			{
				cantReason = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(modExtension.disableOptionLabelKey, NamedArgument.op_Implicit(((Entity)pawn).LabelShort)));
				__result = false;
			}
		}
	}

	public static bool CanEquip(Thing thing, Pawn pawn, HeavyWeapon options)
	{
		if (pawn.story?.traits != null && options.supportedTraits != null && GenCollection.Any<Trait>(pawn.story.traits.allTraits, (Predicate<Trait>)((Trait x) => options.supportedTraits.Contains(((Def)x.def).defName))))
		{
			return true;
		}
		if (pawn.genes != null && options.supportedGenes != null)
		{
			foreach (string supportedGene in options.supportedGenes)
			{
				GeneDef namedSilentFail = DefDatabase<GeneDef>.GetNamedSilentFail(supportedGene);
				if (namedSilentFail != null && pawn.genes.HasActiveGene(namedSilentFail))
				{
					return true;
				}
			}
		}
		if (pawn.apparel.WornApparel != null)
		{
			foreach (Apparel item in pawn.apparel.WornApparel)
			{
				List<string> supportedArmors = options.supportedArmors;
				if (supportedArmors != null && supportedArmors.Contains(((Def)((Thing)item).def).defName))
				{
					return true;
				}
				if (((Thing)item).def.apparel?.bodyPartGroups?.Contains(BodyPartGroupDefOf.Torso) == true && ((Thing)item).def.tradeTags != null)
				{
					if (((Thing)item).def.tradeTags.Contains("HiTechArmor") && thing.def.tradeTags != null && !thing.def.tradeTags.Contains("VFEP_WarcasketWeapon"))
					{
						return true;
					}
					if (((Thing)item).def.tradeTags.Contains("Warcasket"))
					{
						return true;
					}
				}
			}
		}
		return false;
	}
}
