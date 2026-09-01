using System;
using System.Collections.Generic;
using System.Reflection;
using System.Xml;
using HarmonyLib;
using Verse;

namespace VEF;

[HarmonyPatch(typeof(BackCompatibility), "BackCompatibleDefName")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_BackCompatibility_BackCompatibleDefName_Patch
{
	internal static readonly Func<bool> CheckSaveIdenticalToCurrentEnvironmentMethod = NonPublicMethods.MakeDelegate<Func<bool>>(AccessToolsExtensions.DeclaredMethod(typeof(BackCompatibility), "CheckSaveIdenticalToCurrentEnvironment", (Type[])null, (Type[])null));

	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		if (BackwardsCompatibilityMigrationUtility.converter != null)
		{
			return !GenDictionary.NullOrEmpty<string, Dictionary<Type, string>>(BackwardsCompatibilityMigrationUtility.defNameConverters);
		}
		return false;
	}

	private static void Postfix(Type defType, string defName, bool forDefInjections, XmlNode node, ref string __result)
	{
		try
		{
			if (CheckSaveIdenticalToCurrentEnvironmentMethod())
			{
				string text = ((BackCompatibilityConverter)BackwardsCompatibilityMigrationUtility.converter).BackCompatibleDefName(defType, defName, forDefInjections, node);
				if (text != null)
				{
					__result = text;
				}
			}
		}
		catch (Exception arg)
		{
			Log.Error($"[VEF] Error running defName migration on {defName}, exception:\n{arg}");
		}
	}
}
