using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace VEF.Buildings;

public class CaravanArrivalAction_UseDoorTeleporter : CaravanArrivalAction
{
	public DoorTeleporter Target;

	public DoorTeleporter Use;

	public override string Label => TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.TeleportTo", NamedArgument.op_Implicit(Target.Name)));

	public override string ReportString => JobUtility.GetResolvedJobReportRaw(VEFDefOf.VEF_UseDoorTeleporter.reportString, Use.Name, (object)Use, Target.Name, (object)Target, (string)null, (object)null);

	public CaravanArrivalAction_UseDoorTeleporter(DoorTeleporter origin, DoorTeleporter dest)
	{
		Use = origin;
		Target = dest;
	}

	public override void Arrived(Caravan caravan)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		((WorldObject)caravan).Tile = ((Thing)Target).Map.Tile;
		caravan.Notify_Teleported();
	}

	public override FloatMenuAcceptanceReport StillValid(Caravan caravan, PlanetTile destinationTile)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		DoorTeleporter target = Target;
		int num;
		if (target != null && ((Thing)target).Spawned)
		{
			target = Use;
			num = ((target != null && ((Thing)target).Spawned) ? 1 : 0);
		}
		else
		{
			num = 0;
		}
		return FloatMenuAcceptanceReport.op_Implicit((byte)num != 0);
	}

	public static IEnumerable<FloatMenuOption> GetFloatMenuOptions(Caravan caravan, DoorTeleporter origin, DoorTeleporter dest)
	{
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		return CaravanArrivalActionUtility.GetFloatMenuOptions<CaravanArrivalAction_UseDoorTeleporter>((Func<FloatMenuAcceptanceReport>)(() => FloatMenuAcceptanceReport.op_Implicit(true)), (Func<CaravanArrivalAction_UseDoorTeleporter>)(() => new CaravanArrivalAction_UseDoorTeleporter(origin, dest)), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.TeleportTo", NamedArgument.op_Implicit(dest.Name))), caravan, ((Thing)origin).Map.Tile, (WorldObject)(object)((Thing)origin).Map.Parent, (Action<Action>)null);
	}

	public override void ExposeData()
	{
		((CaravanArrivalAction)this).ExposeData();
		Scribe_References.Look<DoorTeleporter>(ref Target, "target", false);
		Scribe_References.Look<DoorTeleporter>(ref Use, "use", false);
	}
}
