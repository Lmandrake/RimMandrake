using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using Verse;

namespace BigAndSmall.FilteredLists;

public class FilterListSet<T>
{
	public Allowlist<T> allowlist;

	public Whitelist<T> whitelist;

	public AcceptList<T> acceptlist;

	public Blacklist<T> blacklist;

	public Banlist<T> banlist;

	public bool requireExplicitPermission;

	protected List<FilterList<T>> items;

	public List<FilterList<T>> Items => items ?? (items = new List<FilterList<T>> { allowlist, whitelist, blacklist, banlist, acceptlist }.Where((FilterList<T> x) => x != null).ToList());

	public List<T> ExplicitlyAcceptedItems
	{
		get
		{
			if (_003CExplicitlyAcceptedItems_003Ek__BackingField != null)
			{
				return _003CExplicitlyAcceptedItems_003Ek__BackingField;
			}
			return _003CExplicitlyAcceptedItems_003Ek__BackingField = Items.Where((FilterList<T> x) => x.FilterType == FType.Acceptlist || x.FilterType == FType.Allowlist || x.FilterType == FType.Whitelist).SelectMany((FilterList<T> x) => x).Distinct()
				.ToList();
		}
	}

	public bool IsEmpty()
	{
		return !GenCollection.Any<FilterList<T>>(Items);
	}

	public bool AnyItems()
	{
		return GenCollection.Any<FilterList<T>>(Items);
	}

	public IEnumerable<FilterResult> GetFilterResults(T item)
	{
		return Items.GetFilterResults(item);
	}

	public FilterResult GetFilterResult(T item)
	{
		return Items.GetFilterResult(item);
	}

	public FilterResult GetFilterResult(object item, Func<object, T, bool> predicate)
	{
		return Items.GetFilterResult(item, predicate);
	}

	public FilterResult GetFilterResultFromItemList(List<T> itemList)
	{
		return Items.GetFilterResultFromItemList(itemList);
	}

	public FilterResult GetFilterResultFromItemList(IReadOnlyCollection<object> itemList, Func<object, T, bool> predicate)
	{
		return Items.GetFilterResultFromItemList(itemList, predicate);
	}

	public List<T> GetAllItemsInAnyFilter()
	{
		return Items.SelectMany((FilterList<T> x) => x).ToList();
	}

	public bool AnyContains(T obj)
	{
		return GenCollection.Any<FilterList<T>>(Items, (Predicate<FilterList<T>>)((FilterList<T> x) => x.AnyMatch(obj)));
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		List<XmlNode> list = new List<XmlNode>();
		foreach (XmlNode childNode in xmlRoot.ChildNodes)
		{
			switch (childNode.Name.ToLower())
			{
			case "allowlist":
				allowlist = new Allowlist<T>();
				allowlist.LoadDataFromXmlCustom(childNode);
				break;
			case "whitelist":
				whitelist = new Whitelist<T>();
				whitelist.LoadDataFromXmlCustom(childNode);
				break;
			case "blacklist":
				blacklist = new Blacklist<T>();
				blacklist.LoadDataFromXmlCustom(childNode);
				break;
			case "banlist":
				banlist = new Banlist<T>();
				banlist.LoadDataFromXmlCustom(childNode);
				break;
			case "acceptlist":
				acceptlist = new AcceptList<T>();
				acceptlist.LoadDataFromXmlCustom(childNode);
				break;
			case "requireexplicitpermission":
			{
				if (bool.TryParse(childNode.InnerText, out var result))
				{
					requireExplicitPermission = result;
				}
				break;
			}
			default:
				list.Add(childNode);
				break;
			}
		}
		foreach (XmlNode item in list)
		{
			if (blacklist == null)
			{
				blacklist = new Blacklist<T>();
			}
			blacklist.LoadSingleXmlNode(item);
		}
	}
}
