using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class ApparelMatch
{
	public List<string> tags = new List<string>();

	public List<BodyPartGroupDef> bodyParts = new List<BodyPartGroupDef>();

	public List<ApparelLayerDef> apparelLayers = new List<ApparelLayerDef>();

	public bool requireAllParts;

	public bool requireAllLayers;

	public static bool Matches(object apparel, ApparelMatch equipTag)
	{
		if (apparel is IEnumerable<ApparelProperties> apparel2)
		{
			return equipTag.Matches(apparel2);
		}
		return false;
	}

	public bool Matches(IEnumerable<ApparelProperties> apparel)
	{
		if (GenCollection.Any<string>(tags))
		{
			List<ApparelProperties> list = new List<ApparelProperties>();
			list.AddRange(apparel.Where((ApparelProperties x) => GenCollection.Any<string>(x.tags, (Predicate<string>)((string t) => tags.Contains(t)))));
			apparel = new _003C_003Ez__ReadOnlyList<ApparelProperties>(list);
		}
		if (apparelLayers.Count > 0)
		{
			HashSet<ApparelLayerDef> wornLayers = apparel.SelectMany((ApparelProperties x) => x.layers).ToHashSet();
			if (requireAllLayers)
			{
				if (!apparelLayers.All((ApparelLayerDef x) => wornLayers.Contains(x)))
				{
					return false;
				}
			}
			else if (!GenCollection.Any<ApparelLayerDef>(apparelLayers, (Predicate<ApparelLayerDef>)((ApparelLayerDef x) => wornLayers.Contains(x))))
			{
				return false;
			}
		}
		if (bodyParts.Count > 0)
		{
			HashSet<BodyPartGroupDef> wornParts = apparel.SelectMany((ApparelProperties x) => x.bodyPartGroups).ToHashSet();
			if (requireAllParts)
			{
				if (!bodyParts.All((BodyPartGroupDef x) => wornParts.Contains(x)))
				{
					return false;
				}
			}
			else if (!GenCollection.Any<BodyPartGroupDef>(bodyParts, (Predicate<BodyPartGroupDef>)((BodyPartGroupDef x) => wornParts.Contains(x))))
			{
				return false;
			}
		}
		return apparel.Any();
	}
}
