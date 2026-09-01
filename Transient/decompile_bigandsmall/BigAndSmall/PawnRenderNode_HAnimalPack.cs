using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNode_HAnimalPack : PawnRenderNode
{
	public bool isPackAnimal;

	public PawnRenderNode_HAnimalPack(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		props.pawnType = (RenderNodePawnType)0;
	}

	public override GraphicMeshSet MeshSetFor(Pawn pawn)
	{
		Graphic val = ((PawnRenderNode)this).GraphicFor(pawn);
		if (val != null)
		{
			return MeshPool.GetMeshSetForSize(val.drawSize.x, val.drawSize.y);
		}
		return null;
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Invalid comparison between Unknown and I4
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		HumanlikeAnimalGenerator.humanlikeAnimals.TryGetValue(((Thing)pawn).def, out var value);
		if (value == null)
		{
			Log.ErrorOnce("No HumanlikeAnimal found for " + ((Def)((Thing)pawn).def).defName, 123456333);
			return null;
		}
		if (!value.animal.race.packAnimal)
		{
			isPackAnimal = false;
			return null;
		}
		isPackAnimal = true;
		PawnKindLifeStage val = value.animalKind.lifeStages[value.GetLifeStageIndex(pawn)];
		Graphic val2 = (((int)pawn.gender == 2 && val.femaleGraphicData != null) ? val.femaleGraphicData.Graphic : val.bodyGraphicData.Graphic);
		return GraphicDatabase.Get<Graphic_Multi>(val2.path + "Pack", ShaderDatabase.Cutout, val2.drawSize, Color.white);
	}
}
