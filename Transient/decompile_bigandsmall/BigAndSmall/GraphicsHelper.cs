using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class GraphicsHelper
{
	public static Graphic GetBlankMaterial()
	{
		return GraphicDatabase.Get<Graphic_Multi>("UI/EmptyImage");
	}

	public static Apparel GetApparelFromNode(this PawnRenderNode node)
	{
		if (node is IUltimateRendering ultimateRendering)
		{
			return ultimateRendering.Base.apparel;
		}
		return ((node is PawnRenderNode_Apparel) ? node : null)?.apparel;
	}

	public static Color GetColorFromColorListRange(this List<Color> colorList, float rngValue, float rngValue2)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		if (colorList.Count == 1)
		{
			return colorList[0];
		}
		if (colorList.Count == 0)
		{
			Log.WarningOnce("Tried to get color from empty color list. Returning White.", 92345);
			return Color.white;
		}
		int num = (int)Mathf.Lerp(0f, (float)(colorList.Count - 2), rngValue);
		int index = num + 1;
		Color val = colorList[num];
		Color val2 = colorList[index];
		return val * (1f - rngValue2) + val2 * rngValue2;
	}

	public static Color GetColorFromColorListRangeWithWeights(this ColorOptionList colorList, float rngValue)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		List<(float, Color)> colors = colorList.colors;
		if (colors.Count == 0)
		{
			Log.WarningOnce("Tried to get color from empty color list. Returning White.", 92345);
			return Color.white;
		}
		if (colors.Count == 1)
		{
			return colors[0].Item2;
		}
		float num = colors.Sum<(float, Color)>(((float weight, Color color) c) => c.weight);
		float num2 = rngValue * num;
		float num3 = 0f;
		for (int i = 0; i < colors.Count - 1; i++)
		{
			float num4 = num3 + colors[i].Item1;
			if (num2 <= num4)
			{
				float num5 = (num2 - num3) / colors[i].Item1;
				return Color.Lerp(colors[i].Item2, colors[i + 1].Item2, num5);
			}
			num3 = num4;
		}
		return colors.Last().Item2;
	}

	public static Graphic TryGetCustomGraphics(PawnRenderNode renderNode, string path, Color colorOne, Color colorTwo, Color colorThree, Vector2 drawSize, CustomMaterial data)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		if (data != null)
		{
			return data.GetGraphic(renderNode, path, colorOne, colorTwo, colorThree, drawSize);
		}
		return RenderingLib.GetCachableGraphics(path, drawSize, ShaderTypeDefOf.Cutout.Shader, colorOne, colorTwo, colorThree);
	}

	public static int GetPartsWithHediff(Pawn pawn, int count, BodyPartDef targetPart, HediffDef hediffDef, bool? mirrored = null)
	{
		if (mirrored == true)
		{
			return pawn.health.hediffSet.hediffs.Sum((Hediff hediff) => (hediff.def == hediffDef && hediff.Part.def == targetPart && hediff.Part.flipGraphic == mirrored) ? 1 : 0);
		}
		return pawn.health.hediffSet.hediffs.Sum((Hediff hediff) => (hediff.def == hediffDef && hediff.Part.def == targetPart) ? 1 : 0);
	}

	public static int GetPartsReplaced(Pawn pawn, int count, BodyPartDef targetPart, bool? mirrored = null)
	{
		if (mirrored == true)
		{
			return pawn.health.hediffSet.hediffs.Sum((Hediff hediff) => (hediff.Part.def == targetPart && hediff is Hediff_AddedPart && hediff.Part.flipGraphic == mirrored) ? 1 : 0);
		}
		return pawn.health.hediffSet.hediffs.Sum((Hediff hediff) => (hediff.Part.def == targetPart && hediff is Hediff_AddedPart) ? 1 : 0);
	}
}
