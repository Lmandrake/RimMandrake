using Verse;

namespace VEF.Maps;

public class VFEResolveParams
{
	public const string Name = "VFEMResolveParams";

	public ThingDef edgeWallDef;

	public float? towerRadius;

	public bool? symmetricalSandbags;

	public bool? hasDoors;

	public bool? outdoorLighting;

	public bool? generatePawns;
}
