using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public static class DefUtils
{
	public static Texture2D TryGetIcon(Def def, out Color color)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		while (true)
		{
			color = Color.white;
			if (def == null)
			{
				return null;
			}
			PawnKindDef val = (PawnKindDef)(object)((def is PawnKindDef) ? def : null);
			if (val == null)
			{
				ThingDef val2 = (ThingDef)(object)((def is ThingDef) ? def : null);
				if (val2 == null)
				{
					FactionDef val3 = (FactionDef)(object)((def is FactionDef) ? def : null);
					if (val3 == null)
					{
						break;
					}
					if (!GenList.NullOrEmpty<Color>((IList<Color>)val3.colorSpectrum))
					{
						color = val3.colorSpectrum.FirstOrDefault();
					}
					return val3.FactionIcon;
				}
				if (!((Def)val2).defName.StartsWith("Corpse_"))
				{
					ThingDef val4 = GenStuff.DefaultStuffFor((BuildableDef)(object)val2);
					color = ((val4 == null) ? ((BuildableDef)val2).uiIconColor : ((BuildableDef)val2).GetColorForStuff(val4));
					return Widgets.GetIconFor(val2, val4, (ThingStyleDef)null, (int?)null);
				}
				def = (Def)(object)DefDatabase<ThingDef>.GetNamed(((Def)val2).defName.Substring(7), false);
			}
			else
			{
				def = (Def)(object)val.race;
			}
		}
		return null;
	}

	public static string BuildApparelTooltip(ThingDef def)
	{
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		if (def?.apparel == null)
		{
			return ((Def)(def?)).description;
		}
		StringBuilder stringBuilder = new StringBuilder();
		List<ApparelLayerDef> layers = def.apparel.layers;
		TaggedString val;
		if (layers != null && layers.Count > 0)
		{
			string text = string.Join(", ", def.apparel.layers.Select(delegate(ApparelLayerDef l)
			{
				//IL_0001: Unknown result type (might be due to invalid IL or missing references)
				//IL_001a: Unknown result type (might be due to invalid IL or missing references)
				//IL_001f: Unknown result type (might be due to invalid IL or missing references)
				if (string.IsNullOrEmpty(TaggedString.op_Implicit(((Def)l).LabelCap)))
				{
					return ((Def)l).defName;
				}
				TaggedString labelCap = ((Def)l).LabelCap;
				return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString();
			}));
			val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Apparel_Layers", NamedArgument.op_Implicit(text));
			stringBuilder.AppendLine(((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString());
		}
		List<BodyPartGroupDef> bodyPartGroups = def.apparel.bodyPartGroups;
		if (bodyPartGroups != null && bodyPartGroups.Count > 0)
		{
			string text2 = string.Join(", ", def.apparel.bodyPartGroups.Select(delegate(BodyPartGroupDef b)
			{
				//IL_0001: Unknown result type (might be due to invalid IL or missing references)
				//IL_001a: Unknown result type (might be due to invalid IL or missing references)
				//IL_001f: Unknown result type (might be due to invalid IL or missing references)
				if (string.IsNullOrEmpty(TaggedString.op_Implicit(((Def)b).LabelCap)))
				{
					return ((Def)b).defName;
				}
				TaggedString labelCap2 = ((Def)b).LabelCap;
				return ((object)(TaggedString)(ref labelCap2)/*cast due to .constrained prefix*/).ToString();
			}));
			val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Apparel_Coverage", NamedArgument.op_Implicit(text2));
			stringBuilder.AppendLine(((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString());
		}
		if (!string.IsNullOrEmpty(((Def)def).description))
		{
			if (stringBuilder.Length > 0)
			{
				stringBuilder.AppendLine();
			}
			stringBuilder.Append(((Def)def).description);
		}
		if (stringBuilder.Length <= 0)
		{
			return null;
		}
		return stringBuilder.ToString().TrimEnd();
	}
}
