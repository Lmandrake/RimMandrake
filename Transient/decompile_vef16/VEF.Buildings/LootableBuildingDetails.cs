using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class LootableBuildingDetails : DefModExtension
{
	public bool randomFromContents;

	public IntRange totalRandomLoops = new IntRange(1, 1);

	public List<ThingAndCount> contents;

	public ThingDef buildingLeft;

	public SoundDef deconstructSound;

	public string gizmoTexture;

	public string gizmoText;

	public string gizmoDesc;

	public string cancelLootingGizmoTexture;

	public string cancelLootinggizmoText;

	public string cancelLootinggizmoDesc;

	public string requiredMod = "";

	public string overlayTexture;

	public int secondsToOpen = 20;

	public bool useHackingSpeed;

	public bool useThingSetMakerDef;

	public ThingSetMakerDetails setMakerDetails;
}
