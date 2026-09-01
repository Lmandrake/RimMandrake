using RimWorld;
using Verse;

namespace VEF.Plants;

public class Plant_ChecksSea : Plant
{
	private const int radius = 6;

	private int numberOfSea;

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
			return ((Plant)this).GrowthRateFactor_Fertility * ((Plant)this).GrowthRateFactor_Temperature * ((Plant)this).GrowthRateFactor_Light * ((Plant)this).GrowthRateFactor_NoxiousHaze * ((Plant)this).GrowthRateFactor_Drought * GrowthRateFactor_Sea;
		}
	}

	public float GrowthRateFactor_Sea
	{
		get
		{
			if ((double)(1f + 0.01f * (float)numberOfSea) > 1.3)
			{
				return 1.3f;
			}
			return 1f + 0.01f * (float)numberOfSea;
		}
	}

	public override void SpawnSetup(Map map, bool respawningAfterLoad)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		((Plant)this).SpawnSetup(map, respawningAfterLoad);
		int num = GenRadial.NumCellsInRadius(6f);
		for (int i = 0; i < num; i++)
		{
			IntVec3 val = ((Thing)this).Position + GenRadial.RadialPattern[i];
			if (GenGrid.InBounds(val, map))
			{
				TerrainDef terrain = GridsUtility.GetTerrain(val, map);
				if (terrain != null && terrain.IsWater && !terrain.IsRiver)
				{
					numberOfSea++;
				}
			}
		}
	}

	public override void ExposeData()
	{
		((Plant)this).ExposeData();
		Scribe_Values.Look<int>(ref numberOfSea, "numberOfSea", 0, false);
	}

	public override string GetInspectString()
	{
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		if (GrowthRateFactor_Sea == 1f)
		{
			return TaggedString.op_Implicit(((Plant)this).GetInspectString() + "\n" + Translator.Translate("VCE_NoSeaTilesNearby"));
		}
		return TaggedString.op_Implicit(((Plant)this).GetInspectString() + "\n" + TranslatorFormattedStringExtensions.Translate("VCE_SeaTilesNearby", NamedArgument.op_Implicit(numberOfSea)));
	}
}
