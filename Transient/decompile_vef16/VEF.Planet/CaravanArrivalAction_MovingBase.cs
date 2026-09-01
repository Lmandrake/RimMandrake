using System;
using RimWorld;
using RimWorld.Planet;

namespace VEF.Planet;

public class CaravanArrivalAction_MovingBase : CaravanArrivalAction
{
	public MovingBase movingBase;

	public override string Label
	{
		get
		{
			throw new NotImplementedException();
		}
	}

	public override string ReportString
	{
		get
		{
			throw new NotImplementedException();
		}
	}

	public override void Arrived(Caravan caravan)
	{
		VanillaExpandedFramework_Caravan_PathFollower_ExposeData_Patch.caravansToFollow.Remove(caravan.pather);
	}

	public override FloatMenuAcceptanceReport StillValid(Caravan caravan, PlanetTile destinationTile)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		FloatMenuAcceptanceReport val = ((CaravanArrivalAction)this).StillValid(caravan, destinationTile);
		if (!FloatMenuAcceptanceReport.op_Implicit(val))
		{
			return val;
		}
		if (movingBase != null && ((WorldObject)movingBase).Tile != destinationTile)
		{
			return FloatMenuAcceptanceReport.op_Implicit(false);
		}
		return FloatMenuAcceptanceReport.op_Implicit(true);
	}

	public static CaravanArrivalAction CreateCaravanArrivalAction(CaravanArrivalAction action, Caravan caravan, MovingBase movingBase)
	{
		VanillaExpandedFramework_Caravan_PathFollower_ExposeData_Patch.caravansToFollow[caravan.pather] = new MovingBaseDestinationAction
		{
			destination = movingBase,
			arrivalActionType = ((object)action).GetType()
		};
		return action;
	}
}
