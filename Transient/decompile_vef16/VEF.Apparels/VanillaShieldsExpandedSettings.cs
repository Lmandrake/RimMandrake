using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

public class VanillaShieldsExpandedSettings : ModSettings
{
	public static Dictionary<string, bool> usableWithShieldsWeapons = new Dictionary<string, bool>();

	public static List<ThingDef> allWeapons = new List<ThingDef>();

	private string searchKey;

	public bool showMeleeWeapons = true;

	public bool showRangedWeapons = true;

	private static Vector2 scrollPosition = Vector2.zero;

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Collections.Look<string, bool>(ref usableWithShieldsWeapons, "usableWithShieldsWeapons", (LookMode)1, (LookMode)1);
	}

	public void DoSettingsWindowContents(Rect inRect)
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0213: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Unknown result type (might be due to invalid IL or missing references)
		//IL_028b: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_043f: Unknown result type (might be due to invalid IL or missing references)
		//IL_044c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0453: Unknown result type (might be due to invalid IL or missing references)
		//IL_046b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0312: Unknown result type (might be due to invalid IL or missing references)
		//IL_0330: Unknown result type (might be due to invalid IL or missing references)
		//IL_0339: Unknown result type (might be due to invalid IL or missing references)
		//IL_0351: Unknown result type (might be due to invalid IL or missing references)
		//IL_035e: Unknown result type (might be due to invalid IL or missing references)
		//IL_037a: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_03da: Unknown result type (might be due to invalid IL or missing references)
		//IL_0348: Unknown result type (might be due to invalid IL or missing references)
		//IL_03fe: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height);
		Text.Anchor = (TextAnchor)3;
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref val)).x + 5f, ((Rect)(ref val)).y, 60f, 24f);
		Widgets.Label(val2, Translator.Translate("VEF.Shields.Search"));
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref val2)).xMax + 5f, ((Rect)(ref val2)).y, 200f, 24f);
		searchKey = Widgets.TextField(val3, searchKey);
		Text.Anchor = (TextAnchor)0;
		Rect val4 = default(Rect);
		((Rect)(ref val4))._002Ector(((Rect)(ref val3)).xMax + 15f, ((Rect)(ref val3)).y, 180f, 24f);
		Widgets.CheckboxLabeled(val4, TaggedString.op_Implicit(Translator.Translate("VEF.Shields.ShowMeleeWeapons")), ref showMeleeWeapons, false, (Texture2D)null, (Texture2D)null, false, false);
		Widgets.CheckboxLabeled(new Rect(((Rect)(ref val4)).xMax + 30f, ((Rect)(ref val3)).y, 180f, 24f), TaggedString.op_Implicit(Translator.Translate("VEF.Shields.ShowRangeWeapons")), ref showRangedWeapons, false, (Texture2D)null, (Texture2D)null, false, false);
		IEnumerable<ThingDef> source;
		if (!GenText.NullOrEmpty(searchKey))
		{
			source = allWeapons.Where((ThingDef x) => ((Def)x).label.ToLower().Contains(searchKey.ToLower()));
		}
		else
		{
			IEnumerable<ThingDef> enumerable = allWeapons;
			source = enumerable;
		}
		List<ThingDef> list = (from x in source
			where (x.IsRangedWeapon && showRangedWeapons) || (x.IsMeleeWeapon && showMeleeWeapons)
			orderby ((Def)x).label
			select x).ToList();
		Rect val5 = default(Rect);
		((Rect)(ref val5))._002Ector(((Rect)(ref val2)).x, ((Rect)(ref val2)).yMax + 5f, 265f, 24f);
		if (Widgets.ButtonText(val5, TaggedString.op_Implicit(Translator.Translate("VEF.Shields.ResetModSettingsToDefault")), true, true, true, (TextAnchor?)null))
		{
			usableWithShieldsWeapons.Clear();
			VanillaShieldsExpandedStartup.SetValues();
		}
		Widgets.Label(new Rect(((Rect)(ref val5)).xMax + 15f, ((Rect)(ref val5)).y, ((Rect)(ref inRect)).width - (((Rect)(ref val5)).width + 35f), 24f), Translator.Translate("VEF.Shields.ExplanationTitle"));
		float scrollHeight = GetScrollHeight(list);
		Rect val6 = default(Rect);
		((Rect)(ref val6))._002Ector(((Rect)(ref val)).x, ((Rect)(ref val3)).yMax + 35f, ((Rect)(ref val)).width, ((Rect)(ref val)).height - 70f);
		Rect val7 = default(Rect);
		((Rect)(ref val7))._002Ector(((Rect)(ref val)).x, ((Rect)(ref val6)).y, ((Rect)(ref val)).width - 16f, scrollHeight);
		Widgets.BeginScrollView(val6, ref scrollPosition, val7, true);
		Vector2 val8 = default(Vector2);
		((Vector2)(ref val8))._002Ector(((Rect)(ref val)).x + 5f, ((Rect)(ref val6)).y);
		float num = 0f;
		int num2 = 200;
		Rect val10 = default(Rect);
		Rect val11 = default(Rect);
		Rect val12 = default(Rect);
		for (int i = 0; i < list.Count; i++)
		{
			ThingDef val9 = list[i];
			bool num3 = num >= scrollPosition.y - (float)num2 && num <= scrollPosition.y + ((Rect)(ref val6)).height;
			float y = val8.y;
			if (num3)
			{
				((Rect)(ref val10))._002Ector(0f, val8.y + 5f, ((Rect)(ref val7)).width, 24f);
				if (Mouse.IsOver(val10))
				{
					Widgets.DrawHighlight(val10);
				}
				else if (i % 2 != 0)
				{
					Widgets.DrawLightHighlight(val10);
				}
				((Rect)(ref val11))._002Ector(val8.x + 5f, val8.y + 5f, 24f, 24f);
				Widgets.ThingIcon(val11, val9, (ThingDef)null, (ThingStyleDef)null, 1f, (Color?)null, (int?)null, 1f);
				((Rect)(ref val12))._002Ector(((Rect)(ref val11)).xMax + 15f, val8.y + 5f, ((Rect)(ref val7)).width - 80f, 24f);
				Widgets.Label(val12, ((Def)val9).LabelCap);
				if (!usableWithShieldsWeapons.TryGetValue(((Def)val9).defName, out var value))
				{
					VanillaShieldsExpandedStartup.SetValues();
				}
				Widgets.ToggleInvisibleDraggable(val10, ref value, true, true);
				Widgets.CheckboxDraw(((Rect)(ref val7)).width - 40f, ((Rect)(ref val12)).y, value, false, 24f, (Texture2D)null, (Texture2D)null);
				usableWithShieldsWeapons[((Def)val9).defName] = value;
			}
			new Vector2(val8.x + 10f, val8.y);
			val8.y += 24f;
			num += val8.y - y;
		}
		Widgets.EndScrollView();
	}

	private float GetScrollHeight(List<ThingDef> defs)
	{
		float num = 0f;
		foreach (ThingDef def in defs)
		{
			_ = def;
			num += 24f;
		}
		return num + 5f;
	}
}
