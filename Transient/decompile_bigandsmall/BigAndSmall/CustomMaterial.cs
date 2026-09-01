using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CustomMaterial
{
	public ShaderTypeDef shader;

	public ColorSetting colorA = new ColorSetting();

	public ColorSetting colorB = new ColorSetting();

	public ColorSetting colorC = new ColorSetting();

	public bool overrideDesiccated;

	public Graphic GetGraphic(PawnRenderNode pawnRenderNode, string path, Color colorOne, Color colorTwo, Color colorThree, Vector2 drawSize)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		colorOne = colorA.GetColor(pawnRenderNode, colorOne, "someKeyStringClrOne");
		colorTwo = colorB.GetColor(pawnRenderNode, colorTwo, "clrTwoKeyString");
		colorThree = colorC.GetColor(pawnRenderNode, colorThree, "zomgClrThree");
		return RenderingLib.GetCachableGraphics(path, drawSize, shader.Shader, colorOne, colorTwo, colorThree);
	}
}
