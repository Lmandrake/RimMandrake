using Verse;

namespace BigAndSmall;

public static class HotReloadExtension
{
	public static T TryGetExistingDef<T>(this string defName) where T : Def
	{
		return DefDatabase<T>.GetNamed(defName, false);
	}
}
