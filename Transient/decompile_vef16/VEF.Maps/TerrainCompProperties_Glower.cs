using Verse;

namespace VEF.Maps;

public class TerrainCompProperties_Glower : TerrainCompProperties
{
	public float overlightRadius;

	public float glowRadius = 14f;

	public ColorInt glowColor = new ColorInt(255, 255, 255, 0) * 1.45f;

	public bool powered = true;

	public TerrainCompProperties_Glower()
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		compClass = typeof(TerrainComp_Glower);
	}
}
