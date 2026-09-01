namespace VEF.Maps;

public class TerrainCompProperties_TempControl : TerrainCompProperties
{
	public float energyPerSecond;

	public bool reliesOnPower = true;

	public float lowPowerConsumptionFactor = 0.2f;

	public bool cleansSnow = true;

	public float snowMeltAmountPerSecond = 0.02f;

	public TerrainCompProperties_TempControl()
	{
		compClass = typeof(TerrainComp_TempControl);
	}
}
