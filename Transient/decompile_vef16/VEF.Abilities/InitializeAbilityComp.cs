using System;
using UnityEngine;
using VEF.Apparels;
using Verse;

namespace VEF.Abilities;

[StaticConstructorOnStartup]
public static class InitializeAbilityComp
{
	static InitializeAbilityComp()
	{
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		for (int i = 0; i < DefDatabase<ThingDef>.AllDefsListForReading.Count; i++)
		{
			ThingDef val = DefDatabase<ThingDef>.AllDefsListForReading[i];
			RaceProperties race = val.race;
			if (race != null && race.Humanlike && !GenCollection.Any<CompProperties>(val.comps, (Predicate<CompProperties>)((CompProperties cp) => typeof(CompProperties_ShieldBubble).IsAssignableFrom(cp.compClass))))
			{
				CompProperties_ShieldBubble compProperties_ShieldBubble = new CompProperties_ShieldBubble
				{
					compClass = typeof(CompAbilities),
					blockRangedAttack = true,
					blockMeleeAttack = false,
					showWhenDrafted = true,
					showOnHostiles = true,
					showOnNeutralInCombat = true,
					shieldTexPath = "Other/ShieldBubble",
					minShieldSize = 1f,
					maxShieldSize = 1.5f,
					shieldColor = new Color(1f, 1f, 1f, 1f),
					EnergyLossPerDamage = 1f
				};
				val.comps.Add((CompProperties)(object)compProperties_ShieldBubble);
				((CompProperties)compProperties_ShieldBubble).ResolveReferences(val);
				((CompProperties)compProperties_ShieldBubble).PostLoadSpecial(val);
			}
		}
	}
}
