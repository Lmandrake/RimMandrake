using System.Collections.Generic;
using System.Xml;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class ColorOptionList
{
	public List<(float weight, Color color)> colors = new List<(float, Color)>();

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		foreach (XmlNode childNode in xmlRoot.ChildNodes)
		{
			float result = 1f;
			if (childNode.Attributes?["weight"] != null && !float.TryParse(childNode.Attributes["weight"].Value, out result))
			{
				Log.ErrorOnce(string.Format("Failed to parse weight from '{0}' in ColorOptionList on {1}. Defaulting to 1.", childNode.Attributes["weight"].Value, childNode), 8734566);
				result = 1f;
			}
			Color item = ParseHelper.ParseColor(childNode.InnerText);
			colors.Add((result, item));
		}
	}
}
