using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Outposts;

public class WITab_Outpost_Items : WITab
{
	private const float SortersSpace = 25f;

	private List<TransferableImmutable> cachedItems = new List<TransferableImmutable>();

	private int cachedItemsCount;

	private int cachedItemsHash;

	private Vector2 scrollPosition;

	private float scrollViewHeight;

	private TransferableSorterDef sorter1;

	private TransferableSorterDef sorter2;

	public Outpost SelOutpost => ((WITab)this).SelObject as Outpost;

	public WITab_Outpost_Items()
	{
		((InspectTabBase)this).labelKey = "TabCaravanItems";
	}

	public override void UpdateSize()
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		((InspectTabBase)this).UpdateSize();
		CheckCacheItems();
		((InspectTabBase)this).size = CaravanItemsTabUtility.GetSize(cachedItems, ((InspectTabBase)this).PaneTopY, true) - new Vector2(0f, 25f);
	}

	public override void FillTab()
	{
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		CheckCreateSorters();
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(0f, 0f, ((InspectTabBase)this).size.x, ((InspectTabBase)this).size.y);
		GUI.BeginGroup(GenUI.ContractedBy(val, 10f));
		TransferableUIUtility.DoTransferableSorters(sorter1, sorter2, (Action<TransferableSorterDef>)delegate(TransferableSorterDef x)
		{
			sorter1 = x;
			CacheItems();
		}, (Action<TransferableSorterDef>)delegate(TransferableSorterDef x)
		{
			sorter2 = x;
			CacheItems();
		});
		GUI.EndGroup();
		((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 25f;
		GUI.BeginGroup(val);
		CheckCacheItems();
		DoRows(((Rect)(ref val)).size);
		GUI.EndGroup();
	}

	private void CheckCacheItems()
	{
		List<Thing> list = SelOutpost.Things.ToList();
		if (list.Count != cachedItemsCount)
		{
			CacheItems();
			return;
		}
		int num = 0;
		for (int i = 0; i < list.Count; i++)
		{
			num = Gen.HashCombineInt(num, ((object)list[i]).GetHashCode());
		}
		if (num != cachedItemsHash)
		{
			CacheItems();
		}
	}

	private void CacheItems()
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Expected O, but got Unknown
		CheckCreateSorters();
		cachedItems.Clear();
		List<Thing> list = SelOutpost.Things.ToList();
		int num = 0;
		for (int i = 0; i < list.Count; i++)
		{
			TransferableImmutable val = TransferableUtility.TransferableMatching<TransferableImmutable>(list[i], cachedItems, (TransferAsOneMode)0);
			if (val == null)
			{
				val = new TransferableImmutable();
				cachedItems.Add(val);
			}
			val.things.Add(list[i]);
			num = Gen.HashCombineInt(num, ((object)list[i]).GetHashCode());
		}
		cachedItems = cachedItems.OrderBy((TransferableImmutable tr) => (Transferable)(object)tr, (IComparer<Transferable>)sorter1.Comparer).ThenBy((TransferableImmutable tr) => (Transferable)(object)tr, (IComparer<Transferable>)sorter2.Comparer).ThenBy((Func<TransferableImmutable, float>)TransferableUIUtility.DefaultListOrderPriority)
			.ToList();
		cachedItemsCount = list.Count;
		cachedItemsHash = num;
	}

	[MethodImpl(MethodImplOptions.AggressiveInlining)]
	private void CheckCreateSorters()
	{
		if (sorter1 == null)
		{
			sorter1 = TransferableSorterDefOf.Category;
		}
		if (sorter2 == null)
		{
			sorter2 = TransferableSorterDefOf.MarketValue;
		}
	}

	private void DoRows(Vector2 size)
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Invalid comparison between Unknown and I4
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		Text.Font = (GameFont)1;
		Rect val = GenUI.ContractedBy(new Rect(0f, 0f, size.x, size.y), 10f);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref val)).width - 16f, scrollViewHeight);
		Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
		float curY = 0f;
		Widgets.ListSeparator(ref curY, ((Rect)(ref val2)).width, TaggedString.op_Implicit(Translator.Translate("CaravanItems")));
		if (GenCollection.Any<TransferableImmutable>(cachedItems))
		{
			for (int i = 0; i < cachedItems.Count; i++)
			{
				DoRow(ref curY, val2, val, cachedItems[i]);
			}
		}
		else
		{
			Widgets.NoneLabel(ref curY, ((Rect)(ref val2)).width, (string)null);
		}
		if ((int)Event.current.type == 8)
		{
			scrollViewHeight = curY + 30f;
		}
		Widgets.EndScrollView();
	}

	private void DoRow(ref float curY, Rect viewRect, Rect scrollOutRect, TransferableImmutable thing)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		float num = scrollPosition.y - 30f;
		float num2 = scrollPosition.y + ((Rect)(ref scrollOutRect)).height;
		if (curY > num && curY < num2)
		{
			DoRow(new Rect(0f, curY, ((Rect)(ref viewRect)).width, 30f), thing);
		}
		curY += 30f;
	}

	private void DoRow(Rect rect, TransferableImmutable thing)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		GUI.BeginGroup(rect);
		Rect val = GenUI.AtZero(rect);
		Widgets.InfoCardButton(((Rect)(ref val)).width - 24f, (((Rect)(ref rect)).height - 24f) / 2f, ((Transferable)thing).AnyThing);
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 24f;
		Rect val2 = val;
		((Rect)(ref val2)).xMin = ((Rect)(ref val2)).xMax - 60f;
		CaravanThingsTabUtility.DrawMass(thing, val2);
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 60f;
		Widgets.DrawHighlightIfMouseover(val);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(4f, (((Rect)(ref rect)).height - 27f) / 2f, 27f, 27f);
		Widgets.ThingIcon(val3, ((Transferable)thing).AnyThing, 1f, (Rot4?)null, false, 1f, false);
		Rect val4 = default(Rect);
		((Rect)(ref val4))._002Ector(((Rect)(ref val3)).xMax + 4f, 0f, 300f, 30f);
		Text.Anchor = (TextAnchor)3;
		Text.WordWrap = false;
		Widgets.Label(val4, GenText.Truncate(thing.LabelCapWithTotalStackCount, ((Rect)(ref val4)).width, (Dictionary<string, string>)null));
		Text.Anchor = (TextAnchor)0;
		Text.WordWrap = true;
		GUI.EndGroup();
	}
}
