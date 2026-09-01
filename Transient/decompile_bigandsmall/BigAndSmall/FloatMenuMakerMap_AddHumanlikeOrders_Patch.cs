using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace BigAndSmall;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class FloatMenuMakerMap_AddHumanlikeOrders_Patch
{
	public static void Postfix(List<Pawn> selectedPawns, Vector3 clickPos, ref FloatMenuContext context, ref List<FloatMenuOption> __result)
	{
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_026a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_030a: Unknown result type (might be due to invalid IL or missing references)
		//IL_032c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0333: Expected O, but got Unknown
		//IL_03cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f5: Expected O, but got Unknown
		if (selectedPawns.Count != 1 || GenCollection.Any<Pawn>(selectedPawns, (Predicate<Pawn>)((Pawn x) => ((x != null) ? ((Thing)x).Map : null) == null)))
		{
			return;
		}
		Pawn pawn = selectedPawns[0];
		foreach (Pawn pilotable in (from x in GridsUtility.GetThingList(IntVec3.FromVector3(clickPos), ((Thing)pawn).Map)
			where x is Pawn
			select x).Select((Func<Thing, Pawn>)((Thing x) => (Pawn)x)))
		{
			Piloted piloted = pilotable?.health?.hediffSet?.hediffs?.OfType<Piloted>()?.FirstOrDefault();
			if ((piloted != null && !piloted.defaultEnterable) || piloted == null || piloted == null)
			{
				continue;
			}
			Piloted piloted2 = piloted;
			string text = "";
			if (((Thing)((Hediff)piloted2).pawn).Faction != ((Thing)pawn).Faction && !piloted2.Props.pilotRequired)
			{
				text = string.Format("{0} {1}", ((Entity)pawn).Label, Translator.Translate("BS_CannotEnterEnemyAsOperator"));
			}
			else if (((Thing)((Hediff)piloted2).pawn).Faction != ((Thing)pawn).Faction && !((Hediff)piloted2).pawn.Downed && piloted2.InnerContainer.Count > 0)
			{
				text = string.Format("{0} {1}", ((Entity)pawn).Label, Translator.Translate("BS_CannotPilotNonDownedEnemy"));
			}
			else if (piloted2.PilotCount + 1 > piloted2.PilotCapacity)
			{
				text = string.Format("{0} {1}", ((Entity)pawn).Label, Translator.Translate("BS_PilotCapReached"));
			}
			else if (piloted2.MaxCapacity < pawn.BodySize)
			{
				text = string.Format("{0} {1}", ((Entity)pawn).Label, Translator.Translate("BS_TooLargeToPilot"));
			}
			else if (piloted2.TotalMass + pawn.BodySize > piloted2.MaxCapacity)
			{
				text = string.Format("{0} {1}", ((Entity)pawn).Label, Translator.Translate("BS_NotEnoughRoomForPilot"));
			}
			JobDef pilotJobDef = DefDatabase<JobDef>.AllDefsListForReading.Where((JobDef x) => ((Def)x).defName == "BS_EnteringPilotablePawn").FirstOrDefault();
			if (pilotJobDef != null)
			{
				FloatMenuOption val2 = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_EnterPilotable")), (Action)delegate
				{
					//IL_000c: Unknown result type (might be due to invalid IL or missing references)
					Job val = JobMaker.MakeJob(pilotJobDef, LocalTargetInfo.op_Implicit((Thing)(object)pilotable));
					pawn.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)6, false);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				if (text != "")
				{
					val2.Disabled = true;
					val2.Label = text;
				}
				__result.Add(val2);
			}
			if (!((Hediff)piloted2).pawn.Downed || piloted2.PilotCount <= 0)
			{
				continue;
			}
			JobDef ejectJobDef = DefDatabase<JobDef>.AllDefsListForReading.Where((JobDef x) => ((Def)x).defName == "BS_EjectPilotablePawn").FirstOrDefault();
			if (ejectJobDef != null)
			{
				FloatMenuOption item = new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("BS_EjectPilots")), (Action)delegate
				{
					//IL_0011: Unknown result type (might be due to invalid IL or missing references)
					Job val3 = JobMaker.MakeJob(ejectJobDef, LocalTargetInfo.op_Implicit((Thing)(object)pilotable));
					pawn.jobs.TryTakeOrderedJob(val3, (JobTag?)(JobTag)6, false);
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
				__result.Add(item);
			}
		}
	}
}
