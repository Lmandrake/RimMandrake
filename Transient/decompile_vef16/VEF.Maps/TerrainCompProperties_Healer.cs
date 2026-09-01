namespace VEF.Maps;

public class TerrainCompProperties_Healer : TerrainCompProperties
{
	public float amountToHeal;

	public bool curePermanent = true;

	public TerrainCompProperties_Healer()
	{
		compClass = typeof(TerrainComp_Healer);
	}
}
