using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PawnRenderingProps_Ultimate : PawnRenderNodeProperties
{
	public ShaderTypeDef shader;

	protected ConditionalGraphicsSet conditionalGraphics;

	protected GraphicSetDef graphicSetDef;

	public Vector4 colorMultiplier = new Vector4(1f, 1f, 1f, 1f);

	public bool invertEastWest;

	public bool mirrorNorth;

	public bool autoBodyTypePaths;

	public bool autoBodyTypeMasks;

	public bool useHeadMesh;

	public ConditionalGraphicsSet generated;

	public ConditionalGraphicsSet GraphicSet
	{
		get
		{
			if (graphicSetDef == null)
			{
				return conditionalGraphics;
			}
			return graphicSetDef.conditionalGraphics;
		}
	}
}
