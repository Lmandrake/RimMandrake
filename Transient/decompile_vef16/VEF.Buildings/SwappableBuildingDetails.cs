using Verse;

namespace VEF.Buildings;

public class SwappableBuildingDetails : DefModExtension
{
	public ThingDef buildingLeft;

	public SoundDef deconstructSound;

	public int swappingTimer = -1;
}
