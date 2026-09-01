using System;
using System.Collections.Generic;
using System.Xml;
using Verse;

namespace VEF.Graphics;

public abstract class TaggedItem<T> : IExposable, IEquatable<TaggedItem<T>>, ITaggedItem
{
	public string tag;

	public T value;

	public string Tag => tag;

	public TaggedItem()
	{
	}

	public TaggedItem(string tag, T value)
	{
		this.tag = tag;
		this.value = value;
	}

	public bool Equals(TaggedItem<T> other)
	{
		if (tag == other.tag)
		{
			return EqualityComparer<T>.Default.Equals(value, other.value);
		}
		return false;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref tag, "tag", (string)null, false);
		Scribe_Values.Look<T>(ref value, "value", default(T), false);
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		tag = xmlRoot.Name;
		value = ParseHelper.FromString<T>(xmlRoot.InnerText);
	}

	public string GetUniqueLoadID()
	{
		return tag + value.GetHashCode();
	}

	public override string ToString()
	{
		return $"TaggedItem<{typeof(T)}> {tag}: {value}";
	}
}
