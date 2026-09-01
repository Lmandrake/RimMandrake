using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.Factions;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(PawnRenderNode_AnimalPack), "GraphicFor")]
public static class PawnRenderNode_AnimalPack_GraphicFor_Patch
{
	public static void Postfix(PawnRenderNode_AnimalPack __instance, ref Graphic __result, Pawn pawn)
	{
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Invalid comparison between Unknown and I4
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		if (__result == null)
		{
			return;
		}
		Faction faction = ((Thing)pawn).Faction;
		if (faction == null)
		{
			return;
		}
		FactionDefExtension factionDefExtension = FactionDefExtension.Get((Def)(object)faction.def);
		if (!GenText.NullOrEmpty(factionDefExtension.packAnimalTexNameSuffix))
		{
			PawnKindLifeStage curKindLifeStage = pawn.ageTracker.CurKindLifeStage;
			Graphic val = (((int)pawn.gender == 2 && curKindLifeStage.femaleGraphicData != null) ? curKindLifeStage.femaleGraphicData.Graphic : curKindLifeStage.bodyGraphicData.Graphic);
			string text = val.path + factionDefExtension.packAnimalTexNameSuffix;
			if ((Object)(object)ContentFinder<Texture2D>.Get(text + "_south", false) != (Object)null)
			{
				__result = GraphicDatabase.Get<Graphic_Multi>(text, ShaderDatabase.CutoutComplex, val.drawSize, ((Thing)pawn).Faction.Color);
			}
		}
	}
}
