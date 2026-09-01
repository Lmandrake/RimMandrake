using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF.OptionalFeatures;

public class OptionalFeatures : Mod
{
	public OptionalFeatures(ModContentPack content)
		: base(content)
	{
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			Dictionary<string, OptionalFeaturesDef> dictionary = new Dictionary<string, OptionalFeaturesDef>();
			foreach (OptionalFeaturesDef item in DefDatabase<OptionalFeaturesDef>.AllDefsListForReading)
			{
				if (item.feature != null)
				{
					dictionary[item.feature] = item;
				}
			}
			foreach (string item2 in DefDatabase<ModDef>.AllDefs.SelectMany((ModDef def) => def.Activate))
			{
				if (item2 != null && dictionary.TryGetValue(item2, out var value))
				{
					value.Activate();
				}
				else
				{
					Log.ErrorOnce("Feature not found: " + item2, (item2 ?? "null").GetHashCode());
				}
			}
		});
	}
}
