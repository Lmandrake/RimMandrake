using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class ProductionGeneSettings : DefModExtension
{
	public class SubProductionGeneSettings
	{
		public ThingDef product;

		public int baseAmount = 10;
	}

	public int baseAmount = 10;

	public float frequencyInDays = 1f;

	public string progressName = "NameMissing";

	public ThingDef product;

	public string saveKey = "SaveKeyMissing";

	public List<SubProductionGeneSettings> extra = new List<SubProductionGeneSettings>();
}
