using System;
using System.Reflection;
using System.Xml;
using HarmonyLib;
using Verse;

namespace VEF;

[HarmonyPatch(typeof(BackCompatibility), "GetBackCompatibleType")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_BackCompatibility_GetBackCompatibleType_Patch
{
	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		if (BackwardsCompatibilityMigrationUtility.converter != null)
		{
			return !GenDictionary.NullOrEmpty<string, Type>(BackwardsCompatibilityMigrationUtility.abilityClasses);
		}
		return false;
	}

	private static bool Prefix(Type baseType, string providedClassName, XmlNode node, ref Type __result)
	{
		try
		{
			if (!VanillaExpandedFramework_BackCompatibility_BackCompatibleDefName_Patch.CheckSaveIdenticalToCurrentEnvironmentMethod())
			{
				return true;
			}
			Type backCompatibleType = ((BackCompatibilityConverter)BackwardsCompatibilityMigrationUtility.converter).GetBackCompatibleType(baseType, providedClassName, node);
			if (backCompatibleType != null)
			{
				__result = backCompatibleType;
				return false;
			}
		}
		catch (Exception arg)
		{
			Log.Error($"[VEF] Error running Ability class migration with provided class name {providedClassName}, exception:\n{arg}");
		}
		return true;
	}
}
