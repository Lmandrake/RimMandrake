using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNodeWorker_HumanlikeAnimalBody : PawnRenderNodeWorker
{
	private HumanlikeAnimal humanlikeAnimal;

	public HumanlikeAnimal GetHumanlikeAnimal(Pawn pawn)
	{
		if (humanlikeAnimal != null)
		{
			return humanlikeAnimal;
		}
		if (HumanlikeAnimalGenerator.humanlikeAnimals.TryGetValue(((Thing)pawn).def, out var value))
		{
			humanlikeAnimal = value;
			return humanlikeAnimal;
		}
		Log.ErrorOnce("No HumanlikeAnimal found for " + ((Def)((Thing)pawn).def).defName, 123456333);
		return null;
	}

	protected override GraphicStateDef GetGraphicState(PawnRenderNode node, PawnDrawParms parms)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		if (node.tree.currentAnimation != null || !DrawNonHumanlikeSwimmingGraphic(parms.pawn))
		{
			return ((PawnRenderNodeWorker)this).GetGraphicState(node, parms);
		}
		return GraphicStateDefOf.Swimming;
	}

	public override Vector3 OffsetFor(PawnRenderNode node, PawnDrawParms parms, out Vector3 pivot)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		return ((PawnRenderNodeWorker)this).OffsetFor(node, parms, ref pivot) + node.PrimaryGraphic.DrawOffset(parms.facing);
	}

	public bool DrawNonHumanlikeSwimmingGraphic(Pawn pawn)
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)pawn).Spawned || !pawn.WaterCellCost.HasValue)
		{
			return false;
		}
		HumanlikeAnimal obj = GetHumanlikeAnimal(pawn);
		PawnKindDef animalKind = obj.animalKind;
		int lifeStageIndex = obj.GetLifeStageIndex(pawn);
		if (animalKind.lifeStages[lifeStageIndex].swimmingGraphicData != null)
		{
			return GridsUtility.GetTerrain(((Thing)pawn).Position, ((Thing)pawn).Map).IsWater;
		}
		return false;
	}
}
