using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public class CompProperties_Shield : CompProperties
{
	public List<string> shieldTags;

	public bool useDeflectMetalEffect;

	public List<BodyPartGroupDef> coveredBodyPartGroups;

	public GraphicData offHandGraphicData;

	public HoldOffsetSet offHandHoldOffset;

	public CompProperties_Shield()
	{
		base.compClass = typeof(CompShield);
	}

	public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
	{
		if (GenList.NullOrEmpty<BodyPartGroupDef>((IList<BodyPartGroupDef>)coveredBodyPartGroups))
		{
			yield return "coveredBodyPartGroups is not defined or is empty.";
		}
	}

	public override IEnumerable<StatDrawEntry> SpecialDisplayStats(StatRequest req)
	{
		string text = GenText.CapitalizeFirst(GenText.ToCommaList(coveredBodyPartGroups.Select((BodyPartGroupDef p) => ((Def)p).label), true, false));
		yield return new StatDrawEntry(StatCategoryDefOf.Apparel, TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.Protects")), text, string.Empty, 100, (string)null, (IEnumerable<Hyperlink>)null, false, false);
	}
}
