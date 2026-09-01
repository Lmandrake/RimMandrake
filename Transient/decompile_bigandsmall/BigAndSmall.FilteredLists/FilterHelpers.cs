using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall.FilteredLists;

public static class FilterHelpers
{
	public static FilterResult Max(FilterResult a, FilterResult b)
	{
		if ((int)a <= (int)b)
		{
			return b;
		}
		return a;
	}

	public static FilterResult MaxList(this IEnumerable<FilterResult> results)
	{
		return results.Aggregate(FilterResult.None, Max);
	}

	public static FilterResult Fuse(this FilterResult previous, FilterResult next)
	{
		return Max(previous, next);
	}

	public static FilterResult FuseNoNullCheck(this IEnumerable<FilterResult> results)
	{
		if (results.Any())
		{
			return results.MaxList();
		}
		return FilterResult.None;
	}

	public static FilterResult Fuse(this IEnumerable<FilterResult> results)
	{
		if (!GenCollection.EnumerableNullOrEmpty<FilterResult>(results))
		{
			return results.MaxList();
		}
		return FilterResult.None;
	}

	public static FilterResult Fuse(this FilterResult previous, IEnumerable<FilterResult> next)
	{
		return next.FuseNoNullCheck().Fuse(previous);
	}

	public static FilterResult GetFilterResult<T>(this IEnumerable<FilterList<T>> filterList, T item)
	{
		return filterList.Select((FilterList<T> x) => x.GetFilterResult(item)).FuseNoNullCheck();
	}

	public static IEnumerable<FilterResult> GetFilterResults<T>(this IReadOnlyCollection<FilterList<T>> filterList, T item)
	{
		return filterList.Select((FilterList<T> x) => x.GetFilterResult(item));
	}

	public static FilterResult GetFilterResultFromItemList<T>(this IReadOnlyCollection<FilterList<T>> filterList, IReadOnlyCollection<T> itemList)
	{
		if (itemList.Count == 0 && filterList.Any((FilterList<T> x) => x is Whitelist<T>))
		{
			return FilterResult.Deny;
		}
		return filterList.SelectMany((FilterList<T> x) => itemList.Select((T y) => x.GetFilterResult(y))).FuseNoNullCheck();
	}

	public static FilterResult GetFilterResult<T>(this IReadOnlyCollection<FilterList<T>> filterList, object item, Func<object, T, bool> predicate)
	{
		return filterList.Select((FilterList<T> x) => x.GetFilterResult(item, predicate)).FuseNoNullCheck();
	}

	public static IEnumerable<FilterResult> GetFilterResults<T>(this IReadOnlyCollection<FilterList<T>> filterList, object item, Func<object, T, bool> predicate)
	{
		return filterList.Select((FilterList<T> x) => x.GetFilterResult(item, predicate));
	}

	public static FilterResult GetFilterResultFromItemList<T>(this IReadOnlyCollection<FilterList<T>> filterList, IReadOnlyCollection<object> itemList, Func<object, T, bool> predicate)
	{
		if (itemList.Count == 0 && filterList.Any((FilterList<T> x) => x is Whitelist<T>))
		{
			return FilterResult.Deny;
		}
		return filterList.SelectMany((FilterList<T> x) => itemList.Select((object y) => x.GetFilterResult(y, predicate))).FuseNoNullCheck();
	}

	public static bool Banned(this FilterResult fResult)
	{
		return fResult == FilterResult.Banned;
	}

	public static bool Denied(this FilterResult fResult)
	{
		if (fResult != FilterResult.Deny)
		{
			return fResult == FilterResult.Banned;
		}
		return true;
	}

	public static bool NotExplicitlyAllowed(this FilterResult fResult)
	{
		if (!fResult.Denied() && fResult != FilterResult.Neutral)
		{
			return fResult == FilterResult.None;
		}
		return true;
	}

	public static bool Accepted(this FilterResult fResult)
	{
		return !fResult.Denied();
	}

	public static bool ExplicitlyAllowed(this FilterResult fResult)
	{
		if (fResult != FilterResult.ForceAllow)
		{
			return fResult == FilterResult.Allow;
		}
		return true;
	}

	public static bool ForceAllowed(this FilterResult fResult)
	{
		return fResult == FilterResult.ForceAllow;
	}

	public static bool PriorityResult(this FilterResult fResult)
	{
		if (fResult != FilterResult.Banned)
		{
			return fResult == FilterResult.ForceAllow;
		}
		return true;
	}

	public static FilterListSet<T> MergeFilters<T>(this FilterListSet<T> listOne, FilterListSet<T> listTwo)
	{
		if (listTwo == null)
		{
			return listOne;
		}
		if (listOne == null)
		{
			return listTwo;
		}
		return new FilterListSet<T>
		{
			allowlist = (listOne.allowlist.UnionNullableLists(listTwo.allowlist) as Allowlist<T>),
			whitelist = (listOne.whitelist.UnionNullableLists(listTwo.whitelist) as Whitelist<T>),
			blacklist = (listOne.blacklist.UnionNullableLists(listTwo.blacklist) as Blacklist<T>),
			banlist = (listOne.banlist.UnionNullableLists(listTwo.banlist) as Banlist<T>),
			acceptlist = (listOne.acceptlist.UnionNullableLists(listTwo.acceptlist) as AcceptList<T>)
		};
	}

	public static FilterListSet<T> MergeFilters<T>(this IEnumerable<FilterListSet<T>> lists)
	{
		if (!lists.Any())
		{
			return null;
		}
		return lists.Aggregate((FilterListSet<T> x, FilterListSet<T> y) => x.MergeFilters(y));
	}
}
