using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace FactionLoadout;

public static class ReplaceUtils
{
	public static void ReplaceMaybe<T>(ref T field, T maybe) where T : class
	{
		if (maybe != null)
		{
			field = maybe;
		}
	}

	public static void ReplaceMaybe<T>(ref T field, T? maybe) where T : struct
	{
		if (maybe.HasValue)
		{
			field = maybe.Value;
		}
	}

	public static void ReplaceMaybe<T>(ref T? field, T? maybe) where T : struct
	{
		if (maybe.HasValue)
		{
			field = maybe.Value;
		}
	}

	public static void ReplaceMaybe(ref PawnInventoryOption inv, InventoryOptionEdit maybe, PawnKindEdit edit, PawnKindEdit global)
	{
		if (maybe == null)
		{
			return;
		}
		if (global?.Inventory != null || (edit.IsGlobal && !edit.ReplaceDefaultInventory))
		{
			if (inv == null)
			{
				inv = maybe.ConvertToVanilla();
				return;
			}
			PawnInventoryOption val = maybe.ConvertToVanilla();
			if (val.subOptionsTakeAll != null)
			{
				inv.subOptionsTakeAll.AddRange(val.subOptionsTakeAll);
			}
			if (val.subOptionsChooseOne != null)
			{
				inv.subOptionsChooseOne.AddRange(val.subOptionsChooseOne);
			}
		}
		else
		{
			inv = maybe.ConvertToVanilla();
		}
	}

	public static void ReplaceMaybeList<T>(ref T field, T maybe, bool tryAdd) where T : IList, new()
	{
		if (maybe == null)
		{
			return;
		}
		if (tryAdd && field != null)
		{
			foreach (object item in maybe)
			{
				if (!field.Contains(item))
				{
					field.Add(item);
				}
			}
			return;
		}
		field = new T();
		foreach (object item2 in maybe)
		{
			field.Add(item2);
		}
	}

	public static void ReplaceMaybeDefRefList<T>(ref List<T> field, List<DefRef<T>> maybe, bool tryAdd) where T : Def, new()
	{
		if (maybe == null)
		{
			return;
		}
		List<T> list = (from r in maybe
			where r.HasValue
			select r.Def).ToList();
		if (tryAdd && field != null)
		{
			foreach (T item in list)
			{
				if (!field.Contains(item))
				{
					field.Add(item);
				}
			}
			return;
		}
		field = list;
	}
}
