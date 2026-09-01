using RimWorld;
using Verse;
using Verse.Sound;

namespace FactionLoadout;

public static class FactionEditClipboard
{
	public static FactionEdit Clipboard { get; set; }

	public static bool HasData => Clipboard != null;

	public static void Copy(FactionEdit source)
	{
		FactionEdit factionEdit = new FactionEdit();
		factionEdit.CopyFrom(source);
		Clipboard = factionEdit;
		SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
	}

	public static void PasteAll(FactionEdit target)
	{
		if (Clipboard != null)
		{
			target.CopyFrom(Clipboard);
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Low, (Map)null);
		}
	}

	public static string GetDescription()
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val;
		if (Clipboard != null)
		{
			ref TechLevel? techLevel = ref Clipboard.TechLevel;
			val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_FactionClipboard_Description", NamedArgument.op_Implicit(TaggedString.op_Implicit((techLevel.HasValue ? TechLevelUtility.ToStringHuman(techLevel.GetValueOrDefault()) : null) ?? TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_NotOverriden_WithDefault", NamedArgument.op_Implicit("-"))))), NamedArgument.op_Implicit(Clipboard.OverrideFactionXenotypes.ToString()));
		}
		else
		{
			val = Translator.Translate("FactionLoadout_Clipboard_Empty");
		}
		return TaggedString.op_Implicit(val);
	}
}
