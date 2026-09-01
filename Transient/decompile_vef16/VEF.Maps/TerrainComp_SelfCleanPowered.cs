namespace VEF.Maps;

public class TerrainComp_SelfCleanPowered : TerrainComp_SelfClean
{
	protected override bool CanClean
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
