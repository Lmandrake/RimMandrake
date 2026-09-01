using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class BodyPartExtension : DefModExtension
{
	public List<BodyPartDef> importAllRecipesFrom = new List<BodyPartDef>();

	public List<BodyPartDef> mechanicalVersionOf = new List<BodyPartDef>();
}
