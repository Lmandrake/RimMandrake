using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Xml;
using Verse;

namespace BigAndSmall;

public class PatchOp_ReplaceText : PatchOperationPathed
{
	private List<string> oldTexts;

	private List<string> newTexts;

	private bool wholeWordsOnly;

	protected override bool ApplyWorker(XmlDocument xml)
	{
		bool result = false;
		XmlNodeList xmlNodeList = xml.SelectNodes(base.xpath);
		if (xmlNodeList == null || xmlNodeList.Count == 0)
		{
			return false;
		}
		for (int i = 0; i < oldTexts.Count; i++)
		{
			string text = oldTexts[i].ToLower();
			string newText = newTexts[i];
			foreach (XmlNode item in xmlNodeList)
			{
				if ((item.NodeType == XmlNodeType.Element || item.NodeType == XmlNodeType.Text) && !string.IsNullOrEmpty(item.InnerText) && item.InnerText.ToLower().Contains(text))
				{
					string pattern = (wholeWordsOnly ? ("\\b" + Regex.Escape(text) + "\\b") : Regex.Escape(text));
					item.InnerText = Regex.Replace(item.InnerText, pattern, (Match matchingV) => char.IsUpper(matchingV.Value[0]) ? (char.ToUpper(newText[0]) + newText.Substring(1)) : newText, RegexOptions.IgnoreCase);
					result = true;
				}
			}
		}
		return result;
	}
}
