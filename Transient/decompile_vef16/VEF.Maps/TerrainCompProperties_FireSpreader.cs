namespace VEF.Maps;

public class TerrainCompProperties_FireSpreader : TerrainCompProperties
{
	public int spreadTimer;

	public TerrainCompProperties_FireSpreader()
	{
		compClass = typeof(TerrainComp_FireSpreader);
	}
}
