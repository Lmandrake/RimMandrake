using System.Collections.Generic;
using Verse;

namespace VEF.Buildings;

public class CompProperties_RandomBuildingGraphic : CompProperties
{
	public List<string> randomGraphics;

	public List<string> optionalNames;

	public bool startAsRandom = true;

	public bool disableRandomButton;

	public bool disableGraphicChoosingButton;

	public bool disableAllButtons;

	public bool useSouthOrientation;

	public ThingDef onlyApplyToThisDef;

	public CompProperties_RandomBuildingGraphic()
	{
		base.compClass = typeof(CompRandomBuildingGraphic);
	}
}
