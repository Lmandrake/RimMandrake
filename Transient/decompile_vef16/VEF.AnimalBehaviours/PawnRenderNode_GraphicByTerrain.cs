using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class PawnRenderNode_GraphicByTerrain : PawnRenderNode_AnimalPart
{
	public PawnRenderNode_GraphicByTerrain(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		CompGraphicByTerrain compGraphicByTerrain = default(CompGraphicByTerrain);
		if (ThingCompUtility.TryGetComp<CompGraphicByTerrain>((ThingWithComps)(object)pawn, ref compGraphicByTerrain) && compGraphicByTerrain.currentName != "")
		{
			Graphic graphic = pawn.ageTracker.CurKindLifeStage.bodyGraphicData.Graphic;
			if (compGraphicByTerrain.terrainName == "Normal")
			{
				return ((PawnRenderNode_AnimalPart)this).GraphicFor(pawn);
			}
			if (compGraphicByTerrain.terrainName == "Water")
			{
				return GraphicDatabase.Get<Graphic_Multi>(graphic.path + compGraphicByTerrain.Props.waterSuffix, ShaderDatabase.Cutout, graphic.drawSize, Color.white);
			}
			if (compGraphicByTerrain.terrainName == "Cold")
			{
				return GraphicDatabase.Get<Graphic_Multi>(graphic.path + compGraphicByTerrain.Props.lowTemperatureSuffix, ShaderDatabase.Cutout, graphic.drawSize, Color.white);
			}
			if (compGraphicByTerrain.terrainName == "Snowy")
			{
				return GraphicDatabase.Get<Graphic_Multi>(graphic.path + compGraphicByTerrain.Props.snowySuffix, ShaderDatabase.Cutout, graphic.drawSize, Color.white);
			}
			return GraphicDatabase.Get<Graphic_Multi>(graphic.path + compGraphicByTerrain.Props.suffix[compGraphicByTerrain.indexTerrain], ShaderDatabase.Cutout, graphic.drawSize, Color.white);
		}
		return ((PawnRenderNode_AnimalPart)this).GraphicFor(pawn);
	}
}
