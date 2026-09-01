using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Planet;

public class EquipmentOffsetConditions : DefModExtension
{
	public List<TechLevel> techLevels;

	public bool IsValid(Thing weapon, ThingDef apparelDef)
	{
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		List<VerbProperties> verbs = weapon.def.Verbs;
		bool num = verbs != null && GenCollection.Any<VerbProperties>(verbs, (Predicate<VerbProperties>)((VerbProperties v) => v.verbClass == typeof(Verb_Shoot) || v.verbClass.IsSubclassOf(typeof(Verb_Shoot))));
		bool flag = techLevels?.Contains(weapon.def.techLevel) ?? true;
		return num && flag;
	}
}
