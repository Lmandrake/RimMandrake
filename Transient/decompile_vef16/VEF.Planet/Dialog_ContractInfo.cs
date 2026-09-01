using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.Utils;
using Verse;

namespace VEF.Planet;

public class Dialog_ContractInfo : Window
{
	private readonly HiringContractTracker contract;

	private Vector2 pawnsScrollPos = new Vector2(0f, 0f);

	public override Vector2 InitialSize => new Vector2(750f, 650f);

	protected override float Margin => 15f;

	public Dialog_ContractInfo(HiringContractTracker tracker)
		: base((IWindowDrawing)null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		contract = tracker;
		base.forcePause = true;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0100: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0217: Unknown result type (might be due to invalid IL or missing references)
		//IL_021e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0303: Unknown result type (might be due to invalid IL or missing references)
		//IL_0305: Unknown result type (might be due to invalid IL or missing references)
		//IL_0307: Unknown result type (might be due to invalid IL or missing references)
		//IL_0311: Unknown result type (might be due to invalid IL or missing references)
		//IL_031b: Unknown result type (might be due to invalid IL or missing references)
		//IL_031d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0333: Unknown result type (might be due to invalid IL or missing references)
		//IL_0388: Unknown result type (might be due to invalid IL or missing references)
		//IL_038a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0394: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0260: Unknown result type (might be due to invalid IL or missing references)
		//IL_026c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0295: Unknown result type (might be due to invalid IL or missing references)
		//IL_0297: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_0442: Unknown result type (might be due to invalid IL or missing references)
		//IL_0448: Unknown result type (might be due to invalid IL or missing references)
		//IL_0416: Unknown result type (might be due to invalid IL or missing references)
		//IL_042d: Unknown result type (might be due to invalid IL or missing references)
		GameFont font = Text.Font;
		TextAnchor anchor = Text.Anchor;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, 50f, 50f);
		Rect val2 = inRect.TakeTopPart(50f);
		((Rect)(ref val2)).xMin = ((Rect)(ref val2)).xMin + 60f;
		Text.Anchor = (TextAnchor)3;
		Text.Font = (GameFont)2;
		Widgets.Label(val2, TranslatorFormattedStringExtensions.Translate("VEF.ContractTitle", NamedArgument.op_Implicit(GenText.CapitalizeFirst(((Def)(contract.factionDef?)).label ?? contract.hireable.Key))));
		if (contract.factionDef != null)
		{
			Widgets.DrawLightHighlight(val);
			GUI.color = contract.factionDef.Color;
			Widgets.DrawTextureFitted(val, (Texture)(object)contract.factionDef.Texture, 1f, 1f);
			GUI.color = Color.white;
		}
		Rect rect = GenUI.ContractedBy(GenUI.LeftHalf(inRect), 3f);
		Rect rect2 = GenUI.ContractedBy(GenUI.RightHalf(inRect), 3f);
		((Rect)(ref rect2)).yMin = ((Rect)(ref rect2)).yMin + 20f;
		Text.Font = (GameFont)1;
		Widgets.Label(rect.TakeTopPart(20f), Translator.Translate("VEF.PawnsList"));
		Widgets.DrawMenuSection(rect);
		rect = GenUI.ContractedBy(rect, 5f);
		List<Pawn> list = contract.pawns.Where((Pawn x) => x != null).ToList();
		Rect rect3 = default(Rect);
		((Rect)(ref rect3))._002Ector(0f, 0f, ((Rect)(ref rect)).width - 20f, (float)list.Count * 40f);
		Widgets.BeginScrollView(rect, ref pawnsScrollPos, rect3, true);
		foreach (Pawn item in list)
		{
			Rect val3 = rect3.TakeTopPart(33f);
			if (item != list.Last())
			{
				Widgets.DrawLineHorizontal(((Rect)(ref val3)).x, ((Rect)(ref val3)).yMax, ((Rect)(ref val3)).width);
			}
			Widgets.DrawHighlightIfMouseover(val3);
			if (Widgets.ButtonInvisible(val3, true))
			{
				((Window)this).Close(false);
				CameraJumper.TryJumpAndSelect(GlobalTargetInfo.op_Implicit((Thing)(object)item), (MovementMode)0);
			}
			Widgets.ThingIcon(new Rect(((Rect)(ref val3)).x + 3f, ((Rect)(ref val3)).y + 3f, 27f, 27f), (Thing)(object)item, 1f, (Rot4?)Rot4.South, false, 1f, false);
			((Rect)(ref val3)).xMin = ((Rect)(ref val3)).xMin + 35f;
			Widgets.Label(GenUI.LeftHalf(val3), item.NameFullColored);
			Widgets.Label(GenUI.RightHalf(val3), GenText.ToStringPercent(item.health.summaryHealth.SummaryHealthPercent));
		}
		Widgets.EndScrollView();
		Text.Anchor = (TextAnchor)3;
		Text.Font = (GameFont)1;
		Rect val4 = rect2.TakeTopPart(30f);
		Widgets.Label(GenUI.LeftHalf(val4), Translator.Translate("VEF.Spent"));
		Widgets.Label(GenUI.RightHalf(val4), ColoredText.Colorize(GenText.ToStringMoney(contract.price, (string)null), ColoredText.CurrencyColor));
		Widgets.DrawLineHorizontal(((Rect)(ref val4)).x, ((Rect)(ref val4)).y + 30f, ((Rect)(ref val4)).width);
		((Rect)(ref val4)).y = ((Rect)(ref val4)).y + 30f;
		((Rect)(ref rect2)).yMin = ((Rect)(ref rect2)).yMin + 30f;
		Widgets.Label(GenUI.LeftHalf(val4), Translator.Translate("VEF.TimeLeft"));
		int num = contract.endTicks - Find.TickManager.TicksAbs;
		Widgets.Label(GenUI.RightHalf(val4), ColoredText.Colorize(GenDate.ToStringTicksToPeriodVerbose((num >= 0) ? num : 0, true, true), ColoredText.DateTimeColor));
		if (Widgets.ButtonText(rect2.TakeBottomPart(40f), TaggedString.op_Implicit(Translator.Translate("VEF.CancelContract")), true, true, true, (TextAnchor?)null))
		{
			Find.WindowStack.Add((Window)(object)Dialog_MessageBox.CreateConfirmation(Translator.Translate("VEF.NoRefund"), (Action)delegate
			{
				((Window)this).Close(true);
				contract.endTicks = Find.TickManager.TicksAbs;
			}, true, TaggedString.op_Implicit(Translator.Translate("VEF.CancelContract")), (WindowLayer)1));
		}
		Text.Anchor = anchor;
		Text.Font = font;
	}
}
