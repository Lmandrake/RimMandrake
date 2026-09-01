using Verse;

namespace VEF.Graphics;

public class PawnRenderNodeProperties_Omni : PawnRenderNodeProperties
{
	public ConditionalGraphicSet conditionalGraphics = new ConditionalGraphicSet();

	public bool autoBodyTypePaths;

	public bool autoBodyTypeMasks;
}
