using System;
using RimWorld;
using Verse;

namespace Outposts;

public class PostToSetingsAttribute : Attribute
{
	public enum DrawMode
	{
		Checkbox,
		IntSlider,
		Slider,
		Percentage,
		Time
	}

	private readonly object ignore;

	private readonly float max;

	private readonly float min;

	private readonly bool shouldIgnore;

	public object Default;

	public string LabelKey;

	public DrawMode Mode;

	public string TooltipKey;

	public PostToSetingsAttribute(string label, DrawMode mode, object value = null, float min = 0f, float max = 0f, string tooltip = null, object dontShowAt = null)
	{
		LabelKey = label;
		Mode = mode;
		Default = value;
		this.min = min;
		this.max = max;
		TooltipKey = tooltip;
		ignore = dontShowAt;
		shouldIgnore = dontShowAt != null;
	}

	public void Draw(Listing_Standard listing, ref object current)
	{
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0175: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		if (shouldIgnore && object.Equals(current, ignore))
		{
			return;
		}
		switch (Mode)
		{
		case DrawMode.Checkbox:
		{
			bool flag = (bool)current;
			string text = TaggedString.op_Implicit(Translator.Translate(LabelKey));
			string tooltipKey = TooltipKey;
			TaggedString? val = ((tooltipKey != null) ? new TaggedString?(Translator.Translate(tooltipKey)) : ((TaggedString?)null));
			listing.CheckboxLabeled(text, ref flag, val.HasValue ? TaggedString.op_Implicit(val.GetValueOrDefault()) : null, 0f, 1f);
			if (flag != (bool)current)
			{
				current = flag;
			}
			break;
		}
		case DrawMode.Slider:
			listing.Label(TaggedString.op_Implicit(Translator.Translate(LabelKey) + ": ") + current, -1f, (TipSignal?)null);
			current = listing.Slider((float)current, min, max);
			break;
		case DrawMode.Percentage:
			listing.Label(Translator.Translate(LabelKey) + ": " + GenText.ToStringPercent((float)current), -1f, (string)null);
			current = listing.Slider((float)current, min, max);
			break;
		case DrawMode.IntSlider:
			listing.Label(TaggedString.op_Implicit(Translator.Translate(LabelKey) + ": ") + current, -1f, (TipSignal?)null);
			current = (int)listing.Slider((float)(int)current, (float)(int)min, (float)(int)max);
			break;
		case DrawMode.Time:
			listing.Label(Translator.Translate(LabelKey) + ": " + GenDate.ToStringTicksToPeriodVerbose((int)current, true, true), -1f, (string)null);
			current = (int)listing.Slider((float)(int)current, 2500f, 3600000f);
			break;
		default:
			throw new ArgumentOutOfRangeException();
		}
	}
}
