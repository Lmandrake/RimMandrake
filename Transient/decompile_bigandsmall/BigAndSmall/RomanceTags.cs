using System.Collections.Generic;
using System.Xml;
using Verse;

namespace BigAndSmall;

public class RomanceTags
{
	public class Compatibility
	{
		public float chance;

		public float factor = 1f;

		public bool exclude;

		public int priority;
	}

	public Dictionary<string, Compatibility> compatibilities = new Dictionary<string, Compatibility>();

	public static HashSet<ThingDef> defaultUsers = new HashSet<ThingDef>();

	public static RomanceTags simpleRaceDefault = new RomanceTags
	{
		compatibilities = new Dictionary<string, Compatibility>
		{
			["Humanlike"] = new Compatibility
			{
				chance = 0.75f,
				factor = 1f
			},
			["Human"] = new Compatibility
			{
				chance = 1f,
				factor = 1f
			}
		}
	};

	public readonly string TAG_IGNORE = "Exclude";

	public readonly string FACTOR = "Factor";

	public readonly string PRIORITY = "Priority";

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		foreach (XmlNode childNode in xmlRoot.ChildNodes)
		{
			Compatibility compatibility = new Compatibility();
			if (childNode.Attributes != null && childNode.Attributes[TAG_IGNORE] != null)
			{
				compatibility.exclude = true;
			}
			if (childNode.Attributes != null && childNode.Attributes[FACTOR] != null)
			{
				compatibility.factor = (float.TryParse(childNode.InnerText, out var result) ? result : 1f);
			}
			else
			{
				compatibility.chance = (float.TryParse(childNode.InnerText, out var result2) ? result2 : 1f);
			}
			compatibilities[childNode.Name] = compatibility;
		}
	}

	public List<string> GetDescriptions()
	{
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		List<string> list = new List<string>();
		foreach (KeyValuePair<string, Compatibility> compatibility in compatibilities)
		{
			string text = ((compatibility.Value.priority != 0) ? TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_Priority", NamedArgument.op_Implicit(compatibility.Value.priority))) : "");
			if (compatibility.Value.exclude)
			{
				list.Add(compatibility.Key.Replace("_", " ") + ": N/A");
			}
			else if (compatibility.Value.factor != 1f)
			{
				list.Add(string.Format("{0}: {1:f1} * {2}", compatibility.Key.Replace("_", " "), compatibility.Value.chance, compatibility.Value.factor));
			}
			else
			{
				list.Add(string.Format("{0}: {1:f0}%", compatibility.Key.Replace("_", " "), compatibility.Value.chance * 100f) + text);
			}
		}
		return list;
	}
}
