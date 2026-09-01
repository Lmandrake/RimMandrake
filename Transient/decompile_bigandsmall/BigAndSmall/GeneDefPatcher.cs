using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public static class GeneDefPatcher
{
	public static Dictionary<GeneDef, GeneUIDrawData> customGeneBackgrounds = new Dictionary<GeneDef, GeneUIDrawData>();

	private static List<GeneAutoPatcherSettings> patchSettings;

	public static void PatchExistingDefs()
	{
		patchSettings = DefDatabase<GeneAutoPatcherSettings>.AllDefs.ToList();
		patchSettings.OrderBy((GeneAutoPatcherSettings x) => x.priority);
		List<ModContentPack> activeMods = LoadedModManager.RunningMods.ToList();
		patchSettings.ForEach(delegate(GeneAutoPatcherSettings x)
		{
			x.Setup(activeMods);
		});
		foreach (GeneDef item in DefDatabase<GeneDef>.AllDefsListForReading)
		{
			foreach (GeneAutoPatcherSettings patchSetting in patchSettings)
			{
				if (ShouldPatchWithData(item, patchSetting))
				{
					GeneDef val = item;
					if (((Def)val).modExtensions == null)
					{
						((Def)val).modExtensions = new List<DefModExtension>();
					}
					AddGeneBackgrounds(item, patchSetting);
				}
			}
			if (((Def)item).modExtensions == null)
			{
				continue;
			}
			foreach (DefModExtension modExtension in ((Def)item).modExtensions)
			{
				if (modExtension is PawnExtension { hideInGenePicker: not false })
				{
					Dialog_CreateXenotypePatches.hiddenGenes.Add(item);
				}
			}
		}
	}

	private static bool ShouldPatchWithData(GeneDef def, GeneAutoPatcherSettings patchData)
	{
		if (patchData.targetMods != null && !patchData.targetMods.Contains(((Def)def).modContentPack))
		{
			return false;
		}
		if (patchData.targetGeneType != null && !((object)def).GetType().ToString().EndsWith(patchData.targetGeneType))
		{
			return false;
		}
		if (patchData.geneWildcard != null && !((Def)def).defName.Contains(patchData.geneWildcard))
		{
			return false;
		}
		if (patchData.targetModExtension != null)
		{
			List<DefModExtension> modExtensions = ((Def)def).modExtensions;
			if (modExtensions == null || !GenCollection.Any<DefModExtension>(modExtensions, (Predicate<DefModExtension>)((DefModExtension x) => ((object)x).GetType().ToString().EndsWith(patchData.targetModExtension))))
			{
				return false;
			}
		}
		return true;
	}

	private static void AddGeneBackgrounds(GeneDef geneDef, GeneAutoPatcherSettings patchData)
	{
		if (!customGeneBackgrounds.ContainsKey(geneDef))
		{
			customGeneBackgrounds[geneDef] = new GeneUIDrawData();
		}
		if (customGeneBackgrounds.TryGetValue(geneDef, out var value))
		{
			if (patchData.mechanical)
			{
				value.endoBackgroundPath_Mech = patchData.backgroundPathEndogenes ?? value.endoBackgroundPath_Mech;
				value.xenoBackgroundPath_Mech = patchData.backgroundPathXenogenes ?? value.xenoBackgroundPath_Mech;
				value.architeBackgroundPath_Mech = patchData.backgroundPathArchite ?? value.architeBackgroundPath_Mech;
			}
			else
			{
				value.endoBackgroundPath = patchData.backgroundPathEndogenes ?? value.endoBackgroundPath;
				value.xenoBackgroundPath = patchData.backgroundPathXenogenes ?? value.xenoBackgroundPath;
				value.architeBackgroundPath = patchData.backgroundPathArchite ?? value.architeBackgroundPath;
			}
			value.architeCost = geneDef.biostatArc;
		}
	}
}
