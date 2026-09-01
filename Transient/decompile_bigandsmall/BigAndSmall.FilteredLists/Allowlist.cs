using System.Collections.Generic;

namespace BigAndSmall.FilteredLists;

public class Allowlist<T> : FilterList<T>
{
	public override FType FilterType => FType.Allowlist;

	public Allowlist(IEnumerable<T> collection)
		: base(collection)
	{
	}

	public Allowlist()
	{
	}
}
