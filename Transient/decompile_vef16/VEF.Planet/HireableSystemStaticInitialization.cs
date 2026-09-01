using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Planet;

[StaticConstructorOnStartup]
public static class HireableSystemStaticInitialization
{
	public static List<Hireable> Hireables;

	private static HiringContractTracker cachedTracker;

	private static World cachedTrackerWorld;

	static HireableSystemStaticInitialization()
	{
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Expected O, but got Unknown
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Expected O, but got Unknown
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Expected O, but got Unknown
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Expected O, but got Unknown
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Expected O, but got Unknown
		//IL_0191: Unknown result type (might be due to invalid IL or missing references)
		//IL_019d: Expected O, but got Unknown
		//IL_01ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Expected O, but got Unknown
		//IL_0203: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Expected O, but got Unknown
		Hireables = (from def in DefDatabase<HireableFactionDef>.AllDefs
			group def by def.commTag into @group
			select new Hireable(@group.Key, @group.ToList())).ToList();
		if (GenCollection.Any<Hireable>(Hireables))
		{
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(Building_CommsConsole), "GetCommTargets", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "GetCommTargets_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(LoadedObjectDirectory), "Clear", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "AddHireablesToLoadedObjectDirectory", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(QuestUtility), "IsQuestLodger", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "IsQuestLodger_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(EquipmentUtility), "QuestLodgerCanUnequip", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "QuestLodgerCanUnequip_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(CaravanFormingUtility), "AllSendablePawns", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "CaravanAllSendablePawns_Transpiler", (Type[])null), (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "CheckAcceptArrest", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "CheckAcceptArrestPostfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(BillUtility), "IsSurgeryViolationOnExtraFactionMember", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "IsSurgeryViolation_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessTools.Method(typeof(ForbidUtility), "CaresAboutForbidden", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(HireableSystemStaticInitialization), "CaresAboutForbidden_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		}
	}

	private static HiringContractTracker GetContractTracker(World world)
	{
		if (cachedTrackerWorld != world)
		{
			cachedTracker = world.GetComponent<HiringContractTracker>();
			cachedTrackerWorld = world;
		}
		return cachedTracker;
	}

	public static IEnumerable<ICommunicable> GetCommTargets_Postfix(IEnumerable<ICommunicable> communicables)
	{
		if (!GenCollection.Any<Pawn>(Find.World.GetComponent<HiringContractTracker>().pawns))
		{
			return communicables.Concat((IEnumerable<ICommunicable>)Hireables);
		}
		return GenCollection.Concat<ICommunicable>(communicables, (ICommunicable)(object)Find.World.GetComponent<HiringContractTracker>());
	}

	public static void AddHireablesToLoadedObjectDirectory(LoadedObjectDirectory __instance)
	{
		foreach (Hireable hireable in Hireables)
		{
			__instance.RegisterLoaded((ILoadReferenceable)(object)hireable);
		}
	}

	public static void IsQuestLodger_Postfix(Pawn p, ref bool __result)
	{
		__result = __result || GetContractTracker(Find.World).IsHired(p);
	}

	public static void QuestLodgerCanUnequip_Postfix(Pawn pawn, ref bool __result)
	{
		__result = __result && pawn.RaceProps.Humanlike && !GetContractTracker(Find.World).IsHired(pawn);
	}

	public static IEnumerable<CodeInstruction> CaravanAllSendablePawns_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		MethodInfo questLodger = AccessTools.Method(typeof(QuestUtility), "IsQuestLodger", (Type[])null, (Type[])null);
		foreach (CodeInstruction instruction in instructions)
		{
			if (CodeInstructionExtensions.Calls(instruction, questLodger))
			{
				yield return new CodeInstruction(OpCodes.Dup, (object)null);
				yield return instruction;
				yield return CodeInstruction.Call(typeof(HireableSystemStaticInitialization), "CaravanAllSendablePawns_Helper", (Type[])null, (Type[])null);
			}
			else
			{
				yield return instruction;
			}
		}
	}

	public static bool CaravanAllSendablePawns_Helper(Pawn pawn, bool questLodger)
	{
		if (questLodger)
		{
			return !GetContractTracker(Find.World).IsHired(pawn);
		}
		return false;
	}

	public static void CheckAcceptArrestPostfix(Pawn __instance, ref bool __result)
	{
		HiringContractTracker contractTracker = GetContractTracker(Find.World);
		if (contractTracker.IsHired(__instance))
		{
			contractTracker.BreakContract();
			__result = false;
		}
	}

	public static void IsSurgeryViolation_Postfix(Bill_Medical bill, ref bool __result)
	{
		__result = __result || (GetContractTracker(Find.World).IsHired(bill.GiverPawn) && ((Bill)bill).recipe.Worker.IsViolationOnPawn(bill.GiverPawn, bill.Part, Faction.OfPlayer));
	}

	public static void CaresAboutForbidden_Postfix(Pawn pawn, ref bool __result)
	{
		__result = __result && (!GetContractTracker(Find.World).IsHired(pawn) || pawn.CurJobDef != VEFDefOf.VFEC_LeaveMap);
	}
}
