using RimWorld;
using Verse;

namespace VEF.Plants;

internal class Plant_FasterInTropics : Plant
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
			return ((Plant)this).GrowthRateFactor_Fertility * ((Plant)this).GrowthRateFactor_Temperature * ((Plant)this).GrowthRateFactor_Light * ((Plant)this).GrowthRateFactor_NoxiousHaze * ((Plant)this).GrowthRateFactor_Drought * GrowthRateFactor_Latitude;
		}
	}

	public float GrowthRateFactor_Latitude
	{
		get
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Invalid comparison between Unknown and I4
			if ((int)LatitudeSectionUtility.GetReportedLatitudeSection(Find.WorldGrid.LongLatOf(((Thing)this).Map.Tile).y) == 1)
			{
				return 1.3f;
			}
			return 1f;
		}
	}

	public override string GetInspectString()
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		if (GrowthRateFactor_Latitude == 1f)
		{
			return TaggedString.op_Implicit(((Plant)this).GetInspectString() + "\n" + TranslatorFormattedStringExtensions.Translate("VCE_NotInEquator", NamedArgument.op_Implicit(LatitudeSectionUtility.GetMaxLatitude((LatitudeSection)1))));
		}
		return TaggedString.op_Implicit(((Plant)this).GetInspectString() + "\n" + Translator.Translate("VCE_InEquator"));
	}
}
