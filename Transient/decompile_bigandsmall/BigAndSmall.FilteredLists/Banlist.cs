using System.Collections.Generic;

namespace BigAndSmall.FilteredLists;

public class Banlist<T> : FilterList<T>
{
	public override FType FilterType => FType.Banlist;

	public Banlist(IEnumerable<T> collection)
		: base(collection)
	{
	}

	public Banlist()
	{
	}
}
