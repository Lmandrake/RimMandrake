using System.Collections.Generic;

namespace BigAndSmall.FilteredLists;

public class Whitelist<T> : FilterList<T>
{
	public override FType FilterType => FType.Whitelist;

	public Whitelist(IEnumerable<T> collection)
		: base(collection)
	{
	}

	public Whitelist()
	{
	}
}
