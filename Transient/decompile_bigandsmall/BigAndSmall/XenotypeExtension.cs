using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class XenotypeExtension : DefModExtension
{
	public float morphWeight = 1f;

	public bool morphIgnoreGender;

	public ThingDef setRace;

	public bool forceRace;

	public List<List<string>> genePickPriority;
}
