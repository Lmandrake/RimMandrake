namespace VEF.Maps;

public class TerrainComp_HeatPushPowered : TerrainComp_HeatPush
{
	protected override bool ShouldPushHeat
	{
		get
		{
			if (parent.GetComp<TerrainComp_PowerTrader>() != null)
			{
				return parent.GetComp<TerrainComp_PowerTrader>().PowerOn;
			}
			return true;
		}
	}
}
