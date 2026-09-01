using System.Collections.Generic;
using System.Xml;

namespace BigAndSmall;

public class FlagStringList : HashSet<FlagString>
{
	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		foreach (XmlNode childNode in xmlRoot.ChildNodes)
		{
			FlagString flagString = new FlagString();
			flagString.LoadDataFromXML(childNode);
			Add(flagString);
		}
	}
}
