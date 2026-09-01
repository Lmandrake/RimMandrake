using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public static class RomanceTagsExtensions
{
	public static float? GetHighestSharedTag(BSCache first, BSCache second)
	{
		Dictionary<string, RomanceTags.Compatibility> compatibilities = new Dictionary<string, RomanceTags.Compatibility>();
		if (first?.romanceTags == null || second?.romanceTags == null)
		{
			return null;
		}
		if (first == second)
		{
			Log.ErrorOnce("Debug: Attempted to compare romance tags of the same BSCache instance. This should not happen.", 123456);
			return 0f;
		}
		CheckTags(first.romanceTags, second.romanceTags);
		CheckTags(second.romanceTags, first.romanceTags);
		if (compatibilities.Count == 0)
		{
			return 0f;
		}
		KeyValuePair<string, RomanceTags.Compatibility> keyValuePair = (from x in compatibilities
			where !x.Value.exclude
			orderby x.Value.chance * x.Value.factor descending
			select x).FirstOrDefault();
		return keyValuePair.Value?.chance * keyValuePair.Value?.factor;
		void CheckTags(RomanceTags rOne, RomanceTags rTwo)
		{
			foreach (KeyValuePair<string, RomanceTags.Compatibility> tagOne in rOne.compatibilities.Where((KeyValuePair<string, RomanceTags.Compatibility> x) => !x.Value.exclude))
			{
				foreach (KeyValuePair<string, RomanceTags.Compatibility> item in rTwo.compatibilities.Where((KeyValuePair<string, RomanceTags.Compatibility> x) => x.Key == tagOne.Key && !x.Value.exclude))
				{
					compatibilities[tagOne.Key] = new RomanceTags.Compatibility
					{
						chance = Math.Max(tagOne.Value.chance, item.Value.chance),
						factor = tagOne.Value.factor * item.Value.factor
					};
				}
			}
		}
	}

	public static RomanceTags GetMerged(this IEnumerable<RomanceTags> romanceTags)
	{
		if (romanceTags == null || !romanceTags.Any())
		{
			return null;
		}
		if (romanceTags.Count() == 1)
		{
			return romanceTags.First();
		}
		RomanceTags romanceTags2 = new RomanceTags
		{
			compatibilities = new Dictionary<string, RomanceTags.Compatibility>()
		};
		foreach (IGrouping<string, KeyValuePair<string, RomanceTags.Compatibility>> item in from x in romanceTags.SelectMany((RomanceTags rt) => rt.compatibilities)
			group x by x.Key)
		{
			string key = item.Key;
			int highestPrio = item.Max((KeyValuePair<string, RomanceTags.Compatibility> c) => c.Value.priority);
			float chance = item.Where((KeyValuePair<string, RomanceTags.Compatibility> x) => x.Value.priority == highestPrio).Max((KeyValuePair<string, RomanceTags.Compatibility> c) => c.Value.chance);
			float factor = item.Where((KeyValuePair<string, RomanceTags.Compatibility> x) => x.Value.priority == highestPrio).Aggregate(1f, (float acc, KeyValuePair<string, RomanceTags.Compatibility> c) => acc * c.Value.factor);
			romanceTags2.compatibilities[key] = new RomanceTags.Compatibility
			{
				chance = chance,
				factor = factor,
				exclude = item.Any((KeyValuePair<string, RomanceTags.Compatibility> c) => c.Value.exclude)
			};
		}
		GenCollection.RemoveAll<string, RomanceTags.Compatibility>(romanceTags2.compatibilities, (Predicate<KeyValuePair<string, RomanceTags.Compatibility>>)((KeyValuePair<string, RomanceTags.Compatibility> x) => x.Value.exclude));
		return romanceTags2;
	}
}
