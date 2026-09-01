using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Outposts;

public class OutpostsMod : Mod
{
	public static List<WorldObjectDef> Outposts;

	public static Harmony Harm;

	public static OutpostsSettings Settings;

	private static Dictionary<Type, List<FieldInfo>> editableFields;

	private float prevHeight = float.MaxValue;

	private Vector2 scrollPos;

	private Dictionary<WorldObjectDef, float> sectionHeights;

	public OutpostsMod(ModContentPack content)
		: base(content)
	{
		LongEventHandler.ExecuteWhenFinished((Action)FindOutposts);
		Settings = ((Mod)this).GetSettings<OutpostsSettings>();
		editableFields = new Dictionary<Type, List<FieldInfo>>();
		foreach (Type item in GenCollection.Concat<Type>(GenCollection.Concat<Type>((IEnumerable<Type>)GenTypes.AllSubclasses(typeof(Outpost)), typeof(Outpost)), typeof(OutpostExtension)).Concat(GenTypes.AllSubclasses(typeof(OutpostExtension))))
		{
			editableFields[item] = new List<FieldInfo>();
			FieldInfo[] fields = item.GetFields(AccessTools.all);
			foreach (FieldInfo fieldInfo in fields)
			{
				if (GenAttribute.HasAttribute<PostToSetingsAttribute>((MemberInfo)fieldInfo))
				{
					editableFields[item].Add(fieldInfo);
				}
			}
		}
	}

	private void FindOutposts()
	{
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Expected O, but got Unknown
		Outposts = DefDatabase<WorldObjectDef>.AllDefs.Where((WorldObjectDef def) => typeof(Outpost).IsAssignableFrom(def.worldObjectClass)).ToList();
		Harm = new Harmony("vanillaexpanded.outposts");
		sectionHeights = Outposts.ToDictionary((WorldObjectDef o) => o, (WorldObjectDef _) => float.MaxValue);
		if (GenCollection.Any<WorldObjectDef>(Outposts))
		{
			HarmonyPatches.DoPatches();
			((BuildableDef)Outposts_DefOf.VEF_OutpostDeliverySpot).designationCategory = DefDatabase<DesignationCategoryDef>.GetNamed("Misc", true);
		}
	}

	public static void Notify_Spawned(Outpost outpost)
	{
		Setup(outpost);
	}

	private static void Setup(Outpost outpost)
	{
		OutpostsSettings.OutpostSettings outpostSettings = Settings.SettingsFor(((Def)((WorldObject)outpost).def).defName);
		PostToSetingsAttribute postToSetingsAttribute = default(PostToSetingsAttribute);
		foreach (FieldInfo item in editableFields[((object)outpost).GetType()])
		{
			if (GenAttribute.TryGetAttribute<PostToSetingsAttribute>((MemberInfo)item, ref postToSetingsAttribute))
			{
				item.SetValue(outpost, outpostSettings.TryGet(item.DeclaringType.Name + "." + item.Name, item.FieldType, out var value) ? value : (postToSetingsAttribute.Default ?? item.GetValue(outpost)));
			}
		}
		PostToSetingsAttribute postToSetingsAttribute2 = default(PostToSetingsAttribute);
		foreach (FieldInfo item2 in editableFields[((object)outpost.Ext).GetType()])
		{
			if (GenAttribute.TryGetAttribute<PostToSetingsAttribute>((MemberInfo)item2, ref postToSetingsAttribute2))
			{
				item2.SetValue(outpost.Ext, outpostSettings.TryGet(item2.DeclaringType.Name + "." + item2.Name, item2.FieldType, out var value2) ? value2 : (item2.GetValue(outpost.Ext) ?? postToSetingsAttribute2.Default));
			}
		}
	}

	public static void Notify_Removed(Outpost outpost)
	{
	}

	public override string SettingsCategory()
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(GenCollection.Any<WorldObjectDef>(Outposts) ? Translator.Translate("Outposts.Settings.Title") : TaggedString.op_Implicit((string)null));
	}

	public override void DoSettingsWindowContents(Rect inRect)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Expected O, but got Unknown
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Expected O, but got Unknown
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
		((Mod)this).DoSettingsWindowContents(inRect);
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(0f, 0f, ((Rect)(ref inRect)).width - 20f, prevHeight);
		Widgets.BeginScrollView(inRect, ref scrollPos, val, true);
		Listing_Standard val2 = new Listing_Standard();
		((Listing)val2).Begin(val);
		val2.Label(TranslatorFormattedStringExtensions.Translate("Outposts.Settings.Multiplier.Production", NamedArgument.op_Implicit(GenText.ToStringPercent(Settings.ProductionMultiplier))), -1f, (string)null);
		Settings.ProductionMultiplier = val2.Slider(Settings.ProductionMultiplier, 0.1f, 10f);
		val2.Label(TranslatorFormattedStringExtensions.Translate("Outposts.Settings.Multiplier.Time", NamedArgument.op_Implicit(GenText.ToStringPercent(Settings.TimeMultiplier))), -1f, (string)null);
		Settings.TimeMultiplier = val2.Slider(Settings.TimeMultiplier, 0.01f, 5f);
		if (val2.ButtonTextLabeled(TaggedString.op_Implicit(Translator.Translate("Outposts.Settings.DeliveryMethod")), TaggedString.op_Implicit(Translator.Translate($"Outposts.Settings.DeliveryMethod.{Settings.DeliveryMethod}")), (TextAnchor)0, (string)null, (string)null))
		{
			Find.WindowStack.Add((Window)new FloatMenu(Enum.GetValues(typeof(DeliveryMethod)).OfType<DeliveryMethod>().Select((Func<DeliveryMethod, FloatMenuOption>)((DeliveryMethod method) => new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate($"Outposts.Settings.DeliveryMethod.{method}")), (Action)delegate
			{
				Settings.DeliveryMethod = method;
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0)))
				.ToList()));
		}
		((Listing)val2).GapLine(12f);
		foreach (WorldObjectDef outpost in Outposts)
		{
			Listing_Standard val3 = val2.BeginSection(sectionHeights[outpost], 4f, 4f);
			val3.Label(((Def)outpost).LabelCap, -1f, (string)null);
			OutpostsSettings.OutpostSettings settings2 = Settings.SettingsFor(((Def)outpost).defName);
			foreach (FieldInfo item in editableFields[outpost.worldObjectClass])
			{
				DoSetting(val3, settings2, item);
			}
			OutpostExtension modExtension = ((Def)outpost).GetModExtension<OutpostExtension>();
			if (modExtension != null)
			{
				foreach (FieldInfo item2 in editableFields[((object)modExtension).GetType()])
				{
					DoSetting(val3, settings2, item2, modExtension);
				}
			}
			sectionHeights[outpost] = ((Listing)val3).CurHeight;
			val2.EndSection(val3);
			((Listing)val2).Gap(12f);
		}
		prevHeight = ((Listing)val2).CurHeight;
		((Listing)val2).End();
		Widgets.EndScrollView();
		static void DoSetting(Listing_Standard listing, OutpostsSettings.OutpostSettings settings, FieldInfo info, object obj = null)
		{
			PostToSetingsAttribute postToSetingsAttribute = default(PostToSetingsAttribute);
			if (GenAttribute.TryGetAttribute<PostToSetingsAttribute>((MemberInfo)info, ref postToSetingsAttribute))
			{
				string key = info.DeclaringType.Name + "." + info.Name;
				object value;
				object current4 = (settings.TryGet(key, info.FieldType, out value) ? value : ((obj == null) ? postToSetingsAttribute.Default : info.GetValue(obj)));
				postToSetingsAttribute.Draw(listing, ref current4);
				if (current4 == postToSetingsAttribute.Default)
				{
					if (settings.Has(key))
					{
						settings.Remove(key);
					}
				}
				else
				{
					settings.Set(key, current4);
				}
			}
		}
	}

	public override void WriteSettings()
	{
		((Mod)this).WriteSettings();
		if (Find.World?.worldObjects == null)
		{
			return;
		}
		foreach (Outpost item in Find.World.worldObjects.AllWorldObjects.OfType<Outpost>())
		{
			Setup(item);
		}
	}
}
