using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class Dialog_ResetGroupsConfirm : Window
{
	private readonly FactionEdit _edit;

	private List<string> _addedKindNames;

	public override Vector2 InitialSize => new Vector2(480f, (_addedKindNames.Count > 0) ? 300f : 180f);

	public Dialog_ResetGroupsConfirm(FactionEdit edit)
		: base((IWindowDrawing)null)
	{
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		_edit = edit;
		base.doCloseX = true;
		base.closeOnCancel = true;
		base.absorbInputAroundWindow = true;
		base.draggable = false;
		_addedKindNames = new List<string>();
		if (edit.PawnGroupMakerEdits == null)
		{
			return;
		}
		HashSet<string> hashSet = new HashSet<string>(from k in FactionEdit.GetAllPawnKinds((FactionDef)(FactionEdit.TryGetOriginal(edit.Faction.DefName) ?? ((object)edit.Faction.Def) ?? ((object)new FactionDef())))
			select ((Def)k).defName);
		foreach (PawnGroupMakerEdit pawnGroupMakerEdit in edit.PawnGroupMakerEdits)
		{
			foreach (PawnKindDef allKind in pawnGroupMakerEdit.GetAllKinds())
			{
				if (!hashSet.Contains(((Def)allKind).defName))
				{
					List<string> addedKindNames = _addedKindNames;
					TaggedString labelCap = ((Def)allKind).LabelCap;
					if (!addedKindNames.Contains(((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString()))
					{
						_addedKindNames.Add(TaggedString.op_Implicit(((Def)allKind).LabelCap));
					}
				}
			}
		}
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0217: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		Text.Font = (GameFont)2;
		val.Label(Translator.Translate("FactionLoadout_GroupEditor_ResetConfirmTitle"), -1f, (string)null);
		Text.Font = (GameFont)1;
		((Listing)val).GapLine(12f);
		val.Label(Translator.Translate("FactionLoadout_GroupEditor_ResetConfirmBody"), -1f, (string)null);
		if (_addedKindNames.Count > 0)
		{
			((Listing)val).Gap(6f);
			GUI.color = new Color(1f, 0.7f, 0.2f);
			val.Label(TranslatorFormattedStringExtensions.Translate("FactionLoadout_GroupEditor_ResetConfirmOrphans", NamedArgument.op_Implicit(_addedKindNames.Count)), -1f, (string)null);
			GUI.color = Color.white;
			foreach (string addedKindName in _addedKindNames)
			{
				val.Label("  · " + addedKindName, -1f, (TipSignal?)null);
			}
			((Listing)val).Gap(4f);
			GUI.color = Color.grey;
			val.Label("<i>" + Translator.Translate("FactionLoadout_GroupEditor_ResetConfirmOrphanNote") + "</i>", -1f, (string)null);
			GUI.color = Color.white;
		}
		((Listing)val).GapLine(12f);
		Rect rect = ((Listing)val).GetRect(28f, 1f);
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 100f, 24f), TaggedString.op_Implicit(Translator.Translate("Cancel")), true, true, true, (TextAnchor?)null))
		{
			((Window)this).Close(true);
		}
		GUI.color = Color.red;
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).xMax - 120f, ((Rect)(ref rect)).y, 120f, 24f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_ResetConfirmButton")), true, true, true, (TextAnchor?)null))
		{
			_edit.ResetGroupEdits();
			((Window)this).Close(true);
		}
		GUI.color = Color.white;
		((Listing)val).End();
	}
}
