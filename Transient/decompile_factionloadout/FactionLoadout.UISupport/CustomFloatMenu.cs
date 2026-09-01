using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public class CustomFloatMenu : Window
{
	public List<MenuItemBase> Items;

	public Action<MenuItemBase> OnSelected;

	public bool CloseOnSelected = true;

	public int Columns = 2;

	public string SearchString = "";

	public Color Tint = Color.white;

	public bool AllowChangeTint;

	public bool StretchItems;

	private readonly List<MenuItemBase> preRenderItems = new List<MenuItemBase>();

	private float lastHeight;

	private float lastWidth;

	private Vector2 scroll;

	public static CustomFloatMenu Open(List<MenuItemBase> items, Action<MenuItemBase> onSelected, int columns = 2, bool stretchItems = false)
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		CustomFloatMenu customFloatMenu = new CustomFloatMenu
		{
			Items = items,
			OnSelected = onSelected,
			Columns = columns,
			StretchItems = stretchItems,
			closeOnAccept = false,
			closeOnCancel = true,
			closeOnClickedOutside = true,
			layer = (WindowLayer)2
		};
		Find.WindowStack.Add((Window)(object)customFloatMenu);
		return customFloatMenu;
	}

	public static string SearchMatch(string label, string search, bool highlight)
	{
		int num = label.IndexOf(search, StringComparison.OrdinalIgnoreCase);
		if (num < 0)
		{
			return null;
		}
		if (highlight)
		{
			return label.Insert(num + search.Length, "</color>").Insert(num, "<color=#57ff57>");
		}
		return label;
	}

	public static List<MenuItemBase> MakeItems<T>(IEnumerable<T> rawItems, Func<T, MenuItemBase> makeItem)
	{
		List<MenuItemBase> list = new List<MenuItemBase>();
		foreach (T rawItem in rawItems)
		{
			MenuItemBase menuItemBase = makeItem(rawItem);
			if (menuItemBase != null)
			{
				list.Add(menuItemBase);
			}
		}
		list.Sort();
		return list;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_023c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0241: Unknown result type (might be due to invalid IL or missing references)
		//IL_02de: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_024c: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0272: Unknown result type (might be due to invalid IL or missing references)
		//IL_028b: Unknown result type (might be due to invalid IL or missing references)
		//IL_028d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0292: Unknown result type (might be due to invalid IL or missing references)
		//IL_0294: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_027f: Unknown result type (might be due to invalid IL or missing references)
		if (Items == null || Items.Count == 0)
		{
			ModCore.Error("CustomFloatMenu tried to draw with no items! Window has been closed.");
			((Window)this).Close(true);
			return;
		}
		Rect val = inRect;
		((Rect)(ref val)).height = 28f;
		if (AllowChangeTint)
		{
			((Rect)(ref val)).width = ((Rect)(ref val)).width - 100f;
		}
		SearchString = Widgets.TextField(val, SearchString);
		((Rect)(ref inRect)).yMin = ((Rect)(ref inRect)).yMin + 36f;
		Rect val2 = val;
		((Rect)(ref val2)).xMin = ((Rect)(ref val2)).xMax + 5f;
		((Rect)(ref val2)).width = 90f;
		Widgets.DrawBoxSolidWithOutline(val2, Tint, Color.white, 2);
		Widgets.DrawHighlightIfMouseover(val2);
		if (Widgets.ButtonInvisible(val2, true))
		{
			Find.WindowStack.Add((Window)(object)new Window_ColorPicker(Tint, delegate(Color t)
			{
				//IL_0001: Unknown result type (might be due to invalid IL or missing references)
				//IL_0002: Unknown result type (might be due to invalid IL or missing references)
				Tint = t;
			})
			{
				layer = (WindowLayer)3
			});
		}
		preRenderItems.Clear();
		preRenderItems.AddRange(FilteredItems(SearchString));
		int num = Mathf.CeilToInt((float)preRenderItems.Count / (float)Columns);
		if (StretchItems)
		{
			float width = (((Rect)(ref inRect)).width - 16f - (float)(Columns - 1) * 12f) / (float)Columns;
			foreach (MenuItemBase preRenderItem in preRenderItems)
			{
				preRenderItem.SetWidth(width);
			}
		}
		float num2 = 6f;
		float num3 = 0f;
		float y = scroll.y;
		float num4 = scroll.y + ((Rect)(ref inRect)).height;
		Widgets.BeginScrollView(inRect, ref scroll, new Rect(0f, 0f, lastWidth, lastHeight), true);
		lastWidth = 0f;
		lastHeight = 0f;
		bool flag = false;
		Vector2 val3 = default(Vector2);
		for (int i = 0; i < Columns; i++)
		{
			float num5 = 0f;
			float num6 = 0f;
			for (int j = 0; j < num; j++)
			{
				int num7 = num * i + j;
				if (num7 >= preRenderItems.Count)
				{
					break;
				}
				MenuItemBase menuItemBase = preRenderItems[num7];
				Vector2 size = menuItemBase.GetSize();
				if (!flag && num6 + size.y > y && num6 < num4)
				{
					((Vector2)(ref val3))._002Ector(num3, num6);
					if (Tint != Color.white)
					{
						GUI.color = Tint;
					}
					Vector2 val4 = menuItemBase.Draw(val3);
					GUI.color = Color.white;
					Rect val5 = new Rect(val3, val4);
					Widgets.DrawBox(val5, 1, (Texture2D)null);
					if (Widgets.ButtonInvisible(val5, true))
					{
						OnSelected?.Invoke(menuItemBase);
						if (CloseOnSelected)
						{
							flag = true;
							((Window)this).Close(true);
						}
					}
				}
				num6 += size.y + num2;
				if (num5 < size.x)
				{
					num5 = size.x;
				}
				if (num6 > lastHeight)
				{
					lastHeight = num6;
				}
			}
			num3 += num5 + num2 * 2f;
			if (num3 > lastWidth)
			{
				lastWidth = num3;
			}
		}
		Widgets.EndScrollView();
	}

	public IEnumerable<MenuItemBase> FilteredItems(string search)
	{
		if (Items == null)
		{
			yield break;
		}
		bool all = string.IsNullOrWhiteSpace(search);
		string newSearch = search?.Trim();
		foreach (MenuItemBase item in Items)
		{
			if (all || item.Matches(newSearch))
			{
				yield return item;
			}
		}
	}

	public CustomFloatMenu()
		: base((IWindowDrawing)null)
	{
	}//IL_001a: Unknown result type (might be due to invalid IL or missing references)
	//IL_001f: Unknown result type (might be due to invalid IL or missing references)

}
