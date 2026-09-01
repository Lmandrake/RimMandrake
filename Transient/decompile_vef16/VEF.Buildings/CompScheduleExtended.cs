using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompScheduleExtended : CompSchedule
{
	public CompProperties_ScheduleExtended Props => (CompProperties_ScheduleExtended)(object)((ThingComp)this).props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		RecalculateAllowed();
	}

	public override void CompTickInterval(int delta)
	{
		if (Gen.IsHashIntervalTick((Thing)(object)((ThingComp)this).parent, 250, delta))
		{
			RecalculateAllowed();
		}
	}

	public override void CompTickRare()
	{
		RecalculateAllowed();
	}

	public override void CompTickLong()
	{
		RecalculateAllowed();
	}

	private void RecalculateAllowed()
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompSchedule)this).Allowed = AcceptanceReport.op_Implicit(ShouldBeAllowed());
	}

	protected virtual AcceptanceReport ShouldBeAllowed()
	{
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		Thing spawnedParentOrMe = ((Thing)((ThingComp)this).parent).SpawnedParentOrMe;
		if (spawnedParentOrMe == null)
		{
			return AcceptanceReport.op_Implicit(true);
		}
		CompProperties_ScheduleExtended props = Props;
		if (props.disableUnderRoof)
		{
			if (RoofUtility.IsAnyCellUnderRoof(spawnedParentOrMe))
			{
				return AcceptanceReport.op_Implicit(props.disabledDueToRoofMessage);
			}
		}
		else if (props.disableWithoutRoof && !RoofUtility.IsAnyCellUnderRoof(spawnedParentOrMe))
		{
			return AcceptanceReport.op_Implicit(props.disabledDueToRoofMessage);
		}
		float curSkyGlow = spawnedParentOrMe.Map.skyManager.CurSkyGlow;
		if (props.minLight > props.maxLight)
		{
			if (curSkyGlow < props.maxLight || curSkyGlow > props.minLight)
			{
				return AcceptanceReport.op_Implicit(props.sunlightMessage);
			}
		}
		else if (curSkyGlow < props.minLight || curSkyGlow > props.maxLight)
		{
			return AcceptanceReport.op_Implicit(props.sunlightMessage);
		}
		if (((CompProperties_Schedule)props).startTime != 0f || ((CompProperties_Schedule)props).endTime != 1f)
		{
			float num = GenLocalDate.DayPercent(spawnedParentOrMe);
			if (((CompProperties_Schedule)props).startTime > ((CompProperties_Schedule)props).endTime)
			{
				if (num < ((CompProperties_Schedule)props).endTime || num > ((CompProperties_Schedule)props).startTime)
				{
					return AcceptanceReport.op_Implicit(false);
				}
			}
			else if (num < ((CompProperties_Schedule)props).startTime || num > ((CompProperties_Schedule)props).endTime)
			{
				return AcceptanceReport.op_Implicit(false);
			}
		}
		return AcceptanceReport.op_Implicit(true);
	}

	public override string CompInspectStringExtra()
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		if (((CompSchedule)this).Allowed)
		{
			return null;
		}
		AcceptanceReport val = ShouldBeAllowed();
		return ((AcceptanceReport)(ref val)).Reason ?? ((CompProperties_Schedule)Props).offMessage;
	}
}
