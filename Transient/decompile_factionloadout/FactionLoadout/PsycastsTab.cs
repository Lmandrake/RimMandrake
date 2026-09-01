using System;
using FactionLoadout.Modules;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class PsycastsTab : EditTab
{
	private string vpeGiveRandomAbilitiesBuffer;

	private string vpeLevelBuffer;

	public PsycastsTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_VEPsycasts")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		if (VEPsycastsReflectionModule.ModLoaded.Value)
		{
			ref bool? vEPsycastRandomAbilities = ref Current.VEPsycastRandomAbilities;
			TaggedString val = Translator.Translate("FactionLoadout_Psycasts_GiveRandomAbilities");
			DrawOverride(ui, defaultValue: false, ref vEPsycastRandomAbilities, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawVPERandomAbilities, 32f, (PawnKindEdit e) => e.VEPsycastRandomAbilities);
			ref int? vEPsycastLevel = ref Current.VEPsycastLevel;
			val = Translator.Translate("FactionLoadout_Psycasts_Level");
			DrawOverride(ui, 1, ref vEPsycastLevel, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawVPELevel, 32f, (PawnKindEdit e) => e.VEPsycastLevel);
			IntRange zero = IntRange.Zero;
			ref IntRange? vEPsycastStatPoints = ref Current.VEPsycastStatPoints;
			val = Translator.Translate("FactionLoadout_Psycasts_StatPoints");
			base.DrawOverride<IntRange>(ui, zero, ref vEPsycastStatPoints, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (Action<Rect, bool, IntRange>)DrawVPEStats, 32f, (Func<PawnKindEdit, IntRange?>)((PawnKindEdit e) => e.VEPsycastStatPoints));
		}
	}

	private void DrawVPERandomAbilities(Rect rect, bool active, bool _)
	{
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		if (vpeGiveRandomAbilitiesBuffer == null && active)
		{
			vpeGiveRandomAbilitiesBuffer = Current.VEPsycastRandomAbilities?.ToString() ?? "NA";
		}
		if (active)
		{
			bool? vEPsycastRandomAbilities = Current.VEPsycastRandomAbilities;
			int num;
			if (!vEPsycastRandomAbilities.HasValue)
			{
				DefModExtension val = VEPsycastsReflectionModule.FindVEPsycastsExtension(Current.Def);
				if (val != null)
				{
					object obj = VEPsycastsReflectionModule.GiveRandomAbilitiesField.Value?.GetValue(val);
					num = ((obj is bool && (bool)obj) ? 1 : 0);
				}
				else
				{
					num = 0;
				}
			}
			else
			{
				num = ((vEPsycastRandomAbilities == true) ? 1 : 0);
			}
			bool value = (byte)num != 0;
			Widgets.CheckboxLabeled(rect, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Psycasts_GiveRandomAbilities")), ref value, false, (Texture2D)null, (Texture2D)null, false, false);
			Current.VEPsycastRandomAbilities = value;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : "[Default] 1");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	private void DrawVPELevel(Rect rect, bool active, int _)
	{
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		if (vpeLevelBuffer == null && active)
		{
			vpeLevelBuffer = Current.VEPsycastLevel?.ToString() ?? "NA";
		}
		if (active)
		{
			int? vEPsycastLevel = Current.VEPsycastLevel;
			int num2;
			if (!vEPsycastLevel.HasValue)
			{
				DefModExtension val = VEPsycastsReflectionModule.FindVEPsycastsExtension(Current.Def);
				num2 = ((val == null || !(VEPsycastsReflectionModule.LevelField.Value?.GetValue(val) is int num)) ? 1 : num);
			}
			else
			{
				num2 = vEPsycastLevel.GetValueOrDefault();
			}
			int value = num2;
			Widgets.IntEntry(rect, ref value, ref vpeLevelBuffer, 1);
			Current.VEPsycastLevel = value;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : "[Default] 1");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	private void DrawVPEStats(Rect rect, bool active, IntRange defaultRange)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		DefModExtension val = VEPsycastsReflectionModule.FindVEPsycastsExtension(Current.Def);
		if (val != null && VEPsycastsReflectionModule.StatUpgradePointsField.Value?.GetValue(val) is IntRange val2)
		{
			defaultRange = val2;
		}
		DrawIntRange(rect, active, ref Current.VEPsycastStatPoints, defaultRange, ref buffers[bufferIndex++], ref buffers[bufferIndex++]);
	}
}
