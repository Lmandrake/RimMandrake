using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class ProductionHediffSettings : HediffCompProperties
{
	public class ProductionSettings
	{
		public ThingDef product;

		public List<ThingDef> randomProduct = new List<ThingDef>();

		public int baseAmount = 10;

		public string ProductTooltip()
		{
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			if (!GenCollection.Any<ThingDef>(randomProduct))
			{
				ThingDef obj = product;
				return TaggedString.op_Implicit((obj != null) ? ((Def)obj).LabelCap : TaggedString.op_Implicit("ProductLabelMissing"));
			}
			return string.Join(", ", randomProduct.Select((ThingDef rp) => ((Def)rp).LabelCap));
		}
	}

	public float frequencyInDays = 1f;

	public string progressName = "NameMissing";

	public string saveKey = "SaveKeyMissing";

	public int activationAge = 13;

	public bool femaleOnly;

	public float chance = 1f;

	public List<ProductionSettings> products = new List<ProductionSettings>();

	public ProductionHediffSettings()
	{
		base.compClass = typeof(ProductionHediff);
	}

	public Type NextFromThis()
	{
		Type result = null;
		if (base.compClass == typeof(ProductionHediff))
		{
			result = typeof(ProductionHediff_1);
		}
		else if (base.compClass == typeof(ProductionHediff_1))
		{
			result = typeof(ProductionHediff_2);
		}
		else if (base.compClass == typeof(ProductionHediff_2))
		{
			result = typeof(ProductionHediff_3);
		}
		else if (base.compClass == typeof(ProductionHediff_3))
		{
			result = typeof(ProductionHediff_4);
		}
		else if (base.compClass == typeof(ProductionHediff_4))
		{
			result = typeof(ProductionHediff_5);
		}
		else if (base.compClass == typeof(ProductionHediff_5))
		{
			result = typeof(ProductionHediff_6);
		}
		else if (base.compClass == typeof(ProductionHediff_6))
		{
			result = typeof(ProductionHediff_7);
		}
		else if (base.compClass == typeof(ProductionHediff_7))
		{
			result = typeof(ProductionHediff_8);
		}
		else if (base.compClass == typeof(ProductionHediff_8))
		{
			result = null;
		}
		return result;
	}
}
