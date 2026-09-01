using Verse;

namespace VEF.Buildings;

public class PlaceWorker_OnSand : PlaceWorker
{
	public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Invalid comparison between Unknown and I4
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		foreach (IntVec3 item in GenAdj.CellsOccupiedBy(loc, rot, checkingDef.Size))
		{
			if ((int)map.terrainGrid.TerrainAt(item).categoryType != 3)
			{
				return new AcceptanceReport(TaggedString.op_Implicit(Translator.Translate("VFE_NeedsSand")));
			}
		}
		return AcceptanceReport.op_Implicit(true);
	}
}
