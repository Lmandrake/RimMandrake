using Verse;

namespace VEF.Buildings;

public class PlaceWorker_OnWater : PlaceWorker
{
	public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		foreach (IntVec3 item in GenAdj.CellsOccupiedBy(loc, rot, checkingDef.Size))
		{
			if (!map.terrainGrid.TerrainAt(item).IsWater)
			{
				return new AcceptanceReport(TaggedString.op_Implicit(Translator.Translate("VFE_NeedsWater")));
			}
		}
		return AcceptanceReport.op_Implicit(true);
	}
}
