using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderNode_Complex : PawnRenderNode_SimpleSwitches
{
	private PawnComplexRenderingProps ComplexProps => (PawnComplexRenderingProps)(object)((PawnRenderNode)this).props;

	public PawnRenderNode_Complex(Pawn pawn, PawnComplexRenderingProps props, PawnRenderTree tree)
		: base(pawn, props, tree)
	{
	}

	public override string TexPathFor(Pawn pawn)
	{
		if (ComplexProps.isFurskin)
		{
			Pawn_StoryTracker story = pawn.story;
			string text = ((story != null) ? story.furDef.GetFurBodyGraphicPath(pawn) : null);
			if (text != null)
			{
				return text;
			}
		}
		return base.TexPathFor(pawn);
	}

	public override Graphic GraphicFor(Pawn pawn)
	{
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		PawnComplexRenderingProps complexProps = ComplexProps;
		if (complexProps.isFurskin && pawn.story?.furDef == null)
		{
			Log.WarningOnce($"[BigAndSmall] {pawn} requested furDef, but it was null", ((Thing)pawn).thingIDNumber ^ 0x3F2A1B);
		}
		string text = ((PawnRenderNode)this).TexPathFor(pawn);
		if (GenText.NullOrEmpty(text))
		{
			Log.Warning($"[BigAndSmall] No texture path for {pawn}");
			return null;
		}
		Color color = complexProps.colorA.GetColor((PawnRenderNode)(object)this, Color.white, "someKeyStringClrOne");
		Color color2 = complexProps.colorB.GetColor((PawnRenderNode)(object)this, Color.white, "clrTwoKeyString");
		Color color3 = complexProps.colorC.GetColor((PawnRenderNode)(object)this, Color.white, "zomgClrThree");
		ShaderTypeDef shader = complexProps.shader;
		Shader shader2 = ((shader != null) ? shader.Shader : null) ?? ShaderTypeDefOf.CutoutComplex.Shader;
		return RenderingLib.GetCachableGraphics(text, Vector2.one, shader2, color, color2, color3);
	}
}
