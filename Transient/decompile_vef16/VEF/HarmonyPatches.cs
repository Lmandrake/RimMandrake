using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using VEF.Apparels;
using VEF.Factions;
using VEF.Hediffs;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
public static class HarmonyPatches
{
	static HarmonyPatches()
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Expected O, but got Unknown
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Expected O, but got Unknown
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Expected O, but got Unknown
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Expected O, but got Unknown
		//IL_01be: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c9: Expected O, but got Unknown
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Expected O, but got Unknown
		//IL_0256: Unknown result type (might be due to invalid IL or missing references)
		//IL_0261: Expected O, but got Unknown
		//IL_0286: Unknown result type (might be due to invalid IL or missing references)
		//IL_0291: Expected O, but got Unknown
		//IL_02b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c1: Expected O, but got Unknown
		//IL_0315: Unknown result type (might be due to invalid IL or missing references)
		//IL_0320: Expected O, but got Unknown
		//IL_0372: Unknown result type (might be due to invalid IL or missing references)
		//IL_037f: Expected O, but got Unknown
		VEF_Mod.harmonyInstance.Patch((MethodBase)typeof(PawnApparelGenerator).GetNestedType("PossibleApparelSet", BindingFlags.Instance | BindingFlags.NonPublic).GetMethod("CoatButNoShirt", BindingFlags.Instance | BindingFlags.Public), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patch_PawnApparelGenerator.PossibleApparelSet.manual_CoatButNoShirt), "Transpiler", (Type[])null), (HarmonyMethod)null);
		VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(PawnApparelGenerator), "GenerateStartingApparelFor", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(AccessTools.Method(typeof(Patch_PawnApparelGenerator), "GenerateStartingApparelFor_Postfix", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null);
		PhasingPatches.Do(VEF_Mod.harmonyInstance);
		if (ModCompatibilityCheck.DualWield)
		{
			Type typeInAnyAssembly = GenTypes.GetTypeInAnyAssembly("DualWield.HarmonyInstance.FloatMenuMakerMap_AddHumanlikeOrders", (string)null);
			if (typeInAnyAssembly != null)
			{
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly, "Postfix", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_DualWield_Harmony_FloatMenuMakerMap_AddHumanlikeOrders.manual_Postfix), "Transpiler", (Type[])null), (HarmonyMethod)null);
			}
			else
			{
				Log.Error("Could not find type DualWield.HarmonyInstance.FloatMenuMakerMap_AddHumanlikeOrders in Dual Wield");
			}
		}
		if (ModCompatibilityCheck.RimCities)
		{
			Type typeInAnyAssembly2 = GenTypes.GetTypeInAnyAssembly("Cities.GenCity", "Cities");
			if (typeInAnyAssembly2 != null)
			{
				VEF_Mod.harmonyInstance.Patch((MethodBase)typeInAnyAssembly2.GetNestedTypes(BindingFlags.Instance | BindingFlags.NonPublic).First((Type t) => t.GetMethods(BindingFlags.Instance | BindingFlags.NonPublic).Any((MethodInfo m) => m.Name.Contains("RandomCityFaction") && m.ReturnType == typeof(bool))).GetMethods(BindingFlags.Instance | BindingFlags.NonPublic)
					.First((MethodInfo m) => m.Name.Contains("RandomCityFaction")), (HarmonyMethod)null, new HarmonyMethod(typeof(Patch_Cities_GenCity.manual_RandomCityFaction_predicate), "Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			}
			else
			{
				Log.Error("Could not find type Cities.GenCity in RimCities");
			}
		}
		if (ModCompatibilityCheck.RPGStyleInventory)
		{
			Type typeInAnyAssembly3 = GenTypes.GetTypeInAnyAssembly("Sandy_Detailed_RPG_Inventory.Sandy_Detailed_RPG_GearTab", "Sandy_Detailed_RPG_Inventory");
			if (typeInAnyAssembly3 != null)
			{
				Patch_RPG_GearTab.DetailedRPGGearTab = typeInAnyAssembly3;
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly3, "TryDrawOverallArmor", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patch_RPG_GearTab), "TryDrawOverallArmor_Transpiler", (Type[])null), (HarmonyMethod)null);
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly3, "TryDrawOverallArmor1", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patch_RPG_GearTab), "TryDrawOverallArmor1_Transpiler", (Type[])null), (HarmonyMethod)null);
			}
			else
			{
				Log.Error("Could not find type Sandy_Detailed_RPG_Inventory.Sandy_Detailed_RPG_GearTab in RPG Style Inventory");
			}
		}
		if (ModCompatibilityCheck.RPGStyleInventoryRevamped)
		{
			Type typeInAnyAssembly4 = GenTypes.GetTypeInAnyAssembly("Sandy_Detailed_RPG_Inventory.Sandy_Detailed_RPG_GearTab", "Sandy_Detailed_RPG_Inventory");
			if (typeInAnyAssembly4 != null)
			{
				Patch_RPG_GearTab.DetailedRPGGearTabRevamped = typeInAnyAssembly4;
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly4, "TryDrawOverallArmor", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patch_RPG_GearTab), "TryDrawOverallArmor_Revamped_Transpiler", (Type[])null), (HarmonyMethod)null);
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly4, "TryDrawOverallArmor1", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patch_RPG_GearTab), "TryDrawOverallArmor1_Revamped_Transpiler", (Type[])null), (HarmonyMethod)null);
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly4, "TryDrawOverallArmor2", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patch_RPG_GearTab), "TryDrawOverallArmor1_Revamped_Transpiler", (Type[])null), (HarmonyMethod)null);
			}
			else
			{
				Log.Error("Could not find type Sandy_Detailed_RPG_Inventory.Sandy_Detailed_RPG_GearTab in RPG Style Inventory");
			}
		}
		if (ModCompatibilityCheck.RunAndGun)
		{
			Type typeInAnyAssembly5 = GenTypes.GetTypeInAnyAssembly("RunAndGun.Harmony.Verb_TryCastNextBurstShot", "RunAndGun.Harmony");
			if (typeInAnyAssembly5 != null)
			{
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly5, "SetStanceRunAndGun", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_RunAndGun_Harmony_Verb_TryCastNextBurstShot.manual_SetStanceRunAndGun), "Transpiler", (Type[])null), (HarmonyMethod)null);
			}
			else
			{
				Log.Error("Could not find type RunAndGun.Harmony.Verb_TryCastNextBurstShot in RunAndGun");
			}
		}
		if (ModCompatibilityCheck.FactionDiscovery)
		{
			Type typeInAnyAssembly6 = GenTypes.GetTypeInAnyAssembly("FactionDiscovery.ModBase", "FactionDiscovery");
			if (typeInAnyAssembly6 != null)
			{
				VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeInAnyAssembly6, "RunCheck", (Type[])null, (Type[])null), new HarmonyMethod(typeof(VanillaExpandedFramework_FactionDiscovery_ModBase_Patch.manual_RunCheck), "Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
			}
			else
			{
				Log.Error("Could not find type RunAndGun.Harmony.Verb_TryCastNextBurstShot in RunAndGun");
			}
		}
	}
}
