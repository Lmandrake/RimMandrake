using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace Outposts;

public class Dialog_TakeItems : Window
{
	private readonly Vector2 BottomButtonSize = new Vector2(160f, 40f);

	private readonly Caravan caravan;

	private readonly Outpost outpost;

	private TransferableOneWayWidget itemsTransfer;

	private List<TransferableOneWay> transferables;

	public override Vector2 InitialSize => new Vector2(1024f, (float)UI.screenHeight - 100f);

	public override float Margin => 17f;

	public Dialog_TakeItems(Outpost outpost, Caravan caravan)
		: base((IWindowDrawing)null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		outpost.CheckNoDestroyedOrNoStack();
		this.outpost = outpost;
		this.caravan = caravan;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		GUI.BeginGroup(inRect);
		Rect val = GenUI.AtZero(inRect);
		((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 30f;
		DoBottomButtons(val);
		itemsTransfer.OnGUI(val);
		GUI.EndGroup();
	}

	private void DoBottomButtons(Rect rect)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).width - BottomButtonSize.x, ((Rect)(ref rect)).height - 40f, BottomButtonSize.x, BottomButtonSize.y);
		if (Widgets.ButtonText(val, TaggedString.op_Implicit(Translator.Translate("Outposts.Take")), true, true, true, (TextAnchor?)null))
		{
			foreach (TransferableOneWay transferable in transferables)
			{
				while (((Transferable)transferable).HasAnyThing && ((Transferable)transferable).CountToTransfer > 0)
				{
					Thing val2 = GenCollection.Pop<Thing>(transferable.things);
					if (val2.stackCount <= ((Transferable)transferable).CountToTransfer)
					{
						((Transferable)transferable).AdjustBy(-val2.stackCount);
						ThingOwner holdingOwner = val2.holdingOwner;
						if (holdingOwner != null)
						{
							holdingOwner.Remove(val2);
						}
						caravan.AddPawnOrItem(outpost.TakeItem(val2), true);
					}
					else
					{
						caravan.AddPawnOrItem(val2.SplitOff(((Transferable)transferable).CountToTransfer), true);
						((Transferable)transferable).AdjustTo(0);
						transferable.things.Add(val2);
					}
				}
			}
			((Window)this).Close(true);
		}
		if (Widgets.ButtonText(new Rect(0f, ((Rect)(ref val)).y, BottomButtonSize.x, BottomButtonSize.y), TaggedString.op_Implicit(Translator.Translate("CancelButton")), true, true, true, (TextAnchor?)null))
		{
			((Window)this).Close(true);
		}
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).width / 2f - BottomButtonSize.x, ((Rect)(ref val)).y, BottomButtonSize.x, BottomButtonSize.y), TaggedString.op_Implicit(Translator.Translate("ResetButton")), true, true, true, (TextAnchor?)null))
		{
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Low, (Map)null);
			CalculateAndRecacheTransferables();
		}
	}

	public override void PostOpen()
	{
		((Window)this).PostOpen();
		CalculateAndRecacheTransferables();
	}

	private void CalculateAndRecacheTransferables()
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Expected O, but got Unknown
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Expected O, but got Unknown
		transferables = new List<TransferableOneWay>();
		foreach (Thing thing in outpost.Things)
		{
			TransferableOneWay val = TransferableUtility.TransferableMatching<TransferableOneWay>(thing, transferables, (TransferAsOneMode)1);
			if (val == null)
			{
				val = new TransferableOneWay();
				transferables.Add(val);
			}
			if (val.things.Contains(thing))
			{
				Log.Error("Tried to add the same thing twice to TransferableOneWay: " + (object)thing);
				return;
			}
			val.things.Add(thing);
		}
		itemsTransfer = new TransferableOneWayWidget((IEnumerable<TransferableOneWay>)transferables, outpost.Name, caravan.Name, TaggedString.op_Implicit(Translator.Translate("FormCaravanColonyThingCountTip")), false, (IgnorePawnsInventoryMode)3, false, (Func<float>)null, 0f, false, (PlanetTile?)null, false, false, false, false, false, false, false, false, false, false);
	}
}
