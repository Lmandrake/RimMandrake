using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class FlagStringData : Def
{
	private static Dictionary<FlagString, FlagStringStateData> allFlagStringData;

	public FlagStringList flags = new FlagStringList();

	public EditPawnWindow.WindowTab? displayTab;

	public string customCategory;

	public static FlagStringStateData DataFor(FlagString fs)
	{
		if (Setup().TryGetValue(fs, out var value))
		{
			return value;
		}
		return new FlagStringStateData(null, null, null);
	}

	public static Dictionary<FlagString, FlagStringStateData> Setup(bool force = false)
	{
		if (allFlagStringData != null && force)
		{
			foreach (KeyValuePair<FlagString, FlagStringStateData> allFlagStringDatum in allFlagStringData)
			{
				allFlagStringDatum.Key.ClearCache();
			}
		}
		if (allFlagStringData != null && !force)
		{
			return allFlagStringData;
		}
		allFlagStringData = new Dictionary<FlagString, FlagStringStateData>();
		foreach (FlagStringData allDef in DefDatabase<FlagStringData>.AllDefs)
		{
			foreach (FlagString flag in allDef.flags)
			{
				FlagStringStateData flagStringStateData = GenCollection.TryGetValue<FlagString, FlagStringStateData>((IReadOnlyDictionary<FlagString, FlagStringStateData>)allFlagStringData, flag, (FlagStringStateData)null);
				if (flagStringStateData != null)
				{
					flagStringStateData.displayTab = allDef.displayTab ?? flagStringStateData.displayTab;
					flagStringStateData.customCategory = allDef.customCategory ?? flagStringStateData.customCategory;
					flagStringStateData.label = ((Def)allDef).label;
					allFlagStringData[flag] = flagStringStateData;
				}
				else
				{
					allFlagStringData[flag] = new FlagStringStateData(allDef.displayTab, allDef.customCategory, ((Def)allDef).label);
				}
			}
		}
		return allFlagStringData;
	}
}
