using System.Collections.Generic;
using Verse;

namespace VEF.Storyteller;

public class GenStep_Site : GenStep
{
	public StructureSetDef structureSetDef;

	public override int SeedPart => ((object)base.def).GetHashCode();

	public List<CellRect> BuildStructure(Map map, GenStepParams parms)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		return StructureSetGenerator.Generate(map, structureSetDef, map.ParentFaction, parms.sitePart.parms.points);
	}

	public override void Generate(Map map, GenStepParams parms)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		BuildStructure(map, parms);
	}
}
