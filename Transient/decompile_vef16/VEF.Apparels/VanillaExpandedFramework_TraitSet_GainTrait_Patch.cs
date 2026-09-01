using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using VEF.Pawns;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(TraitSet), "GainTrait")]
public static class VanillaExpandedFramework_TraitSet_GainTrait_Patch
{
	public static bool Prefix(Pawn ___pawn, Trait trait)
	{
		Trait obj = trait;
		object obj2;
		if (obj == null)
		{
			obj2 = null;
		}
		else
		{
			TraitDef def = obj.def;
			obj2 = ((def != null) ? ((Def)def).GetModExtension<TraitExtension>() : null);
		}
		TraitExtension traitExtension = (TraitExtension)obj2;
		if (traitExtension != null && traitExtension.apparelExclusiveTrait)
		{
			Pawn_ApparelTracker apparel = ___pawn.apparel;
			List<Apparel> list = ((apparel != null) ? apparel.WornApparel : null);
			if (list != null)
			{
				foreach (Apparel item in list)
				{
					ApparelExtension apparelExtension = ((item != null) ? ((Def)((Thing)item).def).GetModExtension<ApparelExtension>() : null);
					if (apparelExtension?.traitsOnEquip != null && GenCollection.Any<TraitRequirement>(apparelExtension.traitsOnEquip, (Predicate<TraitRequirement>)((TraitRequirement t) => t.def == trait.def && (!t.degree.HasValue || t.degree == trait.Degree))))
					{
						return true;
					}
				}
			}
			return false;
		}
		return true;
	}
}
