using UnityEngine;
using Verse;

namespace BigAndSmall;

public class SoulResourceGizmo : Gizmo_ResourceBase
{
	protected override bool IsDraggable => false;

	protected override Color BarColor
	{
		get
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			ColorInt val = new ColorInt(60, 30, 90);
			return ((ColorInt)(ref val)).ToColor;
		}
	}

	protected override Color BarHighlightColor
	{
		get
		{
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			ColorInt val = new ColorInt(100, 50, 150);
			return ((ColorInt)(ref val)).ToColor;
		}
	}

	public SoulResourceGizmo(SoulResourceHediff resource)
	{
		base.resource = resource;
	}

	protected override string GetTooltip()
	{
		return "";
	}
}
