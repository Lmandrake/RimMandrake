using RimWorld;
using Verse;

namespace VEF.Plants;

internal class Plant_NeedsOutside : Plant
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
			return ((Plant)this).GrowthRateFactor_Fertility * ((Plant)this).GrowthRateFactor_Temperature * ((Plant)this).GrowthRateFactor_NoxiousHaze * ((Plant)this).GrowthRateFactor_Drought * GrowthRateFactor_OutsideAndRoofed;
		}
	}

	public float GrowthRateFactor_OutsideAndRoofed
	{
		get
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			Room room = GridsUtility.GetRoom(((Thing)this).Position, ((Thing)this).Map);
			if (room != null && room.OutdoorsForWork && ((Thing)this).Map.roofGrid.Roofed(((Thing)this).Position))
			{
				return 1f;
			}
			return 0f;
		}
	}

	public override string GetInspectString()
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		if (GrowthRateFactor_OutsideAndRoofed == 0f)
		{
			return TaggedString.op_Implicit(((Plant)this).GetInspectString() + "\n" + Translator.Translate("VCE_NeedsShade"));
		}
		return ((Plant)this).GetInspectString();
	}
}
