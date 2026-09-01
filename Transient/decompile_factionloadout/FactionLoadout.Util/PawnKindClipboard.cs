using RimWorld;
using Verse;
using Verse.Sound;

namespace FactionLoadout.Util;

public static class PawnKindClipboard
{
	public static PawnKindClipboardData Clipboard { get; set; }

	public static bool HasData => Clipboard != null;

	public static void Copy(PawnKindEdit source)
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		PawnKindEdit pawnKindEdit = new PawnKindEdit
		{
			Def = source.Def,
			IsGlobal = source.IsGlobal
		};
		pawnKindEdit.CopyFrom(source);
		PawnKindClipboardData obj = new PawnKindClipboardData
		{
			Clone = pawnKindEdit
		};
		object obj2;
		if (!source.IsGlobal)
		{
			PawnKindDef def = source.Def;
			if (def == null)
			{
				obj2 = null;
			}
			else
			{
				TaggedString labelCap = ((Def)def).LabelCap;
				obj2 = ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString();
			}
			if (obj2 == null)
			{
				obj2 = "Unknown";
			}
		}
		else
		{
			obj2 = "Global";
		}
		obj.SourceLabel = (string)obj2;
		Clipboard = obj;
		SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
	}

	public static void PasteAll(PawnKindEdit target)
	{
		if (Clipboard != null)
		{
			target.CopyFrom(Clipboard.Clone);
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_Low, (Map)null);
		}
	}

	public static string GetDescription()
	{
		if (Clipboard != null)
		{
			return "Source: " + Clipboard.SourceLabel;
		}
		return "Clipboard is empty.";
	}
}
