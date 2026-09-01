using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CustomizableGraphic : IExposable
{
	public class SubItemGraphic : IExposable
	{
		public FlagString flagString;

		public Color? colorA;

		public Color? colorB;

		public Color? colorC;

		public Dictionary<string, List<string>> triggers = new Dictionary<string, List<string>>();

		public override string ToString()
		{
			return string.Format("[{0}] - Def: {1}, ColorA: {2}, ColorB: {3}, ColorC: {4}", "SubItemGraphic", flagString, colorA, colorB, colorC);
		}

		public void ExposeData()
		{
			Scribe_Deep.Look<FlagString>(ref flagString, "flagString", Array.Empty<object>());
			Scribe_Values.Look<Color?>(ref colorA, "colorA", (Color?)null, false);
			Scribe_Values.Look<Color?>(ref colorB, "colorB", (Color?)null, false);
			Scribe_Values.Look<Color?>(ref colorC, "colorC", (Color?)null, false);
			Scribe_Collections.Look<string, List<string>>(ref triggers, "triggers", (LookMode)1, (LookMode)1);
		}
	}

	public Color? colorA;

	public Color? colorB;

	public Color? colorC;

	public Dictionary<string, List<string>> triggers = new Dictionary<string, List<string>>();

	public List<SubItemGraphic> flagItems = new List<SubItemGraphic>();

	public static void Replace(Thing t, CustomizableGraphic graphic)
	{
		if (t != null)
		{
			if (graphic == null)
			{
				CustomizableGraphicTracker.GInstance.thingGraphics.Remove(t.ThingID);
			}
			else
			{
				CustomizableGraphicTracker.GInstance.thingGraphics[t.ThingID] = graphic;
			}
		}
	}

	public static CustomizableGraphic Get(Thing t, bool createIfMissing = false)
	{
		if (t == null)
		{
			Log.WarningOnce("Tried to get graphic for null thing.", 893245);
			return null;
		}
		if (CustomizableGraphicTracker.GInstance.thingGraphics.TryGetValue(t.ThingID, out var value))
		{
			return value;
		}
		if (createIfMissing)
		{
			value = new CustomizableGraphic();
			CustomizableGraphicTracker.GInstance.thingGraphics[t.ThingID] = value;
			return value;
		}
		return null;
	}

	public static SubItemGraphic GetFlagGraphic(Thing t, FlagString fStr, bool createIfMissing = false)
	{
		CustomizableGraphic customizableGraphic = Get(t, createIfMissing);
		if (customizableGraphic == null)
		{
			return null;
		}
		List<SubItemGraphic> list = customizableGraphic.flagItems;
		SubItemGraphic subItemGraphic = ((list != null) ? GenCollection.FirstOrDefault<SubItemGraphic>(list, (Predicate<SubItemGraphic>)((SubItemGraphic x) => x.flagString == fStr)) : null);
		if (subItemGraphic == null && createIfMissing)
		{
			CustomizableGraphic customizableGraphic2 = customizableGraphic;
			if (customizableGraphic2.flagItems == null)
			{
				customizableGraphic2.flagItems = new List<SubItemGraphic>();
			}
			subItemGraphic = new SubItemGraphic
			{
				flagString = fStr
			};
			customizableGraphic.flagItems.Add(subItemGraphic);
		}
		return subItemGraphic;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<Color?>(ref colorA, "colorA", (Color?)null, false);
		Scribe_Values.Look<Color?>(ref colorB, "colorB", (Color?)null, false);
		Scribe_Values.Look<Color?>(ref colorC, "colorC", (Color?)null, false);
		Scribe_Collections.Look<SubItemGraphic>(ref flagItems, "tagItems", (LookMode)2, Array.Empty<object>());
		Scribe_Collections.Look<string, List<string>>(ref triggers, "triggers", (LookMode)1, (LookMode)1);
	}

	public override string ToString()
	{
		return string.Format("[{0}] - ColorA: {1}, ColorB: {2}, ColorC: {3}", "CustomizableGraphic", colorA, colorB, colorC);
	}
}
