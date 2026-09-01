using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnComplexRenderingProps : PawnRenderNode_SimpleSwitchesProps
{
	public ShaderTypeDef shader;

	public ColorSetting colorA = new ColorSetting();

	public ColorSetting colorB = new ColorSetting();

	public ColorSetting colorC = new ColorSetting();

	public Vector4 colorMultiplier = new Vector4(1f, 1f, 1f, 1f);

	/// <summary>
	/// Hacky but this avoid us making a seperate class for what is basically just changing the texture path.
	/// </summary>
	public bool isFurskin;
}
