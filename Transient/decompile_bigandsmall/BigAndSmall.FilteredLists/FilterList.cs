using System;
using System.Collections.Generic;
using System.Xml;
using Verse;

namespace BigAndSmall.FilteredLists;

public abstract class FilterList<T> : List<T>
{
	public abstract FType FilterType { get; }

	public FilterList(IEnumerable<T> collection)
		: base(collection)
	{
	}

	public FilterList()
	{
	}

	public override string ToString()
	{
		return $"{base.ToString()}_{FilterType}_count:{base.Count}";
	}

	private bool Match(object a, object b)
	{
		if (a == b)
		{
			return true;
		}
		if (a is Def && b is Def)
		{
			return a == b;
		}
		if (a is string text && b is string text2)
		{
			return text.ToLower() == text2.ToLower();
		}
		Def val = (Def)((a is Def) ? a : null);
		string a2 = ((val != null) ? val.defName : a.ToString());
		Def val2 = (Def)((b is Def) ? b : null);
		string b2 = ((val2 != null) ? val2.defName : b.ToString());
		return string.Equals(a2, b2, StringComparison.OrdinalIgnoreCase);
	}

	public FilterResult GetFilterResult(T item)
	{
		return FilterType switch
		{
			FType.Allowlist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => Match(item, t)))) ? FilterResult.Neutral : FilterResult.ForceAllow, 
			FType.Whitelist => GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => Match(item, t))) ? FilterResult.Allow : FilterResult.Deny, 
			FType.Acceptlist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => Match(item, t)))) ? FilterResult.Neutral : FilterResult.Allow, 
			FType.Blacklist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => Match(item, t)))) ? FilterResult.Neutral : FilterResult.Deny, 
			FType.Banlist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => Match(item, t)))) ? FilterResult.Neutral : FilterResult.Banned, 
			_ => throw new NotImplementedException($"No filter behaviour for type {FilterType}"), 
		};
	}

	public FilterResult GetFilterResult(object item, Func<object, T, bool> predicate)
	{
		return FilterType switch
		{
			FType.Allowlist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => predicate(item, t)))) ? FilterResult.Neutral : FilterResult.ForceAllow, 
			FType.Whitelist => GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => predicate(item, t))) ? FilterResult.Allow : FilterResult.Deny, 
			FType.Acceptlist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => predicate(item, t)))) ? FilterResult.Neutral : FilterResult.Allow, 
			FType.Blacklist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => predicate(item, t)))) ? FilterResult.Neutral : FilterResult.Deny, 
			FType.Banlist => (!GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => predicate(item, t)))) ? FilterResult.Neutral : FilterResult.Banned, 
			_ => throw new NotImplementedException($"No filter behaviour for type {FilterType}"), 
		};
	}

	public bool AnyMatch(T item)
	{
		return GenCollection.Any<T>((List<T>)this, (Predicate<T>)((T t) => Match(item, t)));
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		foreach (XmlNode childNode in xmlRoot.ChildNodes)
		{
			LoadSingleXmlNode(childNode);
		}
	}

	public void LoadSingleXmlNode(XmlNode cNode)
	{
		if (typeof(T) == typeof(FlagString))
		{
			FlagString flagString = new FlagString();
			flagString.LoadDataFromXML(cNode);
			Add((T)(object)flagString);
		}
		else if (typeof(T) == typeof(string))
		{
			Add((T)(object)cNode.FirstChild.Value);
		}
		else
		{
			string value = cNode.FirstChild.Value;
			string text = cNode.Attributes?["MayRequire"]?.Value;
			DirectXmlCrossRefLoader.RegisterListWantsCrossRef<T>((List<T>)this, value, (object)null, text, (string)null);
		}
	}
}
