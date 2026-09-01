using System.Linq;
using LudeonTK;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Storyteller;

[HotSwappable]
public class QuestChainsDevWindow : Window
{
	private Vector2 scrollPosition = Vector2.zero;

	private float lastHeight;

	public override Vector2 InitialSize => new Vector2(800f, 600f);

	[DebugAction(/*Could not decode attribute arguments.*/)]
	public static void ViewQuestChains()
	{
		Find.WindowStack.Add((Window)(object)new QuestChainsDevWindow());
	}

	public QuestChainsDevWindow()
		: base((IWindowDrawing)null)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.doCloseX = true;
		base.draggable = true;
		base.resizeable = true;
		base.absorbInputAroundWindow = false;
		base.forcePause = false;
		base.preventCameraMotion = false;
		base.focusWhenOpened = false;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0106: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		GameComponent_QuestChains component = Current.Game.GetComponent<GameComponent_QuestChains>();
		if (component == null)
		{
			Widgets.Label(inRect, "Quest Chains component not found.");
			return;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width - 20f, lastHeight);
		Widgets.BeginScrollView(inRect, ref scrollPosition, val, true);
		float num = 0f;
		Widgets.Label(new Rect(0f, num, ((Rect)(ref val)).width, 30f), "Quests (" + component.quests.Count + ")");
		num += 30f;
		foreach (QuestInfo item in component.quests.ToList())
		{
			num += DrawQuestInfo(new Rect(0f, num, ((Rect)(ref val)).width, 0f), item);
		}
		Widgets.Label(new Rect(0f, num, ((Rect)(ref val)).width, 30f), "Future Quests (" + component.futureQuests.Count + ")");
		num += 30f;
		foreach (FutureQuestInfo item2 in component.futureQuests.ToList())
		{
			num += DrawFutureQuestInfo(new Rect(0f, num, ((Rect)(ref val)).width, 0f), item2);
		}
		lastHeight = num;
		Widgets.EndScrollView();
	}

	private float DrawQuestInfo(Rect rect, QuestInfo questInfo)
	{
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Invalid comparison between Unknown and I4
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Unknown result type (might be due to invalid IL or missing references)
		//IL_01da: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_0271: Unknown result type (might be due to invalid IL or missing references)
		//IL_0289: Unknown result type (might be due to invalid IL or missing references)
		//IL_028f: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0341: Unknown result type (might be due to invalid IL or missing references)
		//IL_0359: Unknown result type (might be due to invalid IL or missing references)
		//IL_035f: Unknown result type (might be due to invalid IL or missing references)
		QuestScriptDef questDef = questInfo.questDef;
		QuestChainExtension modExtension = ((Def)questDef).GetModExtension<QuestChainExtension>();
		float num = 0f;
		float num2 = 150f;
		float num3 = ((Rect)(ref rect)).xMax - num2;
		Widgets.Label(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - num2 - 10f, 25f), "- " + ((Def)questDef).defName + " (Chain: " + (((Def)modExtension?.questChainDef).label ?? "None") + ")");
		Quest quest = questInfo.Quest;
		if (quest != null && (int)quest.State == 1)
		{
			if (Widgets.ButtonText(new Rect(num3 - num2 - 10f, ((Rect)(ref rect)).y + num, num2, 25f), "Force Success", true, true, true, (TextAnchor?)null))
			{
				questInfo.Quest.End((QuestEndOutcome)1, false, true);
			}
			num3 = ((Rect)(ref rect)).xMax - num2;
			if (Widgets.ButtonText(new Rect(num3, ((Rect)(ref rect)).y, num2, 25f), "Force Fail", true, true, true, (TextAnchor?)null))
			{
				questInfo.Quest.End((QuestEndOutcome)2, false, true);
			}
		}
		num += 25f;
		if (questInfo.Quest != null)
		{
			Rect val = new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 25f);
			QuestState state = questInfo.Quest.State;
			Widgets.Label(val, "  - State: " + ((object)(QuestState)(ref state)/*cast due to .constrained prefix*/).ToString());
			num += 25f;
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 25f), "  - Outcome: " + ((object)(QuestEndOutcome)(ref questInfo.outcome)/*cast due to .constrained prefix*/).ToString());
		}
		else
		{
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 25f), "  - Quest is null");
		}
		num += 25f;
		if (questInfo.tickAccepted > 0)
		{
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 25f), "  - Accepted: " + GenDate.DateFullStringAt((long)GenDate.TickGameToAbs(questInfo.tickAccepted), default(Vector2)));
			num += 25f;
		}
		if (questInfo.tickCompleted > 0)
		{
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 25f), "  - Completed: " + GenDate.DateFullStringAt((long)GenDate.TickGameToAbs(questInfo.tickCompleted), default(Vector2)));
			num += 25f;
		}
		if (questInfo.tickExpired > 0)
		{
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 25f), "  - Expired: " + GenDate.DateFullStringAt((long)GenDate.TickGameToAbs(questInfo.tickExpired), default(Vector2)));
			num += 25f;
		}
		return num;
	}

	private float DrawFutureQuestInfo(Rect rect, FutureQuestInfo futureQuestInfo)
	{
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ca: Unknown result type (might be due to invalid IL or missing references)
		QuestScriptDef questDef = futureQuestInfo.questDef;
		QuestChainExtension modExtension = ((Def)questDef).GetModExtension<QuestChainExtension>();
		float num = 0f;
		float num2 = 150f;
		float num3 = ((Rect)(ref rect)).xMax - num2;
		Widgets.Label(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - num2 - 10f, 25f), "- " + ((Def)questDef).defName + " (Chain: " + (((Def)modExtension?.questChainDef).label ?? "None") + ")");
		if (Widgets.ButtonText(new Rect(num3, ((Rect)(ref rect)).y + num, num2, 25f), "Fire Now", true, true, true, (TextAnchor?)null))
		{
			questDef.CreateQuest();
			GameComponent_QuestChains.Instance.futureQuests.Remove(futureQuestInfo);
		}
		num += 25f;
		if (futureQuestInfo.tickToFire > 0)
		{
			int num4 = futureQuestInfo.tickToFire - Find.TickManager.TicksGame;
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 50f), "  - Fires in: " + GenDate.ToStringTicksToPeriod(num4, true, false, true, true, false) + " (at " + GenDate.DateFullStringAt((long)GenDate.TickGameToAbs(futureQuestInfo.tickToFire), default(Vector2)) + ")");
			num += 50f;
		}
		else if (futureQuestInfo.mtbDays > 0f)
		{
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 20f, ((Rect)(ref rect)).y + num, ((Rect)(ref rect)).width - 20f, 25f), "  - MTB: " + futureQuestInfo.mtbDays + " days");
			num += 25f;
		}
		return num;
	}
}
