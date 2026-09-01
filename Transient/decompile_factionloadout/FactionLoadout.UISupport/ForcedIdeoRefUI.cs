using System;
using System.Collections.Generic;
using System.IO;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public static class ForcedIdeoRefUI
{
	public const string FactionPrimaryKey = "primary";

	public const float PickerItemWidth = 270f;

	public static bool DisabledByClassicMode
	{
		get
		{
			if (Current.Game != null)
			{
				return ForcedIdeoGameComponent.ClassicMode;
			}
			return false;
		}
	}

	public static void OpenPicker(bool includeFactionPrimary, Action<ForcedIdeoSource, string> onPick, Action onClear = null, string clearLabel = null)
	{
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0201: Unknown result type (might be due to invalid IL or missing references)
		List<MenuItemBase> list = new List<MenuItemBase>();
		TaggedString val;
		if (onClear != null)
		{
			string text = clearLabel;
			if (text == null)
			{
				val = Translator.Translate("FactionLoadout_None");
				text = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
			}
			list.Add(MakeItem(null, text, null, null));
		}
		if (includeFactionPrimary)
		{
			object payload = (ForcedIdeoSource.FactionPrimary, "primary");
			val = Translator.Translate("FactionLoadout_General_IdeoFactionPrimary");
			string label = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
			val = Translator.Translate("FactionLoadout_General_IdeoFactionPrimaryPickTooltip");
			list.Add(MakeItem(payload, label, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), null));
		}
		List<MenuItemBase> list2 = new List<MenuItemBase>();
		foreach (IdeoPresetDef item in DefDatabase<IdeoPresetDef>.AllDefsListForReading)
		{
			val = ((Def)item).LabelCap;
			string label2 = BuildPresetLabel(((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString());
			val = Translator.Translate("FactionLoadout_General_IdeoPresetPickTooltip");
			string text2 = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
			if (!GenText.NullOrEmpty(((Def)item).description))
			{
				text2 = text2 + "\n\n" + ((Def)item).description;
			}
			list2.Add(MakeItem((ForcedIdeoSource.Preset, ((Def)item).defName), label2, text2, item.Icon));
		}
		list2.Sort();
		list.AddRange(list2);
		List<MenuItemBase> list3 = new List<MenuItemBase>();
		foreach (FileInfo allCustomIdeoFile in GenFilePaths.AllCustomIdeoFiles)
		{
			string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(allCustomIdeoFile.Name);
			string label3 = BuildSavedFileLabel(fileNameWithoutExtension, isMissing: false);
			object payload2 = (ForcedIdeoSource.SavedFile, fileNameWithoutExtension);
			val = Translator.Translate("FactionLoadout_General_IdeoSavedPickTooltip");
			list3.Add(MakeItem(payload2, label3, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), null));
		}
		list3.Sort();
		list.AddRange(list3);
		if (list.Count == 0)
		{
			Messages.Message(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_General_IdeoNoTemplates")), MessageTypeDefOf.RejectInput, false);
			return;
		}
		CustomFloatMenu.Open(list, delegate(MenuItemBase item)
		{
			if (item.Payload == null)
			{
				onClear?.Invoke();
			}
			else
			{
				var (arg, arg2) = ((ForcedIdeoSource, string))item.Payload;
				onPick(arg, arg2);
				ForcedIdeoGameComponent.AnyIdeologyEditsActive = true;
			}
		}, 1, stretchItems: true);
	}

	public static MenuItemText MakeItem(object payload, string label, string tooltip, Texture2D icon)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		return new MenuItemText(payload, label, icon, default(Color), tooltip)
		{
			Size = new Vector2(270f, 28f)
		};
	}

	public static string DisplayName(ForcedIdeoSource source, string key)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val;
		if (string.IsNullOrEmpty(key))
		{
			val = Translator.Translate("FactionLoadout_None");
			return ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
		}
		switch (source)
		{
		case ForcedIdeoSource.FactionPrimary:
			val = Translator.Translate("FactionLoadout_General_IdeoFactionPrimary");
			return ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
		case ForcedIdeoSource.Preset:
		{
			IdeoPresetDef namedSilentFail = DefDatabase<IdeoPresetDef>.GetNamedSilentFail(key);
			string presetName;
			if (namedSilentFail == null)
			{
				presetName = key;
			}
			else
			{
				val = ((Def)namedSilentFail).LabelCap;
				presetName = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
			}
			return BuildPresetLabel(presetName);
		}
		default:
			return BuildSavedFileLabel(key, !File.Exists(GenFilePaths.AbsPathForIdeo(key)));
		}
	}

	private static string BuildPresetLabel(string presetName)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_General_IdeoPresetLabel", NamedArgument.op_Implicit(presetName));
		return ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
	}

	private static string BuildSavedFileLabel(string fileName, bool isMissing)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val;
		if (!isMissing)
		{
			val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_General_IdeoSavedLabel", NamedArgument.op_Implicit(fileName));
			return ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
		}
		val = Translator.Translate("FactionLoadout_General_IdeoFileMissing");
		string text = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
		val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_General_IdeoSavedLabelMissing", NamedArgument.op_Implicit(fileName), NamedArgument.op_Implicit(text));
		return ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
	}
}
