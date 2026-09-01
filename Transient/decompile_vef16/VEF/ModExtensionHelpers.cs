using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF;

public static class ModExtensionHelpers
{
	public static List<T> GetModExtensions<T>(this Def def) where T : DefModExtension
	{
		if (GenList.NullOrEmpty<DefModExtension>((IList<DefModExtension>)def.modExtensions))
		{
			return new List<T>();
		}
		return def.modExtensions.OfType<T>().ToList();
	}

	public static bool TryGetModExtensions<T>(this Def def, out List<T> extension) where T : DefModExtension
	{
		if (GenList.NullOrEmpty<DefModExtension>((IList<DefModExtension>)def.modExtensions))
		{
			extension = new List<T>();
			return false;
		}
		extension = def.modExtensions.OfType<T>().ToList();
		return extension.Count > 0;
	}
}
