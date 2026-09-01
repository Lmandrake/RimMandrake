using System.Collections.Generic;

namespace BigAndSmall.FilteredLists;

public class Blacklist<T> : FilterList<T>
{
	public override FType FilterType => FType.Blacklist;

	public Blacklist(IEnumerable<T> collection)
		: base(collection)
	{
	}

	public Blacklist()
	{
	}
}
