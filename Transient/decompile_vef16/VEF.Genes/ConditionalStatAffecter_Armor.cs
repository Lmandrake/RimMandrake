using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Genes;

public class ConditionalStatAffecter_Armor : ConditionalStatAffecter
{
	public override string Label => TaggedString.op_Implicit(Translator.Translate("VGE_StatsReport_Armoured"));

	public override bool Applies(StatRequest req)
	{
		if (!ModsConfig.BiotechActive)
		{
			return false;
		}
		bool flag = false;
		Pawn val;
		if (((StatRequest)(ref req)).HasThing && (val = (Pawn)/*isinst with value type is only supported in some contexts*/) != null && val.apparel != null)
		{
			List<Apparel> wornApparel = val.apparel.WornApparel;
			for (int num = 0; num < wornApparel.Count; num++)
			{
				ThingDef stuff = ((Thing)wornApparel[num]).Stuff;
				if (stuff == null || stuff.stuffProps?.categories?.Contains(StuffCategoryDefOf.Metallic) != true)
				{
					ThingDef def = ((Thing)wornApparel[num]).def;
					if (def == null || def.thingCategories?.Contains(ThingCategoryDefOf.ApparelArmor) != true)
					{
						goto IL_00e3;
					}
				}
				flag = true;
				goto IL_00e3;
				IL_00e3:
				if (((Thing)wornApparel[num]).def?.thingSetMakerTags?.Contains("Warcasket") == true)
				{
					flag = true;
				}
			}
			if (flag)
			{
				return true;
			}
		}
		return false;
	}
}
