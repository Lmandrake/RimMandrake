namespace BigAndSmall.FilteredLists;

public enum FilterResult : byte
{
	None,
	Neutral,
	Allow,
	Deny,
	ForceAllow,
	Banned
}
