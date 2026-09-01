using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Storyteller;

public class CompQuestGiver : ThingComp
{
	private StorytellerWatcher storytellerWatcher;

	public CompProperties_QuestGiver Props => (CompProperties_QuestGiver)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		storytellerWatcher = Current.Game.GetComponent<StorytellerWatcher>();
	}

	public override IEnumerable<FloatMenuOption> CompFloatMenuOptions(Pawn selPawn)
	{
		yield return QuestGiverFloatMenuOption(selPawn);
	}

	public FloatMenuOption QuestGiverFloatMenuOption(Pawn user)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Expected O, but got Unknown
		string floatOptionLabel = Props.floatOptionLabel;
		Action action = delegate
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			Job val = JobMaker.MakeJob(Props.jobToGive, LocalTargetInfo.op_Implicit((Thing)(object)base.parent));
			user.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)0, false);
		};
		return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(floatOptionLabel, action, (MenuOptionPriority)2, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0), user, LocalTargetInfo.op_Implicit((Thing)(object)base.parent), "ReservedBy", (ReservationLayerDef)null);
	}

	public void Use()
	{
		QuestGiverManager value = null;
		if (!storytellerWatcher.questGiverManagers.TryGetValue(Props.questManagerID, out value))
		{
			value = storytellerWatcher.AddQuestGiverManager(Props.questManagerID, Props.questGiver);
			value.Init();
		}
		value.CallWindow();
	}
}
