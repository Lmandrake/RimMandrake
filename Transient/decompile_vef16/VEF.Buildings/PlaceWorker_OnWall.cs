using Verse;

namespace VEF.Buildings;

public class PlaceWorker_OnWall : PlaceWorker
{
	public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 val = loc + ((Rot4)(ref rot)).FacingCell;
		if (GenGrid.InBounds(val, map))
		{
			Building edifice = GridsUtility.GetEdifice(val, map);
			if (edifice != null && ((Thing)edifice).def.IsWall())
			{
				return AcceptanceReport.op_Implicit(false);
			}
		}
		if (GenGrid.InBounds(loc, map))
		{
			Building edifice2 = GridsUtility.GetEdifice(loc, map);
			if (edifice2 != null && ((Thing)edifice2).def.IsWall())
			{
				return AcceptanceReport.op_Implicit(true);
			}
		}
		return AcceptanceReport.op_Implicit(false);
	}
}
