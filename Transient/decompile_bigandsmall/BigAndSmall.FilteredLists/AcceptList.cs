using System.Collections.Generic;

namespace BigAndSmall.FilteredLists;

public class AcceptList<T> : FilterList<T>
{
	public override FType FilterType => FType.Acceptlist;

	public AcceptList(IEnumerable<T> collection)
		: base(collection)
	{
	}

	public AcceptList()
	{
	}
}
