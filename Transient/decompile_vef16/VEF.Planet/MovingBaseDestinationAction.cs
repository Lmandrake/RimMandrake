using System;
using Verse;

namespace VEF.Planet;

public class MovingBaseDestinationAction : IExposable
{
	public MovingBase destination;

	public Type arrivalActionType;

	public void ExposeData()
	{
		Scribe_References.Look<MovingBase>(ref destination, "movingBaseDestination", false);
		Scribe_Values.Look<Type>(ref arrivalActionType, "arrivalActionType", (Type)null, false);
	}
}
