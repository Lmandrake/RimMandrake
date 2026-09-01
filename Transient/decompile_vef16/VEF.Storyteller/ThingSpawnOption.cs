using System;
using System.Xml;
using Verse;

namespace VEF.Storyteller;

public class ThingSpawnOption
{
	public ThingDef thing;

	public IntRange count;

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		DirectXmlCrossRefLoader.RegisterObjectWantsCrossRef((object)this, "thing", xmlRoot.Name, (string)null, (string)null, (Type)null);
		count = (IntRange)((xmlRoot.FirstChild != null) ? ParseHelper.FromString<IntRange>(xmlRoot.FirstChild.Value) : new IntRange(1, 1));
	}
}
