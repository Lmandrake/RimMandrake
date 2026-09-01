using System.Collections.Generic;
using RimWorld.Planet;
using Verse;

namespace VEF.Buildings;

public class WorldComponent_DoorTeleporterManager : WorldComponent
{
	public static WorldComponent_DoorTeleporterManager Instance;

	private HashSet<DoorTeleporter> doorTeleporters = new HashSet<DoorTeleporter>();

	public HashSet<DoorTeleporter> DoorTeleporters
	{
		get
		{
			doorTeleporters.RemoveWhere((DoorTeleporter doorTeleporter) => doorTeleporter == null || !((Thing)doorTeleporter).Spawned);
			return doorTeleporters;
		}
	}

	public WorldComponent_DoorTeleporterManager(World world)
		: base(world)
	{
		Instance = this;
	}
}
