using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Xml;
using Verse;

namespace BigAndSmall;

public class FlagString : IExposable, IEquatable<FlagString>
{
	private const string DEFAULT = "default";

	public string mainTag;

	public string subTag = "default";

	public string label;

	public Dictionary<string, string> extraData = new Dictionary<string, string>();

	[CompilerGenerated]
	private FlagStringStateData _003CData_003Ek__BackingField;

	[CompilerGenerated]
	private string _003CLabel_003Ek__BackingField;

	[CompilerGenerated]
	private EditPawnWindow.WindowTab? _003CDisplayTab_003Ek__BackingField;

	[CompilerGenerated]
	private string _003CCustomCategory_003Ek__BackingField;

	public FlagStringStateData Data
	{
		get
		{
			return _003CData_003Ek__BackingField ?? (_003CData_003Ek__BackingField = FlagStringData.DataFor(this));
		}
		set
		{
			_003CData_003Ek__BackingField = value;
		}
	}

	public string Label
	{
		get
		{
			string text = _003CLabel_003Ek__BackingField;
			if (text == null)
			{
				string obj = label ?? Data?.label ?? ToStringShort();
				string text2 = obj;
				_003CLabel_003Ek__BackingField = obj;
				text = text2;
			}
			return text;
		}
		set
		{
			_003CLabel_003Ek__BackingField = value;
		}
	}

	public EditPawnWindow.WindowTab? DisplayTab
	{
		get
		{
			return _003CDisplayTab_003Ek__BackingField ?? (_003CDisplayTab_003Ek__BackingField = Data?.displayTab);
		}
		set
		{
			_003CDisplayTab_003Ek__BackingField = value;
		}
	}

	public string CustomCategory
	{
		get
		{
			return _003CCustomCategory_003Ek__BackingField ?? (_003CCustomCategory_003Ek__BackingField = Data?.customCategory);
		}
		set
		{
			_003CCustomCategory_003Ek__BackingField = value;
		}
	}

	public bool Equals(FlagString other)
	{
		if ((object)this != null && mainTag != null && (object)other != null && other.mainTag != null && mainTag == other.mainTag)
		{
			return subTag == other.subTag;
		}
		return false;
	}

	public override bool Equals(object obj)
	{
		if (obj is FlagString flagString)
		{
			if (mainTag == flagString.mainTag && subTag == flagString.subTag && extraData.Count == flagString.extraData.Count)
			{
				if (extraData.Count != 0)
				{
					return !extraData.Except(flagString.extraData).Any();
				}
				return true;
			}
			return false;
		}
		return false;
	}

	public static bool operator ==(FlagString left, FlagString right)
	{
		return left?.Equals(right) ?? ((object)right == null);
	}

	public static bool operator !=(FlagString left, FlagString right)
	{
		return !(left == right);
	}

	public bool MainTagEquals(FlagString other)
	{
		if ((object)this != null && mainTag != null && (object)other != null && other.mainTag != null)
		{
			return mainTag == other.mainTag;
		}
		return false;
	}

	public FlagString()
	{
	}

	public FlagString(string mainTag, string subTag = null, Dictionary<string, string> extraData = null, string label = null)
	{
		this.mainTag = mainTag;
		this.subTag = subTag ?? "default";
		this.extraData = extraData ?? new Dictionary<string, string>();
		this.label = label;
	}

	/// <summary>
	/// If the mainTag and subTag are identical, merges the extraData dictionaries, preferring this.extraData on key conflicts.
	/// </summary>
	public FlagString TryFuseIdentical(FlagString other)
	{
		if (other != this)
		{
			return null;
		}
		Dictionary<string, string> dictionary = new Dictionary<string, string>(extraData);
		foreach (KeyValuePair<string, string> extraDatum in other.extraData)
		{
			if (!dictionary.ContainsKey(extraDatum.Key))
			{
				dictionary[extraDatum.Key] = extraDatum.Value;
			}
		}
		return new FlagString
		{
			mainTag = mainTag,
			subTag = subTag,
			extraData = dictionary
		};
	}

	public void ClearCache()
	{
		Label = null;
		DisplayTab = null;
		CustomCategory = null;
		Data = null;
	}

	public override int GetHashCode()
	{
		return (17 * 23 + (mainTag?.GetHashCode() ?? 0)) * 23 + (subTag?.GetHashCode() ?? 0);
	}

	public override string ToString()
	{
		return mainTag + "/" + subTag + (extraData.Any() ? ("[" + string.Join(",", extraData) + "]") : "");
	}

	public string ToStringShort()
	{
		if (!(subTag == "default"))
		{
			return mainTag + ", " + subTag;
		}
		return mainTag;
	}

	public void LoadDataFromXML(XmlNode node)
	{
		extraData = node.Attributes?.OfType<XmlAttribute>().ToDictionary((XmlAttribute attr) => attr.Name, (XmlAttribute attr) => attr.Value) ?? new Dictionary<string, string>();
		if (extraData.ContainsKey("Label"))
		{
			label = extraData["Label"];
			extraData.Remove("Label");
		}
		if (node.Name == "li")
		{
			SetupSimple(node);
			return;
		}
		if (node.NodeType == XmlNodeType.Text && node.InnerText == null)
		{
			SetupSimple(node);
			return;
		}
		mainTag = node.Name;
		if (node.InnerText != "")
		{
			subTag = node.InnerText;
		}
		void SetupSimple(XmlNode node)
		{
			mainTag = node.InnerText;
			subTag = "default";
		}
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		XmlNode firstChild = xmlRoot.FirstChild;
		LoadDataFromXML(firstChild);
	}

	public FlagString Clone(Dictionary<string, string> appendData = null)
	{
		FlagString flagString = new FlagString
		{
			mainTag = mainTag,
			subTag = subTag,
			label = label,
			extraData = new Dictionary<string, string>(extraData)
		};
		if (appendData != null)
		{
			foreach (KeyValuePair<string, string> appendDatum in appendData)
			{
				flagString.extraData[appendDatum.Key] = appendDatum.Value;
			}
		}
		return flagString;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref mainTag, "mainTag", (string)null, false);
		Scribe_Values.Look<string>(ref subTag, "subTag", "default", false);
		Scribe_Collections.Look<string, string>(ref extraData, "extraData", (LookMode)1, (LookMode)1);
	}
}
