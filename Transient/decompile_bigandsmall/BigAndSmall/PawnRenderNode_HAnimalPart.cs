using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNode_HAnimalPart : PawnRenderNode
{
	public PawnRenderNode_HAnimalPart(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
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
		//IL_0106: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Invalid comparison between Unknown and I4
		//IL_015e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Invalid comparison between Unknown and I4
		//IL_021f: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		//IL_022f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0235: Unknown result type (might be due to invalid IL or missing references)
		//IL_0240: Unknown result type (might be due to invalid IL or missing references)
		//IL_0245: Unknown result type (might be due to invalid IL or missing references)
		//IL_024e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		//IL_0263: Unknown result type (might be due to invalid IL or missing references)
		//IL_0268: Unknown result type (might be due to invalid IL or missing references)
		//IL_026a: Unknown result type (might be due to invalid IL or missing references)
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0283: Expected I4, but got Unknown
		//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_018a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_0328: Unknown result type (might be due to invalid IL or missing references)
		//IL_032d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0330: Unknown result type (might be due to invalid IL or missing references)
		//IL_0336: Invalid comparison between Unknown and I4
		//IL_02fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0300: Invalid comparison between Unknown and I4
		//IL_02ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0350: Unknown result type (might be due to invalid IL or missing references)
		//IL_0352: Unknown result type (might be due to invalid IL or missing references)
		//IL_036b: Unknown result type (might be due to invalid IL or missing references)
		//IL_036d: Unknown result type (might be due to invalid IL or missing references)
		HumanlikeAnimalGenerator.humanlikeAnimals.TryGetValue(((Thing)pawn).def, out var value);
		if (value == null)
		{
			Log.ErrorOnce("No HumanlikeAnimal found for " + ((Def)((Thing)pawn).def).defName, 123456333);
			return null;
		}
		PawnKindDef animalKind = value.animalKind;
		PawnKindLifeStage val = animalKind.lifeStages[value.GetLifeStageIndex(pawn)];
		Graphic val2 = null;
		AlternateGraphic val3 = null;
		if (((Thing)pawn).overrideGraphicIndex.HasValue && animalKind.alternateGraphics?.Count > ((Thing)pawn).overrideGraphicIndex + 1)
		{
			val3 = animalKind.alternateGraphics[((Thing)pawn).overrideGraphicIndex.Value];
			val2 = val3.GetGraphic(val.bodyGraphicData.Graphic);
		}
		if (val2 == null)
		{
			val2 = (((int)pawn.gender != 2 || val.femaleGraphicData == null) ? val.bodyGraphicData.Graphic : val.femaleGraphicData.Graphic);
		}
		if ((pawn.Dead || (pawn.IsMutant && pawn.mutant.Def.useCorpseGraphics)) && val.corpseGraphicData != null)
		{
			val2 = (((int)pawn.gender != 2 || val.femaleCorpseGraphicData == null) ? val.corpseGraphicData.Graphic.GetColoredVersion(val.corpseGraphicData.Graphic.Shader, val2.Color, val2.ColorTwo) : val.femaleCorpseGraphicData.Graphic.GetColoredVersion(val.femaleCorpseGraphicData.Graphic.Shader, val2.Color, val2.ColorTwo));
		}
		ColorSetting colorSetting = BSDefs.BS_DefaultSapientAnimalColorA.color;
		ColorSetting colorSetting2 = BSDefs.BS_DefaultSapientAnimalColorB.color;
		CustomMaterial bodyMaterial = HumanoidPawnScaler.GetCache(pawn).bodyMaterial;
		if (bodyMaterial != null)
		{
			if (bodyMaterial.colorA != null)
			{
				colorSetting = bodyMaterial.colorA;
			}
			if (bodyMaterial.colorB != null)
			{
				colorSetting2 = bodyMaterial.colorB;
			}
		}
		Color color = colorSetting.GetColor((PawnRenderNode)(object)this, val2.color, "someKeyStringClrOne");
		Color color2 = colorSetting2.GetColor((PawnRenderNode)(object)this, val2.colorTwo, "clrTwoKeyString");
		val2 = val2.GetColoredVersion(val2.Shader, color, color2);
		RotDrawMode curRotDrawMode = pawn.Drawer.renderer.CurRotDrawMode;
		switch (curRotDrawMode - 1)
		{
		case 0:
			if (ModsConfig.AnomalyActive && pawn.IsMutant && pawn.mutant.HasTurned)
			{
				return val2.GetColoredVersion(ShaderDatabase.Cutout, MutantUtility.GetMutantSkinColor(pawn, color), MutantUtility.GetMutantSkinColor(pawn, color2));
			}
			return val2;
		case 1:
			return val2.GetColoredVersion(ShaderDatabase.Cutout, PawnRenderUtility.GetRottenColor(color), PawnRenderUtility.GetRottenColor(color2));
		case 3:
			if (val.dessicatedBodyGraphicData != null)
			{
				Graphic val4;
				if (pawn.RaceProps.FleshType != FleshTypeDefOf.Insectoid)
				{
					val4 = (((int)pawn.gender == 2 && val.femaleDessicatedBodyGraphicData != null) ? val.femaleDessicatedBodyGraphicData.GraphicColoredFor((Thing)(object)pawn) : val.dessicatedBodyGraphicData.GraphicColoredFor((Thing)(object)pawn));
				}
				else
				{
					Color dessicatedColorInsect = PawnRenderUtility.DessicatedColorInsect;
					val4 = (((int)pawn.gender == 2 && val.femaleDessicatedBodyGraphicData != null) ? val.femaleDessicatedBodyGraphicData.Graphic.GetColoredVersion(ShaderDatabase.Cutout, dessicatedColorInsect, dessicatedColorInsect) : val.dessicatedBodyGraphicData.Graphic.GetColoredVersion(ShaderDatabase.Cutout, dessicatedColorInsect, dessicatedColorInsect));
				}
				if (pawn.IsMutant)
				{
					val4.ShadowGraphic = val2.ShadowGraphic;
				}
				if (val3 != null)
				{
					val4 = val3.GetDessicatedGraphic(val4);
				}
				return val4;
			}
			break;
		}
		return null;
	}
}
