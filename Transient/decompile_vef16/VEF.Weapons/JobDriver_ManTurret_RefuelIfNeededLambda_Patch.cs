using System;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

[HarmonyPatch]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class JobDriver_ManTurret_RefuelIfNeededLambda_Patch
{
	private static bool Prepare()
	{
		return JobDriver_ManTurret_GunNeedsRefueling_Patch.Prepare();
	}

	private static MethodBase TargetMethod()
	{
		Type type = AccessToolsExtensions.InnerTypes(typeof(JobDriver_ManTurret)).FirstOrDefault((Type x) => AccessToolsExtensions.DeclaredField(x, "refuelIfNeeded") != null);
		if (type == null)
		{
			Log.Error("[VEF] Failed to find inner class with \"refuelIfNeeded\" field. Pawns operating mannable turrets will only grab a single piece of ammo to refuel.");
			return null;
		}
		MethodInfo methodInfo = AccessToolsExtensions.FirstMethod(type, (Func<MethodInfo, bool>)((MethodInfo m) => GenCollection.Any<CodeInstruction>(PatchProcessor.GetOriginalInstructions((MethodBase)m, (ILGenerator)null), (Predicate<CodeInstruction>)((CodeInstruction ci) => CodeInstructionExtensions.LoadsConstant(ci, "MessageOutOfNearbyFuelFor")))));
		if (methodInfo == null)
		{
			Log.Error("[VEF] Failed to find a method with \"MessageOutOfNearbyFuelFor\" string. Pawns operating mannable turrets will only grab a single piece of ammo to refuel.");
		}
		return methodInfo;
	}

	private static void Postfix(Toil ___refuelIfNeeded)
	{
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Expected O, but got Unknown
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		Pawn actor = ___refuelIfNeeded.actor;
		Job curJob = actor.CurJob;
		Thing thing = ((LocalTargetInfo)(ref curJob.targetA)).Thing;
		object obj;
		if (thing == null)
		{
			obj = null;
		}
		else
		{
			ThingDef def = thing.def;
			obj = ((def != null) ? ((Def)def).GetModExtension<AutoRefuelMannedTurrets>() : null);
		}
		AutoRefuelMannedTurrets autoRefuelMannedTurrets = (AutoRefuelMannedTurrets)obj;
		if (autoRefuelMannedTurrets == null || !autoRefuelMannedTurrets.reloadsMoreThanSingleItem)
		{
			return;
		}
		LocalTargetInfo targetB = curJob.targetB;
		if (((LocalTargetInfo)(ref targetB)).Thing == null || ((LocalTargetInfo)(ref targetB)).Thing.stackCount == 1)
		{
			return;
		}
		int num = Mathf.Clamp(autoRefuelMannedTurrets.ModifyRefuelCount((Building)thing, ((LocalTargetInfo)(ref targetB)).Thing), 1, ((LocalTargetInfo)(ref targetB)).Thing.stackCount);
		if (num > 1)
		{
			curJob.count = num;
			if (!ReservationUtility.Reserve(actor, targetB, actor.CurJob, 10, num, (ReservationLayerDef)null, true, false))
			{
				actor.jobs.EndCurrentJob((JobCondition)4, true, true);
				TaggedString val = TranslatorFormattedStringExtensions.Translate("MessageOutOfNearbyFuelFor", NamedArgument.op_Implicit(((Entity)actor).LabelShort), NamedArgument.op_Implicit(((Entity)thing).Label), NamedArgumentUtility.Named((object)actor, "PAWN"), NamedArgumentUtility.Named((object)thing, "GUN"), NamedArgumentUtility.Named((object)ThingCompUtility.TryGetComp<CompRefuelable>(thing).Props.fuelFilter.Summary, "FUEL"));
				Messages.Message(TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()), LookTargets.op_Implicit(thing), MessageTypeDefOf.NegativeEvent, true);
			}
		}
	}
}
