using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

internal class PawnRenderNode_HSVHair : PawnRenderNode_Hair
{
	public PawnRenderNodeProps_HSVHair HProps => (PawnRenderNodeProps_HSVHair)(object)((PawnRenderNode)this).props;

	public PawnRenderNode_HSVHair(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		if (((PawnRenderNode_Hair)this).GraphicFor(pawn) == null)
		{
			return null;
		}
		float num = default(float);
		float num2 = default(float);
		float num3 = default(float);
		Color.RGBToHSV(((PawnRenderNode)this).ColorFor(pawn), ref num, ref num2, ref num3);
		if (HProps.valueGradientRemap != null)
		{
			num3 = HProps.valueGradientRemap.Evaluate(num3);
		}
		Color val = Color.HSVToRGB(num, Mathf.Clamp01(num2 * HProps.saturation), Mathf.Clamp01(num3 * HProps.value));
		return ((StyleItemDef)pawn.story.hairDef).GraphicFor(pawn, val);
	}
}
