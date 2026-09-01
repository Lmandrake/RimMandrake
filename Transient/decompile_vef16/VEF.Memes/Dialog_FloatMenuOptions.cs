using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Memes;

public class Dialog_FloatMenuOptions : Window
{
	private static readonly FieldRef<FloatMenuOption, ThingDef> shownItemField = AccessTools.FieldRefAccess<FloatMenuOption, ThingDef>("shownItem");

	private readonly List<FloatMenuOption> options;

	private readonly Dictionary<FloatMenuOption, ThingDef> shownItems;

	private Vector2 scrollPosition = new Vector2(0f, 0f);

	private string searchText = "";

	public override Vector2 InitialSize => new Vector2(620f, 500f);

	public Dialog_FloatMenuOptions(List<FloatMenuOption> opts)
		: base((IWindowDrawing)null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		options = opts;
		shownItems = opts.ToDictionary((FloatMenuOption opt) => opt, (FloatMenuOption opt) => shownItemField.Invoke(opt));
		base.doCloseX = true;
		base.doCloseButton = true;
		base.closeOnClickedOutside = true;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		Text.Font = (GameFont)1;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(inRect);
		((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 20f;
		((Rect)(ref val)).yMax = ((Rect)(ref val)).yMax - 40f;
		((Rect)(ref val)).width = ((Rect)(ref val)).width - 16f;
		searchText = Widgets.TextField(GenUI.TopPartPixels(val, 35f), searchText);
		((Rect)(ref val)).yMin = ((Rect)(ref val)).yMin + 40f;
		List<FloatMenuOption> list = options.Where((FloatMenuOption opt) => opt.Label.ToLower().Contains(searchText.ToLower())).ToList();
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref val)).width - 16f, list.Sum((FloatMenuOption opt) => opt.RequiredHeight + 17f));
		Widgets.BeginScrollView(val, ref scrollPosition, val2, true);
		try
		{
			float num = 0f;
			Rect val3 = default(Rect);
			foreach (FloatMenuOption item in list)
			{
				float num2 = item.RequiredHeight + 10f;
				((Rect)(ref val3))._002Ector(0f, num, ((Rect)(ref val2)).width - 7f, num2);
				if (shownItems[item] != null)
				{
					((Rect)(ref val3)).xMax = ((Rect)(ref val3)).xMax - 31f;
					Widgets.InfoCardButton(((Rect)(ref val3)).xMax + 7f, ((Rect)(ref val3)).y + 1f, (Def)(object)shownItems[item]);
				}
				if (item.DoGUI(val3, false, (FloatMenu)null))
				{
					((Window)this).Close(true);
					break;
				}
				GUI.color = Color.white;
				num += num2 + 7f;
			}
		}
		finally
		{
			Widgets.EndScrollView();
		}
	}
}
