using RimWorld;
using Verse;

namespace VEF.Plants;

public class Plant_AffectedBySnow : Plant
{
	public override float GrowthRate
	{
		get
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			if (((Plant)this).Blighted)
			{
				return 0f;
			}
			if (((Thing)this).Spawned && !PlantUtility.GrowthSeasonNow(((Thing)this).Position, ((Thing)this).Map, ((Thing)this).def))
			{
				return 0f;
			}
			return ((Plant)this).GrowthRateFactor_Fertility * ((Plant)this).GrowthRateFactor_Temperature * ((Plant)this).GrowthRateFactor_Light * ((Plant)this).GrowthRateFactor_NoxiousHaze * ((Plant)this).GrowthRateFactor_Drought * GrowthRateFactor_Snow;
		}
	}

	public float GrowthRateFactor_Snow
	{
		get
		{
			if (((Thing)this).Map.weatherManager.SnowRate > 0f)
			{
				return 1.5f;
			}
			return 1f;
		}
	}
}
