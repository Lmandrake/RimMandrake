using RimWorld;
using Verse;

namespace VEF.Plants;

public class Plant_PrefersRocky : Plant
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
			return GrowthRateFactor_Fertility_Inverse * ((Plant)this).GrowthRateFactor_Temperature * ((Plant)this).GrowthRateFactor_Light * ((Plant)this).GrowthRateFactor_NoxiousHaze * ((Plant)this).GrowthRateFactor_Drought;
		}
	}

	public float GrowthRateFactor_Fertility_Inverse
	{
		get
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			float num = ((Thing)this).Map.fertilityGrid.FertilityAt(((Thing)this).Position);
			if ((double)num <= 0.7)
			{
				return 1f;
			}
			if ((double)num > 0.7 && num <= 1f)
			{
				return 0.6f;
			}
			return 0f;
		}
	}

	public override string GetInspectString()
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		if ((double)GrowthRateFactor_Fertility_Inverse == 0.6)
		{
			return TaggedString.op_Implicit(((Plant)this).GetInspectString() + "\n" + Translator.Translate("VCE_StuntedGrowthFertility"));
		}
		if (GrowthRateFactor_Fertility_Inverse == 0f)
		{
			return TaggedString.op_Implicit(((Plant)this).GetInspectString() + "\n" + Translator.Translate("VCE_StoppedGrowthFertility"));
		}
		return ((Plant)this).GetInspectString();
	}
}
