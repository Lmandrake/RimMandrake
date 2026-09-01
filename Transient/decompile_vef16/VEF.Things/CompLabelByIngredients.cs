using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Things;

internal class CompLabelByIngredients : ThingComp
{
	private CompIngredients ingredients;

	private string cachedLabel = "";

	public CompProperties_LabelByIngredients Props => (CompProperties_LabelByIngredients)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		if (ingredients == null)
		{
			ingredients = ThingCompUtility.TryGetComp<CompIngredients>((Thing)(object)base.parent);
		}
	}

	public override string TransformLabel(string label)
	{
		//IL_014a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0111: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		if (cachedLabel == "" && ingredients != null && !GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)ingredients.ingredients))
		{
			if (!GenDictionary.NullOrEmpty<ThingDef, string>(Props.overrides))
			{
				List<ThingDef> list = ingredients.ingredients.Where(delegate(ThingDef x)
				{
					List<ThingDef> exclusions = Props.exclusions;
					return exclusions == null || !exclusions.Contains(x);
				}).ToList();
				if (list.Count > 0)
				{
					ThingDef val = list.First();
					if (val != null && Props.overrides.ContainsKey(val))
					{
						if (Props.fullReplace)
						{
							cachedLabel = Props.overrides[val];
						}
						else
						{
							cachedLabel = Props.overrides[val] + " " + label;
						}
					}
					else
					{
						cachedLabel = TaggedString.op_Implicit(((Def)ingredients.ingredients.Where(delegate(ThingDef x)
						{
							List<ThingDef> exclusions2 = Props.exclusions;
							return exclusions2 == null || !exclusions2.Contains(x);
						}).First()).LabelCap + " " + label);
					}
				}
			}
			else
			{
				cachedLabel = TaggedString.op_Implicit(((Def)ingredients.ingredients.Where(delegate(ThingDef x)
				{
					List<ThingDef> exclusions3 = Props.exclusions;
					return exclusions3 == null || !exclusions3.Contains(x);
				}).First()).LabelCap + " " + label);
			}
		}
		if (!(cachedLabel == ""))
		{
			return cachedLabel;
		}
		return label;
	}
}
