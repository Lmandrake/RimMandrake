using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class GeneCache
{
	public static Dictionary<Gene, GeneCache> globalCache = new Dictionary<Gene, GeneCache>();

	public bool initialized;

	public bool isOverriden;

	public string disabledMessage;

	public Gene gene;

	private static Gene dummyGene = null;

	public static Gene DummyGene => dummyGene ?? (dummyGene = MakeDummyGene());

	public static void ClearCaches()
	{
		globalCache.Clear();
	}

	public static Gene MakeDummyGene()
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Expected O, but got Unknown
		if (dummyGene == null)
		{
			dummyGene = new Gene
			{
				def = BSDefs.BS_OverrideDummyGene
			};
		}
		return dummyGene;
	}

	public GeneCache(Gene gene)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		TaggedString val = Translator.Translate("BS_RequirementNotMet");
		disabledMessage = TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
		base._002Ector();
		MakeDummyGene();
		this.gene = gene;
	}

	public Gene OverridenBy()
	{
		if (isOverriden)
		{
			return dummyGene;
		}
		return null;
	}
}
