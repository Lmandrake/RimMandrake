using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class Dialog_XenotypeEdit : Window
{
	private readonly FactionEdit _edit;

	private Vector2 _scrollPos;

	public override Vector2 InitialSize => new Vector2(450f, 400f);

	public Dialog_XenotypeEdit(FactionEdit edit)
		: base((IWindowDrawing)null)
	{
		_edit = edit;
		base.doCloseX = true;
		base.closeOnCancel = true;
		base.draggable = true;
		base.resizeable = true;
		base.absorbInputAroundWindow = true;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_0242: Unknown result type (might be due to invalid IL or missing references)
		//IL_0249: Unknown result type (might be due to invalid IL or missing references)
		//IL_0251: Unknown result type (might be due to invalid IL or missing references)
		//IL_0258: Expected O, but got Unknown
		//IL_025a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0305: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0401: Unknown result type (might be due to invalid IL or missing references)
		//IL_0431: Unknown result type (might be due to invalid IL or missing references)
		//IL_0436: Unknown result type (might be due to invalid IL or missing references)
		//IL_043a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0444: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		val.CheckboxLabeled(string.Format("<b>{0}:</b>", Translator.Translate("FactionLoadout_EditXenoSpawnRates")), ref _edit.OverrideFactionXenotypes, (string)null, 0f, 1f);
		if (_edit.OverrideFactionXenotypes)
		{
			if (GenDictionary.NullOrEmpty<string, float>(_edit.xenotypeChances))
			{
				_edit.xenotypeChances = _edit.Faction?.Def?.xenotypeSet?.xenotypeChances?.ToDictionary((XenotypeChance x) => ((Def)x.xenotype).defName, (XenotypeChance x) => x.chance) ?? new Dictionary<string, float>();
				if (!_edit.xenotypeChances.ContainsKey(FactionEditUI.BaselinerDefName))
				{
					Dictionary<string, float> xenotypeChances = _edit.xenotypeChances;
					string baselinerDefName = FactionEditUI.BaselinerDefName;
					DefRef<FactionDef> faction = _edit.Faction;
					float? obj;
					if (faction == null)
					{
						obj = null;
					}
					else
					{
						FactionDef def2 = faction.Def;
						if (def2 == null)
						{
							obj = null;
						}
						else
						{
							XenotypeSet xenotypeSet = def2.xenotypeSet;
							obj = ((xenotypeSet != null) ? new float?(xenotypeSet.BaselinerChance) : ((float?)null));
						}
					}
					xenotypeChances.Add(baselinerDefName, obj ?? 1f);
				}
			}
			_edit.xenotypeChances[FactionEditUI.BaselinerDefName] = Math.Max(0f, 1f - _edit.xenotypeChances.Sum((KeyValuePair<string, float> x) => (!(x.Key == FactionEditUI.BaselinerDefName)) ? x.Value : 0f));
			float num = Mathf.Max(30f, ((Rect)(ref inRect)).height - ((Listing)val).CurHeight - 70f);
			Rect rect = ((Listing)val).GetRect(num, 1f);
			float num2 = (float)_edit.xenotypeChances.Count * 32f;
			Rect val2 = default(Rect);
			((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref rect)).width - 16f, Mathf.Max(num2, num));
			Widgets.BeginScrollView(rect, ref _scrollPos, val2, true);
			Listing_Standard val3 = new Listing_Standard();
			((Listing)val3).Begin(val2);
			List<string> toDelete = new List<string>();
			foreach (string key in _edit.xenotypeChances.Keys.OrderBy(delegate(string k)
			{
				//IL_000d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0012: Unknown result type (might be due to invalid IL or missing references)
				XenotypeDef namedSilentFail = DefDatabase<XenotypeDef>.GetNamedSilentFail(k);
				object obj2;
				if (namedSilentFail == null)
				{
					obj2 = null;
				}
				else
				{
					TaggedString labelCap = ((Def)namedSilentFail).LabelCap;
					obj2 = ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString();
				}
				if (obj2 == null)
				{
					obj2 = k;
				}
				return (string)obj2;
			}).ToList())
			{
				Dictionary<string, float> xenotypeChances2 = _edit.xenotypeChances;
				string key2 = key;
				XenotypeDef namedSilentFail2 = DefDatabase<XenotypeDef>.GetNamedSilentFail(key);
				xenotypeChances2[key2] = UIHelpers.SliderLabeledWithDelete(val3, $"{((namedSilentFail2 != null) ? ((Def)namedSilentFail2).LabelCap : TaggedString.op_Implicit(key))}: {GenText.ToStringPercent(_edit.xenotypeChances[key])}", _edit.xenotypeChances[key], 0f, 1f, 0.5f, null, delegate
				{
					toDelete.Add(key);
				});
			}
			foreach (string item in toDelete)
			{
				_edit.xenotypeChances.Remove(item);
			}
			((Listing)val3).End();
			Widgets.EndScrollView();
			if (val.ButtonText(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_AddNewByDefName")), (string)null, 1f))
			{
				Find.WindowStack.Add((Window)(object)new Dialog_TextEntry(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_AddNewByDefNameDesc")), delegate(string defName)
				{
					//IL_0019: Unknown result type (might be due to invalid IL or missing references)
					//IL_001e: Unknown result type (might be due to invalid IL or missing references)
					if (_edit.xenotypeChances.ContainsKey(defName))
					{
						Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_DuplicateListItem", NamedArgument.op_Implicit(defName))), MessageTypeDefOf.RejectInput, true);
					}
					else
					{
						_edit.xenotypeChances[defName] = 0.1f;
					}
				}));
			}
			if (ModLister.BiotechInstalled)
			{
				TaggedString val4 = Translator.Translate("Add");
				if (val.ButtonText(TaggedString.op_Implicit(((TaggedString)(ref val4)).CapitalizeFirst() + "..."), (string)null, 1f))
				{
					CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefDatabase<XenotypeDef>.AllDefs.Where((XenotypeDef def) => !_edit.xenotypeChances.ContainsKey(((Def)def).defName)), (XenotypeDef def) => new MenuItemText(def, TaggedString.op_Implicit(((Def)def).LabelCap), def.Icon)), delegate(MenuItemBase item)
					{
						XenotypeDef payload = item.GetPayload<XenotypeDef>();
						_edit.xenotypeChances[((Def)payload).defName] = 0.1f;
					});
				}
			}
		}
		else
		{
			_edit.xenotypeChances.Clear();
			_edit.xenotypeChancesByDef.Clear();
		}
		((Listing)val).End();
	}
}
