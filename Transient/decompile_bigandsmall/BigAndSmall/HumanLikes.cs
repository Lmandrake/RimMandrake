using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

/// <summary>
/// Patch defs in other mods. And things related to defs.
/// </summary>
public class HumanLikes : Def
{
	private static List<ThingDef> _humanlikes;

	public List<ThingDef> thingList = new List<ThingDef>();

	public static List<ThingDef> Humanlikes => _humanlikes ?? (_humanlikes = DefDatabase<HumanLikes>.AllDefs.SelectMany((HumanLikes x) => x.thingList).ToList());
}
