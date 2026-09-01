using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class ThoughtWorker_ThoughtFromNearbyThingDef : ThoughtWorker
{
	private const float Radius = 15f;

	protected override ThoughtState CurrentStateInternal(Pawn p)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		if (!((Thing)p).Spawned)
		{
			return ThoughtState.op_Implicit(false);
		}
		if (!((Def)base.def).HasModExtension<ThoughtGiverByProximityDefExtension>())
		{
			return ThoughtState.op_Implicit(false);
		}
		ThoughtGiverByProximityDefExtension modExtension = ((Def)base.def).GetModExtension<ThoughtGiverByProximityDefExtension>();
		if (modExtension.ThingToGiveThought == null)
		{
			return ThoughtState.op_Implicit(false);
		}
		List<Thing> list = ((Thing)p).Map.listerThings.ThingsOfDef(modExtension.ThingToGiveThought);
		for (int i = 0; i < list.Count; i++)
		{
			CompPowerTrader val = ThingCompUtility.TryGetComp<CompPowerTrader>(list[i]);
			if ((val == null || val.PowerOn) && list[i] != p)
			{
				IntVec3 position = ((Thing)p).Position;
				if (((IntVec3)(ref position)).InHorDistOf(list[i].Position, modExtension.DistanceToGiveThought))
				{
					return ThoughtState.op_Implicit(true);
				}
			}
		}
		return ThoughtState.op_Implicit(false);
	}
}
