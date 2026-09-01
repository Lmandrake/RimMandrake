using System.Runtime.CompilerServices;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public abstract class Gizmo_ResourceBase : Gizmo_Slider
{
	public IResourcePool resource;

	[CompilerGenerated]
	private bool _003CDraggingBar_003Ek__BackingField;

	protected override Color BarColor { get; }

	protected override Color BarHighlightColor { get; }

	protected override string BarLabel => $"{resource.ValueForDisplay} / {resource.MaxForDisplay}";

	protected override float ValuePercent => resource.ValuePercent;

	protected override int Increments => resource.Increments / 10;

	protected override bool DraggingBar
	{
		get
		{
			return _003CDraggingBar_003Ek__BackingField;
		}
		set
		{
			_003CDraggingBar_003Ek__BackingField = value;
		}
	}

	protected override float Target
	{
		get
		{
			return resource.TargetValue / resource.Max;
		}
		set
		{
			resource.SetTargetValuePct(value);
		}
	}

	protected override string Title
	{
		get
		{
			string text = GenText.CapitalizeFirst(resource.Label);
			if (Find.Selector.SelectedPawns.Count != 1)
			{
				text = text + " (" + ((Entity)resource.Pawn).LabelShort + ")";
			}
			return text;
		}
	}
}
