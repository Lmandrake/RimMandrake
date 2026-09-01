using System;
using System.Collections.Generic;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class BackstoryFilter : BackstoryCategoryFilter, IExposable, IDeepCopyable<BackstoryFilter>
{
	public string Summary
	{
		get
		{
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0051: Unknown result type (might be due to invalid IL or missing references)
			//IL_0073: Unknown result type (might be due to invalid IL or missing references)
			//IL_0088: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
			List<string> list = new List<string>();
			if (!GenList.NullOrEmpty<string>((IList<string>)base.categories))
			{
				list.Add(string.Join(", ", base.categories));
			}
			if (!GenList.NullOrEmpty<string>((IList<string>)base.categoriesChildhood))
			{
				list.Add(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_ChildPrefix") + string.Join(", ", base.categoriesChildhood)));
			}
			if (!GenList.NullOrEmpty<string>((IList<string>)base.categoriesAdulthood))
			{
				list.Add(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_AdultPrefix") + string.Join(", ", base.categoriesAdulthood)));
			}
			if (list.Count == 0)
			{
				return string.Format("<i>{0}</i>", Translator.Translate("FactionLoadout_Backstory_EmptyFilter"));
			}
			string text = string.Join(" | ", list);
			if (!Mathf.Approximately(base.commonality, 1f))
			{
				text += $" (x{base.commonality:F1})";
			}
			return text;
		}
	}

	public BackstoryFilter()
	{
	}

	public BackstoryFilter DeepClone()
	{
		return new BackstoryFilter((BackstoryCategoryFilter)(object)this);
	}

	public BackstoryFilter(BackstoryCategoryFilter source)
	{
		if (source != null)
		{
			List<string> categories = source.categories;
			base.categories = ((categories != null) ? GenList.ListFullCopy<string>(categories) : null);
			List<string> exclude = source.exclude;
			base.exclude = ((exclude != null) ? GenList.ListFullCopy<string>(exclude) : null);
			List<string> categoriesChildhood = source.categoriesChildhood;
			base.categoriesChildhood = ((categoriesChildhood != null) ? GenList.ListFullCopy<string>(categoriesChildhood) : null);
			List<string> excludeChildhood = source.excludeChildhood;
			base.excludeChildhood = ((excludeChildhood != null) ? GenList.ListFullCopy<string>(excludeChildhood) : null);
			List<string> categoriesAdulthood = source.categoriesAdulthood;
			base.categoriesAdulthood = ((categoriesAdulthood != null) ? GenList.ListFullCopy<string>(categoriesAdulthood) : null);
			List<string> excludeAdulthood = source.excludeAdulthood;
			base.excludeAdulthood = ((excludeAdulthood != null) ? GenList.ListFullCopy<string>(excludeAdulthood) : null);
			base.commonality = source.commonality;
		}
	}

	public void ExposeData()
	{
		Scribe_Collections.Look<string>(ref base.categories, "categories", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref base.exclude, "exclude", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref base.categoriesChildhood, "categoriesChildhood", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref base.excludeChildhood, "excludeChildhood", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref base.categoriesAdulthood, "categoriesAdulthood", (LookMode)0, Array.Empty<object>());
		Scribe_Collections.Look<string>(ref base.excludeAdulthood, "excludeAdulthood", (LookMode)0, Array.Empty<object>());
		Scribe_Values.Look<float>(ref base.commonality, "commonality", 1f, false);
	}
}
