using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public class Dialog_FactionLoadout : Window
{
	public Vector2 scrollPosition = Vector2.zero;

	public override Vector2 InitialSize => new Vector2(800f, 600f);

	public Dialog_FactionLoadout()
		: base((IWindowDrawing)null)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		base.doCloseButton = true;
		base.closeOnAccept = true;
		base.closeOnCancel = true;
		base.doCloseX = true;
		base.forcePause = true;
		base.absorbInputAroundWindow = true;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Expected O, but got Unknown
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0227: Unknown result type (might be due to invalid IL or missing references)
		//IL_022c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0258: Unknown result type (might be due to invalid IL or missing references)
		//IL_0251: Unknown result type (might be due to invalid IL or missing references)
		//IL_0264: Unknown result type (might be due to invalid IL or missing references)
		//IL_026b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0270: Unknown result type (might be due to invalid IL or missing references)
		//IL_0274: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_052b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0507: Unknown result type (might be due to invalid IL or missing references)
		//IL_0512: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_040a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0403: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_033a: Unknown result type (might be due to invalid IL or missing references)
		//IL_035d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0367: Expected O, but got Unknown
		//IL_036d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0390: Unknown result type (might be due to invalid IL or missing references)
		//IL_039a: Expected O, but got Unknown
		//IL_03a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ad: Expected O, but got Unknown
		//IL_0414: Unknown result type (might be due to invalid IL or missing references)
		//IL_0434: Unknown result type (might be due to invalid IL or missing references)
		//IL_0439: Unknown result type (might be due to invalid IL or missing references)
		//IL_043d: Unknown result type (might be due to invalid IL or missing references)
		//IL_041f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0424: Unknown result type (might be due to invalid IL or missing references)
		//IL_0428: Unknown result type (might be due to invalid IL or missing references)
		//IL_0498: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c1: Unknown result type (might be due to invalid IL or missing references)
		int num = (Preset.LoadedPresets.Count + 1) * 30;
		int num2 = 300;
		float num3 = num + num2;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(0f, 0f, ((Rect)(ref inRect)).width - 20f, num3);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 30f, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 70f);
		scrollPosition = GUI.BeginScrollView(val2, scrollPosition, val);
		Listing_Standard val3 = new Listing_Standard();
		try
		{
			((Listing)val3).Begin(val);
			val3.Label(Translator.Translate("FactionLoadout_Settings_FactionPresetDesc"), -1f, (string)null);
			((Listing)val3).GapLine(12f);
			val3.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_VanillaRestrictions")), ref MySettings.VanillaRestrictions, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_VanillaRestrictionsDesc")), 0f, 1f);
			((Listing)val3).GapLine(12f);
			val3.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_Verbose")), ref MySettings.VerboseLogging, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_VerboseDesc")), 0f, 1f);
			val3.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_PatchKindInRequests")), ref MySettings.PatchKindInRequests, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_PatchKindInRequestsDesc")), 0f, 1f);
			val3.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_IgnorePrice")), ref MySettings.IgnorePriceLimits, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_IgnorePriceDesc")), 0f, 1f);
			val3.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_OverrideForcedIdeos")), ref MySettings.OverrideForcedIdeos, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Settings_OverrideForcedIdeosDesc")), 0f, 1f);
			((Listing)val3).GapLine(12f);
			val3.Label(Translator.Translate("FactionLoadout_Settings_FactionPresetDesc"), -1f, (string)null);
			((Listing)val3).GapLine(12f);
			bool flag = Input.GetKey((KeyCode)304) || Input.GetKey((KeyCode)303);
			Preset preset = null;
			foreach (Preset loadedPreset in Preset.LoadedPresets)
			{
				Rect rect = ((Listing)val3).GetRect(30f, 1f);
				((Rect)(ref rect)).width = 80f;
				bool flag2 = MySettings.ActivePreset == loadedPreset.GUID;
				GUI.color = (flag2 ? Color.green : Color.red);
				bool num4 = flag2;
				Rect val4 = rect;
				TaggedString val5 = Translator.Translate("FactionLoadout_Active");
				Widgets.CheckboxLabeled(val4, TaggedString.op_Implicit(((TaggedString)(ref val5)).CapitalizeFirst()), ref flag2, false, (Texture2D)null, (Texture2D)null, true, false);
				if (num4 != flag2)
				{
					MySettings.ActivePreset = (flag2 ? loadedPreset.GUID : null);
					((ModSettings)ModCore.Settings).Write();
				}
				GUI.color = Color.white;
				((Rect)(ref rect)).x = ((Rect)(ref rect)).x + 90f;
				if (loadedPreset.IsPackaged)
				{
					GUI.color = new Color(1f, 0.75f, 0.2f);
					Rect val6 = rect;
					val5 = Translator.Translate("FactionLoadout_PackagedLabel");
					if (Widgets.ButtonText(val6, TaggedString.op_Implicit(((TaggedString)(ref val5)).CapitalizeFirst()), true, true, true, (TextAnchor?)null))
					{
						Preset capturedPreset = loadedPreset;
						List<FloatMenuOption> list = new List<FloatMenuOption>(2)
						{
							new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_CopyToMyPresets")), (Action)delegate
							{
								try
								{
									Preset preset2 = Preset.CreateCopy(capturedPreset);
									Preset.AddNewPreset(preset2);
									preset2.Save();
									PresetUI.OpenEditor(preset2);
									Dialog_ModSettings obj = Find.WindowStack.WindowOfType<Dialog_ModSettings>();
									if (obj != null)
									{
										((Window)obj).Close(true);
									}
									Dialog_Options obj2 = Find.WindowStack.WindowOfType<Dialog_Options>();
									if (obj2 != null)
									{
										((Window)obj2).Close(true);
									}
								}
								catch (Exception e)
								{
									ModCore.Error("Failed to copy packaged preset.", e);
								}
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0),
							new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_EditSourceFile")), (Action)delegate
							{
								PresetUI.OpenEditor(capturedPreset);
								Dialog_ModSettings obj3 = Find.WindowStack.WindowOfType<Dialog_ModSettings>();
								if (obj3 != null)
								{
									((Window)obj3).Close(true);
								}
								Dialog_Options obj4 = Find.WindowStack.WindowOfType<Dialog_Options>();
								if (obj4 != null)
								{
									((Window)obj4).Close(true);
								}
							}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0)
						};
						Find.WindowStack.Add((Window)new FloatMenu(list));
					}
					GUI.color = Color.white;
					((Rect)(ref rect)).x = ((Rect)(ref rect)).x + 90f;
					((Rect)(ref rect)).width = 9999f;
					Widgets.Label(rect, loadedPreset.Name + " <color=#888888><i>(" + loadedPreset.PackagedModName + ")</i></color>");
					continue;
				}
				GUI.color = (flag ? Color.red : Color.white);
				Rect val7 = rect;
				TaggedString val8;
				if (!flag)
				{
					val5 = Translator.Translate("FactionLoadout_Edit");
					val8 = ((TaggedString)(ref val5)).CapitalizeFirst();
				}
				else
				{
					val5 = Translator.Translate("Delete");
					val8 = ((TaggedString)(ref val5)).CapitalizeFirst();
				}
				if (Widgets.ButtonText(val7, TaggedString.op_Implicit(val8), true, true, true, (TextAnchor?)null))
				{
					if (!flag)
					{
						PresetUI.OpenEditor(loadedPreset);
						Dialog_ModSettings obj5 = Find.WindowStack.WindowOfType<Dialog_ModSettings>();
						if (obj5 != null)
						{
							((Window)obj5).Close(true);
						}
						Dialog_Options obj6 = Find.WindowStack.WindowOfType<Dialog_Options>();
						if (obj6 != null)
						{
							((Window)obj6).Close(true);
						}
					}
					else
					{
						preset = loadedPreset;
					}
				}
				GUI.color = Color.white;
				((Rect)(ref rect)).x = ((Rect)(ref rect)).x + 90f;
				((Rect)(ref rect)).width = 9999f;
				Widgets.Label(rect, loadedPreset.Name);
			}
			if (preset != null)
			{
				Preset.DeletePreset(preset);
			}
			if (GenCollection.EnumerableNullOrEmpty<Preset>((IEnumerable<Preset>)Preset.LoadedPresets))
			{
				val3.Label(Translator.Translate("FactionLoadout_NothingHere"), -1f, (string)null);
			}
			((Listing)val3).GapLine(12f);
			if (val3.ButtonText(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_CreateNewPreset")), (string)null, 1f))
			{
				Preset preset3 = new Preset();
				Preset.AddNewPreset(preset3);
				preset3.Save();
				MySettings.ActivePreset = preset3.GUID;
				PresetUI.OpenEditor(preset3);
				Dialog_ModSettings obj7 = Find.WindowStack.WindowOfType<Dialog_ModSettings>();
				if (obj7 != null)
				{
					((Window)obj7).Close(true);
				}
				Dialog_Options obj8 = Find.WindowStack.WindowOfType<Dialog_Options>();
				if (obj8 != null)
				{
					((Window)obj8).Close(true);
				}
			}
		}
		finally
		{
			((Listing)val3).End();
			GUI.EndScrollView();
		}
	}

	public override void PostClose()
	{
		((Window)this).PostClose();
		PresetUI presetUI = Find.WindowStack.WindowOfType<PresetUI>();
		if (presetUI != null)
		{
			((Window)presetUI).Close(true);
		}
		((ModSettings)ModCore.Settings).Write();
	}
}
