using System.Collections.Generic;
using VEF.Genes;
using Verse;

namespace VEF.Hediffs;

public class HediffCompProperties_MoveSpeedFactorByTerrainTag : HediffCompProperties
{
	public Dictionary<string, List<MoveSpeedFactor>> moveSpeedFactorByTerrainTag;
}
