using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class CompProperties_CompRemover : CompProperties
{
	public List<string> compNameList = new List<string>();

	public List<string> compNamespaceList = new List<string>();

	public List<string> compFullNameList = new List<string>();

	public CompProperties_CompRemover()
	{
		base.compClass = typeof(CompRemover);
	}
}
