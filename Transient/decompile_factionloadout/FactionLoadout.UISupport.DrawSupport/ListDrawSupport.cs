using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class ListDrawSupport
{
	public static CustomFloatMenu DrawDefRefList<T>(Rect rect, bool active, ref Vector2 scroll, IList<DefRef<T>> current, IList<T> defaults, IEnumerable<T> allDefs, bool isGlobal, Func<T, MenuItemBase> makeItem = null, Func<T, string> labelFunc = null, Func<T, string> warningFunc = null) where T : Def, new()
	{
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_022e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		//IL_023d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_0324: Unknown result type (might be due to invalid IL or missing references)
		//IL_032b: Unknown result type (might be due to invalid IL or missing references)
		//IL_026f: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0291: Unknown result type (might be due to invalid IL or missing references)
		//IL_0292: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d4: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			CustomFloatMenu result = null;
			Rect val = new Rect(((Rect)(ref rect)).x + 3f, ((Rect)(ref rect)).y + 3f, 130f, 26f);
			TaggedString val2 = Translator.Translate("Add");
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(((TaggedString)(ref val2)).CapitalizeFirst() + "..."), true, true, true, (TextAnchor?)null))
			{
				result = CustomFloatMenu.Open(CustomFloatMenu.MakeItems(allDefs, makeItem ?? ((Func<T, MenuItemBase>)((T d) => new MenuItemText(d, GetLabel(d), DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)))), delegate(MenuItemBase raw)
				{
					T def2 = raw.GetPayload<T>();
					if (current.All((DefRef<T> r) => r.DefName != ((Def)def2).defName))
					{
						current.Add(new DefRef<T>(def2));
					}
				});
			}
			((Rect)(ref rect)).yMin = ((Rect)(ref rect)).yMin + 30f;
			Widgets.BeginScrollView(rect, ref scroll, new Rect(0f, 0f, 100f, (float)(26 * current.Count)), true);
			Rect val3 = default(Rect);
			((Rect)(ref val3))._002Ector(26f, 3f, 1000f, 30f);
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(3f, 3f, 20f, 20f);
			DefRef<T> defRef = null;
			foreach (DefRef<T> item in current)
			{
				string text = ((!item.HasValue) ? null : warningFunc?.Invoke(item.Def));
				if (!string.IsNullOrEmpty(text))
				{
					Widgets.DrawBoxSolid(new Rect(1f, ((Rect)(ref val3)).y - 1f, ((Rect)(ref rect)).width - 6f, 24f), new Color(0.7f, 0.2f, 0.2f, 0.28f));
				}
				GUI.color = Color.red;
				if (Widgets.ButtonText(val4, " X", true, true, true, (TextAnchor?)null))
				{
					defRef = item;
				}
				GUI.color = Color.white;
				if (item.IsMissing)
				{
					GUI.color = new Color(1f, 0.5f, 0.5f);
					Widgets.Label(val3, TranslatorFormattedStringExtensions.Translate("FactionLoadout_DefRef_Missing", NamedArgument.op_Implicit(item.DefName), NamedArgument.op_Implicit(item.ModName ?? TaggedString.op_Implicit(Translator.Translate("FactionLoadout_DefRef_UnknownMod")))));
					GUI.color = Color.white;
				}
				else if (item.HasValue)
				{
					T def3 = item.Def;
					if (def3 is BodyTypeDef)
					{
						Widgets.Label(val3, GetLabel(def3));
					}
					else
					{
						object obj = def3;
						StyleItemDef val5 = (StyleItemDef)((obj is StyleItemDef) ? obj : null);
						if (val5 != null)
						{
							Rect val6 = val3;
							((Rect)(ref val6)).xMin = ((Rect)(ref val6)).xMin + 34f;
							Rect val7 = val3;
							((Rect)(ref val7)).width = ((Rect)(ref val7)).height;
							Widgets.DrawTextureFitted(val7, (Texture)(object)val5.Icon, 1f, 1f);
							Widgets.Label(val6, ((Def)val5).LabelCap);
						}
						else
						{
							Widgets.DefLabelWithIcon(val3, (Def)(object)def3, 2f, 6f);
						}
					}
				}
				if (!string.IsNullOrEmpty(text))
				{
					TooltipHandler.TipRegion(new Rect(1f, ((Rect)(ref val3)).y - 1f, ((Rect)(ref rect)).width - 6f, 24f), TipSignal.op_Implicit(text));
				}
				((Rect)(ref val3)).y = ((Rect)(ref val3)).y + 26f;
				((Rect)(ref val4)).y = ((Rect)(ref val4)).y + 26f;
			}
			Widgets.EndScrollView();
			if (defRef != null)
			{
				current.Remove(defRef);
			}
			return result;
		}
		string text2 = (isGlobal ? "---" : ("[Default] " + MakeDefaultString(defaults)));
		Widgets.Label(rect.GetCentered(text2), text2);
		return null;
		string GetLabel(T def)
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			if (labelFunc != null)
			{
				return labelFunc(def);
			}
			return TaggedString.op_Implicit(((Def)def).LabelCap) ?? ((Def)def).defName;
		}
		string MakeDefaultString(IList<T> list)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			if (list == null || list.Count == 0)
			{
				return string.Format("<i>{0}</i>", Translator.Translate("FactionLoadout_None"));
			}
			string text3 = string.Join(", ", list.Select(GetLabel));
			if (text3.Length > 43)
			{
				text3 = text3.Substring(0, 40) + "...";
			}
			return text3;
		}
	}

	public static CustomFloatMenu DrawDefList<T>(Rect rect, bool active, ref Vector2 scroll, IList<T> current, IList<T> defaultThings, IEnumerable<T> allThings, bool allowDupes, bool isGlobal, Func<T, MenuItemBase> makeItems = null) where T : Def
	{
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0153: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_020c: Unknown result type (might be due to invalid IL or missing references)
		//IL_020d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0222: Unknown result type (might be due to invalid IL or missing references)
		//IL_0223: Unknown result type (might be due to invalid IL or missing references)
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		//IL_024b: Unknown result type (might be due to invalid IL or missing references)
		//IL_024f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e1: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			CustomFloatMenu result = null;
			Rect val = new Rect(((Rect)(ref rect)).x + 3f, ((Rect)(ref rect)).y + 3f, 130f, 26f);
			TaggedString val2 = Translator.Translate("Add");
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(((TaggedString)(ref val2)).CapitalizeFirst() + "..."), true, true, true, (TextAnchor?)null))
			{
				result = CustomFloatMenu.Open(CustomFloatMenu.MakeItems(allThings, makeItems ?? ((Func<T, MenuItemBase>)((T d) => new MenuItemText(d, TaggedString.op_Implicit(((Def)d).LabelCap), DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)))), delegate(MenuItemBase raw)
				{
					T payload = raw.GetPayload<T>();
					if (allowDupes || !current.Contains(payload))
					{
						current.Add(payload);
					}
				});
			}
			((Rect)(ref rect)).yMin = ((Rect)(ref rect)).yMin + 30f;
			Widgets.BeginScrollView(rect, ref scroll, new Rect(0f, 0f, 100f, (float)(26 * current.Count)), true);
			Rect val3 = default(Rect);
			((Rect)(ref val3))._002Ector(26f, 3f, 1000f, 30f);
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(3f, 3f, 20f, 20f);
			T val5 = default(T);
			foreach (T item in current)
			{
				GUI.color = Color.red;
				if (Widgets.ButtonText(val4, " X", true, true, true, (TextAnchor?)null))
				{
					val5 = item;
				}
				GUI.color = Color.white;
				if (item is BodyTypeDef)
				{
					GUI.color = Color.white;
					Widgets.Label(val3, TaggedString.op_Implicit(((Def)item).LabelCap) ?? ((Def)item).defName);
				}
				else if (item != null && !(item is StyleItemDef))
				{
					Widgets.DefLabelWithIcon(val3, (Def)(object)item, 2f, 6f);
				}
				else
				{
					object obj = item;
					StyleItemDef val6 = (StyleItemDef)((obj is StyleItemDef) ? obj : null);
					if (val6 != null)
					{
						Rect val7 = val3;
						((Rect)(ref val7)).xMin = ((Rect)(ref val7)).xMin + 34f;
						Rect val8 = val3;
						((Rect)(ref val8)).width = ((Rect)(ref val8)).height;
						Widgets.DrawTextureFitted(val8, (Texture)(object)val6.Icon, 1f, 1f);
						Widgets.Label(val7, ((Def)val6).LabelCap);
					}
				}
				((Rect)(ref val3)).y = ((Rect)(ref val3)).y + 26f;
				((Rect)(ref val4)).y = ((Rect)(ref val4)).y + 26f;
			}
			Widgets.EndScrollView();
			if (val5 != null)
			{
				current.Remove(val5);
			}
			return result;
		}
		string text = (isGlobal ? "---" : ("[Default] " + MakeString(defaultThings)));
		Widgets.Label(rect.GetCentered(text), text);
		return null;
		static string MakeString(IList<T> list)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			if (list == null || list.Count == 0)
			{
				return string.Format("<i>{0}</i>", Translator.Translate("FactionLoadout_None"));
			}
			string text2 = string.Join(", ", list);
			if (text2.Length > 43)
			{
				text2 = text2.Substring(0, 40) + "...";
			}
			return text2;
		}
	}

	public static void DrawColorList(Rect rect, bool active, ref Vector2 scroll, IList<Color> current, IList<Color> defaultColors, bool isGlobal)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0241: Unknown result type (might be due to invalid IL or missing references)
		//IL_0244: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Unknown result type (might be due to invalid IL or missing references)
		//IL_019b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			Rect val = new Rect(((Rect)(ref rect)).x + 3f, ((Rect)(ref rect)).y + 3f, 130f, 26f);
			TaggedString val2 = Translator.Translate("Add");
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(((TaggedString)(ref val2)).CapitalizeFirst() + "..."), true, true, true, (TextAnchor?)null))
			{
				Find.WindowStack.Add((Window)(object)new Window_ColorPicker(Color32.op_Implicit(new Color32((byte)240, (byte)216, (byte)122, byte.MaxValue)), delegate(Color selected)
				{
					//IL_0012: Unknown result type (might be due to invalid IL or missing references)
					selected.a = 1f;
					current.Add(selected);
				}));
			}
			((Rect)(ref rect)).yMin = ((Rect)(ref rect)).yMin + 30f;
			Widgets.BeginScrollView(rect, ref scroll, new Rect(0f, 0f, 100f, (float)(38 * current.Count)), true);
			Rect val3 = default(Rect);
			((Rect)(ref val3))._002Ector(26f, 3f, ((Rect)(ref rect)).width, 36f);
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(3f, 3f, 20f, 20f);
			for (int i = 0; i < current.Count; i++)
			{
				Color val5 = current[i];
				int currentPosition = i;
				GUI.color = Color.red;
				if (Widgets.ButtonText(val4, " X", true, true, true, (TextAnchor?)null))
				{
					current.RemoveAt(i);
					i--;
					continue;
				}
				GUI.color = Color.white;
				Rect val6 = GenUI.ExpandedBy(val3, -4f, -2f);
				Widgets.DrawBoxSolid(val6, val5);
				Widgets.DrawHighlightIfMouseover(val6);
				if (Widgets.ButtonInvisible(val6, true))
				{
					Find.WindowStack.Add((Window)(object)new Window_ColorPicker(val5, delegate(Color selected)
					{
						//IL_001d: Unknown result type (might be due to invalid IL or missing references)
						selected.a = 1f;
						current[currentPosition] = selected;
					}));
				}
				((Rect)(ref val3)).y = ((Rect)(ref val3)).y + 38f;
				((Rect)(ref val4)).y = ((Rect)(ref val4)).y + 38f;
			}
			Widgets.EndScrollView();
		}
		else
		{
			string text = (isGlobal ? "---" : ("[Default] " + MakeString(defaultColors)));
			Widgets.Label(rect.GetCentered(text), text);
		}
		static string MakeString(IList<Color> list)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			if (list == null || list.Count == 0)
			{
				return string.Format("<i>{0}</i>", Translator.Translate("FactionLoadout_None"));
			}
			string text2 = string.Join(", ", list);
			if (text2.Length > 73)
			{
				text2 = text2.Substring(0, 70) + "...";
			}
			return text2;
		}
	}

	public static void DrawStringList(Rect rect, bool active, ref Vector2 scroll, IList<string> current, IList<string> defaultTags, IEnumerable<string> allTags, bool isGlobal)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			Rect val = new Rect(((Rect)(ref rect)).x + 3f, ((Rect)(ref rect)).y + 3f, 130f, 26f);
			TaggedString val2 = Translator.Translate("Add");
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(((TaggedString)(ref val2)).CapitalizeFirst() + "..."), true, true, true, (TextAnchor?)null))
			{
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(allTags, (string t) => new MenuItemText(t, t)), delegate(MenuItemBase raw)
				{
					string payload = raw.GetPayload<string>();
					if (!current.Contains(payload))
					{
						current.Add(payload);
					}
				});
			}
			((Rect)(ref rect)).yMin = ((Rect)(ref rect)).yMin + 30f;
			Widgets.BeginScrollView(rect, ref scroll, new Rect(0f, 0f, 100f, (float)(26 * current.Count)), true);
			Rect val3 = default(Rect);
			((Rect)(ref val3))._002Ector(26f, 3f, 1000f, 30f);
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(3f, 3f, 20f, 20f);
			string text = null;
			foreach (string item in current)
			{
				GUI.color = Color.red;
				if (Widgets.ButtonText(val4, " X", true, true, true, (TextAnchor?)null))
				{
					text = item;
				}
				GUI.color = Color.white;
				Widgets.Label(val3, item);
				((Rect)(ref val3)).y = ((Rect)(ref val3)).y + 26f;
				((Rect)(ref val4)).y = ((Rect)(ref val4)).y + 26f;
			}
			Widgets.EndScrollView();
			if (text != null)
			{
				current.Remove(text);
			}
		}
		else
		{
			string text2 = (isGlobal ? "---" : ("[Default] " + MakeString(defaultTags)));
			Widgets.Label(rect.GetCentered(text2), text2);
		}
		static string MakeString(IList<string> list)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			if (list == null || list.Count == 0)
			{
				return string.Format("<i>{0}</i>", Translator.Translate("FactionLoadout_None"));
			}
			string text3 = string.Join(", ", list);
			if (text3.Length > 73)
			{
				text3 = text3.Substring(0, 70) + "...";
			}
			return text3;
		}
	}
}
