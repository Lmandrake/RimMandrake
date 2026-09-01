using System;
using System.Xml;
using RimWorld;
using Verse;

namespace VEF.Factions;

public class StartingGoodwillByFaction
{
	public FactionDef factionDef;

	public IntRange startingGoodwill;

	public int Min => startingGoodwill.min;

	public int Max => startingGoodwill.max;

	public StartingGoodwillByFaction()
	{
	}

	public StartingGoodwillByFaction(FactionDef factionDef, int min, int max)
		: this(factionDef, new IntRange(min, max))
	{
	}//IL_0004: Unknown result type (might be due to invalid IL or missing references)


	public StartingGoodwillByFaction(FactionDef factionDef, IntRange startingGoodwill)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		this.factionDef = factionDef;
		this.startingGoodwill = startingGoodwill;
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		if (xmlRoot.ChildNodes.Count != 1)
		{
			Log.Error("Misconfigured StartingGoodwillByFaction: " + xmlRoot.OuterXml);
			return;
		}
		DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "factionDef", xmlRoot.Name, (string)null, (string)null, (Type)null);
		startingGoodwill = ParseHelper.FromString<IntRange>(xmlRoot.FirstChild.Value);
	}

	public override string ToString()
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		string[] obj = new string[5]
		{
			"(",
			(factionDef != null) ? ((Def)factionDef).defName : "null",
			" with starting goodwill of ",
			null,
			null
		};
		IntRange val = startingGoodwill;
		obj[3] = ((object)(IntRange)(ref val)/*cast due to .constrained prefix*/).ToString();
		obj[4] = ")";
		return string.Concat(obj);
	}
}
