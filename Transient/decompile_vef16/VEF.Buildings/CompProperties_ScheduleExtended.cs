using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompProperties_ScheduleExtended : CompProperties_Schedule
{
	public float minLight;

	public float maxLight = 1f;

	public string sunlightMessage;

	public bool disableUnderRoof;

	public bool disableWithoutRoof;

	public string disabledDueToRoofMessage;

	public CompProperties_ScheduleExtended()
	{
		((CompProperties)this).compClass = typeof(CompScheduleExtended);
	}
}
