using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class GeneAutoPatcherSettings : Def
{
	public int priority;

	public string targetModID;

	public string targetGeneType;

	public string geneWildcard;

	public string targetModExtension;

	public string backgroundPathEndogenes;

	public string backgroundPathXenogenes;

	public string backgroundPathArchite;

	public bool mechanical;

	[Unsaved(true)]
	public List<ModContentPack> targetMods;

	public void Setup(List<ModContentPack> activeMods)
	{
		if (targetModID != null)
		{
			targetModID = targetModID.ToLower();
			targetMods = activeMods.Where((ModContentPack x) => x.PackageId.StartsWith(targetModID)).ToList();
		}
	}
}
