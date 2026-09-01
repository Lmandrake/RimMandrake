using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace Outposts;

public class WITab_Outpost_Gear : WITab
{
	private static readonly List<Apparel> tmpApparel = new List<Apparel>();

	private static readonly List<ThingWithComps> tmpExistingEquipment = new List<ThingWithComps>();

	private static readonly List<Apparel> tmpExistingApparel = new List<Apparel>();

	private List<Thing> allThings;

	private Thing draggedItem;

	private Vector2 draggedItemPosOffset;

	private bool droppedDraggedItem;

	private Vector2 leftPaneScrollPosition;

	private float leftPaneScrollViewHeight;

	private float leftPaneWidth;

	private Vector2 rightPaneScrollPosition;

	private float rightPaneScrollViewHeight;

	private float rightPaneWidth;

	public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

	private List<Pawn> Pawns => SelOutpost.AllPawns.Where((Pawn p) => p.apparel != null && p.equipment != null && p.health != null && p.guest != null).ToList();

	public WITab_Outpost_Gear()
	{
		((InspectTabBase)this).labelKey = "TabCaravanGear";
	}

	public override void UpdateSize()
	{
		((InspectTabBase)this).UpdateSize();
		leftPaneWidth = 469f;
		rightPaneWidth = 345f;
		((InspectTabBase)this).size.x = leftPaneWidth + rightPaneWidth;
		((InspectTabBase)this).size.y = Mathf.Min(550f, ((InspectTabBase)this).PaneTopY - 30f);
	}

	public override void OnOpen()
	{
		((InspectTabBase)this).OnOpen();
		draggedItem = null;
	}

	private void DoLeftPane()
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Invalid comparison between Unknown and I4
		Rect val = GenUI.ContractedBy(new Rect(0f, 0f, leftPaneWidth, ((InspectTabBase)this).size.y), 10f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref val)).width - 16f, leftPaneScrollViewHeight);
		float curY = 0f;
		Widgets.BeginScrollView(val, ref leftPaneScrollPosition, val2, true);
		DoPawnRows(ref curY, val2, val);
		if ((int)Event.current.type == 8)
		{
			leftPaneScrollViewHeight = curY + 30f;
		}
		Widgets.EndScrollView();
	}

	private void DoPawnRow(ref float curY, Rect viewRect, Rect scrollOutRect, Pawn p)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		float num = leftPaneScrollPosition.y - 40f;
		float num2 = leftPaneScrollPosition.y + ((Rect)(ref scrollOutRect)).height;
		if (curY > num && curY < num2)
		{
			DoPawnRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 40f), p);
		}
		curY += 40f;
	}

	private void DoPawnRow(Rect rect, Pawn p)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0232: Unknown result type (might be due to invalid IL or missing references)
		//IL_025a: Unknown result type (might be due to invalid IL or missing references)
		GUI.BeginGroup(rect);
		Rect val = GenUI.AtZero(rect);
		Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, (Thing)(object)p);
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
		bool flag = draggedItem != null && ((Rect)(ref val)).Contains(Event.current.mousePosition) && CurrentWearerOf(draggedItem) != p;
		if ((Mouse.IsOver(val) && draggedItem == null) || flag)
		{
			Widgets.DrawHighlight(val);
		}
		if (flag && droppedDraggedItem)
		{
			TryEquipDraggedItem(p);
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Tiny, (Map)null);
		}
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
		Widgets.ThingIcon(val2, (Thing)(object)p, 1f, (Rot4?)null, false, 1f, false);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref val2)).xMax + 4f, 11f, 100f, 18f);
		GenMapUI.DrawPawnLabel(p, val3, 1f, 100f, (Dictionary<string, string>)null, (GameFont)1, false, false);
		float curX = ((Rect)(ref val3)).xMax;
		if (p.equipment != null)
		{
			List<ThingWithComps> allEquipmentListForReading = p.equipment.AllEquipmentListForReading;
			for (int i = 0; i < allEquipmentListForReading.Count; i++)
			{
				DoEquippedGear((Thing)(object)allEquipmentListForReading[i], p, ref curX);
			}
		}
		if (p.apparel != null)
		{
			tmpApparel.Clear();
			tmpApparel.AddRange(p.apparel.WornApparel);
			GenCollection.SortBy<Apparel, int, float>(tmpApparel, (Func<Apparel, int>)((Apparel x) => ((Thing)x).def.apparel.LastLayer.drawOrder), (Func<Apparel, float>)((Apparel x) => 0f - ((Thing)x).def.apparel.HumanBodyCoverage));
			for (int j = 0; j < tmpApparel.Count; j++)
			{
				DoEquippedGear((Thing)(object)tmpApparel[j], p, ref curX);
			}
		}
		if (p.Downed)
		{
			GUI.color = new Color(1f, 0f, 0f, 0.5f);
			Widgets.DrawLineHorizontal(0f, ((Rect)(ref rect)).height / 2f, ((Rect)(ref rect)).width);
			GUI.color = Color.white;
		}
		GUI.EndGroup();
	}

	private void DoInventoryRows(ref float curY, Rect scrollViewRect, Rect scrollOutRect)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanWeaponsAndApparel")));
		bool flag = false;
		for (int i = 0; i < allThings.Count; i++)
		{
			Thing val = allThings[i];
			if (IsVisibleWeapon(val.def))
			{
				if (!flag)
				{
					flag = true;
				}
				DoInventoryRow(ref curY, scrollViewRect, scrollOutRect, val);
			}
		}
		bool flag2 = false;
		for (int j = 0; j < allThings.Count; j++)
		{
			Thing val2 = allThings[j];
			if (val2.def.IsApparel)
			{
				if (!flag2)
				{
					flag2 = true;
				}
				DoInventoryRow(ref curY, scrollViewRect, scrollOutRect, val2);
			}
		}
		if (!flag && !flag2)
		{
			Widgets.NoneLabel(ref curY, ((Rect)(ref scrollViewRect)).width, (string)null);
		}
	}

	private void DoEquippedGear(Thing t, Pawn p, ref float curX)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(curX, 4f, 32f, 32f);
		bool flag = Mouse.IsOver(val);
		float num = ((t == draggedItem) ? 0.2f : ((!flag || draggedItem != null) ? 1f : 0.75f));
		Widgets.ThingIcon(val, t, num, (Rot4?)null, false, 1f, false);
		curX += 32f;
		if (Mouse.IsOver(val))
		{
			TooltipHandler.TipRegion(val, TipSignal.op_Implicit(((Entity)t).LabelCap));
		}
		if ((int)Event.current.type == 0 && Event.current.button == 0 && flag)
		{
			draggedItem = t;
			droppedDraggedItem = false;
			draggedItemPosOffset = Event.current.mousePosition - ((Rect)(ref val)).position;
			Event.current.Use();
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
		}
	}

	private void CheckDraggedItemStillValid()
	{
		if (draggedItem != null)
		{
			if (draggedItem.Destroyed)
			{
				draggedItem = null;
			}
			else if (CurrentWearerOf(draggedItem) == null && !allThings.Contains(draggedItem))
			{
				draggedItem = null;
			}
		}
	}

	private void CheckDropDraggedItem()
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Invalid comparison between Unknown and I4
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Invalid comparison between Unknown and I4
		if (draggedItem != null && ((int)Event.current.type == 1 || (int)Event.current.rawType == 1))
		{
			droppedDraggedItem = true;
		}
	}

	private void TryEquipDraggedItem(Pawn p)
	{
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_022c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0237: Unknown result type (might be due to invalid IL or missing references)
		//IL_023c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0440: Unknown result type (might be due to invalid IL or missing references)
		//IL_044a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0465: Unknown result type (might be due to invalid IL or missing references)
		//IL_0475: Unknown result type (might be due to invalid IL or missing references)
		//IL_047f: Expected O, but got Unknown
		//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_02da: Unknown result type (might be due to invalid IL or missing references)
		//IL_02df: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c1: Expected O, but got Unknown
		droppedDraggedItem = false;
		string text = default(string);
		if (!EquipmentUtility.CanEquip(draggedItem, p, ref text, true))
		{
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(GenText.CapitalizeFirst(text)))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
			draggedItem = null;
			return;
		}
		if (draggedItem.def.IsWeapon)
		{
			if (p.guest.IsPrisoner)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessagePrisonerCannotEquipWeapon", NamedArgumentUtility.Named((object)p, "PAWN"))))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (p.WorkTagIsDisabled((WorkTags)8))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfViolence", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (p.WorkTagIsDisabled((WorkTags)524288) && draggedItem.def.IsRangedWeapon)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfShooting", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (!p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
			{
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantEquipIncapableOfManipulation")), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
		}
		Thing obj = draggedItem;
		Apparel val = (Apparel)(object)((obj is Apparel) ? obj : null);
		if (val != null && p.apparel != null)
		{
			if (!ApparelUtility.HasPartsToWear(p, ((Thing)val).def))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantWearApparelMissingBodyParts", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (CurrentWearerOf((Thing)(object)val) != null && CurrentWearerOf((Thing)(object)val).apparel.IsLocked(val))
			{
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantUnequipLockedApparel")), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (p.apparel.WouldReplaceLockedApparel(val))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageWouldReplaceLockedApparel", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			tmpExistingApparel.Clear();
			tmpExistingApparel.AddRange(p.apparel.WornApparel);
			for (int i = 0; i < tmpExistingApparel.Count; i++)
			{
				if (!ApparelUtility.CanWearTogether(((Thing)val).def, ((Thing)tmpExistingApparel[i]).def, p.RaceProps.body))
				{
					p.apparel.Remove(tmpExistingApparel[i]);
					SelOutpost.AddItem((Thing)(object)tmpExistingApparel[i]);
				}
			}
			p.apparel.Wear((Apparel)SelOutpost.TakeItem((Thing)(object)val), false, false);
			Pawn_OutfitTracker outfits = p.outfits;
			if (outfits != null)
			{
				outfits.forcedHandler.SetForced(val, true);
			}
		}
		else
		{
			Thing val2 = draggedItem;
			ThingWithComps thingWithComps = (ThingWithComps)(object)((val2 is ThingWithComps) ? val2 : null);
			if (thingWithComps != null && p.equipment != null)
			{
				string personaWeaponConfirmationText = EquipmentUtility.GetPersonaWeaponConfirmationText(draggedItem, p);
				if (!GenText.NullOrEmpty(personaWeaponConfirmationText))
				{
					_ = draggedItem;
					Find.WindowStack.Add((Window)new Dialog_MessageBox(TaggedString.op_Implicit(personaWeaponConfirmationText), TaggedString.op_Implicit(Translator.Translate("Yes")), (Action)delegate
					{
						TryEquipDraggedItem_Equipment(p, thingWithComps);
					}, TaggedString.op_Implicit(Translator.Translate("No")), (Action)null, (string)null, false, (Action)null, (Action)null, (WindowLayer)1));
					draggedItem = null;
					return;
				}
				TryEquipDraggedItem_Equipment(p, thingWithComps);
			}
			else
			{
				Log.Warning(string.Concat("Could not make ", p, " equip or wear ", draggedItem));
			}
		}
		draggedItem = null;
	}

	private void TryEquipDraggedItem_Equipment(Pawn p, ThingWithComps eq)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f8: Expected O, but got Unknown
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		string text = default(string);
		if (!EquipmentUtility.CanEquip(draggedItem, p, ref text, true))
		{
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(GenText.CapitalizeFirst(text)))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
			draggedItem = null;
			return;
		}
		if (((Thing)eq).def.IsWeapon)
		{
			if (p.guest.IsPrisoner)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipCustom", NamedArgument.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessagePrisonerCannotEquipWeapon", NamedArgumentUtility.Named((object)p, "PAWN"))))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (p.WorkTagIsDisabled((WorkTags)8))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfViolence", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (p.WorkTagIsDisabled((WorkTags)524288) && draggedItem.def.IsRangedWeapon)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessageCantEquipIncapableOfShooting", NamedArgument.op_Implicit(((Entity)p).LabelShort), NamedArgument.op_Implicit((Thing)(object)p))), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
			if (!p.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation))
			{
				Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantEquipIncapableOfManipulation")), LookTargets.op_Implicit((Thing)(object)p), MessageTypeDefOf.RejectInput, false);
				draggedItem = null;
				return;
			}
		}
		tmpExistingEquipment.Clear();
		tmpExistingEquipment.AddRange(p.equipment.AllEquipmentListForReading);
		for (int i = 0; i < tmpExistingEquipment.Count; i++)
		{
			p.equipment.Remove(tmpExistingEquipment[i]);
			SelOutpost.AddItem((Thing)(object)tmpExistingEquipment[i]);
		}
		p.equipment.AddEquipment((ThingWithComps)SelOutpost.TakeItem((Thing)(object)eq));
		draggedItem = null;
	}

	private static bool IsVisibleWeapon(ThingDef t)
	{
		if (t.IsWeapon && t != ThingDefOf.WoodLog)
		{
			return t != ThingDefOf.Beer;
		}
		return false;
	}

	private static Pawn CurrentWearerOf(Thing t)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Expected O, but got Unknown
		IThingHolder parentHolder = t.ParentHolder;
		if ((parentHolder is Pawn_EquipmentTracker || parentHolder is Pawn_ApparelTracker) ? true : false)
		{
			return (Pawn)parentHolder.ParentHolder;
		}
		return null;
	}

	private void MoveDraggedItemToInventory()
	{
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Expected O, but got Unknown
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		droppedDraggedItem = false;
		Thing obj = draggedItem;
		Apparel val = (Apparel)(object)((obj is Apparel) ? obj : null);
		Pawn val2 = CurrentWearerOf(draggedItem);
		if (val2 != null)
		{
			if (val != null)
			{
				if (val2.apparel.IsLocked(val))
				{
					Messages.Message(TaggedString.op_Implicit(Translator.Translate("MessageCantUnequipLockedApparel")), LookTargets.op_Implicit((Thing)(object)CurrentWearerOf((Thing)(object)val)), MessageTypeDefOf.RejectInput, false);
					draggedItem = null;
					return;
				}
				val2.apparel.Remove(val);
			}
			else
			{
				val2.equipment.Remove((ThingWithComps)draggedItem);
			}
		}
		SelOutpost.AddItem(draggedItem);
		draggedItem = null;
	}

	private void DoInventoryRow(ref float curY, Rect viewRect, Rect scrollOutRect, Thing t)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		float num = rightPaneScrollPosition.y - 30f;
		float num2 = rightPaneScrollPosition.y + ((Rect)(ref scrollOutRect)).height;
		if (curY > num && curY < num2)
		{
			DoInventoryRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 30f), t);
		}
		curY += 30f;
	}

	private void DoInventoryRow(Rect rect, Thing t)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0155: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		GUI.BeginGroup(rect);
		Rect val = GenUI.AtZero(rect);
		Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, t);
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
		if (draggedItem == null && Mouse.IsOver(val))
		{
			Widgets.DrawHighlight(val);
		}
		float num = ((t == draggedItem) ? 0.5f : 1f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
		Widgets.ThingIcon(val2, t, num, (Rot4?)null, false, 1f, false);
		GUI.color = new Color(1f, 1f, 1f, num);
		Rect val3 = new Rect(((Rect)(ref val2)).xMax + 4f, 0f, 250f, 30f);
		Text.Anchor = (TextAnchor)3;
		Text.WordWrap = false;
		Widgets.Label(val3, ((Entity)t).LabelCap);
		Text.Anchor = (TextAnchor)0;
		Text.WordWrap = true;
		GUI.color = Color.white;
		if ((int)Event.current.type == 0 && Event.current.button == 0 && Mouse.IsOver(val))
		{
			draggedItem = t;
			droppedDraggedItem = false;
			draggedItemPosOffset = new Vector2(16f, 16f);
			Event.current.Use();
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Click, (Map)null);
		}
		GUI.EndGroup();
	}

	private void DoPawnRows(ref float curY, Rect scrollViewRect, Rect scrollOutRect)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		List<Pawn> pawns = Pawns;
		Text.Font = (GameFont)0;
		GUI.color = Color.gray;
		Widgets.Label(new Rect(135f, curY + 6f, 200f, 100f), Translator.Translate("DragToRearrange"));
		GUI.color = Color.white;
		Text.Font = (GameFont)1;
		Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanColonists")));
		for (int i = 0; i < pawns.Count; i++)
		{
			Pawn val = pawns[i];
			if (val.IsColonist)
			{
				DoPawnRow(ref curY, scrollViewRect, scrollOutRect, val);
			}
		}
		bool flag = false;
		for (int j = 0; j < pawns.Count; j++)
		{
			Pawn val2 = pawns[j];
			if (val2.IsPrisoner)
			{
				if (!flag)
				{
					Widgets.ListSeparator(ref curY, ((Rect)(ref scrollViewRect)).width, TaggedString.op_Implicit(Translator.Translate("CaravanPrisoners")));
					flag = true;
				}
				DoPawnRow(ref curY, scrollViewRect, scrollOutRect, val2);
			}
		}
	}

	public override void ExtraOnGUI()
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		((InspectTabBase)this).ExtraOnGUI();
		if (draggedItem != null)
		{
			Vector2 mousePosition = Event.current.mousePosition;
			Rect rect = new Rect(mousePosition.x - draggedItemPosOffset.x, mousePosition.y - draggedItemPosOffset.y, 32f, 32f);
			Find.WindowStack.ImmediateWindow(1283641090, rect, (WindowLayer)3, (Action)delegate
			{
				//IL_000f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0014: Unknown result type (might be due to invalid IL or missing references)
				if (draggedItem != null)
				{
					Widgets.ThingIcon(GenUI.AtZero(rect), draggedItem, 1f, (Rot4?)null, false, 1f, false);
				}
			}, false, false, 0f, (Action)null, false);
		}
		CheckDropDraggedItem();
	}

	private void DoRightPane()
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Invalid comparison between Unknown and I4
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		Rect val = GenUI.ContractedBy(new Rect(0f, 0f, rightPaneWidth, ((InspectTabBase)this).size.y), 10f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref val)).width - 16f, rightPaneScrollViewHeight);
		if (draggedItem != null && ((Rect)(ref val)).Contains(Event.current.mousePosition) && CurrentWearerOf(draggedItem) != null)
		{
			Widgets.DrawHighlight(val);
			if (droppedDraggedItem)
			{
				MoveDraggedItemToInventory();
				SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Tiny, (Map)null);
			}
		}
		float curY = 0f;
		Widgets.BeginScrollView(val, ref rightPaneScrollPosition, val2, true);
		DoInventoryRows(ref curY, val2, val);
		if ((int)Event.current.type == 8)
		{
			rightPaneScrollViewHeight = curY + 30f;
		}
		Widgets.EndScrollView();
	}

	public override void FillTab()
	{
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		if (allThings == null)
		{
			allThings = new List<Thing>(SelOutpost.Things.Count());
		}
		allThings.Clear();
		allThings.AddRange(SelOutpost.Things);
		Text.Font = (GameFont)1;
		CheckDraggedItemStillValid();
		CheckDropDraggedItem();
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(0f, 0f, leftPaneWidth, ((InspectTabBase)this).size.y);
		GUI.BeginGroup(val);
		DoLeftPane();
		GUI.EndGroup();
		GUI.BeginGroup(new Rect(((Rect)(ref val)).xMax, 0f, rightPaneWidth, ((InspectTabBase)this).size.y));
		DoRightPane();
		GUI.EndGroup();
		if (draggedItem != null && droppedDraggedItem)
		{
			droppedDraggedItem = false;
			draggedItem = null;
		}
	}
}
