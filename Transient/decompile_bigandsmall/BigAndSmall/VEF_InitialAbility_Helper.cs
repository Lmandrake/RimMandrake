using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class VEF_InitialAbility_Helper
{
	public static Type CompProperties_InitialAbilityType;

	private static FieldInfo initialAbilityField;

	public static List<AbilityDef> TryGetAbilities(List<CompProperties> compPropList)
	{
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Expected O, but got Unknown
		if (!VanillaExpanded.VEActive)
		{
			return null;
		}
		List<AbilityDef> list = new List<AbilityDef>();
		foreach (CompProperties compProp in compPropList)
		{
			try
			{
				if (CompProperties_InitialAbilityType == null)
				{
					CompProperties_InitialAbilityType = AccessTools.TypeByName("VEF.AnimalBehaviours.CompProperties_InitialAbility");
					if (CompProperties_InitialAbilityType == null)
					{
						Log.Error("Big and Small: Could not find VEF.AnimalBehaviours.CompProperties_InitialAbility class.");
						return null;
					}
				}
				if (compProp != null && !(((object)compProp).GetType() != CompProperties_InitialAbilityType))
				{
					if (!(initialAbilityField == null))
					{
						goto IL_00af;
					}
					initialAbilityField = AccessTools.Field(CompProperties_InitialAbilityType, "initialAbility");
					if (!(initialAbilityField == null))
					{
						goto IL_00af;
					}
					Log.Error("Big and Small: Could not find initialAbility field in VEF.AnimalBehaviours.CompProperties_InitialAbility.");
				}
				goto end_IL_0023;
				IL_00af:
				AbilityDef item = (AbilityDef)initialAbilityField.GetValue(compProp);
				list.Add(item);
				end_IL_0023:;
			}
			catch (Exception ex)
			{
				Log.Error($"Big and Small: Exception in VEF_CompProps_InitialAbility_Wrapper.TryGetAbilityFromCompProp: {ex}\n{ex.StackTrace}");
			}
		}
		return list;
	}
}
