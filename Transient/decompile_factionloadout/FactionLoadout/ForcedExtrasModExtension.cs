using System.Collections.Generic;
using Verse;

namespace FactionLoadout;

public class ForcedExtrasModExtension : DefModExtension
{
	public List<ForcedHediff> forcedHediffs = new List<ForcedHediff>();

	public List<ForcedGene> forcedGenes = new List<ForcedGene>();

	public List<ForcedTrait> forcedTraits = new List<ForcedTrait>();
}
