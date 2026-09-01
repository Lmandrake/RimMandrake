using Verse;

namespace VEF.Buildings;

public class Dialog_RenameDoorTeleporter : Dialog_Rename<DoorTeleporter>
{
	public DoorTeleporter DoorTeleporter;

	public Dialog_RenameDoorTeleporter(DoorTeleporter doorTeleporter)
		: base(doorTeleporter)
	{
		DoorTeleporter = doorTeleporter;
		base.curName = doorTeleporter.Name ?? (((Def)((Thing)doorTeleporter).def).label + " #" + Rand.Range(1, 99).ToString("D2"));
	}
}
