using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout.Patches;

public static class PawnGenPatchIdeo
{
	[HarmonyPrefix]
	public static void Prefix(ref PawnGenerationRequest request)
	{
		if (!ForcedIdeoGameComponent.AnyIdeologyEditsActive || ((PawnGenerationRequest)(ref request)).ForceNoIdeo || ((PawnGenerationRequest)(ref request)).KindDef == null || (((PawnGenerationRequest)(ref request)).FixedIdeo != null && !MySettings.OverrideForcedIdeos))
		{
			return;
		}
		ForcedIdeoGameComponent current = ForcedIdeoGameComponent.Current;
		if (current == null)
		{
			return;
		}
		string text = null;
		ForcedIdeoSource source = ForcedIdeoSource.SavedFile;
		foreach (PawnKindEdit item in PawnKindEdit.GetEditsFor(((PawnGenerationRequest)(ref request)).KindDef, ((PawnGenerationRequest)(ref request)).Faction?.def))
		{
			if (!string.IsNullOrEmpty(item.ForcedIdeoKey) && (!item.IsGlobal || text == null))
			{
				text = item.ForcedIdeoKey;
				source = item.ForcedIdeoSourceKind;
			}
		}
		if (text != null)
		{
			Ideo orInjectIdeo = current.GetOrInjectIdeo(((PawnGenerationRequest)(ref request)).Faction, source, text);
			if (orInjectIdeo != null)
			{
				((PawnGenerationRequest)(ref request)).FixedIdeo = orInjectIdeo;
			}
		}
	}
}
